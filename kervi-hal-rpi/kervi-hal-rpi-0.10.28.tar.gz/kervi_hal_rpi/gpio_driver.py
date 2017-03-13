import RPi.GPIO as GPIO
from kervi.hal.gpio import IGPIODeviceDriver

GPIO.setmode(GPIO.BOARD)

class GPIODriver(IGPIODeviceDriver):
    def __init__(self):
        print("init rpi gpio driver")
        self._pwm_pins = {}

    def define_as_input(self, pin):
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def define_as_output(self, pin):
        GPIO.setup(pin, GPIO.OUT)

    def define_as_pwm(self, pin, frequency):
        GPIO.setup(pin, GPIO.OUT)
        pwm_pin = GPIO.PWM(pin, frequency)
        self._pwm_pins[pin] = [pwm_pin,0]

    def set(self, pin, state):
        GPIO.output(pin, state)

    def get(self, pin):
        return GPIO.input(pin)

    def pwm_start(self, pin, duty_cycle=None, frequency=None):
        if duty_cycle!=None:
            self._pwm_pins[pin][1] = duty_cycle

        self._pwm_pins[pin][0].start(self._pwm_pins[pin][1])   

    def pwm_stop(self, pin):
        self._pwm_pins[pin][0].stop()

    def listen(self, pin, callback, bounce_time=0):
        if bounce_time > 0:
            GPIO.add_event_detect(pin, GPIO.BOTH, callback=callback, bouncetime=bounce_time)
        else:
            GPIO.add_event_detect(pin, GPIO.BOTH, callback=callback)

    def listen_rising(self, pin, callback, bounce_time=0):
        GPIO.add_event_detect(pin, GPIO.RISING, callback=callback, bouncetime=bounce_time)

    def listen_falling(self, pin, callback, bounce_time=0):
        GPIO.add_event_detect(pin, GPIO.FALLING, callback=callback, bouncetime=bounce_time)
