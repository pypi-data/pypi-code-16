
import time
from .baro import Barometer
from .temperature import TemperatureSensor
from .imu import Accelerometer, Magnetometer, Gyroscope
from .rgb_ir import RgbIrSensor
from .uva import UvaSensor
from .rtc import RealTimeClock
from .leds import Leds
from .arducam import Camera

barometer = Barometer(None, 0x76)
bottom_thermometer = TemperatureSensor(None, 0x48)
top_thermometer = TemperatureSensor(None, 0x49)
accelerometer = Accelerometer(None, 0x1D)
magnetometer = Magnetometer(None, 0x1D)
gyroscope = Gyroscope(None, 0x6b)
rgb_ir_sensor = RgbIrSensor(None, 0x52)
uva_sensor = UvaSensor(None, 0x38)
real_time_clock = RealTimeClock(None, 0x51)

sensors = [
    barometer,
    bottom_thermometer,
    top_thermometer,
    accelerometer,
    gyroscope,
    rgb_ir_sensor,
    uva_sensor,
    real_time_clock
]

for sensor in sensors:
    sensor.configure({})

leds = Leds()
camera = Camera()


__all__ = (
    'barometer',
    'bottom_thermometer',
    'top_thermometer',
    'accelerometer',
    'gyroscope',
    'magnetometer',
    'rgb_ir_sensor',
    'uva_sensor',
    'real_time_clock',
    'leds',
    'camera'
)






