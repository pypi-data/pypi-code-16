#-*-coding:utf-8-*-
__author__ = 'cchen'
import inspect

class Dialect(object):
    """
    is_remove_repeated_char
    is_remove_newlines
    """

    to_lower = None
    remove_repeated_char = None
    remove_newlines = None
    remove_illformed = None

    def __init__(self, **kwargs):
        for arg in kwargs:
            if not hasattr(self, arg):
                raise TypeError("'%s' is an invalid keyword argument for this function:%s" % (arg, Dialect.__doc__))
            setattr(self, arg, kwargs[arg])

    def __getitem__(self, item):
        try:
            return getattr(self, item)
        except AttributeError:
            raise AttributeError("The object has no attribute '%s'" % item)


class twitter(Dialect):
    to_lower = True
    remove_repeated_char = True
    remove_newlines = True
    remove_illformed = True
