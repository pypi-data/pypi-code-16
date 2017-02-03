VERSION = (0, 99, 9)


def get_version():
    return u'.'.join((unicode(num) for num in VERSION))

__version__ = get_version()
