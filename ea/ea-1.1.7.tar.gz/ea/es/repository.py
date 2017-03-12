import contextlib

from ea.es.storage import MemoryEventStore


class Repository:
    """Repository base class for event-sourced
    aggregates.
    """
    store = MemoryEventStore()

    def persist(self, obj):
        """Persist an :class:`~ea.es.base.Aggregate` implementation."""
        with self.store.transaction():
            if obj.id is None:
                self.store.create_aggregate(obj)
            for event in obj.events.consume():
                self.store.add(event)
