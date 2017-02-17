""" Loglarin RabbitMQ"ya aktarilmasi icin kullanilan sinif """
import json
import logging
from hurriyetlog import hurriyetlog

class RabbitMQHandler(logging.Handler):
    """
     A handler that acts as a RabbitMQ publisher
     Requires the pika module.

     Example setup::

        handler = RabbitMQHandler("amqp://guest:guest@localhost/%2f", queue="HurLogQueue")
    """
    def __init__(self, uri="", queue=""):
        logging.Handler.__init__(self)
        try:
            import pika
        except ImportError:
            raise RuntimeError("The pika library is required for the RabbitMQSubscriber.")
        self.connection = pika.BlockingConnection(pika.URLParameters(uri))
        self.queue = queue
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue, durable=False, exclusive=False, auto_delete=True)

    def emit(self, record):
        log_obj = hurriyetlog.HurriyetLog(record)
        log_str = json.dumps(log_obj.to_json())
        self.channel.basic_publish(exchange="", routing_key=self.queue, body=log_str)

    def close(self):
        self.connection.close()
