#!/usr/bin/env python3
# coding: utf-8

"""


注释


"""
import sys

from .api import YBAI
from .api.messages import MessageConfig,Message,Registered

__title__ = 'ybai'
__version__ = '0.0.3'
__author__ = 'Yinbing'
__license__ = 'MIT'
__copyright__ = '2017, Yinbing'

version_details = 'ybai {ver} from {path} (python {pv.major}.{pv.minor}.{pv.micro})'.format(
    ver=__version__, path=__path__[0], pv=sys.version_info)
