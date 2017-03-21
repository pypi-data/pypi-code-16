#!/usr/bin/env python
# encoding: utf-8

import logging

class Logger(logging.getLoggerClass()):
    __YELLOW = '\033[0;33m%s\033[0m'
    __DARK_RED = '\033[0;41m%s\033[0m'
    __RED = '\033[0;31m%s\033[0m'
    __FORMAT = {
        'fmt': '%(asctime)s %(levelname)s: %(message)s',
        'datefmt': '%Y-%m-%d %H:%M:%S',
    }

    def __init__(self, format=__FORMAT, level=logging.INFO):
        formatter = logging.Formatter(**format)

        self.root.setLevel(level)
        self.root.handlers = []

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.root.addHandler(handler)

    def critical(self, message):
        self.root.critical(self.__DARK_RED,message)

    def error(self, message):
        self.root.error(self.__RED,message)

    def warn(self, message):
        self.root.warn(self.__YELLOW,message)

    def info(self, message):
        self.root.info(message)

    def debug(self, message):
        self.root.debug(message)

if __name__ == '__main__':
    logger = Logger(level=logging.DEBUG)
    logger.info("This message has default color.")
    logger.debug("This message has default color.")
