""" Sample controller """
from kervi.controller import Controller, ControllerNumberInput, ControllerButton

class ControllerInput(ControllerNumberInput):
    def __init__(self, controller):
        ControllerNumberInput.__init__(self, "numberInput", "Number input", controller)
        self.type = "counter"
        self.unit = ""
        self.value = 0
        self.max_value = 359
        self.min_value = 0

    def value_changed(self, new_value, old_value):
        print ("number input set value:", new_value)

class MyController(Controller):
    def __init__(self):
        Controller.__init__(self, "compassSteering", "Compass")
        self.type = "controller_category"

        self.add_components(ControllerInput(self))
        self.parameters = {}


MY_CONTROLLER = MyController()
