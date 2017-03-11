

class QueryParameters:
    """Configures the parameters to a named query."""

    def __init__(self):
        self.limit = None
        self.offset = 0

    def one(self):
        """Indicate that the :class:`QueryParameters` should yield
        one entity.
        """
        self.limit = 1
        return self
