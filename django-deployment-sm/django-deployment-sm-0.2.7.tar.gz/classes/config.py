import json
import os

from classes.exceptions import DeploymentException
from .config_item import ConfigItem


class Config(object):
    """
    The Config object reads the config json named: "django-deploy.json" in the current working directory
    and initializes the config_item objects

    """
    CONFIG_JSON = 'django-deploy.json'
    CURRENT_WORKING_DIR = os.getcwd()
    CONFIG_FILE_PATH = os.path.join(CURRENT_WORKING_DIR, CONFIG_JSON)

    def __init__(self, config_file_path):
        self.config_file_path = config_file_path
        self.config_items = self.init_config_items()

    def config_item(self, deployment_type):
        """
        Searches a config item in the given config file

        :param deployment_type: the deployment type to search for
        :return: the found config item
        :rtype: ConfigItem
        """
        if deployment_type in self.config_items:
            return self.config_items[deployment_type]
        else:
            raise DeploymentException(
                'The deployment type in your django-deploy.json: {} was not found!\n'
                'Please read the docs to edit your django-deploy.json'.format(deployment_type)
            )

    def init_config_items(self):
        config_file = self.read_config_file(self.config_file_path)
        config_items = {}
        for key, values in config_file.items():
            config_items[key] = ConfigItem(key, values)
        return config_items

    def read_config_file(self, config_file_path=None):
        """
        :param config_file_path: the path of the config json
        :return: config_dictionary
        :rtype: dict
        """
        if not config_file_path:
            config_file_path = self.CONFIG_FILE_PATH
        try:
            return json.load(open(config_file_path))
        except Exception as exception:
            raise DeploymentException(str(exception))
