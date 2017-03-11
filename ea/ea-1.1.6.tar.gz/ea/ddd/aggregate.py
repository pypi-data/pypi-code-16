from ea.exc import ImplementationError

from ea.ddd.publisher import DomainEventPublisher


class Aggregate:
    """A basic aggregate implementation that publishes domain
    events.
    """

    @property
    def publisher(self):
        return self.__publisher__

    def __new__(cls, *args, **kwargs):
        instance = super(Aggregate, cls).__new__(cls)
        instance.__publisher__ = DomainEventPublisher(instance)
        return instance
