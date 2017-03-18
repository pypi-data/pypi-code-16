from threading import Event


class WaitableDict:
    def __init__(self, data=None, timeout=5):
        if data is None:
            data = {}
        self.data = data
        self.timeout = timeout

        self.events = {k: Event() for k in data.keys()}

    def __setitem__(self, key, value):
        self.data[key] = value
        if key not in self.events:
            self.events[key] = Event()
        self.events[key].set()
        self.events[key].clear()

    def __delitem__(self, key):
        self.events[key].set()
        del self.data[key]
        del self.events[key]

    def __getitem__(self, key):
        if key not in self.events:
            self.events[key] = Event()
        if key not in self.data:
            self.events[key].wait(self.timeout)
        return self.data[key]

    def __contains__(self, item):
        return item in self

    def __iter__(self):
        yield from self.data

    def get(self, key, default=None):
        try:
            return self[key]
        except:
            return default
