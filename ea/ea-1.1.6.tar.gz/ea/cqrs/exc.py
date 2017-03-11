import ea.exc


class MissingCommandHandler(Exception):

    def __init__(self, name):
        self.name = name

    def __getstate__(self):
        return {
            'name': name
        }

    def __setstate__(self, dto):
        self.__dict__.update(dto)


class CommandFailed(Exception):

    def __init__(self, handler, exc):
        self.handler = handler
        self.exc = exc

    def __getstate__(self):
        return {
            'exc': exc
        }

    def __setstate__(self, dto):
        self.__dict__.update(dto)


class CommandRejected(Exception):

    def __init__(self, request, command, reason=None):
        self.request = request
        self.command = command
        self.reason = reason


class CommandHandlingTimeout(ea.exc.Timeout):
    """Raised when a blocking command request was issued
    and handling was not finished within the specified
    timeout.
    """
