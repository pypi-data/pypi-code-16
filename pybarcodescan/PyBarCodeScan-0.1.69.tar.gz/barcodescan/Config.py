import configparser
import os
import logging

class Config(object):
  logger = logging.getLogger(__name__)

  def __init__(self, path_to_config_file):
    self.config = configparser.ConfigParser()
    self.config["SERVER"] = {}
    self.config["READER"] = {}
    if not os.path.isfile(path_to_config_file):
      self.logger.warning("no config file found under: {}".format(path_to_config_file))
    self.config.read(path_to_config_file, "UTF-8")

  def server_push_url(self):
    return self.config["SERVER"].get('push_url')

  def reader_push_url(self):
    return self.config["READER"].get('push_url')

