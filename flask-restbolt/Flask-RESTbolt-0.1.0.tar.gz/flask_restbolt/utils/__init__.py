try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
from flask import abort as original_flask_abort
from werkzeug.http import HTTP_STATUS_CODES


def abort(http_status_code, **kwargs):
    """Raise a HTTPException for the given http_status_code. Attach any keyword
    arguments to the exception for later processing.
    """
    #noinspection PyUnresolvedReferences
    try:
        original_flask_abort(http_status_code)
    except HTTPException as e:
        if len(kwargs):
            e.data = kwargs
        raise


def http_status_message(code):
    """Maps an HTTP status code to the textual status"""
    return HTTP_STATUS_CODES.get(code, '')


def unpack(value):
    """Return a three tuple of data, code, and headers"""
    if not isinstance(value, tuple):
        return value, 200, {}

    try:
        data, code, headers = value
        return data, code, headers
    except ValueError:
        pass

    try:
        data, code = value
        return data, code, {}
    except ValueError:
        pass

    return value, 200, {}
