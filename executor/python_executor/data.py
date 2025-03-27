from contextvars import ContextVar
from oocana import Context, EXECUTOR_NAME  # noqa: F401

block_var: ContextVar[Context] = ContextVar('block-context')
store = {}
