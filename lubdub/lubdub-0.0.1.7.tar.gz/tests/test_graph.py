import unittest
import random

from lubdub.exceptions import LubDubError
from lubdub import PlotHRV

from .real_data import HRV_SEQUENCE_4

class TestCalc(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_PlotHRV_empty_data_raises_LubDubError(self):
        with self.assertRaises(LubDubError):
            PlotHRV()


