from tcell_agent.appsensor.injections_matcher import InjectionsMatcher
from tcell_agent.appsensor.params import GET_PARAM, POST_PARAM, JSON_PARAM, COOKIE_PARAM, URI_PARAM
from tcell_agent.appsensor.sensor import send_event


class InjectionsReporter(object):
    PARAM_TYPE_TO_L = {
        GET_PARAM: 'query',
        POST_PARAM: 'body',
        JSON_PARAM: 'body',
        URI_PARAM: 'uri',
        COOKIE_PARAM: 'cookie'
    }

    def __init__(self, injections_matcher, payloads_policy):
        self.injections_matcher = injections_matcher
        self.payloads_policy = payloads_policy

    def check(self, meta_data):
        for injection_attempt in self.injections_matcher.each_injection(meta_data):
            vuln_param = injection_attempt.param_name
            type_of_param = injection_attempt.type_of_param

            meta = {"l": self.PARAM_TYPE_TO_L[type_of_param]}
            pattern = injection_attempt.pattern

            payload = self.payloads_policy.apply(
                injection_attempt.detection_point,
                meta_data,
                type_of_param,
                vuln_param,
                injection_attempt.param_value,
                meta,
                pattern
            )

            send_event(
                meta_data,
                injection_attempt.detection_point,
                vuln_param,
                meta,
                payload,
                pattern
            )

    @classmethod
    def from_json(cls, version, data_json, payloads_policy):
        injections_matcher = InjectionsMatcher.from_json(version, data_json)

        return InjectionsReporter(injections_matcher, payloads_policy)
