# Copyright (C) 2017 Michał Góral.
#
# This file is part of Feed Commas
#
# Feed Commas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Feed Commas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Feed Commas. If not, see <http://www.gnu.org/licenses/>.

'''Caching HTTP requests'''

import os
import pickle
import functools
from datetime import datetime, timedelta
import mgcomm.env

import feedcommas.config as config
import feedcommas._version as version


_cache = {}
_cache_dir = os.path.join(mgcomm.env.home(), '.cache', 'feed-commas')


def init():
    '''Initialize a cache. Should be called before any
    accessors/decorators/other functions.'''
    if cache_time() <= 0 or bool(_cache):
        return

    try:
        files = [f for f in os.listdir(_cache_dir)]
    except FileNotFoundError:
        return

    for filename in files:
        fpath = os.path.join(_cache_dir, filename)
        if not os.path.isfile(fpath):
            continue

        try:
            with open(os.path.join(_cache_dir, filename), 'rb') as f:
                _cache[filename] = pickle.load(f)
        except (FileNotFoundError, EOFError):
            pass


def save(key=None):
    '''Save a cache to the persistent storage (err, to the disk)'''
    if cache_time() <= 0:
        return

    try:
        os.makedirs(_cache_dir)
    except FileExistsError:
        pass

    if key:
        _save_impl(key, _cache[key])
    else:
        for key, val in _cache.items():
            _save_impl(key, val)


def clear():
    '''Clear (invalidate) cache'''
    _cache.clear()
    save()


def get(name):
    '''Decorator to be used on a function which is able to fetch things from the
    cache.'''
    def _decorator(fn):
        @functools.wraps(fn)
        def _wrapped(obj, callback, *args, **kwargs):
            ctime = cache_time()

            if ctime <= 0:
                return fn(obj, callback, *args, **kwargs)

            cache = _cache.setdefault(name, {})

            key = _make_key(type(obj).__name__, fn.__name__, *args, **kwargs)
            entry = cache.get(key, CacheEntry(ctime))
            if entry.valid():
                callback(entry.data)
                return entry.returned
            else:
                caching_cb = functools.partial(_set_cache, callback, entry)
                entry.returned = fn(obj, caching_cb, *args, **kwargs)
                cache[key] = entry
                return entry.returned
        return _wrapped
    return _decorator


def invalidate(*names):
    '''Any call to the decorated functions will invalidate caches with a given
    names.'''
    def _decorator(fn):
        @functools.wraps(fn)
        def _wrapped(*args, **kwargs):
            for name in names:
                try:
                    _cache[name] = {}
                    save(name)
                except KeyError:
                    pass
            return fn(*args, **kwargs)
        return _wrapped
    return _decorator


def modify(iterable):
    '''Accepts a list of tuples: (name, func). For each cache with a given name,
    a func will be applied after a wrapped function is called. `func` accepts a
    CacheEntry, which public members can be safely accessed. `func` is also
    passed all arguments and keyword arguments passed to the wrapped
    function.'''
    def _decorator(fn):
        @functools.wraps(fn)
        def _wrapped(*args, **kwargs):
            ret = fn(*args, **kwargs)

            if cache_time() <= 0:
                return ret

            # We don't check cache-time here, but modify everything to avoid
            # problems when user changes cache-time in between two Feed Commas
            # runs.
            for name, mod in iterable:
                cache = _cache.get(name, [])
                for entry in cache:
                    cached_entry = cache[entry]
                    if cached_entry.data:
                        mod(cached_entry, *args, **kwargs)
                save(name)
            return ret
        return _wrapped
    return _decorator


class CacheEntry:
    '''Cache entry'''
    def __init__(self, expiration, data=None):
        self.delta = timedelta(minutes=expiration)
        self._version = version.version
        self.update(data)

    def update(self, data):
        '''Update a cached data'''
        self.created = datetime.now()
        self.data = data

    def valid(self):
        '''Returns whether entry is valid.'''
        return (version.version >= self._version and
                self.data and (self.created + self.delta >= datetime.now()))


def cache_time():
    '''Helper function which safely fetches cache settings from a
    configuration.'''
    settings = config.config()['settings']
    try:
        return settings.getint('cache-time')
    except ValueError:
        return 0


def _set_cache(callback, entry, data):
    entry.update(data)
    callback(data)
    save()


def _make_key(*args, **kwargs):
    key = args
    if kwargs:
        key += tuple(sorted(kwargs.items()))
    return key


def _save_impl(key, val):
    with open(os.path.join(_cache_dir, key), 'wb') as f:
        pickle.dump(val, f, pickle.HIGHEST_PROTOCOL)
