# coding: utf-8
# !/usr/bin/python

"""
Project: simulator
Wed Jul 20 00:07:48 2016
"""

from simulator.models.Model import Model
from simulator.errors.ModelError import ModelError

# Author
__author__ = 'Jason Xing Zhang'
__email__ = 'xingz@uvic.ca'


class IdealVoltageSource(Model):
    """
    model of a ideal voltage source
    """
    def __init__(self, value):
        """
        initialization

        Args:
            value (num): voltage value
        """
        super(IdealVoltageSource, self).__init__()
        self.set_parameters('u', value)
        self.current = 0
        self.voltage = value

    def rule(self, inputs):
        """
        define the relation between inputs and outputs

        Args:
            inputs(dict): {input_name: input_value}
        """
        if 'current' in inputs.keys():
            self.current = inputs['current']
            return self.voltage
        else:
            raise ModelError("Input must be current")
