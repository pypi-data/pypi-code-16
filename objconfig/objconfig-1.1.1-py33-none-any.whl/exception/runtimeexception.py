from objconfig.exception.exceptioninterface import ExceptionInterface


class RuntimeException(RuntimeError, ExceptionInterface):
    pass
