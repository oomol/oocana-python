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

    import argparse
    parser = argparse.ArgumentParser(description="run applet with mqtt address and client id")
    parser.add_argument("--address", help="mqtt address", default="mqtt://127.0.0.1:47688")
    parser.add_argument("--client-id", help="mqtt client id")

    home_directory = os.path.expanduser("~")
    parser.add_argument("--log-dir", help="log dir", default=f"{home_directory}/.oomol-studio")
    args = parser.parse_args()

    # 考虑启动方式，以及获取地址以及执行器名称，or default value
    address: str = args.address
    log_dir: str = args.log_dir

    mainframe = Mainframe(address, args.client_id)
    mainframe.connect()

    # 这个日志，用来告知 bin 模式调用时，连接成功。所以这个格式要主动输出保持不变。
    print(f"connecting to broker {address} success")
    # Python 以子进程启动时，输出不会立刻出现。而我们在业务上需要这一行日志，所以主动 flush 一次。
    sys.stdout.flush()

    if os.path.exists(log_dir):
        file_name = log_dir + '/executor/python.log'
        if not os.path.exists(file_name):
            os.makedirs(os.path.dirname(file_name), exist_ok=True)
            open(file_name, 'w').close()

        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filename=file_name)
        logger.info(f"setup basic logging in file {file_name}")
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

    mainframe.subscribe(f"executor/{EXECUTOR_NAME}/run_block", execute_block)
    mainframe.subscribe(f"executor/{EXECUTOR_NAME}/drop", drop)
    mainframe.subscribe(f"executor/{EXECUTOR_NAME}/run_applet_block", execute_applet_block)

    async def spawn_applet(message: AppletExecutePayload):
        logger.info(f"create new applet {message.get('dir')}")
        applet_id = "-".join(["applet", message.get("job_id")])
        appletMap[message.get("dir")] = applet_id

        parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        process = await asyncio.create_subprocess_shell(
            f"python -u -m impl.applet --address {address} --client-id {applet_id} | tee /tmp/1.log",
            cwd=parent_dir
        )

        mainframe.subscribe(f"executor/applet/{applet_id}/spawn", lambda _: mainframe.publish(f"executor/applet/{applet_id}/config", message))


        # 等待子进程结束
        await process.wait()
        logger.info(f"applet {applet_id} exit")
        appletMap.pop(message.get("dir"))
        mainframe.unsubscribe(f"executor/applet/{applet_id}/spawn")
    

    def run_applet_block(message: AppletExecutePayload, applet_id: str):
        logger.info(f"applet block {message.get('job_id')} start")
        mainframe.publish(f"executor/applet/{applet_id}/config", message)

    while True:
        await asyncio.sleep(1)
        if not fs.empty():
            f = fs.get()
            message = await f
            if message.get("applet_executor") is not None:
                applet_dir = message.get("dir")
                applet_id = appletMap.get(applet_dir)
                if applet_id is None:
                    asyncio.create_task(spawn_applet(message))
                else:
                    run_applet_block(message, applet_id)
            else:
                await run_block(message, mainframe)


if __name__ == '__main__':

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(setup(loop))
    loop.close()
