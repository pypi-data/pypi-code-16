# coding: utf-8
# !/usr/bin/python

"""
Project: simulator
Wed Jul 20 00:07:48 2016
"""

import math

from simulator.models.Model import Model
from simulator.miscs import Table
from simulator.models.electrical import LionBattery, Ultracapacitor
from simulator.errors.ModelError import ModelError

# Author
__author__ = 'Jason Xing Zhang'
__email__ = 'xingz@uvic.ca'


class HessPassive(Model):
    """
    model of the passive HESS
    """
    def __init__(self, b_resistor, b_soc, b_ocv, b_init_soc, b_thermal_mass,
                 atemp, b_cap, c_resistor, capacitor, c_init_soc, c_max_voltage
                ):
        """
        initialization

        Args:
            b_resistor (list): resistor value
            b_soc (list): state of charge (table axis)
            b_ocv (list): open circuit voltage (table value)
            b_init_soc (float): initial soc
            b_thermal_mass (float): thermal mass
            atemp (float): ambient temp
            b_cap (float): capacity
            c_resistor (float): capacitor resistor
            capacitor (float): capacitor
            c_init_soc (float): capacitor initial soc
            c_max_voltage (float): capacitor max voltage
        """
        super(HessPassive, self).__init__()
        self.battery = LionBattery.LionBattery(
            b_resistor, b_soc, b_ocv, b_init_soc, b_thermal_mass, atemp, b_cap
        )
        self.ucap = Ultracapacitor.Ultracapacitor(
            c_resistor, capacitor, c_init_soc, c_max_voltage
        )
        self.c_resistor = c_resistor
        self.capacoitor = capacitor
        self.current = 0
        self.voltage = self.battery.voltage

    def rule(self, inputs):
        """
        define the relation between inputs and outputs

        Args:
            inputs(dict): {input_name: input_value, simulation_step}
        """
        if 'current' in inputs.keys():
            self.current = inputs['current']
            if self.battery.ocv.voltage >= self.ucap.capacitor.voltage:

                # Trapezoidal method approximation
                # Ub - (Uc_old + 1/2/c*(ic+ic_old)/step) - il*Rb
                # ----------------------------------------------
                #   Rb + Rc + 1/2/c/step*(1 if time >0 else 0)

                n = self.battery.ocv.voltage - self.ucap.capacitor.voltage - \
                self.ucap.capacitor.old/2.0/self.capacoitor/inputs['step'] \
                *(1 if inputs['time'] else 0)- self.current*self.battery.r.r

                d = self.battery.r.r + self.c_resistor + \
                1.0/2.0/self.capacoitor*(1 if inputs['time'] else 0)

                c_current = n/d
                inputs['current'] = c_current
                self.ucap(**inputs)
                inputs['current'] = self.current + c_current
                self.voltage = self.battery(**inputs)
            else:

                # Trapezoidal method approximation
                # (Uc_old + 1/2/c*(ic+ic_old)/step) - Uc + il*Rb
                # ----------------------------------------------
                #   Rb + Rc - 1/2/c/step*(1 if time >0 else 0)

                n = self.ucap.capacitor.voltage + \
                self.ucap.capacitor.old/2.0/self.capacoitor/inputs['step'] \
                *(1 if inputs['time'] else 0) - self.battery.ocv.voltage + \
                self.current*self.battery.r.r

                d = self.battery.r.r + self.c_resistor - \
                1.0/2.0/self.capacoitor*(1 if inputs['time'] else 0)

                c_current = n/d
                inputs['current'] = -c_current
                self.ucap(**inputs)
                inputs['current'] = self.current - c_current
                self.voltage = self.battery(**inputs)
        else:
            raise ModelError("Input current load")
