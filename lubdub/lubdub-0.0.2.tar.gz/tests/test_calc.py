import unittest
import random

from lubdub.calc import *
from lubdub import PlotHRV

from .real_data import HRV_SEQUENCE_4

class TestCalc(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_baseline_4_measurements(self):
        assert hrv_baseline(HRV_SEQUENCE_4) == 75.0


