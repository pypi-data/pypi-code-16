""" Sample controller """
from kervi.controller import Controller, UINumberControllerInput, UISwitchButtonControllerInput
from kervi.hal import GPIO
#Switch button shown on a dashboard
class LightController(Controller):
    def __init__(self):
        Controller.__init__(self, "lightController", "Light")
        self.type = "light"

        #define an input and link it to the dashboard panel
        self.light_button = UISwitchButtonControllerInput("lightctrl.on", "Light", self)
        self.light_button.link_to_dashboard("app", "light", label_icon="light")

        self.level_input = UINumberControllerInput("lightctrl.level", "Level", self)
        self.level_input.min = 0
        self.level_input.max = 100
        self.level_input.value = 0
        self.level_input.link_to_dashboard("app", "light")

        #define GPIO
        GPIO.define_as_pwm(12, 50)

    def input_changed(self, changed_input):
        if changed_input == self.light_button:
            if changed_input.value:
                GPIO.pwm_start(12)
            else:
                GPIO.pwm_stop(12)

        if changed_input.input_id == "lightctrl.level":
            #change the duty_cycle on the pwm pin
            GPIO.pwm_start(12, duty_cycle=changed_input.value)

LightController()

