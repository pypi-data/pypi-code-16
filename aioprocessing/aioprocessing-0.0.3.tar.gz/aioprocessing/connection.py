import multiprocessing
from multiprocessing.connection import (Listener, Client, deliver_challenge,
                                        answer_challenge, wait)

from .executor import CoroBuilder
from .util import run_in_executor

__all__ = ['AioConnection']


class AioConnection(metaclass=CoroBuilder):
    coroutines = ['recv', 'poll', 'send_bytes', 'recv_bytes',
                  'recv_bytes_into', 'send']

    def __init__(self, obj):
        """ Initialize the AioConnection.
        
        obj - a multiprocessing.Connection object.
        
        """
        super().__init__()
        self._obj = obj

    def __enter__(self):
        self._obj.__enter__()
        return self

    def __exit__(self, *args, **kwargs):
        self._obj.__exit__(*args, **kwargs)


def AioClient(*args, **kwargs):
    """ Returns an AioConnection instance. """
    conn = Client(*args, **kwargs)
    return AioConnection(conn)


class AioListener(metaclass=CoroBuilder):
    delegate = Listener
    coroutines = ['accept']

    def accept(self):
        conn = self._obj.accept()
        return AioConnection(conn)

    def __enter__(self):
        self._obj.__enter__()
        return self

    def __exit__(self, *args, **kwargs):
        self._obj.__exit__(*args, **kwargs)


def coro_deliver_challenge(*args, **kwargs):
    executor = ThreadPoolExecutor(max_workers=1)
    return run_in_executor(executor, deliver_challenge, *args, **kwargs)

def coro_answer_challenge(*args, **kwargs):
    executor = ThreadPoolExecutor(max_workers=1)
    return run_in_executor(executor, answer_challenge, *args, **kwargs)

def coro_wait(*args, **kwargs):
    executor = ThreadPoolExecutor(max_workers=1)
    return run_in_executor(executor, wait, *args, **kwargs)

