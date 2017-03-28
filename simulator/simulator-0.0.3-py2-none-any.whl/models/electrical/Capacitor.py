# coding: utf-8
# !/usr/bin/python

"""
Project: simulator
Wed Jul 20 00:07:48 2016
"""

from simulator.models.Model import Model
from simulator.miscs import Table
from simulator.errors.ModelError import ModelError

# Author
__author__ = 'Jason Xing Zhang'
__email__ = 'xingz@uvic.ca'


class Capacitor(Model):
    """
    model of a Li-on battery
    """
    def __init__(self, capacitor, init_voltage, max_voltage):
        """
        initialization

        Args:
            capacitor (float): capacitor
            init_voltage (float): initial voltage
            max_voltage (float): max voltage
        """
        super(Capacitor, self).__init__()
        self.set_parameters('cap', capacitor)
        self.set_parameters('max_voltage', max_voltage)
        self.voltage = init_voltage
        self.current = 0
        self.old = 0

    def rule(self, inputs):
        """
        define the relation between inputs and outputs

        Args:
            inputs(dict): {input_name: input_value, simulation_step}
        """
        if 'current' in inputs.keys():
            self.current = inputs['current']
            # Not like battery, for capacitor, positive current is charing it
            # and negative current is discharing it.
            self.voltage += (self.old + self.current) * inputs['step'] / 2 \
                    / self.parameters.cap * (1 if inputs['time'] else 0)
            self.old = self.current
            self.voltage = min(
                max(-1 * self.parameters.max_voltage, self.voltage),
                self.parameters.max_voltage
            )
            output = self.voltage
        elif 'voltage' in inputs.keys():
            self.old = self.voltage
            self.voltage = inputs['voltage']
            self.current = self.parameters.cap * \
                    (self.voltage - self.old) / inputs['step']
            output = self.current
        else:
            raise ModelError("Inputd must be current or voltage")
        return output
