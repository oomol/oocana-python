#!/usr/bin/env python

import sys
import importlib
import importlib.util
import os
import traceback

from vocana import setup_vocana_sdk

def run():
    sdk = setup_vocana_sdk()
    try:
        index_module = load_module(get_source())
        index_module.main(sdk.props, sdk)
    except Exception:
        traceback_str = traceback.format_exc()
        sdk.send_error(traceback_str)
        sys.exit(1)

def get_source():
    source = sys.argv[1]
    if source is None or source == "":
        raise Exception("source file path is empty")
    return source.strip()

def load_module(source):
    if (os.path.isabs(source)):
        source_abs_path = source
    else:
        source_abs_path = os.path.join(os.getcwd(), source)

    module_name = os.path.basename(source_abs_path).replace('.py', '')
    file_spec = importlib.util.spec_from_file_location(module_name, source_abs_path)
    module = importlib.util.module_from_spec(file_spec)
    file_spec.loader.exec_module(module)
    return module

run()
