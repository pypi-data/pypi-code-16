"""
Tests of the Population class, using the pyNN.mock backend and two mock MPI processes

:copyright: Copyright 2006-2016 by the PyNN team, see AUTHORS.
:license: CeCILL, see LICENSE for details.
"""

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from pyNN import random
import numpy
from numpy.testing import assert_array_equal, assert_array_almost_equal
from .mocks import MockRNG
import pyNN.mock as sim


orig_mpi_get_config = random.get_mpi_config


def setUp():
    random.get_mpi_config = lambda: (0, 2)


def tearDown():
    random.get_mpi_config = orig_mpi_get_config


class PopulationTest(unittest.TestCase):

    def setUp(self, sim=sim, **extra):
        sim.setup(num_processes=2, rank=0, **extra)

    def tearDown(self, sim=sim):
        sim.end()

    def test_create_with_standard_cell_simple(self, sim=sim):
        p = sim.Population(11, sim.IF_cond_exp())
        self.assertEqual(p.size, 11)
        self.assertEqual(p.local_size, 6)

    def test_set(self, sim=sim):
        p = sim.Population(4, sim.IF_cond_exp, {'tau_m': 12.3, 'tau_syn_E': 0.987, 'tau_syn_I': 0.7})
        rng = MockRNG(start=1.21, delta=0.01, parallel_safe=True)
        p.set(tau_syn_E=random.RandomDistribution('uniform', (0.5, 1.5), rng=rng), tau_m=9.87)
        tau_m, tau_syn_E, tau_syn_I = p.get(('tau_m', 'tau_syn_E', 'tau_syn_I'), gather=False)
        assert_array_equal(tau_syn_E, numpy.array([1.21, 1.23]))
        assert_array_almost_equal(tau_m, 9.87 * numpy.ones((2,)))
        assert_array_equal(tau_syn_I, 0.7 * numpy.ones((2,)))