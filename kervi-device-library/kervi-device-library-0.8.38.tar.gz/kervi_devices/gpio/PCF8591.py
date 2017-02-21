from kervi.hal import I2CGPIODevice, DeviceChannelOutOfBoundsError, DACValueOutOfBoundsError

class PCF8591Driver(I2CGPIODevice):

    # Constructor
    def __init__(self, address, bus):
        I2CGPIODevice.__init__(self, address, bus)
        self._dac_enabled = 0x00

    def device_name(self):
        return "PFC8591"

    def get(self, channel):
        """Read single ADC Channel"""
        checked_channel = self._check_channel_no(channel)
        self.i2c.write_raw8(checked_channel  | self._dac_enabled)
        reading = self.i2c.read_raw8() # seems to need to throw away first reading
        reading = self.i2c.read_raw8() # read A/D
        return reading / 255.0

    def set(self, channel, state):
        """Set DAC value and enable output"""
        checked_val = self._check_dac_val(channel, state)
        self._dac_enabled = 0x40
        self.i2c.write8(self._dac_enabled, checked_val * 255)

    # Enable DAC output
    def enable_dac(self):
        self._dac_enabled = 0x40
        self.i2c.write_raw8(self._dac_enabled)

    # Disable DAC output
    def disable_dac(self):
        self.__dac_enabled = 0x00
        self.i2c.write_raw8(self.__dac_enabled)

    # Check if ADC channel number is within bounds
    def _check_channel_no(self, chan):
        if type(chan) is not int:
            raise DeviceChannelOutOfBoundsError(self.device_name, chan)
        elif chan < 0:
            raise DeviceChannelOutOfBoundsError(self.device_name, chan)
        elif chan > 3:
            raise DeviceChannelOutOfBoundsError(self.device_name, chan)
        return chan

    # Check if DAC output value is within bounds
    def _check_dac_val(self, channel, val):
        if type(val) is not float:
            raise DACValueOutOfBoundsError(self.device_name, channel, val)
        elif val < 0:
            raise DACValueOutOfBoundsError(self.device_name, channel, val)
        elif val > 1:
            raise DACValueOutOfBoundsError(self.device_name, channel, val)
        return val
