import Queue
import json
import threading
import traceback
from thread import start_new_thread
from threading import Thread
from time import sleep, time
import confluent_kafka
from kafka.errors import KafkaTimeoutError

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


class PythonKafkaProducer(CypressBase):
    """
    A python kafka producer class
    """
    def __init__(self, bootstrap_server,  config=None):
        """
        :param bootstrap_server: kafka producer configuration. 'host[:port]' string (or list of 'host[:port]'
                strings) that the producer should contact to bootstrap initial
                cluster metadata. This does not have to be the full node list.
                It just needs to have at least one broker that will respond to a
                Metadata API Request. Default port is 9092. If no servers are
                specified, will default to localhost:9092.
        :param config: kafka producer configurations, see KafkaProducer object doc.
                If config is None, 'retries' will be default to 2, 'max_block_ms' will be default to 1,
                'value_serializer' will be default to utf-8 encode. The rest arguments will be the original defaults.
        """
        t1 = time()
        CypressBase.__init__(self)
        self.bootstrap_server = bootstrap_server
        self.config = config if config is not None else {}
        if not self.config:
            # set default config for cypress service
            self.config = {
                'retries': 2,
                'max_block_ms': 1,
                'value_serializer': lambda v: json.dumps(v).encode('utf-8')
            }
        self.config['bootstrap_servers'] = bootstrap_server
        self.kafka_producer_client = None
        self.connect_kafka_producer()
        self.logger.debug("init PythonKafkaProducer spent {0}".format(time() - t1))

    def connect_kafka_producer(self, connect_retries=100, retry_interval=0.1):
        """
        Connect and Get a Kafka client that publishes records to the Kafka cluster.
        :param connect_retries: the maximum number to do connect retries. Default: 100
        :param retry_interval: the time interval for every connection retry in seconds. Default: 0.1
        :return: a python kafka producer object, or None if failed to get producer
        """
        while connect_retries >= 0:
            connect_retries -= 1
            try:
                self.kafka_producer_client = KafkaProducer(**self.config)
                break
            except Exception:
                self.logger.error(traceback.format_exc())
                sleep(retry_interval)
                self.kafka_producer_client = None

    def get_kafka_producer(self):
        """
        Get a Kafka client that publishes records to the Kafka cluster.
        :return: a python kafka producer object, or None if failed to get producer
        """
        if not self.kafka_producer_client or self.kafka_producer_client._closed:
            self.connect_kafka_producer()

        return self.kafka_producer_client

    def send_message(self, topic, msg, timeout=1, unittest=False):
        """
        Send out message to the specific topic.
        :param topic: producer topic
        :param msg: message to be sent through kafka pipe. It is a json object.
        :param timeout: the timeout to wait for the result of sending the record. default to 1 ms
        :param unittest: default to False
        :type msg: json object. It has a mandatory attribute: task_id
        """
        while True:  # loop until the message is send out
            # connect to kafka client
            if not self.get_kafka_producer():
                self.logger.error('Failed to get kafka producer.')
                raise Exception('Failed to get kafka producer.')
            try:
                if unittest:
                    sleep(2)
                evt_sent = self.kafka_producer_client.send(topic, msg).get(timeout=timeout)
                self.kafka_producer_client.flush()

                self.logger.debug("message sent to: " + topic)
                if evt_sent > 0:
                    break
                # if the message is not sent out,  create a new producer.
                self.kafka_producer_client = None
            except KafkaTimeoutError as e:
                self.logger.debug(str(e))
            except Exception:
                self.logger.error(traceback.format_exc())


