from typing import Callable, Any
from oocana import Context, AppletExecutePayload, Mainframe
from .bin import createContext, output_return_object, load_module
import threading
import time
import inspect
import asyncio
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

        mainframe.subscribe(f"executor/applet/{applet_id}/execute", self.run_block)

    async def run(self):
        applet_config = self._config["applet_executor"]
        m = load_module(applet_config["entry"], self._config["dir"])
        fn = m.__dict__.get(applet_config["function"])
        if not callable(fn):
            raise Exception(f"function {applet_config['function']} not found in {applet_config['entry']}")
        if inspect.iscoroutinefunction(fn):
            await fn()
        else:
            await fn()
        await self.run_block(self._config)

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

def config_callback(payload: Any, mainframe: Mainframe, client_id: str):
    applet = AppletRuntime(payload, mainframe, client_id)
    asyncio.run(applet.run())
    asyncio.run(applet.run_block(payload))


async def start_applet(loop, address, client_id):
    mainframe = Mainframe(address, client_id)
    mainframe.connect()

    mainframe.subscribe(f"executor/applet/{client_id}/config", config_callback)
    mainframe.publish(f"executor/applet/{client_id}/spawn", {})


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="run applet with mqtt address and client id")
    parser.add_argument("--address", help="mqtt address", required=True)
    parser.add_argument("--client-id", help="mqtt client id")
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_applet(loop, args.address, args.client_id))
    loop.run_forever()