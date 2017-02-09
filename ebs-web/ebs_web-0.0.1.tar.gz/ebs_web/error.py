# coding=utf-8

from flask import jsonify


def _lstrip_str(line, lstr):
    if line.startswith(lstr):
        return line[len(lstr):]
    return line


class BaseError(Exception):
    """Base class for exception

    Args:
        cname: class in which the error occured
        message: error message
        status_code: http status code
    """

    def __init__(self, cname, message, status_code):
        super(BaseError, self).__init__()
        self.cname = cname
        self.status_code = status_code

        msg = _lstrip_str(message, 'Error: ')
        msg = _lstrip_str(msg, '[Error]: ')
        self.message = msg

    def __str__(self):
        return '{}'.format(self.message)


class Unauthorized(BaseError):

    def __init__(self, cname):
        super(Unauthorized, self).__init__(cname, u'Unauthorized', 401)


class InvalidToken(BaseError):

    def __init__(self, cname):
        super(InvalidToken, self).__init__(cname, u'Invalide token', 405)


class ApiHTTPError(BaseError):
    """Generic Exception raised from API calls.
    """

    def __init__(self, message, status_code):
        super(ApiHTTPError, self).__init__(None, message, status_code)

    def build_response(self):
        resp = jsonify({'message': self.message,
                        'status_code': self.status_code})
        resp.status_code = self.status_code
        return resp
