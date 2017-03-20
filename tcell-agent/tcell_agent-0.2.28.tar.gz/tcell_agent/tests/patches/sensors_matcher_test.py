import unittest

from collections import namedtuple

from django.utils.datastructures import MultiValueDict

from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.patches.sensors_matcher import SensorsMatcher

# set is builtin in python 3 but a module in earlier version
try:
    set
except NameError:
    from sets import Set as set

FakeFile = namedtuple('FakeFile', ['name'], verbose=True)
FakeRequest = namedtuple('FakeRequest', ['body', 'META', 'GET', 'POST', 'FILES', 'COOKIES'], verbose=True)
FakeResponse = namedtuple('FakeResponse', ['content', 'status_code'], verbose=True)


class SensorsMatcherTest(unittest.TestCase):
    def xss_sensor_config_from_json_test(self):
        sensor_matcher_json = {
            "xss": {
                "libinjection": True,
                "exclude_cookies": False,
                "exclude_forms": False,
                "exclusions": {"generic": ["form", "cookies"]},
                "patterns": ["1", "2"]
            }
        }

        sensor_matcher = SensorsMatcher.from_json(sensor_matcher_json)

        sensors = sensor_matcher.injections_matcher.sensors

        self.assertEqual(len(sensors), 1)
        self.assertTrue(sensors[0].libinjection)
        self.assertFalse(sensors[0].exclude_cookies)
        self.assertFalse(sensors[0].exclude_forms)
        self.assertEqual(sensors[0].exclusions, {"generic": set(["form", "cookies"])})

    def no_injections_any_matches_test(self):
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"
        files_dict = MultiValueDict()

        request = FakeRequest('', {'CONTENT_LENGTH': 1024, 'HTTP_USER_AGENT': 'user_agent'}, {}, {}, files_dict, {})
        response = FakeResponse('AA', 200)
        appsensor_meta.set_request(request)
        appsensor_meta.set_response(type(response), response)

        sensor_matcher_json = {
            "xss": {
                "libinjection": True,
                "exclude_cookies": False,
                "exclude_forms": False,
                "exclusions": {"generic": ["form", "cookies"]},
                "patterns": ["1", "2"]
            }
        }

        sensor_matcher = SensorsMatcher.from_json(sensor_matcher_json)

        self.assertFalse(sensor_matcher.any_matches(appsensor_meta))

    def one_injection_any_matches_test(self):
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"
        files_dict = MultiValueDict({'avatar': [FakeFile('<script>alert()</script>')]})

        request = FakeRequest('', {'CONTENT_LENGTH': 1024, 'HTTP_USER_AGENT': 'user_agent'}, {}, {}, files_dict, {})
        response = FakeResponse('AA', 200)
        appsensor_meta.set_request(request)
        appsensor_meta.set_response(type(response), response)

        sensor_matcher_json = {
            "xss": {
                "libinjection": True,
                "exclude_cookies": False,
                "exclude_forms": False,
                "exclusions": {"generic": ["form", "cookies"]},
                "patterns": ["1", "2"]
            }
        }

        sensor_matcher = SensorsMatcher.from_json(sensor_matcher_json)

        self.assertTrue(sensor_matcher.any_matches(appsensor_meta))

    def two_injections_any_matches_test(self):
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"
        files_dict = MultiValueDict({
            'avatar': [FakeFile('<script>alert()</script>'), FakeFile('<script></script>')]
        })

        request = FakeRequest('', {'CONTENT_LENGTH': 1024, 'HTTP_USER_AGENT': 'user_agent'}, {}, {}, files_dict, {})
        response = FakeResponse('AA', 200)
        appsensor_meta.set_request(request)
        appsensor_meta.set_response(type(response), response)

        sensor_matcher_json = {
            "xss": {
                "libinjection": True,
                "exclude_cookies": False,
                "exclude_forms": False,
                "exclusions": {"generic": ["form", "cookies"]},
                "patterns": ["1", "2"]
            }
        }

        sensor_matcher = SensorsMatcher.from_json(sensor_matcher_json)

        self.assertTrue(sensor_matcher.any_matches(appsensor_meta))
