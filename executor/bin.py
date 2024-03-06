#!/usr/bin/env python

import sys
import time
import os
import traceback
import importlib
import importlib.util
import asyncio
from vocana import setup_vocana_sdk, Mainframe, ObjectStoreDescriptor
import queue


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
        f = loop.create_future()
        fs.put(f)
        f.set_result(message)

    def drop(message):
        obj = ObjectStoreDescriptor(**message)
        o = store.get(obj)
        print('drop obj', obj, o)
        if o is not None:
            del store[obj]
        
    mainframe.subscribe_execute(f'{name}', run)
    mainframe.subscribe_drop(f'{name}', drop)

    while True:
        await asyncio.sleep(1)
        if not fs.empty():
            f = fs.get()
            message = await f
            setup_sdk(message, mainframe)

        

def setup_sdk(message, mainframe):

    # 这两个参数肯定存在，所以这里只做 raise Exception 防止调试时没传的问题
    if message.get('session_id') is None:
        raise Exception('session_id is required')
    if message.get('job_id') is None:
        raise Exception('job_id is required')

    sdk = setup_vocana_sdk(mainframe, message['session_id'], message['job_id'], store)
    
    dir = message.get('dir')

    options = message.get('options')
    source = options["entry"] if options is not None and options.get("entry") is not None else 'index.py'

    try:
        index_module = load_module(source, dir)
        index_module.main(sdk.props, sdk)
    except Exception as e:
        print('Error:', repr(e))
        traceback_str = traceback.format_exc()
        sdk.send_error(traceback_str)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup(loop))
    loop.close()
