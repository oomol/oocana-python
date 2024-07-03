from typing import Callable, Any
from oocana import Context, AppletExecutePayload, Mainframe, StopAtOption
from .block import output_return_object, load_module
from .context import createContext
from threading import Timer
import inspect
import asyncio

DEFAULT_BLOCK_ALIVE_TIME = 10

class AppletRuntime:

    block_handler: dict[str, Callable[[Any, Context], Any]] | Callable[[str, Any, Context], Any] = dict()
    _store = {}
    _config: AppletExecutePayload
    _mainframe: Mainframe
    _applet_id: str
    _timer: Timer | None = None
    _stop_at: StopAtOption
    _keep_alive: int | None = None

    # TODO: 需要考虑多线程问题
    _runningBlocks = dict()

    def __init__(self, config: AppletExecutePayload, mainframe: Mainframe, applet_id: str):
        self._config = config
        self._mainframe = mainframe
        self._applet_id = applet_id
        self._stop_at = config["applet_executor"]["stop_at"]
        self._keep_alive = config["applet_executor"]["keep_alive"]

        mainframe.subscribe(f"executor/applet/{applet_id}/execute", self.run_block)

    def _setup_timer(self):
        if self._stop_at is None:
            return
        elif self._stop_at == "session_end":
            self._mainframe.subscribe(f"executor/session/{self._config['session_id']}", lambda payload: self.exit() if payload["type"] == "SessionFinished" else None)
        elif self._stop_at == "app_end":
            # TODO: app_end 有 executor 来中止？
            pass
        elif self._stop_at == "block_end":
            # 在 run block 实现
            pass

    def __setitem__(self, key, value):
        if key == "block_handler":
            self.block_handler = value

    async def run(self):
        applet_config = self._config["applet_executor"]
        m = load_module(applet_config["entry"], self._config["dir"])
        fn = m.__dict__.get(applet_config["function"])
        # TODO: 从 entry 附近查找到当前 Applet 依赖的 module
        if not callable(fn):
            raise Exception(f"function {applet_config['function']} not found in {applet_config['entry']}")
        if inspect.iscoroutinefunction(fn):
            await fn(self)
        else:
            fn(self)
        await self.run_block(self._config)
    
    def exit(self):
        self._mainframe.publish(f"executor/applet/{self._applet_id}/exit", {})
        self._mainframe.disconnect()
        exit(0)

    async def run_block(self, payload: AppletExecutePayload):
        block_name = payload["block_name"]

        if self._timer is not None:
            self._timer.cancel()
            self._timer = None

        count = self._runningBlocks[block_name]
        if count is None:
            count = 1
        else:
            count += 1
        self._runningBlocks[block_name] = count

        context = createContext(self._mainframe, payload["session_id"], payload["job_id"], self._store, payload["outputs"])

        if isinstance(self.block_handler, dict):
            handler = self.block_handler.get(block_name)
            if handler is None:
                raise Exception(f"block {block_name} not found")
            result = handler(context.inputs, context)
        elif callable(self.block_handler):
            handler = self.block_handler
            result = handler(block_name, context.inputs, context)
        else:
            raise Exception("blockHandler must be a dict or a callable function")
        output_return_object(result, context)

        count = self._runningBlocks[block_name]
        count -= 1
        if count == 0:
            del self._runningBlocks[block_name]
        else:
            self._runningBlocks[block_name] = count

        if self._stop_at == "block_end" and len(self._runningBlocks) == 0:
            self._timer = Timer(self._keep_alive or DEFAULT_BLOCK_ALIVE_TIME, self.exit)
            self._timer.start()

def run_async_code(async_func):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(async_func)
    loop.run_forever()

def config_callback(payload: Any, mainframe: Mainframe, client_id: str):
    applet = AppletRuntime(payload, mainframe, client_id)

    async def run():
        await applet.run()

    import threading
    threading.Thread(target=run_async_code, args=(run(),)).start()


async def start_applet(loop, address, client_id):
    mainframe = Mainframe(address, client_id)
    mainframe.connect()

    mainframe.subscribe(f"executor/applet/{client_id}/config", lambda payload: config_callback(payload, mainframe, client_id))
    await asyncio.sleep(1)
    mainframe.publish(f"executor/applet/{client_id}/spawn", {})


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="run applet with mqtt address and client id")
    parser.add_argument("--address", help="mqtt address", required=True)
    parser.add_argument("--client-id", help="mqtt client id")
    args = parser.parse_args()

    loop = asyncio.new_event_loop()
    loop.run_until_complete(start_applet(loop, args.address, args.client_id))
    loop.run_forever()