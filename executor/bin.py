#!/usr/bin/env python

import sys
import json
import os
import traceback
import importlib
import importlib.util
from vocana import setup_vocana_sdk, Mainframe

mainframe

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

def setup():
    # 考虑启动方式，以及获取地址以及执行器名称，or default value
    address = os.environ.get('VOCANA_ADDRESS') if os.environ.get('VOCANA_ADDRESS') else 'mqtt://127.0.0.1:8080'
    executor = os.environ.get('VOCANA_EXECUTOR') if os.environ.get('VOCANA_EXECUTOR') else 'python-executor'
    global mainframe
    mainframe = Mainframe(address)
    mainframe.connect()

    def run(message):
        try:
            start_args = json.loads(message.payload)
            sdk = setup_vocana_sdk(mainframe, start_args['session_id'], start_args['job_id'])
            index_module = load_module(start_args['source'])
            index_module.main(sdk.props, sdk)
        except Exception:
            traceback_str = traceback.format_exc()
            mainframe.send_error(traceback_str)
            sys.exit(1)

    mainframe.subscribe(f'{executor}', run)


setup()
