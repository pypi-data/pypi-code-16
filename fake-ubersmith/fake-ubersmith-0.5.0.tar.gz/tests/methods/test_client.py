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

import unittest
from unittest.mock import patch

from fake_ubersmith.api.adapters.data_store import DataStore
from fake_ubersmith.api.methods.client import Client
from fake_ubersmith.api.ubersmith import FakeUbersmithError


class TestClientModule(unittest.TestCase):
    def setUp(self):
        self.data_store = DataStore()
        self.client = Client(self.data_store)

    @patch('fake_ubersmith.api.methods.client.response')
    def test_client_add_creates_a_client(self, m_resp):
        m_resp.return_value = '{"data": "1", ' \
                              '"error_code": null, ' \
                              '"error_message": "", ' \
                              '"status": true}'

        self.assertEqual(
            self.client.client_add(
                form_data={
                    'first': 'John',
                    'last': 'Smith',
                    'email': 'john.smith@invalid.com',
                    'uber_login': 'john',
                    'uber_pass': 'smith',
                }
            ),
            m_resp.return_value
        )

        m_resp.assert_called_once_with(data="1")

    @patch('fake_ubersmith.api.methods.client.response')
    def test_client_get_returns_successfully(self, m_resp):
        self.data_store.clients = [{"clientid": "1"}]

        m_resp.return_value = '{"data": {"clientid": "1"}, ' \
                              '"error_code": null, ' \
                              '"error_message": "", "status": true}'

        self.assertEqual(
            self.client.client_get(form_data={'client_id': '1'}),
            '{"data": {"clientid": "1"}, "error_code": null, '
            '"error_message": "", "status": true}'
        )

        m_resp.assert_called_once_with(data={"clientid": "1"})

    @patch('fake_ubersmith.api.methods.client.response')
    def test_client_get_errs_when_no_match(self, m_resp):
        self.data_store.clients = [{"clientid": "100"}]

        m_resp.return_value = '{"data": None, ' \
                              '"error_code": 1, ' \
                              '"error_message": ' \
                              '"Client ID \'1\' not found.", "status": false}'

        self.assertEqual(
            self.client.client_get(form_data={'client_id': '1'}),
            '{"data": None, "error_code": 1, '
            '"error_message": "Client ID \'1\' not found.", "status": false}'
        )

        m_resp.assert_called_once_with(
           error_code=1, message="Client ID '1' not found."
        )

    @patch('fake_ubersmith.api.methods.client.response')
    def test_client_contact_add_creates_a_contact(self, m_resp):
        m_resp.return_value = '{"data": "1", ' \
                              '"error_code": null, ' \
                              '"error_message": "", ' \
                              '"status": true}'

        self.assertEqual(
            self.client.contact_add(
                form_data={
                    'client_id': 1,
                    'real_name': 'John Doe',
                    'email': 'john.doe@invalid.com',
                    'login': 'john',
                    'password': 'doe',
                }
            ),
            m_resp.return_value
        )

        m_resp.assert_called_once_with(data="1")

    @patch('fake_ubersmith.api.methods.client.response')
    def test_client_cc_add_is_successful(self, m_resp):
        m_resp.return_value = '{"data": "1", ' \
                              '"error_code": null, ' \
                              '"error_message": "", "status": true}'

        self.assertEqual(
            self.client.client_cc_add(form_data={'client_id': '1'}),
            '{"data": "1", "error_code": null, '
            '"error_message": "", "status": true}'
        )

        m_resp.assert_called_once_with(data=1)

    @patch('fake_ubersmith.api.methods.client.response')
    def test_client_cc_add_fails_returns_error(self, m_resp):
        self.client.credit_card_response = FakeUbersmithError(999, 'oh fail')

        m_resp.return_value = '{"data": None, ' \
                              '"error_code": "999", ' \
                              '"error_message": "oh fail", "status": false}'

        self.assertEqual(
            self.client.client_cc_add(form_data={'client_id': '1'}),
            '{"data": None, "error_code": "999", '
            '"error_message": "oh fail", "status": false}'
        )

        m_resp.assert_called_once_with(error_code=999, message='oh fail')

    @patch('fake_ubersmith.api.methods.client.response')
    def test_client_cc_update_is_successful(self, m_resp):
        m_resp.return_value = '{"data": True, ' \
                              '"error_code": null, ' \
                              '"error_message": "", "status": true}'

        self.assertEqual(
            self.client.client_cc_add(form_data={'client_id': '1'}),
            '{"data": True, "error_code": null, '
            '"error_message": "", "status": true}'
        )

        m_resp.assert_called_once_with(data=True)

    @patch('fake_ubersmith.api.methods.client.response')
    def test_client_cc_update_fails_returns_error(self, m_resp):
        self.client.credit_card_response = FakeUbersmithError(999, 'oh fail')

        m_resp.return_value = '{"data": None, ' \
                              '"error_code": "999", ' \
                              '"error_message": "oh fail", "status": false}'

        self.assertEqual(
            self.client.client_cc_update(form_data={'client_id': '1'}),
            '{"data": None, "error_code": "999", '
            '"error_message": "oh fail", "status": false}'
        )

        m_resp.assert_called_once_with(error_code=999, message='oh fail')

    @patch('fake_ubersmith.api.methods.client.response')
    def test_client_cc_info_with_billing_info_id(self, m_resp):
        self.data_store.credit_cards = [{"billing_info_id": "123"}]

        m_resp.return_value = '{"data": {"123": {"billing_info_id": "123"}}, ' \
                              '"error_code": null, ' \
                              '"error_message": "", "status": true}'

        self.assertEqual(
            self.client.client_cc_info(form_data={'billing_info_id': '123'}),
            '{"data": {"123": {"billing_info_id": "123"}}, "error_code": null, '
            '"error_message": "", "status": true}'
        )

        m_resp.assert_called_once_with(data={"123": {"billing_info_id": "123"}})

    @patch('fake_ubersmith.api.methods.client.response')
    def test_client_cc_info_with_client_id(self, m_resp):
        self.data_store.credit_cards = [
            {
                "clientid": "1",
                "billing_info_id": "123"
            }
        ]

        m_resp.return_value = '{"data": {"123": {"clientid": "1", ' \
                              '"billing_info_id": "123"}}, ' \
                              '"error_code": null, ' \
                              '"error_message": "", "status": true}'

        self.assertEqual(
            self.client.client_cc_info(form_data={'client_id': '1'}),
            '{"data": {"123": {"clientid": "1", "billing_info_id": "123"}}, '
            '"error_code": null, "error_message": "", "status": true}'
        )

        m_resp.assert_called_once_with(
            data={"123": {"clientid": "1", "billing_info_id": "123"}}
        )

    @patch('fake_ubersmith.api.methods.client.response')
    def test_client_cc_info_fails(self, m_resp):
        self.data_store.credit_cards = [
            {
                "clientid": "1",
                "billing_info_id": "123"
            }
        ]

        m_resp.return_value = '{"data": None, ' \
                              '"error_code": "1", ' \
                              '"error_message": ' \
                              '"request failed: ' \
                              'client_id parameter not supplied", ' \
                              '"status": false}'

        self.assertEqual(
            self.client.client_cc_info(form_data={'bogus': 'thing'}),
            '{"data": None, "error_code": "1", '
            '"error_message": '
            '"request failed: client_id parameter not supplied", '
            '"status": false}'
        )

        m_resp.assert_called_once_with(
            error_code=1,
            message='request failed: client_id parameter not supplied'
        )

    @patch('fake_ubersmith.api.methods.client.response')
    def test_client_cc_delete_is_successful(self, m_resp):
        m_resp.return_value = '{"data": "True", ' \
                              '"error_code": null, ' \
                              '"error_message": "", "status": true}'

        self.assertEqual(
            self.client.client_cc_add(form_data={'client_id': '1'}),
            '{"data": "True", "error_code": null, '
            '"error_message": "", "status": true}'
        )

        m_resp.assert_called_once_with(data=True)

    @patch('fake_ubersmith.api.methods.client.response')
    def test_client_cc_delete_fails(self, m_resp):
        self.client.credit_card_delete_response = FakeUbersmithError(
            999, 'oh fail'
        )

        m_resp.return_value = '{"data": None, ' \
                              '"error_code": "999", ' \
                              '"error_message": "oh fail", "status": false}'

        self.assertEqual(
            self.client.client_cc_delete(form_data={'client_id': '1'}),
            '{"data": None, "error_code": "999", '
            '"error_message": "oh fail", "status": false}'
        )

        m_resp.assert_called_once_with(error_code=999, message='oh fail')
