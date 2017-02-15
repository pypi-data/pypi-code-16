import json

from time import time
from websocket import create_connection


class WebsocketPublisher(object):
    def __init__(self, ws_host):
        """Initialise a new object.

        Initialises a new WebsocketPublisher object and establishes a new
        WebSocket connection to the given host
        """
        self.ws = create_connection("ws://" + ws_host)

    def publish(self, channel, data):
        """Publish a new message on the given channel.

        Creates a new data message and publishes it on the given channel. The
        data itself can be any Python data structure which can be serialised
        to JSON (e.g. dictionaries or lists).
        """
        self.ws.send(json.dumps({
            'type': 'data',
            'channel': channel,
            'data': data
        }))

    def rtt(self):
        """Measure the round-trip time (RTT).

        This method measures the round-trip time from the current host to the
        WebSocket server. Note that in order to be accurate, this method should
        be called several times. Returns the RTT in milliseconds.
        """
        self.ws.send(json.dumps({
            'type': 'echo',
            'cmd': 'rtt',
            'timestamp': time()
        }))

        response = json.loads(self.ws.recv())
        return (time() - response['timestamp']) * 1000

    def close(self):
        """Close the connection.

        This method closes the underlying WebSocket connection. From this point
        on, no more messages can be published.
        """
        self.ws.close()


class WebsocketSubscriber(object):
    def __init__(self, ws_host):
        """Initialise a new object.

        Initialises a new WebsocketSubscriber object and establishes a new
        WebSocket connection to the given host
        """

        self.ws = create_connection("ws://" + ws_host)
        self.subscriptions = []

    def subscribe(self, channel):
        """Subscribe to a given channel.

        This method subscribes the object to the given channel, i.e. it will
        receive all messages which are published on the channel. Returns True
        if the subscription was successful or False otherwise.
        """
        if channel in self.subscriptions:
            raise AlreadySubscribedError(channel)

        self.ws.send(json.dumps({
            'type': 'subscribe',
            'channel': channel
        }))

        response = json.loads(self.ws.recv())

        if response['type'] == "control" and response['status'] == "OK":
            self.subscriptions.append(channel)
            return True
        else:
            return False

    def unsubscribe(self, channel):
        """Unsubscribe from the given channel.

        Unsubscribes the object from the given channel, i.e. this object will
        not receive anymore messages posted to the channel. This method returns
        True on success and False otherwise.
        If the object is not subscribed to the given channel, any exception is
        raised.
        """
        if channel not in self.subscriptions:
            raise NotSubscribedError(channel)

        self.ws.send(json.dumps({
            'type': 'unsubscribe',
            'channel': channel
        }))

        while True:
            response = json.loads(self.ws.recv())

            if response['type'] != "control":
                continue

            if response['status'] == "OK":
                if channel in self.subscriptions:
                    self.subscriptions.remove(channel)

                return True
            else:
                return False

    def rtt(self):
        """Measure the round-trip time (RTT).

        This method measures the round-trip time from the current host to the
        WebSocket server. Note that in order to be accurate, this method should
        be called several times. Returns the RTT in milliseconds.
        """
        self.ws.send(json.dumps({
            'type': 'echo',
            'cmd': 'rtt',
            'timestamp': time()
        }))

        response = json.loads(self.ws.recv())
        return (time() - response['timestamp']) * 1000

    def next_event(self, channel=None):
        """Retrieve the next event from the channel.

        This method blocks until the next event is published. If no channel
        name is passed in, the method will return messages for any channel that
        the object is subscribed to. If a channel name is given, only messages
        published on that channel are returned, provided the object is
        subscribed to that channel. Otherwise an exception is raised. The
        method returns the received data. The data is returned as a Python data
        structure.

        Note that this should only be called after a call to subscribe().
        Otherwise an exception is raised. Also note that messages are buffered
        by the socket until they are read.
        """
        return self.next_event_with_channel(channel)[0]

    def next_event_with_channel(self, channel=None):
        """Retrieve the next event from the channel.

        This method blocks until the next event is published. If no channel
        name is passed in, the method will return messages for any channel that
        the object is subscribed to. If a channel name is given only messages
        published on that channel are returned, provided the object is
        subscribed to that channel. Otherwise an exception is raised. The
        method returns a tuple of the received data and the channel the message
        has been received on The data portion of the tuple is returned as a
        Python data structure and the channel name is a string.

        Note that this should only be called after a call to subscribe().
        Otherwise an exception is raised. Also note that messages are buffered
        by the socket until they are read.
        """
        if not self.subscriptions:
            raise NotSubscribedError()

        if channel is None:
            while True:
                msg = json.loads(self.ws.recv())

                if msg['channel'] in self.subscriptions:
                    return msg['data'], msg['channel']
        else:
            if channel not in self.subscriptions:
                raise NotSubscribedError(channel)

            while True:
                msg = json.loads(self.ws.recv())

                if msg['channel'] == channel:
                    return msg['data'], msg['channel']

    def close(self):
        """Close the connection.

        This method closes the underlying WebSocket connection and thus
        invalidates all subscriptions.
        """
        self.ws.close()


class SubscriptionError(Exception):
    pass


class NotSubscribedError(SubscriptionError):
    def __init__(self, channel=None):
        self.channel = channel

    def __str__(self):
        if self.channel is None:
            return "Not subscribed to any channel"
        else:
            return "Not subscribed to channel '%s'" % self.channel


class AlreadySubscribedError(SubscriptionError):
    def __init__(self, channel):
        self.channel = channel

    def __str__(self):
        return "Already subscribed to channel '%s'" % self.channel
