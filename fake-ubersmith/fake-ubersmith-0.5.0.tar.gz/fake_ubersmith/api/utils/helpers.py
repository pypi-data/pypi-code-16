# Copyright 2017 Internap.
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


def record(method):
    def wrap(fn):
        def wrapper(*args, **kwargs):
            self = args[0]
            if method not in self.records:
                self.records[method] = []
            self.records[method].append({'args': args, 'kwargs': kwargs})
            return fn(*args, **kwargs)
        return wrapper
    return wrap
