

class ResourceLocked(Exception):
    """Raised when concurrent access to a resource is
    requested but it doesn't support concurrent write
    access so it is locked.
    """


class ImplementationError(Exception):
    """Raised when the framework is incorrectly implemented."""


class Timeout(Exception):
    """Generic timeout exception."""
