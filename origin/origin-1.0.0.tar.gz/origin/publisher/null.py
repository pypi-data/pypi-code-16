from origin.publisher.base import BaseEventPublisher


class NullEventPublisher(BaseEventPublisher):
    """An implementation of the :class:`BaseEventPublisher`
    interface that does not transmit events. Use for
    mocking and prototyping purposes.
    """
    pass
