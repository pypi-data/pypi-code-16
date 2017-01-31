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
from swagger_client.apis.search_api import SearchApi


class TestSearchApi(unittest.TestCase):
    """ SearchApi unit test stubs """

    def setUp(self):
        self.api = swagger_client.apis.search_api.SearchApi()

    def tearDown(self):
        pass

    def test_get_search(self):
        """
        Test case for get_search

        Search groups using the q64 value returned from a previous search
        """
        pass

    def test_get_search_0(self):
        """
        Test case for get_search_0

        Search locations using the q64 value returned from a previous search
        """
        pass

    def test_get_search_1(self):
        """
        Test case for get_search_1

        Search using the q64 value returned from a previous search.
        """
        pass

    def test_get_search_2(self):
        """
        Test case for get_search_2

        Search users using the q64 value returned from a previous search
        """
        pass

    def test_get_search_3(self):
        """
        Test case for get_search_3

        Search voicemails using the q64 value returned from a previous search
        """
        pass

    def test_get_suggest(self):
        """
        Test case for get_suggest

        Suggest resources using the q64 value returned from a previous suggest query.
        """
        pass

    def test_post_search(self):
        """
        Test case for post_search

        Search groups
        """
        pass

    def test_post_search_0(self):
        """
        Test case for post_search_0

        Search locations
        """
        pass

    def test_post_search_1(self):
        """
        Test case for post_search_1

        Search resources.
        """
        pass

    def test_post_search_2(self):
        """
        Test case for post_search_2

        Search users
        """
        pass

    def test_post_search_3(self):
        """
        Test case for post_search_3

        Search voicemails
        """
        pass

    def test_post_suggest(self):
        """
        Test case for post_suggest

        Suggest resources.
        """
        pass


if __name__ == '__main__':
    unittest.main()