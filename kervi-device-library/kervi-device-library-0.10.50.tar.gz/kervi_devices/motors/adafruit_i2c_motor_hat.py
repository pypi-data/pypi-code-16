
import time

from kervi_devices.pwm.PCA9685 import PCA9685DeviceDriver
from kervi.hal.motor_controller import MotorControllerBoard, DCMotor, DCMotorControllerBase, StepperMotor, StepperMotorControllerBase


FORWARD = 1
BACKWARD = 2
BRAKE = 3
RELEASE = 4

SINGLE = 1
DOUBLE = 2
INTERLEAVE = 3
MICROSTEP = 4


class _DCMotor(DCMotor):
    def __init__(self, pwm_device, num):
        self.pwm_device = pwm_device
        self.motornum = num
        pwm = in1 = in2 = 0

        if num == 0:
            pwm = 8
            in2 = 9
            in1 = 10
        elif num == 1:
            pwm = 13
            in2 = 12
            in1 = 11
        elif num == 2:
            pwm = 2
            in2 = 3
            in1 = 4
        elif num == 3:
            pwm = 7
            in2 = 6
            in1 = 5
        else:
            raise NameError('MotorHAT Motor must be between 1 and 4 inclusive')
        self.PWMpin = pwm
        self.IN1pin = in1
        self.IN2pin = in2

    def run(self, speed):
        if speed > 0:
            self.pwm_device.set(self.IN2pin, 0)
            self.pwm_device.set(self.IN1pin, 1)
        if speed < 0:
            self.pwm_device.set(self.IN1pin, 0)
            self.pwm_device.set(self.IN2pin, 1)
        if speed == 0:
            self.pwm_device.set(self.IN1pin, 0)
            self.pwm_device.set(self.IN2pin, 0)

        self.pwm_device.set_pwm(self.PWMpin, 0, abs(int(4095 * (speed/100))))

class _DCMotorController(DCMotorControllerBase):
    def __init__(self, pwm):
        self.pwm = pwm
        DCMotorControllerBase.__init__(self, "Adafruit DC + Stepper hat:dc", 4)
        self._motors = []


    def __getitem__(self, motor_num):
        for motor in self._motors:
            if motor.motornum == motor_num:
                return motor
        motor = _DCMotor(self.pwm, motor_num)
        self._motors += [motor]
        return motor

    def stop_all(self):
        for motor in self._motors:
            motor.run(0)

