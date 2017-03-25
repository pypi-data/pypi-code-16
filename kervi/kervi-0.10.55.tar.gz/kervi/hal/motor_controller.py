import time

class _MotorNumOutOfBoundsError(Exception):
    def __init__(self, device_name, motor):
        super(_MotorNumOutOfBoundsError, self).__init__(
            '{0} Exception: Motor num out of Bounds, motor={1}'.format(device_name, motor)
        )

class DCMotor(object):
    def __init__(self, device, motor):
        self._device = device
        self._motor = motor

    def set_speed(self, speed):
        self._device._set_speed(self._motor, speed)

class DCMotorControllerBase(object):
    def __init__(self, device_name, num_motors):
        self._num_motors = num_motors
        self._device_name = device_name

    def __getitem__(self, motor):
        return DCMotor(self, motor)


    def _validate_motor(self, motor):
        if motor < 0 or motor > self._num_motors:
            raise _MotorNumOutOfBoundsError(self._device_name, motor)

    @property
    def device_name(self):
        """Motor controller device name"""
        return self._device_name

    @property
    def num_motors(self):
        """Number of DC motors this motor controller can handle"""
        return self._num_motors

    def _set_speed(self, motor, speed):
        """
        Change the speed of a motor on the controller.

        :param motor: The motor to change.
        :type motor: ``int``

        :param speed: Speed from -100 to +100, 0 is stop
        :type speed: ``int``

        """
        raise NotImplementedError

    def stop_all(self):
        """Stops all motors connected to the motor controller"""
        raise NotImplementedError


class StepperMotor(object):
    SINGLE = 1
    DOUBLE = 2
    INTERLEAVE = 3
    MICROSTEP = 4
    MICROSTEPS = 8

    FORWARD = 1

    def __init__(self, device, motor):
        self._device = device
        self._motor = motor
        self._step_style = self.SINGLE
        self._step_interval = 1
        self.stepping_counter = 0
        self.current_step = 0

    @property
    def step_style(self):
        return self._step_style

    @step_style.setter
    def step_style(self, value):
        self._step_style = value

    @property
    def step_interval(self):
        self.stepping_counter = 0
        return self._step_interval

    @step_interval.setter
    def step_interval(self, value):
        self._step_interval = value

    def _step(self, dir, style):
        raise NotImplementedError

    def step(self, steps, direction = 1, step_style=None):
        s_per_s = self._step_interval
        lateststep = 0
        if not step_style:
            step_style = self.step_style

        if step_style == self.INTERLEAVE:
            s_per_s = s_per_s / 2.0
        if step_style == self.MICROSTEP:
            s_per_s /= self.MICROSTEPS
            steps *= self.MICROSTEPS

        #print("{} sec per step".format(s_per_s))

        for s in range(steps):
            lateststep = self._step(direction, step_style)
            time.sleep(s_per_s)

        if step_style == self.MICROSTEP:
            # this is an edge case, if we are in between full steps, lets just keep going
            # so we end on a full step
            while (lateststep != 0) and (lateststep != self.MICROSTEPS):
                lateststep = self._step(direction, step_style)
                time.sleep(s_per_s)

class StepperMotorControllerBase(object):
    def __init__(self, device_name, num_motors):
        self._num_motors = num_motors
        self._device_name = device_name

    def __getitem__(self, motor):
        return StepperMotor(self, motor)


    def _validate_motor(self, motor):
        if motor < 0 or motor > self._num_motors:
            raise _MotorNumOutOfBoundsError(self._device_name, motor)

    @property
    def device_name(self):
        """Motor controller device name"""
        return self._device_name

    @property
    def num_motors(self):
        """Number of DC motors this motor controller can handle"""
        return self._num_motors

    def _set_speed(self, motor, speed):
        """
        Change the speed of a motor on the controller.

        :param motor: The motor to change.
        :type motor: ``int``

        :param speed: Speed from -100 to +100, 0 is stop
        :type speed: ``int``

        """
        raise NotImplementedError

    def stop_all(self):
        """Stops all motors connected to the motor controller"""
        raise NotImplementedError


class ServoMotor(object):
    def __init__(self, device, motor):
        self._device = device
        self._motor = motor

    def speed(self, speed):
        self._device._set_speed(self._motor, speed)

class ServoMotorControllerBase(object):
    def __init__(self, device_name, num_motors):
        self._num_motors = num_motors
        self._device_name = device_name

    def __getitem__(self, motor):
        return ServoMotor(self, motor)

    def _validate_motor(self, motor):
        if motor < 0 or motor > self._num_motors:
            raise _MotorNumOutOfBoundsError(self._device_name, motor)

    @property
    def device_name(self):
        """Motor controller device name"""
        return self._device_name

    @property
    def num_motors(self):
        """Number of DC motors this motor controller can handle"""
        return self._num_motors

    def _set_speed(self, motor, speed):
        """
        Change the speed of a motor on the controller.

        :param motor: The motor to change.
        :type motor: ``int``

        :param speed: Speed from -100 to +100, 0 is stop
        :type speed: ``int``

        """
        raise NotImplementedError

    def stop_all(self):
        """Stops all motors connected to the motor controller"""
        raise NotImplementedError



class MotorControllerBoard(object):
    def __init__(self, device_name, dc_controller=None, stepper_controller=None, servo_controller=None):
        if dc_controller:
            self._dc = dc_controller
        else:
            self._dc = DCMotorControllerBase(device_name, 0)

        if stepper_controller:
            self._stepper = stepper_controller
        else:
            self._stepper = StepperMotorControllerBase(device_name, 0)

        if servo_controller:
            self._servo = servo_controller
        else:
            self._servo = ServoMotorControllerBase(device_name, 0)

    @property
    def dc_motors(self):
        return self._dc

    @property
    def servo_motors(self):
        return self._servo

    @property
    def stepper_motors(self):
        return self._stepper