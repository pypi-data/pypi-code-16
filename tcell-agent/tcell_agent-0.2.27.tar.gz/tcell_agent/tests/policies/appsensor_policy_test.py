import json
import unittest

from collections import namedtuple
from mock import patch

from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.appsensor.sensors import InjectionSensor
from tcell_agent.appsensor.sensors import MiscSensor
from tcell_agent.appsensor.sensors import RequestSizeSensor
from tcell_agent.appsensor.sensors import ResponseCodesSensor
from tcell_agent.appsensor.sensors import ResponseSizeSensor
from tcell_agent.appsensor.sensors import UserAgentSensor
from tcell_agent.policies.appsensor_policy import AppSensorPolicy

# set is builtin in python 3 but a module in earlier version
try:
    set
except NameError:
    from sets import Set as set

FakeRequest = namedtuple('FakeRequest', ['body', 'META', 'GET', 'POST', 'FILES', 'COOKIES'], verbose=True)
FakeResponse = namedtuple('FakeResponse', ['content', 'status_code'], verbose=True)

policy_one_disabled = """
{
    "policy_id":"abc-abc-abc",
    "data": {
    }
}
"""

policy_one = """
{
    "policy_id":"abc-abc-abc",
    "data": {
        "options": {
            "xss":true
        }
    }
}
"""

policy_v2_req_size = """
{
    "policy_id":"abc-abc-abc",
    "version":2,
    "data": {
        "options": {
            "payloads": {}
        },
        "sensors": {
            "req_size": {
                "limit":1024,
                "exclude_routes":["2300"]
            }
        }
    }
}
"""

policy_v2_all_options = """
{
    "policy_id":"abc-abc-abc",
    "version":2,
    "data": {
        "options": {
            "payloads": {
                "send_payloads": true,
                "send_blacklist": {
                    "JSESSIONID": ["cookie"],
                    "ssn": ["*"],
                    "password": ["*"]
                },
                "send_whitelist": {},
                "log_payloads": true,
                "log_blacklist": {},
                "log_whitelist": {
                    "username": ["*"]
                }
            }
        },
        "sensors": {
            "req_size": {
                "limit":1024,
                "exclude_routes":["2300"]
            },
            "resp_size": {
                "limit":2048,
                "exclude_routes":["2323"]
            },
            "resp_codes": {
                "series_400_enabled":true,
                "series_500_enabled":true
            },
            "xss": {
                "libinjection":true,
                "patterns":["1","2","8"],
                "exclusions":{
                    "bob":["*"]
                }
            },
            "sqli":{
                "libinjection":true,
                "exclude_headers":true,
                "patterns":["1"]
            },
            "fpt":{
                "patterns":["1","2"],
                "exclude_forms":true,
                "exclude_cookies":true,
                "exclusions":{
                    "somethingcommon":["form"]
                }
            },
            "cmdi":{
                 "patterns":["1","2"]
            },
            "nullbyte":{
                 "patterns":["1","2"]
            },
            "retr":{
                "patterns":["1","2"]
            },
            "ua": {
                "empty_enabled": true
            },
            "errors":{
                "csrf_exception_enabled": true,
                "sql_exception_enabled": true
            },
            "database":{
                "large_result": {
                    "limit": 10
                }
            }
        }
    }
}
"""


