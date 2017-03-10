# -*- coding: utf-8 -*-

__version__ = '0.0.1'

try:
	from _storage import Storage as Open
except ImportError:
	from storage import Storage as Open
