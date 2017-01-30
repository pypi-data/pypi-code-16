import types
from functools import wraps


def handle_bounded_methods(decorator_function):
    """
    We went meta - a decorator for decorators. METORATOR!
    """
    @wraps(decorator_function)
    def wrapper(function):
        if getattr(function, '__self__', None) is None:
            return decorator_function(function)

        # with __self__ it's bounded, so we need special handling to support it

        method_self = function.__self__
        method_function = function.__func__

        wrapped_method_function = decorator_function(method_function)

        return types.MethodType(wrapped_method_function, method_self)

    return wrapper
