import collections
import logging

from ea.messaging.exc import InvalidState
from ea.messaging.exc import Fatal
from ea.messaging.receiver import ReceiverManager
from ea.messaging.sender import SenderManager
from ea.messaging.utils import get_remote_address
from ea.messaging.observer import AMQPObserver
from ea.messaging.error import ErrorHandler


class LinkManager(AMQPObserver):
    logger = logging.getLogger('amqp')

    def __init__(self, connections, create_sender, create_receiver):
        self._send = create_sender
        self._recv = create_receiver
        self.sender = SenderManager(connections, self, create_sender)
        self.receiver = ReceiverManager(connections, self, create_receiver)
        self.closed = False
        self.registry = connections
        self.error_handler = ErrorHandler()
        self.hosts = collections.defaultdict(list)
        super(LinkManager, self).__init__(connections)

    def has_links(self):
        """Return a bool indicating if there are links
        established.
        """
        return bool(self.sender.links or self.receiver.links)

    def create_sender(self, hostname, connection, address, *args, **kwargs):
        """Establish a new link on `connection` to a remote
        source and return a :class:`Sender` instance.
        """
        assert connection.state & connection.LOCAL_ACTIVE,\
            "Connection.state must be at least LOCAL_ACTIVE"
        if self.closed:
            raise InvalidState("Cannot create links in closed state")
        sender = self.sender.create(self.registry, connection, address, *args, **kwargs)
        return sender

    def create_receiver(self, hostname, connection, address, *args, **kwargs):
        """Establish a new link on `connection` to a remote
        source and return a :class:`Receiver` instance.
        """
        assert connection.state & connection.LOCAL_ACTIVE,\
            "Connection.state must be at least LOCAL_ACTIVE"
        if self.closed:
            raise InvalidState("Cannot create links in closed state")
        receiver = self.receiver.create(self.registry, connection, address, *args, **kwargs)
        return receiver

    def notify(self, typename, event):
        fn = getattr(self, typename, lambda event: None)
        fn(event)

    def close(self):
        """Closes all links established on this :class:`LinkManager`."""
        self.sender.close()
        self.receiver.close()

    def on_heartbeat(self, event):
        self.sender.on_heartbeat(event)

    def on_link_opened(self, event):
        link = event.link
        direction = 'ingress' if link.is_receiver else 'egress'
        self.logger.debug("Established %s link with address %s", direction,
            get_remote_address(link))

    def on_sendable(self, event):
        link = event.link
        addr = get_remote_address(link)
        self.logger.debug("Link %s is ready to send", addr)
        self.sender.on_sendable(event)

    def on_settled(self, event):
        if event.link.is_sender:
            self.sender.on_settled(event)
        if event.link.is_receiver:
            self.receiver.on_settled(event)

    def on_message(self, event):
        """Dispatch the message to its receiving :class:`ea.messaging.Endpoint`
        instance.
        """
        self.logger.debug("Incoming message (id: %s)", event.message.id)
        self.receiver.on_message(event)

    def on_link_closed(self, event):
        link = event.link
        if link.is_sender:
            self.sender.on_link_closed(event)

        if link.is_receiver:
            self.receiver.on_link_closed(event)

    def on_link_error(self, event):
        """This method is invoked when an error on a link occurs."""
        link = event.link
        self.error_handler.handle(self, link.remote_condition, event)
        if link.is_receiver:
            self.error_handler.handle(self.receiver,
                link.remote_condition, event)

        if link.is_sender:
            self.error_handler.handle(self.sender,
                link.remote_condition, event)

    def on_transport_error(self, event):
        self.error_handler.handle(self, event.transport.condition, event)

        # This does not handle the situation where the program connects
        # to multiple hosts; it just recreates all links and connection,
        # even the ones that are healthy.

    def on_amqp_not_found(self, event, condition):
        # With Apache Apollo, this error is raised when the user is not
        # allowed to create a link.
        if condition.description and condition.description.startswith("Not authorized"):
            raise Fatal(condition.description)

