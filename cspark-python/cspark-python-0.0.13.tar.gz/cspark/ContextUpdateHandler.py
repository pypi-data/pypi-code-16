from .UpdateHandler import UpdateHandler
from .ContextBuilder import ContextBuilder


class ContextUpdateHandler(ContextBuilder, UpdateHandler):

    def __init__(self, context_engine):
        ContextBuilder.__init__(self, context_engine)
        UpdateHandler.__init__(self)

    def before(self, update):
        self.build_context(update)

    def after(self, update):
        self.save_context(update)
