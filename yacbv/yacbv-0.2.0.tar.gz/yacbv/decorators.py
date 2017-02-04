from django.utils.decorators import method_decorator


def class_decorator(decorator):
    """Simple decorator to decorate dispatch method"""
    def wrapper(klass):
        klass.dispatch = method_decorator(decorator)(klass.dispatch)

        return klass

    return wrapper
