# -*- coding: utf-8 -*-

__all__ = ['GAPIException', 'APIValueError', 'APINoMethod', 'APINoData',
           'APIMethodNotAllowed', 'APIInternalError', 'APINotAllowed', 'APIInvalidCredentials']


class GAPIException(Exception):
    pass


class APIException(GAPIException):
    data = {}

    def __init__(self, message, **kwargs):
        super(Exception, self).__init__(message)
        self.data = kwargs

    def __str__(self):
        return '{}: {}'.format(self.message, self.data)


class APIValueError(APIException):
    pass


class APINoMethod(APIException):
    pass


class APINoData(APIException):
    pass


class APIMethodNotAllowed(APIException):
    pass


class APIInternalError(APIException):
    pass


class APINotAllowed(APIException):
    pass


class APIInvalidCredentials(APINotAllowed):
    pass


class APIQuotaLimit(APIException):
    pass


class APIParallelRequests(APIException):
    pass


class APINetworkError(APIException):
    pass


class APIInvalidVersion(APIException):
    # TODO RequestError UNSUPPORTED_VERSION
    pass


