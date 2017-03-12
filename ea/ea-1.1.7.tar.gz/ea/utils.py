


class MissingDependency:
    """Used to defer :class:`ImportError` on missing dependencies."""

    def __init__(self, exc):
        self.exc = exc

    def __getattr__(self, attname):
        raise self.exc
