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
            del store[obj]

    mainframe.subscribe_execute(f'{name}', run)
    mainframe.subscribe_drop(f'{name}', drop)

    while True:
        await asyncio.sleep(1)
        if not fs.empty():
            f = fs.get()
            message = await f
            run_block(message, mainframe)

async def run_block(message, mainframe: Mainframe):

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

    original_stdout = sys.stdout
    original_stderr = sys.stderr

    try:
        captured_output = StringIO()
        captured_error = StringIO()

        sys.stdout = captured_output
        sys.stderr = captured_error
        index_module = load_module(source, dir)
        main = index_module.main
        if inspect.iscoroutinefunction(main):
            await main(sdk.props, sdk)
        else:
            main(sdk.props, sdk)
    except Exception as e:
        traceback_str = traceback.format_exc()
        sdk.done(traceback_str)
    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        stdout_lines = captured_output.getvalue()
        for line in stdout_lines.splitlines():
            sdk.report_log(line)
        stderr_lines = captured_error.getvalue()
        for line in stderr_lines.splitlines():
            sdk.report_log(line, 'stderr')

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup(loop))
    loop.close()
