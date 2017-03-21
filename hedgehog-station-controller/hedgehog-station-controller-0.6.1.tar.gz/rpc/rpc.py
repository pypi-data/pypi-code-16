#!/usr/bin/env python
import pika
import threading
import logging
import json
import uuid


class RpcError(Exception):
    def __init__(self, message):
        self.message = message


class RpcClient(object):
    def __init__(self, name, username, password, exchange='', host='localhost', port=5432):
        credentials = pika.PlainCredentials(username=username, password=password)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port,credentials=credentials))
        self.channel = self.connection.channel()
        self.name = name
        self.exchangeName = exchange

    def on_response(self, ch, method, props, body):
        logging.info('on_response = ' + str(props))
        if self.corr_id == props.correlation_id:
            self.response = body

    def declare_method(self, callbackMethod):
        result = self.channel.queue_declare(exclusive=True)
        self.channel.queue_bind(exchange=self.exchangeName, queue=result.method.queue)
        self.callback_queue = result.method.queue
        logging.info('set callback queue ' + self.callback_queue)
        self.channel.basic_consume(
            self.on_response,
            no_ack=True,
            queue=self.callback_queue)

    def call(self, body, method_name):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        message_properties = pika.BasicProperties(reply_to=self.callback_queue, correlation_id=self.corr_id, content_type='application/json', content_encoding='utf-8')
        self.channel.basic_publish(
            exchange=self.exchangeName,
            routing_key=method_name,
            properties=message_properties,
            body=json.dumps(obj=body,ensure_ascii=False))
        logging.debug('Call \"' + method_name + '\" request ' + str(body) + ' -> ' + str(message_properties))
        while self.response is None:
            self.connection.process_data_events()
        logging.debug('Call \"' + method_name + '\" response ' + str(self.response) + '.')
        return json.loads(self.response.decode("utf-8"))

    def dispose(self):
        self.connection.close()


class RpcServer(threading.Thread):
    def __init__(self, name, username, password, exchange='', host='localhost'):
        threading.Thread.__init__(self, name=name)
        logging.info('name=' + str(name) + ', username=' + str(username) + ', password=' + str(password) + ', exchange=' + str(exchange) + ', host=' + str(host))
        credentials = pika.PlainCredentials(username=username, password=password)
        parameters = pika.ConnectionParameters(connection_attempts=2, retry_delay=1, virtual_host='/', port=5672, host=host, credentials=credentials)
        # self.connection = pika.BlockingConnection(pika.URLParameters("amqp://tardozzi:qwe123@localhost"))
        self.connection = pika.BlockingConnection(parameters=parameters)
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=1)
        self.exchange = exchange
        self._stop = threading.Event()
        self.channel.exchange_declare(exchange=self.exchange, type='direct')

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def create_method(self, name, request_handler_method):
        self.channel.queue_declare(queue=name)
        self.channel.queue_bind(exchange=self.exchange, queue=name, routing_key=name)
        logging.debug('Declare ' + self.exchange +'.' + name + '.')
        self.channel.basic_consume(request_handler_method, queue=name)

    def return_acknowledgement(self, ch, method, props, response, headers={}):
        logging.debug('Acknowledge ' + str(method) + ' -> ' + str(props))
        ch.basic_publish(
            exchange=self.exchange,
            routing_key=props.reply_to,
            properties=pika.BasicProperties(correlation_id=props.correlation_id, content_type='application/json', content_encoding='utf-8',headers=headers),
            body=json.dumps(response)
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def dispose(self):
        self.connection.close()
        self.channel.stop_consuming()

    def run(self):
        logging.info('%s is running' % self.name)
        self.channel.start_consuming()
        self.dispose()
        return
