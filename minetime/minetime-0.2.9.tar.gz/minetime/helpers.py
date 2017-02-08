# -*- coding: utf-8 -*-
import logging
import os
from datetime import datetime

import click
import yaml


def get_config():
    """read config from file and return python dictionnary"""

    config = False
    for loc in os.curdir, click.get_app_dir('minetime'), os.environ.get("MINETIME_CONF"):
        try:
            with open(os.path.join(loc, "config.yml")) as source:
                config = yaml.safe_load(source)
                if config:
                    if 'XXXXXX' in config['user']['api_key']:
                        continue
                    else:
                        return config
        except (IOError, AttributeError):
            pass

    # No config
    return False


def get_logger(debug=False):
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.ERROR)

    logger.debug('minetime ready : %s', 'time\'s on!')
    return logger


def day_between(start, end, day):
    return start <= day <= end
