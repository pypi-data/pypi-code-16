from ea.exc import ImplementationError


class ObjectDoesNotExist(LookupError):
    pass


class MultipleObjectsReturned(LookupError, ImplementationError):
    """Raised when multiple objects are returned on a query
    that expected a single object.
    """
