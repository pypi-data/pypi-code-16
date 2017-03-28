# coding: utf-8
# !/usr/bin/python

"""
Project: simulator
Wed Aug  3 22:04:58 2016
"""

import json
from simulator.models.Model import Model
from simulator.errors.ScopeError import ScopeError

# Author
__author__ = 'Jason Xing Zhang'
__email__ = 'xingz@uvic.ca'

class Scope(object):

    """
    Scope logs, display and save states of models
    """

    def __init__(self):
        """
        initialization
        """
        self.states = {}
        self.results = {}
        self.timeline = None

    def add_timeline(self, timeline):
        """
        called by simulation instance to add time line
        """
        self.timeline = timeline

    def setpoint(self, model, state, name):
        """
        set scope on states

        Args:
            model (Model): model instance
            state (): state
            name (str): give signal a name for display
        """
        if '.' in name:
            raise ScopeError('''Variable names in scope cannot contain '.'.''')
        self.results[name] = []
        self.states[name] = (model, state)

    def reset(self):
        """
        reset scope
        """
        self.states = {}
        self.results = {}

    def _check_subs(self, state):
        """
        get sub-states in to a dictionary of list

        Args:
            state (): state

        Return:
            values (): values
        """
        if isinstance(state, Model):
            values = {}
            for key, value in state.display_states().iteritems():
                values[key] = self._check_subs(value)
        else:
            values = state
        return values

    def _conv2list(self):
        """
        convert list of dictionary in self.results to dictionary of list

        Example:
            {'r1': [{'r2: 1, 'r3': 2}, {'r2': 3, 'r3': 4}]}
            ===>
            {'r1.r2': [1, 3], 'r1.r3': [2, 4]}
        """
        results = {}
        for key, value in self.results.iteritems():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                comkeys = self._combine_dict_keys(key, value[0])
                for comkey in comkeys:
                    keylist = comkey.split('.')
                    results[comkey] = []
                    for val in value:
                        re = val
                        for subkey in keylist[1:]:
                            re = re[subkey]
                        results[comkey].append(re)
            else:
                results[key] = value
        return results

    def _combine_dict_keys(self, parent_key, dictionary):
        """
        get key relation

        example:
            {'r1r2': {'outputs': 0, 'r1': {'outputs': 0}, 'r2': {'outputs':0}}
            ===>
            {
                'r1r2.outputs': ['outputs'],
                'r1r2.r1.outputs': ['r1', 'outputs'],
                'r1r2.r2.outputs': ['r2', 'outputs']
            }
            this function returns ['r1r2.outputs', 'r1r2.r1.outputs',
            'r1r2.r2.outputs']

        Args:
            parent_key (str): keys
            dictionary (dict): dictionary

        Returns:
            results (list): list of combined keys
        """
        comlist = []
        for key, value in dictionary.iteritems():
            if isinstance(value, dict):
                ncomlist = self._combine_dict_keys(key, value)
                for ncom in ncomlist:
                    comlist.append(parent_key + '.' + ncom)
            else:
                comlist.append(parent_key + '.' + key)
        return comlist

    def log(self):
        """
        log state value during simulation, called by Model.py
        """
        for name, model_state in self.states.iteritems():
            value = self._check_subs(model_state[0].__dict__[model_state[1]])
            self.results[name].append(value)

    def display(self):
        """
        display scope results
        """
        results = self._conv2list()
        for key in self.results.keys():
            self.results[key] = []
        return results

