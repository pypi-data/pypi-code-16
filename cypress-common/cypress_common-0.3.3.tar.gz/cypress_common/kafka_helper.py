import json
from .logger_helper import get_logger
import socket
import traceback
from threading import Thread
from time import sleep
import confluent_kafka
from .cypress_base import CypressBase
from kafka import KafkaProducer

# search engine consumes messages with topic "search" and produces messages with topic "search_mw"
KAFKA_SEARCH_TOPIC = "search"
KAFKA_SEARCH_RESULT_TOPIC = "search_mw"

# engine face detection service consumes messages with topic "face_detection"
#  and produces messages with topic "face_detection_mw"
KAFKA_DETECTION_TOPIC = "face_detection"
KAFKA_DETECTION_RESULT_TOPIC = "face_detection_mw"

# engine face recognition service consumes messages with topic "face_recognition"
#  and produces messages with topic "face_recognition_mw"
KAFKA_RECOGNITION_TOPIC = "face_recognition"
KAFKA_RECOGNITION_RESULT_TOPIC = "face_recognition_mw"

# engine profile_creation service consumes messages with topic "profile_creation"
#  and produces messages with topic "profile_creation_mw"
KAFKA_PROFILE_TOPIC = "profile_creation"
KAFKA_PROFILE_RESULT_TOPIC = "profile_creation_mw"


LOGGER = get_logger("KafkaHelper")

  
def get_kafka_producer(bootstrap_server, retries=2, max_block_ms=1):
    """
    returns a python kafka producer object
    :param bootstrap_server: 'host[:port]' string (or list of 'host[:port]'
            strings) that the producer should contact to bootstrap initial
            cluster metadata. This does not have to be the full node list.
            It just needs to have at least one broker that will respond to a
            Metadata API Request. Default port is 9092. If no servers are
            specified, will default to localhost:9092.
    :param retries: Setting a value greater than zero will cause the client
            to resend any record whose send fails with a potentially transient
            error. Note that this retry is no different than if the client
            resent the record upon receiving the error. Allowing retries
            without setting max_in_flight_requests_per_connection to 1 will
            potentially change the ordering of records because if two batches
            are sent to a single partition, and the first fails and is retried
            but the second succeeds, then the records in the second batch may
            appear first.
            Default: 2.
    :param max_block_ms:  Number of milliseconds to block during send() and
            partitions_for(). These methods can be blocked either because the
            buffer is full or metadata unavailable. Blocking in the
            user-supplied serializers or partitioner will not be counted against
            this timeout. Default: 1.
    :return: a python kafka producer object
    """
    try:

        kafka_client = KafkaProducer(bootstrap_servers=bootstrap_server, client_id=socket.gethostname(),
                                     value_serializer=lambda v: json.dumps(v).encode('utf-8'), retries=retries,
                                     max_block_ms=max_block_ms)
    except:
        LOGGER.error(traceback.format_exc())
        # wait 0.1 second to retry
        sleep(0.1)
        kafka_client = None
    return kafka_client


def get_kafka_producer_with_config(config):
    """

    :param config: kafka producer configurations
    :return:
    """
    try:
        config["value_serializer"] = lambda v: json.dumps(v).encode('utf-8')
        kafka_client = KafkaProducer(**config)
    except:
        LOGGER.error(traceback.format_exc())
        # wait 0.1 second to retry
        sleep(0.1)
        kafka_client = None
    return kafka_client


def send_message(kafka_producer, topic, msg, bootstrap_server=None, unittest=False):
    """
    Send out message to the specific topic, the kafka producer object needs to be either None or python-kafka producer object
    :param kafka_producer: a python kafka producer instance
    :param topic: producer topic
    :param msg: message to be sent through kafka pipe. It is a json object.
    :param bootstrap_server: kafka server ip:port. Note this parameter is optional,
                            only use it if the caller does not have a kafka producer object
    :param unittest: default to False
    :type msg: json object. It has a mandatory attribute: task_id
    """

    # send a message to the topic
    while True:  # do a for loop until the message is send out
        if kafka_producer is None:
            if bootstrap_server is None:
                raise Exception("kafka producer is not initalized, missing bootstrap_server")
            kafka_producer = get_kafka_producer(bootstrap_server)
        try:
            if unittest:
                sleep(2)
            evt_sent = kafka_producer.send(topic, msg).get(timeout=1)
            kafka_producer.flush()

            LOGGER.info("message sent to: " + topic)
            if evt_sent > 0:
                break
            # if the message is not sent out, create a new producer.
            if bootstrap_server:
                kafka_producer = None
        except Exception as ex:
            LOGGER.error(traceback.format_exc())


