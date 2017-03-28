# coding: utf-8
# !/usr/bin/python

"""
Project: simulator
Wed Jul 20 00:07:48 2016
"""

from simulator.models.Model import Model
from simulator.miscs import Table
from simulator.models.electrical import ResistorForBattery
from simulator.models.electrical import VoltageSourceForBattery
from simulator.errors.ModelError import ModelError

# Author
__author__ = 'Jason Xing Zhang'
__email__ = 'xingz@uvic.ca'


class LionBattery(Model):
    """
    model of a Li-on battery
    """
    def __init__(self, resistor, soc, ocv, init_soc, thermal_mass, \
                 atemp, cap, currane_range = [-110.2493, 194.2335]):
        """
        initialization

        Args:
            resistor (list): resistor value
            soc (list): state of charge (table axis)
            ocv (list): open circuit voltage (table value)
            init_soc (float): initial soc
            thermal_mass (float): thermal mass
            atemp (float): ambient temp
            cap (float): capacity
        """
        super(LionBattery, self).__init__()
        self.ocv = VoltageSourceForBattery.VoltageSourceForBattery(
            soc, ocv, init_soc
        )
        self.r = ResistorForBattery.ResistorForBattery(
            soc, resistor, thermal_mass, atemp
        )
        self.soc = init_soc
        self.set_parameters('cap', cap)
        self.set_parameters('crange', currane_range)
        self.voltage = self.ocv.parameters.u[init_soc]
        self.current = 0
        self.current_old = 0
        self.temp = atemp

    def _update_soc(self, step):
        delta_cap = (self.current + self.current_old) * step / 2.0 / 3600
        self.soc = min(
            max(0, self.soc - delta_cap / float(self.parameters.cap)), 1
        )
        self.current_old = self.current

    def rule(self, inputs):
        """
        define the relation between inputs and outputs

        Args:
            inputs(dict): {input_name: input_value, simulation_step}
        """
        if 'current' in inputs.keys():
            self.current = inputs['current']
            self.current = min(
                self.parameters.crange[1], max(
                    self.parameters.crange[0], self.current
                )
            )
            inputs.update({'soc': self.soc})
            self.voltage = self.ocv(**inputs) - self.r(**inputs)
            output = self.voltage
            self._update_soc(inputs['step'])
            self.temp = self.r.temp
        else:
            raise ModelError("Input current load")
        return output
