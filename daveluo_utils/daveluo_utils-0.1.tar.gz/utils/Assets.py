#!/usr/bin/env python
# -*- coding:utf-8 -*-


class FailError(Exception):
    def __init__(self, msg="严重错误", error_id=-1, args=None):
        if args is not None:
            msg = msg % args
        Exception.__init__(self, msg)
        self.error_id = error_id


# noinspection PyPep8Naming
def Fail(msg, *args, **kwargs):
    msg = str(msg).__mod__(args)
    msg = str(msg).format(*args, **kwargs)
    raise FailError(msg)


def Assert(expr, msg="出现错误了", *args, **kwargs):
    if expr is None or expr is False:
        if len(args) > 0:
            msg = str(msg).__mod__(args)
            msg = str(msg).format(*args, **kwargs)
        raise FailError(msg)
