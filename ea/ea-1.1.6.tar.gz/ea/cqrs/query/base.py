

class Query:
    """Represent a predetermined query to a system."""

    def prepare(self, **kwargs):
        """Prepares  the query to issue it to the datastore."""
        raise NotImplementedError("Subclasses must override this method.")
