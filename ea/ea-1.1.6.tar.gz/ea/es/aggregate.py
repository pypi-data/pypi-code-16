from ea.es.publisher import EventPublisher
from ea.es.base import DomainObject


class Aggregate(DomainObject):
    """The base class for all event-sourced aggegrates.

    This class provides a conveniant building block for designing
    event-sourced aggegrates. It collects all events published
    within the aggregate and makes them available to the repositories
    for persistence.

    Example:

        import ea.lib.timezone


        class OrderAggregate(ea.es.Aggregate):

            @ddd.es.publisher
            def place(self):
                return self.events.publish('OrderPlaced',
                    placed=ea.lib.timezone.now())


    The framework will automatically look for a method called
    ``on_`` followed by the event name lowercased; e.g.
    ``on_orderplaced()``.
    """
    __abstract__ = True

    @property
    def events(self):
        return self.__publisher__

    def __new__(cls, *args, **kwargs):
        instance = super(Aggregate, cls).__new__(cls)
        instance.id = None
        instance.__publisher__ = EventPublisher(instance)
        return instance

