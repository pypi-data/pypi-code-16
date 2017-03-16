

from kervi.hal import i2c
from kervi.hal.dc_motor_controller import DCMotorControllerBase

MOTOR_SPEED_SET = 0x82
PWM_FREQUENCE_SET = 0x84
DIRECTION_SET = 0xaa
MOTOR_SET_A = 0xa1
MOTOR_SET_B = 0xa5
NOTHING = 0x01
ENABLE_STEPPER = 0x1a
UNENABLE_STEPPER = 0x1b
STEPERNU = 0x1c
I2C_MOTOR_DRIVER_ADD = 0x0f #Set the address of the I2CMotorDriver

BOTH_CLOCK_WISE = 0x0a
BOTH_ANTI_CLOCK_WISE = 0x05
M1_CW_M2_ACW = 0x06
M1_ACW_M2CW = 0x09

class MotorDeviceDriver(DCMotorControllerBase):
    def __init__(self, address=I2C_MOTOR_DRIVER_ADD, bus=None):
        DCMotorControllerBase.__init__(self, "Grove i2c motor driver", 2)
        self.i2c = i2c(address, bus)
        self.m1_speed = 0
        self.m2_speed = 0

        self.m1_direction = 1
        self.m2_direction = 1

    def _set_speed(self, motor, speed):
        if motor == 1:
            self.m1_speed = Map(speed, 0, 100, 0, 255)
            if speed >= 0:
                this.m1_direction = 1
            else:
                this.m1_direction = -1

        else:
            self.m2_speed = Map(speed, 0, 100, 0, 255)
            if speed >= 0:
                this.m2_direction = 1
            else:
                this.m2_direction = -1

        if _M1_direction == 1 and _M2_direction == 1:
            direction = BOTH_CLOCK_WISE
        if _M1_direction == 1 and _M2_direction == -1:
            direction = M1_CW_M2_ACW
        if _M1_direction == -1 and _M2_direction == 1:
            direction = M1_ACW_M2CW
        if _M1_direction == -1 and _M2_direction == -1:
            direction = BOTH_ANTI_CLOCK_WISE

        i2c.write_list(MOTOR_SPEED_SET, [self.m1_speed, self.m2_speed])
        bus.write_list(DIRECTION_SET, [direction, NOTHING])
