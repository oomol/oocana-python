#!/usr/bin/env python

import asyncio
import os
import queue
import sys
import logging

from oocana import Mainframe, ServiceExecutePayload
from .data import service_map
from .utils import run_in_new_thread, run_async_code, base_dir
from .block import run_block, vars
from oocana import EXECUTOR_NAME
from .service import SERVICE_EXECUTOR_TOPIC_PREFIX
from .matplot_helper import import_helper, add_matplot_module
from typing import Literal

logger = logging.getLogger(EXECUTOR_NAME)

# 日志目录 ~/.oocana/executor/{session_id}/[python-{suffix}.log | python.log]
def config_logger(session_id: str, suffix: str | None, output: Literal["console", "file"]):

    if output == "file":
        logger_file = os.path.join(base_dir(), session_id, f"python-{suffix}.log") if suffix is not None else os.path.join(os.path.expanduser("~"), ".oocana", "executor", session_id, "python.log")

        if not os.path.exists(logger_file):
            os.makedirs(os.path.dirname(logger_file), exist_ok=True)

        print(f"setup logging in file {logger_file}")
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - {%(filename)s:%(lineno)d} - %(message)s', filename=logger_file)
    else:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - {%(filename)s:%(lineno)d} - %(message)s')


async def run_executor(address: str, session_id: str, package: str | None, tmp_dir: str):

    mainframe = Mainframe(address)
    mainframe.connect()

    print(f"connecting to broker {address} success")
    sys.stdout.flush()

    logger.info("executor start") if package is None else logger.info(f"executor start with package {package}")

    # TODO: 透传给其他模块的 全局变量。比较 hack。后续考虑优化，或者把变量共享到另一个文件。使用见 oomol.py
    sys.modules['oomol'] = vars # type: ignore

    add_matplot_module()
    import_helper(logger)


    def not_current_session(message):
        return message.get("session_id") != session_id
    
    def not_current_package(message):
        return message.get("package") != package

    # 目前的 mqtt 库，在 subscribe 回调里 publish 消息会导致死锁无法工作，参考 https://github.com/eclipse/paho.mqtt.python/issues/527 或者 https://stackoverflow.com/a/36964192/4770006
    # 通过这种方式来绕过，所有需要 callback 后 publish message 的情况，都需要使用 future 类似方式来绕过。
    fs = queue.Queue()
    loop = asyncio.get_event_loop()

    def execute_block(message):
        if not_current_session(message):
            return

        if not_current_package(message):
            return

        nonlocal fs
        f = loop.create_future()
        fs.put(f)
        f.set_result(message)
    
    def execute_service_block(message):
        if not_current_session(message):
            return
        
        if not_current_package(message):
            return

        nonlocal fs
        f = loop.create_future()
        fs.put(f)
        f.set_result(message)

    # 现在 session 要保留 var 进行 rerun 缓存，所以这个回调目前不处理。如果 var 功能保留，这个回调就直接删除。
    def drop(message):
        pass
        # if not_current_session(message):
        #     return

    def report_message(message):
        type = message.get("type")
        if type == "SessionFinished":
            if not_current_session(message):
                return
            logger.info(f"session {session_id} finished, exit executor")
            mainframe.disconnect() # TODO: 即使调用 disconnect，在 broker 上也无法看不到主动断开的信息，有时间再调查。
            if os.getenv("IS_FORKED"): # fork 进程无法直接使用 sys.exit 退出
                os._exit(0)
            else:
                sys.exit()
        

    mainframe.subscribe(f"executor/{EXECUTOR_NAME}/run_block", execute_block)
    mainframe.subscribe(f"executor/{EXECUTOR_NAME}/drop", drop)
    mainframe.subscribe(f"executor/{EXECUTOR_NAME}/run_service_block", execute_service_block)
    mainframe.subscribe('report', report_message)

    mainframe.notify_executor_ready(session_id, EXECUTOR_NAME, package)

    async def spawn_service(message: ServiceExecutePayload):
        logger.info(f"create new service {message.get('dir')}")
        service_id = "-".join(["service", message.get("job_id")])
        service_map[message.get("dir")] = service_id

        parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        process = await asyncio.create_subprocess_shell(
            f"python -u -m python_executor.service --address {address} --service-id {service_id} --tmp-dir {tmp_dir}",
            cwd=parent_dir
        )

        mainframe.subscribe(f"{SERVICE_EXECUTOR_TOPIC_PREFIX}/{service_id}/spawn", lambda _: mainframe.publish(f"{SERVICE_EXECUTOR_TOPIC_PREFIX}/{service_id}/config", message))


        # 等待子进程结束
        await process.wait()
        logger.info(f"service {service_id} exit")
        service_map.pop(message.get("dir"))
        mainframe.unsubscribe(f"{SERVICE_EXECUTOR_TOPIC_PREFIX}/{service_id}/spawn")
    

    def run_service_block(message: ServiceExecutePayload, service_id: str):
        logger.info(f"service block {message.get('job_id')} start")
        mainframe.publish(f"{SERVICE_EXECUTOR_TOPIC_PREFIX}/{service_id}/config", message)

    while True:
        await asyncio.sleep(1)
        if not fs.empty():
            f = fs.get()
            message = await f
            if message.get("service_executor") is not None:
                service_dir = message.get("dir")
                service_id = service_map.get(service_dir)
                if service_id is None:
                    asyncio.create_task(spawn_service(message))
                else:
                    run_service_block(message, service_id)
            else:
                if not_current_session(message):
                    continue
                run_block_in_new_thread(message, mainframe, tmp_dir=tmp_dir)

def run_block_in_new_thread(message, mainframe: Mainframe, tmp_dir: str):

    async def run():
        await run_block(message, mainframe, tmp_dir=tmp_dir)
    run_in_new_thread(run)

if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(description="run executor with address, session-id, tmp-dir")
    parser.add_argument("--session-id", help="executor subscribe session id", required=True)
    parser.add_argument("--address", help="mqtt address", default="mqtt://127.0.0.1:47688")
    parser.add_argument("--tmp-dir", help="tmp dir for executor", required=True)
    parser.add_argument("--output", help="output log to console or file", default="file", choices=["console", "file"])
    parser.add_argument("--package", help="package path, if set, executor will only run same package block", default=None)
    parser.add_argument("--suffix", help="suffix for log file", default=None)
    home_directory = os.path.expanduser("~")

    args = parser.parse_args()

    address: str = args.address
    session_id: str = str(args.session_id)
    output: Literal["console", "file"] = args.output
    package: str | None = args.package
    suffix: str | None = args.suffix
    tmp_dir: str = args.tmp_dir

    config_logger(session_id, suffix, output)

    run_async_code(run_executor(address=address, session_id=session_id, package=package, tmp_dir=tmp_dir))