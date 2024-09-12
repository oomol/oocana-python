from typing import Callable, Any, TypedDict
from oocana import Context, ServiceExecutePayload, Mainframe, StopAtOption
from .block import output_return_object, load_module
from .context import createContext
from threading import Timer
import inspect
import asyncio

DEFAULT_BLOCK_ALIVE_TIME = 10
SERVICE_EXECUTOR_TOPIC_PREFIX = "executor/service"

class ServiceMessage(TypedDict):
    job_id: str
    node_id: str
    flow_path: str
    payload: Any


class ServiceRuntime:

    block_handler: dict[str, Callable[[Any, Context], Any]] | Callable[[str, Any, Context], Any] = dict()
    _store = {}
    _config: ServiceExecutePayload
    _mainframe: Mainframe
    _service_id: str
    _timer: Timer | None = None
    _stop_at: StopAtOption
    _keep_alive: int | None = None

    _runningBlocks = set()
    _jobs = set()

    def __init__(self, config: ServiceExecutePayload, mainframe: Mainframe, service_id: str):
        self._config = config
        self._mainframe = mainframe
        self._service_id = service_id
        self._stop_at = config.get("service_executor").get("stop_at") if config.get("service_executor") is not None and config.get("service_executor").get("stop_at") is not None else "session_end"
        self._keep_alive = config.get("service_executor").get("keep_alive") if config.get("service_executor") is not None else None

        mainframe.subscribe(f"{SERVICE_EXECUTOR_TOPIC_PREFIX}/{service_id}/execute", self.run_block)

    def _setup_timer(self):
        if self._stop_at is None:
            return
        elif self._stop_at == "session_end":
            # session level 的 executor，由于缓存的存在，不能立刻退出。要等到新 session 启动才退出
            self._mainframe.subscribe(f"session/{self._config.get('session_id')}", lambda payload: self.exit() if payload.get("type") == "SessionStarted" and payload.get("session_id") != self._config.get("session_id") else None)
        elif self._stop_at == "app_end":
            # TODO: app_end 有 executor 来中止？
            pass
        elif self._stop_at == "block_end":
            # 在 run block 实现
            pass

    def __setitem__(self, key, value):
        if key == "block_handler":
            self.block_handler = value

    def add_message_callback(self, callback: Callable[[ServiceMessage], Any]):
        def filter(payload):
            if payload.get("job_id") in self._jobs:
                callback(payload)
        self._mainframe.subscribe(f"service/{self._service_id}", filter)

    async def run(self):
        service_config = self._config.get("service_executor")
        m = load_module(service_config.get("entry"), self._config.get("dir"))
        fn = m.__dict__.get(service_config.get("function"))
        # TODO: 从 entry 附近查找到当前 Service 依赖的 module
        if not callable(fn):
            raise Exception(f"function {service_config.get('function')} not found in {service_config.get('entry')}")
        if inspect.iscoroutinefunction(fn):
            await fn(self)
        else:
            fn(self)
        await self.run_block(self._config)
    
    def exit(self):
        self._mainframe.publish(f"{SERVICE_EXECUTOR_TOPIC_PREFIX}/{self._service_id}/exit", {})
        self._mainframe.disconnect()
        exit(0)

    async def run_block(self, payload: ServiceExecutePayload):
        block_name = payload["block_name"]
        job_id = payload["job_id"]

        if self._timer is not None:
            self._timer.cancel()
            self._timer = None

        self._runningBlocks.add(job_id)
        self._jobs.add(job_id)

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

        self._runningBlocks.remove(job_id)

        if self._stop_at == "block_end" and len(self._runningBlocks) == 0:
            self._timer = Timer(self._keep_alive or DEFAULT_BLOCK_ALIVE_TIME, self.exit)
            self._timer.start()

def run_async_code(async_func):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(async_func)
    loop.run_forever()

def config_callback(payload: Any, mainframe: Mainframe, service_id: str):
    service = ServiceRuntime(payload, mainframe, service_id)

    async def run():
        await service.run()

    import threading
    threading.Thread(target=run_async_code, args=(run(),)).start()


async def run_service(address, service_id):
    mainframe = Mainframe(address, service_id)
    mainframe.connect()
    mainframe.subscribe(f"{SERVICE_EXECUTOR_TOPIC_PREFIX}/{service_id}/config", lambda payload: config_callback(payload, mainframe, service_id))
    await asyncio.sleep(1)
    mainframe.publish(f"{SERVICE_EXECUTOR_TOPIC_PREFIX}/{service_id}/spawn", {})


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="run service with mqtt address and client id")
    parser.add_argument("--address", help="mqtt address", required=True)
    parser.add_argument("--service-id", help="service id")
    args = parser.parse_args()

    loop = asyncio.new_event_loop()
    loop.run_until_complete(run_service(args.address, args.service_id))
    loop.run_forever()