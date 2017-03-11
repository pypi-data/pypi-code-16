import threading

import ioc.loader


class EventListenerProvider(object):
    """Provides listeners for incoming events."""
    EventListenerRegistered = type('EventListenerRegistered', (Exception,), {})

    @property
    def listener_classes(self):
        return self._listener_classes

    def __init__(self, listener_classes=None):
        self._listener_classes = listener_classes or []
        self._listeners = []
        self._lock = threading.RLock()
        self.__initialized = False

    def register(self, cls):
        """Registers a event listener. Raises :exc:`EventListenerRegistered`
        if a listener is already registered for the event it declares to
        handle.
        """
        listener = cls()
        with self._lock:
            if listener in self._listeners:
                raise self.EventListenerRegistered(cls)
            self._listeners.append(listener)

    def is_initialized(self):
        return self.__initialized

    def get(self, event):
        if not self.is_initialized():
            self._setup()
        for listener in self._listeners:
            is_interested, params = listener.is_interested(event)
            if not is_interested:
                continue
            yield listener, params

    def _setup(self):
        with self._lock:
            # Check if self._initialized is True, because the caller
            # may have been locked by another thread that called
            # _setup()
            if self.is_initialized():
                return

            listeners = list(self.listener_classes)
            failed = []
            while listeners:
                cls = listeners.pop()
                try:
                    if isinstance(cls, str):
                        cls = ioc.loader.import_symbol(cls)
                    self.register(cls)
                except (self.EventListenerRegistered, ImportError) as e:
                    failed.append((e, cls))

            if failed:
                # TODO: A more descriptive error describing all
                # exceptions that occurred.
                raise failed[0][0]

            self.__initialized = True
