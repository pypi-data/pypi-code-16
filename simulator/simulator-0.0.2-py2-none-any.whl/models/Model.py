# coding: utf-8
# !/usr/bin/python

"""
Project: simulator
Tue Jul 19 23:59:07 2016
"""

from simulator.miscs.setlogger import setlogger
from simulator.miscs.Parameters import Parameters

# Author
__author__ = 'Jason Xing Zhang'
__email__ = 'xingz@uvic.ca'


class Model(object):
    """
    abstract class for component
    """
    def __init__(self):
        """
        initilization
        """
        self.parameters = Parameters()
        self.logger = setlogger()

    def set_parameters(self, name, value):
        """
        define parameters, which are CONSTANTS

        Args:
            name (str): parameter name
            value (num): parameter value
        """
        self.parameters.__dict__[name] = value

    def display_states(self):
        """
        display all states
        """
        return dict(
            [(name, value) for name, value in self.__dict__.iteritems() \
                if name not in ['logger', 'parameters']]
        )

    def __call__(self, **inputs):
        """
        call
        """
        if 'logger' in inputs.keys() and inputs['logger']:
            self.logger.info("Running {0}.".format(self.__class__.__name__))
        return self.rule(inputs)
