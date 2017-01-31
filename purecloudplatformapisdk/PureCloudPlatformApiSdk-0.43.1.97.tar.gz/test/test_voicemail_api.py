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
from swagger_client.apis.voicemail_api import VoicemailApi


class TestVoicemailApi(unittest.TestCase):
    """ VoicemailApi unit test stubs """

    def setUp(self):
        self.api = swagger_client.apis.voicemail_api.VoicemailApi()

    def tearDown(self):
        pass

    def test_delete_messages(self):
        """
        Test case for delete_messages

        Delete all voicemail messages
        """
        pass

    def test_delete_messages_message_id(self):
        """
        Test case for delete_messages_message_id

        Delete a message.
        """
        pass

    def test_get_groups_group_id_mailbox(self):
        """
        Test case for get_groups_group_id_mailbox

        Get the group's mailbox information
        """
        pass

    def test_get_groups_group_id_messages(self):
        """
        Test case for get_groups_group_id_messages

        List voicemail messages
        """
        pass

    def test_get_groups_group_id_policy(self):
        """
        Test case for get_groups_group_id_policy

        Get a group's voicemail policy
        """
        pass

    def test_get_mailbox(self):
        """
        Test case for get_mailbox

        Get the current user's mailbox information
        """
        pass

    def test_get_me_mailbox(self):
        """
        Test case for get_me_mailbox

        Get the current user's mailbox information
        """
        pass

    def test_get_me_messages(self):
        """
        Test case for get_me_messages

        List voicemail messages
        """
        pass

    def test_get_me_policy(self):
        """
        Test case for get_me_policy

        Get the current user's voicemail policy
        """
        pass

    def test_get_messages(self):
        """
        Test case for get_messages

        List voicemail messages
        """
        pass

    def test_get_messages_message_id(self):
        """
        Test case for get_messages_message_id

        Get message.
        """
        pass

    def test_get_messages_message_id_media(self):
        """
        Test case for get_messages_message_id_media

        Get media playback URI for this message
        """
        pass

    def test_get_policy(self):
        """
        Test case for get_policy

        Get a policy
        """
        pass

    def test_get_search(self):
        """
        Test case for get_search

        Search voicemails using the q64 value returned from a previous search
        """
        pass

    def test_get_userpolicies_user_id(self):
        """
        Test case for get_userpolicies_user_id

        Get a user's voicemail policy
        """
        pass

    def test_patch_groups_group_id_policy(self):
        """
        Test case for patch_groups_group_id_policy

        Update a group's voicemail policy
        """
        pass

    def test_patch_me_policy(self):
        """
        Test case for patch_me_policy

        Update the current user's voicemail policy
        """
        pass

    def test_patch_userpolicies_user_id(self):
        """
        Test case for patch_userpolicies_user_id

        Update a user's voicemail policy
        """
        pass

    def test_post_messages(self):
        """
        Test case for post_messages

        Copy a voicemail message to a user or group
        """
        pass

    def test_post_search(self):
        """
        Test case for post_search

        Search voicemails
        """
        pass

    def test_put_messages_message_id(self):
        """
        Test case for put_messages_message_id

        Update a message.
        """
        pass

    def test_put_policy(self):
        """
        Test case for put_policy

        Update a policy
        """
        pass


if __name__ == '__main__':
    unittest.main()