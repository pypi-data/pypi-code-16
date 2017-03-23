import os
import configparser

from climb.exceptions import ConfigNotFound

DEFAULT_CONFIG_PATHS = [
    './{name}.conf',
    '~/.{name}.conf',
    '/etc/{name}/{name}.conf',
]

config = configparser.ConfigParser()


def load_config(name):
    config.clear()

    paths = [path.format(name=name) for path in DEFAULT_CONFIG_PATHS]
    for config_path in paths:
        if _read_config(config_path):
            break
    else:
        raise ConfigNotFound("Could not find {name}.conf".format(name))


def load_config_file(path):
    config.clear()

    if not _read_config(path):
        raise ConfigNotFound("Could not load {}".format(path))


def _read_config(path):
    config_path = os.path.expanduser(path)
    if os.path.isfile(config_path) and os.access(config_path, os.R_OK):
        config.read(config_path)
        return True
    else:
        return False
