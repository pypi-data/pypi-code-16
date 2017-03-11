import logging

from proton import Message

from ea.messaging.utils import get_remote_address
from ea.messaging.exc import InvalidState
from ea.messaging.delivery import Delivery
from ea.messaging.factory import LinkFactory
from ea.messaging.observer import AMQPObserver
from ea.messaging.endpoint import Endpoint


class Sender(AMQPObserver, Endpoint):
    """Manages a sender link and the handlers for incoming
    messages.
    """
    logger = logging.getLogger('amqp')
    message_class = Message
    remote = 'target'

    def __init__(self, registry, manager, address):
        self.registry = registry
        self.manager = manager
        self.link = None
        self.address = address
        self.outbox = []
        self.deliveries = {}
        self.closed = False

    def send(self, body, *args, **kwargs):
        """Add a message to the outbox and return a :class:`Delivery`
        instance tracking the message.
        """
        autoflush = kwargs.pop('autoflush', True) # TODO: this must be False

        if self.closed:
            raise InvalidState("Cannot send messages on closed Sender")
        msg = Delivery(self.message_class(body=body, *args, **kwargs))
        self.outbox.append(msg)

        self.logger.debug("Enqueing message (id: %s, tag: %s)", msg.id, msg.tag)
        if autoflush:
            self.flush()
        return msg

    def flush(self):
        if not self.outbox or not self.link.credit:
            return

        self.logger.debug("Flushing messages to %s",
            self.link.remote_target.address)
        n = 0
        while self.link.credit and self.outbox:
            message = self.outbox.pop(0)
            message.send(self.link.send)
            self.deliveries[message.tag] = message
            n += 1

    def settle(self, tag):
        """Indicate that the delivery identified by `tag` is settled
        with the other endpoint.
        """
        delivery = self.deliveries.pop(tag, None)
        if delivery is not None:
            # The delivery may be None if there where messages in the
            # broker that where not sent by us during this process
            # lifecycle.
            delivery.settle()

    def close(self):
        """Flag the :class:`Sender` as closed and start the teardown
        process.
        """
        self.logger.debug("Tearing down sending link %s",
            self.link.remote_target.address)
        self.closed = True

        # If there are no messages pending in the outbox, we can
        # close the link immediately.
        if not self.outbox:
            self.link.close()

    def on_settled(self, event):
        # RECEIVED = RECEIVED
        # ACCEPTED = ACCEPTED
        # REJECTED = REJECTED
        # RELEASED = RELEASED
        # MODIFIED = MODIFIED
        delivery = event.delivery
        state = delivery.remote_state
        keys = (
            (delivery.ACCEPTED, 'ACCEPTED'),
            (delivery.REJECTED, 'REJECTED')
        )
        for k, v in keys:
            if bool(state & k):
                self.logger.debug("Delivery (tag: %s) is ACCEPTED" % delivery.tag)
                break

        self.settle(event.delivery.tag)

        # If all messages in the outbox are settled and we
        # are in closed state, we can now safely tear down
        # the link.
        if not self.outbox and self.closed:
            # TODO: This assumes that all messages always get
            # settled -- to prevent hangups, a timeout is to
            # be implemented for pending deliveries. Drop or
            # save to disk.
            self.link.close()

    def on_link_closed(self, event):
        pass

    def __repr__(self):
        return "<Sender: %s>" % self.address


class SenderManager(LinkFactory):
    logger = logging.getLogger('amqp')
    link_class = Sender
    endpoint_type = 'target'

    def __init__(self, registry, manager, create):
        super(SenderManager, self).__init__(registry, create)
        self.manager = manager
        self.links = {}
        self.closed = False
        self.must_close = False
        self.addresses = set()

    def close(self):
        """Closes all links established on this :class:`SenderManager`."""
        self.must_close = True
        for s in self.links.values(): s.close()

    def on_heartbeat(self, event):
        # TODO: This is a hack for senders that werent being
        # removed.
        pass

    def on_sendable(self, event):
        self.links[self.get_address_from_link(event.link)].flush()

    def on_settled(self, event):
        print(event)
        self.links[self.get_address_from_link(event.link)].on_settled(event)


