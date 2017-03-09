from __future__ import absolute_import

import ast
import threading

import stomp
from six.moves import queue
from stomp import listener


class MessageListener(listener.ConnectionListener):
    """stomp.py listener used by ``kombu-stomp``"""

    def __init__(self, connected_event=threading.Event(), prefix='', q=None):
        if not q:
            q = queue.Queue()

        self.q = q
        self.prefix = prefix
        self.connected_event = connected_event

    def on_connected(self, headers, body):
        self.connected_event.set()

    def on_disconnected(self):
        self.connected_event.clear()

    def on_message(self, headers, body):
        """Received message hook.

        :arg headers: message headers.
        :arg body: message body.
        """
        self.q.put(self.to_kombu_message(headers, body))

    def to_kombu_message(self, headers, body):
        """Get STOMP headers and body message and return a Kombu message dict.

        :arg headers: message headers.
        :arg body: message body.
        :return dict: A dictionary that Kombu can use for creating a new
            message object.
        """

        message = {}
        # properties is a dictionary and we need evaluate it
        if 'properties' in headers:
            message['properties'] = ast.literal_eval(headers['properties'])
        else:
            message['properties'] = {'delivery_tag': ''}

        if 'content-type' not in headers and headers.get('transformation') == 'jms-map-json':
            message['content-type'] = 'application/json'
            message['content-encoding'] = 'binary'
        else:
            message['content-type'] = headers.get('content-type')
            message['content-encoding'] = headers.get('content-encoding')

        message['body'] = body
        message['headers'] = dict(
            [(header, value) for header, value in headers.items()
             if header not in message]
        )
        return (
            message,
            self.queue_from_destination(headers['destination']),
        )

    def iterator(self):
        """Return a Python generator consuming received messages.

        If we try to consume a message and there is no messages remaining, then
        an exception will be raised.

        :yields dict: A dictionary representing the message in a Kombu
            compatible format.
        :raises: :py:exc:`Queue.Empty` When there is no message to be consumed.
        """
        while True:
            yield self.q.get_nowait()

    def queue_from_destination(self, destination):
        """Get the queue name from a destination header value."""
        return destination.split('/{0}'.format(self.prefix)).pop()


class StompTimeoutException(Exception):
    pass


class Connection(stomp.Connection10):
    """Connection object used by ``kombu-stomp``"""

    def __init__(self, prefix='', *args, **kwargs):
        super(Connection, self).__init__(*args, **kwargs)
        self.connected_event = threading.Event()
        self.message_listener = MessageListener(self.connected_event, prefix=prefix)
        self.set_listener('message_listener', self.message_listener)

    def connect(self, wait=False, timeout=None, **kwargs):
        super(Connection, self).connect(wait=False, **kwargs)
        if wait and not self.connected_event.wait(timeout):
            raise StompTimeoutException()
