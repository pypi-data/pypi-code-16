#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "0.0.3"
__short_description__ = "make your data importable"
__license__ = "MIT"
__author__ = "Sanhe Hu"

try:
    from .helpers import create_data_script
    from .metadata import gen_code
    from .name_convention import to_variable_name
except ImportError:
    pass
    