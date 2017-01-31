import logging
# from logging.handlers import RotatingFileHandler
from logging.handlers import SysLogHandler


FORMAT_STRING = "[%(asctime)s-%(levelname)5s-%(filename)20s:%(lineno)3s  %(message)s"


def get_logger(logger_name, verbose=True):
    logger = logging.getLogger(name=logger_name)
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    # create a rolling file handler
    try:
        # handler = RotatingFileHandler(output_file, mode='a',
        #                               maxBytes=1024*1024*10, backupCount=10)
        # Use stdout/stderr as the logging facility in the docker environment for centralized logging.
        handler = logging.StreamHandler()
    except:
        handler = SysLogHandler()

    handler.setFormatter(logging.Formatter("[%(asctime)s -%(levelname)5s- %(filename)20s:%(lineno)3s]    %(message)s"))
    logger.addHandler(handler)

    return logger


def set_logging_level(logger_obj, verbose):
    if verbose:
        logger_obj .setLevel(logging.DEBUG)
    else:
        logger_obj.setLevel(logging.INFO)
