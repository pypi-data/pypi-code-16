import logging

from NucleusUtils.versions.deprecated import Deprecated
from . import decorators
from . import dumps

# TODO: remove this. Use logging.config.

handlers = []
log_level = logging.DEBUG


@Deprecated('Use logging configs')
def set_level(level):
    global log_level
    log_level = level


@Deprecated('Use logging configs')
def register_handler(handler):
    handlers.append(handler)


@Deprecated('Use logging configs')
def get_logger(name='app'):
    """
    Get logger with handlers
    :param name: logger name
    :return: logger
    """
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(log_level)

    log_handlers = []
    for handler in logger.handlers:
        log_handlers.append(handler.__class__)

    for handler in handlers:
        if handler.__class__ not in log_handlers:
            logger.addHandler(handler)

    return logger
