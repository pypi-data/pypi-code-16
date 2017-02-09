"""defaultlog.py - In a seperate module to prevent circular imports."""
from logging import getLogger
from logging.config import dictConfig

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '[%(levelname)s] %(name)s: %(message)s'
        }
    },
    'handlers': {
        'stdout': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'stream': 'ext://sys.stdout'
        },
        "syslog": {
            "class": "logging.handlers.SysLogHandler",
            'formatter': 'default',
            'address': '/dev/log'
        }
    },
    'loggers': {
        '': {
            'handlers': ['stdout', 'syslog'],
            'level': 'DEBUG',
            'propagate': True
        }
    }
}
dictConfig(LOGGING)
log = getLogger()
