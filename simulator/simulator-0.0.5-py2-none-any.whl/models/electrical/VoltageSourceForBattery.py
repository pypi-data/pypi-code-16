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


class VoltageSourceForBattery(Model):
    """
    model of a voltage source for li-on battery
    """
    def __init__(self, soc, ocv, init_soc):
        """
        initialization

        Args:
            soc (list): axis of soc
            ocv (list): ocv curve
        """
        super(VoltageSourceForBattery, self).__init__()
        self.set_parameters('u', Table(soc, ocv))
        self.current = 0
        self.voltage = self.parameters.u[init_soc]

    def rule(self, inputs):
        """
        define the relation between inputs and outputs

        Args:
            inputs(dict): {input_name: input_value}
        """
        if 'current' in inputs.keys() and 'soc' in inputs.keys():
            self.current = inputs['current']
            self.voltage = self.parameters.u[inputs['soc']]
        else:
            raise ModelError("Inputs must be current and soc")
        return self.voltage
