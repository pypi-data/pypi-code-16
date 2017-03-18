import logging
import logging.handlers

from py_build_server.lib.web_server.decorators import multi_line_log


class Logger(object):
    _logger = logging.getLogger('py-build-server')
    handler = logging.handlers.SysLogHandler(address='/dev/log')
    _logger.propagate = False
    _logger.addHandler(handler)

    def __init__(self, identifier):
        self.identifier = identifier

    @multi_line_log
    def debug(self, msg):
        self._logger.debug('[DEBUG] {}:{}'.format(self.identifier, msg))

    @multi_line_log
    def info(self, msg, *args):
        self._logger.info('{}:{}'.format(self.identifier, msg))

    @multi_line_log
    def warn(self, msg):
        self._logger.warn('[WARN] {}:{}'.format(self.identifier, msg))

    @multi_line_log
    def error(self, msg, *args):
        self._logger.error('[ERROR] {}:{}'.format(self.identifier, msg))

    def log(self, level, msg, exc_info):  # implemented as a log interface for cherrypy
        if level == 20:
            self.info(msg)
        else:
            self.error(msg)

    def __str__(self):
        return "{} logger object".format(self.identifier)


