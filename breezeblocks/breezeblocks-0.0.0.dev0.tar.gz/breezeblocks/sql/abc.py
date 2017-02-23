"""Defines abstract base classes present in this package."""
from abc import ABCMeta

class Queryable(metaclass=ABCMeta):
    """Signifies a subclass can be used by a :class:`query.Query`."""
    pass
