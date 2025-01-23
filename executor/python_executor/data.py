from contextvars import ContextVar
from oocana import Context, EXECUTOR_NAME

vars: ContextVar[Context] = ContextVar('context')
store = {}
