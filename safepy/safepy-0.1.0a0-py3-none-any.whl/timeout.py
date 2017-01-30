import asyncio
from asyncio import CancelledError
from functools import wraps



class TimeoutError(Exception):
    pass


def timeout(time):

    def decorator(function):

        @wraps(function)
        async def wrapper(*args, **kwargs):
            # TODO: explicit loop - yes, no?

            try:
                await asyncio.wait_for(function(*args, **kwargs), time)

            except CancelledError as e:
                raise TimeoutError() from e

        return wrapper

    return decorator
