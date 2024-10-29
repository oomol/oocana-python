from typing import Callable, Any
from oocana import ServiceExecutePayload, Mainframe, StopAtOption, ServiceContextAbstractClass, ServiceMessage, BlockHandler
from .block import output_return_object, load_module
from .context import createContext
from .utils import run_async_code_and_loop, loop_in_new_thread, run_in_new_thread, base_dir
from threading import Timer
import inspect
import asyncio
import logging
import os

DEFAULT_BLOCK_ALIVE_TIME = 10
SERVICE_EXECUTOR_TOPIC_PREFIX = "executor/service"

# ~/.oocana/executor/services/{service_id}/python.log
def config_logger(service_id: str):
    import os.path
    # TODO: 目前 service log 与 executor log 分离，没有关联关系。会导致导出日志时，无法导出。后续再优化处理
    logger_file = os.path.join(base_dir(), "services", service_id, "python.log")

    if not os.path.exists(logger_file):
        os.makedirs(os.path.dirname(logger_file), exist_ok=True)

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - {%(filename)s:%(lineno)d} - %(message)s', filename=logger_file)


class ServiceRuntime(ServiceContextAbstractClass):

    _store = {}
    _config: ServiceExecutePayload
    _mainframe: Mainframe
    _service_id: str
    _timer: Timer | None = None
    _stop_at: StopAtOption
    _keep_alive: int | None = None
    _registered = asyncio.futures.Future()

    _runningBlocks = set()
    _jobs = set()

    def __init__(self, config: ServiceExecutePayload, mainframe: Mainframe, service_id: str):
        self._block_handler = dict()
        self._config = config
        self._mainframe = mainframe
        self._service_id = service_id
        self._stop_at = config.get("service_executor").get("stop_at") if config.get("service_executor") is not None and config.get("service_executor").get("stop_at") is not None else "session_end"
        self._keep_alive = config.get("service_executor").get("keep_alive") if config.get("service_executor") is not None else None

        mainframe.subscribe(f"{SERVICE_EXECUTOR_TOPIC_PREFIX}/{service_id}/execute", self.run_block)
        self._setup_timer()

    def _setup_timer(self):
        if self._stop_at is None:
            return
        elif self._stop_at == "session_end":
            self._mainframe.subscribe("report", lambda payload: self.exit() if payload.get("type") == "SessionFinished" and payload.get("session_id") == self._config.get("session_id") else None)
        elif self._stop_at == "app_end":
            # app 暂停可以直接先不管
            pass
        elif self._stop_at == "block_end":
            pass

    def __setitem__(self, key: str, value: Any):
        if key == "block_handler":
            self.block_handler = value

    @property
    def block_handler(self) -> BlockHandler:
        return self._block_handler
    
    @block_handler.setter
    def block_handler(self, value: BlockHandler):
        self._block_handler = value
        if not self.waiting_ready_notify:
            self._registered.set_result(None)
    
    def notify_ready(self):
        self._registered.set_result(None)

    def add_message_callback(self, callback: Callable[[ServiceMessage], Any]):
        def filter(payload):
            if payload.get("job_id") in self._jobs:
                callback(payload)
        self._mainframe.subscribe(f"service/{self._service_id}", filter)

    async def run(self):
        service_config = self._config.get("service_executor")
        m = load_module(service_config.get("entry"), self._config.get("dir"))
        fn = m.__dict__.get(service_config.get("function"))
        if not callable(fn):
            raise Exception(f"function {service_config.get('function')} not found in {service_config.get('entry')}")

        if inspect.iscoroutinefunction(fn):
            async def run(): # type: ignore
                await fn(self)
            run_in_new_thread(run)
        else:
            def run():
                fn(self)
            import threading
            threading.Thread(target=run).start()
    
        await self.run_block(self._config)
    
    def exit(self):
        self._mainframe.publish(f"{SERVICE_EXECUTOR_TOPIC_PREFIX}/{self._service_id}/exit", {})
        self._mainframe.disconnect()
        # child process need call os._exit not sys.exit
        os._exit(0)

    async def run_block(self, payload: ServiceExecutePayload):
        await self._registered
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

def config_callback(payload: Any, mainframe: Mainframe, service_id: str):
    service = ServiceRuntime(payload, mainframe, service_id)

    async def run():
        await service.run()
    loop_in_new_thread(run)


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

    config_logger(args.service_id)

    run_async_code_and_loop(run_service(args.address, args.service_id))