from dataclasses import asdict
from .data import BlockInfo, RefDescriptor
from .mainframe import Mainframe


class VocanaSDK:
    __inputs: dict
    __block_info: BlockInfo
    __outputs: any
    __store: any

    def __init__(
        self, node_props, mainframe: Mainframe, store=None, outputs=None
    ) -> None:
        self.__inputs = node_props.get("inputs")
        self.__block_info = BlockInfo(**node_props)

        self.__mainframe = mainframe
        self.__store = store
        self.__outputs = outputs

        if self.__inputs is None:
            self.__inputs = {}

        for k, v in self.__inputs.items():
            if isinstance(v, dict) and v.get("executor") == "python_executor":
                try:
                    obj_key = RefDescriptor(**v)
                except:
                    print(f"not valid object ref: {v}")
                    continue

                value = store.get(obj_key)

                if value is None:
                    print(f"ObjectRefDescriptor not found: {v}")
                    continue

                self.__inputs[k] = value

    @property
    def props(self):
        return self.__inputs

    @property
    def session_id(self):
        return self.__block_info.session_id

    @property
    def job_id(self):
        return self.__block_info.job_id

    def __store_ref(self, handle: str):
        return RefDescriptor(
            executor="python_executor",
            handle=handle,
            job_id=self.job_id,
            session_id=self.session_id,
        )

    def output(self, output: any, handle: str, done: bool = False):

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
        self.__mainframe.send(self.__block_info, node_result)

        if done:
            # 多次调用，需要至少给个警告
            self.done()

    def done(self, error: str = None):
        if error is None:
            self.__mainframe.send(self.__block_info, {"type": "BlockFinished"})
        else:
            self.__mainframe.send(
                self.__block_info, {"type": "BlockFinished", "error": error}
            )

    def send_message(self, payload):
        self.__mainframe.report(
            self.__block_info,
            {
                "type": "BlockMessage",
                "payload": payload,
            },
        )

    def report_progress(self, progress: int):
        self.__mainframe.report(
            {
                "type": "BlockProgress",
                "rate": progress,
            }
        )

    def report_log(self, line: str, stdio: str = "stdout"):
        self.__mainframe.report(
            self.__block_info,
            {
                "type": "BlockLog",
                "log": line,
                stdio: stdio,
            },
        )

    def log_json(self, payload):
        self.__mainframe.report(
            self.__block_info,
            {
                "type": "BlockLogJSON",
                "json": payload,
            },
        )

    def send_error(self, error: str):
        self.__mainframe.send(self.__block_info, {"type": "BlockError", "error": error})
