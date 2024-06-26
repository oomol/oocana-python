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

def load_module(source: str, source_dir=None):


    if (os.path.isabs(source)):
        source_abs_path = source
    else:
        dirname = source_dir if source_dir else os.getcwd()
        source_abs_path = os.path.join(dirname, source)

    is_directory_module = os.path.isdir(source) or source.endswith('__init__.py')
    module_name = os.path.basename(source_abs_path).replace('.py', '') if not is_directory_module else os.path.basename(os.path.dirname(source_abs_path))
    module_dir = os.path.dirname(source_abs_path)

    # 在sys.path中临时添加模块所在目录
    original_sys_path = sys.path.copy()
    sys.path.append(module_dir)

    try:
        # 加载模块
        file_spec = importlib.util.spec_from_file_location(module_name, source_abs_path)
        module = importlib.util.module_from_spec(file_spec)  # type: ignore

        if is_directory_module:
            sys.modules[module_name] = module

        file_spec.loader.exec_module(module)  # type: ignore
        return module
    finally:
        # 恢复原始的sys.path
        sys.path = original_sys_path


def output_return_object(obj, context: Context):
    if obj is None:
        context.done()
    elif obj is context.keepAlive:
        pass
    elif isinstance(obj, dict):
        for k, v in obj.items():
            context.output(v, k)
    else:
        context.done("return value needs to be a dict")

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
    source = config["entry"] if config is not None and config.get("entry") is not None else 'index.py'

    try:
        # TODO: 这里的异常处理，应该跟详细一些，提供语法错误提示。
        index_module = load_module(source, load_dir)
    except Exception:
        traceback_str = traceback.format_exc()
        context.done(traceback_str)
        return
    function_name: str = payload.executor["function"] if payload.executor is not None and payload.executor.get("function") is not None else 'main' # type: ignore
    fn = index_module.__dict__.get(function_name)

    if fn is None:
        context.done(f"function {function_name} not found in {source}")
        return
    if not callable(fn):
        context.done(f"{function_name} is not a function in {source}")
        return

    try:
        # TODO: 这种重定向 stdout 和 stderr 的方式比较优雅，但是由于仍然是替换的全局 sys.stdout 和 sys.stderr 对象，所以在协程切换时，仍然会有错乱的问题。
        #       目前任务是一个个排队执行，因此暂时不会出现错乱。
        #       应该和 nodejs 寻找替换 function，在 function 里面读取 contextvars，来进行分发。大体的尝试代码写在 ./ctx.py 里，有时间，或者有需求时，再进行完善。
        with redirect_stderr(StringIO()) as stderr, redirect_stdout(StringIO()) as stdout:
            if inspect.iscoroutinefunction(fn):
                result = await fn(context.inputs, context)
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

