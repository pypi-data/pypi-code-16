"""
Shaft

Error

"""


class ShaftError(Exception):
    """
    This exception is not reserved, but it used for all Shaft exception.
    It helps catch Core problems.
    """
    pass


class AppError(ShaftError):
    """
    Use this exception in your application level.
    """
    pass


class ModelError(AppError):
    """
    Use this exception in your model level.
    """
    pass


class ExtensionError(ShaftError):
    """
    This Exception wraps the exception that was raised.
    Having multiple extension, we need a way to catch them all :)
    """
    def __init__(self, exc):
        """
        :param exc: Exception
        """
        self.exception = exc
        message = "%s : %s" % (exc.__class__.__name__, exc.message)
        super(self.__class__, self).__init__(message)








