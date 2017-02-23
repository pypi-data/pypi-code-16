# -*- coding: utf-8 -*-

import logging


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
)


def get_logger(name):

    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    return log

