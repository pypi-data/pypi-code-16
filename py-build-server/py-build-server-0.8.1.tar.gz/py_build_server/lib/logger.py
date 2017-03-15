import logging
import logging.handlers


class Logger(object):
    _logger = logging.getLogger('py-build-server')
    handler = logging.handlers.SysLogHandler(address='/dev/log')
    _logger.propagate = False
    _logger.addHandler(handler)

    def __init__(self, identifier):
        self.identifier = identifier

    def debug(self, msg):
        for msg in msg.splitlines():
            self._logger.debug('[DEBUG] {}:{}'.format(self.identifier, msg))

    def info(self, msg, *args):
        for msg in msg.splitlines():
            self._logger.info('{}:{}'.format(self.identifier, msg))

    def warn(self, msg):
        for msg in msg.splitlines():
            self._logger.warn('[WARN] {}:{}'.format(self.identifier, msg))

    def error(self, msg, *args):
        for msg in msg.splitlines():
            self._logger.error('[ERROR] {}:{}'.format(self.identifier, msg))

    def log(self, level, msg, exc_info):  # implemented as a log interface for cherrypy
        if level == 20:
            self.info(msg)
        else:
            self.error(msg)

    def __str__(self):
        return "{} logger object".format(self.identifier)

