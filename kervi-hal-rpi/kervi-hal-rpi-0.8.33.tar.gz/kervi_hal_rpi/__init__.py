from . import gpio_driver
from . import i2c_driver


def get_gpio_driver():
    return gpio_driver.GPIODriver()

def get_i2c_driver(address, bus):
    return i2c_driver.I2CDeviceDriver(address, bus)
