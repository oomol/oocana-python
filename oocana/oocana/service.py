from typing import Literal, Callable, Any, TypedDict, Optional, TypeAlias, Union
from .context import Context
from .data import JobDict
from abc import ABC, abstractmethod

__all__ = ["ServiceMessage", "BlockHandler", "ServiceContextAbstractClass", "ServiceExecutor", "ServiceExecutePayload", "StopAtOption"]

class ServiceMessage(TypedDict):
    job_id: str
    node_id: str
    flow_path: str
    payload: Any

BlockHandler: TypeAlias = Union[Callable[[str, Any, Context], Any], dict[str, Callable[[Any, Context], Any]]]

class ServiceContextAbstractClass(ABC):
    
    @property
    @abstractmethod
    def block_handler(self) -> BlockHandler:
        pass
    
    @block_handler.setter
    @abstractmethod
    def block_handler(self, value: BlockHandler):
        pass

    def __setitem__(self, key: str, value: Any):
        pass
    
    @property
    @abstractmethod
    def waiting_ready_notify(self) -> bool:
        """set to True if the service need to wait for the ready signal before start. default is false which means the service will start immediately after block_handler is set.
            this function need to be called before set block_handler
            after set this function, developer need call notify_ready manually when the service is ready to start, otherwise the service will not run block
        """
        pass

    @waiting_ready_notify.setter
    @abstractmethod
    def waiting_ready_notify(self, value: bool):
        pass

    def notify_ready(self):
        """notify the service that the service is ready to start. this function need to be called after waiting_ready_notify is set to True otherwise this function has no effect"""
        pass

    def add_message_callback(self, callback: Callable[[ServiceMessage], Any]):
        """add a callback to handle the message to the service, the callback will be called when the message is sent to the service
        :param callback: the callback to handle the message
        """
        pass

StopAtOption: TypeAlias = Optional[Literal["block_end", "session_end", "app_end", "never"]]

class ServiceExecutor(TypedDict):
    name: str
    entry: str
    function: str
    start_at: Optional[Literal["block_start", "session_start", "app_start"]]
    stop_at: StopAtOption
    keep_alive: Optional[int]

class ServiceExecutePayload(JobDict):
    dir: str
    block_name: str
    service_executor: ServiceExecutor
    outputs: dict
    service_hash: str