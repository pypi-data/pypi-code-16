# -*- coding: utf-8 -*-

"""
Takumi-ext
==========

Simple extension system for extending Takumi framework.

Every extension has a name and the name should be unique. The name
identifies the entry point the extension hooks in.

Different extensions have different implementations. One kind of
extension can only have one implementation. The use of an extension
determines its interface.

For example, here is an extension for running codes before app starts and
after app exists.

.. code:: python

    app = AppRunner()
    app_runner_ext = ext['app-runner']

    if app_runner_ext:
        runner_ext = app_runner_ext(app)
        app.cfg.set('when_ready', lambda x: runner_ext.on_start())
        app.cfg.set('on_exit', lambda x: runner_ext.on_exit())
    app.run()

To implement this extension:

.. code:: python

    # package name runner_ext
    class RunnerExt(ExtBase):
        name = 'app-runner'

        def __init__(self, app):
            self.app = app

        def on_start(self):
            print('app starting...')

        def on_exit(self):
            print('app existing...')

Add the following config to *app.yml* to use the extension:

.. code:: yaml

    extensions:
        - runner_ext

The extension implementation should be in its own package.

API
---
"""

import importlib

try:
    from types import MappingProxyType
except ImportError:
    import collections

    class MappingProxyType(collections.Mapping):
        def __init__(self, data):
            self._data = data

        def __getitem__(self, key):
            return self._data[key]

        def __len__(self):
            return len(self._data)

        def __iter__(self):
            return iter(self._data)


__all__ = ['ExtBase', 'ext']


class ExtMeta(type):
    name = None
    _registry = {}

    def __new__(self, name, bases, attrs):
        cls = type.__new__(self, name, bases, attrs)
        if name != 'ExtBase':
            self._registry[cls.name] = cls
        return cls


ExtBase = ExtMeta('ExtBase', (object,), {
    '__doc__': """Base class for registering extensions.

    The subclass should have a class attribute ``name`` which identifies the
    extension.
    """
})


class _ExtDict(object):
    """Extension manager for accessing specified extensions.

    To access an extension:

    >>> ext['extension-name']

    Extensions can have different usages which is determined by the interface
    the extension used.
    """
    def __init__(self):
        # The read-only view of the extension registry
        self.registry = MappingProxyType(ExtMeta._registry)

    def __getitem__(self, item):
        return self.registry.get(item)

ext = _ExtDict()


def _import_extensions():
    from takumi_config import config

    extensions = config.extensions or []
    for extension in extensions:
        importlib.import_module(extension)
# Eager import extensions
_import_extensions()
