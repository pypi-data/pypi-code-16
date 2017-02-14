class Event:
    def __init__(self, evt_type, content):
        self.evt_type = evt_type
        self.content = content


class _EventBus:
    def __init__(self):
        self._listeners = {}

    def register(self, token, callback_fn):
        self._listeners[token] = callback_fn

    def deregister(self, token):
        if token in self._listeners:
            del self._listeners[token]

    def publish(self, evt: Event):
        for handler in self._listeners.values():
            handler(evt)


bus = _EventBus()
