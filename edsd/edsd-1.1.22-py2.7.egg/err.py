# coding:utf-8
# Copyright (C) Alibaba Group

"""
Errors : A collection of exceptions used in the whole checking process.
"""
import functools

from . import __version__

__author__ = "Thomas Li <yanliang.lyl@alibaba-inc.com>"
__license__ = "GNU License"


class Ignore(Exception):
    """This exception can be used as a method return, which could be caught by
    the decorator, after this exception is caught, the decorator should return
    directly.

    """


class Fine(Exception):
    """This Exception used in a check point marked as 'OK'
    """


class _IE(Exception):
    """Base class of the errors."""
    data = None

    def __init__(self, *args, **kwargs):
        if kwargs.has_key('data'):
            self.data = kwargs.pop('data')

        super(Exception, self).__init__(*args, **kwargs)

class Info(_IE):
    """This Exception used in a check point marked as 'OK'
    """
    pass


class Failed(_IE):
    """This Exception used in a check point marked as 'FAILED'
    """

def report(clz, msg, **kwargs):
    """An utility used and ONLY USED in the checkpoint functions to report the
    result, this method is only to raise an exception to end the function's
    execution immediately.

    :param clz: The exception class about to raise.
    :param msg: Status message
    :raise : see clz, e,g: Fine(represents OK) or Failed (represents FAILED)
    """
    raise clz(msg, **kwargs)


report_ok = functools.partial(report, Fine)
report_fail = functools.partial(report, Failed)
report_info = functools.partial(report, Info)
