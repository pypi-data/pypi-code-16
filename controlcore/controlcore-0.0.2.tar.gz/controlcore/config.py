import os
import copy
import configparser

AMQP_SECTION = "AMQP"

class Config(object):
    def __init__(self, configfile=None):
        config = configparser.ConfigParser()
        config.read(configfile)
        config_vars = dict()

        for option in config.options(AMQP_SECTION):
            config_vars[option] = config.get(AMQP_SECTION, option)

        for key, value in config_vars.items():
            setattr(self, key, value)