class KafkaProducerBase(Thread, CypressBase):
    def __init__(self, bootstrap_server, config=None, message_queue=None):
        """
        :param bootstrap_server:
        :param config:
        """
        t1 = time()
        CypressBase.__init__(self)
        Thread.__init__(self)
        self.bootstrap_server = bootstrap_server
        self.running = True
        self.config = config if config else {}
        self.config["bootstrap.servers"] = self.bootstrap_server
        self.config["socket.keepalive.enable"] = True
        self.producer = self.try_connect_kafka()
        self.message_queue = message_queue if message_queue else Queue.Queue()
        self.logger.debug("init KafkaProducerBase spent {0}".format(time() - t1))

    def run(self):
        # start_new_thread(self.producer_poll, ())
        while self.running:
            try:
                topic, msg = self.message_queue.get(block=False, timeout=1000)
            except:
                continue
            if self.producer is None:
                start_time = time()
                self.producer = self.try_connect_kafka()
                if self.producer is None:
                    self.logger.info(
                        "Cannot send message to {0}:{1}".format(self.bootstrap_server, topic))
                    return
                self.logger.debug("Create kafka producer spends {0}s".format(time() - start_time))
            start = time()
            self.produce_message(topic, msg)
            self.logger.info("sent messages to topic [{0}] spent {1}s".format(topic, time() - start))

    def produce_message(self, topic, msg):
        retry = 5
        while retry:
            try:
                self.producer.produce(topic, value=json.dumps(msg))
                self.producer.poll(0)
                return
            except BufferError as e:
                self.logger.error(e)
                retry -= 1
                self.producer.poll(0)
            except Exception as ex:
                self.logger.error(traceback.format_exc())
                self.logger.error(ex)
                self.logger.error("Failed to send message to {0}:{1}".format(self.bootstrap_server, topic))
                # reset kafka producer to allow reconnect
                self.producer = None
                return
            except KeyboardInterrupt:
                self.logger.info("Received exit input. Exiting...")
                self.running = False
        self.logger.error("Failed to send message to {0}:{1}".format(self.bootstrap_server, topic))
        self.producer = None

    def stop(self):
        self.running = False

    def send_message(self, topic, message):
        self.message_queue.put((topic, message))

    def try_connect_kafka(self):
        """
        This function tries to connect to a kafka pipe. If success, it returns a Kafka client object; otherwise,
        it returns None.

        :return: on success: a kafka  producer object. on failure: it returns None
        """
        kafka_client = None
        retry = 100
        while retry >= 0:
            if kafka_client:
                break
            retry -= 1
            try:
                kafka_client = confluent_kafka.Producer(**self.config)
            except Exception:
                self.logger.error(traceback.format_exc())
                # wait 0.1 second to retry
                sleep(0.1)
                kafka_client = None
        return kafka_client


class KafkaConsumerBase(Thread, CypressBase):
    """
    This is the kafka consumer base class. This class run on thread to poll messages from given server and topic,
    each subclass need to implement its own message_handler
    .. note:: this class has to be extended to some real functionality.
    """
    def __init__(self, bootstrap_server, topic, partition=0, group="group1", polling_timeout=0.1, connect_retries=100,
                 reconnect_interval=0.1, config=None):
        """
        :param bootstrap_server: server ip:port
        :param topic: consumer topic
        :param partition: consumer partition.
        :param polling_timeout: If no records are received before this timeout expires,
               then poll() will return an empty record set. Default: 0.1s.
        :param connect_retries:  the maximum number of retries for connecting kafka. Default: 100.
        :param reconnect_interval:  seconds spent waiting in reconnecting. Default: 0.1s.
        :param config: confluent kafka consumer configurations
        """
        t1 = time()
        CypressBase.__init__(self)
        Thread.__init__(self)
        self.running = True
        self.config = config if config else {}
        self.config["bootstrap.servers"] = bootstrap_server
        self.config["group.id"] = group
        self.consumer_topic = topic
        self.producer_topic = topic+"_mw"
        self.partition = partition
        self.polling_timeout = polling_timeout
        self.reconnect_interval = reconnect_interval
        self.connect_retries = connect_retries
        self.message_queue = Queue.Queue()
        self.kafka_producer = None
        self.kafka_consumer = None
        self.try_connect_kafka()
        self.logger.debug("init KafkaConsumerBase spent {0} sec".format(time() - t1))

    def stop(self):
        self.running = False
        if self.kafka_producer:
            try:
                self.kafka_producer.stop()
            except:
                pass

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
        :return: on success: a kafka consumer object. on failure: it returns None

        """

        self.kafka_consumer = None
        while self.connect_retries >= 0:
            if self.kafka_consumer:
                break
            self.connect_retries -= 1
            try:
                self.kafka_consumer = confluent_kafka.Consumer(**self.config)
                # use partition for consume messages. The partition number is determined by the client io
                self.kafka_consumer.assign([confluent_kafka.cimpl.TopicPartition(self.consumer_topic, self.partition)])
            # TODO: catch different types of exception, dealing with different strategies
            except Exception:
                self.logger.error(traceback.format_exc())
                # wait 0.1 second to retry
                sleep(self.reconnect_interval)
                self.kafka_consumer = None

    def run(self):

        """
        main loop.

        """

        self.logger.info("Kafka Consumer for topic: {0} starting~~".format(self.consumer_topic))
        while self.running:
            try:
                if self.kafka_consumer is None:
                    self.try_connect_kafka()
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
                    response = self.message_handler(message)
                    if response:
                        self.message_queue.put((self.producer_topic, response))
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
                try:
                    if self.kafka_producer:
                        self.kafka_producer.stop()
                except:
                    pass
                self.running = False

        if self.kafka_consumer:
            self.kafka_consumer.close()

    def message_handler(self, message):
        """
        .. warning: This is a abstract function. Child class should override this function.
        """
        raise NotImplementedError('This is a abstract function. Child class should override this function.')

