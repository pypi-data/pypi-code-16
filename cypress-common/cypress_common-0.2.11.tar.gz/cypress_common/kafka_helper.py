import json
import logging
import socket
import traceback
from time import sleep
import confluent_kafka


class KafkaHelper:
    __logger = logging.getLogger(name="KafkaHelper")

    def __init__(self):
        pass

    @staticmethod
    def try_connect_kafka(bootstrap_server, is_consumer=False, topic=None, group="group1", partition=0):
        """
        This function tries to connect to a kafka pipe. If success, it returns a Kafka client object; otherwise,
        it returns None.
        :param bootstrap_server: bootstrap server url. The bootstrap server should be kafka broker.
        e.g. <hostname>:<port>

        :param is_consumer: is a consumer connection. default: False
        :param topic: kafka topic. only needed when is_consumer is set to True.
        :param group: consumer group, default to group1. only needed when is_consumer is set to True.
        :param partition: consumer partition, default to 0. only needed when is_consumer is set to True.
        :return: on success: a kafka consumer or producer object. on failure: it returns None
        """
        kafka_client = None
        retry = 100
        while retry >= 0:
            if kafka_client:
                break
            retry -= 1
            try:
                if is_consumer:
                    consumer_config = {'bootstrap.servers': bootstrap_server,
                                       'group.id': group,
                                       # 'client.id': socket.gethostname(),
                                       'max.partition.fetch.bytes': 10485760,
                                       # 'default.topic.config': {'auto.offset.reset': 'smallest'},
                                       'session.timeout.ms': 8000}
                    kafka_client = confluent_kafka.Consumer(**consumer_config)
                    # use partition for consume messages. The partition number is determined by the client io
                    kafka_client.assign([confluent_kafka.cimpl.TopicPartition(topic, partition)])
                else:
                    # producer_config = {'bootstrap.servers': bootstrap_server,
                    #                    'client.id': socket.gethostname(),
                    #                    'queue.buffering.max.messages': 1,
                    #                    'queue.buffering.max.ms': 1,
                    #                    'default.topic.config': {'produce.offset.report': True}}
                    # kafka_client = confluent_kafka.Producer(**producer_config)

                    from kafka import KafkaProducer
                    kafka_client = KafkaProducer(bootstrap_servers=bootstrap_server, client_id=socket.gethostname(),
                                                 value_serializer=lambda v: json.dumps(v).encode('utf-8'), retries=2,
                                                 max_block_ms=1)
            # TODO: catch different types of exception, dealing with different strategies
            except Exception as ex:
                KafkaHelper.__logger.error(traceback.format_exc())
                # wait 0.1 second to retry
                sleep(0.1)
                kafka_client = None
        return kafka_client

    @staticmethod
    def send_message(kafka_producer, topic, msg, bootstrap_server=None, unittest=False):
        """
        Send out message to the specific topic, with the task uuid
        :param kafka_producer: a kafka producer instance
        :param topic: producer topic
        :param msg: message to be sent through kafka pipe. It is a json object.
        :type msg: json object. It has a mandatory attribute: task_id
        """

        # send a message to the topic
        while True:  # do a for loop until the message is send out
            if kafka_producer is None:
                if bootstrap_server is None:
                    raise Exception("kafka producer is not initalized, missing bootstrap_server")
                kafka_producer = KafkaHelper.try_connect_kafka(bootstrap_server)
            try:
                if unittest:
                    sleep(2)
                evt_sent = kafka_producer.send(topic, msg).get(timeout=1)
                kafka_producer.flush()

                KafkaHelper.__logger.info("message sent to: " + topic)
                if evt_sent > 0:
                    break
                # if the message is not sent out, create a new producer.
                if bootstrap_server:
                    kafka_producer = None
            except Exception as ex:
                KafkaHelper.__logger.error(traceback.format_exc())

