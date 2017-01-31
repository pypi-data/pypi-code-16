
from setuptools import setup
setup(**{'name': 'django-etcd-settings', 'author': 'Enrique Paz', 'author_email': 'quiquepaz@gmail.com', 'include_package_data': True, 'long_description': "Django ETCD Settings\n=====================\n\n.. image:: https://secure.travis-ci.org/kpn-digital/django-etcd-settings.svg?branch=master\n    :target:  http://travis-ci.org/kpn-digital/django-etcd-settings?branch=master\n\n.. image:: https://img.shields.io/codecov/c/github/kpn-digital/django-etcd-settings/master.svg\n    :target: http://codecov.io/github/kpn-digital/django-etcd-settings?branch=master\n\n.. image:: https://img.shields.io/pypi/v/django-etcd-settings.svg\n    :target: https://pypi.python.org/pypi/django-etcd-settings\n\n.. image:: https://readthedocs.org/projects/django-etcd-settings/badge/?version=latest\n    :target: http://django-etcd-settings.readthedocs.org/en/latest/?badge=latest\n\n\nFeatures\n--------\n\nThis application allows you to extend the Django settings as configured in the\n``settings.py`` file with:\n\n* Environment dependent values\n* Values in different config sets, identified by name, which can be selected on\n  a 'per request' basis using the ``X-DYNAMIC-SETTINGS`` HTTP header\n\nBoth the added configuration values and config sets would live at ETCD, which\nwill be continuously monitored by this library in order to transparently update\nyour app settings upon changes.\n\n\nBackends\n--------\n\n- ETCD 2.2.1\n\n\nInstallation\n------------\n\n.. code-block:: bash\n\n    $ pip install django-etcd-settings\n\n\nUsage\n-----\n\nThis Django application uses the following configuration keys:\n\n* ``DJES_ETCD_DETAILS``: a dict with 'host', 'port', 'protocol', 'prefix',\n    'long_polling_timeout' and 'long_polling_safety_delay' (both in seconds).\n    'prefix' is a string to be used as base path for all configuration\n    managed by this app.\n    i.e. '/config/api' will result in '/config/api/<ENV>' and\n    '/config/api/extensions/' to be used for environment defaults and\n    config_sets respectively\n    Timeouts default to 50 and 5 seconds respectively.\n    If ``DJES_ETCD_SETTINGS`` is None, this app will start with no errors and\n    etcd_settings.settings will resolve to django.conf.settings plus your\n    DJES_DEV_PARAMS overwrites\n    i.e.\n\n    .. code-block:: python\n\n        ETCD_DETAILS = dict(\n            host='localhost', port=4000, protocol='http',\n            long_polling_timout=50, long_polling_safety_delay=5\n        )\n\n* ``DJES_DEV_PARAMS``: A module with local overwrites, generally used for\n    development. The overwrites must be capitalized module attributes.\n    These overwrites will have preference over development settings on ETCD,\n    but not over configset overwrites indicated by the ``X-DYNAMIC-SETTINGS``\n    HTTP header\n\n* ``DJES_ENV``: A string with the name of the environment in which the code is\n    running. This will be used for accessing the env_defaults in\n    ETCD in a directory with that name\n    i.e. 'test', 'staging', 'prod'...\n\n* ``DJES_REQUEST_GETTER``: path to a function which accesses the HTTP request\n    object being handled. Ensuring access to this value can be implemented\n    with, for instance, middleware. This settings is only used to allow\n    config overwrites on runtime based on predifined config_sets. In case you\n    don't want to use this functionality, just set this setting to None\n    i.e. 'middleware.thread_local.get_current_request'\n\n* ``DJES_WSGI_FILE``: path to the ``wsgi.py`` file for the django\n    project. If not None, the monitoring of environment configuration will\n    perform a ``touch`` of the file everytime the env_defaults are updated, so\n    that all processes consuming settings from ``django.conf`` can consume the\n    latest settings available as well\n    The path can be absolute or relative to the 'manage.py' file.\n    i.e. /project/src/wsgi.py, wsgi.py\n\nThen, add ``etcd_settings`` to the list of ``INSTALLED_APPS`` before any other that\nrequires dynamic settings.\n\nFrom your code, just do ``from etcd_settings import settings`` instead of ``from\ndjango.conf import settings``.\n\nIn case you want to use ``etcd_settings`` to modify some values in your standard\nDjango settings.py file (i.e. Database config), you can use the following\nsnippet in your settings file, as high as possible in the file and immediately\nunder the ``DJES_*`` settings definition:\n\n    .. code-block:: python\n\n        import etcd_settings.loader\n        extra_settings = etcd_settings.loader.get_overwrites(\n            DJES_ENV, DJES_DEV_PARAMS, DJES_ETCD_DETAILS)\n        locals().update(extra_settings)\n", 'url': 'https://github.com/kpn-digital/django-etcd-settings', 'version': '0.1.14', 'zip_safe': False, 'install_requires': ['Django>=1.7.5', 'python-etcd>=0.4.1', 'python-dateutil>=2.2', 'six<2.0.0,>=1.10.0'], 'packages': ['etcd_settings'], 'classifiers': ['Development Status :: 5 - Production/Stable', 'Environment :: Web Environment', 'Intended Audience :: Developers', 'Operating System :: OS Independent', 'Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 2.7', 'Topic :: Internet :: WWW/HTTP'], 'tests_require': ['tox'], 'description': 'A dynamic settings management solution for Django using ETCD'})
