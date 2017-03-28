# coding: utf-8
# !/usr/bin/python

"""
Project: simulator
Wed Jul 20 00:07:48 2016
"""

from simulator.models.Model import Model
from simulator.miscs import Table
from simulator.models.electrical import Resistor
from simulator.models.electrical import Capacitor
from simulator.errors.ModelError import ModelError

# Author
__author__ = 'Jason Xing Zhang'
__email__ = 'xingz@uvic.ca'


class Ultracapacitor(Model):
    """
    model of a Ultracapacitor
    """
    def __init__(self, resistor, capacitor, init_soc, max_voltage):
        """
        initialization

        Args:
            resistor (float): resistor value
            capacitor (float): capacitor value
            init_soc (float): initial soc
            max_voltage (float): max voltage
        """
        super(Ultracapacitor, self).__init__()
        self.voltage = init_soc * max_voltage
        self.capacitor = Capacitor.Capacitor(
            capacitor, self.voltage, max_voltage
        )
        self.r = Resistor.Resistor(resistor)
        self.soc = init_soc
        self.set_parameters('max_voltage', max_voltage)
        self.current = 0

    def rule(self, inputs):
        """
        define the relation between inputs and outputs

        Args:
            inputs(dict): {input_name: input_value, simulation_step}
        """
        if 'current' in inputs.keys():
            self.current = inputs['current']
            inputs['current'] = inputs['current'] # positive for charge
            self.voltage = min(
                max(0, self.capacitor(**inputs) + self.r(**inputs)),
                self.parameters.max_voltage
            )
            self.soc = self.capacitor.voltage / self.parameters.max_voltage
            return self.voltage
        else:
            raise ModelError("Input current load")
