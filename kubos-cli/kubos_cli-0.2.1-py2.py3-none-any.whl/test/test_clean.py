# Kubos CLI
# Copyright (C) 2016 Kubos Corporation
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

import kubos
import mock
import sys
import unittest
import yotta.clean

from kubos.test.utils import  KubosTestCase

class KubosCleanTest(KubosTestCase):
    '''
    Since the kubos clean command proxies to the default yotta implementation
    this test only looks to make sure that the yotta implementation is called.
    There's a separate yotta unit test to test the clean functionality.
    '''
    def setUp(self):
        super(KubosCleanTest, self).setUp()
        self.test_function = mock.MagicMock()
        yotta.clean.execCommand = self.test_function
        self.test_command = 'clean'
        sys.argv.append(self.test_command)


    def test_list(self):
        kubos.main()
        call_list = self.test_function.call_args.call_list()
        self.assertTrue(len(call_list) == 1)
        args, kwargs = call_list[0]
        arg_dict = vars(args[0])
        self.assertTrue(arg_dict['subcommand_name'] == self.test_command)


    def tearDown(self):
        super(KubosCleanTest, self).tearDown()

if __name__ == '__main__':
    unittest.main()
