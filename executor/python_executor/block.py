from oocana import Context, Mainframe
from dataclasses import dataclass
from typing import Optional, TypedDict
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import inspect
import traceback
import logging
from .data import store, original_sys_path, original_sys_keys
from .context import createContext
import os
import sys
import importlib
import importlib.util

class ExecutorDict(TypedDict):
    entry: Optional[str]
    function: Optional[str]


@dataclass
class ExecutePayload:
    session_id: str
    job_id: str
    dir: str
    executor: Optional[ExecutorDict] = None
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
            "job_id": message["job_id"], 
            "error": traceback_str
        })
        return


    load_dir = payload.dir

    config = payload.executor
    file_path = config["entry"] if config is not None and config.get("entry") is not None else 'index.py'

    stacks = message.get("stacks")
    node_id = stacks[-1]["node_id"]

    try:
        # TODO: 这里的异常处理，应该跟详细一些，提供语法错误提示。
        index_module = load_module(file_path, payload.session_id+node_id, load_dir) # type: ignore
    except Exception:
        traceback_str = traceback.format_exc()
        context.done(traceback_str)
        return
    function_name: str = payload.executor["function"] if payload.executor is not None and payload.executor.get("function") is not None else 'main' # type: ignore
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
        # TODO: 这种重定向 stdout 和 stderr 的方式比较优雅，但是由于仍然是替换的全局 sys.stdout 和 sys.stderr 对象，所以在协程切换时，仍然会有错乱的问题。
        #       目前任务是一个个排队执行，因此暂时不会出现错乱。
        #       应该和 nodejs 寻找替换 function，在 function 里面读取 contextvars，来进行分发。大体的尝试代码写在 ./ctx.py 里，有时间，或者有需求时，再进行完善。
        with redirect_stderr(StringIO()) as stderr, redirect_stdout(StringIO()) as stdout:
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
        output_return_object(result, context)

        for line in stdout.getvalue().splitlines():
            context.report_log(line)
        for line in stderr.getvalue().splitlines():
            context.report_log(line, "stderr")
    except Exception:
        traceback_str = traceback.format_exc()
        context.done(traceback_str)
    finally:
        logger.info(f"block {message.get('job_id')} done")

