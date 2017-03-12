import logging
import threading
import random

from ea.messaging.handlers import HeartbeatMixin
from proton import Message
from proton.handlers import MessagingHandler
from proton.reactor import Container

from origin.utils import group_channels
from origin.publisher.null import NullEventPublisher


class AMQPEventPublisher(NullEventPublisher):
    """A :class:`BaseEventPublisher` implementation that transmits
    events over the AMQP 1.0 protocol using the :mod:`proton`
    library.
    """

    def __init__(self, channels, logger=None):
        self.channels = channels
        self.parent = threading.current_thread()
        self.logger = logger or logging.getLogger('amqp')
        self.child = None
        self.handler = None
        self.container = None

    def publish(self, *args, **kwargs):
        pass

    def start(self):
        """Open a link to the message broker and start waiting
        for outbound event messages.
        """
        self.handler = self.handler_factory(self.parent)
        self.container = Container(self.handler)
        self.child = threading.Thread(target=self.container.run)
        self.child.start()

    def stop(self, timeout=None):
        """Close all connections to the message broker and kill the
        child thread.
        """
        if not self.child or not self.child.is_alive():
            return
        self.handler.exit(timeout=timeout)
        self.child.join()

    def handler_factory(self, thread):
        """Instantiate a new :class:`AMQPConnectionHandler`."""
        return AMQPConnectionHandler(thread, self.channels, self.logger)


class AMQPConnectionHandler(MessagingHandler, HeartbeatMixin):
    # On teardown, all pending outbound messages must be sent
    # within this interval, in milliseconds.
    grace_period = 5000
    interval = 1

    @property
    def sendables(self):
        """Return all senders that have credit."""
        return [x for x in self.senders if x.credit]

    def __init__(self, thread, channels, logger=None):
        MessagingHandler.__init__(self)
        HeartbeatMixin.__init__(self)
        self.channels = group_channels(channels)
        self.logger = logger or logging.getLogger('amqp')
        self.parent = thread
        self.must_exit = False
        self.connections = []
        self.senders = []
        self.outbox = []

    def exit(self, timeout=None):
        """Inform the event loop that it has to exit."""
        self.must_exit = True

    def on_start(self, event):
        HeartbeatMixin.on_start(self, event)
        for dsn, channels, opts in self.channels:
            self.logger.info("Connecting to message broker at %s" % dsn)
            c = event.container.connect(dsn)
            for channel in channels:
                self.logger.debug("Establishing link %s" % channel)
                s = event.container.create_sender(c, target=channel)
                self.senders.append(s)
            self.connections.append(c)

        self.container = event.container

    def on_sendable(self, event):
        pass

    def on_heartbeat(self, event):
        # Bail out if the parent thread has died. Try to deliver all pending
        # messages and exit the main event loop.
        if not self.parent.is_alive() or self.must_exit:
            self.logger.debug("Closing all links and connections")
            for s in self.senders: s.close()
            for c in self.connections: c.close()
            self.injector.close()
            self.container.stop()
