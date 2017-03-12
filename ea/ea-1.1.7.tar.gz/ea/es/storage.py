import uuid

import contextlib


class IEventStore:
    """The base class for all event store implementations."""

    def generate_aggregate_id(self, obj):
        """Generates a unique value to identify an aggregate."""
        return str(uuid.uuid4())

    def create_aggregate(self, obj):
        """Persist a new :class:`~ea.es.Aggregate` instance and return
        its identifier.
        """
        raise NotImplementedError("Subclasses must override this method.")

    @contextlib.contextmanager
    def transaction(self):
        self.begin()
        try:
            yield
        except Exception:
            self.rollback()
            raise
        self.commit()
        self.flush()

    def add(self, event):
        """Add a new event to the persistent storage backend."""
        raise NotImplementedError("Subclasses must override this method.")

    def begin(self):
        """Subclasses must override this method to begin a transaction
        in the persistent storage backend.
        """
        raise NotImplementedError("Subclasses must override this method.")

    def commit(self):
        """Subclasses must override this method to commit a transaction
        in the persistent storage backend.
        """
        raise NotImplementedError("Subclasses must override this method.")

    def rollback(self):
        """Subclasses must override this method to rollback a transaction
        in the persistent storage backend.
        """
        raise NotImplementedError("Subclasses must override this method.")

    def flush(self):
        """If the persistent storage framework supports and/or requires
        it, this method must be overriden to persist pending changed
        to the storage medium (e.g. write to disk). Implementors must
        ensure that invoking :meth:`flush()` guarantees this promise
        (notwithstanding lying filesystems et. al.).
        """
        raise NotImplementedError("Subclasses must override this method.")

    def unitofwork(self):
        """Demarcates the boundaries of a business
        transaction."""
        raise NotImplementedError("Subclasses must override this method.")


class MemoryEventStore(IEventStore):
    """An event store implementation that persists events in local
    memory.
    """

    def __init__(self):
        self.events = {}

    def create_aggregate(self, obj):
        obj.id = self.generate_aggregate_id(obj)
        self.events[obj.id] = []

    def add(self, event):
        self.events[event.aggregate_id].append(event)

    def begin(self):
        pass

    def commit(self):
        pass

    def rollback(self):
        pass

    def flush(self):
        pass

    def unitofwork(self):
        return set()
