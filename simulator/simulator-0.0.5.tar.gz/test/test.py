# coding: utf-8
# !/usr/bin/python

"""
Project: simulator
Wed Jul 20 21:17:18 2016
"""

import pytest
import numpy as np

from simulator.miscs.Scope import Scope
from simulator.miscs.simulation import simulation

from simulator.models.electrical import Resistor, ResistorInSeries, TResistor
from simulator.models.electrical import IdealVoltageSource
from simulator.models.electrical import VoltageSourceForBattery
from simulator.models.electrical import LionBattery
from simulator.models.electrical import Capacitor, Ultracapacitor
from simulator.models.electrical import HessPassive

# Author
__author__ = 'Jason Xing Zhang'
__email__ = 'xingz@uvic.ca'


def test_resistor():
    """
    test parameters
    """
    resistor = Resistor.Resistor(10)
    scope = Scope()
    scope.setpoint(resistor, 'voltage', 'voltage')
    simulation(resistor, scope, {'current': range(0, 10)}, range(0, 10), 0.3)
    assert scope.display()['voltage'][-4] == 81.0

def test_resistor_in_series():
    """
    test solver
    """
    ris = ResistorInSeries.ResistorInSeries(10, 20, 1000, 20)
    scope = Scope()
    scope.setpoint(ris, 'r1', 'r1')
    scope.setpoint(ris, 'r2', 'r2')
    scope.setpoint(ris.r2, 'voltage', 'r2v')
    scope.setpoint(ris, 'voltage', 'all')
    simulation(ris, scope, {'current': range(0, 10)}, range(0, 10), 0.3)
    assert scope.display()['r2.voltage'][1] == 6.0

def test_tresistor():
    """
    test tresistor
    """
    tresistor = TResistor.TResistor(1000, 10, 20)
    scope = Scope()
    scope.setpoint(tresistor, 'temp', 'temp')
    simulation(tresistor, scope, {'current': range(0, 10)}, range(0, 10), 0.3)
    assert scope.display()['temp'][1] == 20.0009

def test_idealvoltagesource():
    """
    test ideal voltage source
    """
    volsource = IdealVoltageSource.IdealVoltageSource(300)
    scope = Scope()
    scope.setpoint(volsource, 'current', 'current')
    scope.setpoint(volsource, 'voltage', 'voltage')
    simulation(volsource, scope, {'current': range(0, 10)}, range(0, 10), 0.2)
    assert scope.display()['voltage'][0] == 300

def test_voltagesourceforbattery():
    """
    test voltage source for battery
    """
    vsb = VoltageSourceForBattery.VoltageSourceForBattery(
        [list(np.linspace(0, 0.9, 10))], range(280, 380, 10), 1
    )
    scope = Scope()
    scope.setpoint(vsb, 'voltage', 'voltage')
    scope.setpoint(vsb, 'current', 'current')
    simulation(
        vsb, scope,
        {'current': range(0, 10), 'soc': list(np.arange(1, 0, -0.1))},
        range(0, 10), 1
    )
    assert scope.display()['voltage'][0] == 380

def test_lionbattery():
    """
    test battery
    """
    battery = LionBattery.LionBattery(
        [0.0042, 0.0037, 0.0026, 0.0024, 0.0022, 0.0021, 0.0022, 0.0021,
         0.0022, 0.0023, 0.0024],
        [list(np.linspace(0, 1, 11))], range(280, 390, 10), 1, 28.56, 25, 6.5
    )
    scope = Scope()
    scope.setpoint(battery, 'voltage', 'voltage')
    scope.setpoint(battery, 'current', 'current')
    scope.setpoint(battery, 'soc', 'soc')
    scope.setpoint(battery.r, 'r', 'r')
    scope.setpoint(battery, 'temp', 'temp')
    simulation(
        battery, scope, {'current': range(0, 30, 1)}, range(0, 30), 1
    )
    assert scope.display()['current'][1] == 1.0

def test_capacitor():
    """
    test capacitor
    """
    cap = Capacitor.Capacitor(2, 10, 12)
    scope = Scope()
    scope.setpoint(cap, 'current', 'current')
    scope.setpoint(cap, 'voltage', 'voltage')
    simulation(cap, scope, {'current': range(0, 10)}, range(0, 10), 1)
    assert scope.display()['voltage'][-1] == 12
    cap = Capacitor.Capacitor(2, 0, 12)
    scope = Scope()
    scope.setpoint(cap, 'current', 'current')
    scope.setpoint(cap, 'voltage', 'voltage')
    simulation(cap, scope, {'voltage': range(10, 20)}, range(0, 10), 1)
    assert scope.display()['current'][1] == 2.0

def test_ultracapacitor():
    """
    test ultracapacitor
    """
    ultracap = Ultracapacitor.Ultracapacitor(0.0126, 82.5, 0, 102)
    scope = Scope()
    scope.setpoint(ultracap, 'voltage', 'voltage')
    scope.setpoint(ultracap, 'current', 'current')
    scope.setpoint(ultracap, 'soc', 'soc')
    scope.setpoint(ultracap.capacitor, 'voltage', 'cap_voltage')
    simulation(
        ultracap, scope, {'current': range(0, -20, -1)}, range(0, 20), 1
    )
    assert scope.display()['current'][0] == 0

def test_hesspassive():
    """
    test battery
    """
    hess = HessPassive.HessPassive(
        [0.0022, 0.0022], [list(np.linspace(0, 1, 2))], [280, 280], 1, 28.56,
        25, 6.5, 0.0126, 82.5, 0, 280
    )
    scope = Scope()
    scope.setpoint(hess, 'voltage', 'voltage')
    scope.setpoint(hess, 'current', 'current')
    scope.setpoint(hess.battery, 'current', 'b_current')
    scope.setpoint(hess.ucap, 'voltage', 'c_voltage')
    scope.setpoint(hess.battery, 'temp', 'temp')
    scope.setpoint(hess.battery, 'soc', 'b_soc')
    scope.setpoint(hess.ucap, 'soc', 'c_soc')
    scope.setpoint(hess.ucap, 'current', 'c_current')
    simulation(
        hess, scope, {'current': range(0, 30, 1)}, range(0, 30), 1
    )
    print scope.display()

test_hesspassive()


