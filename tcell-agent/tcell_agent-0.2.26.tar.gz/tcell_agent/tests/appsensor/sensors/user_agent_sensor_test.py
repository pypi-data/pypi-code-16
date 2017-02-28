import unittest

from collections import namedtuple

from mock import Mock, MagicMock, patch
from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.appsensor.sensors import UserAgentSensor

FakeRequest = namedtuple('FakeRequest', ['body', 'META', 'GET', 'POST', 'FILES', 'COOKIES'], verbose=True)


class UserAgentSensorTest(unittest.TestCase):
    def create_default_sensor_test(self):
        sensor = UserAgentSensor()
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.empty_enabled, False)

    def create_enabled_sensor_test(self):
        sensor = UserAgentSensor({"enabled": True})
        self.assertEqual(sensor.enabled, True)

    def create_empty_enabled_sensor_test(self):
        sensor = UserAgentSensor({"empty_enabled": True})
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.empty_enabled, True)

    def with_disabled_sensor_check_test(self):
        sensor = UserAgentSensor({"enabled": False})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch('tcell_agent.appsensor.sensors.user_agent_sensor.send_event') as patched_send_event:
            sensor.check(appsensor_meta)
            self.assertFalse(patched_send_event.called)

    def with_enabled_sensor_and_user_agent_is_present_check_test(self):
        sensor = UserAgentSensor({"enabled": True, "empty_enabled": True})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"
        appsensor_meta.user_agent_str = 'user_agent'

        request = FakeRequest('', {'CONTENT_LENGTH': 1024}, {}, {}, {}, {})
        appsensor_meta.set_request(request)
        with patch('tcell_agent.appsensor.sensors.user_agent_sensor.send_event') as patched_send_event:
            sensor.check(appsensor_meta)
            self.assertFalse(patched_send_event.called)

    def with_enabled_sensor_and_user_agent_is_none_check_test(self):
        sensor = UserAgentSensor({"enabled": True, "empty_enabled": True})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        request = FakeRequest('', {'CONTENT_LENGTH': 1024}, {}, {}, {}, {})
        appsensor_meta.set_request(request)
        with patch('tcell_agent.appsensor.sensors.user_agent_sensor.send_event') as patched_send_event:
            sensor.check(appsensor_meta)
            patched_send_event.assert_called_once_with(appsensor_meta, UserAgentSensor.DP_CODE, None, None)

    def with_enabled_sensor_and_user_agent_is_empty_string_check_test(self):
        sensor = UserAgentSensor({"enabled": True, "empty_enabled": True})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"
        appsensor_meta.user_agent_str = ''

        request = FakeRequest('', {'CONTENT_LENGTH': 1024}, {}, {}, {}, {})
        appsensor_meta.set_request(request)
        with patch('tcell_agent.appsensor.sensors.user_agent_sensor.send_event') as patched_send_event:
            sensor.check(appsensor_meta)
            patched_send_event.assert_called_once_with(appsensor_meta, UserAgentSensor.DP_CODE, None, None)

    def with_enabled_sensor_and_user_agent_is_blank_string_check_test(self):
        sensor = UserAgentSensor({"enabled": True, "empty_enabled": True})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"
        appsensor_meta.user_agent_str = "   \t \n"

        request = FakeRequest('', {'CONTENT_LENGTH': 1024}, {}, {}, {}, {})
        appsensor_meta.set_request(request)
        with patch('tcell_agent.appsensor.sensors.user_agent_sensor.send_event') as patched_send_event:
            sensor.check(appsensor_meta)
            patched_send_event.assert_called_once_with(appsensor_meta, UserAgentSensor.DP_CODE, None, None)

    def with_enabled_sensor_and_user_agent_is_empty_string_and_matching_exluded_route_check_test(self):
        sensor = UserAgentSensor({"enabled": True, "empty_enabled": True, "exclude_routes": ["23947"]})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"
        appsensor_meta.user_agent_str = ""

        request = FakeRequest('', {'CONTENT_LENGTH': 1024}, {}, {}, {}, {})
        appsensor_meta.set_request(request)
        with patch('tcell_agent.appsensor.sensors.user_agent_sensor.send_event') as patched_send_event:
            sensor.check(appsensor_meta)
            self.assertFalse(patched_send_event.called)

    def with_enabled_sensor_and_user_agent_is_empty_string_and_nonmatching_exluded_route_check_test(self):
        sensor = UserAgentSensor({"enabled": True, "empty_enabled": True, "exclude_routes": ["nonmatching"]})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"
        appsensor_meta.user_agent_str = ""

        request = FakeRequest('', {'CONTENT_LENGTH': 1024}, {}, {}, {}, {})
        appsensor_meta.set_request(request)
        with patch('tcell_agent.appsensor.sensors.user_agent_sensor.send_event') as patched_send_event:
            sensor.check(appsensor_meta)
            patched_send_event.assert_called_once_with(appsensor_meta, UserAgentSensor.DP_CODE, None, None)
