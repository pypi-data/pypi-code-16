import functools

from NucleusUtils.logging.dumps import CrashDump


def dump_exception(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            with CrashDump() as report:
                report.new_line('args: ' + str(args))
                report.new_line('kwargs: ' + str(kwargs))
            raise

    return wrapper


def handle_exceptions(name='', no_raise=True, handler=None):
    """
    Decorator for handling exceptions
    :param name: Name of crash report
    :param no_raise: prevent to raise exceptions. Return None
    :param handler: handler function must have 4 arguments: 'function', 'args', 'kwargs' and 'report'
    :return:
    """

    def dump_exception_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except:
                with CrashDump(name) as report:
                    report.new_line('args: ' + str(args))
                    report.new_line('kwargs: ' + str(kwargs))
                    if callable(handler):
                        handler(func, args, kwargs, report)
                if no_raise:
                    return None
                raise

        return wrapper

    return dump_exception_decorator
