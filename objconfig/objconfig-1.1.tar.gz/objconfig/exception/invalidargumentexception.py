from objconfig.exception.exceptioninterface import ExceptionInterface


class InvalidArgumentException(RuntimeError, ExceptionInterface):
    pass
