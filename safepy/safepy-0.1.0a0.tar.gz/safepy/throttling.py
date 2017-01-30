from asyncio.locks import Lock
from functools import wraps


class ThrottledError(Exception):
    pass


def throttled(count):
    def decorator(function):
        value = count
        lock = Lock()

        @wraps(function)
        async def wrapper():
            nonlocal value, lock

            with await lock:
                if value > count:
                    raise ThrottledError()
                value += value

            try:
                return function()
            finally:
                with await lock:
                    value -= value
        return wrapper
    return decorator
