from .i2c import I2cDevice
from collections import namedtuple

# # LSM9DS0 Gyro Registers
# CTRL_REG1_G = 0x20
# CTRL_REG2_G = 0x21
# CTRL_REG3_G = 0x22
# CTRL_REG4_G = 0x23
# CTRL_REG5_G = 0x24
#
# # LSM9DS0 Accel and Magneto Registers
# CTRL_REG1_XM = 0x20
# CTRL_REG2_XM = 0x21
# CTRL_REG3_XM = 0x22
# CTRL_REG4_XM = 0x23
# CTRL_REG5_XM = 0x24
# CTRL_REG6_XM = 0x25
# CTRL_REG7_XM = 0x26


AccelerometerMeasurement = namedtuple(
    'AccelerometerMeasurement',
    'x y z'
)


GryoscopeMeasurement = namedtuple(
    'GryoscopeMeasurement',
    'x y z'
)


MagnetometerMeasurement = namedtuple(
    'MagnetometerMeasurement',
    'x y z'
)


class Lsm9ds0I2cDevice(I2cDevice):
    """
    This overrides the read method to toggle the high bit in the register address.
    This is needed for multi-byte reads.
    """
    def read(self, cmd, length):
        return 0.0


class Accelerometer(Lsm9ds0I2cDevice):
    # These values come from the LSM9DS0 data sheet p13 table3 in the row about sensitivities.
    acceleration_scale = 0.000732 * 9.80665
    magnetometer_scale = 0.00048

    def configure(self, args):
        pass

    def measure(self):
        """
        :return: acceleration (X, Y, Z triple in m s^-1)
        """
        return AccelerometerMeasurement(0.0, 0.0, 0.0)

    @property
    def x(self):
        return 0.0

    @property
    def y(self):
        return 0.0

    @property
    def z(self):
        return 9.8


class Magnetometer(Lsm9ds0I2cDevice):
    # These values come from the LSM9DS0 data sheet p13 table3 in the row about sensitivities.
    acceleration_scale = 0.000732 * 9.80665
    magnetometer_scale = 0.00048

    def self_test(self):
        return True

    def configure(self, args):
        return

    def measure(self):
        """
        :return: magnetic field (X, Y, Z triple in mgauss)
        """
        return MagnetometerMeasurement(0.0, 0.0, 0.0)

    @property
    def x(self):
        return 0.0

    @property
    def y(self):
        return 0.0

    @property
    def z(self):
        return 0.0


class Gyroscope(Lsm9ds0I2cDevice):
    gyroscope_scale = 0.070

    def self_test(self):
        return True

    def configure(self, args):
        return

    def measure(self):
        """
        :return: X, Y, Z triple in degrees per second
        """
        return GryoscopeMeasurement(0.0, 0.0, 0.0)

    @property
    def x(self):
        return 0.0

    @property
    def y(self):
        return 0.0

    @property
    def z(self):
        return 0.0