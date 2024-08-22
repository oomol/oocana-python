#!/usr/bin/env python

import asyncio
import os
import queue
import sys
import logging

from oocana import Mainframe, ServiceExecutePayload
from .data import serviceMap
from .block import run_block
from oocana import EXECUTOR_NAME

logger = logging.getLogger(EXECUTOR_NAME)

async def setup(loop):

    import argparse
    parser = argparse.ArgumentParser(description="run service with mqtt address and client id")
    parser.add_argument("--address", help="mqtt address", default="mqtt://127.0.0.1:47688")
    parser.add_argument("--session-id", help="executor subscribe session id", required=True)
    parser.add_argument("--client-id", help="mqtt client id")
    parser.add_argument("--output", help="output log to console or file", default="file", choices=["console", "file"])
    home_directory = os.path.expanduser("~")

    # TODO: 迁移到 .oocana 下
    default_log_dir = os.path.join(home_directory, ".oomol-studio", "executor")
    parser.add_argument("--log-dir", help="log file's directory", default=default_log_dir)


    args = parser.parse_args()

    address: str = args.address
    session_id: str = args.session_id
    log_dir: str = args.log_dir
    output: str = args.output

    mainframe = Mainframe(address, args.client_id)
    mainframe.connect()

    # 这个日志，用来告知 bin 模式调用时，连接成功。所以这个格式要主动输出保持不变。
    print(f"connecting to broker {address} success")
    # Python 以子进程启动时，输出不会立刻出现。而我们在业务上需要这一行日志，所以主动 flush 一次。
    sys.stdout.flush()

    if output == "file":
        logger_file = os.path.join(log_dir, f'python-{session_id}.log')
        if not os.path.exists(logger_file):
            os.makedirs(os.path.dirname(logger_file), exist_ok=True)
            open(logger_file, 'w').close()

        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filename=logger_file)
        print(f"setup basic logging in file {logger_file}")
    else:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        logger.info("setup basic logging in console")

    fs = queue.Queue()

    def not_current_session(message):
        return message.get("session_id") != session_id
    
    def not_current_service(message):
        return message.get("service_id") != service_id

    def execute_block(message):
        if not_current_session(message):
            return

        nonlocal fs
        # 在当前使用的 mqtt 库里，如果在 subscribe 之后，直接 publish 消息，会一直阻塞无法发送成功。
        # 所以要切换线程后，再进行 publish。这里使用 future 来实现线程切换和数据传递。
        f = loop.create_future()
        fs.put(f)
        f.set_result(message)
    
    def execute_service_block(message):
        if not_current_session(message):
            return

        nonlocal fs
        f = loop.create_future()
        fs.put(f)
        f.set_result(message)

    def drop(message):
        if not_current_session(message):
            return

    original_keys = set(sys.modules.keys())

    def ping(message):
        nonlocal fs
        f = loop.create_future()
        fs.put(f)
        f.set_result({"type": "ExecutorPing"})

    def ask_ready(message):
        nonlocal fs
        f = loop.create_future()
        fs.put(f)
        f.set_result({"type": "ExecutorReady"})

    def report_message(message):
        type = message.get("type")

        if type == "SessionStarted":
            if not_current_session(message):
                logger.info(f"new session {message.get('session_id')} started, exit current session {session_id} executor")
                exit()
            

        elif type == "SessionFinished":
            if not_current_session(message):
                return
            
            # 每次运行结束，清理新增的模块
            delete = set(sys.modules.keys()) - original_keys
            for key in delete:
                del sys.modules[key]
            
            # sys.path 可能也需要清理。
        

    mainframe.subscribe(f"executor/{EXECUTOR_NAME}/run_block", execute_block)
    mainframe.subscribe(f"executor/{EXECUTOR_NAME}/drop", drop)
    mainframe.subscribe(f"executor/{EXECUTOR_NAME}/run_service_block", execute_service_block)
    mainframe.subscribe(f"executor/{EXECUTOR_NAME}/{session_id}/ping", ping)
    mainframe.subscribe(f"executor/{EXECUTOR_NAME}/{session_id}/ready", ask_ready)
    mainframe.subscribe('report', report_message)

    mainframe.notify_executor_ready(session_id, EXECUTOR_NAME, client_id=args.client_id)

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
                if not_current_service(message):
                    continue

                service_dir = message.get("dir")
                service_id = serviceMap.get(service_dir)
                if service_id is None:
                    asyncio.create_task(spawn_service(message))
                else:
                    run_service_block(message, service_id)
            # TODO: 把类型约束弄好
            elif message.get("type") == "ExecutorPing":
                mainframe.publish(f"session/{session_id}", {"type": "ExecutorPong", "session_id": session_id, "executor_name": EXECUTOR_NAME, "client_id": args.client_id})
                pass
            elif message.get("type") == "ExecutorReady":
                mainframe.notify_executor_ready(session_id, EXECUTOR_NAME, client_id=args.client_id)
            else:
                if not_current_session(message):
                    continue
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
