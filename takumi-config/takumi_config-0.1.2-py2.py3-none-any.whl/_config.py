# -*- coding: utf-8 -*-

import os
import yaml

from ._settings import Settings
from .utils import load_class

ENV_NAME = 'TAKUMI_ENV'
ENV_CONFIG_NAME = 'TAKUMI_APP_CONFIG_PATH'
DEFAULT_PATH = 'app.yaml'
DEFAULT_ENV = 'dev'

DEFAULT_THRIFT_WORKER_CONNECTIONS = 1000
DEFAULT_WORKER_TIMEOUT = 30  # seconds
DEFAULT_APP_PORT = 8010
DEFAULT_WORKER_NUMBER = 2
DEFAULT_CLIENT_TIMEOUT = 20 * 60  # seconds


def _load(path):
    with open(path) as f:
        return yaml.load(f)


class Config(object):
    """Load and store configs.
    """
    def __init__(self):
        self._path = path = os.getenv(ENV_CONFIG_NAME, DEFAULT_PATH)
        self._confs = _load(path)
        self.syslog_disabled = False
        self._settings = None

    def __repr__(self):
        return '<{} path={!r}>'.format(self.__class__.__name__, self._path)

    def __getattr__(self, attr):
        """Allow to get extra configs
        """
        return self._confs.get(attr)

    __getitem__ = __getattr__

    @property
    def env(self):
        """Get current runtime environment type

        This implementation gets env name from an environment vairable.

        Default: 'dev'
        """
        return os.getenv(ENV_NAME, DEFAULT_ENV)

    @property
    def settings(self):
        """Lazily create app settings
        """
        if self._settings is None:
            self._settings = Settings(self._confs['settings'])
        return self._settings

    @property
    def app(self):
        """Get app uri
        """
        return self._confs['app']

    @property
    def app_name(self):
        """Get application name
        """
        return self._confs['app_name']

    @property
    def thrift_file(self):
        """Get the full path of thrift file
        """
        thrift_file = self._confs['thrift_file']
        return os.path.join(os.getcwd(), thrift_file)

    @property
    def thrift_protocol_class(self):
        """Get thrift protocol class
        """
        cls_name = self._confs.get('thrift_protocol_class')
        if cls_name:
            return load_class(cls_name)

    @property
    def worker_connections(self):
        """Get gunicorn worker connections config
        """
        return self._confs.get('worker_connections',
                               DEFAULT_THRIFT_WORKER_CONNECTIONS)

    @property
    def workers(self):
        """Get worker numbers
        """
        return self._confs.get('workers', DEFAULT_WORKER_NUMBER)

    @property
    def timeout(self):
        """Get gunicorn worker timeout
        """
        return self._confs.get('timeout', DEFAULT_WORKER_TIMEOUT)

    @property
    def client_timeout(self):
        """Get thrift client socket timeout
        """
        return self._confs.get('client_timeout', DEFAULT_CLIENT_TIMEOUT)

    @property
    def port(self):
        """Get bind port
        """
        return self._confs.get('port', DEFAULT_APP_PORT)

# Config singleton
config = Config()
