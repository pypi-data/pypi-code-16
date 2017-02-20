from __future__ import absolute_import

from functools import wraps

from turbodbc_intern import Error as InternError


# Python 2/3 compatibility
try:
    from exceptions import StandardError as _BaseError
except ImportError:
    _BaseError = Exception


class Error(_BaseError):
    pass


class InterfaceError(Error):
    pass


class DatabaseError(Error):
    pass 


def translate_exceptions(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        try:
            return f(*args, **kwds)
        except InternError as e:
            raise DatabaseError(str(e))
    return wrapper