from tcell_agent.appsensor.params import COOKIE_PARAM
from tcell_agent.appsensor.sensors import InjectionSensor

class FptSensor(InjectionSensor):

    def __init__(self, policy_json=None):
        super(FptSensor, self).__init__("fpt", policy_json)

    def applicable_for_param_type(self, param_type):
        return COOKIE_PARAM is not param_type
