import functools
import threading


def run_thread(target, args=None, kwargs=None, name=None, include_thread=True):
    if not name:
        name = 'Thread("{}")'.format(target.__name__)
    thread = threading.Thread(target=target, args=args, kwargs=kwargs, name=name)
    if include_thread and '__thread__' in target.__code__.co_varnames:
        kwargs.update({'__thread__': thread})
        thread._kwargs = kwargs
    thread.start()
    return thread


class Thread(object):
    def __init__(self, func):
        self._target = func

    def __get__(self, obj, type=None):
        return functools.partial(self, obj)

    def __call__(self, *args, **kwargs):
        return run_thread(self._target, args, kwargs)
