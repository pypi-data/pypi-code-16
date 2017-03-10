# -*- coding: utf-8 -*-
# Copyright (c) 2016 Sqreen. All Rights Reserved.
# Please refer to our terms for more information: https://www.sqreen.io/terms.html
""" Sqreen python agent package
"""
from sqreen.vendors import install_vendors
install_vendors()

from sqreen.config import Config
from sqreen.log import configure_root_logger
from sqreen.runner_thread import start

from sqreen.sdk.auth import *

__author__ = 'Boris Feld'
__email__ = 'boris@sqreen.io'
__version__ = '1.0.3'
VERSION = __version__

# Configure logging
config = Config()
config.load()
configure_root_logger(config['LOG_LEVEL'], config['LOG_LOCATION'])

__all__ = ['start']
