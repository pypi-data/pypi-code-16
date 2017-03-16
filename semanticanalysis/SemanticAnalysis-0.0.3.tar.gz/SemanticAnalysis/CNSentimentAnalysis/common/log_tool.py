#!/usr/bin/python

import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='/tmp/log_file.log',
                    filemode='a')

class Logging(object):
    @staticmethod
    def get_logger():
        return logging
