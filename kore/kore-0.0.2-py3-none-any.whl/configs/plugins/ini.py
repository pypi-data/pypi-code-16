from os.path import isfile
from logging.config import fileConfig

from configparser import ConfigParser

from kore.configs.plugins.base import BasePluginConfig


class IniConfig(BasePluginConfig):

    def __init__(self, *args, **kwargs):
        try:
            ini_file = kwargs['ini_file']
        except KeyError:
            raise RuntimeError("`ini_file` not defined")

        if not isfile(ini_file):
            raise RuntimeError("`ini_file` not exists")

        ini_prefix = kwargs.get('ini_prefix', '')
        ini_logging = kwargs.get('ini_logging', False)
        ini_logging_disable_existing = kwargs.get(
            'ini_logging_disable_existing', True)

        if ini_logging:
            fileConfig(ini_file,
                       disable_existing_loggers=ini_logging_disable_existing)

        self.prefix = ini_prefix
        self.config_parser = ConfigParser()
        self.config_parser.read(ini_file)

    def __getitem__(self, key):
        return self.config_parser[self.prefix + key]
