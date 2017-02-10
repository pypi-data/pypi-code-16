from shaman.src.abstract_message import MessageFormat
import sys
import traceback


class AbstractStage(object):
    def __init__(self, stage_config):
        """
        Do not modify __init__, use init_stage
        :return: nothing
        """
        self.config = stage_config

        self.consumer_name = 'No consumer' # default name

        self.py_version = sys.version_info.major

        self.init_stage()

    def set_logger(self, logger):
        self.my_logger = logger

    def set_consumer_name(self, consumer_name):
        self.consumer_name = consumer_name

    def init_stage(self):
        """
        Do model init in this method, save model to self
        :return: nothing
        """
        pass

    def _do_stage(self, message):
        '''
        This is private method, dont modify/overwrite it!
        :param message:
        :return: nothing
        '''
        if 'format' in message.__dict__:
            if message.format == MessageFormat.CONTROL:
                if message.control_message == 'shutdown':
                    try:
                        self.shutdown()
                    except Exception as e:
                        self.my_logger.error('Exception in stage: {}\n{}'.format(str(e),traceback.format_exc()))
                    return message

        self.do_stage(message)

    def do_stage(self, message):
        """
        This method takes message object, proccesses it, and appends attributes with results to it.
        :param message: message object with fieds for processing. For example, if you need grab object for stage, you
        must take it from message.grab_obj
        :return: message, enriched with results
        """
        return message

    def finish_batch(self):
        """
        This method is used in bulk write operation to flush results
        :return:
        """
        pass

    def shutdown(self):
        """
        This method is used for graceful stage shutdown
        :return: nothing
        """
        print('Stage shutdown called')
        #pass
