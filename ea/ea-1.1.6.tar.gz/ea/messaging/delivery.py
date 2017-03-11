import logging
import uuid


class Delivery:
    logger = logging.getLogger('amqp')

    @property
    def id(self):
        return self.msg.id

    def __init__(self, msg):
        self.msg = msg
        self.msg.id = str(uuid.uuid4())
        self.tag = str(uuid.uuid4())

    def send(self, send):
        """Sends the queued message to the message broker. Assumed is
        that when this method is invoked, the link over which this
        message is to be sent has credit.
        """
        self.logger.debug("Sending message (id: %s, tag: %s)", self.id, self.tag)
        send(self.msg, tag=self.tag)

    def settle(self):
        """Flag the delivery as settled."""
        pass
