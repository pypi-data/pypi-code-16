from kervi.hal import SensorDeviceDriver

class DummySensorDeviceDriver(SensorDeviceDriver):
    def __init__(self):
        self.value = 0
        self.delta = 4

    def read_value(self):
        self.value += self.delta
        if self.value == 100:
            self.delta *= -1
        return self.value

    def type(self):
        return "counter"

    def unit(self):
        return "%"