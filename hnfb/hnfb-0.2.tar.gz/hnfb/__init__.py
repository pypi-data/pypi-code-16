import logging
from logging.config import dictConfig 

logging_config = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'formatter': 'simple',
            'class': 'logging.StreamHandler'
        }
    },
    'loggers': {
        'hnfb': {
            'handlers': ['console'],
            'level': 'DEBUG'
        }
    }
}

dictConfig(logging_config)

from .main import HN, HNException, HNNotFoundException
