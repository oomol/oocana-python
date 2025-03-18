#!/usr/bin/env python

import asyncio
import os
import queue
import sys
import logging
import re
from . import hook
from oocana import Mainframe, ServiceExecutePayload
from .utils import run_in_new_thread, run_async_code, oocana_dir
from .block import run_block
from oocana import EXECUTOR_NAME
from .matplot.oomol_matplot_helper import import_helper, add_matplot_module
from typing import Literal
from .topic import prepare_report_topic, service_config_topic, run_action_topic, ServiceTopicParams, ReportStatusPayload, exit_report_topic, status_report_topic

logger = logging.getLogger(EXECUTOR_NAME)
service_store: dict[str, Literal["launching", "running"]] = {}
job_set = set()

# 日志目录 ~/.oocana/sessions/{session_id}
# executor 的日志都会记录在 [python-executor-{suffix}.log | python-executor.log]
# 全局 logger 会记录在 python-{suffix}.log | python.log
def config_logger(session_id: str, suffix: str | None, output: Literal["console", "file"]):


    format = '%(asctime)s - %(levelname)s - {%(pathname)s:%(lineno)d} - %(message)s'
    fmt = logging.Formatter(format)
    logger.setLevel(logging.DEBUG)
    if output == "file":
        executor_dir = os.path.join(oocana_dir(), "sessions", session_id)
        logger_file = os.path.join(executor_dir, f"python-executor-{suffix}.log") if suffix is not None else os.path.join(executor_dir, "python-executor.log")

        if not os.path.exists(logger_file):
            os.makedirs(os.path.dirname(logger_file), exist_ok=True)

        print(f"setup logging in file {logger_file}")
        h = logging.FileHandler(logger_file)

        global_logger_file = os.path.join(executor_dir, f"python-{suffix}.log") if suffix is not None else os.path.join(executor_dir, "python.log")
        logging.basicConfig(filename=global_logger_file, level=logging.DEBUG, format=format)
    else:
        logging.basicConfig(level=logging.DEBUG, format=format)
        h = logging.StreamHandler(sys.stdout)

    h.setFormatter(fmt)
    logger.addHandler(h)
    # 跟全局日志分开。避免有的库在全局 logger 里面使用了 print 等 API，导致 hook 出现递归调用
    logger.propagate = False


async def run_executor(address: str, session_id: str, package: str | None, session_dir: str, suffix: str | None = None):

    if suffix is not None:
        mainframe = Mainframe(address, f"python-executor-{suffix}", logger)
    else:
        mainframe = Mainframe(address, f"python-executor-{session_id}", logger)

    mainframe.connect()

    print(f"connecting to broker {address} success")
    sys.stdout.flush()

    logger.info("executor start") if package is None else logger.info(f"executor start for package {package}")

    add_matplot_module()
    import_helper(logger)

    # add package to sys.path
    if package is not None:
        # TODO: compatibility for package with prefix. e.g. package-/app/workspace. remove it after new version of oocana
        sys.path.append(re.sub(r"^.*?/", "/", package))
    elif os.path.exists("/app/workspace"):
        sys.path.append("/app/workspace")


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
        
        # https://github.com/oomol/oocana-rust/issues/310 临时解决方案
        job_id = message.get("job_id")
        if job_id in job_set:
            logger.warning(f"job {job_id} already running, ignore")
            return
        job_set.add(job_id)

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

    def service_exit(message: ReportStatusPayload):
        service_hash = message.get("service_hash")
        if service_hash in service_store:
            del service_store[service_hash]

    def service_status(message: ReportStatusPayload):
        service_hash = message.get("service_hash")
        if service_hash in service_store:
            service_store[service_hash] = "running"

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
                hook.original_exit(0)
        

    mainframe.subscribe(f"executor/{EXECUTOR_NAME}/run_block", execute_block)
    mainframe.subscribe(f"executor/{EXECUTOR_NAME}/run_service_block", execute_service_block)
    mainframe.subscribe('report', report_message)
    mainframe.subscribe(exit_report_topic(), service_exit)
    mainframe.subscribe(status_report_topic(), service_status)

    mainframe.notify_executor_ready(session_id, EXECUTOR_NAME, package)

    async def spawn_service(message: ServiceExecutePayload, service_hash: str):
        logger.info(f"create new service {message.get('dir')}")
        service_store[service_hash] = "launching"

        parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

        is_global_service = message.get("service_executor").get("stop_at") in ["app_end", "never"]

        if is_global_service:
            process = await asyncio.create_subprocess_shell(
                f"python -u -m python_executor.service --address {address}  --service-hash {service_hash} --session-dir {session_dir}",
                cwd=parent_dir
            )
        else:
            process = await asyncio.create_subprocess_shell(
                f"python -u -m python_executor.service --address {address} --session-id {session_id}  --service-hash {service_hash} --session-dir {session_dir}",
                cwd=parent_dir
            )
        params: ServiceTopicParams = {
            "service_hash": service_hash,
            "session_id": session_id
        }

        def send_service_config(params: ServiceTopicParams, message: ServiceExecutePayload):

            async def run():
                mainframe.publish(service_config_topic(params), message)
                service_store[service_hash] = "running"
            run_in_new_thread(run)

        # FIXME: mqtt 不能在 subscribe 后立即 publish，需要修复。
        mainframe.subscribe(prepare_report_topic(params), lambda _: send_service_config(params, message))

        await process.wait()
        logger.info(f"service {service_hash} exit")
        del service_store[service_hash]
    

    def run_service_block(message: ServiceExecutePayload):
        logger.info(f"service block {message.get('job_id')} start")
        service_hash = message.get("service_hash")
        params: ServiceTopicParams = {
            "service_hash": service_hash,
            "session_id": session_id
        }
        mainframe.publish(run_action_topic(params), message)

    while True:
        await asyncio.sleep(1)
        if not fs.empty():
            f = fs.get()
            message = await f
            if message.get("service_executor") is not None:
                service_hash = message.get("service_hash")
                status = service_store.get(service_hash)
                if status is None:
                    asyncio.create_task(spawn_service(message, service_hash))
                elif status == "running":
                    run_service_block(message)
                elif status == "launching":
                    logger.info(f"service {service_hash} is launching, set message back to fs to wait next time")
                    fs.put(f)
            else:
                if not_current_session(message):
                    continue
                run_block_in_new_thread(message, mainframe, session_dir=session_dir)

def run_block_in_new_thread(message, mainframe: Mainframe, session_dir: str):

    async def run():
        await run_block(message, mainframe, session_dir=session_dir)
    run_in_new_thread(run)

def main():

    import argparse
    parser = argparse.ArgumentParser(description="run executor with address, session-id, tmp-dir")
    parser.add_argument("--session-id", help="executor subscribe session id", required=True)
    parser.add_argument("--address", help="mqtt address", default="mqtt://127.0.0.1:47688")
    parser.add_argument("--session-dir", help="a tmp dir for whole session", required=True)
    parser.add_argument("--output", help="output log to console or file", default="file", choices=["console", "file"])
    parser.add_argument("--package", help="package path, if set, executor will only run same package block", default=None)
    parser.add_argument("--suffix", help="suffix for log file", default=None)

    args = parser.parse_args()

    address: str = args.address
    session_id: str = str(args.session_id)
    output: Literal["console", "file"] = args.output
    package: str | None = args.package
    suffix: str | None = args.suffix
    session_dir: str = args.session_dir

    config_logger(session_id, suffix, output)

    run_async_code(run_executor(address=address, session_id=session_id, package=package, session_dir=session_dir, suffix=suffix))

if __name__ == '__main__':
    main()