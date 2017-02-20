from .i2c import I2cDevice
from collections import namedtuple


RgbIrMeasurement = namedtuple(
    'RgbIrMeasurement',
    'red green blue ir'
)


def _parse_rgb_ir_bytes(colour_data):
    return 0.0, 0.0, 0.0, 0.0


class RgbIrSensor(I2cDevice):
    def self_test(self):
        id = self.read(0x06, 1)[0]
        return id == 0xB2

    def configure(self, args):
        # set light sensor enabled, colour sensing mode.
        self.pack_and_write(0x00, 'B', 0b00000110)
        super().configure(args)

    def measure(self):
        """
        :return: R, G, B and IR Channel readings and a fraction of the total.
        """
        return RgbIrMeasurement(*_parse_rgb_ir_bytes(0.0))

    @property
    def red(self):
        return self.measure()[0]

    @property
    def green(self):
        return self.measure()[1]

    @property
    def blue(self):
        return self.measure()[2]

    @property
    def ir(self):
        return self.measure()[3]
