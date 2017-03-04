from functools import update_wrapper
from six import with_metaclass
from pipeliner.exceptions import TaskAlreadyRegistered, TaskNotFound


class Singleton(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = type.__call__(cls, *args, **kwargs)
        return cls._instance


class Register(with_metaclass(Singleton, object)):
    """
    Handles task registration (including providers control)
    """

    _handlers = {}

    def add_handler(self, func_name, depends=[], provides=[]):
        if func_name not in self._handlers:
            self._handlers[func_name] = dict(depends=depends, provides=provides)
        else:
            raise TaskAlreadyRegistered()

    def get_handler(self, func_name):
        if func_name in self._handlers:
            return self._handlers[func_name]
        else:
            raise TaskNotFound()

    def _get_handler_data(self, func_name, data):
        return self.get_handler(func_name)[data]

    def get_depends(self, func_name):
        return self._get_handler_data(func_name, 'depends')

    def get_provides(self, func_name):
        return self._get_handler_data(func_name, 'provides')

    def _clear(self):
        """ Remove all handlers """
        self._handlers = {}


def task(depends=[], provides=[]):
    def wrapper(f):
        Register().add_handler(f.__name__, depends=depends, provides=provides)
        def args_wrapper(*args, **kwargs):
            def context_wrapper(context):
                f(context, *args, **kwargs)
                return context
            update_wrapper(context_wrapper, f)
            context_wrapper._applied = True
            return context_wrapper
        update_wrapper(args_wrapper, f)
        return args_wrapper
    return wrapper
