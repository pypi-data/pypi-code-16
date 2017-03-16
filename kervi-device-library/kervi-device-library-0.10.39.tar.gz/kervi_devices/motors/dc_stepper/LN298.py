from kervi.hal.dc_motor_controller import DCMotorControllerBase

class LN298MotorController(DCMotorControllerBase):
    def __init__(self, ena, in1, in2, enb, in3, in4):
        DCMotorControllerBase.__init__(self, "LN298", 2)

        self._motors = [(ena, in1, in2), (enb, in3, in4)]
        for motor in self._motors:
            en, in1, in2 = motor
            en.define_as_pwm()
            in1.define_as_output()
            in2.define_as_output()

    def _set_speed(self, motor, speed):
        """
        Change the speed of a motor on the controller.

        :param motor: The motor to change.
        :type motor: ``int``

        :param speed: Speed from -100 to +100, 0 is stop
        :type speed: ``int``

        """
        self._validate_motor(motor)
        en, in1, in2 = self._motors[motor-1]

        if speed == 0:
            en.pwm_stop()
            in1.set(False)
            in2.set(False)
        elif speed > 0:
            en.pwm_start(abs(speed))
            in1.set(True)
            in2.set(False)
        else:
            en.pwm_start(abs(speed))
            in1.set(False)
            in2.set(True)
