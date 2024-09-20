import re
from dataclasses import asdict
from json import loads
from .data import BlockInfo, StoreKey, JobDict, BlockDict
from .handle_data import HandleDef
from .mainframe import Mainframe
from typing import Dict, Any
from base64 import b64encode
from io import BytesIO
from .throtter import throttle
from .preview import PreviewPayload
from .data import EXECUTOR_NAME
class OnlyEqualSelf:
    def __eq__(self, value: object) -> bool:
        return self is value

class Context:
    __inputs: Dict[str, Any]

    __block_info: BlockInfo
    __outputs_def: Dict[str, HandleDef]
    __store: Any
    __is_done: bool = False
    __keep_alive: OnlyEqualSelf = OnlyEqualSelf()

    def __init__(
        self, inputs: Dict[str, Any], blockInfo: BlockInfo, mainframe: Mainframe, store, outputs
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
                v = asdict(ref)

        # 如果传入 key 在输出定义中不存在，直接忽略，不发送数据。但是 done 仍然生效。
        if self.__outputs_def is not None and self.__outputs_def.get(key) is None:
            # TODO: 未来添加 warning 级别日志时，更改为 warning 而不是 error
            self.send_error(
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
            # TODO: 添加 warning 日志，提示重复报错
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
        # payload is a dataframe
        if hasattr(payload, "__dataframe__") and hasattr(payload, "to_dict"):
            payload = { "type": "table", "data": payload }

        if isinstance(payload, dict) and payload.get("type") is not None and payload["type"] == "table":
            df: Any = payload.get("data")
            if hasattr(df, "__dataframe__") and hasattr(df, "to_dict"):
                row_count = df.shape[0]
                if row_count <= 10:
                    data = df.to_dict(orient='split')
                    columns = data.get("columns", [])
                    rows = data.get("data", [])
                else:
                    data_columns = loads(df.head(5).to_json(orient='split'))
                    columns = data_columns.get("columns", [])
                    rows_head = data_columns.get("data", [])
                    data_tail = loads(df.tail(5).to_json(orient='split'))
                    rows_tail = data_tail.get("data", [])
                    rows_dots = [["..."] * len(columns)]
                    rows = rows_head + rows_dots + rows_tail
                payload["data"] = { "rows": rows, "columns": columns, "row_count": row_count }
        
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

    __all_whitespace_matcher = re.compile(r"^\s*$")
    def report_log(self, line: str, stdio: str = "stdout"):
        if self.__all_whitespace_matcher.fullmatch(line) is not None:
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

    def send_error(self, error: str):
        self.__mainframe.send(self.job_info, {"type": "BlockError", "error": error})
