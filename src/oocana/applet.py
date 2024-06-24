from typing import Callable, Any, TypedDict, Optional
from .context import Context
from enum import Enum
from .data import JobDict, HandleDict

class AppletStopOption(Enum):
    BLOCK = "block_end"
    SESSION = "session_end"
    App = "app_end"
    Never = "never"

class AppletStartOption(Enum):
    BLOCK = "block_start"
    SESSION = "session_start"
    App = "app_start"

class AppletContext(TypedDict):
    block_handler: dict[str, Callable[[Any, Context], Any]] | Callable[[str, Any, Context], Any]

class AppletExecutor(TypedDict):
    name: str
    entry: str
    function: str
    start_at: Optional[AppletStartOption]
    stop_at: Optional[AppletStopOption]
    keep_alive: Optional[int]

class AppletExecutePayload(JobDict):
    dir: str
    block_name: str
    applet_executor: AppletExecutor
    outputs: dict[str, HandleDict]