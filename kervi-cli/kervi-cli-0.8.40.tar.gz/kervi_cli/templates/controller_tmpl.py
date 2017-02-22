""" Sample controller """
from kervi.controller import Controller, UINumberControllerInput, UISwitchButtonControllerInput

#Switch button shown on a dashboard
class LightButton(UISwitchButtonControllerInput):
    def __init__(self, controller):
        UISwitchButtonControllerInput.__init__(
            self,
            controller.component_id+".light",
            "Light 1",
            controller
        )
        self.set_ui_parameter("size",0)

    def on(self):
        #event fired when user click the button in UI
        #set GPIO pin high
        print("set GPIO pin 23 heigh")

    def off(self):
        #event fired when user click the button in UI
        #set GPIO pin low
        print("set GPIO pin 23 low")

class LightLevel(UINumberControllerInput):
    def __init__(self, controller):
        UINumberControllerInput.__init__(
            self,
            controller.component_id+".lightLevel",
            "level",
            controller
        )

    def value_changed(self, value, old_value):
        #User has changed level
        #Set pwm controller
        print("Update light pwm:", value)

class LightController(Controller):
    def __init__(self):
        Controller.__init__(self, "lightController", "Light")
        self.type = "light"

        self.add_input(LightButton(self), LightLevel(self))
        self.link_to_dashboard("system", "light")

LIGHT_CONTROLLER = LightController()

