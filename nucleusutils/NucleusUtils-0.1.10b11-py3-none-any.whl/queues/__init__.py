import threading
import time

from NucleusUtils.queues.iterator import Iterator
from NucleusUtils.singleton import Singleton

DEFAULT_QUERY_LIFETIME = 30


class QueueManager(metaclass=Singleton):
    def __init__(self):
        self.queue = {}
        self.queries = {}
        self.unhandled_handlers = []
        self.locked = False
        self.iterator = Iterator()

    def lock(self):
        self.locked = True

    def unlock(self):
        self.locked = False

    def is_locked(self):
        return self.locked

    def add_query(self, query):
        """
        Register query
        :param query:
        :return:
        """
        if not self.is_locked():
            self.queries[query.get_index()] = query
        raise RuntimeError('Queue is locked!')

    def remove_query(self, query):
        """
        Un-register query
        :return:
        """
        if query.get_index() in self.queries.keys():
            del self.queries[query.get_index()]

    def done_query(self, index, data=None):
        if data is None:
            data = {}

        self.queue[index] = data

        # Handle unregistered response
        if index not in self.queries:
            self.call_unregistered_handler(index)

    def clean_queue(self):
        self.lock()
        queries = self.queries.copy()
        for query in queries.values():
            query.kill()
            del query
        del queries

    def register_unhandled_handler(self, function):
        self.unhandled_handlers.append(function)

    def unaregister_unhandled_handler(self, function):
        if function in self.unhandled_handlers:
            self.unhandled_handlers.remove(function)

    def call_unregistered_handler(self, index):
        for handler in self.unhandled_handlers:
            handler(index, self.queue[index])


class Query:
    """
    Query processor.
    """

    def __init__(self, name='query', target=None, args=None, kwargs=None, lifetime=DEFAULT_QUERY_LIFETIME,
                 index_key='index'):
        """
        Create query request and prepare to proceed
        :param name: str - query name (system)
        :param target: callable - function (sending method)
        :param args: list or tuple - target args
        :param kwargs: dict - target key-value args
        :param lifetime: int - query lifetime
        :param index_key: str
        """
        self.name = name
        self._index = -1
        self.target = target
        self.lifetime = lifetime
        self.index_key = index_key

        self._callback = None

        if args is None:
            args = []
        if kwargs is None:
            kwargs = {index_key: self._index}

        self.args = args
        self.kwargs = kwargs

        self._kill = False

        self.manager = QueueManager()

    def start(self, callback=None):
        """
        Call function and wait result
        :type callback: callable object (for async) or None (for linear)
        :return: result (if it's linear request) or thread (async request)
        """
        self._index = self.manager.iterator.next()
        self._exec(*self.args, **self.kwargs)
        self.manager.add_query(self)
        if callable(callback):
            # "Async" request
            # BUGFIX: TypeError: 'dict' object is not callable
            # Why 'dict'? Don't know..
            self._callback = callback
            thread = threading.Thread(target=self._lock(), name='{}_{}'.format(self.name, self._index))
            thread.start()
            return thread
        else:
            return self._lock()

    def kill(self):
        """
        Kill request
        :return:
        """
        self.manager.remove_query(self)
        self._kill = True

    def get_index(self) -> int:
        """
        Get process index
        :return: int
        """
        return self._index

    def _exec(self, *args, **kwargs):
        """
        Call target function
        :param args:
        :param kwargs:
        :return:
        """
        kwargs[self.index_key] = self._index
        if callable(self.target):
            self.target(*args, **kwargs)

    def _lock(self):
        """
        Wait result
        :return: result (linear/async) or TimeoutError
        """
        # TODO: remake using threading.Lock()
        start = time.time()
        try:
            while time.time() - start <= self.lifetime and not self._kill:
                if self._index in self.manager.queue or 0 in self.manager.queue:
                    result = self.manager.queue[0 if 0 in self.manager.queue else self._index]
                    del self.manager.queue[0 if 0 in self.manager.queue else self._index]
                    self.manager.remove_query(self)
                    if callable(self._callback):
                        # For async request
                        return self._callback(result)
                    else:
                        # For linear request
                        return result
        except KeyboardInterrupt:
            return None
        raise TimeoutError(
            'query: "{query}", timeout: {timeout}, index: {index}'.format(query=self.name, timeout=self.lifetime,
                                                                          index=self._index))
