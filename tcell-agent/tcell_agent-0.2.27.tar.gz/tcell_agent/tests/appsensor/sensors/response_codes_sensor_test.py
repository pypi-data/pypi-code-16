import unittest

from mock import patch
from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.appsensor.sensors import ResponseCodesSensor


class ResponseCodesSensorTest(unittest.TestCase):
    def create_default_sensor_test(self):
        sensor = ResponseCodesSensor()
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.series_400_enabled, False)
        self.assertEqual(sensor.series_500_enabled, False)

    def create_enabled_sensor_test(self):
        sensor = ResponseCodesSensor({"enabled": True})
        self.assertEqual(sensor.enabled, True)
        self.assertEqual(sensor.series_400_enabled, False)
        self.assertEqual(sensor.series_500_enabled, False)

    def create_sensor_with_series_400_enabled_test(self):
        sensor = ResponseCodesSensor({"series_400_enabled": True})
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.series_400_enabled, True)
        self.assertEqual(sensor.series_500_enabled, False)

    def create_sensor_with_series_500_enabled_test(self):
        sensor = ResponseCodesSensor({"series_500_enabled": True})
        self.assertEqual(sensor.enabled, False)
        self.assertEqual(sensor.series_400_enabled, False)
        self.assertEqual(sensor.series_500_enabled, True)

    def with_disabled_sensor_check_test(self):
        sensor = ResponseCodesSensor({"enabled": False})
        with patch('tcell_agent.appsensor.sensors.response_codes_sensor.send_event') as patched_send_event:
            sensor.check({}, 200)
            self.assertFalse(patched_send_event.called)

    def with_enabled_sensor_and_200_response_code_check_test(self):
        sensor = ResponseCodesSensor({"enabled": True, "series_400_enabled": True, "series_500_enabled": True})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch('tcell_agent.appsensor.sensors.response_codes_sensor.send_event') as patched_send_event:
            sensor.check(appsensor_meta, 200)
            self.assertFalse(patched_send_event.called)

    def with_enabled_sensor_and_300_response_code_check_test(self):
        sensor = ResponseCodesSensor({"enabled": True, "series_400_enabled": True, "series_500_enabled": True})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch('tcell_agent.appsensor.sensors.response_codes_sensor.send_event') as patched_send_event:
            sensor.check(appsensor_meta, 300)
            self.assertFalse(patched_send_event.called)

    def with_disabled_400_series_and_400_response_code_check_test(self):
        sensor = ResponseCodesSensor({"enabled": True, "series_400_enabled": False, "series_500_enabled": True})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch('tcell_agent.appsensor.sensors.response_codes_sensor.send_event') as patched_send_event:
            sensor.check(appsensor_meta, 400)
            self.assertFalse(patched_send_event.called)

    def with_enabled_sensor_and_400_response_code_check_test(self):
        sensor = ResponseCodesSensor({"enabled": True, "series_400_enabled": True, "series_500_enabled": True})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch('tcell_agent.appsensor.sensors.response_codes_sensor.send_event') as patched_send_event:
            sensor.check(appsensor_meta, 400)
            patched_send_event.assert_called_once_with(appsensor_meta, ResponseCodesSensor.RESPONSE_CODE_DP_DICT[4],
                                                       None, {"code": 400})

    def with_enabled_sensor_and_400_response_code_and_matching_excluded_route_id_check_test(self):
        sensor = ResponseCodesSensor({
            "enabled": True,
            "series_400_enabled": True,
            "series_500_enabled": True,
            "exclude_routes": ["23947"]})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch('tcell_agent.appsensor.sensors.response_codes_sensor.send_event') as patched_send_event:
            sensor.check(appsensor_meta, 400)
            self.assertFalse(patched_send_event.called)

    def with_enabled_sensor_and_400_response_code_and_nonmatching_excluded_route_id_check_test(self):
        sensor = ResponseCodesSensor({
            "enabled": True,
            "series_400_enabled": True,
            "series_500_enabled": True,
            "exclude_routes": ["nonmatching"]})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch('tcell_agent.appsensor.sensors.response_codes_sensor.send_event') as patched_send_event:
            sensor.check(appsensor_meta, 400)
            patched_send_event.assert_called_once_with(appsensor_meta, ResponseCodesSensor.RESPONSE_CODE_DP_DICT[4],
                                                       None, {"code": 400})

    def with_enabled_sensor_and_401_response_code_check_test(self):
        sensor = ResponseCodesSensor({"enabled": True, "series_400_enabled": True, "series_500_enabled": True})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch('tcell_agent.appsensor.sensors.response_codes_sensor.send_event') as patched_send_event:
            sensor.check(appsensor_meta, 401)
            patched_send_event.assert_called_once_with(appsensor_meta, ResponseCodesSensor.RESPONSE_CODE_DP_DICT[401],
                                                       None, {"code": 401})

    def with_enabled_sensor_and_403_response_code_check_test(self):
        sensor = ResponseCodesSensor({"enabled": True, "series_400_enabled": True, "series_500_enabled": True})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch('tcell_agent.appsensor.sensors.response_codes_sensor.send_event') as patched_send_event:
            sensor.check(appsensor_meta, 403)
            patched_send_event.assert_called_once_with(appsensor_meta, ResponseCodesSensor.RESPONSE_CODE_DP_DICT[403],
                                                       None, {"code": 403})

    def with_enabled_sensor_and_404_response_code_check_test(self):
        sensor = ResponseCodesSensor({"enabled": True, "series_400_enabled": True, "series_500_enabled": True})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch('tcell_agent.appsensor.sensors.response_codes_sensor.send_event') as patched_send_event:
            sensor.check(appsensor_meta, 404)
            patched_send_event.assert_called_once_with(appsensor_meta, ResponseCodesSensor.RESPONSE_CODE_DP_DICT[404],
                                                       None, {"code": 404})

    def with_disabled_500_series_and_500_response_code_check_test(self):
        sensor = ResponseCodesSensor({"enabled": True, "series_400_enabled": True, "series_500_enabled": False})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch('tcell_agent.appsensor.sensors.response_codes_sensor.send_event') as patched_send_event:
            sensor.check(appsensor_meta, 500)
            self.assertFalse(patched_send_event.called)

    def with_enabled_sensor_and_500_response_code_check_test(self):
        sensor = ResponseCodesSensor({"enabled": True, "series_400_enabled": True, "series_500_enabled": True})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch('tcell_agent.appsensor.sensors.response_codes_sensor.send_event') as patched_send_event:
            sensor.check(appsensor_meta, 500)
            patched_send_event.assert_called_once_with(appsensor_meta, ResponseCodesSensor.RESPONSE_CODE_DP_DICT[500],
                                                       None, {"code": 500})

    def with_enabled_sensor_and_501_response_code_check_test(self):
        sensor = ResponseCodesSensor({"enabled": True, "series_400_enabled": True, "series_500_enabled": True})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch('tcell_agent.appsensor.sensors.response_codes_sensor.send_event') as patched_send_event:
            sensor.check(appsensor_meta, 501)
            patched_send_event.assert_called_once_with(appsensor_meta, ResponseCodesSensor.RESPONSE_CODE_DP_DICT[5],
                                                       None, {"code": 501})
