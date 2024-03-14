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

# TODO: 最好用 dataclass 固化校验
# message 格式: {
#     "session_id": "xxxx",
#     "job_id": "xxxx",
#     "executor": {
#         "entry": "index.py"
#     },
#     "dir": "xxxx",
#     "outputs": {
#         "output1": {
#               "handleName": "xxxx",
#               "executor": "python_executor",
#          }
#     }
# }
def run_block(message, mainframe):

    # 这两个参数肯定存在，所以这里只做 raise Exception 防止调试时没传的问题
    if message.get('session_id') is None:
        raise Exception('session_id is required')
    if message.get('job_id') is None:
        raise Exception('job_id is required')

    sdk = setup_vocana_sdk(mainframe, message['session_id'], message['job_id'], store, message.get('outputs'))
    
    dir = message.get('dir')

    config = message.get('executor')
    source = config["entry"] if config is not None and config.get("entry") is not None else 'index.py'

    original_stdout = sys.stdout
    original_stderr = sys.stderr

    try:
        captured_output = StringIO()
        captured_error = StringIO()

        sys.stdout = captured_output
        sys.stderr = captured_error
        index_module = load_module(source, dir)
        index_module.main(sdk.props, sdk)
    except Exception as e:
        traceback_str = traceback.format_exc()
        sdk.send_error(traceback_str)
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
