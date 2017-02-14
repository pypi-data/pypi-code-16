import os
import json
import configparser

from bucketlist.errors import BucketlistError


PROVIDER_CONFIGS = {
    'wunderlist': ['access-token', 'folder-name', 'client-id'],
    'localfs': ['data-dir']
}

VALID_CONFIGS = {
    'provider': ['name'],
    'io': ['mode'],
    'logging': ['level', 'file']
}

def get_provider_config(provider_name):
    return PROVIDER_CONFIGS.get(provider_name)

def get_supported_providers():
    return PROVIDER_CONFIGS.keys()

def get_general_config():
    return VALID_CONFIGS


class Config:
    folder_name = '.bucket-list'
    config_filename = 'config'

    def __init__(self):
        self.config_folder_path = os.path.join(os.environ.get('HOME'),
                                               Config.folder_name)
        self.config_filepath = os.path.join(self.config_folder_path,
                                            Config.config_filename)

        self.allconfig = configparser.ConfigParser()
        self.allconfig.read(self.config_filepath)


    def save_config(self):
        with open(self.config_filepath, 'w') as config_file:
            self.allconfig.write(config_file)

    def config_exists(self):
        return os.path.exists(self.config_filepath)

    def get_provider_name(self):
        try:
            return self.allconfig.get('provider', 'name')
        except configparser.NoSectionError as e:
            raise BucketlistError("No provider set.", error_code="no_provider")
        except configparser.NoOptionError as e:
            raise BucketlistError("No provider set.", error_code="no_provider")

    def section_exists(self, section_name):
        return section_name in self.allconfig.sections()

    def create_section(self, section_name):
        self.allconfig.add_section(section_name)
        self.save_config()

    def delete_section(self, section_name):
        if not self.section_exists(section_name):
            return
        self.allconfig.remove_section(section_name)
        self.save_config()

    def _put_config_in_section(self, section_name, config_name, value):
        self.allconfig.set(section_name, config_name, value)
        self.save_config()

    def _get_config_value_for_section(self, section_name, config_name):
        try:
            return self.allconfig.get(section_name, config_name)
        except configparser.NoSectionError as e:
            return None
        except configparser.NoOptionError as e:
            return None

    def get_all(self, section_name):
        if not self.section_exists(section_name):
            return {}
        return {x[0]: x[1] for x in self.allconfig.items(section_name)}

    def validate(self, section_name, config_name):
        if section_name != 'provider_config':
            if section_name not in get_general_config():
                raise BucketlistError("Invalid config {}".format(section_name))

            if config_name not in get_general_config()[section_name]:
                raise BucketlistError("Invalid config {} under {}".format(config_name, section_name))

        if section_name == 'provider_config':
            provider_name = self.get_provider_name()
            provider_config = get_provider_config(provider_name)

            if provider_config and config_name not in provider_config:
                raise BucketlistError("Invalid config {} under {}".format(config_name, section_name))

    def init(self, provider_name):
        if not os.path.exists(self.config_folder_path):
            os.makedirs(self.config_folder_path)

        if provider_name not in get_supported_providers():
            raise BucketlistError("Unsupported provider {}".format(provider_name))

        for section_name, config_names in get_general_config().items():
            for config_name in config_names:
                self.put(section_name, config_name, '')

        self.put('provider', 'name', provider_name)
        self.put('io', 'mode', 'interactive')
        self.put('logging', 'level', 'error')
        self.put('logging', 'file', os.path.join(self.config_folder_path, 'bucketlist.log'))


    def put(self, section_name, config_name, value):
        """It creates section with name = section_name if not exists and sets
        config in it.
        """
        if not self.section_exists(section_name):
            self.create_section(section_name)
        self.validate(section_name, config_name)
        self._put_config_in_section(section_name, config_name, value)


    def get(self, section_name, config_name):
        """Returns the config value and if section_name or config_name
        does not exist, return None.

        It silently absorbs any errors whatsoever
        """
        self.validate(section_name, config_name)
        return self._get_config_value_for_section(section_name, config_name)
