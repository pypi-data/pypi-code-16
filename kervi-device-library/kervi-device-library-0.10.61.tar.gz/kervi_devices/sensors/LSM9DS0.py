# Copyright (c) 2016, Tim Wentzlau
# Licensed under MIT

import time
import math
from kervi.hal import I2CSensorDeviceDriver

I2C_GYRO_ADDRESS = 0x6A
I2C_ACCL_ADDRESS = 0x1e

magXmax = 419
magYmax = 683
magZmax = 528
magXmin = -658
magYmin = -397
magZmin = -472

MAG_LPF_FACTOR = 0.4
ACC_LPF_FACTOR = 0.1

class LSM9DS0RawGyroDeviceDriver(I2CSensorDeviceDriver):
    def __init__(self, address=I2CSensorDeviceDriver, bus=None):
        I2CSensorDeviceDriver.__init__(self, address, bus)
        self.i2c.write8(0x20, 0x0F)
        self.i2c.write_list(0x6A, 0x23, 0x30)

    def read_value(self):

        data0 = self.i2c.read_U8(0x6A, 0x28)
        data1 = self.i2c.read_U8(0x6A, 0x29)

        # Convert the data
        x_gyro = data1 * 256 + data0
        if x_gyro > 32767:
            x_gyro -= 65536

        data0 = self.i2c.read_U8(0x6A, 0x2A)
        data1 = self.i2c.read_U8(0x6A, 0x2B)

        # Convert the data
        y_gyro = data1 * 256 + data0
        if y_gyro > 32767:
            y_gyro -= 65536

        # LSM9DS0 Gyro address, 0x6A(106)
        # Read data back from 0x2C(44), 2 bytes
        # Z-Axis Gyro LSB, Z-Axis Gyro MSB
        data0 = self.i2c.read_U8(0x6A, 0x2C)
        data1 = self.i2c.read_U8(0x6A, 0x2D)

        # Convert the data
        z_gyro = data1 * 256 + data0
        if z_gyro > 32767:
            z_gyro -= 65536

        return (x_gyro, y_gyro, z_gyro)


class LSM9DS0RawAcclDeviceDriver(I2CSensorDeviceDriver):
    def __init__(self, address=I2C_ACCL_ADDRESS, bus=None):
        I2CSensorDeviceDriver.__init__(self, address, bus)

        self.i2c.write8(0x20, 0x67)
        # LSM9DS0 Accl and Mag address, 0x1E(30)
        # Select control register2, 0x21(33)
        #		0x20(32)	Full scale = +/-16g
        self.i2c.write8(0x21, 0x20)
        # LSM9DS0 Accl and Mag address, 0x1E(30)
        # Select control register5, 0x24(36)
        #		0x70(112)	Magnetic high resolution, Output data rate = 50Hz
        self.i2c.write8(0x24, 0x70)
        # LSM9DS0 Accl and Mag address, 0x1E(30)
        # Select control register6, 0x25(37)
        #		0x60(96)	Magnetic full scale selection = +/-12 gauss
        self.i2c.write8(0x25, 0x60)
        # LSM9DS0 Accl and Mag address, 0x1E(30)
        # Select control register7, 0x26(38)
        #		0x00(00)	Normal mode, Magnetic continuous conversion mode
        self.i2c.write8(0x26, 0x00)

    def read_value(self):

        data0 = self.i2c.read_U8(0x28)
        data1 = self.i2c.read_U8(0x29)

        # Convert the data
        x_accl = data1 * 256 + data0
        if x_accl > 32767:
            x_accl -= 65536

        # LSM9DS0 Accl and Mag address, 0x1E(30)
        # Read data back from 0x2A(42), 2 bytes
        # Y-Axis Accl LSB, Y-Axis Accl MSB
        data0 = self.i2c.read_U8(0x2A)
        data1 = self.i2c.read_U8(0x2B)

        # Convert the data
        y_accl = data1 * 256 + data0
        if y_accl > 32767:
            y_accl -= 65536

        # LSM9DS0 Accl and Mag address, 0x1E(30)
        # Read data back from 0x2C(44), 2 bytes
        # Z-Axis Accl LSB, Z-Axis Accl MSB
        data0 = self.i2c.read_U8(0x2C)
        data1 = self.i2c.read_U8(0x2D)

        # Convert the data
        z_accl = data1 * 256 + data0
        if z_accl > 32767:
            z_accl -= 65536

        return (x_accl, y_accl, z_accl)

class LSM9DS0RawMagDeviceDriver(I2CSensorDeviceDriver):
    def __init__(self, address=I2C_ACCL_ADDRESS, bus=None):
        I2CSensorDeviceDriver.__init__(self, address, bus)

        self.i2c.write8(0x20, 0x67)
        # LSM9DS0 Accl and Mag address, 0x1E(30)
        # Select control register2, 0x21(33)
        #		0x20(32)	Full scale = +/-16g
        self.i2c.write8(0x21, 0x20)
        # LSM9DS0 Accl and Mag address, 0x1E(30)
        # Select control register5, 0x24(36)
        #		0x70(112)	Magnetic high resolution, Output data rate = 50Hz
        self.i2c.write8(0x24, 0x70)
        # LSM9DS0 Accl and Mag address, 0x1E(30)
        # Select control register6, 0x25(37)
        #		0x60(96)	Magnetic full scale selection = +/-12 gauss
        self.i2c.write8(0x25, 0x60)
        # LSM9DS0 Accl and Mag address, 0x1E(30)
        # Select control register7, 0x26(38)
        #		0x00(00)	Normal mode, Magnetic continuous conversion mode
        self.i2c.write8(0x26, 0x00)

    def read_value(self):

        # LSM9DS0 Accl and Mag address, 0x1E(30)
        # Read data back from 0x08(08), 2 bytes
        # X-Axis Mag LSB, X-Axis Mag MSB
        data0 = self.i2c.read_U8(0x08)
        data1 = self.i2c.read_U8(0x09)

        # Convert the data
        x_mag = data1 * 256 + data0
        if x_mag > 32767:
            x_mag -= 65536

        # LSM9DS0 Accl and Mag address, 0x1E(30)
        # Read data back from 0x0A(10), 2 bytes
        # Y-Axis Mag LSB, Y-Axis Mag MSB
        data0 = self.i2c.read_U8(0x0A)
        data1 = self.i2c.read_U8(0x0B)

        # Convert the data
        y_mag = data1 * 256 + data0
        if y_mag > 32767:
            y_mag -= 65536

        # LSM9DS0 Accl and Mag address, 0x1E(30)
        # Read data back from 0x0C(12), 2 bytes
        # Z-Axis Mag LSB, Z-Axis Mag MSB
        data0 = self.i2c.read_U8(0x0C)
        data1 = self.i2c.read_U8(0x0D)

        # Convert the data
        z_mag = data1 * 256 + data0
        if z_mag > 32767:
            z_mag -= 65536


        return (x_mag, y_mag, z_mag)


