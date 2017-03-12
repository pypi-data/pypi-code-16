# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.conf import settings
from django.utils.functional import SimpleLazyObject as LazyObj
from django.utils.module_loading import import_string
import django
if django.VERSION[0:2] < (1, 9): #pragma: no cover
    from django.utils.functional import new_method_proxy
    class SimpleLazyObject(LazyObj):
        __iter__ = new_method_proxy(iter)
else:
    SimpleLazyObject = LazyObj

__all__ = ['CallbackRegistry', 'callback_registry']

class CallbackRegistry(object):
    __slots__ = ('callbacks', 'callback_paths')
    def __init__(self, defaults=None):
        if defaults is None:
            defaults = settings.CONTEXTAWARE_PROCESSORS
        self.callbacks = []
        self.callback_paths = []
        for default in defaults:
            self.register(default)

    def register(self, callback):
        if callback in self.callback_paths:
            raise ValueError("'{0!s}' is already in this callback "
                             "registry".format(callback))
        self.callback_paths.append(callback)
        _callback = import_string(callback)
        self.callbacks.append(_callback)

    def __iter__(self):
        return iter(self.callbacks)

callback_registry = SimpleLazyObject(CallbackRegistry)
