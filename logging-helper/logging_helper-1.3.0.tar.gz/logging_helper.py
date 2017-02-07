#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import codecs
import datetime
from logging import *
from getpass import getuser
from types import MethodType
from tempfile import gettempdir
from inspect import stack, getmodule

u"""
set_up_basic_logging function configures the log file
to use and the logging level.

The global 'logging_file' is used to prevent the config
being set more than once.
"""

__author__ = u'Oli Davis & Hywel Thomas'
__copyright__ = u'Copyright (C) 2016 Oli Davis & Hywel Thomas'

LOG_FOLDER_PATH = gettempdir()
LOG_FOLDER_NAME = u'logs'


# Setup logger for this helper (note will log out to whatever you setup).
logging_handler_logger = getLogger(__name__)


# Basic Helper Functions

def ensure_path_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)


def get_logging_root_path_config():
        with codecs.open(TEMP_PATH_CONFIG_FILE, encoding=u'UTF8') as f:
            return f.read().strip()


def write_logging_root_path_user_config():

        ensure_path_exists(USER_CONFIG_PATH)

        logging_handler_logger.info(u'Initialising TEMP_PATH_CONFIG_FILE.')

        with codecs.open(TEMP_PATH_CONFIG_FILE, encoding=u'UTF8', mode=u'w') as f:
            f.write(u"Change this to a path if you want 'temp' to "
                    u"be somewhere else. e.g. C:/Users/{user}".format(user=getuser()))


def get_logging_root_path_text():
    try:
        path = get_logging_root_path_config()

        if not os.path.isdir(path):
            raise ValueError(u'{path} not found.'.format(path=path))

    except IOError as err:
        if __name__ == u'__main__':
            exception(err)

        path = os.path.normpath(os.path.dirname(__file__)).split(u'Libraries{sep}Utilities'.format(sep=os.sep))[0]
        write_logging_root_path_user_config()

    except ValueError:
        path = os.path.normpath(os.path.dirname(__file__)).split(u'Libraries{sep}Utilities'.format(sep=os.sep))[0]

    return path


# Setup Parameters
BASE_CONFIG_PATH = u'{int_test_tools}{sep}config{sep}'\
                      .format(int_test_tools=os.sep.join(os.path.normpath(__file__).split(os.sep)[:-3]),
                              sep=os.sep)

USER_BASE_CONFIG_PATH = u'{root}user_config{sep}'.format(root=BASE_CONFIG_PATH,
                                                         sep=os.sep)

USER_CONFIG_PATH = u'{root}{username}{sep}'.format(root=USER_BASE_CONFIG_PATH,
                                                   sep=os.sep,
                                                   username=getuser())

TEMP_PATH_CONFIG_FILENAME = u'Temp_Path.txt'

TEMP_PATH_CONFIG_FILE = u'{user_folder}{filename}'.format(sep=os.sep,
                                                          user_folder=USER_CONFIG_PATH,
                                                          filename=TEMP_PATH_CONFIG_FILENAME)


# Logging Helper Functions

def setup_log_format(date_format=u'%Y-%m-%d %H:%M:%S'):

    # Setup formatter to define format of log messages
    format_string = u'{timestamp} - {level} - {name} : {msg}'.format(timestamp=u'%(asctime)s',
                                                                     level=u'%(levelname)-7s',
                                                                     name=u'%(name)-45s',
                                                                     msg=u'%(message)s')

    log_formatter = Formatter(fmt=format_string,
                              datefmt=date_format)

    return log_formatter


def check_for_main():

    name = get_caller_name(level=3)
    logging_handler_logger.debug(u'Check Main: {c}'.format(c=name))

    return name == u'__main__' or name.endswith(u'__main__')


def get_caller_filename(level=2):

    path = stack()[level][1]
    filename = path.split(u'/')[-1]
    filename = filename.replace(u'.py', u'')

    logging_handler_logger.debug(u'Caller Filename: {c}'.format(c=filename))

    return filename


def get_caller_name(level=2):

    frame = stack()[level][0]
    module = getmodule(frame)

    if module is None:
        name = None

        if frame.f_locals is not None:
            name = frame.f_locals.get(u'__name__')

        if name is None:
            name = u'Cannot get __name__, filename: {fn}'.format(fn=get_caller_filename(level=3))

    else:
        name = module.__name__

    logging_handler_logger.debug(u'Caller Name: {c}'.format(c=name))

    return name


# New logger methods (these are added to the logger in setup_logging function

