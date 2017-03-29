from kervi.hal.motor_controller import MotorControllerBoard, ServoMotorControllerBase, DCMotorControllerBase, StepperMotorControllerBase

class _DummyDCMotorDeviceDriver(DCMotorControllerBase):
    def __init__(self):
        DCMotorControllerBase.__init__(self, "Dummy dc motor driver", 2)

    def _set_speed(self, motor, speed):
        print("set speed:", motor, speed)

class _DummyStepperMotorDeviceDriver(StepperMotorControllerBase):
    def __init__(self):
        StepperMotorControllerBase.__init__(self, "Dummy stepper motor driver", 2)
        self.steps = 0

    def _step(self, motor, style):
        print("step:", motor, style)

    def _release(self, motor):
        print("release step motor:", motor)

    def run(self, step_interval):
        print("stepper, run")


class _DummyServoController(ServoMotorControllerBase):
    def __init__(self):
        ServoMotorControllerBase.__init__(self, "Dummy servo controller", 4)

    def _set_position(self, channel, position, adjust_min=0, adjust_max=0, adjust_center=0):
        print("servo set position", channel, position)

class DummyMotorBoard(MotorControllerBoard):
    def __init__(self):
        MotorControllerBoard.__init__(
            self,
            "Dummy motor board",
            dc_controller=_DummyDCMotorDeviceDriver(),
            stepper_controller=_DummyStepperMotorDeviceDriver(),
            servo_controller = _DummyServoController(),
        )
