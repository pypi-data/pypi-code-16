"""Lumberjack - Logging for Humans."""
__author__ = "Santosh Venkatraman<santosh.venk@gmail.com>"
__all__ = ("Lumberjack",)
import sys
sys.dont_write_bytecode = True
from os import getcwd, path, mkdir, makedirs
import logging
from time import strftime, gmtime


class Lumberjack():
    """Lumberjack - Logger class for humans"""
    default_level_number = 999
    default_level = logging.DEBUG
    default_name = "Lumberjack"
    default_format = " - ".join([
        "%(asctime)s",
        "%(name)s",
        "%(levelname)s",
        "%(message)s"
    ])
    default_file_name = "lumberjack.log"
    default_timestamp_format = "%Y%m%d-%H%M%S"
    valid_handlers = ("file", "console")

    def __init__(self, *args, **kwargs):
        """
        Logging for humans
        :param name            : Logger name
        :type  name            : basestring
        :param level           : Logging level
        :type  level           : basestring
        :param format          : Logging format
        :type  format          : basestring
        :param handler_type    : Logger handler type
        :type  handler_type    : basestring
        :param file_name       : Logger file name
        :type  file_name       : basestring, NoneType
        :param timestamp_based : Flag for file name being timestamp based
        :type  timestamp_based : bool
        :param timestamp_format: Timestamp format for log filename
        :type  timestamp_format: basestring
        """
        self.name = kwargs.get("name", self.default_name) 
        self.logger = logging.getLogger(self.name)
        level = kwargs.get("level")
        if level == "info":
            self.level = logging.INFO
        else:
            self.level = self.default_level
        self.logger.setLevel(self.level)
        handler_type = kwargs.get("handler_type", "file")

        if handler_type == "file":
            file_name = kwargs.get("file_name", self.name)
            self.check_file_path(file_name)
            timestamp_based = kwargs.get("timestamp_based", True)
            if timestamp_based:
                timestamp_format = \
                    kwargs.get("timestamp_format",
                               self.default_timestamp_format)
                file_name = file_name.rstrip(".log")
                file_name = "{}_{}.log".format(
                    file_name,
                    strftime(timestamp_format)
                )
            self.handler = logging.FileHandler(file_name)
            self.handler.setLevel(self.level)
        else:
            self.handler = logging.StreamHandler()

        logging_format = kwargs.get("format", self.default_format)
        logging.Formatter.converter = gmtime
        self.formatter = \
            logging.Formatter(logging_format)
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)


    def check_file_path(self, file_name):
        """
        Checks if given file_name is valid or not.
        Creates director(y/ies) if absent.
        """
        if "/" not in file_name:
            return file_name

        dir_name = "/".join(file_name.split("/")[:-1])

        if path.exists(dir_name):
            return file_name

        if not dir_name.startswith("/"):
            dir_name = path.join(getcwd(), dir_name)

        if dir_name.count("/") > 1:
            makedirs(dir_name)
        else:
            mkdir(dir_name)

        return file_name

    def info(self, message):
        """
        Function to log information messages.
        :param message: Log information message
        :type  message: basestring
        """
        assert isinstance(message, basestring)
        self.logger.info(message)

    def log(self, *args):
        """
        Function to log messages.
        :param level  : Logging level
        :type  level  : int, NoneType
        :param message: Log information message
        :type  message: basestring
        """
        assert len(args) >= 1, "Message needs to be passed"
        if len(args) == 1:
            level = self.default_level_number 
            message, = args
        else:
            level, message = args
        assert isinstance(message, basestring)
        assert isinstance(level, int)
        self.logger.log(level, message)

    def critical(self, *args, **kwargs):
        raise NotImplementedError()

    def debug(self, message):
        """
        Function to log debug messages.
        :param message: Log debug message
        :type  message: basestring
        """
        assert isinstance(message, basestring)
        self.logger.debug(message)

    def error(self, *args, **kwargs):
        raise NotImplementedError()

    def exception(self, *args, **kwargs):
        raise NotImplementedError()

    def warn(self, *args, **kwargs):
        raise NotImplementedError()
