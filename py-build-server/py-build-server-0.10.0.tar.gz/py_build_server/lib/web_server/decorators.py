def except_attribute_error(f):
    def wrapper(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except AttributeError:
            pass
    return wrapper


def multi_line_log(f):
    def wrapper(self, msg, *args):
        for msg in msg.splitlines():
            f(self, msg, *args)
    return wrapper


def while_true(f):
    def wrapper(*args, **kwargs):
        while True:
            f(*args, **kwargs)
    return wrapper

