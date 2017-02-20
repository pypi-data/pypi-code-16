import time
from .i2c import I2cDevice
from collections import namedtuple

BarometerMeasurement = namedtuple(
    'BarometerMeasurement',
    'temperature pressure humidity'
)

class Barometer(I2cDevice):

    """
    Interface for BME280 pressure and humidity
    """
    def read_raw_measurements(self):
        return 0.0, 0.0, 0.0

    def apply_calibration(self, t_raw, p_raw, h_raw, t_calib=None):
        pass
        return 0.0,0.0,0.0

    def measure(self):
        """
        :return: tuple of: temperature (C), pressure (Pa), humidity (% relative humidity)
        """
        return 0.0, 0.0, 0.0


    @property
    def temperature(self):
        return 0.0

    @property
    def pressure(self):
        return 0.0

    @property
    def humidity(self):
        return 0.0
