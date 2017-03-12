'''
Adafruit compatible using BaseGPIO class to represent a PCF8574/A IO expander
Copyright (C) 2015 Sylvan Butler
Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.'''



from kervi.hal import I2CGPIODeviceDriver


IN = 1
OUT = 0
HIGH = True
LOW = False


class PCF8574DeviceDriver(I2CGPIODeviceDriver):
    """
    Class to represent a PCF8574 or PCF8574A GPIO extender.
    """
    def __init__(self, address=0x27, bus=None):
        I2CGPIODeviceDriver.__init__(self, address, bus)
        self.__name__ = \
            "PCF8574" if address in range(0x20, 0x28) else \
            "PCF8574A" if address in range(0x38, 0x40) else \
            "Bad address for PCF8574(A): 0x%02X not in range [0x20..0x27, 0x38..0x3F]" % address
        if self.__name__[0] != 'P':
            raise ValueError(self.__name__)
        
        # Buffer register values so they can be changed without reading.
        self.iodir = 0xFF  # Default direction to all inputs is in
        self.gpio = 0x00
        self._write_pins()

    @property
    def device_name(self):
        return self.__name__

    @property
    def num_gpio(self):
        return 8

    def _write_pins(self):
        self.i2c.writeRaw8(self.gpio | self.iodir)

    def _read_pins(self):
        return self.i2c.readRaw8() & self.iodir

    def define_as_input(self, channel):
        self._validate_channel(channel)
        self.iodir = self._bit2(self.iodir, channel, IN)
        self._write_pins()

    def define_as_output(self, channel):
        self._validate_channel(channel)
        self.iodir = self._bit2(self.iodir, channel, OUT)
        self._write_pins()

    def set(self, pin, value):
        self._validate_channel(pin)
        self.gpio = self._bit2(self.gpio, pin, bool(value))
        self._write_pins()

    def get(self, pin):
        self._validate_channel(pin)
        inp = self._read_pins()
        return bool(inp & (1<<pin))
