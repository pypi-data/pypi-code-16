# coding: utf-8
# !/usr/bin/python

"""
Project: simulator
Fri Jul 15 00:11:55 2016
"""

# Author
__author__ = 'Jason Xing Zhang'
__email__ = 'xingz@uvic.ca'

class ModelError(Exception):
    """
    Model Error
    """
    def __init__(self, error):
        """
        initialization

        Args:
            error (str): error message
        """
        super(ModelError, self).__init__(error)

