import logging
import threading
import uuid

import ioc

from ea.lib import timezone
from ea.event.factory import NullFactory
from ea.event.transport import NullTransport


class EventPublisher(object):
    """Publishes events to the event-driven architecture."""
    logger = logging.getLogger('ea.events')
    observer = ioc.class_property('EventPublisher.observer')
    transport = ioc.class_property('EventPublisher.transport')
    factory = ioc.class_property('EventPublisher.factory')

    def __init__(self):
        self._local = threading.local()

    def create(self, event, **kwargs):
        """Create a new event.

        Args:
            event: a :class:`~ea.event.Event` instance.
            occurred: an unsigned long integer representing the number
                of milliseconds since the UNIX epoch at which the
                event occurred.
            cid: a correlation identifier. If `cid` is ``None``, one
                will be generated.
        """
        kwargs.setdefault('observer', self.observer)
        self.logger.debug("Event: %s", event.description)
        return self.factory.create(event, **kwargs)

    def publish(self, events):
        """Publishes an event to the event-driven architecture."""
        return self.transport.send_events(events)

    def transaction(self, **kwargs):
        """Begins a new transaction and returns a :class:`Transaction`
        object.
        """
        if not hasattr(self._local, 'tx'):
            self._local.tx = TransactionContext(self, None, **kwargs)
            return self._local.tx

        return TransactionContext(self, self._local.tx, **kwargs)


class MockEventPublisher(EventPublisher):
    """An :class:`EventPublisher` implementation that does not
    publish any events.
    """

    def publish(self, events, *args, **kwargs):
        return


class TransactionContext(object):
    Aborted = type('Aborted', (Exception,), {})
    logger = logging.getLogger('ea.events')

    def __init__(self, publisher, tx, **kwargs):
        print("Subtransaction: ", tx)
        self.tx = tx
        self.publisher = publisher
        self.events = []
        self.txid = str(uuid.uuid4())
        self.aborted = False

    def transaction(self):
        """Begin a subtransaction."""
        return TransactionContext(self.publisher, self, **kwargs)

    def is_subtransaction(self):
        return self.tx is not None

    def add(self, event, *args, **kwargs):
        if self.aborted:
            raise self.Aborted
        self.events.append(event)

    def extend(self, events):
        if self.aborted:
            raise self.Aborted
        self.events.extend(events)

    def publish(self, *args, **kwargs):
        self.add(self.publisher.create(*args, **kwargs))
        return self.events[-1]

    def abort(self):
        """Aborts the transaction. Pending events will not be
        published.
        """
        self.aborted = True

    def commit(self):
        self.logger.debug('Commit %s', self.txid)
        self.publisher.publish(self.events)
        self.logger.debug('Finished commit %s', self.txid)

    def __enter__(self):
        return self

    def __contains__(self, obj):
        return obj in self.events

    def __exit__(self, cls, exc, tb):
        if self.aborted:
            return

        if self.is_subtransaction() and cls is None:
            # On success, the events published in the
            # subtransaction are added to the parent
            # transaction.
            self.tx.extend(self.events)
            print(self.tx.events)
            return

        if cls is None:
            self.commit()

    def __repr__(self):
        tpl = "Transaction: {id}"
        parent_id = None
        if self.is_subtransaction():
            tpl += ", parent: {parent_id}"
            parent_id = self.tx.txid
        return "<%s>" % tpl.format(id=self.txid, parent_id=parent_id)
