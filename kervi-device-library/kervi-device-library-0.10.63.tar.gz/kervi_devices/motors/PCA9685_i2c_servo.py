from kervi_devices.pwm.PCA9685 import PCA9685DeviceDriver
from kervi.hal.motor_controller import MotorControllerBoard, ServoMotor, ServoMotorControllerBase






# Configure min and max servo pulse lengths
servo_min = 150  # Min pulse length out of 4096
servo_max = 600  # Max pulse length out of 4096

# Helper function to make setting a servo pulse width simpler.


class _ServoController(ServoMotorControllerBase):
    def __init__(self, pwm_device):
        ServoMotorControllerBase.__init__(self, "PCA9685", 16)
        self.pwm_device = pwm_device

    def _set_position(self, channel, position, adjust_min=0, adjust_max=0, adjust_center=0):
        pulse_min = 200 + 200 * adjust_min
        pulse_center = 400 + 400 * adjust_center
        pulse_max = 600 + 600 * adjust_max

        if position == 0:
            pulse = pulse_center
        elif position > 0:
            pulse = (pulse_max - pulse_center) * (position/100.0)
        else:
            pulse = (pulse_center - pulse_min) * (position/100.0)

        #pulse_length = 1000000    # 1,000,000 us per second
        #pulse_length //= 60       # 60 Hz
        #pulse_length //= 4096     # 12 bits of resolution
        #pulse *= 1000
        #pulse //= pulse_length
        self.pwm_device.set_pwm(channel, 0, int(pulse))

class PCA9685ServoBoard(MotorControllerBoard):
    def __init__(self, address=0x60, bus=None):
        self.pwm = PCA9685DeviceDriver(address, bus)
        self.pwm.set_pwm_freq(1600)

        MotorControllerBoard.__init__(
            self,
            "PCA9685 servohat hat",
            servo_controller = _ServoController(self.pwm),
            
        )

