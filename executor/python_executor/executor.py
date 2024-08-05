#!/usr/bin/env python

import asyncio
import os
import queue
import sys
import logging
import shutil

from oocana import Mainframe, StoreKey, ServiceExecutePayload
from .data import store, serviceMap
from .block import run_block, tmp_files
from oocana import EXECUTOR_NAME

logger = logging.getLogger(EXECUTOR_NAME)

async def setup(loop):

    import argparse
    parser = argparse.ArgumentParser(description="run service with mqtt address and client id")
    parser.add_argument("--address", help="mqtt address", default="mqtt://127.0.0.1:47688")
    parser.add_argument("--client-id", help="mqtt client id")

    home_directory = os.path.expanduser("~")
    default_log_dir = os.path.join(home_directory, ".oomol-studio")
    parser.add_argument("--log-dir", help="log dir", default=default_log_dir)
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

        file_name = os.path.join(log_dir, 'executor', 'python.log')
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
    
    def execute_service_block(message):
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

    def session_end(message):
        if message.get("type") == "SessionFinished":
            dir_set: set[str] = set()
            for k in tmp_files:
                if os.path.exists(k):
                    os.remove(k)
                dir_set.add(os.path.dirname(k))
            for d in dir_set:
                # 如果子目录是在 .scriptlets 目录下，删除子目录
                if os.path.exists(d) and os.path.dirname(d).endswith(".scriptlets"):
                    shutil.rmtree(d)
            

    mainframe.subscribe(f"executor/{EXECUTOR_NAME}/run_block", execute_block)
    mainframe.subscribe(f"executor/{EXECUTOR_NAME}/drop", drop)
    mainframe.subscribe(f"executor/{EXECUTOR_NAME}/run_service_block", execute_service_block)
    mainframe.subscribe('report', session_end)

    async def spawn_service(message: ServiceExecutePayload):
        logger.info(f"create new service {message.get('dir')}")
        service_id = "-".join(["service", message.get("job_id")])
        serviceMap[message.get("dir")] = service_id

        parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        process = await asyncio.create_subprocess_shell(
            f"python -u -m python_executor.service --address {address} --client-id {service_id}",
            cwd=parent_dir
        )

        mainframe.subscribe(f"executor/service/{service_id}/spawn", lambda _: mainframe.publish(f"executor/service/{service_id}/config", message))


        # 等待子进程结束
        await process.wait()
        logger.info(f"service {service_id} exit")
        serviceMap.pop(message.get("dir"))
        mainframe.unsubscribe(f"executor/service/{service_id}/spawn")
    

    def run_service_block(message: ServiceExecutePayload, service_id: str):
        logger.info(f"service block {message.get('job_id')} start")
        mainframe.publish(f"executor/service/{service_id}/config", message)

    while True:
        await asyncio.sleep(1)
        if not fs.empty():
            f = fs.get()
            message = await f
            if message.get("service_executor") is not None:
                service_dir = message.get("dir")
                service_id = serviceMap.get(service_dir)
                if service_id is None:
                    asyncio.create_task(spawn_service(message))
                else:
                    run_service_block(message, service_id)
            else:
                run_in_background(message, mainframe)

def run_async_code(async_func):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(async_func)
    loop.run_forever()

# 先凑合用线程跑，后续再考虑优化
def run_in_background(message, mainframe: Mainframe):

    async def run():
        await run_block(message, mainframe)
    import threading
    threading.Thread(target=run_async_code, args=(run(),)).start()

if __name__ == '__main__':

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(setup(loop))
    loop.close()
