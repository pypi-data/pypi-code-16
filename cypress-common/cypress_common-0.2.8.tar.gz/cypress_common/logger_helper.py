import logging
# from logging.handlers import RotatingFileHandler
from logging.handlers import SysLogHandler


FORMAT_STRING = "[%(asctime)s-%(levelname)5s-%(filename)20s:%(lineno)3s  %(message)s"


def get_logger(logger_name, verbose=False):
    logger = logging.getLogger(name=logger_name)

    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    if len(logger.handlers) == 0:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("[%(asctime)s -%(levelname)5s- %(filename)20s:%(lineno)3s]  %(message)s"))
        logger.addHandler(handler)

    # create a rolling file handler
    # handler = RotatingFileHandler(output_file, mode='a',
    #                               maxBytes=1024*1024*10, backupCount=10)
    # Use stdout/stderr as the logging facility in the docker environment for centralized logging.
    return logger


def set_logging_level(logger_obj, verbose):
    logger_obj.setLevel(logging.DEBUG if verbose else logging.INFO)
