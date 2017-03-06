# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
"""
An utility package
"""

__author__ = "the01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2013-17, Florian JUNG"
__license__ = "MIT"
__version__ = "0.3.5a0"
__date__ = "2017-03-06"

import logging

from .loadable import Loadable, load_file, save_file, \
    loadJSON, saveJSON, loadJSONFile, saveJSONFile
from .logable import Logable, ModuleLogable, get_logger
from .runable import StartStopable, Startable, Stopable, StartException


logger = logging.getLogger(__name__)
__all__ = ["logable", "loadable", "runable"]
