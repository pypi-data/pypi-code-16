class ValidationError(Exception):
    """
    Raised when HTML document is invalid.
    """


class DoesNotAcceptInputError(ValueError):
    """
    Exception raised on operations that tries to send input to invalid elements.
    """


class QueryError(Exception):
    """
    Base class for errors that happen during queries.
    """


class NotFoundError(QueryError):
    """
    Error for failed queries.
    """


class MultipleElementsFoundError(QueryError):
    """
    Multiple elements were found when we were expecting only one.
    """
