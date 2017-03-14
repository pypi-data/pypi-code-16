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

import ubersmith_client
from six.moves.urllib.parse import urlparse

from ubersmith_remote_module_server.exceptions import NoRequestContext, NamedArgumentsOnly

_configuration = None

__all__ = ['ubersmith']


class ConfiguredRequestContext(object):
    def __init__(self, **kwargs):
        self.kwargs = kwargs or {}

    def __enter__(self):
        global _configuration
        _configuration = self.kwargs

    def __exit__(self, exc_type, exc_val, exc_tb):
        global _configuration
        _configuration = None


class UbersmithRemoteProxy(object):
    def _invoke_method(self, name, *args, **kwargs):
        global _configuration
        if args:
            raise NamedArgumentsOnly()
        if _configuration is None:
            raise NoRequestContext()
        executor = RemoteExecutor(**_configuration)
        executor.invoke_global(name, args=kwargs)

    def __getattr__(self, func_name):
        def invoke_without_name(*args, **kwargs):
            return self._invoke_method(func_name, *args, **kwargs)
        return invoke_without_name


class RemoteExecutor(object):
    def __init__(self, context):
        self.context = context

    def invoke_global(self, func_name, args):
        url = urlparse(self.context.callback_url)
        ubersmith_url = "{0}://{1}{2}".format(url.scheme, url.hostname, url.path)
        ubersmith_api = ubersmith_client.api.init(url=ubersmith_url,
                                                  user=url.username,
                                                  password=url.password)
        if self.context.device_id:
            ubersmith_api.device.module_call(device_id=self.context.device_id,
                                             module_id=self.context.module_id,
                                             function='_web_hook_invoke_global',
                                             module_params=[func_name, [args]])
        else:
            ubersmith_api.client.service_module_call(service_id=self.context.service_id,
                                                     module_id=self.context.module_id,
                                                     function='_web_hook_invoke_global',
                                                     module_params=[func_name, [args]])

ubersmith = UbersmithRemoteProxy()
