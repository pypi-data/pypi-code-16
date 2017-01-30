import json
import logging
from logging.config import dictConfig
import os


def load_environment_variable(key, default=None):
    """
    Retrieves env vars and makes Python boolean replacements
    """
    val = os.getenv(key, default)
    if isinstance(val, str) and val.lower() == 'true':
        return True
    elif isinstance(val, str) and val.lower() == 'false':
        return False
    return val


SERENYTICS_API_DOMAIN = load_environment_variable('SERENYTICS_API_DOMAIN', 'https://api.serenytics.com')


def enable_log(log_level=logging.INFO):
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '%(asctime)s [%(levelname)s] %(message)s',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            },
        },
        'loggers': {
            'requests.packages.urllib3': {
                'level': logging.WARNING
            },
            'paramiko': {
                'level': logging.WARNING
            },
        },
        'root': {
            'handlers': ['console'],
            'level': log_level,
        },
    }
    dictConfig(config)


def __get_script_params():
    """
    :return: dict containing params passed to the script
    """
    try:
        with open('params.json') as params_file:
            params = json.load(params_file)
        return params
    except IOError:
        return {}


script_params = __get_script_params()
