from .i2c import I2cDevice
from .telemetry import Telemetry
from collections import namedtuple
import json

# LSM9DS0 Gyro Registers
CTRL_REG1_G = 0x20
CTRL_REG2_G = 0x21
CTRL_REG3_G = 0x22
CTRL_REG4_G = 0x23
CTRL_REG5_G = 0x24

# LSM9DS0 Accel and Magneto Registers
CTRL_REG1_XM = 0x20
CTRL_REG2_XM = 0x21
CTRL_REG3_XM = 0x22
CTRL_REG4_XM = 0x23
CTRL_REG5_XM = 0x24
CTRL_REG6_XM = 0x25
CTRL_REG7_XM = 0x26


AccelerometerMeasurement = namedtuple(
    'AccelerometerMeasurement',
    'x y z'
)


GyroscopeMeasurement = namedtuple(
    'GyroscopeMeasurement',
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
        cmd |= 0x80
        return super(Lsm9ds0I2cDevice, self).read(cmd, length)


class Accelerometer(Lsm9ds0I2cDevice):
    # These values come from the LSM9DS0 data sheet p13 table3 in the row about sensitivities.
    acceleration_scale = 0.000732 * 9.80665
    magnetometer_scale = 0.00048

    def self_test(self):
        id, = self.read_and_unpack(0x0F, 'B')
        return id == 0b01001001

    def configure(self, args):
        self.write(CTRL_REG1_XM, [0b01100111])
        self.write(CTRL_REG2_XM, [0b00100000])

        # initialise the magnetometer
        self.write(CTRL_REG5_XM, [0b11110000])
        self.write(CTRL_REG6_XM, [0b01100000])
        self.write(CTRL_REG7_XM, [0b00000000])

    def measure(self):
        """
        :return: acceleration (X, Y, Z triple in m s^-2)
        """
        acc = self.read_and_unpack(0x28, '<hhh')
        acc = tuple(acc * self.acceleration_scale for acc in acc)
        result = AccelerometerMeasurement(*acc)
        packet = {
            "x": str(result[0]),
            "y": str(result[1]),
            "z": str(result[2])
        }

        Telemetry.update("acc", packet)
        return result

    @property
    def x(self):
        return self.measure()[0]

    @property
    def y(self):
        return self.measure()[1]

    @property
    def z(self):
        return self.measure()[2]


class Magnetometer(Lsm9ds0I2cDevice):
    # These values come from the LSM9DS0 data sheet p13 table3 in the row about sensitivities.
    acceleration_scale = 0.000732 * 9.80665
    magnetometer_scale = 0.00048

    def self_test(self):
        id, = self.read_and_unpack(0x0F, 'B')
        return id == 0b01001001

    def configure(self, args):
        self.write(CTRL_REG1_XM, [0b01100111])
        self.write(CTRL_REG2_XM, [0b00100000])

        # initialise the magnetometer
        self.write(CTRL_REG5_XM, [0b11110000])
        self.write(CTRL_REG6_XM, [0b01100000])
        self.write(CTRL_REG7_XM, [0b00000000])

    def measure(self):
        """
        :return: magnetic field (X, Y, Z triple in mgauss)
        """
        mag = self.read_and_unpack(0x08, '<hhh')
        mag = tuple(mag * self.magnetometer_scale for mag in mag)
        result = MagnetometerMeasurement(*mag)

        packet = {
            "x": str(result[0]),
            "y": str(result[1]),
            "z": str(result[2])
        }

        Telemetry.update("mag", packet)

        return result

    @property
    def x(self):
        return self.measure()[0]

    @property
    def y(self):
        return self.measure()[1]

    @property
    def z(self):
        return self.measure()[2]


class Gyroscope(Lsm9ds0I2cDevice):
    gyroscope_scale = 0.070

    def self_test(self):
        id, = self.read_and_unpack(0x0F, 'B')
        return id == 0b11010100

    def configure(self, args):
        # initialise the gyroscope
        self.write(CTRL_REG1_G, [0b00001111])
        self.write(CTRL_REG4_G, [0b00110000])

    def measure(self):
        """
        :return: X, Y, Z triple in degrees per second
        """
        gyro = self.read_and_unpack(0x28, '<hhh')
        gyro = tuple(gyro * self.gyroscope_scale for gyro in gyro)
        result = GyroscopeMeasurement(*gyro)

        packet = {
            "x": str(result[0]),
            "y": str(result[1]),
            "z": str(result[2])
        }

        Telemetry.update("gyr", packet)
        return result

    @property
    def x(self):
        return self.measure()[0]

    @property
    def y(self):
        return self.measure()[1]

    @property
    def z(self):
        return self.measure()[2]

