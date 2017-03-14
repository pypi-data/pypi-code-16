#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2016 TUNE, Inc. (http://www.tune.com)
#  @namespace logging_mv_integrations
import logging

from logging_mv_integrations.errors import (print_traceback)
from logging_mv_integrations.support import (Singleton)
from .logging_format import (TuneLoggingFormat)
from .tune_logging_handler import (TuneLoggingHandler)


class TuneLogger(logging.Logger):
    def __init__(self, name, level):
        logging.Logger.__init__(self, name, level)


class TuneRootLogger(TuneLogger):
    def __init__(self, level):
        TuneLogger.__init__(self, name="root", level=level)


root = TuneRootLogger(logging.WARNING)
TuneLogger.root = root
TuneLogger.manager = logging.Manager(TuneLogger.root)


class _TuneLoggingBase(metaclass=Singleton):
    """TUNE Mv-Integration Logger

    """
    #  Logger
    #  @var object
    __logger = None

    #  Logger Handler
    #  @var str
    __logger_name = None

    #  Logger Level
    __logger_level = logging.NOTSET

    #  Maximum resident set size
    __ru_maxrss_start = None

    #  Tune Logging Format
    __logger_format = None

    #  Tune Logging Version
    __logger_version = None

    def __init__(
        self, logger_name, logger_version, logger_level=logging.NOTSET, logger_format=None, ru_maxrss_start=None
    ):
        # print('_TuneLoggingBase', '__init__')
        try:
            logging._checkLevel(logger_level)
        except ValueError as va_ex:
            print_traceback(va_ex)
            raise

        if logger_level == logging.NOTSET:
            logger_level = logging.INFO

        if logger_format is None:
            logger_format = TuneLoggingFormat.JSON

        self.logger_name = logger_name
        self.logger_level = logger_level
        self.logger_format = logger_format
        self.logger_version = logger_version

        self.ru_maxrss_start = ru_maxrss_start

    @property
    def ru_maxrss_start(self):
        return self.__ru_maxrss_start

    @ru_maxrss_start.setter
    def ru_maxrss_start(self, value):
        self.__ru_maxrss_start = value

    @property
    def logger(self):
        # print('_TuneLoggingBase', 'logger.getter', type(self.__logger).__name__, id(self.__logger))
        return self.__logger

    @logger.setter
    def logger(self, value):
        # print('_TuneLoggingBase', 'logger.setter', type(value).__name__, id(value))
        self.__logger = value

    @property
    def logger_name(self):
        return self.__logger_name

    @logger_name.setter
    def logger_name(self, value):
        self.__logger_name = value

    @property
    def logger_version(self):
        return self.__logger_version

    @logger_version.setter
    def logger_version(self, value):
        self.__logger_version = value

    @property
    def logger_level(self):
        return self.__logger_level

    @logger_level.setter
    def logger_level(self, value):
        self.__logger_level = value
        # if self.__logger:
        #     self.__logger.setLevel(value)

    @property
    def logger_format(self):
        return self.__logger_format

    @logger_format.setter
    def logger_format(self, value):
        self.__logger_format = value

    # Convert from string to logging level.
    #
    @staticmethod
    def get_logging_level(str_logging_level):
        """Convert from string to logging level.

        Args:
            str_logging_level:

        Returns:

        """
        assert str_logging_level
        str_logging_level = str_logging_level.upper()

        return {
            'NOTSET': logging.NOTSET,
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }.get(str_logging_level, logging.INFO)

    # Convert from logging level to string.
    #
    @staticmethod
    def get_str_logging_level(logging_level):
        """Convert from string to logging levels.

        Args:
            str_logging_level:

        Returns:

        """
        return {
            logging.NOTSET: 'NOTSET',
            logging.DEBUG: 'DEBUG',
            logging.INFO: 'INFO',
            logging.WARNING: 'WARNING',
            logging.ERROR: 'ERROR',
            logging.CRITICAL: 'CRITICAL'
        }.get(logging_level, None)

    def debug(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'DEBUG'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.debug("Houston, we have a %s", "thorny problem", exc_info=1)
        """
        if self.__logger.isEnabledFor(logging.DEBUG):
            logging_extra = {}

            if 'extra' in kwargs and kwargs['extra'] and len(kwargs['extra']) > 0:
                kwargs['extra'].update(logging_extra)
            else:
                kwargs['extra'] = logging_extra

            self.__logger._log(logging.DEBUG, msg, args, **kwargs)

    def info(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'INFO'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.info("Houston, we have a %s", "interesting problem", exc_info=1)
        """
        if self.__logger.isEnabledFor(logging.INFO):
            logging_extra = {}

            if 'extra' in kwargs and kwargs['extra'] and len(kwargs['extra']) > 0:
                kwargs['extra'].update(logging_extra)
            else:
                kwargs['extra'] = logging_extra

            self.__logger._log(logging.INFO, msg, args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'WARNING'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.warning("Houston, we have a %s", "bit of a problem", exc_info=1)
        """
        if self.__logger.isEnabledFor(logging.WARNING):
            logging_extra = {}

            if 'extra' in kwargs and kwargs['extra'] and len(kwargs['extra']) > 0:
                kwargs['extra'].update(logging_extra)
            else:
                kwargs['extra'] = logging_extra

            self.__logger._log(logging.WARNING, msg, args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'ERROR'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.error("Houston, we have a %s", "major problem", exc_info=1)
        """
        if self.__logger.isEnabledFor(logging.ERROR):
            logging_extra = {}

            if 'extra' in kwargs and kwargs['extra'] and len(kwargs['extra']) > 0:
                kwargs['extra'].update(logging_extra)
            else:
                kwargs['extra'] = logging_extra

            self.__logger._log(logging.ERROR, msg, args, **kwargs)

    def exception(self, msg, *args, exc_info=True, **kwargs):
        """
        Convenience method for logging an ERROR with exception information.
        """
        logging_extra = {}

        if 'extra' in kwargs and kwargs['extra'] and len(kwargs['extra']) > 0:
            kwargs['extra'].update(logging_extra)
        else:
            kwargs['extra'] = logging_extra

        self.error(msg, *args, exc_info=exc_info, **kwargs)

    def critical(self, msg, *args, **kwargs):
        """
        Log 'msg % args' with severity 'CRITICAL'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.critical("Houston, we have a %s", "major disaster", exc_info=1)
        """

        logging_extra = {}

        if 'extra' in kwargs and kwargs['extra'] and len(kwargs['extra']) > 0:
            kwargs['extra'].update(logging_extra)
        else:
            kwargs['extra'] = logging_extra

        if self.__logger.isEnabledFor(logging.CRITICAL):
            self.__logger._log(logging.CRITICAL, msg, args, **kwargs)


class TuneLogging(_TuneLoggingBase):
    def __init__(
        self,
        logger_level=logging.NOTSET,
        logger_format=None,
        logger_name=None,
        logger_version=None,
        ru_maxrss_start=None
    ):
        # print('TuneLogging', '__init__')

        super(TuneLogging, self).__init__(
            logger_level=logger_level,
            logger_format=logger_format,
            logger_name=logger_name,
            logger_version=logger_version,
            ru_maxrss_start=ru_maxrss_start
        )

        self.logger = self.create_logger()

    def get_logger(self, logger_name=None, logger_level=logging.NOTSET):
        # print('TuneLogging', 'get_logger')

        _logger_level = logging.WARNING
        if logger_level != logging.NOTSET:
            _logger_level = logger_level
        elif self.logger_level != logging.NOTSET:
            _logger_level = self.logger_level

        if logger_name is None:
            logger_name = self.logger_name

        # print('TuneLogging', 'get_logger', logger_name, _logger_level)
        _logger = None
        if logger_name:
            _logger = TuneLogger(name=logger_name, level=_logger_level)
        else:
            _logger = TuneRootLogger(level=_logger_level)

        # print('TuneLogging', 'get_logger', type(_logger).__name__, id(_logger))
        return _logger

    def create_logger(self):
        """Generate Logger

        Args:
            integration_name:
            logger_name:
            logger_level:

        Returns:

        """
        # print('TuneLogging', 'create_logger')
        logging._checkLevel(self.logger_level)

        if self.logger_level == logging.NOTSET:
            self.logger_level = logging.INFO

        logger = self.get_logger(logger_name=self.logger_name)

        if logger:
            tune_loggin_handler = TuneLoggingHandler(
                logger_name=self.logger_name, logger_version=self.logger_version, logger_format=self.logger_format
            )

            logger.addHandler(tune_loggin_handler.log_handler)

            logger.setLevel(level=self.logger_level)

        # print('TuneLogging', 'create_logger', type(logger).__name__, id(logging))

        return logger

    def setLevel(self, logger_level=logging.NOTSET):
        self.logger.setLevel(logger_level)
