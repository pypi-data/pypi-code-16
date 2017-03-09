
class BaseException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class ParamInvalidError(BaseException):
    def __init__(self, message):
        BaseException.__init__(self, message)


class AccessKeyInvalidError(BaseException):
    def __init__(self, message):
        BaseException.__init__(self, message)


class ResourceUnauthorizedError(BaseException):
    def __init__(self, message):
        BaseException.__init__(self, message)


class ResourceNotFoundError(BaseException):
    def __init__(self, message):
        BaseException.__init__(self, message)


class ActionDisallowError(BaseException):
    def __init__(self, message):
        BaseException.__init__(self, message)


class RequestFormatInvalidError(BaseException):
    def __init__(self, message):
        BaseException.__init__(self, message)


class QuotaNotEnoughError(BaseException):
    def __init__(self, message):
        BaseException.__init__(self, message)


class ServerErrorError(BaseException):
    def __init__(self, message):
        BaseException.__init__(self, message)


class ActionsTotallyFailedError(BaseException):
    def __init__(self, message):
        BaseException.__init__(self, message)


class ActionsPartiallyFailedError(BaseException):
    def __init__(self, message):
        BaseException.__init__(self, message)


class HTTPError(Exception):
    def __init__(self, status_code):
        self.status_code = status_code

    def __str__(self):
        return 'http failed status=%s' % self.status_code
