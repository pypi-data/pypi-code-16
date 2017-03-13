import logging
import logging.handlers


class Logger(object):
    _logger = logging.getLogger('py-build-server')
    handler = logging.handlers.SysLogHandler(address='/dev/log')
    _logger.addHandler(handler)

    def __init__(self, identifier):
        self.identifier = identifier

    def debug(self, msg):
        self._logger.debug('{}:{}'.format(self.identifier, msg))

    def info(self, msg):
        self._logger.info('{}:{}'.format(self.identifier, msg))

    def warn(self, msg):
        self._logger.warn('{}:{}'.format(self.identifier, msg))

    def error(self, msg):
        self._logger.error('{}:{}'.format(self.identifier, msg))
