# -*- coding: utf-8

from __future__ import unicode_literals

import requests
import hashlib

from django.core.cache import cache

from . import __version__
from .conf import DANDELION_HOST, DANDELION_TOKEN, DANDELION_USE_CACHE
from .exceptions import DandelionException


class AttributeDict(dict):
    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        del self[name]


class BaseDandelionRequest(object):
    def __init__(self):
        self.__requests = requests.session()
        self.__uri = DANDELION_HOST if DANDELION_HOST.startswith('http') else 'https://' + DANDELION_HOST

    def _do_request(self, extra_url='', method='post', extra_dict=None, use_cache=False):
        if extra_dict is None:
            params = {}
        else:
            params = extra_dict.copy()
        params['token'] = DANDELION_TOKEN

        url = self.__uri + ''.join('/' + x for x in extra_url)

        cache_key = self.__cache_get_key_for(url=url, params=params, method=method)
        if cache.get(cache_key) and use_cache:
            response = cache.get(cache_key)
        else:
            response = self.__do_raw_request(url, params, method)
            if response.ok and use_cache:
                cache.set(cache_key, response)

        obj = response.json(object_hook=AttributeDict)
        if not response.ok:
            raise DandelionException(message=obj.message, code=obj.code, data=obj.data)

        return obj

    def __do_raw_request(self, url, params, method):
        kwargs = {
            'data' if method in ('post', 'put') else 'params': params,
            'url': url,
            'headers': {
                'User-Agent': 'django-dandelion/' + __version__
            }
        }

        return getattr(self.__requests, method)(**kwargs)

    @staticmethod
    def __cache_get_key_for(**kwargs):
        input_s = ''
        for key in sorted(kwargs):
            input_s += u'{}={},'.format(key, kwargs[key])
        input_s = input_s.encode('utf-8')
        return 'dandelion_' + hashlib.sha1(input_s).hexdigest()


class BaseDandelionParamsRequest(BaseDandelionRequest):
    def __init__(self, keys_allowed, keys_unique, **params):
        self.__keys_allowed = keys_allowed
        self.__keys_unique = keys_unique

        self.__params = params
        for key in params:
            self.__validate_param(key)

        super(BaseDandelionParamsRequest, self).__init__()

    def _do_request(self, extra_url='', method='post', extra_dict=None, use_cache=DANDELION_USE_CACHE):
        return super(BaseDandelionParamsRequest, self)._do_request(
            extra_url=extra_url,
            method=method,
            extra_dict=self.__params,
            use_cache=use_cache
        )

    def __validate_param(self, key):
        if key not in self.__keys_allowed:
            raise DandelionException(message='Key not allowed; you can use the following keys: {}'.format(
                ', '.join(self.__keys_allowed)))

        for keys in self.__keys_unique:
            if key in keys:
                temp = set(keys)
                temp.discard(key)
                intersection = list(set(self.__params.keys()) & temp)
                if len(intersection) > 0:
                    self.__params_remove_key(intersection[0])

    @property
    def params(self):
        return self.__params

    @params.setter
    def params(self, value):
        if not isinstance(value, (list, set, tuple)) or len(value) != 2:
            raise DandelionException(message='Two inputs are required: key and value')

        self.__validate_param(value[0])
        self.__params[value[0]] = value[1]

    @params.deleter
    def params(self):
        self.__params = {}

    def __params_remove_key(self, key):
        del self.__params[key]

    def analyze(self):
        raise NotImplementedError
