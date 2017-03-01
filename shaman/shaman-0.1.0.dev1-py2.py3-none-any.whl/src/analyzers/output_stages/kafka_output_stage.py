import time
import json

from kafka import KeyedProducer, KafkaClient
from kafka.errors import MessageSizeTooLargeError, FailedPayloadsError, NotLeaderForPartitionError

from shaman.src.analyzers.abstract_stage import AbstractStage
from shaman.src.helpers.kafka_exceptions import KafkaSendMaximumRetriesExceeded

import random


class KafkaJsonOutputStage(AbstractStage):
    def init_stage(self):
        self.kafka_cluster = self.config['cluster']
        self.topic = self.config['topic']
        self.retry_send_timeout = float(self.config['retry_send_timeout'])
        self.max_send_retries = int(self.config['max_send_retries'])

        # this is used to send only url to offine analyzers
        self.fields_to_send = self.config['fields_to_send'].split(',')

        self.kafka = KafkaClient(self.kafka_cluster)
        self.producer = KeyedProducer(self.kafka, async=True,
                                      async_retry_backoff_ms=100,
                                      batch_send_every_n=100,
                                      async_retry_limit=30

                                      )
        if 'key_id' in self.config:
            self.key_id = self.config['key_id']
        else:
            self.key_id = None

    def do_stage(self,  message):
        """
        Kafka output stage is used to output json results to kafka with retries
        Pay attention to fields_to_send. If field is only one, and it's type in message is dict then all this dict would
        be outputted to kafka as json.

        Else json would be constructed from fields listed in fields_to_send.
        """
        kafka_to_send_dict = dict()

        if len(self.fields_to_send) == 1:
            field_to_send = self.fields_to_send[0]
            if field_to_send in message.__dict__:
                if type(message.__dict__[field_to_send]) is dict:
                    kafka_to_send_dict = message.__dict__[field_to_send]

                else:
                    kafka_to_send_dict[field_to_send] = message.__dict__[field_to_send]
            else:
                return message
        else:
            for f in self.fields_to_send:
                if f in message.__dict__:
                    kafka_to_send_dict[f] = message.__dict__[f]

        if not kafka_to_send_dict:
            return message

        if self.key_id:
            self.msg_key = kafka_to_send_dict[self.key_id]
        else:
            self.msg_key = str(random.random())

        try:
            kafka_msg = json.dumps(kafka_to_send_dict, ensure_ascii=False, encoding='utf-8')
        except UnicodeDecodeError:
            try:
                kafka_msg = json.dumps(kafka_to_send_dict, encoding='utf-8')
            except UnicodeDecodeError:
                kafka_msg = json.dumps(kafka_to_send_dict, encoding='cp1251')

        retries = 0
        is_error = self.send_to_kafka(kafka_msg)
        while is_error :
            time.sleep(self.retry_send_timeout)
            is_error = self.send_to_kafka(kafka_msg)

            retries += 1
            if retries >= self.max_send_retries:
                raise KafkaSendMaximumRetriesExceeded()

        #del kafka_msg

        return message

    def shutdown(self):
        self.producer.stop()
        self.kafka.close()

    def send_to_kafka(self, msg):
        """
        Trying send to kafka and return error status
        :param msg:
        :return:
        """
        try:

            if self.py_version == 2:
                msg = msg.encode('utf-8')
            else:
                msg = str(msg)
                # message should be bytes, check out here:
                # http://kafka-python.readthedocs.io/en/master/apidoc/kafka.producer.html
            self.producer.send_messages(self.topic, self.msg_key, msg)


        except MessageSizeTooLargeError as e:
            self.my_logger.error('Cant put result json to kafka queue, message too large: {} bytes'.format(
                msg.__sizeof__()
            ))
            return False
        except FailedPayloadsError as e:
            self.my_logger.error('Exception FailedPayloadsError occured: {}'.format(e))
            self.my_logger.error('Retrying message send to kafka')
            return True

        except NotLeaderForPartitionError as e:
            self.my_logger.error('Exception NotLeaderForPartitionError occured: {}'.format(e))
            self.my_logger.error('Retrying message send to kafka')
            return True

        return False
