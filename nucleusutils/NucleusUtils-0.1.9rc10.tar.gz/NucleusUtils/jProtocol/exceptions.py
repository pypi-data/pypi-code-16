from .entity import Entity

INTERNAL_SERVER_ERROR = 'Internal server error!'


class ProtocolError(Exception, Entity):
    public_fields = ('error', 'message')

    def __init__(self, message, server_exc=None):
        if isinstance(message, Exception):
            error = message.__class__.__name__
            message = str(message)
        else:
            error = self.__class__.__name__
        self.error = error
        self.message = message
        self.index = None
        self.server_exc = server_exc


class APIException(Exception):
    def __init__(self, error, message):
        self.error = error
        self.message = message

    def __str__(self):
        return self.error + ': ' + self.message
