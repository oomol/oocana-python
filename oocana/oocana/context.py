import asyncio
from dataclasses import asdict
from .data import BlockInfo, StoreKey, JobDict, BlockDict, BinValueDict, VarValueDict
from .mainframe import Mainframe
from .handle_data import HandleDef
from typing import Dict, Any, TypedDict, Optional, Callable, Mapping
from types import MappingProxyType
from base64 import b64encode
from io import BytesIO
from .throttler import throttle
from .preview import PreviewPayload, DataFrame, ShapeDataFrame
from .data import EXECUTOR_NAME
import os.path
import logging
import random
import string

__all__ = ["Context", "HandleDefDict", "RunResponse", "BlockFinishPayload"]

def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

class BlockFinishPayload(TypedDict):
    """
    A payload that represents the block finish message.
    """

    result: Dict[str, Any] | None
    """the result of the block, should be a dict, if the block has no result, this field should be None.
    """

    error: str | None
    """the error message of the block, if the block has no error, this field should be None.
    """

class RunResponse:

    __outputs_callbacks: set[Callable[[str, Any], None]]
    __events: set[Callable[[Dict[str, Any]], None]]
    __finish_future: asyncio.Future[BlockFinishPayload]

    def __init__(self, event_callbacks: set[Callable[[Dict[str, Any]], None]], outputs_callbacks: set[Callable[[str, Any], None]], future: asyncio.Future[BlockFinishPayload]) -> None:
        self.__outputs_callbacks = outputs_callbacks
        self.__events = event_callbacks
        self.__finish_future = future

    def add_output_callback(self, fn: Callable[[str, Any], None]):
        """
        register a callback function to handle the output of the block.
        :param fn: the callback function, it should accept two arguments, the first is the handle of the output, the second is the value of the output.
        """
        if not callable(fn):
            raise ValueError("output_callback should be a callable function.")
        self.__outputs_callbacks.add(fn)

    # todo: add more detail about the event payload.
    def add_event_callback(self, fn: Callable[[Dict[str, Any]], None]):
        """
        register a callback function to handle the events of the block.
        :param fn: the callback function, it should accept a single argument, which is the event payload.
        """
        if not callable(fn):
            raise ValueError("event_callback should be a callable function.")
        self.__events.add(fn)

    def finish(self) -> asyncio.Future[BlockFinishPayload]:
        return self.__finish_future

class HandleDefDict(TypedDict):
    """a dict that represents the handle definition, used in the block schema output and input defs.
    """

    handle: str
    """the handle of the output, should be defined in the block schema output defs, the field name is handle
    """

    description: str | None
    """the description of the output, should be defined in the block schema output defs, the field name is description
    """

    json_schema: Dict[str, Any] | None
    """the schema of the output, should be defined in the block schema output defs, the field name is json_schema
    """

    kind: str | None
    """the kind of the output, should be defined in the block schema output defs, the field name is kind
    """

    nullable: bool
    """if the output can be None, should be defined in the block schema output defs, the field name is nullable
    """

    is_additional: bool
    """if the output is an additional output, should be defined in the block schema output defs, the field name is is_additional
    """

class OnlyEqualSelf:
    def __eq__(self, value: object) -> bool:
        return self is value

class OOMOL_LLM_ENV(TypedDict):
    base_url: str
    """{basUrl}/v1 openai compatible endpoint
    """
    base_url_v1: str
    api_key: str
    models: list[str]

class HostInfo(TypedDict):
    gpu_vendor: str
    gpu_renderer: str