class LSM9DS0CompasDeviceDriver(I2CSensorDeviceDriver):
    def __init__(self, is_flipped=False, address=I2C_ACCL_ADDRESS, bus=None):
        self.accl = LSM9DS0RawAcclDeviceDriver(address, bus)
        self.mag = LSM9DS0RawMagDeviceDriver(address, bus)

        self.is_flipped = is_flipped

        self.accXnorm = 0.0
        self.accYnorm = 0.0
        self.pitch = 0.0
        self.roll = 0.0
        self.magXcomp = 0.0
        self.magYcomp = 0.0
        self.scaledMag = [0.0, 0.0, 0.0]

        self.oldXMagRawValue = 0
        self.oldYMagRawValue = 0
        self.oldZMagRawValue = 0
        self.oldXAccRawValue = 0
        self.oldYAccRawValue = 0
        self.oldZAccRawValue = 0

        self.magRaw = [0, 0, 0]
        self.accRaw = [0, 0, 0]

    def read_value(self):

        self.magRaw = list(self.mag, self.mag.read_value)
        self.accRaw = list(self.accl.read_value)

        self.magRaw[0] = self.magRaw[0] * MAG_LPF_FACTOR + self.oldXMagRawValue*(1 - MAG_LPF_FACTOR)
        self.magRaw[1] = self.magRaw[1] * MAG_LPF_FACTOR + self.oldYMagRawValue*(1 - MAG_LPF_FACTOR)
        self.magRaw[2] = self.magRaw[2] * MAG_LPF_FACTOR + self.oldZMagRawValue*(1 - MAG_LPF_FACTOR)
        self.accRaw[0] = self.accRaw[0] * ACC_LPF_FACTOR + self.oldXAccRawValue*(1 - ACC_LPF_FACTOR)
        self.accRaw[1] = self.accRaw[1] * ACC_LPF_FACTOR + self.oldYAccRawValue*(1 - ACC_LPF_FACTOR)
        self.accRaw[2] = self.accRaw[2] * ACC_LPF_FACTOR + self.oldZAccRawValue*(1 - ACC_LPF_FACTOR)

        self.oldXMagRawValue = self.magRaw[0]
        self.oldYMagRawValue = self.magRaw[1]
        self.oldZMagRawValue = self.magRaw[2]
        self.oldXAccRawValue = self.accRaw[0]
        self.oldYAccRawValue = self.accRaw[1]
        self.oldZAccRawValue = self.accRaw[2]

        #Apply hard iron calibration
        self.magRaw[0] -= (magXmin + magXmax) /2
        self.magRaw[1] -= (magYmin + magYmax) /2
        self.magRaw[2] -= (magZmin + magZmax) /2

        #Apply soft iron calibration
        self.scaledMag[0] = (self.magRaw[0] - magXmin) / (magXmax - magXmin) * 2 - 1
        self.scaledMag[1] = (self.magRaw[1] - magYmin) / (magYmax - magYmin) * 2 - 1
        self.scaledMag[2] = (self.magRaw[2] - magZmin) / (magZmax - magZmin) * 2 - 1

        if self.is_flipped:
            self.accRaw[0] = -self.accRaw[0]
            self.accRaw[1] = -self.accRaw[1]

        #Compute heading
        heading = 180 * math.atan2(self.magRaw[1], self.magRaw[0]) / math.pi

        #Convert heading to 0 - 360
        if heading < 0:
            heading += 360

        #Normalize accelerometer raw values.
        accXnorm = self.accRaw[0] / math.sqrt(self.accRaw[0] * self.accRaw[0] + self.accRaw[1] * self.accRaw[1] + self.accRaw[2] * self.accRaw[2])
        accYnorm = self.accRaw[1] / math.sqrt(self.accRaw[0] * self.accRaw[0] + self.accRaw[1] * self.accRaw[1] + self.accRaw[2] * self.accRaw[2])

        #Calculate pitch and roll
        pitch = math.asin(accXnorm)
        roll = -math.asin(accYnorm / math.cos(pitch))

        #Calculate the new tilt compensated values
        magXcomp = self.magRaw[0] * math.cos(pitch) + self.magRaw[2] * math.sin(pitch)
        magYcomp = self.magRaw[0] * math.sin(roll) * math.sin(pitch) + self.magRaw[1] * math.cos(roll) - self.magRaw[2] * math.sin(roll) * math.cos(pitch)

        #Calculate heading
        heading = 180 * math.atan2(magYcomp, magXcomp)/math.pi

        #Convert heading to 0 - 360
        if heading < 0:
            heading += 360

        return heading