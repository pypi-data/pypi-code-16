__version__ = '0.1.0'


def generates(container):
    def decorator(func):
        def wrapper(*args, **kwargs):
            return container(x for x in func(*args, **kwargs))
        return wrapper
    return decorator