class _StepperMotor(StepperMotor):
    MICROSTEPS = 8
    MICROSTEP_CURVE = [0, 50, 98, 142, 180, 212, 236, 250, 255]

    #MICROSTEPS = 16
    # a sinusoidal curve NOT LINEAR!
    #MICROSTEP_CURVE = [0, 25, 50, 74, 98, 120, 141, 162, 180, 197, 212, 225, 236, 244, 250, 253, 255]

    def __init__(self, pwm_device, num, steps=200):
        self.pwm = pwm_device
        self.revsteps = steps
        self.motornum = num
        self.sec_per_step = 0.1
        self.steppingcounter = 0
        self.currentstep = 0

        num -= 1

        if num == 0:
            self.PWMA = 8
            self.AIN2 = 9
            self.AIN1 = 10
            self.PWMB = 13
            self.BIN2 = 12
            self.BIN1 = 11
        elif num == 1:
            self.PWMA = 2
            self.AIN2 = 3
            self.AIN1 = 4
            self.PWMB = 7
            self.BIN2 = 6
            self.BIN1 = 5
        else:
            raise NameError('MotorHAT Stepper must be between 1 and 2 inclusive')

    def setSpeed(self, rpm):
        self.sec_per_step = 60.0 / (self.revsteps * rpm)
        self.steppingcounter = 0

    def oneStep(self, dir, style):
        pwm_a = pwm_b = 255

        # first determine what sort of stepping procedure we're up to
        if style == SINGLE:
            if (self.currentstep//(self.MICROSTEPS//2)) % 2:
                # we're at an odd step, weird
                if dir == FORWARD:
                    self.currentstep += self.MICROSTEPS//2
                else:
                    self.currentstep -= self.MICROSTEPS//2
            else:
                # go to next even step
                if dir == FORWARD:
                    self.currentstep += self.MICROSTEPS
                else:
                    self.currentstep -= self.MICROSTEPS
        if style == DOUBLE:
            if not self.currentstep//(self.MICROSTEPS//2) % 2:
                # we're at an even step, weird
                if dir == FORWARD:
                    self.currentstep += self.MICROSTEPS//2
                else:
                    self.currentstep -= self.MICROSTEPS//2
            else:
                # go to next odd step
                if dir == FORWARD:
                    self.currentstep += self.MICROSTEPS
                else:
                    self.currentstep -= self.MICROSTEPS
        if style == INTERLEAVE:
            if dir == FORWARD:
                self.currentstep += self.MICROSTEPS//2
            else:
                self.currentstep -= self.MICROSTEPS//2

        if style == MICROSTEP:
            if dir == FORWARD:
                self.currentstep += 1
            else:
                self.currentstep -= 1

                # go to next 'step' and wrap around
                self.currentstep += self.MICROSTEPS * 4
                self.currentstep %= self.MICROSTEPS * 4

            pwm_a = pwm_b = 0
            if (self.currentstep >= 0) and (self.currentstep < self.MICROSTEPS):
                pwm_a = self.MICROSTEP_CURVE[self.MICROSTEPS - self.currentstep]
                pwm_b = self.MICROSTEP_CURVE[self.currentstep]
            elif (self.currentstep >= self.MICROSTEPS) and (self.currentstep < self.MICROSTEPS*2):
                pwm_a = self.MICROSTEP_CURVE[self.currentstep - self.MICROSTEPS]
                pwm_b = self.MICROSTEP_CURVE[self.MICROSTEPS*2 - self.currentstep]
            elif (self.currentstep >= self.MICROSTEPS*2) and (self.currentstep < self.MICROSTEPS*3):
                pwm_a = self.MICROSTEP_CURVE[self.MICROSTEPS*3 - self.currentstep]
                pwm_b = self.MICROSTEP_CURVE[self.currentstep - self.MICROSTEPS*2]
            elif (self.currentstep >= self.MICROSTEPS*3) and (self.currentstep < self.MICROSTEPS*4):
                pwm_a = self.MICROSTEP_CURVE[self.currentstep - self.MICROSTEPS*3]
                pwm_b = self.MICROSTEP_CURVE[self.MICROSTEPS*4 - self.currentstep]


        # go to next 'step' and wrap around
        self.currentstep += self.MICROSTEPS * 4
        self.currentstep %= self.MICROSTEPS * 4

        # only really used for microstepping, otherwise always on!
        self.pwm.set_pwm(self.PWMA, 0, pwm_a*16)
        self.pwm.set_pwm(self.PWMB, 0, pwm_b*16)

        # set up coil energizing!
        coils = [0, 0, 0, 0]

        if style == MICROSTEP:
            if (self.currentstep >= 0) and (self.currentstep < self.MICROSTEPS):
                coils = [1, 1, 0, 0]
            elif (self.currentstep >= self.MICROSTEPS) and (self.currentstep < self.MICROSTEPS*2):
                coils = [0, 1, 1, 0]
            elif (self.currentstep >= self.MICROSTEPS*2) and (self.currentstep < self.MICROSTEPS*3):
                coils = [0, 0, 1, 1]
            elif (self.currentstep >= self.MICROSTEPS*3) and (self.currentstep < self.MICROSTEPS*4):
                coils = [1, 0, 0, 1]
        else:
            step2coils = [
                [1, 0, 0, 0],
                [1, 1, 0, 0],
                [0, 1, 0, 0],
                [0, 1, 1, 0],
                [0, 0, 1, 0],
                [0, 0, 1, 1],
                [0, 0, 0, 1],
                [1, 0, 0, 1]
            ]
            coils = step2coils[self.currentstep//(self.MICROSTEPS//2)]

        #print "coils state = " + str(coils)
        self.pwm.set(self.AIN2, coils[0])
        self.pwm.set(self.BIN1, coils[1])
        self.pwm.set(self.AIN1, coils[2])
        self.pwm.set(self.BIN2, coils[3])

        return self.currentstep

    def step(self, steps, direction, stepstyle):
        s_per_s = self.sec_per_step
        lateststep = 0

        if stepstyle == INTERLEAVE:
            s_per_s = s_per_s / 2.0
        if stepstyle == MICROSTEP:
            s_per_s /= self.MICROSTEPS
            steps *= self.MICROSTEPS

        print("{} sec per step".format(s_per_s))

        for s in range(steps):
            lateststep = self.oneStep(direction, stepstyle)
            time.sleep(s_per_s)

        if stepstyle == MICROSTEP:
            # this is an edge case, if we are in between full steps, lets just keep going
            # so we end on a full step
            while (lateststep != 0) and (lateststep != self.MICROSTEPS):
                lateststep = self.oneStep(direction, stepstyle)
                time.sleep(s_per_s)

class _StepperMotorController(StepperMotorControllerBase):
    def __init__(self, pwm):
        self.pwm = pwm
        StepperMotorControllerBase.__init__(self, "Adafruit DC + Stepper hat:servo", 2)

    def __getitem__(self, motor):
        return _StepperMotor(self.pwm, motor)

class AdafruitMotorHAT(MotorControllerBoard):
    def __init__(self, address=0x60, bus=None):
        self.pwm = PCA9685DeviceDriver(address, bus)
        self.pwm.set_pwm_freq(1600)

        MotorControllerBoard.__init__(
            self,
            "Adafruit DC + Stepper hat",
            dc_controller=_DCMotorController(self.pwm),
            stepper_controller=_StepperMotorController(self.pwm)
        )
