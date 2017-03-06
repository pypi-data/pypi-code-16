class BotSocketBaseException(Exception):
    """Base exception"""
    pass


class BotSocketWrapperException(BotSocketBaseException):
    """Wrap exception"""

    def __init__(self, msg, original_exception):
        super().__init__(msg + '(: %s)' % original_exception)
        self.original_exception = original_exception


class KillServerException(SystemExit):
    "Raise it in command to stop server"
    pass
