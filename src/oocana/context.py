from dataclasses import asdict
from .data import BlockInfo, StoreKey, JobDict, BlockDict
from .data import InputHandleDict, HandleDict
from .data import can_convert_to_var_handle_def
from .mainframe import Mainframe
from typing import Dict, Any


class Context:
    __inputs: Dict[str, Any]
    __inputs_def: Dict[str, InputHandleDict]

    __block_info: BlockInfo
    __outputs: Dict[str, HandleDict]
    __store: Any

    def __init__(
        self, node_props, mainframe: Mainframe, store, outputs
    ) -> None:
        self.__inputs = node_props.get("inputs")
        self.__inputs_def = node_props.get("inputs_def")

        self.__block_info = BlockInfo(**node_props)

        self.__mainframe = mainframe
        self.__store = store
        self.__outputs = outputs

        if self.__inputs is None:
            self.__inputs = {}

        for k, v in self.__inputs_def.items():
            if can_convert_to_var_handle_def(v):
                try:
                    ref = StoreKey(**self.__inputs[k])
                except:
                    print(f"not valid object ref: {self.__inputs[k]}")
                    continue

                value = store.get(ref)
                self.__inputs[k] = value

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

    def __store_ref(self, handle: str):
        return StoreKey(
            executor="python_executor",
            handle=handle,
            job_id=self.job_id,
            session_id=self.session_id,
        )

    def output(self, output, handle: str, done: bool = False):

        v = output

        if self.__outputs is not None:
            output_def = self.__outputs.get(handle)
            if (
                output_def is not None
                and output_def.get("serialize")
                and output_def.get("serialize").get("executor")
            ):
                ref = self.__store_ref(handle)
                self.__store[ref] = output
                v = asdict(ref)

        if self.__outputs is not None and self.__outputs.get(handle) is None:
            # TODO: 未来添加 warning 级别日志时，更改为 warning 而不是 error
            self.send_error(
                f"Output handle key: [{handle}] is not defined in Block outputs schema."
            )

        node_result = {
            "type": "BlockOutput",
            "handle": handle,
            "output": v,
            "done": done,
        }
        self.__mainframe.send(self.job_info, node_result)

        if done:
            # 多次调用，需要至少给个警告
            self.done()

    def done(self, error: str | None = None):
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

    def report_progress(self, progress: int):
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

    def send_error(self, error: str):
        self.__mainframe.send(self.job_info, {"type": "BlockError", "error": error})
