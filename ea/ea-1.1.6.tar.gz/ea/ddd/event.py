

class DomainEvent:
    """Reports a state change within a domain model."""

    def __init__(self, typename, value=None):
        self.typename = typename
        self.value = value
