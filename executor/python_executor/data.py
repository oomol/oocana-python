from contextvars import ContextVar
from oocana import Context, EXECUTOR_NAME  # noqa: F401

vars: ContextVar[Context] = ContextVar('context')
store = {}
