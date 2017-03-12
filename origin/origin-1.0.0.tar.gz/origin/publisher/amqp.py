from origin.publisher.null import NullEventPublisher


class AMQPEventPublisher(NullEventPublisher):
    """A :class:`BaseEventPublisher` implementation that transmits
    events over the AMQP 1.0 protocol using the :mod:`proton`
    library.
    """

    def __init__(self, channels):
        self.channels = channels

    def publish(self, *args, **kwargs):
        pass

    def start(self):
        pass

    def stop(self):
        pass
