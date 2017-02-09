# coding=utf-8

import sys
import logging

from logging.handlers import WatchedFileHandler
from logging.handlers import RotatingFileHandler


try:
    LOG_LEVELS = dict(logging._nameToLevel)
    LOG_LEVELS.update(logging._levelToName)
except AttributeError:
    LOG_LEVELS = dict(logging._levelNames)
LOG_LEVELS.setdefault('FATAL', logging.FATAL)
LOG_LEVELS.setdefault(logging.FATAL, 'FATAL')

DISABLE_TRACEBACKS = False


def get_logger(logger):
    if isinstance(logger, (str, unicode)):
        logger = logging.getLogger(logger)
    if not logger.handlers:
        handler = RotatingFileHandler('console.log',
                                      maxBytes=10000,
                                      backupCount=1)
        logger.addHandler(handler)
    return logger


def get_loglevel(level):
    if isinstance(level, unicode):
        return LOG_LEVELS[level]
    return level


class LogMixin(object):
    def debug(self, *args, **kwargs):
        return self.log(logging.DEBUG, *args, **kwargs)

    def info(self, *args, **kwargs):
        return self.log(logging.INFO, *args, **kwargs)

    def warn(self, *args, **kwargs):
        return self.log(logging.WARN, *args, **kwargs)

    def error(self, *args, **kwargs):
        return self._error(logging.ERROR, *args, **kwargs)

    def critical(self, *args, **kwargs):
        return self._error(logging.CRITICAL, *args, **kwargs)

    def _error(self, severity, *args, **kwargs):
        kwargs.setdefault('exc_info', True)
        if DISABLE_TRACEBACKS:
            kwargs.pop('exc_info', None)
        return self.log(severity, *args, **kwargs)

    def annotate(self, text):
        return '{} - {}'.format(self.logger_name, text)

    def log(self, severity, *args, **kwargs):
        if self.logger.isEnableFor(severity):
            log = self.logger.log
            log(severity, self.annotate(' '.join(args)), **kwargs)

    def is_enabled_for(self, level):
        return self.logger.isEnabledFor(level)

    def get_logger(self):
        return get_logger(self.logger_name)

    @property
    def logger(self):
        return self.get_logger()

    @property
    def logger_name(self):
        return self.__class__.__name__


class Log(LogMixin):
    def __init__(self, name, logger=None):
        self._logger_name = name
        self._logger = logger

    def get_logger(self):
        if self._logger:
            return self._logger
        return LogMixin.get_logger(self)

    @property
    def logger_name(self):
        return self._logger_name


def setup_logging(logname=None, loglevel=None, logfile=None):
    logger = logging.getLogger(logname)
    loglevel = get_loglevel(loglevel or 'ERROR')
    logfile = logfile if logfile else sys.__stderr__

    if not logger.handlers:
        if hasattr(logfile, 'write'):
            handler = RotatingFileHandler(logfile,
                                          maxBytes=10000,
                                          backupCount=1)
        else:
            handler = WatchedFileHandler(logfile)

        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]')
        handler.setFormatter(formatter)
        logger.setLevel(loglevel)
        logger.addHandler(handler)
    return logger


def configure_log(app, loglevel=None, logfile=None):
    loglevel = get_loglevel(loglevel or 'ERROR')
    logfile = logfile if logfile else sys.__stderr__
    if hasattr(logfile, 'write'):
        handler = RotatingFileHandler(logfile,
                                      maxBytes=10000,
                                      backupCount=1)

    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]')
    handler.setFormatter(formatter)
    app.logger.setLevel(loglevel)
    app.logger.addHandler(handler)

    get_logger('werkzeug').addHandler(handler)

    # email error to the administrators
    # TODO: email error log
    # mail_handler = MailgunHandler()
    # mail_handler.setLevel(logging.ERROR)
    # app.logger.addHandler(mail_handler)
