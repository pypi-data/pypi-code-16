# -*- coding: utf-8 -*-

"""
takumi_http.utils
~~~~~~~~~~~~~~~~~

Utilities for metadata handling.
"""


class Headers(object):
    """Used to query http headers from context
    """

    PREFIX = '__HEADER__'

    def __init__(self, ctx):
        self.ctx = ctx

    def _key(self, key):
        return ''.join([self.PREFIX, key.lower()])

    def get(self, key, default=None):
        return self.ctx.get(self._key(key), default)

    def __contains__(self, key):
        return self._key(key) in self.ctx

    def __getitem__(self, key):
        return self.ctx.get(self._key(key))

    def __setitem__(self, key, value):
        self.ctx[self._key(key)] = value

    def items(self):
        for k in self.keys():
            yield k, self[k]

    def keys(self):
        for k in self.ctx.keys():
            if not k.startswith(self.PREFIX):
                continue
            yield k.lstrip(self.PREFIX)

    def values(self):
        for _, v in self.items():
            yield v


class Qs(Headers):
    """Used to get query string items
    """

    PREFIX = '__QUERY_STRING__'


class HttpMeta(object):
    """For handling http related metadata

    :Example:

    >>> meta = HttpMeta(ctx)
    >>> meta.headers['content-type']
    >>> meta.qs['hello']

    :param ctx: context holding metadatas
    """
    def __init__(self, ctx):
        self.ctx = ctx
        self.headers = Headers(ctx)
        self.qs = Qs(ctx)

    @property
    def method(self):
        """Get http method
        """
        return self.ctx.get('method')

    @property
    def http_version(self):
        """Get http version
        """
        return self.ctx.get('http_version')
