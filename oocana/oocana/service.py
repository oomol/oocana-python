from typing import Literal, Callable, Any, TypedDict, Optional, TypeAlias, Union
from .context import Context
from .data import JobDict

class ServiceContext(TypedDict):
    block_handler:  Union[Callable[[str, Any, Context], Any], dict[str, Callable[[Any, Context], Any]]]

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