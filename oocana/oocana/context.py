from dataclasses import asdict
from json import loads
from .data import BlockInfo, StoreKey, JobDict, BlockDict, BinValueDict, VarValueDict
from .handle_data import HandleDef
from .mainframe import Mainframe
from typing import Dict, Any, TypedDict, Optional
from base64 import b64encode
from io import BytesIO
from .throtter import throttle
from .preview import PreviewPayload, TablePreviewData, DataFrame, ShapeDataFrame, PartialDataFrame
from .data import EXECUTOR_NAME
import os.path
import logging

__all__ = ["Context"]

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
    __store: Any
    __is_done: bool = False
    __keep_alive: OnlyEqualSelf = OnlyEqualSelf()
    __session_dir: str
    __tmp_dir: str
    __package_name: str | None = None
    _logger: Optional[logging.Logger] = None

    def __init__(
        self, inputs: Dict[str, Any], blockInfo: BlockInfo, mainframe: Mainframe, store, outputs, session_dir: str, tmp_dir: str, package_name: str
    ) -> None:

        self.__block_info = blockInfo

        self.__mainframe = mainframe
        self.__store = store
        self.__inputs = inputs

        outputs_defs = {}
        if outputs is not None:
            for k, v in outputs.items():
                outputs_defs[k] = HandleDef(**v)
        self.__outputs_def = outputs_defs
        self.__session_dir = session_dir
        self.__tmp_dir = tmp_dir
        self.__package_name = package_name

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
    def keepAlive(self):
        return self.__keep_alive

    @property
    def inputs(self):
        return self.__inputs

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
        return {
            "base_url": os.getenv("OOMOL_LLM_BASE_URL", ""),
            "base_url_v1": os.getenv("OOMOL_LLM_BASE_URL_V1", ""),
            "api_key": os.getenv("OOMOL_LLM_API_KEY", ""),
            "models": os.getenv("OOMOL_LLM_MODELS", "").split(","),
        }
    
    @property
    def host_info(self) -> HostInfo:
        """this is a dict contains the host information
        """
        return {
            "gpu_vendor": os.getenv("OOMOL_HOST_GPU_VENDOR", "unknown"),
            "gpu_renderer": os.getenv("OOMOL_HOST_GPU_RENDERER", "unknown"),
        }
    
    @property
    def is_done(self) -> bool:
        return self.__is_done

    def __store_ref(self, handle: str):
        return StoreKey(
            executor=EXECUTOR_NAME,
            handle=handle,
            job_id=self.job_id,
            session_id=self.session_id,
        )
    
    def __is_basic_type(self, value: Any) -> bool:
        return isinstance(value, (int, float, str, bool))

    def output(self, key: str, value: Any, done: bool = False):
        """
        output the value to the next block

        key: str, the key of the output, should be defined in the block schema output defs, the field name is handle
        value: Any, the value of the output
        """

        v = value

        if self.__outputs_def is not None:
            output_def = self.__outputs_def.get(key)
            if (
                output_def is not None and output_def.is_var_handle() and not self.__is_basic_type(value) # 基础类型即使是变量也不放进 store，直接作为 json 内容传递
            ):
                ref = self.__store_ref(key)
                self.__store[ref] = value
                d: VarValueDict = {
                    "__OOMOL_TYPE__": "oomol/var",
                    "value": asdict(ref)
                }
                v = d
            elif output_def is not None and output_def.is_bin_handle():
                if not isinstance(value, bytes):
                    self.send_warning(
                        f"Output handle key: [{key}] is defined as binary, but the value is not bytes."
                    )
                    return
                
                bin_file = f"{self.session_dir}/binary/{self.session_id}/{self.job_id}/{key}"
                os.makedirs(os.path.dirname(bin_file), exist_ok=True)
                try:
                    with open(bin_file, "wb") as f:
                        f.write(value)
                except IOError as e:
                    self.send_warning(
                        f"Output handle key: [{key}] is defined as binary, but an error occurred while writing the file: {e}"
                    )
                    return

                if os.path.exists(bin_file):
                    bin_value: BinValueDict = {
                        "__OOMOL_TYPE__": "oomol/bin",
                        "value": bin_file,
                    }
                    v = bin_value
                else:
                    self.send_warning(
                        f"Output handle key: [{key}] is defined as binary, but the file is not written."
                    )
                    return

        # 如果传入 key 在输出定义中不存在，直接忽略，不发送数据。但是 done 仍然生效。
        if self.__outputs_def is not None and self.__outputs_def.get(key) is None:
            self.send_warning(
                f"Output handle key: [{key}] is not defined in Block outputs schema."
            )
            if done:
                self.done()
            return

        node_result = {
            "type": "BlockOutput",
            "handle": key,
            "output": v,
            "done": done,
        }
        self.__mainframe.send(self.job_info, node_result)

        if done:
            self.done()

    def done(self, error: str | None = None):
        if self.__is_done:
            self.send_warning("done has been called multiple times, will be ignored.")
            return
        self.__is_done = True
        if error is None:
            self.__mainframe.send(self.job_info, {"type": "BlockFinished"})
        else:
            self.__mainframe.send(
                self.job_info, {"type": "BlockFinished", "error": error}
            )

    def send_message(self, payload):
        self.__mainframe.report(
            self.block_info,
            {
                "type": "BlockMessage",
                "payload": payload,
            },
        )
    
    def __dataframe(self, payload: PreviewPayload) -> PreviewPayload:
        if isinstance(payload, DataFrame):
            payload = { "type": "table", "data": payload }

        if isinstance(payload, dict) and payload.get("type") == "table":
            df = payload.get("data")
            if isinstance(df, ShapeDataFrame):
                row_count = df.shape[0]
                if row_count <= 10:
                    data = df.to_dict(orient='split')
                    columns = data.get("columns", [])
                    rows = data.get("data", [])
                elif isinstance(df, PartialDataFrame):
                    data_columns = loads(df.head(5).to_json(orient='split'))
                    columns = data_columns.get("columns", [])
                    rows_head = data_columns.get("data", [])
                    data_tail = loads(df.tail(5).to_json(orient='split'))
                    rows_tail = data_tail.get("data", [])
                    rows_dots = [["..."] * len(columns)]
                    rows = rows_head + rows_dots + rows_tail
                else:
                    print("dataframe more than 10 rows but not support head and tail is not supported")
                    return payload
                data: TablePreviewData = { "rows": rows, "columns": columns, "row_count": row_count }
                payload = { "type": "table", "data": data }
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
