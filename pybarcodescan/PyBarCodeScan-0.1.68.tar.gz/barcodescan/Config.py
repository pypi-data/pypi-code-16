import configparser
import os

class Config(object):
  config_key = "BARCODE_SCANNER"
  def __init__(self, path_to_config_file):
    self.config = configparser.ConfigParser()
    self.config["SERVER"] = {}
    self.config["READER"] = {'push_url': 'http://localhost:8000'}
    if not os.path.isfile(path_to_config_file):
      with open(path_to_config_file, 'w') as configfile:
        self.config.write(configfile)
    self.config.read(path_to_config_file, "UTF-8")

  def server_push_url(self):
    return self.config["SERVER"].get('push_url')

  def reader_push_url(self):
    return self.config["READER"].get('push_url')

