import json
import traceback
import time

from shaman.src.analyzers.abstract_stage import AbstractStage
from shaman.src.abstract_message import control_messages_invert_dict, MessageFormat

from socket import gaierror
from shaman.src.helpers.url_helpers import canonurl
from kafka import KafkaConsumer #MultiProcessConsumer
from shaman.src.helpers.kafka_exceptions import KafkaSendMaximumRetriesExceeded
from kafka.common import CommitFailedError, NoBrokersAvailable
from kafka.errors import NotLeaderForPartitionError, UnrecognizedBrokerVersion
from kafka.coordinator.assignors.roundrobin import RoundRobinPartitionAssignor


class CrawlerKafkaInputStage(AbstractStage):
    """
        Processes a message from kafka topic (Crawlers). Actions:
            - inits stage
            - creates kafka consumer
            - acquire a message from kafka topic
            - deals with exceptions
            - proceed with a message, checks if it is ok and extracts some fields from it

        Input data:
            - kafka message
        Output data:
            - url
            - owner
            - comment

        Using modules:
            - kafka-python (https://github.com/dpkp/kafka-python)
            - json (https://docs.python.org/2/library/json.html)
            - traceback (https://docs.python.org/2/library/traceback.html)
            - time (https://docs.python.org/2/library/time.html)
            - socket (https://docs.python.org/2/library/socket.html)
        """
    def __init__(self,stage_config):

        super(CrawlerKafkaInputStage, self).__init__(stage_config)

        self.consumer = None

        self.init_stage()

        #self.create_consumer()

    def init_stage(self):
        self.topic = self.config['topic']
        self.group_id = self.config['group']
        self.max_partition_fetch_bytes = int(self.config['max_partition_fetch_bytes'])
        self.kafka_cluster = self.config['cluster']
        self.request_timeout_ms = int(self.config['request_timeout_ms'])
        self.session_timeout_ms = int(self.config['session_timeout_ms'])
        self.heartbeat_interval_ms = int(self.config['heartbeat_interval_ms'])
        self.metadata_max_age_ms = int(self.config['metadata_max_age_ms'])
        self.commit_every = int(self.config['commit_every'])
        self.commit_counter = 0
        self.retries_on_error = int(self.config['retries_on_error'])
        self.current_retry = 0
        self.retry_pause = float(float(self.config['retry_pause']))

    def create_consumer(self):
        if not self.consumer:
            self.consumer = KafkaConsumer(self.topic,
                                          bootstrap_servers=[self.kafka_cluster],
                                          group_id=self.group_id,
                                          auto_offset_reset='latest',
                                          max_partition_fetch_bytes=self.max_partition_fetch_bytes,
                                          enable_auto_commit=False,
                                          #max_poll_records=1,
                                          request_timeout_ms=self.request_timeout_ms,
                                          session_timeout_ms=self.session_timeout_ms,
                                          heartbeat_interval_ms=self.heartbeat_interval_ms,
                                          metadata_max_age_ms=self.metadata_max_age_ms,
                                          partition_assignment_strategy=[RoundRobinPartitionAssignor, ],
                                          client_id=self.consumer_name)

    def do_stage(self,  message):
        try:
            self.create_consumer()

            stdin_line = self.in_queue.get().strip()

            message = self._process_input_line(stdin_line,message)

            if not self.consumer:
                self.create_consumer()

            self.commit_counter += 1
            if self.commit_counter%self.commit_every == 0:
                self.consumer.commit()
                self.commit_counter = 0

            if self.py_version == 2:
                kafka_message = self.consumer.next()
            else:
                kafka_message = next(self.consumer)

            while not kafka_message.key:
                self.my_logger.warning('No key in kafka message!')
                if self.py_version == 2:
                    kafka_message = self.consumer.next()
                else:
                    kafka_message = next(self.consumer)

            if not kafka_message.value:
                value = None
            else:
                value = json.loads(kafka_message.value)

            if value:
                if type(value) is dict:
                    self.owner = value["owner"]
                    self.comment = value["comment"]
                else:
                    self.owner = value
                    self.comment = ""
            else:
                self.owner = "hbase_scan"
                self.comment = ""

            if self.py_version == 2:
                url = canonurl(str(kafka_message.key).rstrip("\n")).encode("utf-8")
            else:
                url = canonurl(str(kafka_message.key).rstrip("\n"))

            message.url = url
            message.comment = self.comment
            message.owner = self.owner
            message.add_result_to_message('_id', message.url, 'failed_urls')

            self.current_retry = 0
            return message


        except CommitFailedError as e:
            self.my_logger.error("CommitFailedError exception: {}".format(e))
            self.my_logger.error('Traceback: {}'.format(traceback.format_exc()))
            self.on_kafka_read_fail()
            self.total_kafka_retry(message)

        except NoBrokersAvailable as e:
            self.my_logger.error("NoBrokersAvailable exception: {}".format(e))
            self.my_logger.error('Traceback: {}'.format(traceback.format_exc()))
            self.on_kafka_read_fail()
            self.total_kafka_retry(message)

        except gaierror as e:
            self.my_logger.error("gaierror exception: {}".format(e))
            self.my_logger.error('Traceback: {}'.format(traceback.format_exc()))
            self.on_kafka_read_fail()
            self.total_kafka_retry(message)

        except NotLeaderForPartitionError as e:
            self.my_logger.error("NotLeaderForPartitionError exception: {}".format(e))
            self.my_logger.error('Traceback: {}'.format(traceback.format_exc()))
            self.on_kafka_read_fail()
            self.total_kafka_retry(message)

        except UnrecognizedBrokerVersion as e:
            self.my_logger.error("UnrecognizedBrokerVersion exception: {}".format(e))
            self.my_logger.error('Traceback: {}'.format(traceback.format_exc()))
            self.on_kafka_read_fail()
            self.total_kafka_retry(message)

        self.consumer = None

    def _process_input_line(self, line, message):
        if line in control_messages_invert_dict:
            if control_messages_invert_dict[line] == 'shutdown':
                message.format = MessageFormat.CONTROL
                message.control_message = 'shutdown'
        return message

    def on_kafka_read_fail(self):
        pass

    def total_kafka_retry(self, message):
        self.consumer = None
        time.sleep(self.retry_pause)
        self.create_consumer()
        self.current_retry+=1
        if self.current_retry%self.retries_on_error == 0:
            raise KafkaSendMaximumRetriesExceeded()

        self.do_stage(message)

    def shutdown(self):
        self.consumer.commit()