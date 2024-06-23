#!/usr/bin/env python

import asyncio
import importlib
import importlib.util
import inspect
import os
import queue
import sys
import traceback
import logging
import json
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from io import StringIO
from typing import Optional, Any, TypedDict
from oocana import Mainframe, StoreKey, Context, can_convert_to_var_handle_def, BlockInfo


logger = logging.getLogger(__name__)
EXECUTOR_NAME = "python_executor"
SECRET_FILE = "/home/ovm/app-config/oomol-secrets/secrets.json"

def createContext(
    mainframe: Mainframe, session_id: str, job_id: str, store, output
) -> Context:

    node_props = mainframe.notify_ready(session_id, job_id)

    inputs_def = node_props.get("inputs_def")
    inputs = node_props.get("inputs")

    try:
        secretJson = json.load(open(SECRET_FILE))
    except FileNotFoundError:
        logger.warning(f"secret file {SECRET_FILE} not found")
        secretJson = None
    except json.JSONDecodeError:
        logger.error(f"secret file {SECRET_FILE} is not a valid json file")
        secretJson = None

    if inputs_def is not None and inputs is not None:
        for k, v in inputs_def.items():
            if can_convert_to_var_handle_def(v):
                try:
                    ref = StoreKey(**inputs[k])
                except:  # noqa: E722
                    print(f"not valid object ref: {inputs[k]}")
                    continue

                value = store.get(ref)
                inputs[k] = value
            elif is_secret(v):
                inputs[k] = replace_secret(inputs[k], secretJson)

    elif inputs is None:
        inputs = {}
    
    blockInfo = BlockInfo(**node_props)

    return Context(inputs, blockInfo, mainframe, store, output)

def is_secret(value: dict):
    if not isinstance(value, dict):
        return False
    
    serialize = value.get("serialize")
    if serialize is None or isinstance(serialize, dict) is False:
        return False

    if serialize.get("serializer") != "json":
        return False
    
    json_schema = serialize.get("json_schema")
    if json_schema is None or isinstance(json_schema, dict) is False:
        return False
    
    return json_schema.get("ui:widget") == "secret"

def replace_secret(path: str, secretJson: dict | None) -> str:
    if secretJson is None:
        # throw error
        logger.error(f"secret file {SECRET_FILE} not found")
        raise ValueError("secret file not found or invalid json file")

    assert isinstance(secretJson, dict)

    try:
        [secretType, secretName, secretKey] =  path.split(",")
    except ValueError:
        logger.error(f"invalid secret path: {path}")
        return ""
    
    s = secretJson.get(secretName)

    if s is None:
        logger.error(f"secret {secretName} not found in {SECRET_FILE}")
        return ""

    if s.get("secretType") != secretType:
        logger.warning(f"secret type mismatch: {s.get('secretType')} != {secretType}")

    secrets: list[Any] = s.get("secrets")
    if secrets:
        for secret in secrets:
            if secret.get("secretKey") == secretKey:
                return secret.get("value")
    else:
        logger.error(f"secret {secretName} has no value")
        return ""

    logger.error(f"secret {secretKey} not found in {secretName}")
    return ""

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

store = {}

def load_module(source, source_dir=None):
    if (os.path.isabs(source)):
        source_abs_path = source
    else:
        dirname = source_dir if source_dir else os.getcwd()
        source_abs_path = os.path.join(dirname, source)

    module_name = os.path.basename(source_abs_path).replace('.py', '')
    sys.path.append(os.path.dirname(source_abs_path))
    file_spec = importlib.util.spec_from_file_location(module_name, source_abs_path)
    module = importlib.util.module_from_spec(file_spec) # type: ignore
    file_spec.loader.exec_module(module) # type: ignore
    return module


async def setup(loop):
    # 考虑启动方式，以及获取地址以及执行器名称，or default value
    address = os.environ.get('ADDRESS') if os.environ.get('ADDRESS') else 'mqtt://127.0.0.1:47688'
    # name = os.environ.get('EXECUTOR') if os.environ.get('EXECUTOR') else 'python_executor'
    mainframe = Mainframe(address) # type: ignore
    mainframe.connect()

    # 这个日志，用来告知 bin 模式调用时，连接成功。所以这个格式要主动输出保持不变。
    print(f"connecting to broker {address} success")
    # 子进程模式启动时，Python 不会立刻输出，我们需要这一行日志的输出，所以主动 flush 一次。
    sys.stdout.flush()

    log_dir: str = os.environ.get('LOG_DIR') if os.environ.get('LOG_DIR') else "/ovm/.oomol-studio" # type: ignore

    if os.path.exists(log_dir):
        file_name = log_dir + '/executor/python.log'
        if not os.path.exists(file_name):
            os.makedirs(os.path.dirname(file_name), exist_ok=True)
            open(file_name, 'w').close()

        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filename=log_dir + '/executor/python.log')
        logger.info("setup basic logging in file ~/.oomol-studio/executor/python.log")
    else:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
        logger.info("setup basic logging in console")

    fs = queue.Queue()
    def run(message):
        nonlocal fs
        # 在当前使用的 mqtt 库里，如果在 subscribe 之后，直接 publish 消息，会一直阻塞无法发送成功。
        # 所以要切换线程后，再进行 publish。这里使用 future 来实现线程切换和数据传递。
        f = loop.create_future()
        fs.put(f)
        f.set_result(message)

    def drop(message):
        obj = StoreKey(**message)
        o = store.get(obj)
        if o is not None:
            logger.info(f"drop {obj.job_id} {obj.handle}")
            del store[obj]

    mainframe.subscribe(f"executor/{EXECUTOR_NAME}/execute", run)
    mainframe.subscribe(f"executor/{EXECUTOR_NAME}/drop", drop)

    while True:
        await asyncio.sleep(1)
        if not fs.empty():
            f = fs.get()
            message = await f
            await run_block(message, mainframe)

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

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(setup(loop))
    loop.close()
