from oocana import Context, Mainframe
from dataclasses import dataclass
from typing import Optional, TypedDict
import inspect
import traceback
import logging
from .data import store, vars, EXECUTOR_NAME
from .context import createContext
from .hook import ExitFunctionException
import os
import sys
import importlib
import importlib.util
import threading


class ExecutorOptionsDict(TypedDict):
    function: Optional[str]
    entry: Optional[str]
    source: Optional[str]

# entry 与 source 是二选一的存在
class ExecutorDict(TypedDict):
    options: Optional[ExecutorOptionsDict]

tmp_files = set()

@dataclass
class ExecutePayload:
    session_id: str
    job_id: str
    dir: str
    executor: ExecutorDict
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

lock = threading.Lock()

def load_module(file_path: str, source_dir=None):

    if (os.path.isabs(file_path)):
        file_abs_path = file_path
    else:
        dirname = source_dir if source_dir else os.getcwd()
        file_abs_path = os.path.abspath(os.path.join(dirname, file_path))
    with lock:
        if file_abs_path in sys.modules:
            return sys.modules[file_abs_path]

        module_dir = os.path.dirname(file_abs_path)
        sys.path.insert(0, module_dir)

        file_spec = importlib.util.spec_from_file_location(file_abs_path, file_abs_path)
        module = importlib.util.module_from_spec(file_spec)  # type: ignore
        sys.modules[file_abs_path] = module

        file_spec.loader.exec_module(module)  # type: ignore
    return module


def output_return_object(obj, context: Context):
    if obj is None:
        context.done()
    elif obj is context.keepAlive:
        pass
    elif isinstance(obj, dict):
        for k, v in obj.items():
            context.output(k, v)
        context.done()
    else:
        context.done(f"return object needs to be a dictionary, but get type: {type(obj)}")

logger = logging.getLogger(EXECUTOR_NAME)

async def run_block(message, mainframe: Mainframe, session_dir: str):

    logger.info(f"block {message.get('job_id')} start")
    try:
        payload = ExecutePayload(**message)
        context = createContext(mainframe, payload.session_id, payload.job_id, store, payload.outputs, session_dir)
    except Exception:
        traceback_str = traceback.format_exc()
        # rust 那边会保证传过来的 message 一定是符合格式的，所以这里不应该出现异常。这里主要是防止 rust 修改错误。
        mainframe.send(
        {
            "job_id": message["job_id"],
            "session_id": message["session_id"],
        },
        {
            "type": "BlockFinished",
            "job_id": message["job_id"], 
            "error": traceback_str
        })
        return

    vars.set(context)

    load_dir = payload.dir

    options = payload.executor.get("options")

    node_id = context.node_id

    file_path = options["entry"] if options is not None and options.get("entry") is not None else 'index.py'

    source = options.get("source") if options is not None else None
    if source is not None:
        if not os.path.exists(load_dir):
            os.makedirs(load_dir)
        
        dir_path = os.path.join(load_dir, ".scriptlets")
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        tmp_py = os.path.join(dir_path, f"{node_id}.py")
        # 记录临时文件，但是现在不再清理
        tmp_files.add(tmp_py)

        with open(tmp_py, "w") as f:
            f.write(source)
        file_path = tmp_py

    try:
        # TODO: 这里的异常处理，应该跟详细一些，提供语法错误提示。
        index_module = load_module(file_path, load_dir) # type: ignore
    except Exception:
        traceback_str = traceback.format_exc()
        context.done(traceback_str)
        return
    function_name: str = options.get("function") if payload.executor is not None and options.get("function") is not None else 'main' # type: ignore
    fn = index_module.__dict__.get(function_name)

    if fn is None:
        context.done(f"function {function_name} not found in {file_path}")
        return
    if not callable(fn):
        context.done(f"{function_name} is not a function in {file_path}")
        return

    try:
        signature = inspect.signature(fn)
        params_count = len(signature.parameters)
        result = None
        traceback_str = None

        try:
            if inspect.iscoroutinefunction(fn):
                if params_count == 0:
                    result = await fn()
                elif params_count == 1:
                    only_context_param = list(signature.parameters.values())[0].annotation is Context
                    result = await fn(context) if only_context_param else await fn(context.inputs)
                else:
                    result = await fn(context.inputs, context)
            else:
                if params_count == 0:
                    result = fn()
                elif params_count == 1:
                    only_context_param = list(signature.parameters.values())[0].annotation is Context
                    result = fn(context) if only_context_param else fn(context.inputs)
                else:
                    result = fn(context.inputs, context)
        except ExitFunctionException as e:
            if e.args[0] is not None:
                context.done("block call exit with message: " + str(e.args[0]))
            else:
                context.done()
        except Exception:
            traceback_str = traceback.format_exc()

        if traceback_str is not None:
            context.done(traceback_str)
        else:
            output_return_object(result, context)
    except Exception:
        traceback_str = traceback.format_exc()
        context.done(traceback_str)
    finally:
        logger.info(f"block {message.get('job_id')} done")

