import logging
from oocana import Context
import weakref

class ContextHandler(logging.Handler):

    @property
    def context(self):
        return self._context

    def __init__(self, context: Context):
        super().__init__()
        self._context = weakref.ref(context)

    def emit(self, record):
        msg = self.format(record)
        ctx = self.context()
        if ctx:
            ctx.report_log(msg)