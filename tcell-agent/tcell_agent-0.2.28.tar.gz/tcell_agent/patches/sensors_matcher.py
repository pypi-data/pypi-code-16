from tcell_agent.appsensor.injections_matcher import InjectionsMatcher


class SensorsMatcher(object):
    def __init__(self, injections_matcher):
        self.injections_matcher = injections_matcher

    def any_matches(self, meta_data):
        if not self.injections_matcher.enabled:
            return True

        for injection_attempt in self.injections_matcher.each_injection(meta_data):
            return True

        return False

    @classmethod
    def from_json(cls, sensor_matcher_json):
        injections_matcher = InjectionsMatcher.from_json(2, sensor_matcher_json)
        return SensorsMatcher(injections_matcher)
