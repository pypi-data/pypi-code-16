import logging
import os
from customlogger.run_rotating_handler import RunRotatingHandler


class OnlyFilter(object):
    def __init__(self, level):
        self.__level = level

    def filter(self, log_record):
        return log_record.levelno == self.__level


class CustomLogger:
    NOTSET = logging.NOTSET
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    LOG_FILE_PATH = 'all.log'
    LOG_DIR_PATH = './log'
    DEFAULT_STREAM_LEVEL = WARNING
    IS_SAVE_LOG = True

    LOGGER_LISTS = []

    @classmethod
    def debugMode(cls):
        cls.DEFAULT_STREAM_LEVEL = CustomLogger.DEBUG

    @classmethod
    def setDefaultStreamLevel(cls, level):
        cls.DEFAULT_STREAM_LEVEL = level

    @classmethod
    def saveLog(cls):
        cls.IS_SAVE_LOG = True

    @classmethod
    def setLogDirPath(cls, path):
        cls.LOG_DIR_PATH = path

    @classmethod
    def setLogFileName(cls, filename):
        cls.LOG_FILE_PATH = filename

    def checkLoggerLists(self, logger):
        id_ = id(logger)
        if id_ in CustomLogger.LOGGER_LISTS:
            return True

        CustomLogger.LOGGER_LISTS.append(id_)
        return False

    def __init__(self, parent=None, logger_name=None, default=True):
        name = parent or self
        name = logger_name or name
        logger = logging.getLogger(type(name).__name__)
        self.__logger = logger
        if self.checkLoggerLists(logger):
            return

        logger.setLevel(CustomLogger.DEBUG)

        self.createLogDir()
        if default:
            fmt = '[%(levelname)s: File "%(filename)s", line %(lineno)s, in %(funcName)s] "%(message)s"'
            self.addStreamHandler(CustomLogger.DEFAULT_STREAM_LEVEL, fmt=fmt)
            self.addStreamHandler(
                CustomLogger.INFO, is_only=True, check_level=True)
            if CustomLogger.IS_SAVE_LOG:
                self.addFileHandler(CustomLogger.DEBUG)
                self.addRunRotatingHandler(CustomLogger.DEBUG, 5)

    @property
    def logger(self):
        return self.__logger

    def createLogDir(self, path=None):
        path = path or CustomLogger.LOG_DIR_PATH
        if os.path.isdir(path):
            return

        os.mkdir(path)
        print('Create log directory. ({})'.format(os.path.abspath(path)))

    def addStreamHandler(self,
                         level,
                         fmt=None,
                         is_only=False,
                         check_level=False):
        if check_level:
            if CustomLogger.DEFAULT_STREAM_LEVEL <= level:
                return
        handler = logging.StreamHandler()
        self.addHandler(handler, level, fmt, is_only)

    def addHandler(self, handler, level, fmt=None, datefmt=None,
                   is_only=False):
        # set handler level
        handler.setLevel(level)

        # set format
        datefmt = datefmt or '%Y-%m-%d %a %H:%M:%S'
        handler.setFormatter(logging.Formatter(fmt, datefmt))

        # set only filter
        if is_only is True:
            handler.addFilter(OnlyFilter(level))

        self.__logger.addHandler(handler)

    def addFileHandler(self, level, out_path=None, fmt=None, is_only=False):
        out_path = out_path or os.path.join(CustomLogger.LOG_DIR_PATH,
                                            CustomLogger.LOG_FILE_PATH)
        handler = logging.FileHandler(out_path)
        fmt = fmt or '%(asctime)s %(filename)s %(name)s %(lineno)s %(levelname)s "%(message)s"'
        self.addHandler(handler, level, fmt, is_only)

    def addRotatingFileHandler(self,
                               level,
                               out_path,
                               max_bytes,
                               backup_count,
                               fmt=None,
                               is_only=False):
        handler = logging.handlers.RotatingFileHandler(
            filename=out_path, maxBytes=max_bytes, backupCount=backup_count)
        fmt = fmt or '%(asctime)s %(filename)s %(name)s %(lineno)s %(levelname)s "%(message)s"'
        self.addHandler(handler, level, fmt, is_only)

    def addRunRotatingHandler(self,
                              level,
                              backup_count,
                              out_path=None,
                              fmt=None,
                              is_only=False):
        out_path = out_path or CustomLogger.LOG_DIR_PATH
        handler = RunRotatingHandler(out_path, backup_count)
        fmt = fmt or '%(asctime)s %(filename)s %(name)s %(lineno)s %(levelname)s "%(message)s"'
        self.addHandler(handler, level, fmt, is_only)

    def setLevel(self, level):
        self.__loger.setLevel(level)


if __name__ == '__main__':
    CustomLogger.LOG_DIR_PATH = './log'
    CustomLogger.DEFAULT_STREAM_LEVEL = CustomLogger.DEBUG
    # CustomLogger.IS_SAVE_LOG = True
    logger = CustomLogger()
    logger = logger.logger
    logger.debug('debug test')
    logger.info('info test')
    logger.warning('warning test')
    logger1 = CustomLogger(logger_name='logger name').logger
    logger1.info('info test2')
