"""A pure Python API API."""
from typing import Callable

from .conversion import build_converter
from .endpoint import Endpoint

__all__ = ['api', 'endpoint']
__author__ = 'Jonathan Sharpe'
__version__ = '0.0.2'


def api(base_url: str) -> Callable[[type], type]:
    """Decorator for creating root API classes.

    Arguments:
      base_url: The base URL of the API.

    Returns:
      The wrapper for the API class.

    """
    def wrapper(cls: type) -> type:
        for val in cls.__dict__.values():
            if isinstance(val, Endpoint):
                val.base_url = base_url
        return cls
    return wrapper


def endpoint(path: str) -> Callable[[], Endpoint]:
    """Decorator for creating an

    Arguments:
      path: The path to the API endpoint (relative to the API's
        ``base_url``).

    Returns:
      The wrapper for the endpoint method.

    """
    def wrapper(method):
        return Endpoint(path, build_converter(method))
    return wrapper
