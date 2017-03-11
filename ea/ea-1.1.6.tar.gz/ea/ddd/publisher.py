from ea.ddd.event import DomainEvent


class DomainEventPublisher:
    """Publishes domain event within the context of an
    aggregate.
    """
    @property
    def events(self):
        return tuple(self._events)

    def __init__(self, agg):
        self._agg = agg
        self._events = []

    def count(self):
        """Return the number of pending events."""
        return len(self._events)

    def publish(self, typename, value):
        """Publish a domain event with the given value."""
        self._events.append(DomainEvent(typename, value))
