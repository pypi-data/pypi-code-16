# -*- coding: utf-8 -*-
import os

__author__ = """Per Unneberg"""
__email__ = 'per.unneberg@scilifelab.se'
__version__ = '0.1.0'

WORKFLOW=os.path.join(os.path.normpath(os.path.dirname(__file__)), "workflow.sm")


from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
