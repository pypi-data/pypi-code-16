# Copyright 2016 Internap
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

from flexmock import flexmock, flexmock_teardown

from tests import mock_ubersmith_client, mock_ubersmith_api
from ubersmith_remote_module_server import remote
from ubersmith_remote_module_server.exceptions import NoRequestContext, NamedArgumentsOnly
from ubersmith_remote_module_server.objects import RequestContext
from ubersmith_remote_module_server.remote import RemoteExecutor, ubersmith, \
    ConfiguredRequestContext


class UbersmithCoreTest(unittest.TestCase):
    def test_raises_when_out_of_context(self):
        remote_executor_mock = flexmock()
        flexmock(remote).should_receive('RemoteExecutor').and_return(remote_executor_mock)
        with self.assertRaises(NoRequestContext):
            ubersmith.test()

    def test_raises_when_args(self):
        remote_executor_mock = flexmock()
        flexmock(remote).should_receive('RemoteExecutor').and_return(remote_executor_mock)
        with self.assertRaises(NamedArgumentsOnly):
            ubersmith.test('hello')

    def test_calls_executor_with_context_when_called(self):
        remote_executor_mock = flexmock()
        flexmock(remote).should_receive('RemoteExecutor'). \
            with_args(context='context').and_return(remote_executor_mock).once()
        remote_executor_mock.should_receive('invoke_global').with_args('test', args={}).once()

        with ConfiguredRequestContext(context='context'):
            ubersmith.test()

    def tearDown(self):
        flexmock_teardown()
        super(UbersmithCoreTest, self).tearDown()


class RemoteExecutorTest(unittest.TestCase):
    def test_invoke_global_from_device_module(self):
        ubersmith_client = mock_ubersmith_client()
        ubersmith_api = mock_ubersmith_api()

        flexmock(remote).should_receive('ubersmith_client').and_return(ubersmith_client)

        ubersmith_client.api.should_receive('init')\
            .with_args(url='http://ubersmith.example/url',
                       password='pass',
                       user='user')\
            .and_return(ubersmith_api)

        ubersmith_api.device.should_receive('module_call').\
            with_args(device_id=20025,
                      function='_web_hook_invoke_global',
                      module_id=173,
                      module_params=['logevent', [dict(action='hello from python')]])

        remote_executor = RemoteExecutor(
            context=RequestContext(callback_url='http://user:pass@ubersmith.example/url',
                                   module_id=173, device_id=20025))
        remote_executor.invoke_global('logevent', dict(action='hello from python'))

    def test_invoke_global_from_service_module(self):
        ubersmith_client = mock_ubersmith_client()
        ubersmith_api = mock_ubersmith_api()

        flexmock(remote).should_receive('ubersmith_client').and_return(ubersmith_client)

        ubersmith_client.api.should_receive('init')\
            .with_args(url='http://ubersmith.example/url',
                       password='pass',
                       user='user')\
            .and_return(ubersmith_api)

        ubersmith_api.client.should_receive('service_module_call').\
            with_args(service_id=1260,
                      function='_web_hook_invoke_global',
                      module_id=44,
                      module_params=['logevent', [dict(action='hello from python')]])

        remote_executor = RemoteExecutor(
            context=RequestContext(callback_url='http://user:pass@ubersmith.example/'
                                                'url?method=method',
                                   module_id=44,
                                   service_id=1260))
        remote_executor.invoke_global('logevent', dict(action='hello from python'))

    def tearDown(self):
        flexmock_teardown()
        super(RemoteExecutorTest, self).tearDown()
