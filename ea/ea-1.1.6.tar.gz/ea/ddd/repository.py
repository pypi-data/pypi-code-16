from ea.exc import ImplementationError
from ea.ddd.exc import ObjectDoesNotExist


class Repository:
    """Basic implementation of a repository. A repository
    is responsible for persisting and reconstructing domain
    objects.

    This basic implementation exposes a :meth:`persist()`
    method with handlers the events in a dirty aggregate.
    For each event, it will try to invoke an ``on_<typename>`
    handler function with the aggregate and the event as
    its positional arguments. It is the responsibility
    of the aggregate to publish the events in the right
    order.
    """
    DoesNotExist = ObjectDoesNotExist

    def notify(self, typename, agg, value):
        """Invoke the handler for domain event `typename`."""
        try:
            fn = getattr(self, "on_%s" % typename)
        except AttributeError:
            raise ImplementationError(
                "%s must define a handler for domain event '%s'"\
                % (type(self).__name__, typename))

        fn(agg, value)

    def persist(self, agg):
        """Run all events handlers for the given aggregate."""
        with self:
            for event in agg.publisher.events:
                self.notify(event.typename, agg, event.value)

    def begin(self):
        """Override this method for your specific use case."""
        return self

    def commit(self):
        """Override this method for your specific use case."""

    def rollback(self):
        """Override this method for your specific use case."""

    def enter(self, *args, **kwargs):
        """Override this method for your specific use case."""

    def exit(self, cls, exc, tb):
        """Override this method for your specific use case."""
    
    def __enter__(self):
        return self.begin()

    def __exit__(self, cls, exc, tb):
        if cls:
            self.rollback()
        else:
            self.commit()

        self.exit(cls, exc, tb)
