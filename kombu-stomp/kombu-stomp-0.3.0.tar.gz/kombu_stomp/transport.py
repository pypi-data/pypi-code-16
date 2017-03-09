from __future__ import absolute_import

import contextlib
import os
import socket

from kombu import utils
from kombu.transport import virtual
from stomp import exception as exc
from stomp.exception import ConnectFailedException

from kombu_stomp import jms
from kombu_stomp.stomp import StompTimeoutException
from . import stomp


class Message(virtual.Message):
    """Kombu virtual transport message class for kombu-stomp.

    This class extends :py:class:`kombu.transport.virtual.Message`, so it
    keeps STOMP message ID for later use.
    """

    def __init__(self, raw_message, channel):
        super(Message, self).__init__(raw_message, channel)
        self.transformation = self.headers.get('transformation')
        self.msg_id = self.headers.get('message-id')

    def decode(self):
        if not self._decoded_cache:
            self._decoded_cache = jms.convert_jms_to_python(self._decode(), self.transformation)
        return self._decoded_cache


class QoS(virtual.QoS):
    """Kombu quality of service class for ``kombu-stomp``."""

    def __init__(self, *args, **kwargs):
        self.ids = {}
        self.prefetch_size = 0
        super(QoS, self).__init__(*args, **kwargs)

    def append(self, message, delivery_tag):
        self.ids[delivery_tag] = message.msg_id
        super(QoS, self).append(message, delivery_tag)

    def ack(self, delivery_tag):
        self._stomp_ack(delivery_tag)
        return super(QoS, self).ack(delivery_tag)

    def _stomp_ack(self, delivery_tag):
        msg_id = self.ids.pop(delivery_tag, None)
        if msg_id:
            with self.channel.conn_or_acquire() as conn:
                conn.ack(msg_id)


class StompChannelException(Exception):
    pass


class Channel(virtual.Channel):
    """``kombu-stomp`` channel class."""
    QoS = QoS
    Message = Message

    def __init__(self, *args, **kwargs):
        super(Channel, self).__init__(*args, **kwargs)
        self._stomp_conn = None
        self._subscriptions = set()

    def _poll(self, cycle, callback, timeout=None):

        with self.conn_or_acquire() as conn:
            # FIXME(rafaduran): inappropriate intimacy code smell
            next_message, queue = next(conn.message_listener.iterator())
            callback(next_message, queue)

    def _put(self, queue, message, **kwargs):
        with self.conn_or_acquire() as conn:
            body = message.pop('body')
            conn.send(self.queue_destination(queue), body, **message)

    def basic_consume(self, queue, *args, **kwargs):

        with self.conn_or_acquire() as conn:
            self.subscribe(conn, queue)

        return super(Channel, self).basic_consume(queue, *args, **kwargs)

    def subscribe(self, conn, queue):
        if queue in self._subscriptions:
            return

        self._subscriptions.add(queue)
        return conn.subscribe(self.queue_destination(queue),
                              headers=self.exchange_headers(queue),
                              transformation='jms-json',
                              ack='client-individual')

    def queue_unbind(self,
                     queue,
                     exchange=None,
                     routing_key='',
                     arguments=None,
                     **kwargs):
        super(Channel, self).queue_unbind(queue,
                                          exchange,
                                          routing_key,
                                          arguments,
                                          **kwargs)
        with self.conn_or_acquire() as conn:
            conn.unsubscribe(self.queue_destination(queue))
            self._subscriptions.discard(queue)

    def queue_destination(self, queue):
        exchange = self.get_exchange(queue)
        stomp_prefix = 'topic' if exchange['type'] == 'topic' else 'queue'
        return '/{stomp_prefix}/{prefix}{name}'.format(stomp_prefix=stomp_prefix,
                                                       prefix=self.prefix,
                                                       name=queue)

    @contextlib.contextmanager
    def conn_or_acquire(self, disconnect=False):
        """Use current connection or create a new one."""
        if not self.stomp_conn.is_connected():
            self.connect()

        yield self.stomp_conn

        if disconnect:
            self.stomp_conn.disconnect()
            self.iterator = None

    def connect(self):
        try:
            self.stomp_conn.start()
            self.stomp_conn.connect(wait=True, timeout=10, **self._get_conn_params())
            self.reset_subscriptions()
        except (ConnectFailedException, StompTimeoutException):
            self.stomp_conn.stop()
            raise StompChannelException()

    @property
    def stomp_conn(self):
        """Property over the stomp.py connection object.

        It will create the connection object at first use.
        """
        if not self._stomp_conn:
            self._stomp_conn = stomp.Connection(self.prefix,
                                                **self._get_params())

        return self._stomp_conn

    @property
    def transport_options(self):
        return self.connection.client.transport_options

    @utils.cached_property
    def prefix(self):
        return self.transport_options.get('queue_name_prefix', '')

    def _get_params(self):
        return {
            'host_and_ports': [
                (self.connection.client.hostname or '127.0.0.1',
                 self.connection.client.port or 61613)
            ],
            'reconnect_attempts_max': 1,
            'wait_on_receipt': True,
            'auto_content_length': False
        }

    def _get_conn_params(self):
        return {
            'username': self.connection.client.userid,
            'passcode': self.connection.client.password,
        }

    def close(self):
        super(Channel, self).close()
        if self._stomp_conn:
            try:
                # TODO (rafaduran): do we need unsubscribe all queues first?
                self._stomp_conn.disconnect()
            except exc.NotConnectedException:
                pass

    def reset_subscriptions(self):
        subscriptions = self._subscriptions.copy()
        self._subscriptions.clear()
        for queue in subscriptions:
            self.subscribe(self.stomp_conn, queue)

    def exchange_headers(self, queue):
        exchange = self.get_exchange(queue)
        headers = {}
        if exchange['type'] == 'topic' and exchange['durable']:
            headers['activemq.subscriptionName'] = os.getenv('KOMBU_SUBSCRIPTION_NAME', socket.gethostname())
        if self.qos.prefetch_size > 0:
            headers['activemq.prefetchSize'] = self.qos.prefetch_size
        return headers

    def get_exchange(self, queue):
        (binding,) = self.connection.state.queue_bindings(queue)
        return self.connection.state.exchanges[binding.exchange]

    def basic_qos(self, prefetch_size=0, prefetch_count=0,
                  apply_global=False):
        self.qos.prefetch_size = prefetch_size
        self.qos.prefetch_count = prefetch_count


class Transport(virtual.Transport):
    """Transport class for ``kombu-stomp``."""
    Channel = Channel

    recoverable_connection_errors = (StompChannelException,)

    def establish_connection(self):
        channel = self.create_channel(self)
        channel.connect()
        self._avail_channels.append(channel)
        return self  # for drain events

    def drain_events(self, connection, timeout=None):
        try:
            super(Transport, self).drain_events(connection, timeout)
        except self.recoverable_connection_errors:
            self.client.ensure_connection()