def __lh_setup_file_handler(self,
                            filename,
                            level=NOTSET):

    if self.LH_FILE_HANDLER is None:
        logging_file = filename
        sub_folder = u'Root_logger' if logging_file in (u'', u'__main__') else logging_file

        log_folder = u'{p}{sep}{d}'.format(p=LOG_FOLDER_PATH,
                                           sep=os.sep,
                                           d=LOG_FOLDER_NAME)

        folder = u'{logs_folder}{sep}{sub_folder}{sep}'.format(logs_folder=log_folder,
                                                               sub_folder=sub_folder,
                                                               sep=os.sep)

        ensure_path_exists(folder)

        filepath = u'{folder}{date} {filename}.log'.format(folder=folder,
                                                           date=datetime.datetime.now().strftime(u'%Y-%m-%d %H%M%S'),
                                                           filename=logging_file)

        self.LH_FILE_HANDLER = FileHandler(filename=filepath, encoding=u'UTF8')
        self.LH_FILE_HANDLER.setFormatter(setup_log_format())
        self.LH_FILE_HANDLER.setLevel(level=level)

        self.addHandler(self.LH_FILE_HANDLER)
        logging_handler_logger.info(u'Logging to file: {filepath}'.format(filepath=self.LH_FILE_HANDLER.baseFilename))

    else:
        logging_handler_logger.warning(u'Not setting up file handler, handler already setup')


def __lh_setup_console_handler(self,
                               level=NOTSET):

    if self.LH_CONSOLE_HANDLER is None:
        self.LH_CONSOLE_HANDLER = StreamHandler()
        self.LH_CONSOLE_HANDLER.setFormatter(setup_log_format())
        self.LH_CONSOLE_HANDLER.setLevel(level=level)

        self.addHandler(self.LH_CONSOLE_HANDLER)
        logging_handler_logger.info(u'Logging to console')

    else:
        logging_handler_logger.warning(u'Not setting up console handler, handler already setup for logger')


def __lh_set_file_level(self,
                        level):
    self.LH_FILE_HANDLER.setLevel(level)


def __lh_set_console_level(self,
                          level):
    self.LH_CONSOLE_HANDLER.setLevel(level)


def __lh_setLevel(self,
                  level,
                  handler=None):

    if handler is not None:
        handler.setLevel(level)

    else:
        self._oldSetLevel(level)


# Logging setup function - use this to setup logging in your modules

def setup_logging(logger_name=None,
                  level=NOTSET,
                  log_to_file=True,
                  log_to_console=True):

    """
    Eases setup of logging to file and console

    @param logger_name:         Name of logger.  This will also be used for file/folder name
                                DEFAULT: name of calling module
    @param level:               Log level to be used.
                                DEFAULT: logging.NOTSET
    @param log_to_file:         Enable/Disable logging to file.
                                DEFAULT: True
    @param log_to_console:      Enable/Disable logging to console.
                                DEFAULT: True
    @return:                    Returns the configured logger.
    """

    if not logger_name:
        logger_name = get_caller_name()

    # Get the logger
    if logger_name == u'__main__' or check_for_main():

        if logger_name == u'__main__':
            logger_name = u'Root Logger'

        logger = getLogger()
        logger.setLevel(NOTSET)  # Root logger level is set for individual handlers

        logger.name = logger_name
        setup_handlers = True

    else:
        logger = getLogger(logger_name)
        logger.setLevel(level)  # Non-root loggers can set their own level (this will be limited by the root logger)
        setup_handlers = False

    # Setup handler attributes & methods
    if not hasattr(logger, u'LH_CONSOLE_HANDLER'):
        logger.LH_CONSOLE_HANDLER = None

    if not hasattr(logger, u'LH_FILE_HANDLER'):
        logger.LH_FILE_HANDLER = None

    if u'lh_setup_console_handler' not in dir(logger):
        logger.lh_setup_console_handler = MethodType(__lh_setup_console_handler, logger, logger.__class__)

    if u'lh_setup_file_handler' not in dir(logger):
        logger.lh_setup_file_handler = MethodType(__lh_setup_file_handler, logger, logger.__class__)

    if u'__lh_set_console_level' not in dir(logger):
        logger.lh_set_console_level = MethodType(__lh_set_console_level, logger, logger.__class__)

    if u'__lh_set_file_level' not in dir(logger):
        logger.lh_set_file_level = MethodType(__lh_set_file_level, logger, logger.__class__)

    logger._oldSetLevel = logger.setLevel
    logger.setLevel = MethodType(__lh_setLevel, logger, logger.__class__)

    if setup_handlers:
        if log_to_console:
            logger.lh_setup_console_handler(level=level if log_to_console is True else log_to_console)

        if log_to_file:
            logger.lh_setup_file_handler(filename=logger_name,
                                         level=level if log_to_file is True else log_to_file)

    return logger


if __name__ == u'__main__':
    logtest = setup_logging(logger_name=u'TESTING HELPER', level=DEBUG, log_to_file=False)
    logtest.debug(u'Test log message 1')
    logtest.lh_set_console_level(INFO)
    logtest.debug(u'Test log message 2')  # This message should not display
    logtest.lh_set_console_level(DEBUG)
    logtest.debug(u'Test log message 3')
    logtest.setLevel(INFO, logtest.LH_CONSOLE_HANDLER)  # this is the same as logtest.lh_set_console_level(INFO)
    logtest.debug(u'Test log message 4')  # This message should not display
    logtest.setLevel(DEBUG, logtest.LH_CONSOLE_HANDLER)  # this is the same as logtest.lh_set_console_level(DEBUG)
    logtest.debug(u'Test log message 5')
    logtest.setLevel(WARN)  # This sets the root logger level
    logtest.debug(u'Test log message 6')  # This message should not display
