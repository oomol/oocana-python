from dataclasses import asdict
from .data import BlockInfo, StoreKey, JobDict, BlockDict
from .handle_data import HandleDef
from .mainframe import Mainframe
from typing import Dict, Any

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
            executor="python_executor",
            handle=handle,
            job_id=self.job_id,
            session_id=self.session_id,
        )

    def output(self, output, handle: str, done: bool = False):

        v = output

        if self.__outputs_def is not None:
            output_def = self.__outputs_def.get(handle)
            if (
                output_def is not None and output_def.is_var_handle()
            ):
                ref = self.__store_ref(handle)
                self.__store[ref] = output
                v = asdict(ref)

        if self.__outputs_def is not None and self.__outputs_def.get(handle) is None:
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