class KafkaConsumerBase(Thread, CypressBase):
    """
    This is the kafka consumer base class. This class run on thread to poll messages from given server and topic,
    each subclass need to implement its own message_handler
    .. note:: this class has to be extended to some real functionality.
    """
    def __init__(self, bootstrap_server, topic, group='group1', partition=0, polling_timeout=0.1, max_retries=100,
                 reconnect_interval=0.1, config=None):
        """
        :param bootstrap_server: server ip:port
        :param topic: consumer topic
        :param group: consumer group
        :param partition: consumer partition.
        :param polling_timeout: If no records are received before this timeout expires,
               then poll() will return an empty record set. Default: 0.1s.
        :param max_retries:  the maximum number of retries for connecting kafka. Default: 100.
        :param reconnect_interval:  seconds spent waiting in reconnecting. Default: 0.1s.
        :param config: confluent kafka consumer configurations
        """
        CypressBase.__init__(self)
        Thread.__init__(self)
        self.kafka_consumer = None
        self.running = True
        self.config = config if config else dict()
        self.consumer_topic = topic
        self.partition = partition
        self.polling_timeout = polling_timeout
        self.reconnect_interval = reconnect_interval
        self.max_retries = max_retries
        self.config['group.id'] = group
        self.config['bootstrap.servers'] = bootstrap_server

    def stop(self):
        self.running = False

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Release the message queue.
        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        try:
            if not self.kafka_consumer:
                self.kafka_consumer.close()
        except Exception as ex:
            self.logger.info(ex)

    def try_connect_kafka(self):
        """
        This function tries to connect to a kafka pipe. If success, it returns a Kafka client object; otherwise,
        it returns None.
        :return: on success: a kafka consumer or producer object. on failure: it returns None
        """
        kafka_client = None
        while self.max_retries >= 0:
            if kafka_client:
                break
                self.max_retries -= 1
            try:
                kafka_client = confluent_kafka.Consumer(**self.config)
                # use partition for consume messages. The partition number is determined by the client io
                kafka_client.assign([confluent_kafka.cimpl.TopicPartition(self.consumer_topic, self.partition)])
            # TODO: catch different types of exception, dealing with different strategies
            except Exception:
                self.logger.error(traceback.format_exc())
                # wait 0.1 second to retry
                sleep(self.reconnect_interval)
                kafka_client = None
        return kafka_client

    def run(self):

        """
        main loop.

        """
        self.logger.info("Kafka Consumer for topic: {0} starting~~".format(self.consumer_topic))
        while self.running:
            try:
                if self.kafka_consumer is None:
                    self.kafka_consumer = self.try_connect_kafka()
                    if self.kafka_consumer is None:
                        self.logger.info("Run: cannot connect to Kafka server.")
                        continue
                message = self.kafka_consumer.poll(timeout=self.polling_timeout)
                if not self.running:
                    break
                if message is None:
                    continue
                if message.error():
                    # Error or event
                    if message.error().code() == confluent_kafka.KafkaError._PARTITION_EOF:
                        # End of partition event
                        self.logger.info("{0} {1} reached end at offset {2}\n".format(
                            message.topic(),
                            message.partition(),
                            message.offset()))
                    else:
                        # Error
                        raise confluent_kafka.KafkaError(message.error())
                else:
                    # self.kafka_consumer.commitSync();
                    # self.kafka_consumer.pause();
                    message = json.loads(message.value())
                    self.message_handler(message)
            except confluent_kafka.KafkaError as ke:
                self.logger.info(ke.message)
                self.kafka_consumer.close()
                self.kafka_consumer = None  # reset consumer connection. Try to connect to kafka server again.
                continue
            except Exception as ex:
                self.logger.error(traceback.format_exc())
                self.logger.error(ex)
                self.kafka_consumer.close()
                self.kafka_consumer = None  # reset consumer connection. Try to connect to kafka server again.
                continue
            except KeyboardInterrupt:
                self.logger.info("Received exit input. Exiting...")
                running = False

        if self.kafka_consumer:
            self.kafka_consumer.close()

    def message_handler(self, message):
        """
        .. warning: This is a abstract function. Child class should override this function.
        """
        pass

