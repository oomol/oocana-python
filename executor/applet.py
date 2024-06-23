from typing import Callable, Any
from oocana import Context, AppletExecutePayload, Mainframe
from .bin import createContext, output_return_object
import threading
import time

class Timer(threading.Thread):
    def __init__(self, interval, function):
        super().__init__()
        self.interval = interval
        self.function = function
        self.cancelled = threading.Event()

    def run(self):
        time.sleep(self.interval)
        if not self.cancelled.is_set():
            self.function()

    def cancel(self):
        self.cancelled.set()

class AppletRuntime:

    blockHandler: dict[str, Callable[[Any, Context], Any]] | Callable[[str, Any, Context], Any]
    _store = {}
    _config: AppletExecutePayload
    _mainframe: Mainframe
    _applet_id: str
    _timer: Timer | None = None

    def __init__(self, config: AppletExecutePayload,mainframe: Mainframe, applet_id: str):
        self._config = config
        self._mainframe = mainframe
        self._applet_id = applet_id

    async def run_block(self, payload: AppletExecutePayload):
        block_name = payload["block_name"]

        context = createContext(self._mainframe, payload["session_id"], payload["job_id"], self._store, payload["outputs"])

        if isinstance(self.blockHandler, dict):
            handler = self.blockHandler.get(block_name)
            if handler is None:
                raise Exception(f"block {block_name} not found")
            result = handler(context.inputs, context)
        elif callable(self.blockHandler):
            handler = self.blockHandler
            result = handler(block_name, context.inputs, context)
        else:
            raise Exception("blockHandler must be a dict or a callable")

        output_return_object(result, context)