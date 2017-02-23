# -*- coding: utf-8 -*-

from __future__ import absolute_import

from fanstatic import Library
from fanstatic import Resource
from js.jquery import jquery


library = Library(
    'jquery-maskmoney',
    'resources')
jquery_maskmoney = Resource(
    library,
    'jquery.maskMoney.js',
    minified='jquery.maskMoney.min.js',
    depends=[jquery, ])
