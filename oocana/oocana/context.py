import asyncio
from dataclasses import asdict
from .data import BlockInfo, StoreKey, JobDict, BlockDict, BinValueDict, VarValueDict
from .mainframe import Mainframe
from .handle import OutputHandleDef
from typing import Dict, Any, TypedDict, Optional, Callable, Mapping, Literal
from types import MappingProxyType
from base64 import b64encode
from io import BytesIO
from .throttler import throttle
from .preview import PreviewPayload, DataFrame, PreviewPayloadInternal, ShapeDataFrame
from .data import EXECUTOR_NAME
import os.path
import logging
import random
import string
import hashlib

__all__ = ["Context", "HandleDefDict", "BlockJob", "BlockExecuteException"]

def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def string_hash(text: str) -> str:
    """
    Generates a deterministic hash for a given string.
    """
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

class ToNode(TypedDict):
    node_id: str

    input_handle: str

class ToFlow(TypedDict):
    output_handle: str

class BlockExecuteException(Exception):
    """Exception raised when a block execution fails."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"BlockExecuteException: {self.message}"

class BlockJob:

    __outputs_callbacks: set[Callable[[Dict[str, Any]], None]]
    __progress_callbacks: set[Callable[[float | int], None]]
    __finish_future: asyncio.Future[None]

    def __init__(self, outputs_callbacks: set[Callable[[Dict[str, Any]], None]], progress_callbacks: set[Callable[[float | int], None]], future: asyncio.Future[None]) -> None:
        self.__outputs_callbacks = outputs_callbacks
        self.__progress_callbacks = progress_callbacks
        self.__finish_future = future

    def add_output_callback(self, fn: Callable[[Dict[str, Any]], None]):
        """Register a callback function to handle the output of the block.
        :param fn: the callback function, it should accept a dict as the first parameter, the output handle will be the key, and the output value will be the value.

        Note: the callback function is running in mqtt's callback thread, so it currently does not support run context.sendXX message directly.
        """
        if not callable(fn):
            raise ValueError("output_callback should be a callable function.")
        self.__outputs_callbacks.add(fn)

    def add_progress_callback(self, fn: Callable[[float | int], None]):
        """Register a callback function to handle the progress of the block.
        :param fn: the callback function, it should accept a float or int as the first parameter, the progress value will be passed to the callback function.

        Note: the callback function is running in mqtt's callback thread, so it currently does not support run context.sendXX message directly.
        """
        if not callable(fn):
            raise ValueError("progress_callback should be a callable function.")
        self.__progress_callbacks.add(fn)

    def finish(self) -> asyncio.Future[None]:
        """Wait for the block to finish and return the future.
        
        Returns:
            asyncio.Future: A future that will be resolved when the block finishes.
            If the block finishes with an error, the future will throw a Exception.
        """
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

class QueryBlockResponse(TypedDict):

    type: Literal["task", "subflow"]
    """the type of the block, can be "task" or "subflow"."""

    description: str | None
    """the description of the block, if the block has no description, this field should be
    None.
    """

    inputs_def: Dict[str, HandleDefDict] | None
    """the inputs of the block, should be a dict, if the block has no inputs
    this field should be None.
    """

    outputs_def: Dict[str, HandleDefDict] | None
    """the outputs of the block, should be a dict, if the block has no outputs  
    this field should be None.
    """

    additional_outputs: bool
    """if the block author declare this block accept additional outputs, this field should be True, otherwise False.
    """

    additional_inputs: bool
    """if the block author declare this block accept additional inputs, this field should be True, otherwise False.
    """


class FlowDownstream(TypedDict):
    output_handle: str
    output_handle_def: HandleDefDict | None

class NodeDownstream(TypedDict):
    node_id: str
    description: str | None
    """node description"""
    input_handle: str
    input_handle_def: HandleDefDict | None

class Downstream(TypedDict):
    to_flow: list[FlowDownstream]
    to_node: list[NodeDownstream]

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
    __outputs_def: Dict[str, OutputHandleDef]
    # Only dict can support some field type like `Optional[FieldSchema]`(this key can not in dict). Dataclass will always convert it to None if the field is not set which will cause some issues.
    __outputs_def_dict: Dict[str, HandleDefDict]
    __inputs_def: Dict[str, HandleDefDict]
    __store: Any
    __keep_alive: OnlyEqualSelf = OnlyEqualSelf()
    __session_dir: str
    __tmp_dir: str
    __package_name: str | None = None
    _logger: Optional[logging.Logger] = None
    __pkg_data_dir: str

    # TODO: remove the pkg_dir parameter, use pkg_data_dir instead.
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
                outputs_defs_cls[k] = OutputHandleDef(**v)
        self.__outputs_def = outputs_defs_cls
        self.__inputs_def = inputs_def
        self.__session_dir = session_dir
        self.__tmp_dir = tmp_dir
        self.__package_name = package_name
        self.__pkg_data_dir = pkg_dir

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
        """Deprecated, use pkg_data_dir instead.
        """
        return self.__pkg_data_dir

    @property
    def pkg_data_dir(self) -> str:
        """A directory for the current package data, all blocks in this package will share the same directory. 
        This directory's content will be persisted after the session finishes, so you can use it to store some data that need to be shared between blocks in the same package.
        Please note that this directory is not cleaned after the session finishes, so you need to manage the content of this directory by yourself. The same package with different versions will share the same directory, so you need to be careful with different package versions.
        """
        return self.__pkg_data_dir

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
        # fix: run block don't have node_id
        if len(self.__block_info.stacks) > 0:
            return self.__block_info.stacks[-1].get("node_id", "unknown")
        else:
            return "none"

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

            serialize_path = None
            # only cache root flow
            if len(self.__block_info.stacks) < 2 and output_def.need_serialize_var_for_cache() and value.__class__.__name__ == 'DataFrame' and callable(getattr(value, 'to_pickle', None)):
                from .serialization import compression_suffix, compression_options
                suffix = compression_suffix(context=self)
                compression = compression_options(context=self)
                flow_node = self.__block_info.stacks[-1].get("flow", "unknown") + "-" + self.node_id
                serialize_path = f"{self.pkg_data_dir}/.cache/{string_hash(flow_node)}/{handle}{suffix}"
                os.makedirs(os.path.dirname(serialize_path), exist_ok=True)
                try:
                    copy_value = value.copy()  # copy the value to avoid blocking the main thread
                    import threading
                    def write_pickle():
                        copy_value.to_pickle(serialize_path, compression=compression)
                    thread = threading.Thread(target=write_pickle)
                    thread.start()
                except IOError as e:
                    pass
            var: VarValueDict = {
                "__OOMOL_TYPE__": "oomol/var",
                "value": asdict(ref),
                "serialize_path": serialize_path,
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

    def output(self, key: str, value: Any, *, to_node: list[ToNode] | None = None, to_flow: list[ToFlow] | None = None):
        """
        output the value to the next block

        :param key: str, the key of the output, should be defined in the block schema output defs, the field name is handle
        :param value: Any, the value of the output
        :param to_node: list[ToNode] | None, the target node(with input handle) to send the output
        :param to_flow: list[ToFlow] | None, the target flow(with output handle) to send the output
        if both to_node and to_flow are None, the output will be sent to all connected nodes and flows.
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

        if to_node is not None or to_flow is not None:
            target = {
                "to_node": to_node,
                "to_flow": to_flow,
            }
        else:
            target = None

        payload = {
            "type": "BlockOutput",
            "handle": key,
            "output": wrap_value,
        }
        if target is not None:
            payload["options"] = {"target": target}
        self.__mainframe.send(self.job_info, payload)
    
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
        """
        send a message to the block, this message will be displayed in the log of the block.
        :param payload: the payload of the message, it can be a string or a dict
        """
        self.__mainframe.report(
            self.block_info,
            {
                "type": "BlockMessage",
                "payload": payload,
            },
        )
    
    def __dataframe(self, payload: PreviewPayload) -> PreviewPayloadInternal:
        target_dir = os.path.join(self.tmp_dir, self.job_id)
        os.makedirs(target_dir, exist_ok=True)
        csv_file = os.path.join(target_dir, f"{random_string(8)}.csv")
        if isinstance(payload, DataFrame):
            payload.to_csv(path_or_buf=csv_file)
            payload = { "type": "table", "data": csv_file }

        if isinstance(payload, dict) and payload.get("type") == "table":
            df = payload.get("data")
            if isinstance(df, ShapeDataFrame):
                df.to_csv(path_or_buf=csv_file)
                payload = { "type": "table", "data": csv_file }
        
        return payload

    def __matplotlib(self, payload: PreviewPayloadInternal) -> PreviewPayloadInternal:
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
        

    def preview(self, payload: PreviewPayload, id: str | None = None):
        payload_internal = self.__dataframe(payload)
        payload_internal = self.__matplotlib(payload_internal)

        if id is not None:
            payload_internal["id"] = id #type: ignore

        self.__mainframe.report(
            self.block_info,
            {
                "type": "BlockPreview",
                "payload": payload_internal,  # type: ignore
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
        self.__mainframe.send(self.job_info, {
            "type": "BlockProgress",
            "progress": progress,
        })
        self.__mainframe.report(
            self.block_info,
            {
                "type": "BlockProgress",
                "progress": progress,
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

    async def query_downstream(self, handles: list[str] | None = None) -> Dict[str, Downstream]:
        """
        query the downstream nodes of the given output handles.
        :param handle: the handle of the output, should be defined in the block schema output defs. If None means query all handles.
        :return: a dict that contains the downstream nodes, including the node id and input handle.
        """
        request_id = random_string(16)
        loop = asyncio.get_running_loop()
        f: asyncio.Future[Dict[str, Any]] = loop.create_future()

        def response_callback(payload: Dict[str, Any]):
            if payload.get("request_id") != request_id:
                return
            self.__mainframe.remove_request_response_callback(self.session_id, request_id, response_callback)
            if payload.get("result") is not None:
                loop.call_soon_threadsafe(lambda: f.set_result(payload.get("result", {})))
            elif payload.get("error") is not None:
                loop.call_soon_threadsafe(lambda: f.set_exception(ValueError(payload.get("error", "Unknown error occurred while querying the downstream."))))

        self.__mainframe.add_request_response_callback(self.session_id, request_id, response_callback)

        self.__mainframe.send(self.job_info, {
            "type": "BlockRequest",
            "action": "QueryDownstream",
            "handles": handles,
            "session_id": self.session_id,
            "job_id": self.job_id,
            "request_id": request_id,
        })

        return await f
    
    async def query_block(self, block: str) -> QueryBlockResponse:
        """
        this is a experimental api, it is used to query the block information..

        query a block by its id.
        :param block: the id of the block to query. format: `self::<block_name>` or `<package_name>::<block_name>`.
        :return: a dict that contains the block information, including the block schema, inputs and outputs.

        if the block is not found, it will raise a ValueError.

        example:
        ```python
        response = await context.query_block("self::my_block")
        print(response)
        """

        request_id = random_string(16)
        loop = asyncio.get_running_loop()
        f: asyncio.Future[QueryBlockResponse] = loop.create_future()

        def response_callback(payload: Dict[str, Any]):
            """
            This callback is called when the block information is received.
            It will return the block information to the caller.
            """
            if payload.get("request_id") != request_id:
                return
            self.__mainframe.remove_request_response_callback(self.session_id, request_id, response_callback)
            
            if payload.get("result") is not None:
                loop.call_soon_threadsafe(lambda: f.set_result(payload.get("result", {})))
            elif payload.get("error") is not None:
                loop.call_soon_threadsafe(lambda: f.set_exception(ValueError(payload.get("error", "Unknown error occurred while querying the block."))))

        
        self.__mainframe.add_request_response_callback(self.session_id, request_id, response_callback)

        self.__mainframe.send(self.job_info, {
            "type": "BlockRequest",
            "action": "QueryBlock",
            "block": block,
            "session_id": self.session_id,
            "job_id": self.job_id,
            "request_id": request_id,
        })

        return await f
        

    def run_block(self, block: str, *, inputs: Dict[str, Any], additional_inputs_def: list[HandleDefDict] | None = None, additional_outputs_def: list[HandleDefDict] | None = None, strict: bool = False) -> BlockJob:
        """
        :param block: the id of the block to run. format: `self::<block_name>` or `<package_name>::<block_name>`.
        :param inputs: the inputs of the block. if the block has no inputs, this parameter can be dict. 
                    If the inputs missing some required inputs, the response's finish future will send {"error": "<error message>" }.
                    some missing inputs will be filled:
                        1. with the default value if the block's input_def has a default value (which is defined in the value field).
                        2. input_def's nullable is true, the missing input will be filled with Null.
        :param additional_inputs_def: additional inputs definitions, this is a list of dicts, each dict should contain the handle(required), description, json_schema, kind, nullable and is_additional fields. This is used to define additional inputs that are not defined in the block schema.
        :param additional_outputs_def: additional outputs definitions, this is a list of dicts, each dict should contain the handle(required), description, json_schema, kind, nullable and is_additional fields. This is used to define additional outputs that are not defined in the block schema.
        :param strict: if True, oocana will use input_def's json_schema(only when it exists) to validate the inputs and if they are not valid oocana will reject to run this block, return error message. otherwise it will run with the inputs as they are.
        :return: a RunResponse object, which contains the event callbacks and output callbacks. You can use the `add_event_callback` and `add_output_callback` methods to register callbacks for the events and outputs of the block. You can also use the `finish` method to wait for the block to finish and get the result.
        Notice do not call any context.send_message or context.report_progress or context.preview and other context methods(which will send message) directly in the callbacks, it may cause deadlock.

        this is a experimental api, it is used to run a block in the current context.
        It will send a request to the mainframe to run the block with the given inputs.
        It will return a RunResponse object, which contains the event callbacks and output callbacks.
        You can use the `add_event_callback` and `add_output_callback` methods to register callbacks for the events and outputs of the block.
        You can also use the `finish` method to wait for the block to finish and get the result or error.

        example:
        ```python
        response = context.run_block("self::my_block", {"input1": "value1", "input2": "value2"})
        response.add_event_callback(lambda event: print(f"Event received: {event}"))
        response.add_output_callback(lambda handle, value: print(f"Output received: {handle} = {value}"))
        payload = await response.finish()
        if payload.get("error"):
            print(f"Block finished with error: {payload['error']}")
        else:
            print(f"Block finished with result: {payload['result']}")
        ```
        """

        # consider use uuid, remove job_id and block_job_id.
        block_job_id = f"{self.job_id}-{block}-{random_string(8)}"
        request_id = random_string(16)
        self.__mainframe.send(self.job_info, {
            "type": "BlockRequest",
            "action": "RunBlock",
            "block": block,
            "block_job_id": block_job_id,
            "payload": {
                "inputs": inputs,
                "additional_inputs_def": additional_inputs_def,
                "additional_outputs_def": additional_outputs_def,
            },
            "stacks": self.__block_info.stacks,
            "strict": strict,
            "request_id": request_id,
        })

        outputs_callbacks: set[Callable[[Dict[str, Any]], None]] = set()
        progress_callbacks: set[Callable[[float | int], None]] = set()

        # run_block will always run in a coroutine, so we can use asyncio.Future to wait for the result.
        loop = asyncio.get_running_loop()
        future: asyncio.Future[None] = loop.create_future()

        def response_callback(payload: Dict[str, Any]):
            """
            This callback is called when an error occurs while running a block.
            It will call the error callbacks registered by the user.
            """
            if payload.get("request_id") != request_id:
                return

            error = payload.get("error")
            # only handle error 
            if error is not None:
                set_future_and_clean(error)

        def run_output_callback(payload: Dict[str, Any]):
            # TODO: run callback in different coroutine, so it can send mqtt message directly.
            for output_callback in outputs_callbacks:
                output_callback(payload)

        def run_progress_callback(progress: float | int):
            for progress_callback in progress_callbacks:
                progress_callback(progress)

        def event_callback(payload: Dict[str, Any]):

            if payload.get("session_id") != self.session_id:
                return

            if payload.get("job_id") != block_job_id:
                return
            elif payload.get("type") == "ExecutorReady" or payload.get("type") == "BlockReady" or payload.get("type") == "BlockRequest":
                # ignore these messages
                return

            if payload.get("type") == "BlockOutput":
                output = {}
                output[payload.get("handle")] = payload.get("output")
                run_output_callback(output)
            elif payload.get("type") == "BlockOutputs":
                run_output_callback(payload.get("outputs", {}))
            elif payload.get("type") == "SubflowBlockOutput":
                output = {}
                output[payload.get("handle")] = payload.get("output")
                run_output_callback(output)
            elif payload.get("type") == "BlockProgress":
                progress = payload.get("progress")
                if progress is not None:
                    run_progress_callback(progress)
            elif payload.get("type") == "SubflowBlockFinished":
                error = payload.get("error")
                if error is None:
                    run_progress_callback(100)
                set_future_and_clean(error)
            elif payload.get("type") == "BlockFinished":
                result = payload.get("result", {})
                error = payload.get("error")
                if result is not None and not isinstance(result, dict):
                    pass
                elif result is not None:
                    run_output_callback(result)
                
                if error is None:
                    run_progress_callback(100)

                set_future_and_clean(error)

        job = BlockJob(outputs_callbacks=outputs_callbacks, progress_callbacks=progress_callbacks, future=future)

        def set_future_and_clean(error: None | str = None):
            self.__mainframe.remove_report_callback(event_callback)
            self.__mainframe.remove_request_response_callback(self.session_id, request_id, response_callback)

            def set_future():
                if future.done():
                    return
                if error is None:
                    future.set_result(None)
                else:
                    future.set_exception(BlockExecuteException(f"run block {block} failed: {error}"))

            loop.call_soon_threadsafe(set_future)
            outputs_callbacks.clear()


        self.__mainframe.add_report_callback(event_callback)
        self.__mainframe.add_request_response_callback(self.session_id, request_id, response_callback)

        return job
