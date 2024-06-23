from typing import Callable, Any
from oocana import Context, AppletExecutePayload, Mainframe
from .bin import createContext

class AppletRuntime:

    blockHandler: dict[str, Callable[[Any, Context], Any]] | Callable[[str, Any, Context], Any]
    _store = {}
    _config: AppletExecutePayload
    _mainframe: Mainframe
    _applet_id: str

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
            handler(context.inputs, context)
        elif callable(self.blockHandler):
            handler = self.blockHandler
            handler(block_name, context.inputs, context)
        else:
            raise Exception("blockHandler must be a dict or a callable")
        