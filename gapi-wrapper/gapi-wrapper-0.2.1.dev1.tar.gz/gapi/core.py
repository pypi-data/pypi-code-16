# -*- coding: utf-8 -*-
import logging
import types
from functools import wraps

from .exceptions import APINoMethod, APIMethodNotAllowed


def customer_callable(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        return func(*args, **kwargs)
    wrapped.customer_callable = True
    return wrapped


class GoogleService(object):
    USER_AGENT = 'Digly Lib v2.0'
    _cache = None
    log = logging.getLogger('diglib.gapi')

    def __init__(self, refresh=False):
        self.refresh = refresh

    def call_method(self, name, params=None, refresh=None, cache_timeout=1800):
        cache_key = self._get_cache_key(name, params)
        refresh = self.refresh if refresh is None else refresh
        if self._cache is not None and not refresh:
            cached = self._cache.get_cache(params=cache_key)
            if cached is not None:
                return cached

        method = getattr(self, name, None)
        if method is None or (not callable(method)):
            raise APINoMethod("Nonexistent method {}".format(name))
        if not getattr(method, 'customer_callable', False):
            raise APIMethodNotAllowed("Forbidden method {}".format(name))
        try:
            data = method(**params) if params else method()
            if isinstance(data, types.GeneratorType):
                data = list(data)
            data = self._data_post_processing(data)
            if self._cache is not None:
                self._cache.set_cache(data, params=cache_key, timeout=cache_timeout)
            return data
        except Exception:
            self.log.exception("GoogleService: method {}, params={}".format(name, params))
            raise

    def _get_cache_key(self, name, params):
        return [name, params]

    def _data_post_processing(self, data):
        return data

    def __call__(self, name, params=None, **kwargs):
        return self.call_method(name, params=params, refresh=kwargs.get('refresh', None))

    def set_refresh(self, refresh=False):
        self.refresh = refresh