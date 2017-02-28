import logging
import pika

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


class YasConsumer(object):
    """This is an example consumer that will handle unexpected interactions
    with RabbitMQ such as channel and connection closures.

    If RabbitMQ closes the connection, it will reopen it. You should
    look at the output, as there are limited reasons why the connection may
    be closed, which usually are tied to permission related issues or
    socket timeouts.

    If the channel is closed, it will indicate a problem with one of the
    commands that were issued and that should surface in the output as well.

    """
    EXCHANGE = 'message'
    EXCHANGE_TYPE = 'topic'
    QUEUE = 'yas'
    ROUTING_KEY = 'yas'

    def __init__(self, amqp_url):
        """Create a new instance of the consumer class, passing in the AMQP
        URL used to connect to RabbitMQ.

        :param str amqp_url: The AMQP url to connect with

        """
        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._url = amqp_url

    def __connect(self):
        """This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the __on_connection_open method
        will be invoked by pika.

        :rtype: pika.SelectConnection

        """
        LOGGER.info('Connecting to %s', self._url)
        return pika.SelectConnection(pika.URLParameters(self._url),
                                     self.__on_connection_open,
                                     stop_ioloop_on_close=False)

    def __on_connection_open(self, unused_connection):
        """This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.

        :type unused_connection: pika.SelectConnection

        """
        LOGGER.info('Connection opened')
        self._connection.add_on_close_callback(self.__on_connection_closed)
        self.__open_channel()

    def __on_connection_closed(self, connection, reply_code, reply_text):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.

        :param pika.connection.Connection connection: The closed connection obj
        :param int reply_code: The server provided reply_code if given
        :param str reply_text: The server provided reply_text if given

        """
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            LOGGER.warning('Connection closed, reopening in 5 seconds: (%s) %s',
                           reply_code,
                           reply_text)
            self._connection.add_timeout(5, self.__reconnect)

    def __reconnect(self):
        """Will be invoked by the IOLoop timer if the connection is
        closed. See the __on_connection_closed method.

        """
        # This is the old connection IOLoop instance, stop its ioloop
        self._connection.ioloop.stop()

        if not self._closing:
            # Create a new connection
            self._connection = self.__connect()
            # There is now a new connection, needs a new ioloop to run
            self._connection.ioloop.start()

    def __open_channel(self):
        """Open a new channel with RabbitMQ by issuing the Channel.Open RPC
        command. When RabbitMQ responds that the channel is open, the
        __on_channel_open callback will be invoked by pika.

        """
        LOGGER.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.__on_channel_open)

    def __on_channel_open(self, channel):
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.

        Since the channel is now open, we'll declare the exchange to use.

        :param pika.channel.Channel channel: The channel object

        """
        LOGGER.info('Channel opened')
        self._channel = channel
        LOGGER.info('Adding channel close callback')
        self._channel.add_on_close_callback(
                lambda _, _, _: self._connection.close()
        )

        # Setup exchange
        self._channel.exchange_declare(
            # Invoked by pika upan successful exchange declaration
            lambda _: self._channel.queue_declare(
                # Invoked by pika upon queue declare completion
                lambda _: self._channel.queue_bind(
                    # Invoked by pika upon queue bind completion
                    lambda _: self.__start_consuming(),
                    self.QUEUE,
                    self.EXCHANGE,
                    self.ROUTING_KEY
                ),
                self.QUEUE
            ),
            exchange_name,
            self.EXCHANGE_TYPE
        )

    def __start_consuming(self):
        """This method sets up the consumer by __add_on_cancel_callback so that
        the object is notified if RabbitMQ cancels the consumer. It then issues
        the Basic.Consume RPC command which returns the consumer tag that is
        used to uniquely identify the consumer with RabbitMQ. We keep the value
        to use it when we want to cancel consuming. The __on_message method is
        passed in as a callback pika will invoke when a message is fully received.

        """
        self._channel.add_on_cancel_callback(
                lambda _: self._channel and self._channel.close()
        )
        self._consumer_tag = self._channel.basic_consume(self.__on_message,
                                                         self.QUEUE)

    def __on_message(self, unused_channel, basic_deliver, properties, body):
        """Invoked by pika when a message is delivered from RabbitMQ. The basic_deliver
        object that is passed in carries the exchange, routing key, delivery tag
        and a redelivered flag for the message. The properties passed in is an
        instance of BasicProperties with the message properties and the body
        is the message that was sent.

        :param pika.channel.Channel unused_channel: The channel object
        :param pika.Spec.Basic.Deliver: basic_deliver method
        :param pika.Spec.BasicProperties: properties
        :param str|unicode body: The message body

        """
        LOGGER.info('Received message # %s from %s: %s',
                    basic_deliver.delivery_tag,
                    properties.app_id,
                    body)
        LOGGER.info('Acknowledging message %s', delivery_tag)
        self._channel.basic_ack(delivery_tag)

    def run(self):
        """Run the example consumer by connecting to RabbitMQ and then
        starting the IOLoop to block and allow the SelectConnection to operate.
        """
        self._connection = self.__connect()
        self._connection.ioloop.start()

    def stop(self):
        """Cleanly shutdown the connection to RabbitMQ by stopping the consumer
        with RabbitMQ. The IOLoop is started again in case this method is invoked
        when an exception which stops the IOLoop is raised as the IOLoop needs
        to be running for pika to communicate with RabbitMQ. All of the commands
        issued prior to starting the IOLoop will be buffered but not processed.
        """
        LOGGER.info('Stopping')
        self._closing = True
        # Stop consuming
        if self._channel:
            LOGGER.info('Sending a Basic.Cancel RPC command to RabbitMQ')
            self._channel.basic_cancel(lambda _: self._channel.close(), self._consumer_tag)
        self._connection.ioloop.start()
        LOGGER.info('Stopped')


def main():
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    YasConsumer('amqp://guest:guest@localhost:5672/%2F').run()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        consumer.stop()
