# -*- coding: utf-8 -*-

"""Takumi framework configuration manager.

All configs are yaml files. There two different kinds of configs:

* Env configs are independent to applications. Default path
  ``/etc/takumi/env.yaml``. All fields are optional by default.

* Application related configs. Default path ``$APP_ROOT/app.yaml``.
  Required fields: ``app_name``.


For the given config files::

    # /etc/takumi/env.yaml
    env: prod

    # app.yaml
    app_name: echo
    app: echo:service
    settings: settings

    # settings.py
    DB_DSN = 'psycopg2+postgresql://root:123@localhost:5432/dev'

:Example:

>>> from takumi_config import config
>>> print(config.env.name)
'prod'
>>> print(config.app_name)
'echo'
>>> config.settings.update({'TEST': True, 'HELLO': 'world'})
>>> print(config.settings['TEST'])
True
>>> print(config.settings['DB_DSN'])
'psycopg2+postgresql://root:123@localhost:5432/dev'
"""

from ._app import AppConfig

__all__ = ['config']

config = AppConfig()
