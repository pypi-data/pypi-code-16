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

import argparse
import kubos
import mock
import sys
import unittest
import yotta.remove

from kubos.test.utils import  KubosTestCase

class KubosRemoveTest(KubosTestCase):
    '''
    Since the kubos remove command proxies to the default yotta implementation
    this test only looks to make sure that the yotta implementation is called.
    There's a separate yotta unit test to test the remove functionality.
    '''
    def setUp(self):
        super(KubosRemoveTest, self).setUp()
        self.test_function = mock.MagicMock()
        yotta.remove.execCommand = self.test_function
        self.test_command = 'remove'
        sys.argv.append(self.test_command)


    def test_remove(self):
        kubos.main()
        self.assert_test_function_call()


    def tearDown(self):
        super(KubosRemoveTest, self).tearDown()


if __name__ == '__main__':
    unittest.main()
