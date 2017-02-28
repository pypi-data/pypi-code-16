import unittest

from mock import patch, Mock

from django.db.utils import ProgrammingError, InterfaceError, OperationalError

from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.appsensor.sensors import MiscSensor


class MiscSensorTest(unittest.TestCase):
    def create_default_sensor_test(self):
        sensor = MiscSensor()
        self.assertFalse(sensor.csrf_exception_enabled)
        self.assertFalse(sensor.sql_exception_enabled)

    def create_enabled_sensor_test(self):
        sensor = MiscSensor({
            "csrf_exception_enabled": True,
            "sql_exception_enabled": True
        })
        self.assertTrue(sensor.csrf_exception_enabled)
        self.assertTrue(sensor.sql_exception_enabled)

    def with_disabled_sensor_csrf_rejected_test(self):
        sensor = MiscSensor({"csrf_exception_enabled": False})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch('tcell_agent.appsensor.sensors.misc_sensor.send_event') as patched_send_event:
            sensor.csrf_rejected(appsensor_meta, "Missing CSRF")
            self.assertFalse(patched_send_event.called)

    def with_enabled_sensor_csrf_rejected_test(self):
        sensor = MiscSensor({"csrf_exception_enabled": True})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch('tcell_agent.appsensor.sensors.misc_sensor.send_event') as patched_send_event:
            sensor.csrf_rejected(appsensor_meta, "Missing CSRF")
            patched_send_event.assert_called_once_with(appsensor_meta, "excsrf", None, None)

    def with_disabled_sensor_sql_exception_test(self):
        sensor = MiscSensor({"sql_exception_enabled": False})

        with patch('tcell_agent.appsensor.sensors.misc_sensor.send_event') as patched_send_event:
            with patch('traceback.print_tb', return_value="printed stack") as patched_print_tb:
                db = Mock()
                meta = Mock()
                exc_type = Mock()
                exc_value = "some error"
                tb = Mock()

                sensor.sql_exception_detected(db, meta, exc_type, exc_value, tb)
                self.assertFalse(patched_send_event.called)
                self.assertFalse(patched_print_tb.called)

    def with_enabled_sensor_sql_exception_test(self):
        sensor = MiscSensor({"sql_exception_enabled": True})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch('tcell_agent.appsensor.sensors.misc_sensor.send_event') as patched_send_event:
            with patch('traceback.print_tb', return_value="printed stack") as patched_print_tb:
                db = Mock()
                db.ProgrammingError = ProgrammingError
                db.OperationalError = OperationalError
                exc_type = ProgrammingError
                exc_value = "some error"
                tb = Mock()

                sensor.sql_exception_detected(db, appsensor_meta, exc_type, exc_value, tb)
                patched_send_event.assert_called_once_with(appsensor_meta, "exsql", "ProgrammingError", None,
                                                           payload='printed stack')
                patched_print_tb.assert_called_once_with(tb)

    def with_enabled_sensor_sql_exception_operational_error_test(self):
        sensor = MiscSensor({"sql_exception_enabled": True})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch('tcell_agent.appsensor.sensors.misc_sensor.send_event') as patched_send_event:
            with patch('traceback.print_tb', return_value="printed stack") as patched_print_tb:
                db = Mock()
                db.ProgrammingError = ProgrammingError
                db.OperationalError = OperationalError
                exc_type = OperationalError
                exc_value = "some error"
                tb = Mock()

                sensor.sql_exception_detected(db, appsensor_meta,  exc_type, exc_value, tb)
                patched_send_event.assert_called_once_with(appsensor_meta, "exsql", "OperationalError", None, payload='printed stack')
                patched_print_tb.assert_called_once_with(tb)

    def with_enabled_sensor_sql_exception_interface_error_test(self):
        sensor = MiscSensor({"sql_exception_enabled": True})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch('tcell_agent.appsensor.sensors.misc_sensor.send_event') as patched_send_event:
            with patch('traceback.print_tb', return_value="printed stack") as patched_print_tb:
                db = Mock()
                db.ProgrammingError = ProgrammingError
                db.OperationalError = OperationalError
                exc_type = InterfaceError
                exc_value = "some error"
                tb = Mock()

                sensor.sql_exception_detected(db, appsensor_meta, exc_type, exc_value, tb)
                self.assertFalse(patched_send_event.called)
                self.assertFalse(patched_print_tb.called)

    def with_enabled_sensor_sql_exception_matching_excluded_route_test(self):
        sensor = MiscSensor({"sql_exception_enabled": True, "exclude_routes": ["23947"]})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch('tcell_agent.appsensor.sensors.misc_sensor.send_event') as patched_send_event:
            with patch('traceback.print_tb', return_value="printed stack") as patched_print_tb:
                db = Mock()
                db.ProgrammingError = ProgrammingError
                db.OperationalError = OperationalError
                exc_type = ProgrammingError
                exc_value = "some error"
                tb = Mock()

                sensor.sql_exception_detected(db, appsensor_meta, exc_type, exc_value, tb)
                self.assertFalse(patched_send_event.called)
                self.assertFalse(patched_print_tb.called)

    def with_enabled_sensor_sql_exception_nonmatching_excluded_route_test(self):
        sensor = MiscSensor({"sql_exception_enabled": True, "exclude_routes": ["nonmatching"]})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "23947"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        with patch('tcell_agent.appsensor.sensors.misc_sensor.send_event') as patched_send_event:
            with patch('traceback.print_tb', return_value="printed stack") as patched_print_tb:
                db = Mock()
                db.ProgrammingError = ProgrammingError
                db.OperationalError = OperationalError
                exc_type = ProgrammingError
                exc_value = "some error"
                tb = Mock()

                sensor.sql_exception_detected(db, appsensor_meta, exc_type, exc_value, tb)
                patched_send_event.assert_called_once_with(appsensor_meta, "exsql", "ProgrammingError", None,
                                                           payload='printed stack')
                patched_print_tb.assert_called_once_with(tb)
