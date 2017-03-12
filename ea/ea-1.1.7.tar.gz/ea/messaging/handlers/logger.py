import logging


class LoggerMixin:
    logger_name = 'amqp'

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(self.logger_name)
