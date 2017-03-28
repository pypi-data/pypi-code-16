# coding: utf-8
# !/usr/bin/python

"""
Project: simulator
Thu Jul 28 22:10:50 2016
"""

from simulator.models.Model import Model
from simulator.errors.ModelError import ModelError

# Author
__author__ = 'Jason Xing Zhang'
__email__ = 'xingz@uvic.ca'

class TResistor(Model):
    """
    Resistor with thermal performance
    """
    def __init__(self, thermal_mass, initial_resistance, initial_temp):
        """
        initialization

        Args:
            thermal_mass (num): thermal mass, which is total mass * c
            (material)
            initial_resistance (num): initial resistor value
            initial_temp (num): ambient temperature
        """
        super(TResistor, self).__init__()
        self.set_parameters('thermal_mass', thermal_mass)
        self.set_parameters('ambient_temp', initial_temp)
        self.r = initial_resistance
        self.temp = initial_temp
        self.current = 0
        self.voltage = 0

    def rule(self, inputs):
        """
        define the relation between inputs and outputs

        Args:
            inputs (dict): {input_name: input_value}
        """
        self.r += (self.temp - self.parameters.ambient_temp)* 0.01
        if 'current' in inputs.keys():
            self.current = inputs['current']
            self.voltage = inputs['current'] * self.r
            output = self.voltage
        elif 'voltage' in inputs.keys():
            self.voltage = inputs['voltage']
            self.current = inputs['voltage'] / self.r
            output = self.current
        else:
            raise ModelError("Please input current ot voltage")
        self.temp += self.current**2*self.r/self.parameters.thermal_mass
        return output

