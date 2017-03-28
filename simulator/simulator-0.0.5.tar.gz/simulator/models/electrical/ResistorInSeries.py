# coding: utf-8
# !/usr/bin/python

"""
Project: simulator
Wed Jul 20 21:50:01 2016
"""

from simulator.models.Model import Model
from simulator.models.electrical import Resistor, TResistor
from simulator.miscs.Scope import Scope

# Author
__author__ = 'Jason Xing Zhang'
__email__ = 'xingz@uvc.ca'

class ResistorInSeries(Model):
    """
    model of two resistors in series
    """
    def __init__(self, value1, value2, thermal_mass, temp):
        """
        initialization
        """
        super(ResistorInSeries, self).__init__()
        self.r1 = Resistor.Resistor(value1)
        self.r2 = TResistor.TResistor(thermal_mass, value2, temp)
        self.voltage = 0

    def rule(self, inputs):
        """
        define the rules of the model
        """
        self.voltage = self.r1(current=inputs['current']) + self.r2(current=inputs['current'])
        return self.voltage

# ris = ResistorInSeries(10, 20, 1000, 20)
# scope = Scope()
# scope.setpoint(ris, 'r1', 'r1')
# scope.setpoint(ris, 'r2', 'r2')
# scope.setpoint(ris.r2, 'voltage', 'r2v')
# for i in range(10):
#     ris(current=i)
#     scope.log()
# print scope.display()
# 
