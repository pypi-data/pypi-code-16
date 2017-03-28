# coding: utf-8
# !/usr/bin/python

"""
Project: simulator
Wed Jul 20 00:07:48 2016
"""

from simulator.models.electrical import Resistor
from simulator.errors.ModelError import ModelError

# Author
__author__ = 'Jason Xing Zhang'
__email__ = 'xingz@uvic.ca'


class ResistorTemp(Resistor.Resistor):
    """
    model of a resistor
    """
    def __init__(self, value, atemp, thermal_mass, cp=521):
        """
        initialization

        Args:
            value (num): resistor value
            atemp (float): ambient temp
            thermal_mass (float): equivalent thermal mass
            cp (float): heat capacitor, default to the li-on battery
        """
        super(ResistorTemp, self).__init__(value)
        self.set_parameters('mass', thermal_mass)
        self.set_parameters('cp', cp)
        self.current = 0
        self.voltage = 0
        self.temp = atemp

    def _calculate_temp(self):
        """
        calculate temp
        """
        self.temp += self.current ** 2 * self.parameters.r / \
                     self.parameters.mass / self.parameters.cp

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
        self._calculate_temp()
        return output
