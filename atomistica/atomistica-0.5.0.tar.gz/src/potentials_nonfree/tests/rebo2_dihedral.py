#! /usr/bin/env python

# ======================================================================
# Atomistica - Interatomic potential library
# https://github.com/pastewka/atomistica
# Lars Pastewka, lars.pastewka@iwm.fraunhofer.de, and others.
# See the AUTHORS file in the top-level Atomistica directory.
#
# Copyright (2005-2013) Fraunhofer IWM
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

import math
import sys

import unittest

import numpy as np

import ase
import ase.io as io
from ase.units import kcal, mol
from ase.structure import molecule
from ase.optimize import FIRE

import atomistica.native as native
from atomistica import Rebo2SiCH, Rebo2SiCHScr
from atomistica.tests import test_forces

import matplotlib.pyplot as plt

###

def trig_on(x, x1=0.1, x2=0.5):
    if x < x1:
        return 0.0
    elif x > x2:
        return 1.0
    else:
        return (1-np.cos(np.pi*(x-x1)/(x2-x1)))/2

def rotate(a, n=2, nsteps=101):
    angles = np.linspace(0, 2*np.pi, nsteps)
    energies = []
    x0, y0, z0 = a.positions.T.copy()
    mx = x0.mean()
    my = y0.mean()
    for angle in angles:
        rot = np.array([[np.cos(angle), np.sin(angle)],
                        [-np.sin(angle), np.cos(angle)]])
        x = x0.copy()
        y = y0.copy()
        z = z0.copy()
        x[:-n], y[:-n] = rot.dot([x0[:-n]-mx, y0[:-n]-my])
        x[:-n] += mx
        y[:-n] += my
        a.set_positions(np.transpose([x, y, z]))
        energies += [a.get_potential_energy()]
        #io.write('ethylene_{}.xyz'.format(int(angle*180/np.pi)), a)
    energies = np.array(energies)
    energies -= energies.min()
    return angles, energies

class TestDihedral(unittest.TestCase):

    def test_ethane_barrier(self):
        barrier = 4.679

        a = molecule('C2H4')
        a.center(vacuum=10.0)
        #for c in [Rebo2SiCH(), Rebo2SiCHScr()]:
        for c in [Rebo2SiCH(), Rebo2SiCHScr()]:
            a.set_calculator(c)
            FIRE(a, logfile=None).run(fmax=0.01)

            angles, energies = rotate(a)
            de = energies-barrier*(1+np.cos(2*angles+np.pi))/2
            #np.savetxt('barrier_{}.out'.format(c.name), np.transpose([angles, energies, de]))
            self.assertAlmostEqual(np.abs(de).max(), 0.0, places=3)

    def test_deformed_ethane_barrier(self):
        """Similar to ethane test above, but change H-H bond length to test
        region where angular cutoff in the screened potential kicks in."""
        barrier = 4.679

        a = molecule('C2H4')
        a.set_calculator(Rebo2SiCH())
        FIRE(a, logfile=None).run(fmax=0.01)
        a.center(vacuum=10.0)
        #for c in [Rebo2SiCH(), Rebo2SiCHScr()]:
        for c in [Rebo2SiCHScr()]:
            a.set_calculator(c)

            for i, bondlen in enumerate([1.25, 1.0, 0.75, 0.50]):
                a.set_distance(2, 3, bondlen)
                a.set_distance(4, 5, bondlen)
                sin_sq = np.sin(a.get_angle([1,0,2]))**2

                #np.savetxt('barrier_{}.out'.format(c.name), np.transpose([angles, energies, de]))
                #self.assertAlmostEqual(np.abs(de).max(), 0.0, places=3)
                angles, energies = rotate(a)
                de = energies-barrier*(1+np.cos(2*angles+np.pi))/2 * trig_on(sin_sq)**2
                self.assertAlmostEqual(np.abs(de).max(), 0.0, places=3)

    def test_ethane_forces(self):
        dx = 1e-6
        a = molecule('C2H4')
        a.rattle(0.2)
        for c in [Rebo2SiCH(), Rebo2SiCHScr()]:
            a.set_calculator(c)
            ffd, f0, maxdf = test_forces(a, dx=dx)
            self.assertAlmostEqual(maxdf, 0.0)

    def test_deformed_ethane_forces(self):
        """Similar to ethane force test above, but change H-H bond length to test
        region where angular cutoff in the screened potential kicks in."""
        dx = 1e-6
        a = molecule('C2H4')
        a.set_calculator(Rebo2SiCH())
        FIRE(a, logfile=None).run(fmax=0.01)
        a.center(vacuum=10.0)
        #for c in [Rebo2SiCH(), Rebo2SiCHScr()]:
        for c in [Rebo2SiCH(), Rebo2SiCHScr()]:
            a.set_calculator(c)

            for i, bondlen in enumerate([1.25, 1.0, 0.75, 0.50]):
                a.set_distance(2, 3, bondlen)
                a.set_distance(4, 5, bondlen)
                a.rattle(0.05)
                ffd, f0, maxdf = test_forces(a, dx=dx)
                self.assertAlmostEqual(maxdf, 0.0)

if __name__ == '__main__':
    unittest.main()