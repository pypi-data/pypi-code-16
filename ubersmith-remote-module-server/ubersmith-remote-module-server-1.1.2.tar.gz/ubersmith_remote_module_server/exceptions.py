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


class NoRequestContext(Exception):
    def __init__(self, msg="UbersmithCore was called without a context, "
                           "you can't save this object"):
        super(NoRequestContext, self).__init__(msg)


class NamedArgumentsOnly(Exception):
    def __init__(self, msg="UbersmithCore was called with non-named arguments, "
                           "you MUST use named arguments (kwargs)"):
        super(NamedArgumentsOnly, self).__init__(msg)
