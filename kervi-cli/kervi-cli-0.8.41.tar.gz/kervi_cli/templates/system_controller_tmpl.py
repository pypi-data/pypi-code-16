""" Sample controller """
from kervi.controller import Controller, UINumberControllerInput, UIButtonControllerInput


class PowerOffButton(UIButtonControllerInput):
    def __init__(self, controller):
        UIButtonControllerInput.__init__(
            self,
            controller.component_id+".powerDown",
            "Power off",
            controller
        )
        self.link_to_dashboard("system", "power", icon="power-off")

    def click(self):
        print ("stop kervi")
        self.user_log_message("stop kervi")
        self.controller.spine.send_command("stopKervi")


class RebootButton(UIButtonControllerInput):
    def __init__(self, controller):
        UIButtonControllerInput.__init__(
            self,
            controller.component_id + ".reebotDown",
            "Reboot",
            controller
        )
        self.link_to_dashboard("system", "power", icon="repeat")

    def click(self):
        print ("restart kervi")
        self.user_log_message("restart kervi")
        self.controller.spine.send_command("restartKervi")



class SystemController(Controller):
    def __init__(self):
        Controller.__init__(self, "systemController", "System")
        self.type = "controller_category"

        self.add_input(PowerOffButton(self), RebootButton(self))
        self.parameters = {}


MY_CONTROLLER = SystemController()
