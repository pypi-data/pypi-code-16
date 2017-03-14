import unittest
import statistics
import math

from lubdub import Measurement

from .real_data import RR_INTERVALS_1, RR_INTERVALS_2, RR_INTERVALS_3


class TestMeasurement(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_measurement_rr1(self):
        meas = Measurement(RR_INTERVALS_1)
        assert round(meas.rmssd, 2) == 60.54
        assert meas.nn50 == 53
        assert round(meas.pnn50, 2) == 0.47
        assert round(meas.sdnn, 2) == 70.03
        assert len(meas.nns) == 113
        assert len(meas.rrs) == 114
        assert meas.hrv_baseline is None
        assert meas.calm_time is None
        assert meas.stress_time is None

    def test_measurement_rr2_with_hrv_baseline(self):
        baseline = 68
        meas = Measurement(RR_INTERVALS_2, hrv_baseline=baseline)
        assert round(meas.rmssd, 2) == 80.79
        assert meas.nn50 == 47
        assert round(meas.pnn50, 2) == .42
        assert round(meas.sdnn, 2) == 74.47
        assert len(meas.nns) == 111
        assert len(meas.rrs) == 112
        assert meas.hrv_baseline == 68
        assert round(meas.calm_time, 2) == 26.88
        assert round(meas.stress_time, 2) == 26.88

    def test_measurement_rr3_with_hrv_baseline(self):
        baseline = 70.5
        meas = Measurement(RR_INTERVALS_3, hrv_baseline=baseline)
        assert round(meas.rmssd, 2) == 100.76
        assert meas.nn50 == 40
        assert round(meas.pnn50, 2) == .43
        assert round(meas.sdnn, 2) == 136.24
        assert len(meas.nns) == 93
        assert len(meas.rrs) == 94
        assert meas.hrv_baseline == 70.5
        assert round(meas.calm_time, 2) == 33.81
        assert round(meas.stress_time, 2) == 2.67


