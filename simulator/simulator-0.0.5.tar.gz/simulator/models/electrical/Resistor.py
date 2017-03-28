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


class Resistor(Model):
    """
    model of a resistor
    """
    def __init__(self, value):
        """
        initialization

        Args:
            value (num): resistor value
        """
        super(Resistor, self).__init__()
        self.set_parameters('r', value)
        self.current = 0
        self.voltage = 0

    def rule(self, inputs):
        """
        define the relation between inputs and outputs

        Args:
            inputs(dict): {input_name: input_value}
        """
        if 'current' in inputs.keys():
            self.current = inputs['current']
            self.voltage = self.parameters.r * inputs['current']
            output = self.voltage
        elif 'voltage' in inputs.keys():
            self.voltage = inputs['voltage']
            self.current = inputs['voltage'] / self.parameters.r
            output = self.current
        else:
            raise ModelError("Input current or voltage")
        return output
