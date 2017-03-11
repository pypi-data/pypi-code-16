import logging
import threading
import time
import queue
import uuid
import warnings

from proton.handlers import MessagingHandler
from proton.reactor import ApplicationEvent
from proton.reactor import Container
from proton.reactor import EventInjector
import ioc

from ea.event.contrib.apollo_proton.adapter import ProtonAdapter
import ea.event.transport


class EventSender(MessagingHandler):
    logger = logging.getLogger("ea.events")

    def __init__(self, parent, url, queue, channel, injector):
        super(EventSender, self).__init__()
        self.queue = queue
        self.url = url
        self.channel = channel
        self.injector = injector
        self.connection = None
        self.deliveries = {}
        self.parent = parent

    def on_start(self, event):
        """Invoked when the container is entering its main event loop. This
        method should connect the sender to all channels it wishes to publish
        to.
        """
        self.container = event.container
        self.container.selectable(self.injector)
        self.sender = event.container.create_sender(self.url, target=self.channel)

    def on_heartbeat(self, event):
        if not self.parent.is_alive():
            self.injector.trigger(ApplicationEvent('teardown'))
            return

        time.sleep(0.1)
        self.injector.trigger(ApplicationEvent('heartbeat'))

    def on_connection_opened(self, event):
        self.connection = event.connection

    def on_teardown(self, event):
        self.logger.info("Stopping event transport")
        self.injector.close()
        if self.sender is not None:
            self.sender.close()
        if self.connection is not None:
            self.connection.close()
        if self.container is not None:
            self.container.stop()

    def on_sendable(self, event):
        """Invoked when the producer has enough credit to send at least
        one message.
        """
        self.flush()

    def on_accepted(self, event):
        delivery = self.deliveries.pop(event.delivery.tag, None)
        if delivery is None:
            # TODO: May happen after expired deliveries have been
            # removed, but that is not implemented now.
            return

        delivery.settle()

    def on_flush(self, event):
        self.flush()

    def flush(self):
        sender = self.sender
        if not sender.credit:
            self.logger.debug("Sender %s has no credit, flush aborted", self.channel)
            return

        self.logger.debug("Flushing enqueued messages")
        while sender.credit:
            try:
                msg, delivery = self.queue.get(False)
                self.deliveries[delivery.tag] = delivery

                self.logger.debug("Sending message %s", msg.id)
                sender.send(msg, tag=delivery.tag)

                self.queue.task_done()
            except queue.Empty:
                break


class ProtonTransport(ea.event.transport.BaseTransport):
    logger = logging.getLogger("ea.events")

    def __init__(self, dsn, channel, adapter):
        super(ProtonTransport, self).__init__(adapter)
        self.dsn = dsn
        self.channel = channel
        self.queue = queue.Queue()
        self.injector = EventInjector()
        self.sender = EventSender(threading.current_thread(),
            self.dsn, self.queue, self.channel, self.injector)
        self.thread = threading.Thread(target=Container(self.sender).run, daemon=True)
        self.thread.start()
        self.injector.trigger(ApplicationEvent('heartbeat'))

    def flush(self):
        self.injector.trigger(ApplicationEvent('flush'))

    def send(self, message):
        self.logger.debug("Enqueued message %s", message.id)
        delivery = ProtonDelivery()
        self.queue.put((message, delivery))
        return delivery

    def stop(self):
        self.injector.trigger(ApplicationEvent('teardown'))
        self.thread.join()


class ProtonDelivery(ea.event.transport.BaseDelivery):

    def __init__(self):
        self.tag = str(uuid.uuid4())
        self.event = threading.Event()
        self.ttl = 60000

    def settle(self, *args, **kwargs):
        self.event.set()

    def wait(self, *args, **kwargs):
        return self.event.wait(*args, **kwargs)

    def is_settled(self):
        return self.event.is_set()
