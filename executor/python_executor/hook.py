from sys import exit
from builtins import exit as global_exit
from typing import TypeAlias, Any
import sys
import builtins
from .block import vars, logger

class ExitFunctionException(Exception):
    pass

original_exit = exit
original_global_exit = global_exit
original_print = print

_ExitCode: TypeAlias = str | int | None

def sys_exit(status: _ExitCode = None) -> None:
    raise ExitFunctionException(status)

def sys_global_exit(status: _ExitCode = None) -> None:
    raise ExitFunctionException(status)

def global_print(*values: object, sep: str | None = " ", end: str | None = "\n", file: Any | None = None, flush: bool = False) -> None:
    
    try:
        context = vars.get()
    except LookupError:
        logger.warning("print called outside of block")
    except Exception as e:
        logger.error(f"print error: {e}")

    if context is not None:
        try:
            msg_sep = sep or " "
            msg = msg_sep.join(map(str, values))
            context.report_log(msg)
        except Exception as e:
            logger.error(f"transform print message to context log error: {e}")

    original_print(*values, sep=sep, end=end, file=file, flush=flush)


sys.exit = sys_exit
builtins.exit = sys_global_exit
builtins.print = global_print