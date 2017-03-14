#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2016 TUNE, Inc. (http://www.tune.com)
#  @namespace logging_mv_integrations

import logging
from .logging_format import (TuneLoggingFormat)
from .logging_json_formatter import (LoggingJsonFormatter)
from .logging_standard_formatter import (LoggingStandardFormatter)
from logging_mv_integrations.support import (Singleton)


class TuneLoggingHandler(metaclass=Singleton):

    __log_formatter = None
    __log_handler = None

    def add_logger_version(self, logger_name, logger_version):
        if hasattr(self.log_formatter, 'add_logger_version'):
            self.log_formatter.add_logger_version(logger_name, logger_version)

    @property
    def log_formatter(self):
        # print('TuneLoggingHandler', 'log_formatter.getter', type(self.__log_formatter).__name__,
        #       id(self.__log_formatter))
        return self.__log_formatter

    @log_formatter.setter
    def log_formatter(self, value):
        # print('TuneLoggingHandler', 'log_formatter.setter', type(value).__name__, id(value))
        self.__log_formatter = value

    @property
    def log_handler(self):
        # print('TuneLoggingHandler', 'log_handler.getter', type(self.__log_handler).__name__, id(self.__log_handler))
        return self.__log_handler

    @log_handler.setter
    def log_handler(self, value):
        # print('TuneLoggingHandler', 'log_handler.setter', type(value).__name__, id(value))
        self.__log_handler = value

    def __init__(self, logger_name, logger_version, logger_format):
        self.log_formatter = self.get_logger_formatter(
            logger_name=logger_name, logger_version=logger_version, logger_format=logger_format
        )

        self.log_handler = logging.StreamHandler()
        self.log_handler.setFormatter(self.log_formatter)

    @staticmethod
    def get_logger_formatter(logger_name, logger_version, logger_format):
        if not TuneLoggingFormat.validate(logger_format):
            raise ValueError("Invalid 'logger_format': '{}'".format(logger_format))

        if logger_format == TuneLoggingFormat.JSON:
            log_formatter = LoggingJsonFormatter(
                logger_name,
                logger_version,
                fmt=(
                    "%(asctime)s "
                    "%(levelname)s "
                    "%(name)s "
                    "%(version)s "
                    # "%(mvi_name)s "
                    # "%(mvi_version)s "
                    # "%(memory_used)s "
                    "%(message)s"
                )
            )
        elif logger_format == TuneLoggingFormat.STANDARD:
            log_formatter = LoggingStandardFormatter(
                fmt=(
                    "%(asctime)-30s "
                    "%(levelname)-8s "
                    "%(name)-12s "
                    # "%(version)-7s "
                    # "'%(mvi_name)s' "
                    # "%(mvi_version)-3s "
                    # "[%(memory_used)9s] "
                    "'%(message)s'"
                )
            )

        return log_formatter


def get_tune_logger_with_handler(logger_name, logger_version, logger_format, logger_level=logging.NOTSET, logger=None):
    if not logger_name:
        raise ValueError("Undefined 'logger_name'")
    if not logger_version:
        raise ValueError("Undefined 'logger_version'")
    if not logger_format:
        raise ValueError("Undefined 'logger_format'")

    if not TuneLoggingFormat.validate(logger_format):
        raise ValueError("Invalid 'logger_format': {}".format(logger_format))

    tune_loggin_handler = TuneLoggingHandler(
        logger_format=logger_format, logger_name=logger_name, logger_version=logger_version
    )

    tune_loggin_handler.add_logger_version(logger_name, logger_version)

    if logger_level == logging.NOTSET:
        logger_level = logging.INFO

    if logger is None:
        logger = logging.getLogger(logger_name)

    logger.addHandler(tune_loggin_handler.log_handler)
    logger.setLevel(level=logger_level)

    return logger
