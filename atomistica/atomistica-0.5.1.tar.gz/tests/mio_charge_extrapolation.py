#! /usr/bin/env python

# ======================================================================
# Atomistica - Interatomic potential library and molecular dynamics code
# https://github.com/Atomistica/atomistica
#
# Copyright (2005-2015) Lars Pastewka <lars.pastewka@kit.edu> and others
# See the AUTHORS file in the top-level Atomistica directory.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ======================================================================

"""
Test the mio parametrization of Frauenheim and co-workers.
"""

from __future__ import print_function

import os
import sys
import unittest

import numpy as np

from ase.structure import molecule
from ase.optimize import FIRE

import atomistica.native as native
from atomistica import Atomistica

###

def run_mio_test(test=None):
    

###

class TestMIOChargeExtrapolation(unittest.TestCase):

    def test_mio_charge_extrapolation(self):
        if os.getenv('MIO') is None:
            print('Skipping MIO test. Specify path to mio Slater-Koster ' \
                  'tables in MIO environment variable if you want to run it.')
        else:
            database_folder = os.getenv('MIO')
            if database_folder is None:
                raise RuntimeError('Please use environment variable MIO to specify path to mio Slater-Koster tables.')
        
            calc = Atomistica(
                [ native.TightBinding(
                database_folder = database_folder,
                SolverLAPACK = dict(electronic_T=0.001),
                SCC = dict(dq_crit = 1e-4,
                           mixing = 0.2, # 0.2
                           andersen_memory = 3, # 3
                           maximum_iterations = 100,
                           log = True)
                ),
                  native.DirectCoulomb(),
                  native.SlaterCharges(cutoff=10.0) ],
                avgn = 1000
                )
            a = molecule('CO2')
            

            

###

if __name__ == '__main__':
    run_mio_test()
