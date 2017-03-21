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
from swagger_client.apis.architect_api import ArchitectApi


class TestArchitectApi(unittest.TestCase):
    """ ArchitectApi unit test stubs """

    def setUp(self):
        self.api = swagger_client.apis.architect_api.ArchitectApi()

    def tearDown(self):
        pass

    def test_delete_prompts(self):
        """
        Test case for delete_prompts

        Batch-delete a list of prompts asynchronously
        """
        pass

    def test_delete_prompts_prompt_id(self):
        """
        Test case for delete_prompts_prompt_id

        Delete specified user prompt
        """
        pass

    def test_delete_prompts_prompt_id_resources_languagecode(self):
        """
        Test case for delete_prompts_prompt_id_resources_languagecode

        Delete specified user prompt resource
        """
        pass

    def test_delete_systemprompts_prompt_id_resources_languagecode(self):
        """
        Test case for delete_systemprompts_prompt_id_resources_languagecode

        Delete a system prompt resource override.
        """
        pass

    def test_get_flows(self):
        """
        Test case for get_flows

        Get a pageable list of flows, filtered by query parameters
        """
        pass

    def test_get_prompts(self):
        """
        Test case for get_prompts

        Get a pageable list of user prompts
        """
        pass

    def test_get_prompts_prompt_id(self):
        """
        Test case for get_prompts_prompt_id

        Get specified user prompt
        """
        pass

    def test_get_prompts_prompt_id_resources(self):
        """
        Test case for get_prompts_prompt_id_resources

        Get a pageable list of user prompt resources
        """
        pass

    def test_get_prompts_prompt_id_resources_languagecode(self):
        """
        Test case for get_prompts_prompt_id_resources_languagecode

        Get specified user prompt resource
        """
        pass

    def test_get_systemprompts(self):
        """
        Test case for get_systemprompts

        Get System Prompts
        """
        pass

    def test_get_systemprompts_prompt_id(self):
        """
        Test case for get_systemprompts_prompt_id

        Get a system prompt
        """
        pass

    def test_get_systemprompts_prompt_id_resources(self):
        """
        Test case for get_systemprompts_prompt_id_resources

        Get IVR System Prompt resources.
        """
        pass

    def test_get_systemprompts_prompt_id_resources_languagecode(self):
        """
        Test case for get_systemprompts_prompt_id_resources_languagecode

        Get a system prompt resource.
        """
        pass

    def test_post_prompts(self):
        """
        Test case for post_prompts

        Create a new user prompt
        """
        pass

    def test_post_prompts_prompt_id_resources(self):
        """
        Test case for post_prompts_prompt_id_resources

        Create a new user prompt resource
        """
        pass

    def test_post_systemprompts_prompt_id_resources(self):
        """
        Test case for post_systemprompts_prompt_id_resources

        Create system prompt resource override.
        """
        pass

    def test_put_prompts_prompt_id(self):
        """
        Test case for put_prompts_prompt_id

        Update specified user prompt
        """
        pass

    def test_put_prompts_prompt_id_resources_languagecode(self):
        """
        Test case for put_prompts_prompt_id_resources_languagecode

        Update specified user prompt resource
        """
        pass

    def test_put_systemprompts_prompt_id_resources_languagecode(self):
        """
        Test case for put_systemprompts_prompt_id_resources_languagecode

        Updates a system prompt resource override.
        """
        pass


if __name__ == '__main__':
    unittest.main()