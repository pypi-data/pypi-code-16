from kervi import hal
from kervi_devices.gpio.MCP230XX import MCP23017DeviceDriver
from kervi_devices.displays.HD44780 import HD44780RGBDeviceDriver

class I2CAdafruitCharLCDPlate(HD44780RGBDeviceDriver):
    """Class to represent and interact with an Adafruit Raspberry Pi character
    LCD plate."""

    def __init__(self, address=0x20, busnum=hal.default_i2c_bus(), cols=16, lines=2):
        """Initialize the character LCD plate.  Can optionally specify a separate
        I2C address or bus number, but the defaults should suffice for most needs.
        Can also optionally specify the number of columns and lines on the LCD
        (default is 16x2).
        """
        # Configure MCP23017 device.
        self._mcp = MCP23017DeviceDriver(address=address, bus=busnum)
        # Set LCD R/W pin to low for writing only.
        self._mcp.define_as_output(LCD_PLATE_RW)
        self._mcp.set(LCD_PLATE_RW, False)
        # Set buttons as inputs with pull-ups enabled.
        for button in (SELECT, RIGHT, DOWN, UP, LEFT):
            self._mcp.define_as_input(button, True)
        # Initialize LCD (with no PWM support).
        super(I2CAdafruitCharLCDPlate, self).__init__(LCD_PLATE_RS, LCD_PLATE_EN,
            LCD_PLATE_D4, LCD_PLATE_D5, LCD_PLATE_D6, LCD_PLATE_D7, cols, lines,
            LCD_PLATE_RED, LCD_PLATE_GREEN, LCD_PLATE_BLUE, enable_pwm=False, 
            gpio=self._mcp)

    def is_pressed(self, button):
        """Return True if the provided button is pressed, False otherwise."""
        if button not in set((SELECT, RIGHT, DOWN, UP, LEFT)):
            raise ValueError('Unknown button, must be SELECT, RIGHT, DOWN, UP, or LEFT.')
        return self._mcp.get(button)
