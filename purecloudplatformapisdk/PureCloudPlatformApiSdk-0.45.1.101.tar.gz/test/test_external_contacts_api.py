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
from swagger_client.apis.external_contacts_api import ExternalContactsApi


class TestExternalContactsApi(unittest.TestCase):
    """ ExternalContactsApi unit test stubs """

    def setUp(self):
        self.api = swagger_client.apis.external_contacts_api.ExternalContactsApi()

    def tearDown(self):
        pass

    def test_delete_contacts_contact_id(self):
        """
        Test case for delete_contacts_contact_id

        Delete an external contact
        """
        pass

    def test_delete_contacts_contact_id_notes_note_id(self):
        """
        Test case for delete_contacts_contact_id_notes_note_id

        Delete a note for an external contact
        """
        pass

    def test_delete_organizations_externalorganization_id(self):
        """
        Test case for delete_organizations_externalorganization_id

        Delete an external organization
        """
        pass

    def test_delete_organizations_externalorganization_id_notes_note_id(self):
        """
        Test case for delete_organizations_externalorganization_id_notes_note_id

        Delete a note for an external organization
        """
        pass

    def test_delete_relationships_relationship_id(self):
        """
        Test case for delete_relationships_relationship_id

        Delete a relationship
        """
        pass

    def test_get_contacts(self):
        """
        Test case for get_contacts

        Search for external contacts
        """
        pass

    def test_get_contacts_contact_id(self):
        """
        Test case for get_contacts_contact_id

        Fetch an external contact
        """
        pass

    def test_get_contacts_contact_id_notes(self):
        """
        Test case for get_contacts_contact_id_notes

        List notes for an external contact
        """
        pass

    def test_get_contacts_contact_id_notes_note_id(self):
        """
        Test case for get_contacts_contact_id_notes_note_id

        Fetch a note for an external contact
        """
        pass

    def test_get_organizations(self):
        """
        Test case for get_organizations

        Search for external organizations
        """
        pass

    def test_get_organizations_externalorganization_id(self):
        """
        Test case for get_organizations_externalorganization_id

        Fetch an external organization
        """
        pass

    def test_get_organizations_externalorganization_id_contacts(self):
        """
        Test case for get_organizations_externalorganization_id_contacts

        Search for external contacts in an external organization
        """
        pass

    def test_get_organizations_externalorganization_id_notes(self):
        """
        Test case for get_organizations_externalorganization_id_notes

        List notes for an external organization
        """
        pass

    def test_get_organizations_externalorganization_id_notes_note_id(self):
        """
        Test case for get_organizations_externalorganization_id_notes_note_id

        Fetch a note for an external organization
        """
        pass

    def test_get_organizations_externalorganization_id_relationships(self):
        """
        Test case for get_organizations_externalorganization_id_relationships

        Fetch a relationship for an external organization
        """
        pass

    def test_get_relationships_relationship_id(self):
        """
        Test case for get_relationships_relationship_id

        Fetch a relationship
        """
        pass

    def test_get_reversewhitepageslookup(self):
        """
        Test case for get_reversewhitepageslookup

        Lookup contacts and externalOrganizations based on an attribute
        """
        pass

    def test_post_contacts(self):
        """
        Test case for post_contacts

        Create an external contact
        """
        pass

    def test_post_contacts_contact_id_associateconversation(self):
        """
        Test case for post_contacts_contact_id_associateconversation

        Associate an external contact with a conversation
        """
        pass

    def test_post_contacts_contact_id_notes(self):
        """
        Test case for post_contacts_contact_id_notes

        Create a note for an external contact
        """
        pass

    def test_post_organizations(self):
        """
        Test case for post_organizations

        Create an external organization
        """
        pass

    def test_post_organizations_externalorganization_id_notes(self):
        """
        Test case for post_organizations_externalorganization_id_notes

        Create a note for an external organization
        """
        pass

    def test_post_relationships(self):
        """
        Test case for post_relationships

        Create a relationship
        """
        pass

    def test_put_contacts_contact_id(self):
        """
        Test case for put_contacts_contact_id

        Update an external contact
        """
        pass

    def test_put_contacts_contact_id_notes_note_id(self):
        """
        Test case for put_contacts_contact_id_notes_note_id

        Update a note for an external contact
        """
        pass

    def test_put_conversations_conversation_id(self):
        """
        Test case for put_conversations_conversation_id

        Associate an external contact with a conversation
        """
        pass

    def test_put_organizations_externalorganization_id(self):
        """
        Test case for put_organizations_externalorganization_id

        Update an external organization
        """
        pass

    def test_put_organizations_externalorganization_id_notes_note_id(self):
        """
        Test case for put_organizations_externalorganization_id_notes_note_id

        Update a note for an external organization
        """
        pass

    def test_put_relationships_relationship_id(self):
        """
        Test case for put_relationships_relationship_id

        Update a relationship
        """
        pass


if __name__ == '__main__':
    unittest.main()