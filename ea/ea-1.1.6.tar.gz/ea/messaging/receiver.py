import logging

from ea.messaging.utils import get_remote_address
from ea.messaging.exc import InvalidState
from ea.messaging.factory import LinkFactory
from ea.messaging.observer import AMQPObserver
from ea.messaging.endpoint import Endpoint


class Receiver(AMQPObserver, Endpoint):
    logger = logging.getLogger('amqp')
    remote = 'source'

    def __init__(self, registry, manager, address, handlers):
        super(Receiver, self).__init__(registry)
        self.registry = registry
        self.manager = manager
        self.link = None
        self.handlers = handlers
        self.closed = False
        self.address = address

    def close(self):
        """Flag the :class:`Receiver` as closed and start the teardown
        process.
        """
        self.logger.debug("Tearing down receiving link %s",
            self.link.remote_source.address)
        self.closed = True
        self.link.close()

    def on_message(self, event):
        event.delivery.update(event.delivery.ACCEPTED)
        for handler in self.handlers:
            if not handler.wants(event.message):
                continue
            handler.handle(event.message)

    def on_link_closed(self, event):
        self.logger.debug("Receiving link %s is now closed",
            event.link.remote_source.address)

    def __repr__(self):
        return "<Receiver: %s>" % self.address


class ReceiverManager(LinkFactory):
    logger = logging.getLogger('amqp')
    link_class = Receiver
    endpoint_type = 'source'

    def __init__(self, registry, manager, create):
        super(ReceiverManager, self).__init__(registry, create)
        self.manager = manager
        self.links = {}
        self.closed = False

    def close(self):
        """Closes all links established on this :class:`SenderManager`."""
        for s in self.links.values(): s.close()

    def on_message(self, event):
        """Dispatch the message to its receiving :class:`ea.messaging.Endpoint`
        instance.
        """
        self.links[self.get_address_from_link(event.link)].on_message(event)

    def on_settled(self, event):
        pass
