# coding: utf-8

"""
Copyright 2016 SmartBear Software

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

   ref: https://github.com/swagger-api/swagger-codegen
"""

from __future__ import absolute_import

import os
import sys
import unittest

import swagger_client
from swagger_client.rest import ApiException
from swagger_client.apis.scripts_api import ScriptsApi


class TestScriptsApi(unittest.TestCase):
    """ ScriptsApi unit test stubs """

    def setUp(self):
        self.api = swagger_client.apis.scripts_api.ScriptsApi()

    def tearDown(self):
        pass

    def test_get_published(self):
        """
        Test case for get_published

        Get the published scripts.
        """
        pass

    def test_get_published_script_id(self):
        """
        Test case for get_published_script_id

        Get the published script.
        """
        pass

    def test_get_published_script_id_pages(self):
        """
        Test case for get_published_script_id_pages

        Get the list of published pages
        """
        pass

    def test_get_published_script_id_pages_page_id(self):
        """
        Test case for get_published_script_id_pages_page_id

        Get the published page.
        """
        pass

    def test_get_published_script_id_variables(self):
        """
        Test case for get_published_script_id_variables

        Get the published variables
        """
        pass

    def test_get_script_id(self):
        """
        Test case for get_script_id

        Get a script
        """
        pass

    def test_get_script_id_pages(self):
        """
        Test case for get_script_id_pages

        Get the list of pages
        """
        pass

    def test_get_script_id_pages_page_id(self):
        """
        Test case for get_script_id_pages_page_id

        Get a page
        """
        pass

    def test_get_scripts(self):
        """
        Test case for get_scripts

        Get the list of scripts
        """
        pass


if __name__ == '__main__':
    unittest.main()