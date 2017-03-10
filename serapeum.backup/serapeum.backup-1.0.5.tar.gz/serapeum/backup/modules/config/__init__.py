import configparser
from os.path import isfile


class Config:
    def __init__(self, config_file=None):
        if config_file is None:
            config_file = 'config/config.ini'
        if not isfile(config_file):
            raise Exception('Error: failed to parse configuration file: {0} not found!'.format(config_file))
        try:
            self.config = configparser.ConfigParser()
            self.config.read(config_file)
        except configparser.ParsingError as e:
            raise Exception('Error: failed to parse configuration file: parsing error: {0}'.format(e))