class AppSensorPolicyTest(unittest.TestCase):
    def classname_test(self):
        self.assertEqual(AppSensorPolicy.api_identifier, "appsensor")

    def read_appensor_v1_policy_disabled_test(self):
        policy_json = json.loads(policy_one_disabled)
        policy = AppSensorPolicy()
        policy.loadFromJson(policy_json)

        self.assertIsNone(policy.options.get("req_size"))
        self.assertIsNone(policy.options.get("resp_size"))
        self.assertIsNone(policy.options.get("resp_codes"))
        self.assertIsNone(policy.options.get("ua"))
        self.assertIsNone(policy.options.get("errors"))
        self.assertIsNone(policy.options.get("database"))

    def read_appensor_v1_policy_test(self):
        policy_json = json.loads(policy_one)
        policy = AppSensorPolicy()
        policy.loadFromJson(policy_json)

        self.assertIsNotNone(policy.options["req_size"])
        self.assertIsNotNone(policy.options["resp_size"])
        self.assertIsNotNone(policy.options["resp_codes"])
        self.assertIsNotNone(policy.options["ua"])
        self.assertIsNotNone(policy.options["errors"])
        self.assertIsNotNone(policy.options["database"])

        self.assertFalse(policy.options["req_size"].enabled)
        self.assertFalse(policy.options["resp_size"].enabled)
        self.assertFalse(policy.options["resp_codes"].enabled)
        self.assertFalse(policy.options["ua"].enabled)
        self.assertFalse(policy.options["errors"].csrf_exception_enabled)
        self.assertFalse(policy.options["errors"].sql_exception_enabled)
        self.assertFalse(policy.options["database"].enabled)

        self.assertTrue(policy.options["resp_codes"].series_400_enabled)
        self.assertTrue(policy.options["resp_codes"].series_500_enabled)

        self.assertTrue(policy.injections_reporter.payloads_policy.send_payloads)
        self.assertTrue(policy.injections_reporter.payloads_policy.log_payloads)
        self.assertEqual(policy.injections_reporter.payloads_policy.send_blacklist,
                         policy.injections_reporter.payloads_policy.DEFAULT_BLACKLIST)
        self.assertEqual(policy.injections_reporter.payloads_policy.send_whitelist, {})
        self.assertFalse(policy.injections_reporter.payloads_policy.use_send_whitelist)
        self.assertEqual(policy.injections_reporter.payloads_policy.log_blacklist,
                         policy.injections_reporter.payloads_policy.DEFAULT_BLACKLIST)
        self.assertEqual(policy.injections_reporter.payloads_policy.log_whitelist, {})
        self.assertFalse(policy.injections_reporter.payloads_policy.use_log_whitelist)

    def read_appensor_v2_req_size_policy_test(self):
        policy_json = json.loads(policy_v2_req_size)
        policy = AppSensorPolicy()
        policy.loadFromJson(policy_json)

        self.assertIsNotNone(policy.options["req_size"])
        self.assertIsNotNone(policy.options["resp_size"])
        self.assertIsNotNone(policy.options["resp_codes"])
        self.assertIsNotNone(policy.options["ua"])
        self.assertIsNotNone(policy.options["errors"])
        self.assertIsNotNone(policy.options["database"])

        self.assertTrue(policy.options["req_size"].enabled)
        self.assertFalse(policy.options["resp_size"].enabled)
        self.assertFalse(policy.options["resp_codes"].enabled)
        self.assertFalse(policy.options["ua"].enabled)
        self.assertFalse(policy.options["errors"].csrf_exception_enabled)
        self.assertFalse(policy.options["errors"].sql_exception_enabled)
        self.assertFalse(policy.options["database"].enabled)

        self.assertFalse(policy.injections_reporter.payloads_policy.send_payloads)
        self.assertFalse(policy.injections_reporter.payloads_policy.log_payloads)
        self.assertEqual(policy.injections_reporter.payloads_policy.send_blacklist,
                         policy.injections_reporter.payloads_policy.DEFAULT_BLACKLIST)
        self.assertEqual(policy.injections_reporter.payloads_policy.send_whitelist, {})
        self.assertFalse(policy.injections_reporter.payloads_policy.use_send_whitelist)
        self.assertEqual(policy.injections_reporter.payloads_policy.log_blacklist,
                         policy.injections_reporter.payloads_policy.DEFAULT_BLACKLIST)
        self.assertEqual(policy.injections_reporter.payloads_policy.log_whitelist, {})
        self.assertFalse(policy.injections_reporter.payloads_policy.use_log_whitelist)

    def read_appensor_v2_all_options_policy_test(self):
        policy_json = json.loads(policy_v2_all_options)
        policy = AppSensorPolicy()

        policy.loadFromJson(policy_json)

        self.assertIsNotNone(policy.injections_reporter)
        self.assertIsNotNone(policy.options["req_size"])
        self.assertIsNotNone(policy.options["resp_size"])
        self.assertIsNotNone(policy.options["resp_codes"])
        self.assertIsNotNone(policy.options["ua"])
        self.assertIsNotNone(policy.options["errors"])
        self.assertIsNotNone(policy.options["database"])

        self.assertTrue(policy.options["req_size"].enabled)
        self.assertTrue(policy.options["resp_size"].enabled)
        self.assertTrue(policy.options["resp_codes"].enabled)
        self.assertTrue(policy.options["ua"].enabled)
        self.assertTrue(policy.options["ua"].empty_enabled)
        self.assertTrue(policy.options["errors"].csrf_exception_enabled)
        self.assertTrue(policy.options["errors"].sql_exception_enabled)
        self.assertTrue(policy.options["database"].enabled)
        self.assertEqual(policy.options["database"].max_rows, 10)

        self.assertTrue(policy.injections_reporter.payloads_policy.send_payloads)
        self.assertTrue(policy.injections_reporter.payloads_policy.log_payloads)
        self.assertEqual(policy.injections_reporter.payloads_policy.send_blacklist, {
            "jsessionid": set(["cookie"]),
            "ssn": set(["*"]),
            "password": set(["*"])
        })
        self.assertEqual(policy.injections_reporter.payloads_policy.send_whitelist, {})
        self.assertTrue(policy.injections_reporter.payloads_policy.use_send_whitelist)
        self.assertEqual(policy.injections_reporter.payloads_policy.log_blacklist, {})
        self.assertEqual(policy.injections_reporter.payloads_policy.log_whitelist, {
            "username": set(["*"])
        })
        self.assertTrue(policy.injections_reporter.payloads_policy.use_log_whitelist)

    def test_run_for_response(self):
        policy_json = json.loads(policy_v2_all_options)
        policy = AppSensorPolicy()
        policy.loadFromJson(policy_json)

        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        request = FakeRequest('', {'CONTENT_LENGTH': 1024, 'HTTP_USER_AGENT': None}, {}, {}, {}, {})
        response = FakeResponse(
            'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
            200)
        appsensor_meta.set_request(request)
        appsensor_meta.set_response(type(response), response)

        with patch.object(ResponseSizeSensor, 'check') as patched_size_check:
            with patch.object(ResponseCodesSensor, 'check') as patched_codes_check:
                policy.process_appsensor_meta(appsensor_meta)
                patched_size_check.assert_called_once_with(appsensor_meta)
                patched_codes_check.assert_called_once_with(appsensor_meta, 200)

    def test_run_for_request_with_no_params(self):
        policy_json = json.loads(policy_v2_all_options)
        policy = AppSensorPolicy()
        policy.loadFromJson(policy_json)

        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        request = FakeRequest('', {'CONTENT_LENGTH': 1024, 'HTTP_USER_AGENT': None}, {}, {}, {}, {})
        response = FakeResponse(
            'AA',
            200)
        appsensor_meta.set_request(request)
        appsensor_meta.set_response(type(response), response)

        with patch.object(RequestSizeSensor, 'check') as patched_check:
            with patch.object(InjectionSensor, 'get_injection_attempt') as patched_get_injection_attempt:
                with patch.object(UserAgentSensor, 'check') as patched_ua_check:
                    policy.process_appsensor_meta(appsensor_meta)
                    patched_check.assert_called_once_with(appsensor_meta)
                    patched_ua_check.assert_called_once_with(appsensor_meta)
                    self.assertFalse(patched_get_injection_attempt.called)

    def test_csrf_rejected(self):
        policy_json = json.loads(policy_v2_all_options)
        policy = AppSensorPolicy()
        policy.loadFromJson(policy_json)

        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch.object(MiscSensor, 'csrf_rejected') as patched_csrf_rejected:
            policy.csrf_rejected(appsensor_meta, "Missing CSRF")
            patched_csrf_rejected.assert_called_once_with(appsensor_meta, "Missing CSRF")
