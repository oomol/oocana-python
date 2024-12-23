from typing import Callable, Any
from oocana import ServiceExecutePayload, Mainframe, StopAtOption, ServiceContextAbstractClass, ServiceMessage, BlockHandler
from .block import output_return_object, load_module
from .context import createContext
from .utils import run_async_code_and_loop, loop_in_new_thread, run_in_new_thread, oocana_dir
from .topic import service_config_topic, ServiceTopicParams, ReportStatusPayload, prepare_report_topic, shutdown_action_topic, run_action_topic, service_message_topic, exit_report_topic, status_report_topic,global_shutdown_topic
from threading import Timer
import inspect
import asyncio
import logging
import os
import threading

DEFAULT_BLOCK_ALIVE_TIME = 10

# 两种文件，根据是否有 session id 来区分：
# 1. session service： ~/.oocana/sessions/{session_id}/python-{service_hash}.log
# 2. 跨 session service（global service）： ~/.oocana/services/python-{service_hash}.log
def config_logger(service_hash: str, session_id: str | None):
    import os.path
    logger_file = os.path.join(oocana_dir(), "services", "python-" + service_hash + ".log") if session_id is None else os.path.join(oocana_dir(), "sessions", session_id, "python-" + service_hash + ".log") 

    if not os.path.exists(logger_file):
        os.makedirs(os.path.dirname(logger_file), exist_ok=True)

    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - {%(filename)s:%(lineno)d} - %(message)s', filename=logger_file)


class ServiceRuntime(ServiceContextAbstractClass):

    _store = {}
    _config: ServiceExecutePayload
    _mainframe: Mainframe
    _service_hash: str
    _session_id: str | None = None
    _timer: Timer | None = None
    _stop_at: StopAtOption
    _keep_alive: int | None = None
    _registered = threading.Event()
    _waiting_ready_notify = False
    _session_dir: str
    _topic_params: ServiceTopicParams
    _report_timer: Timer | None = None

    _runningBlocks = set()
    _jobs = set()

    def __init__(self, config: ServiceExecutePayload, mainframe: Mainframe, service_hash: str, session_dir: str, session_id: str | None = None):
        self._block_handler = dict()
        self._config = config
        self._mainframe = mainframe
        self._service_hash = service_hash
        self._session_id = session_id
        self._session_dir = session_dir
        self._topic_params = {
            "service_hash": service_hash,
            "session_id": session_id
        }

        self._stop_at = config.get("service_executor").get("stop_at") if config.get("service_executor") is not None and config.get("service_executor").get("stop_at") is not None else "session_end"
        self._keep_alive = config.get("service_executor").get("keep_alive") if config.get("service_executor") is not None else None

        mainframe.subscribe(run_action_topic(self._topic_params), self.run_action_callback)
        mainframe.subscribe(shutdown_action_topic(self._topic_params), self.shutdown_callback)
        mainframe.subscribe(global_shutdown_topic, self.shutdown_callback)

        self._setup_timer()
        self.report_status()

    # post message every 5 seconds
    def report_status(self):
        payload: ReportStatusPayload = {
            "service_hash": self._service_hash,
            "session_id": self._session_id,
            "executor": "python"
        }
        self._mainframe.publish(status_report_topic(), payload)
        self._report_timer = Timer(5, self.report_status)
        self._report_timer.start()

    # 不能直接在 callback 里面调用 mainframe publish 所以 callback 都要单独开
    def shutdown_callback(self, payload: Any):
        
        async def shutdown():
            self.exit()
        
        run_in_new_thread(shutdown)

    def run_action_callback(self, payload: ServiceExecutePayload):

        async def run():
            await self.run_block(payload)
        
        run_in_new_thread(run)

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
    def waiting_ready_notify(self) -> bool:
        return self._waiting_ready_notify
    
    @waiting_ready_notify.setter
    def waiting_ready_notify(self, value: bool):
        self._waiting_ready_notify = value

    @property
    def block_handler(self) -> BlockHandler:
        return self._block_handler
    
    @block_handler.setter
    def block_handler(self, value: BlockHandler):
        self._block_handler = value
        if not self.waiting_ready_notify:
            self._registered.set()
    
    def notify_ready(self):
        self._registered.set()

    def add_message_callback(self, callback: Callable[[ServiceMessage], Any]):
        def filter(payload):
            if payload.get("job_id") in self._jobs:
                callback(payload)
        self._mainframe.subscribe(service_message_topic, filter)

    async def run(self):
        service_config = self._config.get("service_executor")
        m = load_module(service_config.get("entry"), self._config.get("dir"))
        fn = m.__dict__.get(service_config.get("function"))
        if not callable(fn):
            raise Exception(f"function {service_config.get('function')} not found in {service_config.get('entry')}")

        if inspect.iscoroutinefunction(fn):
            async def async_run():
                await fn(self)
            run_in_new_thread(async_run)
        else:
            def run():
                fn(self)
            import threading
            threading.Thread(target=run).start()
    
        await self.run_block(self._config)
    
    def exit(self):

        payload: ReportStatusPayload = {
            "service_hash": self._service_hash,
            "session_id": self._session_id,
            "executor": "python"
        }

        self._mainframe.publish(exit_report_topic(), payload)
        self._mainframe.disconnect()
        # child process need call os._exit not sys.exit
        os._exit(0)

    async def run_block(self, payload: ServiceExecutePayload):
        self._registered.wait()
        block_name = payload["block_name"]
        job_id = payload["job_id"]

        if self._timer is not None:
            self._timer.cancel()
            self._timer = None

        self._runningBlocks.add(job_id)
        self._jobs.add(job_id)

        context = createContext(self._mainframe, payload["session_id"], payload["job_id"], self._store, payload["outputs"], self._session_dir)

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

def setup_service(payload: Any, mainframe: Mainframe, service_id: str, session_dir: str):
    service = ServiceRuntime(payload, mainframe, service_id, session_dir)

    async def run():
        await service.run()
    loop_in_new_thread(run)


async def run_service(address: str, service_hash: str, session_id: str | None, session_dir: str):
    mainframe = Mainframe(address, service_hash)
    mainframe.connect()

    params: ServiceTopicParams = {
        "session_id": session_id,
        "service_hash": service_hash
    }
    mainframe.subscribe(service_config_topic(params), lambda payload: setup_service(payload, mainframe, service_hash, session_dir))
    await asyncio.sleep(1)
    mainframe.publish(prepare_report_topic(params), {})


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="run service")
    parser.add_argument("--address", help="mqtt address", required=True)
    parser.add_argument("--service-hash", help="service hash", required=True)
    parser.add_argument("--session-id", help="session id")
    parser.add_argument("--session-dir", required=True)
    args = parser.parse_args()

    address: str = args.address
    service_hash: str = args.service_hash
    session_id: str | None = args.session_id
    session_dir: str = args.session_dir

    config_logger(service_hash, session_id)
    run_async_code_and_loop(run_service(address, service_hash, session_id, session_dir))