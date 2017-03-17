import unittest

from collections import namedtuple
from mock import call, patch

from django.utils.datastructures import MultiValueDict
from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.policies.appsensor_policy import AppSensorPolicy

FakeFile = namedtuple('FakeFile', ['name'], verbose=True)
FakeRequest = namedtuple('FakeRequest', ['body', 'META', 'GET', 'POST', 'FILES', 'COOKIES'], verbose=True)
FakeResponse = namedtuple('FakeResponse', ['content', 'status_code'], verbose=True)


class AppSensorPolicyCheckParamsTest(unittest.TestCase):
    def uploading_zero_file_test(self):
        policy = AppSensorPolicy()
        files_dict = MultiValueDict()
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        request = FakeRequest('', {'CONTENT_LENGTH': 1024, 'HTTP_USER_AGENT': 'user_agent'}, {}, {}, files_dict, {})
        response = FakeResponse('AA', 200)
        appsensor_meta.set_request(request)
        appsensor_meta.set_response(type(response), response)

        with patch('tcell_agent.policies.appsensor_policy.safe_wrap_function') as patched_safe_wrap_function:
            policy.process_appsensor_meta(appsensor_meta)
            self.assertFalse(patched_safe_wrap_function.called)

    def uploading_one_file_test(self):
        policy_one = {
            "policy_id": "abc-abc-abc",
            "data": {
                "options": {
                    "xss": True
                }
            }
        }

        policy = AppSensorPolicy(policy_one)
        files_dict = MultiValueDict({'avatar': [FakeFile('<script>alert()</script>')]})
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        request = FakeRequest('', {'CONTENT_LENGTH': 1024, 'HTTP_USER_AGENT': 'user_agent'}, {}, {}, files_dict, {})
        response = FakeResponse('AA', 200)
        appsensor_meta.set_request(request)
        appsensor_meta.set_response(type(response), response)

        with patch('tcell_agent.appsensor.injections_reporter.send_event') as patched_send_event:
            policy.process_appsensor_meta(appsensor_meta)
            patched_send_event.assert_called_once_with(appsensor_meta, 'xss', 'avatar', {'l': 'body'}, None, '1')

    def uploading_two_files_for_same_param_test(self):
        policy_one = {
            "policy_id": "abc-abc-abc",
            "data": {
                "options": {
                    "xss": True
                }
            }
        }
        policy = AppSensorPolicy(policy_one)
        files_dict = MultiValueDict({
            'avatar': [FakeFile('<script>alert()</script>'), FakeFile('<script></script>')]
        })
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        request = FakeRequest('', {'CONTENT_LENGTH': 1024, 'HTTP_USER_AGENT': 'user_agent'}, {}, {}, files_dict, {})
        response = FakeResponse('AA', 200)
        appsensor_meta.set_request(request)
        appsensor_meta.set_response(type(response), response)

        with patch('tcell_agent.appsensor.injections_reporter.send_event') as patched_send_event:
            policy.process_appsensor_meta(appsensor_meta)
            patched_send_event.assert_has_calls(
                [
                    call(appsensor_meta, 'xss', 'avatar', {'l': 'body'}, None, '1'),
                    call(appsensor_meta, 'xss', 'avatar', {'l': 'body'}, None, '1')
                ],
                True
            )

    def uploading_two_files_for_different_params_test(self):
        policy_one = {
            "policy_id": "abc-abc-abc",
            "data": {
                "options": {
                    "xss": True
                }
            }
        }
        policy = AppSensorPolicy(policy_one)
        files_dict = MultiValueDict({
            'avatar': [FakeFile('<script>alert()</script>')],
            'picture': [FakeFile('<script>alert()</script>')]
        })
        appsensor_meta = AppSensorMeta()
        appsensor_meta.remote_address = "remote_addr"
        appsensor_meta.method = "request_method"
        appsensor_meta.location = "abosolute_uri"
        appsensor_meta.route_id = "route_id"
        appsensor_meta.session_id = "session_id"
        appsensor_meta.user_id = "user_id"

        request = FakeRequest('', {'CONTENT_LENGTH': 1024, 'HTTP_USER_AGENT': 'user_agent'}, {}, {}, files_dict, {})
        response = FakeResponse('AA', 200)
        appsensor_meta.set_request(request)
        appsensor_meta.set_response(type(response), response)

        with patch('tcell_agent.appsensor.injections_reporter.send_event') as patched_send_event:
            policy.process_appsensor_meta(appsensor_meta)
            patched_send_event.assert_has_calls(
                [
                    call(appsensor_meta, 'xss', 'picture', {'l': 'body'}, None, '1'),
                    call(appsensor_meta, 'xss', 'avatar', {'l': 'body'}, None, '1')
                ],
                True
            )
