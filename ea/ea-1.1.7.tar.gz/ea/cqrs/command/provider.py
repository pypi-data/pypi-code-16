import threading

import ioc.loader

from ea.cqrs.exc import MissingCommandHandler


class CommandHandlerProvider(object):
    """Provides handlers for incoming commands."""
    CommandHandlerRegistered = type('CommandHandlerRegistered', (Exception,), {})
    MissingCommandHandler = MissingCommandHandler

    @property
    def handler_classes(self):
        return self._handler_classes

    @classmethod
    def fromqualnames(cls, qualnames):
        return cls([ioc.loader.import_symbol(x) for x in qualnames])

    def __init__(self, handler_classes=None):
        self._handler_classes = handler_classes or []
        self._handlers = {}
        self._lock = threading.RLock()
        self.__initialized = False

    def register(self, handler):
        """Registers a command handler. Raises :exc:`CommandHandlerRegistered`
        if a handler is already registered for the command it declares to
        handle.
        """
        with self._lock:
            if handler.command_name in self._handlers:
                raise self.CommandHandlerRegistered(handler.command_name)
            self._handlers[handler.command_name] = handler()

    def is_initialized(self):
        return self.__initialized

    def get(self, name):
        if not self.is_initialized():
            self._setup()

        if name not in self._handlers:
            raise MissingCommandHandler(name)
        return self._handlers[name]

    def _setup(self):
        with self._lock:
            # Check if self._initialized is True, because the caller
            # may have been locked by another thread that called
            # _setup()
            if self.is_initialized():
                return

            handlers = list(self.handler_classes)
            failed = []
            while handlers:
                cls = handlers.pop()
                try:
                    if isinstance(cls, str):
                        cls = ioc.loader.import_symbol(cls)
                    self.register(cls)
                except (self.CommandHandlerRegistered, ImportError) as e:
                    failed.append((e, cls))

            if failed:
                # TODO: A more descriptive error describing all
                # exceptions that occurred.
                raise failed[0][0]

            self.__initialized = True
