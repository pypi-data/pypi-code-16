from .log import logger
from yaz.decorator import decorator
import functools

@decorator
def cache(func):
    def generate_key(args, kwargs):
        # todo: do not cache when args and kwargs are not collections.Hashable (i.e. when we can not
        # generate a proper key)
        return args, tuple(sorted((key, value) for key, value in kwargs.items()))

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = generate_key(args, kwargs)

        if key in _cache:
            logger.debug("Cache hit for %s with key %s", func, key)
        else:
            logger.debug("Cache miss for %s with key %s", func, key)
            _cache[key] = func(*args, **kwargs)

        return _cache[key]

    _cache = {}
    return wrapper

