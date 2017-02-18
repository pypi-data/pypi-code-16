# -----------------------------------------------------------------------------
#
# -----------------------------------------------------------------------------
import paho.mqtt.client as mqtt
import time
# These imports are auto generated files.
import messages_pb2 as messages
import proto_io as ProtoIO
# These imports are auto generated files.
import logging
logger = logging.getLogger(__name__)


class Ioant:
    on_message_callback = None
    mqtt_client = None
    loaded_configuration = None
    delay = 1000

    def __init__(self, callback):
        """ Constructor """
        self.on_message_callback = callback
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.__on_connect
        self.mqtt_client.on_message = self.__on_message

    def setup(self, configuration):
        """ Setup """
        logger.debug("Attempting connect to: " +
                     configuration['mqtt']['broker'] +
                     " " + str(configuration['mqtt']['port']))
        self.loaded_configuration = configuration
        self.mqtt_client.connect(configuration['mqtt']['broker'],
                                 configuration['mqtt']['port'],
                                 60)
        self.delay = configuration['delay']

    def update_loop(self):
        """ Updates the mqtt loop - checking for messages """
        logger.debug("Loop Tick!")
        rc = self.mqtt_client.loop()
        if rc is not 0:
            logger.error("No connection!")
            time.sleep(2)
            client.reconnect()
        time.sleep(self.delay/1000)

    def subscribe(self, topic):
        """ subscribe to a topic """
        subscription = topic['top']+ \
        "/"+topic['global']+\
        "/"+topic['local']+\
        "/"+topic['client_id']+"/"

        if topic['message_type'] == -1:
            subscription += '+/'
        else:
            subscription += str(topic['message_type'])+"/"

        if topic['stream_index'] == -1:
            subscription += '#'
        else:
            subscription += str(topic['stream_index'])

        logger.debug("Subscribed to:" + subscription)
        self.mqtt_client.subscribe(subscription)

    def publish(self, message, topic):
        """ publish message with topic """
        payload = message.SerializeToString()

        if topic['stream_index'] < 0:
            topic['stream_index'] = 0
        topic_string = topic['top'] + "/" + topic['global'] \
            + "/" + topic['local'] + "/" + topic['client_id'] \
            + "/" + str(ProtoIO.message_type_index_dict(message.DESCRIPTOR.name)) \
            + "/" + str(topic['stream_index'])

        (result, mid) = self.mqtt_client.publish(topic_string, bytearray(payload))

        if result is not 0:
            logger.debug("Failed to publish message with topic:" + topic_string)
            return True
        else:
            logger.debug("Message sent with topic:" + topic_string)
            return False


    def __on_message(self, client, obj, message):
        """ When message is recieved from broker """
        logger.debug("Message recieved")
        if self.on_message_callback is not None:
            topic_dict = self.get_topic_from_string(str(message.topic))
            try:
                decoded_message = ProtoIO.create_proto_message(topic_dict['message_type'])
                decoded_message.ParseFromString(message.payload)
            except:
                logger.debug("Failed to decode message")
                return

            self.on_message_callback(topic_dict, decoded_message)

    def __on_connect(self, client, userdata, flags, rc):
        """ When client connects to broker """
        logger.debug("Connected with rc code: " + str(rc))

    def get_topic(self):
        """ Return a empty topic structure """
        topic_dict = {}
        topic_dict['top'] = "+"
        topic_dict['global'] = "+"
        topic_dict['local'] = "+"
        topic_dict['client_id'] = "+"
        topic_dict['message_type'] = -1
        topic_dict['stream_index'] = -1
        return topic_dict

    def get_topic_from_string(self, topic):
        """ Return a populated topic structure """
        sub_topics_list = topic.split('/')
        if len(sub_topics_list) is not 6:
            return None
        else:
            topic_dict = {}
            topic_dict['top'] = sub_topics_list[0]
            topic_dict['global'] = sub_topics_list[1]
            topic_dict['local'] = sub_topics_list[2]
            topic_dict['client_id'] = sub_topics_list[3]
            topic_dict['message_type'] = int(sub_topics_list[4])
            topic_dict['stream_index'] = int(sub_topics_list[5])
            return topic_dict

    def get_message_type(self, message_name):
        """ Return message type of the given message name """
        return ProtoIO.message_type_index_dict[message_name]

    def get_message_type_name(self, message_type):
        """ Return message name of the given message type """
        return ProtoIO.index_message_type_dict[message_type]

    def get_configuration(self):
        """ Return message name of the given message type """
        return self.loaded_configuration

    def create_message(self, message_name):
        """ Return message based on message_name """
        return ProtoIO.create_proto_message(ProtoIO.message_type_index_dict[message_name])
