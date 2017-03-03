# Copyright 2016 Internap.
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

from . import ContextMatcher
from ubersmith_remote_module_server import remote
from ubersmith_remote_module_server.objects import RequestContext
from ubersmith_remote_module_server.router import Router
from ubersmith_remote_module_server.remote import ubersmith


class FakeModule(object):
    def call_uber_core(self):
        ubersmith.test()


class RouterUbersmithCoreTest(unittest.TestCase):
    def test_a_module_can_call_ubersmith_core_without_context(self):
        fake_module = FakeModule()
        remote_executor_mock = flexmock()

        flexmock(remote).should_receive('RemoteExecutor').\
            with_args(context=RequestContext).and_return(remote_executor_mock)

        remote_executor_mock.should_receive('invoke_global').with_args('test', args={}).once()

        self.basic_router = Router(env_as_kwarg=False)
        self.basic_router.invoke_method(module=fake_module, method='call_uber_core')

    def test_module_context_is_injected_when_service_module(self):
        fake_module = FakeModule()
        remote_executor_mock = flexmock()

        example_callback = {'params': {'module_id': '44', 'service_id': '1260'},
                            'url': 'http://user:pass@ubersmith.example/'
                                   'api/2.0/?method=service.module_call'}

        flexmock(remote).should_receive('RemoteExecutor'). \
            with_args(context=ContextMatcher(callback_url=example_callback['url'],
                                             module_id='44',
                                             service_id='1260'))\
            .and_return(remote_executor_mock)

        remote_executor_mock.should_receive('invoke_global')

        self.basic_router = Router(env_as_kwarg=False)
        self.basic_router.invoke_method(module=fake_module,
                                        method='call_uber_core',
                                        callback=example_callback)

    def test_module_context_is_injected_when_device_module(self):
        fake_module = FakeModule()

        example_callback = {'params': {'module_id': '173', 'device_id': '200025'},
                            'url': 'http://user:pass@ubersmith.example/'
                                   'api/2.0/?method=device.module_call'}

        remote_executor_mock = flexmock()
        flexmock(remote).should_receive('RemoteExecutor'). \
            with_args(context=ContextMatcher(callback_url=example_callback['url'],
                                             module_id='173',
                                             device_id='200025'))\
            .and_return(remote_executor_mock)

        remote_executor_mock.should_receive('invoke_global')

        self.basic_router = Router(env_as_kwarg=False)
        self.basic_router.invoke_method(module=fake_module,
                                        method='call_uber_core',
                                        callback=example_callback)

    def tearDown(self):
        flexmock_teardown()
        super(RouterUbersmithCoreTest, self).tearDown()
