from oocana import Context, Mainframe
from dataclasses import dataclass
from typing import Optional, TypedDict
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import inspect
import traceback
import logging
from .data import store
from .context import createContext
import os
import sys
import importlib
import importlib.util


class ExecutorOptionsDict(TypedDict):
    function: Optional[str]
    entry: Optional[str]
    source: Optional[str]

# entry 与 source 是二选一的存在
class ExecutorDict(TypedDict):
    options: Optional[ExecutorOptionsDict]

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

def load_module(file_path: str, module_name: str, source_dir=None):

    if module_name in sys.modules:
        return sys.modules[module_name]

    if (os.path.isabs(file_path)):
        file_abs_path = file_path
    else:
        dirname = source_dir if source_dir else os.getcwd()
        file_abs_path = os.path.join(dirname, file_path)

    module_dir = os.path.dirname(file_abs_path)
    sys.path.insert(0, module_dir)


    file_spec = importlib.util.spec_from_file_location(module_name, file_abs_path)
    module = importlib.util.module_from_spec(file_spec)  # type: ignore
    sys.modules[module_name] = module

    file_spec.loader.exec_module(module)  # type: ignore
    return module


def output_return_object(obj, context: Context):
    if obj is None:
        context.done()
    elif obj is context.keepAlive:
        pass
    elif isinstance(obj, dict):
        for k, v in obj.items():
            context.output(v, k)
        context.done()
    else:
        context.done(f"return object needs to be a dictionary, but get type: {type(obj)}")

logger = logging.getLogger("EXECUTOR_NAME")

async def run_block(message, mainframe: Mainframe):

    logger.info(f"block {message.get('job_id')} start")
    try:
        payload = ExecutePayload(**message)
        context = createContext(mainframe, payload.session_id, payload.job_id, store, payload.outputs)
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


    load_dir = payload.dir

    options = payload.executor.get("options")

    node_id = context.node_id

    file_path = options["entry"] if options is not None and options.get("entry") is not None else 'index.py'

    source = options.get("source") if options is not None else None
    if source is not None:
        # write source to file 
        if not os.path.exists(load_dir):
            os.makedirs(load_dir)
        
        dir_path = os.path.join(load_dir, ".scriptlets")
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        with open(os.path.join(dir_path, f"{node_id}.py"), "w") as f:
            f.write(source)
        file_path = os.path.join(dir_path, f"{node_id}.py")

    try:
        # TODO: 这里的异常处理，应该跟详细一些，提供语法错误提示。
        index_module = load_module(file_path, payload.session_id+node_id, load_dir) # type: ignore
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
        # 多进程的 stdout 和 stderr 是互相独立不影响的；
        # 目前使用的多线程的 stdout 和 stderr 是共享的，导致目前的 redirect_stdout 和 redirect_stderr 会捕获到其他线程的输出。
        with redirect_stderr(StringIO()) as stderr, redirect_stdout(StringIO()) as stdout:
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
            except Exception:
                traceback_str = traceback.format_exc()

        for line in stdout.getvalue().splitlines():
            context.report_log(line)
        for line in stderr.getvalue().splitlines():
            context.report_log(line, "stderr")

        if traceback_str is not None:
            context.done(traceback_str)
        else:
            output_return_object(result, context)
    except Exception:
        traceback_str = traceback.format_exc()
        context.done(traceback_str)
    finally:
        logger.info(f"block {message.get('job_id')} done")

