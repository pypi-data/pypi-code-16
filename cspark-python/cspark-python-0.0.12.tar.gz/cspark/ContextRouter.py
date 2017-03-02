from .Router import Router
from .ContextBuilder import ContextBuilder


class ContextRouter(ContextBuilder, Router):

    def __init__(self, context_engine=None):
        super(ContextRouter, self).__init__(context_engine)

    def handle_update(self, update):
        self.build_context(update)
        handler_class = self.get_handler_class()
        self.save_context(update)

        handler = handler_class(
            context_engine=self.get_context_engine()
        )

        handler.before(update)
        new_handler_class = handler.handle_update(update)
        handler.after(update)

        while new_handler_class:
            new_handler = new_handler_class(context_engine=self.get_context_engine())

            new_handler.before(update)
            new_handler_class = new_handler.handle_update(update)
            new_handler.after(update)
