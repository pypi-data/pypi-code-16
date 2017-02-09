# coding=utf-8

from functools import wraps
from threading import Thread


def api_route(bp, *args, **kwargs):
    kwargs.setdefault('strict_slashes', False)

    def decorator(f):
        @bp.route(*args, **kwargs)
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        return f

    return decorator


"""
Async processing based on threads

Example:

@async
def dosomething(call_args):
    print call_args

"""


def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper
