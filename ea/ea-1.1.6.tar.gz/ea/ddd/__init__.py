import functools

from ea.lib.datastructures import DTO
from ea.ddd.aggregate import Aggregate
from ea.ddd.repository import Repository


def publishes(typename):
    """A decorator that wraps an method of a :class:`Aggregate`
    and publishes a domain event of `typename` with the
    return value of the method.
    """
    def decorator(func):
        @functools.wraps(func)
        def inner(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            self.publisher.publish(typename, result)
            return result
        
        return inner

    return decorator
