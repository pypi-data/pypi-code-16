import sys
import time
from kervi.hal import I2CSensorDevice

class TSL2561Device(I2CSensorDevice):
    def __init__(self, address=0x39, bus=None):
        I2CSensorDevice.__init__(self, address, bus)
        self.gain = 0 # no gain preselected
        self.i2c.write8(0x80, 0x03)     # enable the device
        self.pause = 1
        self.gain = 0

    def set_gain(self, gain=1):
        """ Set the gain """
        if gain == 1:
            self.i2c.write8(0x81, 0x02)     # set gain = 1X and timing = 402 mSec
        else:
            self.i2c.write8(0x81, 0x12)     # set gain = 16X and timing = 402 mSec

        time.sleep(self.pause)              # pause for integration (self.pause must be bigger than integration time)


    def read_word(self, reg):
        try:
            wordval = self.i2c.read_U16(reg)
            newval = self.i2c.reverseByteOrder(wordval)
            return newval
        except IOError:
            print("Error accessing 0x%02X: Check your I2C address" % self.i2c.address)
            return -1


    def read_full(self, reg=0x8C):
        """Reads visible+IR diode from the I2C device"""
        return self.read_word(reg)

    def read_ir(self, reg=0x8E):
        """Reads IR only diode from the I2C device"""
        return self.read_word(reg)

    def read_value(self):
        """Grabs a lux reading either with autoranging (gain=0) or with a specified gain (1, 16)"""
        if self.gain == 1 or self.gain == 16:
            self.set_gain(self.gain)
            ambient = self.read_full()
            IR = self.read_ir()
        elif self.gain == 0: # auto gain
            self.set_gain(16) # first try highGain
            ambient = self.read_full()
            if ambient < 65535:
                ir_reading = self.read_ir()
            if ambient >= 65535 or IR >= 65535: # value(s) exeed(s) datarange
                self.set_gain(1) # set lowGain
                ambient = self.read_full()
                ir_reading = self.read_ir()

        if self.gain == 1:
            ambient *= 16    # scale 1x to 16x
            ir_reading *= 16         # scale 1x to 16x

        ratio = (ir_reading / float(ambient)) # changed to make it run under python 2

        if (ratio >= 0) & (ratio <= 0.52):
            lux = (0.0315 * ambient) - (0.0593 * ambient * (ratio**1.4))
        elif ratio <= 0.65:
            lux = (0.0229 * ambient) - (0.0291 * ir_reading)
        elif ratio <= 0.80:
            lux = (0.0157 * ambient) - (0.018 * ir_reading)
        elif ratio <= 1.3:
            lux = (0.00338 * ambient) - (0.0026 * ir_reading)
        elif ratio > 1.3:
            lux = 0

        return lux
