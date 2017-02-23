# -*- coding: utf-8 -*-
import time


URLS = [
    'just=some&post=data',
    '/some/path',
    'http://example.com/foo',
    'http://example.com/foo?a=1'
]

# lets have some creazy utf-8 key
KEYS = ['1234asdf', u'♥ unicode ♥']

# checl different expire times are used
EXPIRES = [5, 60]

# check different times, including one bigger than 32 bit
TIMES = [0, int(time.time()), 2**33]
