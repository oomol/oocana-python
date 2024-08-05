import sys

store = {}
serviceMap = {}
original_sys_keys = set(sys.modules.keys())
original_sys_path = sys.path.copy()
