import functools
import inspect
import warnings


def get_full_object_name(obj):
    """
    Get full name of object
    :param obj:
    :return:
    """
    result = []
    if hasattr(obj, '__module__'):
        result.append(getattr(obj, '__module__'))
    if hasattr(obj, '__name__'):
        result.append(getattr(obj, '__name__'))
    return '.'.join(result)


class Deprecated(object):
    def __init__(self, reason):
        if inspect.isclass(reason) or inspect.isfunction(reason):
            raise TypeError("Reason for deprecation must be supplied")
        self.reason = reason

    def __call__(self, cls_or_func):
        if inspect.isfunction(cls_or_func):
            if hasattr(cls_or_func, 'func_code'):
                _code = cls_or_func.func_code
            else:
                _code = cls_or_func.__code__
            fmt = "Call to deprecated function or method {name} ({reason})."
            filename = _code.co_filename
            lineno = _code.co_firstlineno + 1

        elif inspect.isclass(cls_or_func):
            fmt = "Call to deprecated class {name} ({reason})."
            filename = cls_or_func.__module__
            lineno = 1

        else:
            raise TypeError(type(cls_or_func))

        msg = fmt.format(name=cls_or_func.__name__, reason=self.reason)

        @functools.wraps(cls_or_func)
        def new_func(*args, **kwargs):
            warnings.simplefilter('always', DeprecationWarning)  # turn off filter
            warnings.warn_explicit(msg, category=DeprecationWarning, filename=filename, lineno=lineno)
            warnings.simplefilter('default', DeprecationWarning)  # reset filter
            return cls_or_func(*args, **kwargs)

        return new_func


@Deprecated('Bad method')
def simple_deprecated(description=None, url=None, new_line=True):
    """
    Mark function or method as deprecated
    :param description: short description
    :param url: to issue
    :param new_line: need split lines
    :return:
    """

    def wrapper(func):
        func_name = '.'.join([func.__module__, func.__name__])
        message = ["[WARNING]\tMethod '{}' deprecated and will be removed in the future.".format(func_name)]
        if description is not None:
            message.append('\tDescription: ' + str(description))
        if url is not None:
            message.append('\tURL: ' + str(url))
        print(('\n' if new_line else '').join(message))
        return func

    return wrapper
