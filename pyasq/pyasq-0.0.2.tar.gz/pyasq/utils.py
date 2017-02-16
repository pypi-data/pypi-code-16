from functools import wraps

JSON_PRIMITIVES = (str, int, float, bool)
"""The four JSON primitive types."""


def memoize(func):
    """Standard memoization decorator."""
    @wraps(func)
    def wrapper(key):
        if key not in wrapper.cache:
            wrapper.cache[key] = func(key)
        return wrapper.cache[key]
    wrapper.cache = {}
    return wrapper
