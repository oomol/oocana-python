from typing import Literal, Callable, Any, TypedDict, Optional, TypeAlias
from .context import Context
from .data import JobDict, HandleDict

class ServiceContext(TypedDict):
    block_handler: dict[str, Callable[[Any, Context], Any]] | Callable[[str, Any, Context], Any]

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
    outputs: dict[str, HandleDict]