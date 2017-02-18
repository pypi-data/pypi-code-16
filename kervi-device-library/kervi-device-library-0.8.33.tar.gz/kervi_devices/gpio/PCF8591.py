from kervi.hal import I2CGPIODevice

class I2CaddressOutOfBoundsError(Exception):
    message = 'I2C Exception: I2C Address Out of Bounds'

# Exception class for a channel number out of bounds
class PCF8591PchannelOutOfBoundsError(Exception):
    message = 'PCF8591P Exception: ADC Channel Out of Bounds'

# Exception class for a DAC value out of bounds
class PCF8591PDACvalueOutOfBoundsError(Exception):
    message = 'PCF8591P Exception: DAC Output Value Out of Bounds'

class PCF8591P(I2CGPIODevice):

    # Constructor
    def __init__(self, address, bus):
        I2CGPIODevice.__init__(self, address, bus)
        self._dac_enabled = 0x00

    def get(self, channel):
        """Read single ADC Channel"""
        checked_channel = self._check_channel_no(channel)
        self.i2c.write_raw8(checked_channel  | self._dac_enabled)
        reading = self.i2c.read_raw8() # seems to need to throw away first reading
        reading = self.i2c.read_raw8() # read A/D
        return reading

    def set(self, channel, state):
        """Set DAC value and enable output"""
        checked_val = self._check_dac_val(state)
        self._dac_enabled = 0x40
        self.i2c.write8(self._dac_enabled, checked_val)

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
            raise PCF8591PchannelOutOfBoundsError
        elif chan < 0:
            raise PCF8591PchannelOutOfBoundsError
        elif chan > 3:
            raise PCF8591PchannelOutOfBoundsError
        return chan

    # Check if DAC output value is within bounds
    def _check_dac_val(self, val):
        if type(val) is not int:
            raise PCF8591PDACvalueOutOfBoundsError
        elif val < 0:
            raise PCF8591PDACvalueOutOfBoundsError
        elif val > 255:
            raise PCF8591PDACvalueOutOfBoundsError
        return val
