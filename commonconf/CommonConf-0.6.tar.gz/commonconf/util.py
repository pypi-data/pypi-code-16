from commonconf.proxy import ConfProxy
from unittest import TestCase


class override_settings(object):

    def __init__(self, *args, **kwargs):
        self.overrides = kwargs

    def _class(self, cls, *args, **kwargs):
        if not hasattr(cls, "tearDown") or not hasattr(cls, "setUp"):
            raise Exception("Need unittest protocol for class override")

        tearDown = cls.tearDown
        setUp = cls.setUp

        def wrapped_setup(*args, **kwargs):
            self.__enter__()
            setUp(*args, **kwargs)

        def wrapped_teardown(*args, **kwargs):
            tearDown(*args, **kwargs)
            self.__exit__()

        cls.tearDown = wrapped_teardown
        cls.setUp = wrapped_setup

        return cls

    def _function(self, func, *args, **kwargs):
        def wrapped(*args, **kwargs):
            try:
                self.__enter__()
                value = func(*args, **kwargs)
            finally:
                self.__exit__()
            return value
        return wrapped

    # This handles function decorators + class decorators.  Needs to switch
    # on argument type :(
    def __call__(self, decorated, *args, **kwargs):
        if isinstance(decorated, type):
            return self._class(decorated, *args, **kwargs)

        return self._function(decorated, *args, **kwargs)

    # These handle context managers, and are used by the others
    def __enter__(self, *args, **kwargs):
        ConfProxy.set_overrides(self.overrides)

    def __exit__(*args, **kwargs):
        ConfProxy.clear_overrides()
