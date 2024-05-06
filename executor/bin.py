#!/usr/bin/env python

import sys
import os
import traceback
import importlib
import importlib.util
import asyncio
from vocana import setup_vocana_sdk, Mainframe, RefDescriptor
import queue
from io import StringIO
from dataclasses import dataclass
from typing import Optional
import inspect
from contextlib import redirect_stdout, redirect_stderr

from io import StringIO 
import sys

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

def load_module(source, dir=None):
    if (os.path.isabs(source)):
        source_abs_path = source
    else:
        dirname = dir if dir else os.getcwd()
        source_abs_path = os.path.join(dirname, source)

    module_name = os.path.basename(source_abs_path).replace('.py', '')
    sys.path.append(os.path.dirname(source_abs_path))
    file_spec = importlib.util.spec_from_file_location(module_name, source_abs_path)
    module = importlib.util.module_from_spec(file_spec)
    file_spec.loader.exec_module(module)
    return module


async def setup(loop):
    # 考虑启动方式，以及获取地址以及执行器名称，or default value
    address = os.environ.get('VOCANA_ADDRESS') if os.environ.get('VOCANA_ADDRESS') else 'mqtt://127.0.0.1:47688'
    name = os.environ.get('VOCANA_EXECUTOR') if os.environ.get('VOCANA_EXECUTOR') else 'python_executor'
    mainframe = Mainframe(address)
    mainframe.connect()
    print(f"connecting to broker {address} success")
    # 保证在以子进程模式启动时，不会等待缓冲区满了才输出，导致连接日志输出不及时。
    sys.stdout.flush()

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
            print("drop", obj.job_id, obj.handle)
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

    print("block", message.get("job_id"), "start")
    try:
        payload = ExecutePayload(**message)
    except Exception as e:
        traceback_str = traceback.format_exc()
        # rust 那边会保证传过来的 message 一定是符合格式的，所以这里不应该出现异常。这里主要是防止 rust 修改错误。
        mainframe.send({
            "type": "BlockError",
            "session_id": message["session_id"], 
            "job_id": message["job_id"], 
            "error": traceback_str
        })
        return

    sdk = setup_vocana_sdk(mainframe, payload.session_id, payload.job_id, store, payload.outputs)
    
    dir = payload.dir

    config = payload.executor
    source = config["entry"] if config is not None and config.get("entry") is not None else 'index.py'

    try:
        # TODO: 这里的异常处理，应该跟详细一些，提供语法错误提示。
        index_module = load_module(source, dir)
    except Exception as e:
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
    except Exception as e:
        traceback_str = traceback.format_exc()
        sdk.done(traceback_str)
    finally:
        print("block", message.get("job_id"), "done")


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(setup(loop))
    loop.close()
