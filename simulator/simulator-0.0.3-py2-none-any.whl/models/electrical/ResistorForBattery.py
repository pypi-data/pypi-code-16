# coding: utf-8
# !/usr/bin/python

"""
Project: simulator
Wed Jul 20 00:07:48 2016
"""

from simulator.models.Model import Model
from simulator.miscs.Table import Table
from simulator.errors.ModelError import ModelError

# Author
__author__ = 'Jason Xing Zhang'
__email__ = 'xingz@uvic.ca'


class ResistorForBattery(Model):
    """
    model of a resistor for lion battery
    """
    def __init__(self, soc, resistor, atemp, thermal_mass, cp=521):
        """
        initialization

        Args:
            soc (list): soc list (Table axis)
            resistor (list): resistor value list (Table values)
            atemp (float): ambient temp
            thermal_mass (float): equivalent thermal mass
            cp (float): heat capacitor, default to the li-on battery
        """
        super(ResistorForBattery, self).__init__()
        self.set_parameters('mass', thermal_mass)
        self.set_parameters('cp', cp)
        self.set_parameters('rmap', Table(soc, resistor))
        self.current = 0
        self.voltage = 0
        self.r = resistor[0]
        self.temp = atemp

    def _calculate_temp(self):
        """
        calculate temp
        """
        self.temp += self.current ** 2 * self.r / self.parameters.mass \
                / self.parameters.cp

    def rule(self, inputs):
        """
        define the relation between inputs and outputs

        Args:
            inputs(dict): {input_name: input_value}
        """
        if 'soc' in inputs.keys():
            self.r = self.parameters.rmap[inputs['soc']]
            if 'current' in inputs.keys():
                self.current = inputs['current']
                self.voltage = self.r * inputs['current']
                output = self.voltage
            elif 'voltage' in inputs.keys():
                self.voltage = inputs['voltage']
                self.current = inputs['voltage'] / self.parameters.r
                output = self.current
            else:
                raise ModelError("Input current or voltage")
            self._calculate_temp()
            return output
        else:
            raise ModelError("Input soc")