class Context:
    __inputs: Dict[str, Any]

    __block_info: BlockInfo
    __outputs_def: Dict[str, HandleDef]
    # Only dict can support some field type like `Optional[FieldSchema]`(this key can not in dict). Dataclass will always convert it to None if the field is not set which will cause some issues.
    __outputs_def_dict: Dict[str, HandleDefDict]
    __inputs_def: Dict[str, HandleDefDict]
    __store: Any
    __keep_alive: OnlyEqualSelf = OnlyEqualSelf()
    __session_dir: str
    __tmp_dir: str
    __package_name: str | None = None
    _logger: Optional[logging.Logger] = None
    __pkg_dir: str

    def __init__(
        self, *, inputs: Dict[str, Any], blockInfo: BlockInfo, mainframe: Mainframe, store, inputs_def, outputs_def: Dict[str, Any], session_dir: str, tmp_dir: str, package_name: str, pkg_dir: str
    ) -> None:

        self.__block_info = blockInfo

        self.__mainframe = mainframe
        self.__store = store
        self.__inputs = inputs

        self.__outputs_def_dict = outputs_def
        outputs_defs_cls = {}
        if outputs_def is not None:
            for k, v in outputs_def.items():
                outputs_defs_cls[k] = HandleDef(**v)
        self.__outputs_def = outputs_defs_cls
        self.__inputs_def = inputs_def
        self.__session_dir = session_dir
        self.__tmp_dir = tmp_dir
        self.__package_name = package_name
        self.__pkg_dir = pkg_dir

    @property
    def logger(self) -> logging.Logger:
        """a custom logger for the block, you can use it to log the message to the block log. this logger will report the log by context report_logger api.
        """

        # setup after init, so the logger always exists
        if self._logger is None:
            raise ValueError("logger is not setup, please setup the logger in the block init function.")
        return self._logger

    @property
    def session_dir(self) -> str:
        """a temporary directory for the current session, all blocks in the one session will share the same directory.
        """
        return self.__session_dir
    
    @property
    def tmp_dir(self) -> str:
        """a temporary directory for the current follow, all blocks in the this flow will share the same directory. this directory will be cleaned if this session finish successfully, otherwise it will be kept for debugging or other purpose.
        """
        return self.__tmp_dir
    
    @property
    def tmp_pkg_dir(self) -> str:
        """a temporary directory for the current package, all blocks in the this package will share the same directory. this directory will be cleaned if this session finish successfully, otherwise it will be kept for debugging or other purpose.
        """
        return os.path.join(self.__tmp_dir, self.__package_name) if self.__package_name else self.__tmp_dir

    @property
    def pkg_dir(self) -> str:
        """a directory for the current package, all blocks in the this package will share the same directory. this directory will be cleaned if this session finish successfully, otherwise it will be kept for debugging or other purpose.
        """
        return self.__pkg_dir

    @property
    def keepAlive(self):
        return self.__keep_alive

    @property
    def inputs(self):
        return self.__inputs
    
    @property
    def inputs_def(self) -> Mapping[str, HandleDefDict]:
        """a dict that represents the input definitions, used in the block schema input defs.
        This is a read-only property, you can not modify it.
        """
        return MappingProxyType(self.__inputs_def) if self.__inputs_def is not None else MappingProxyType({})

    @property
    def outputs_def(self) -> Mapping[str, HandleDefDict]:
        """a dict that represents the output definitions, used in the block schema output defs.
        This is a read-only property, you can not modify it.
        """
        return MappingProxyType(self.__outputs_def_dict) if self.__outputs_def_dict is not None else MappingProxyType({})

    @property
    def session_id(self):
        return self.__block_info.session_id

    @property
    def job_id(self):
        return self.__block_info.job_id
    
    @property
    def job_info(self) -> JobDict:
        return self.__block_info.job_info()
    
    @property
    def block_info(self) -> BlockDict:
        return self.__block_info.block_dict()
    
    @property
    def node_id(self) -> str:
        return self.__block_info.stacks[-1].get("node_id", None)
    
    @property
    def oomol_llm_env(self) -> OOMOL_LLM_ENV:
        """this is a dict contains the oomol llm environment variables
        """

        oomol_llm_env: OOMOL_LLM_ENV = {
            "base_url": os.getenv("OOMOL_LLM_BASE_URL", ""),
            "base_url_v1": os.getenv("OOMOL_LLM_BASE_URL_V1", ""),
            "api_key": os.getenv("OOMOL_LLM_API_KEY", ""),
            "models": os.getenv("OOMOL_LLM_MODELS", "").split(","),
        }

        for key, value in oomol_llm_env.items():
            if value == "" or value == []:
                self.send_warning(
                    f"OOMOL_LLM_ENV variable {key} is ({value}), this may cause some features not working properly."
                )

        return oomol_llm_env

    @property
    def host_info(self) -> HostInfo:
        """this is a dict contains the host information
        """
        return {
            "gpu_vendor": os.getenv("OOMOL_HOST_GPU_VENDOR", "unknown"),
            "gpu_renderer": os.getenv("OOMOL_HOST_GPU_RENDERER", "unknown"),
        }

    @property
    def host_endpoint(self) -> str | None:
        """A host endpoint that allows containers to access services running on the host system.
        
        Returns:
            str: The host endpoint if available.
            None: If the application is running in a cloud environment where no host endpoint is defined.
        """
        return os.getenv("OO_HOST_ENDPOINT", None)

    def __store_ref(self, handle: str):
        return StoreKey(
            executor=EXECUTOR_NAME,
            handle=handle,
            job_id=self.job_id,
            session_id=self.session_id,
        )
    
    def __is_basic_type(self, value: Any) -> bool:
        return isinstance(value, (int, float, str, bool))
    
    def __wrap_output_value(self, handle: str, value: Any):
        """
        wrap the output value:
        if the value is a var handle, store it in the store and return the reference.
        if the value is a bin handle, store it in the store and return the reference.
        if the handle is not defined in the block outputs schema, raise an ValueError.
        otherwise, return the value.
        :param handle: the handle of the output
        :param value: the value of the output
        :return: the wrapped value
        """
        # __outputs_def should never be None
        if self.__outputs_def is None:
            return value
        
        output_def = self.__outputs_def.get(handle)
        if output_def is None:
            raise ValueError(
                f"Output handle key: [{handle}] is not defined in Block outputs schema."
            )
        
        if output_def.is_var_handle() and not self.__is_basic_type(value):
            ref = self.__store_ref(handle)
            self.__store[ref] = value
            var: VarValueDict = {
                "__OOMOL_TYPE__": "oomol/var",
                "value": asdict(ref)
            }
            return var
        
        if output_def.is_bin_handle():
            if not isinstance(value, bytes):
                self.send_warning(
                    f"Output handle key: [{handle}] is defined as binary, but the value is not bytes."
                )
                return value
            
            bin_file = f"{self.session_dir}/binary/{self.session_id}/{self.job_id}/{handle}"
            os.makedirs(os.path.dirname(bin_file), exist_ok=True)
            try:
                with open(bin_file, "wb") as f:
                    f.write(value)
            except IOError as e:
                raise IOError(
                    f"Output handle key: [{handle}] is defined as binary, but an error occurred while writing the file: {e}"
                )

            if os.path.exists(bin_file):
                bin_value: BinValueDict = {
                    "__OOMOL_TYPE__": "oomol/bin",
                    "value": bin_file,
                }
                return bin_value
            else:
                raise IOError(
                    f"Output handle key: [{handle}] is defined as binary, but the file is not written."
                )
        return value

    def output(self, key: str, value: Any):
        """
        output the value to the next block

        key: str, the key of the output, should be defined in the block schema output defs, the field name is handle
        value: Any, the value of the output
        """

        try:
            wrap_value = self.__wrap_output_value(key, value)
        except ValueError as e:
            self.send_warning(
                f"{e}"
            )
            return
        except IOError as e:
            self.send_warning(
                f"{e}"
            )
            return

        node_result = {
            "type": "BlockOutput",
            "handle": key,
            "output": wrap_value,
        }
        self.__mainframe.send(self.job_info, node_result)
    
    def outputs(self, outputs: Dict[str, Any]):
        """
        output the value to the next block

        map: Dict[str, Any], the key of the output, should be defined in the block schema output defs, the field name is handle
        """

        values = {}
        for key, value in outputs.items():
            try:
                wrap_value = self.__wrap_output_value(key, value)
                values[key] = wrap_value
            except ValueError as e:
                self.send_warning(
                    f"{e}"
                )
            except IOError as e:
                self.send_warning(
                    f"{e}"
                )
        self.__mainframe.send(self.job_info, {
            "type": "BlockOutputs",
            "outputs": values,
        })

        

    def finish(self, *, result: Dict[str, Any] | None = None, error: str | None = None):
        """
        finish the block, and send the result to oocana.
        if error is not None, the block will be finished with error.
        then if result is not None, the block will be finished with result.
        lastly, if both error and result are None, the block will be finished without any result.
        """

        if error is not None:
            self.__mainframe.send(self.job_info, {"type": "BlockFinished", "error": error})
        elif result is not None:
            wrap_result = {}
            if isinstance(result, dict):
                for key, value in result.items():
                    try:
                        wrap_result[key] = self.__wrap_output_value(key, value)
                    except ValueError as e:
                        self.send_warning(
                            f"Output handle key: [{key}] is not defined in Block outputs schema. {e}"
                        )
                    except IOError as e:
                        self.send_warning(
                            f"Output handle key: [{key}] is not defined in Block outputs schema. {e}"
                        )

                self.__mainframe.send(self.job_info, {"type": "BlockFinished", "result": wrap_result})
            else:
                raise ValueError(
                    f"result should be a dict, but got {type(result)}"
                )
        else:
            self.__mainframe.send(self.job_info, {"type": "BlockFinished"})

    def send_message(self, payload):
        self.__mainframe.report(
            self.block_info,
            {
                "type": "BlockMessage",
                "payload": payload,
            },
        )
    
    def __dataframe(self, payload: PreviewPayload) -> PreviewPayload:
        target_dir = os.path.join(self.tmp_dir, self.job_id)
        os.makedirs(target_dir, exist_ok=True)
        csv_file = os.path.join(target_dir, f"{random_string(8)}.csv")
        if isinstance(payload, DataFrame):
            payload.to_csv(path_or_buf=csv_file)
            payload = { "type": "table", "data": csv_file}

        if isinstance(payload, dict) and payload.get("type") == "table":
            df = payload.get("data")
            if isinstance(df, ShapeDataFrame):
                df.to_csv(path_or_buf=csv_file)
                payload = { "type": "table", "data": csv_file }
            else:
                print("dataframe is not support shape property")
        
        return payload

    def __matplotlib(self, payload: PreviewPayload) -> PreviewPayload:
        # payload is a matplotlib Figure
        if hasattr(payload, 'savefig'):
            fig: Any = payload
            buffer = BytesIO()
            fig.savefig(buffer, format='png')
            buffer.seek(0)
            png = buffer.getvalue()
            buffer.close()
            url = f'data:image/png;base64,{b64encode(png).decode("utf-8")}'
            payload = { "type": "image", "data": url }

        return payload

    def preview(self, payload: PreviewPayload):
        payload = self.__dataframe(payload)
        payload = self.__matplotlib(payload)

        self.__mainframe.report(
            self.block_info,
            {
                "type": "BlockPreview",
                "payload": payload,
            },
        )

    @throttle(0.3)
    def report_progress(self, progress: float | int):
        """report progress

        This api is used to report the progress of the block. but it just effect the ui progress not the real progress.
        This api is throttled. the minimum interval is 0.3s. 
        When you first call this api, it will report the progress immediately. After it invoked once, it will report the progress at the end of the throttling period.

        |       0.25 s        |   0.2 s  |
        first call       second call    third call  4 5 6 7's calls
        |                     |          |          | | | |
        | -------- 0.3 s -------- | -------- 0.3 s -------- |
        invoke                  invoke                    invoke
        :param float | int progress: the progress of the block, the value should be in [0, 100].
        """
        self.__mainframe.report(
            self.block_info,
            {
                "type": "BlockProgress",
                "rate": progress,
            }
        )

    def report_log(self, line: str, stdio: str = "stdout"):
        self.__mainframe.report(
            self.block_info,
            {
                "type": "BlockLog",
                "log": line,
                stdio: stdio,
            },
        )

    def log_json(self, payload):
        self.__mainframe.report(
            self.block_info,
            {
                "type": "BlockLogJSON",
                "json": payload,
            },
        )

    def send_warning(self, warning: str):
        self.__mainframe.report(self.block_info, {"type": "BlockWarning", "warning": warning})

    def send_error(self, error: str):
        '''
        deprecated, use error(error) instead.
        consider to remove in the future.
        '''
        self.error(error)

    def error(self, error: str):
        self.__mainframe.send(self.job_info, {"type": "BlockError", "error": error})

    def run_block(self, block: str, inputs: Dict[str, Any]) -> RunResponse:
        """
        run a block with the given inputs.
        :param block: the id of the block to run
        :param inputs: the inputs of the block

        Returns:
            RunResponse: a RunResponse object, which contains the event callbacks and output callbacks.
            You can use the `add_event_callback` and `add_output_callback` methods to register callbacks for the events and outputs of the block.
            You can also use the `finish` method to wait for the block to finish and get the result.
        """

        # consider use uuid, remove job_id and block_job_id.
        block_job_id = f"{self.job_id}-{block}-{random_string(8)}"
        request_id = random_string(16)
        self.__mainframe.send(self.job_info, {
            "type": "BlockRequest",
            "action": "RunBlock",
            "block": block,
            "block_job_id": block_job_id,
            "inputs": inputs,
            "stacks": self.__block_info.stacks,
            "request_id": request_id,
        })

        event_callbacks = set()
        outputs_callbacks = set()

        # run_block will always run in a coroutine, so we can use asyncio.Future to wait for the result.
        loop = asyncio.get_running_loop()
        future: asyncio.Future[BlockFinishPayload] = loop.create_future()

        def response_callback(payload: Dict[str, Any]):
            """
            This callback is called when an error occurs while running a block.
            It will call the error callbacks registered by the user.
            """
            if payload.get("request_id") != request_id:
                return

            def set_future_with_error():
                if not future.done():
                    future.set_result({
                        "result": None,
                        "error": payload.get("error", "Unknown error occurred while running the block.")
                    })
            loop.call_soon_threadsafe(set_future_with_error)

        def event_callback(payload: Dict[str, Any]):

            if payload.get("job_id") != block_job_id:
                return
            elif payload.get("type") == "ExecutorReady" or payload.get("type") == "BlockReady" or payload.get("type") == "BlockRequest":
                # ignore these messages
                return

            for callback in event_callbacks:
                callback(payload)

            if payload.get("type") == "BlockOutput":
                for callback in outputs_callbacks:
                    callback(payload.get("handle"), payload.get("output"))
            elif payload.get("type") == "BlockOutputs":
                for handle, value in payload.get("outputs", {}).items():
                    for callback in outputs_callbacks:
                        callback(handle, value)
            elif payload.get("type") == "BlockFinished":
                result = payload.get("result")
                if result is not None and not isinstance(result, dict):
                    pass
                elif result is not None:
                    for handle, value in result.items():
                        for callback in outputs_callbacks:
                            callback(handle, value)

                self.__mainframe.remove_session_callback(self.session_id, event_callback)
                self.__mainframe.remove_request_response_callback(self.session_id, request_id, response_callback)

                def set_future_result():
                    if not future.done():
                        future.set_result({"result": payload.get("result"), "error": payload.get("error")})

                loop.call_soon_threadsafe(set_future_result)


        self.__mainframe.add_session_callback(self.session_id, event_callback)
        self.__mainframe.add_request_response_callback(self.session_id, request_id, response_callback)

        return RunResponse(event_callbacks, outputs_callbacks, future)