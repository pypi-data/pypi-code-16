import os
import logging

from .os_cache import OSCache


def get_os_cache():
    cache = None
    if 'OS_API_CACHE' in os.environ:
        host = os.environ.get('OS_API_CACHE')
        cache_timeout = int(os.environ.get('OS_API_CACHE_TIMEOUT', 86400))
        cache = OSCache(host, 6379, cache_timeout)

        logging.error('CACHE %s', cache)
        logging.error('CACHE TIMEOUT %s', cache_timeout)
    return cache
