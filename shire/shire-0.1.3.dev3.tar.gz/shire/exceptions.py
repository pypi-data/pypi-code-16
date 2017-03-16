# -*- coding: utf-8 -*-


__all__ = ['ShireException', 'PoolInvalidStatusException', 'RestartJobException']


class ShireException(Exception):
    pass


class PoolInvalidStatusException(ShireException):
    pass


class RestartJobException(Exception):
    pass


