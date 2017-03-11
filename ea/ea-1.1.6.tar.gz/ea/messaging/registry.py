import logging

from proton.reactor import ApplicationEvent
import dsnparse

from ea.messaging.link import LinkManager
from ea.messaging.utils import get_remote_address
import ea.patterns.observer


class Registry(ea.patterns.observer.Subject):
    logger = logging.getLogger('amqp')

    def __init__(self, connect, create_sender, create_receiver, injector):
        super(Registry, self).__init__()
        self._connection_factory = connect
        self._sender_factory = create_sender
        self._receiver_factory = create_receiver
        self._reg = {}
        self._injector = injector
        self.links = LinkManager(self, create_sender, create_receiver)
        self.closed = False

        # This is a set of hostnames to which we have established a connection.
        self.established = set()

        # Hosts to which we are reconnecting.
        self.reconnecting = set()

    def can_create_link(self, url):
        """Return a boolean indicating if a link may be created on the
        specified connection.
        """
        c = self.get_connection_by_url(url)
        return bool(c.state & c.REMOTE_ACTIVE)

    def get_connection_by_url(self, url):
        hostname = dsnparse.parse(url).hostname
        return hostname, self._reg[hostname]

    def on_heartbeat(self, event):
        self.links.on_heartbeat(event)

        # TODO: This is a hack for senders that werent being
        # removed.

    def create_sender(self, url, address, *args, **kwargs):
        hostname, c = self.get_connection_by_url(url)
        return self.links.create_sender(hostname, c,
            address, *args, **kwargs)

    def create_receiver(self, url, address, *args, **kwargs):
        hostname, c = self.get_connection_by_url(url)
        return self.links.create_receiver(hostname, c,
            address, *args, **kwargs)

    def connect(self, url, *args, **kwargs):
        host = dsnparse.parse(url).hostname
        if host not in self._reg:
            self.logger.info("Registering connection to %s", url)
            c =  self._connection_factory(url, *args, **kwargs)
            self._reg[host] = c
            self._reg[c] = url
        return self._reg[host]

    def close(self):
        """Tears down the complete registry."""
        self.closed = True
        self.links.close()

    def on_connection_opened(self, event):
        """This is invoked when a connection is opened. It must handle the
        following situations:

        1. A new connection was opened (recently added through the connect()
            method).
        2. A connection is re-established.
        """
        if event.connection.hostname in self.reconnecting:
            self.on_reconnect(event)
        else:
            self.logger.debug("Connection to %s is now active"\
                % event.connection.hostname)
            self.established.add(event.connection.hostname)

        self.update('on_connection_opened', event)

    def on_connection_closed(self, event):
        url = self._reg.pop(event.connection, None)
        self.logger.debug("Connection %s is now closed", url)

    # These events are propagated to their appropriate receiver
    # or sender managers.
    def on_message(self, event):
        self.links.on_message(event)

    def on_sendable(self, event):
        self.links.on_sendable(event)

    def on_link_closed(self, event):
        self.links.on_link_closed(event)

        # If the registry is closed and there are no
        # remaining links, we can destroy all connections.
        if self.closed and not self.links.has_links():
            self.teardown()

    def teardown(self):
        for c in self._reg.values():
            if isinstance(c, str):
                continue
            url = self._reg[c]
            self.logger.debug("Closing connection %s", url)
            c.close()

        self._injector.trigger(ApplicationEvent('registry_closed'))

    def on_link_error(self, event):
        self.update

    def on_transport_error(self, event):
        # Mark all established connections as reconnecting;
        # we have to do this since Transport.connection will
        # be None, so we can not get the hostname.
        self.reconnecting = set(self.established)
        self.established = set()

