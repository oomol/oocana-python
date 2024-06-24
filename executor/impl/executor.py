#!/usr/bin/env python

import asyncio
import os
import queue
import sys
import logging

from oocana import Mainframe, StoreKey, AppletExecutePayload
from .data import store, appletMap
from .block import run_block

EXECUTOR_NAME = "python_executor"
logger = logging.getLogger(EXECUTOR_NAME)


async def setup(loop):
    # 考虑启动方式，以及获取地址以及执行器名称，or default value
    address = os.environ.get('ADDRESS') if os.environ.get('ADDRESS') else 'mqtt://127.0.0.1:47688'
    # name = os.environ.get('EXECUTOR') if os.environ.get('EXECUTOR') else 'python_executor'
    mainframe = Mainframe(address) # type: ignore
    mainframe.connect()

    # 这个日志，用来告知 bin 模式调用时，连接成功。所以这个格式要主动输出保持不变。
    print(f"connecting to broker {address} success")
    # 子进程模式启动时，Python 不会立刻输出，我们需要这一行日志的输出，所以主动 flush 一次。
    sys.stdout.flush()

    log_dir: str = os.environ.get('LOG_DIR') if os.environ.get('LOG_DIR') else "/ovm/.oomol-studio" # type: ignore

    if os.path.exists(log_dir):
        file_name = log_dir + '/executor/python.log'
        if not os.path.exists(file_name):
            os.makedirs(os.path.dirname(file_name), exist_ok=True)
            open(file_name, 'w').close()

        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filename=log_dir + '/executor/python.log')
        logger.info("setup basic logging in file ~/.oomol-studio/executor/python.log")
    else:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        logger.info("setup basic logging in console")

    fs = queue.Queue()
    def execute_block(message):
        nonlocal fs
        # 在当前使用的 mqtt 库里，如果在 subscribe 之后，直接 publish 消息，会一直阻塞无法发送成功。
        # 所以要切换线程后，再进行 publish。这里使用 future 来实现线程切换和数据传递。
        f = loop.create_future()
        fs.put(f)
        f.set_result(message)
    
    def execute_applet_block(message):
        nonlocal fs
        f = loop.create_future()
        fs.put(f)
        f.set_result(message)

    def drop(message):
        obj = StoreKey(**message)
        o = store.get(obj)
        if o is not None:
            logger.info(f"drop {obj.job_id} {obj.handle}")
            del store[obj]

    mainframe.subscribe(f"executor/{EXECUTOR_NAME}/execute", execute_block)
    mainframe.subscribe(f"executor/{EXECUTOR_NAME}/drop", drop)
    mainframe.subscribe(f"executor/{EXECUTOR_NAME}/applet", execute_applet_block)

    while True:
        await asyncio.sleep(1)
        if not fs.empty():
            f = fs.get()
            message = await f
            if message.get("applet_executor") is not None:
                applet_dir = message.get("dir")
                applet_id = appletMap.get(applet_dir)
                if applet_id is None:
                    asyncio.create_task(spawn_applet(message, mainframe, address)) # type: ignore
                else:
                    run_applet_block(message, mainframe, applet_id)
            else:
                await run_block(message, mainframe)

async def spawn_applet(message: AppletExecutePayload, mainframe: Mainframe, address: str):
    logger.info(f"create new applet {message.get('dir')}")
    applet_id = "-".join([message.get("applet_executor").get("name"), message.get("job_id")])
    appletMap[message.get("dir")] = applet_id

    parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    process = await asyncio.create_subprocess_shell(
        f"python -m python.applet --address {address} --client-id {applet_id}",
        cwd=parent_dir
    )

    mainframe.subscribe(f"executor/applet/{applet_id}/spawn", lambda _: mainframe.publish(f"executor/applet/{applet_id}/config", message))

    # 等待子进程结束
    await process.wait()
    appletMap.pop(message.get("dir"))
    mainframe.unsubscribe(f"executor/applet/{applet_id}/spawn")
    

def run_applet_block(message: AppletExecutePayload, mainframe: Mainframe, applet_id: str):
    logger.info(f"applet block {message.get('job_id')} start")
    mainframe.publish(f"executor/applet/{applet_id}/config", message)

if __name__ == '__main__':

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(setup(loop))
    loop.close()
