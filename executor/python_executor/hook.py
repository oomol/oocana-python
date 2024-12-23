from sys import exit
from builtins import exit as global_exit
from typing import TypeAlias
import sys
import builtins

class ExitFunctionException(Exception):
    pass

original_exit = exit
original_global_exit = global_exit

_ExitCode: TypeAlias = str | int | None

def sys_exit(status: _ExitCode = None) -> None:
    raise ExitFunctionException(status)

def sys_global_exit(status: _ExitCode = None) -> None:
    raise ExitFunctionException(status)

sys.exit = sys_exit
builtins.exit = sys_global_exit