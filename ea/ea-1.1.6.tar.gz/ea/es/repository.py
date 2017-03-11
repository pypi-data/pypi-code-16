import contextlib


class Repository:
    """Repository base class for event-sourced
    aggregates.
    """

    @contextlib.contextmanager
    def transaction(self, publisher):
        self.begin()
        try:
            yield list(publisher.consume())
        except Exception:
            self.rollback()
            raise
        self.commit()
        self.flush()

    def begin(self):
        """Subclasses may override this method to begin a transaction
        in the persistent storage backend.
        """
        pass

    def commit(self):
        """Subclasses may override this method to commit a transaction
        in the persistent storage backend.
        """
        pass

    def rollback(self):
        """Subclasses may override this method to rollback a transaction
        in the persistent storage backend.
        """
        pass

    def flush(self):
        """If the persistent storage framework supports and/or requires
        it, this method may be overriden to persist pending changed
        to the storage medium (e.g. write to disk). Implementors must
        ensure that invoking :meth:`flush()` guarantees this promise
        (notwithstanding lying filesystems et. al.).
        """
        pass

    def unitofwork(self):
        """Demarcates the boundaries of a business
        transaction."""
        raise NotImplementedError("Subclasses must override this method.")

    def persist(self, obj):
        """Persist an :class:`~ea.es.base.Aggregate` implementation."""
        with self.transaction(obj.events) as events:
            uow = self.unitofwork()
            for event in events:
                uow.add(event)
