import configparser
import os

class Config(object):
  config_key = "BARCODE_SCANNER"
  def __init__(self, path_to_config_file):
    self.config = configparser.ConfigParser()
    self.config[self.config_key] = {'push_url': 'http://localhost:8000/dummy_endpoint'}
    if not os.path.isfile(path_to_config_file):
      with open(path_to_config_file, 'w') as configfile:
        self.config.write(configfile)

    self.config.read(path_to_config_file)

  def push_url(self):
    self.config[self.config_key].get("push_url")

