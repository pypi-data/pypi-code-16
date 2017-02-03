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
# limitations under the License.import argparse

import argparse
import json
import kubos
import os
import mock
import sys
import unittest
import yotta.link
import yotta.test.cli.util as yotta_util

from kubos.utils import sdk_utils
from kubos.test import utils


class KubosLinkTest(utils.KubosTestCase):

    def setUp(self):
        super(KubosLinkTest, self).setUp()
        self.args = argparse.Namespace()
        self.test_command = 'link'
        sys.argv.append(self.test_command)


    def test_proxy_to_yotta(self):
        #Set up this specific test case
        self.test_function = mock.MagicMock()
        yotta.link.execCommand = self.test_function
        #run the test
        kubos.main()
        self.assert_test_function_call()


    def test_link_all_to_proj(self):
        #setup this test's specifics
        self.test_function = mock.MagicMock()
        sdk_utils.link_global_cache_to_project = self.test_function
        self.proj_file = os.path.join(self.base_dir, 'module.json')
        with open(self.proj_file, 'w') as module_json:
            module_json.write(json.dumps(yotta_util.Test_Trivial_Lib)) #Yotta's test module.json file contents
        sys.argv.append('--all')
        #run the test
        kubos.main()
        self.test_function.assert_called_once()

    def tearDown(self):
        super(KubosLinkTest, self).tearDown()

if __name__ == '__main__':
    unittest.main()
