#!/usr/bin/env python

import asyncio
import importlib
import importlib.util
import inspect
import os
import queue
import sys
import traceback
import logging
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from io import StringIO
from typing import Optional
from vocana import Mainframe, RefDescriptor, setup_vocana_sdk

logger = logging.getLogger(__name__)

@dataclass
class ExecutePayload:
    session_id: str
    job_id: str
    dir: str
    executor: Optional[dict] = None
    outputs: Optional[dict] = None

    def __init__(self, *args, **kwargs):
        if args:
            self.session_id = args[0]
            self.job_id = args[1]
            self.executor = args[2]
            self.dir = args[3]
            self.outputs = args[4]
        if kwargs:
            for key, value in kwargs.items():
                setattr(self, key, value)

store = {}

def load_module(source, source_dir=None):
    if (os.path.isabs(source)):
        source_abs_path = source
    else:
        dirname = source_dir if source_dir else os.getcwd()
        source_abs_path = os.path.join(dirname, source)

    module_name = os.path.basename(source_abs_path).replace('.py', '')
    sys.path.append(os.path.dirname(source_abs_path))
    file_spec = importlib.util.spec_from_file_location(module_name, source_abs_path)
    module = importlib.util.module_from_spec(file_spec) # type: ignore
    file_spec.loader.exec_module(module) # type: ignore
    return module


async def setup(loop):
    # 考虑启动方式，以及获取地址以及执行器名称，or default value
    address = os.environ.get('VOCANA_ADDRESS') if os.environ.get('VOCANA_ADDRESS') else 'mqtt://127.0.0.1:47688'
    # name = os.environ.get('VOCANA_EXECUTOR') if os.environ.get('VOCANA_EXECUTOR') else 'python_executor'
    mainframe = Mainframe(address) # type: ignore
    mainframe.connect()

    # 这个日志，用来告知 bin 模式调用时，连接成功。所以这个格式要主动输出保持不变。
    print(f"connecting to broker {address} success")
    # 子进程模式启动时，Python 不会立刻输出，我们需要这一行日志的输出，所以主动 flush 一次。
    sys.stdout.flush()

    log_dir: str = os.environ.get('VOCANA_LOG_DIR') if os.environ.get('VOCANA_LOG_DIR') else "/ovm/.oomol-studio" # type: ignore

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
    def run(message):
        nonlocal fs
        # 在当前使用的 mqtt 库里，如果在 subscribe 之后，直接 publish 消息，会一直阻塞无法发送成功。
        # 所以要切换线程后，再进行 publish。这里使用 future 来实现线程切换和数据传递。
        f = loop.create_future()
        fs.put(f)
        f.set_result(message)

    def drop(message):
        obj = RefDescriptor(**message)
        o = store.get(obj)
        if o is not None:
            logger.info(f"drop {obj.job_id} {obj.handle}")
            del store[obj]

    mainframe.subscribe_execute(run)
    mainframe.subscribe_drop(drop)

    while True:
        await asyncio.sleep(1)
        if not fs.empty():
            f = fs.get()
            message = await f
            await run_block(message, mainframe)

async def run_block(message, mainframe: Mainframe):

    logger.info(f"block {message.get('job_id')} start")
    try:
        payload = ExecutePayload(**message)
    except Exception:
        traceback_str = traceback.format_exc()
        # rust 那边会保证传过来的 message 一定是符合格式的，所以这里不应该出现异常。这里主要是防止 rust 修改错误。
        mainframe.send(
        {
            "job_id": message["job_id"],
            "session_id": message["session_id"],
        },
        {
            "job_id": message["job_id"], 
            "error": traceback_str
        })
        return

    sdk = setup_vocana_sdk(mainframe, payload.session_id, payload.job_id, store, payload.outputs)

    load_dir = payload.dir

    config = payload.executor
    source = config["entry"] if config is not None and config.get("entry") is not None else 'index.py'

    try:
        # TODO: 这里的异常处理，应该跟详细一些，提供语法错误提示。
        index_module = load_module(source, load_dir)
    except Exception:
        traceback_str = traceback.format_exc()
        sdk.done(traceback_str)
        return
    main = index_module.main

    try:
        # TODO: 这种重定向 stdout 和 stderr 的方式比较优雅，但是由于仍然是替换的全局 sys.stdout 和 sys.stderr 对象，所以在协程切换时，仍然会有错乱的问题。
        #       目前任务是一个个排队执行，因此暂时不会出现错乱。
        #       应该和 nodejs 寻找替换 function，在 function 里面读取 contextvars，来进行分发。大体的尝试代码写在 ./ctx.py 里，有时间，或者有需求时，再进行完善。
        with redirect_stderr(StringIO()) as stderr, redirect_stdout(StringIO()) as stdout:
            if inspect.iscoroutinefunction(main):
                await main(sdk.props, sdk)
            else:
                main(sdk.props, sdk)
        for line in stdout.getvalue().splitlines():
            sdk.report_log(line)
        for line in stderr.getvalue().splitlines():
            sdk.report_log(line, "stderr")
    except Exception:
        traceback_str = traceback.format_exc()
        sdk.done(traceback_str)
    finally:
        logger.info(f"block {message.get('job_id')} done")


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(setup(loop))
    loop.close()
