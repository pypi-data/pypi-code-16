# -*- coding: utf-8 -*-

"""
Application configs.

Configs are stored in a yaml file. Default path is ``./app.yaml``.
Config file path can be changed using ``TAKUMI_APP_CONFIG_PATH``.
"""

import importlib
import os
from .loader import Config
from ._env import EnvConfig
from .utils import load_class

ENV_NAME = 'TAKUMI_APP_CONFIG_PATH'
DEFAULT_PATH = 'app.yaml'

DEFAULT_THRIFT_WORKER_CLASS = 'gevent_thriftpy'
DEFAULT_THRIFT_WORKER_CONNECTIONS = 1000
DEFAULT_WORKER_TIMEOUT = 30  # seconds
DEFAULT_APP_PORT = 8010
DEFAULT_WORKER_NUMBER = 2
DEFAULT_CLIENT_TIMEOUT = 20 * 60  # seconds


class AppSettings(dict):
    """Application related settings.

    Load settings lazily. To set default settings or add extra settings use
    ``AppSettings.update``.

    :Example:

    >>> settings = AppSettings(lambda: 'echo.settings')
    >>> # set default settings
    >>> settings.update({'SETTINGS_A': 'hello', 'SETTINGS_B': 'world'})
    >>> print(settings['SETTINGS_A'])
    'hello'
    >>> print(settings.get('SETTINGS_C', 'missing'))
    'missing'
    """
    def __init__(self, get_uri):
        self._imported = False
        self._get_uri = get_uri

    def valid(self, name):
        return name.isupper()

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)

    def __getitem__(self, key):
        if not self._imported:
            settings = importlib.import_module(self._get_uri())
            for k in dir(settings):
                if self.valid(k):
                    self[k] = getattr(settings, k)
        return super(AppSettings, self).__getitem__(key)


class AppConfig(Config):
    """Application related configs

    Supported configs:

        * app                  app dsn
        * app_name             application name
        * settings             application settings, should be importable
        * thrift_file          thrift file path, relative to app directory
        * requirements         requirement file
        * worker_class         gunicorn worker class, default 'thriftpy_gevent'
        * worker_connections   gunicorn worker connections, default 1000
        * timeout              gunicorn worker timeout, default 30s
        * port                 app bind port, default 8081
        * workers              gunicorn worker number, default 2
        * client_timeout       thriftpy client socket timeout, default 1200s

    Example:

        app: echo:service
        app_name: echo
        settings: echo.settings
        thrift_file: echo/echo.thrift
        requirements: requirements.txt
    """
    def __init__(self):
        super(AppConfig, self).__init__(os.getenv(ENV_NAME, DEFAULT_PATH))
        self.settings = AppSettings(lambda: self.get('settings', True))
        self.env = EnvConfig()
        self.syslog_disabled = False

    @property
    def worker_class(self):
        """Get gunicorn worker class config
        """
        return self.get('worker_class') or DEFAULT_THRIFT_WORKER_CLASS

    @property
    def worker_connections(self):
        """Get gunicorn worker connections config
        """
        return self.get('worker_connections') or \
            DEFAULT_THRIFT_WORKER_CONNECTIONS

    @property
    def workers(self):
        """Get worker numbers
        """
        return self.get('workers') or DEFAULT_WORKER_NUMBER

    @property
    def timeout(self):
        """Get gunicorn worker timeout
        """
        return self.get('timeout') or DEFAULT_WORKER_TIMEOUT

    @property
    def client_timeout(self):
        """Get thrift client socket timeout
        """
        return self.get('client_timeout') or DEFAULT_CLIENT_TIMEOUT

    @property
    def port(self):
        """Get bind port
        """
        return self.get('port') or DEFAULT_APP_PORT

    @property
    def app(self):
        """Get app uri
        """
        return self.get('app', True)

    @property
    def app_name(self):
        """Get application name
        """
        return self.get('app_name', True)

    @property
    def requirement(self):
        """Get requirement file name
        """
        return self.get('requirements') or 'requirements.txt'

    @property
    def thrift_file(self):
        """Get the full path of thrift file
        """
        thrift_file = self.get('thrift_file')
        if not thrift_file:
            raise RuntimeError('Fail to find thrift file')
        return os.path.join(os.getcwd(), thrift_file)

    @property
    def thrift_protocol_class(self):
        """Get thrift protocol class
        """
        cls_name = self.get('thrift_protocol_class')
        if cls_name:
            return load_class(cls_name)
