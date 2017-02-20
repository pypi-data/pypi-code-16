

class Leds:
    led1_pin = 27
    led2_pin = 22
    red_pin = 25
    green_pin = 23
    blue_pin = 24
    on = False
    off = True

    def __init__(self):
        pass

    def _set_pin(self, pin, value='on'):
        return
        # GPIO.output(pin, self.on if value == 'on' else self.off)

    def set_led1(self, *args):
        print("<[VIRTUAL MACHINE LOG] - led1 toggled>")
        return
        # self._set_pin(self.led1_pin, *args)

    def set_led2(self, *args):
        print("<[VIRTUAL MACHINE LOG] - led2 toggled>")
        return
        # self._set_pin(self.led2_pin, *args)

    def set_red(self, *args):
        print("<[VIRTUAL MACHINE LOG] - red led toggled>")
        return
        # self._set_pin(self.red_pin, *args)

    def set_green(self, *args):
        print("<[VIRTUAL MACHINE LOG] - green led toggled>")
        return
        # self._set_pin(self.green_pin, *args)

    def set_blue(self, *args):
        print("<[VIRTUAL MACHINE LOG] - blue led toggled>")
        return
        # self._set_pin(self.blue_pin, *args)

