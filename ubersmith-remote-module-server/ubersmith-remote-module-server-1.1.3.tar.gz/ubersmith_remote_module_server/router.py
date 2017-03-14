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

from ubersmith_remote_module_server.objects import RequestContext
from ubersmith_remote_module_server.remote import ConfiguredRequestContext


class Router(object):
    def __init__(self, env_as_kwarg=True):
        self.env_as_kwarg = env_as_kwarg

    def invoke_method(self, module, method, params=None, env=None, callback=None):
        if params is None:
            params = []
        if env is None:
            env = {}

        if self.env_as_kwarg:
            additional_kwargs = {'env': env}
        else:
            additional_kwargs = {}

        with ConfiguredRequestContext(context=self._build_request_context(callback)):
            return getattr(module, method)(*params, **additional_kwargs)

    def _build_request_context(self, callback):
        callback = callback or {}
        params = callback.get('params', {})
        if isinstance(params, list):
            params = dict()
        return RequestContext(callback_url=callback.get('url'),
                              module_id=params.get('module_id'),
                              device_id=params.get('device_id'),
                              service_id=params.get('service_id'))

    def list_implemented_methods(self, module):
        return [method for method in dir(module) if callable(getattr(module, method)) and not method.startswith('_')]
