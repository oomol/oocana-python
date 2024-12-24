from contextvars import ContextVar
from oocana import Context

vars: ContextVar[Context] = ContextVar('context')
store = {}
