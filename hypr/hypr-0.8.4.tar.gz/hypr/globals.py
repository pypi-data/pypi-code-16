# Copyright 2014-2016 Morgan Delahaye-Prat. All Rights Reserved.
#
# Licensed under the Simplified BSD License (the "License");
# you may not use this file except in compliance with the License.
"""Task context global variables."""


import tasklocals
from functools import partial


class LocalStorage:
    """A key-value data storage bind with a task context."""

    _app = None
    _task = None

    @classmethod
    def bind(cls, app):
        """Bind the storage to the app."""
        cls._app = app
        cls._task = tasklocals.local(loop=app.loop)

    def app(self):
        """Return the app."""
        return self._app

    def set(self, name, attr):
        """Set an attribute to the task context."""
        if self._task is None:  # pragma: no cover
            raise RuntimeError('LocalStorage is not bind to an application.')
        setattr(self._task, name, attr)

    def get(self, name, default=...):
        """Get an attribute from the task context."""
        if self._task is None:
            raise RuntimeError('LocalStorage is not bind to an application.')
        rv = getattr(self._task, name, default)

        if rv is Ellipsis:  # pragma: no cover
            raise KeyError(name)
        return rv

    def delete(self, name):  # pragma: no cover
        """Delete an attribute from the task context."""
        if self._task is None:
            raise RuntimeError('LocalStorage is not binded to an application')
        delattr(self._task, name)


class _Proxy:

    def __init__(self, proxy):
        self._proxy = proxy

    def __getattr__(self, attr):
        proxy = self._proxy()
        return getattr(proxy, attr)

    def __eq__(self, other):
        return other is self._proxy()

    def __repr__(self):
        proxy = self._proxy()
        return '<Proxy: %s>' % proxy.__repr__()


request = _Proxy(partial(LocalStorage().get, 'request'))
current_app = _Proxy(partial(LocalStorage().app))
