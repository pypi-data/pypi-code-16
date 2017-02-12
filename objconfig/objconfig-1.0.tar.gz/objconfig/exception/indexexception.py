from objconfig.exception.exceptioninterface import ExceptionInterface


class IndexException(IndexError, ExceptionInterface):
    pass
