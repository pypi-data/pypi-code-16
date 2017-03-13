# -*- coding: utf-8 -*-

"""
takumi_config
~~~~~~~~~~~~~

Takumi framework configuration manager.

Configs are in yaml format stored in *app.yaml* by default. An
environment vairable ``TAKUMI_APP_CONFIG_PATH`` can be used to change
the path of the yaml file.

To set current running environment of the app use environment vairable
``TAKUMI_ENV``. The default env is ``dev``.

For the given config files:

.. code:: yaml

    # app.yaml
    app_name: echo
    app: echo:service
    settings: settings

.. code:: python

    # settings.py
    DB_DSN = 'psycopg2+postgresql://root:123@localhost:5432/dev'

:Example:

>>> # With this environment set:
>>> # TAKUMI_ENV=prod
>>> from takumi_config import config
>>> print(config.env)
'prod'
>>> print(config.app_name)
'echo'
>>> config.settings.update({'TEST': True, 'HELLO': 'world'})
>>> print(config.settings['TEST'])
True
>>> print(config.settings['DB_DSN'])
'psycopg2+postgresql://root:123@localhost:5432/dev'
"""

from ._config import config

__all__ = ['config']
