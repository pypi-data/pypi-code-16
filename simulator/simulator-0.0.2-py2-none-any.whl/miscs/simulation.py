# coding: utf-8
# !/usr/bin/python

"""
Project: simulator
Fri Aug 12 21:47:28 2016
"""

from simulator.errors.SimulationError import SimulationError
from simulator.miscs.Table import Table
import copy

# Author
__author__ = 'Jason Xing Zhang'
__email__ = 'xingz@uvic.ca'

def simulation(model, scope, inputs, time, simulation_step):
    """
    run simulation

    Args:
        model (Model): model
        scope (Scope): scope
        inputs (dict): {'name': list of inputs}
        time (list): list of time, must starts from 0
        simulation_step (float): simulation step width
    """
    if not inputs or not inputs.values()[0]:
        raise SimulationError("Empty inputs")
    if len(time) != len(inputs.values()[0]):
        raise SimulationError("Lengthes of time and inputs are different")
    if time[0] != 0:
        raise SimulationError("time must start from 0")
    div = time[-1] / float(simulation_step)
    if not (div - int(div)):
        simulation_time = [
            float(simulation_step) * i
            for i in range(0, int(time[-1] / simulation_step) + 1)
        ]
    else:
        raise SimulationError("Simulation duration must be divisible by step")
    inputs_table = {}
    for key, value in inputs.iteritems():
        inputs_table[key] = Table([time], value)
    for step in simulation_time:
        activate = dict(
            [(key, value[step]) for key, value in inputs_table.iteritems()] +
            [('step', simulation_step), ('time', step)]
        )
        model(**activate)
        scope.log()

