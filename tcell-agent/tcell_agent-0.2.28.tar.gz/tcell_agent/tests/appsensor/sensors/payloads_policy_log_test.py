import json
import unittest

from mock import Mock, ANY, patch

from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.appsensor.params import GET_PARAM
from tcell_agent.appsensor.sensors.payloads_policy import PayloadsPolicy


class PayloadsPolicyTest(unittest.TestCase):
    def false_log_payloads_log_test(self):
        policy_json = {"payloads": {"log_payloads": False}}
        policy = PayloadsPolicy.from_json(policy_json)
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch("tcell_agent.appsensor.sensors.payloads_policy.get_payloads_logger") as patched_get_payloadds_logger:
            policy.log("xss", appsensor_meta, GET_PARAM, "password", "123password123", {"l": "query"}, "pattern")

            self.assertFalse(patched_get_payloadds_logger.called)

    def true_log_payloads_no_blacklist_no_whitelist_log_test(self):
        policy_json = {"payloads": {"log_payloads": True}}
        policy = PayloadsPolicy.from_json(policy_json)
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch("tcell_agent.appsensor.sensors.payloads_policy.get_payloads_logger") as patched_get_payloadds_logger:
            policy.log("xss", appsensor_meta, GET_PARAM, "password", "123password123", {"l": "query"}, "pattern")

            self.assertFalse(patched_get_payloadds_logger.called)

    def true_log_payloads_no_blacklist_with_whitelist_missing_param_log_test(self):
        policy_json = {"payloads": {"log_payloads": True, "log_whitelist": {"username": ["*"]}}}
        policy = PayloadsPolicy.from_json(policy_json)
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch("tcell_agent.appsensor.sensors.payloads_policy.get_payloads_logger") as patched_get_payloadds_logger:
            policy.log("xss", appsensor_meta, GET_PARAM, "password", "123password123", {"l": "query"}, "pattern")

            self.assertFalse(patched_get_payloadds_logger.called)

    def true_log_payloads_no_blacklist_param_in_whitelist_but_incorrect_location_log_test(
            self):
        policy_json = {
            "payloads": {
                "log_payloads": True,
                "log_whitelist": {
                    "username": ["*"],
                    "password": ["cookie"]
                }
            }
        }
        policy = PayloadsPolicy.from_json(policy_json)
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch("tcell_agent.appsensor.sensors.payloads_policy.get_payloads_logger") as patched_get_payloadds_logger:
            policy.log("xss", appsensor_meta, GET_PARAM, "password", "123password123", {"l": "query"}, "pattern")

            self.assertFalse(patched_get_payloadds_logger.called)

    def true_log_payloads_no_blacklist_param_in_whitelist_log_test(self):
        policy_json = {
            "payloads": {
                "log_payloads": True,
                "log_whitelist": {
                    "username": ["*"],
                    "password": ["form"]
                }
            }
        }
        policy = PayloadsPolicy.from_json(policy_json)
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch("tcell_agent.appsensor.sensors.payloads_policy.get_payloads_logger") as patched_get_payloadds_logger:
            policy.log("xss", appsensor_meta, GET_PARAM, "password", "123password123", {"l": "query"}, "pattern")

            self.assertFalse(patched_get_payloadds_logger.called)

    def true_log_payloads_no_whitelist_with_blacklist_missing_param_log_test(self):
        policy_json = {"payloads": {"log_payloads": True, "log_blacklist": {"username": ["*"]}}}
        policy = PayloadsPolicy.from_json(policy_json)
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        mock_logger = Mock()
        with patch("tcell_agent.appsensor.sensors.payloads_policy.get_payloads_logger",
                   return_value=mock_logger) as patched_get_payloadds_logger:
            policy.log("xss", appsensor_meta, GET_PARAM, "password", "123password123", {"l": "query"}, "pattern")

            patched_get_payloadds_logger.assert_called_once_with()

            mock_logger.info.assert_called_once_with(ANY)
            call_args, call_kwargs = mock_logger.info.call_args
            self.assertEqual(sorted(json.loads(call_args[0])), sorted({
                "event_type": "as",
                "remote_addr": "remote_addr",
                "pattern": "pattern",
                "m": "request_method",
                "param": "password",
                "meta": {"l": "query"},
                "sid": "session_id",
                "rid": "23947",
                "payload": "123password123",
                "dp": "xss",
                "uid": "user_id"
            }))

    def true_log_payloads_no_whitelist_param_in_blacklist_but_incorrect_location_log_test(self):
        policy_json = {
            "payloads": {
                "log_payloads": True,
                "log_blacklist": {
                    "username": ["*"],
                    "password": ["cookie"]
                }
            }
        }
        policy = PayloadsPolicy.from_json(policy_json)
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        mock_logger = Mock()
        with patch("tcell_agent.appsensor.sensors.payloads_policy.get_payloads_logger",
                   return_value=mock_logger) as patched_get_payloadds_logger:
            policy.log("xss", appsensor_meta, GET_PARAM, "password", "123password123", {"l": "query"}, "pattern")

            patched_get_payloadds_logger.assert_called_once_with()

            mock_logger.info.assert_called_once_with(ANY)
            call_args, call_kwargs = mock_logger.info.call_args
            self.assertEqual(sorted(json.loads(call_args[0])), sorted({
                "event_type": "as",
                "remote_addr": "remote_addr",
                "pattern": "pattern",
                "m": "request_method",
                "param": "password",
                "meta": {"l": "query"},
                "sid": "session_id",
                "rid": "23947",
                "payload": "123password123",
                "dp": "xss",
                "uid": "user_id"
            }))

    def true_log_payloads_no_whitelist_param_in_blacklist_log_test(self):
        policy_json = {
            "payloads": {
                "log_payloads": True,
                "log_blacklist": {
                    "username": ["*"],
                    "password": ["form"]
                }
            }
        }
        policy = PayloadsPolicy.from_json(policy_json)
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch("tcell_agent.appsensor.sensors.payloads_policy.get_payloads_logger") as patched_get_payloadds_logger:
            policy.log("xss", appsensor_meta, GET_PARAM, "password", "123password123", {"l": "query"}, "pattern")

            self.assertFalse(patched_get_payloadds_logger.called)
