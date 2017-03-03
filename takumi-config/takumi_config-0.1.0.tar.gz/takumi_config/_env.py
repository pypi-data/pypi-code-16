# -*- coding: utf-8 -*-

"""
SDK level config.

Configs are stored in a yaml file. Default path is ``/etc/takumi/env.yaml``.
Config file path can be changed using the environment vairable
``TAKUMI_CONFIG_PATH``.
"""

import os
from .loader import Config

ENV_NAME = 'TAKUMI_CONFIG_PATH'
DEFAULT_PATH = '/etc/takumi/env.yaml'

ENV_DEV = 'dev'


class EnvConfig(Config):
    """Environment related configs.

    Supported configs:

        * env

    Example:

        env: dev
    """
    def __init__(self):
        super(EnvConfig, self).__init__(os.getenv(ENV_NAME, DEFAULT_PATH))

    @property
    def name(self):
        """Get environment name.

        Default 'dev'
        """
        return self.get('env') or ENV_DEV

    def __getitem__(self, attr):
        if attr == 'name':
            return self.name
        return super(EnvConfig, self).__getitem__(attr)
