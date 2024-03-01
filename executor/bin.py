#!/usr/bin/env python

import sys
import time
import os
import traceback
import importlib
import importlib.util
import asyncio
from vocana import setup_vocana_sdk, Mainframe

def load_module(source):
    if (os.path.isabs(source)):
        source_abs_path = source
    else:
        source_abs_path = os.path.join(os.getcwd(), source)

    module_name = os.path.basename(source_abs_path).replace('.py', '')
    sys.path.append(os.path.dirname(source_abs_path))
    file_spec = importlib.util.spec_from_file_location(module_name, source_abs_path)
    module = importlib.util.module_from_spec(file_spec)
    file_spec.loader.exec_module(module)
    return module


async def setup(loop):
    # 考虑启动方式，以及获取地址以及执行器名称，or default value
    address = os.environ.get('VOCANA_ADDRESS') if os.environ.get('VOCANA_ADDRESS') else 'mqtt://127.0.0.1:47688'
    name = os.environ.get('VOCANA_EXECUTOR') if os.environ.get('VOCANA_EXECUTOR') else 'python-executor'
    mainframe = Mainframe(address)
    mainframe.connect()

    future = None
    # 直接在 run 的 function 里面，publish message，在这个 mqtt 库里面，会一直发送不成功。目前是在主线程拿到 future 对象，绕过
    # FIXME: 问题是，如果连续 receive 两次，那么 future 可能会丢失，需要再兼容。
    def run(message):
        nonlocal future
        future = loop.create_future()
        future.set_result(message)
        
    mainframe.subscribe_executor(f'{name}', run)

    while True:
        await asyncio.sleep(1)
        if future is not None:
            message = await future
            setup_sdk(message, mainframe)
            future = None
        

def setup_sdk(message, mainframe):
    sdk = setup_vocana_sdk(mainframe, message['session_id'], message['job_id'])
    try:
        index_module = load_module(message['dir'])
        index_module.main(sdk.props, sdk)
    except Exception as e:
        print('Error:', repr(e))
        traceback_str = traceback.format_exc()
        sdk.send_error(traceback_str)
        sys.exit(1)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup(loop))
    loop.close()
