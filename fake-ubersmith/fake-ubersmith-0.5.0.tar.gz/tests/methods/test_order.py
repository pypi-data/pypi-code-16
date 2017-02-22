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

from werkzeug.datastructures import ImmutableMultiDict

from fake_ubersmith.api.adapters.data_store import DataStore
from fake_ubersmith.api.methods.order import Order
from fake_ubersmith.api.ubersmith import FakeUbersmithError


class TestOrderModule(unittest.TestCase):
    def setUp(self):
        self.data_store = DataStore()
        self.order = Order(self.data_store)

    @patch('fake_ubersmith.api.methods.order.response')
    def test_coupon_get_returns_successfully(self, m_resp):
        self.coupons = [
            {"coupon": {"coupon_code": "1"}},
            {"coupon": {"coupon_code": "2"}}
        ]

        m_resp.return_value = '{"data": {"coupon": {"coupon_code": "1"}}, ' \
                              '"error_code": null, ' \
                              '"error_message": "", "status": true}'

        self.assertEqual(
            self.order.coupon_get(form_data={"coupon_code": "1"}),
            '{"data": {"coupon": {"coupon_code": "1"}}, "error_code": null, '
            '"error_message": "", "status": true}'
        )

        m_resp.asert_called_once_with(data={"coupon": {"coupon_code": "1"}})

    @patch('fake_ubersmith.api.methods.order.response')
    def test_coupon_get_returns_error(self, m_resp):
        self.coupons = [
            {"coupon": {"coupon_code": "100"}},
            {"coupon": {"coupon_code": "200"}}
        ]

        m_resp.return_value = '{"data": None, "error_code": 1, ' \
                              '"error_message": ' \
                              '"could not get coupon info for", ' \
                              '"status": false}'

        self.assertEqual(
            self.order.coupon_get(form_data={"coupon_code": "1"}),
            '{"data": None, "error_code": 1, '
            '"error_message": "could not get coupon info for", "status": false}'
        )

        m_resp.asert_called_once_with(
            error_code=1,
            message="could not get coupon info for")

    @patch('fake_ubersmith.api.methods.order.response')
    def test_create_order_succeeds(self, m_resp):
        self.data_store.order = {"100": {"order_id": "100"}}

        m_resp.return_value = '{"data": {"order_id": "100"}, ' \
                              '"error_code": null, ' \
                              '"error_message": "", "status": true}'

        self.assertEqual(
            self.order.create_order(
                form_data=ImmutableMultiDict([('order_id', '100')])
            ),
            '{"data": {"order_id": "100"}, "error_code": null, '
            '"error_message": "", "status": true}'
        )

        m_resp.assert_called_once_with(data={"order_id": "100"})

    @patch('fake_ubersmith.api.methods.order.response')
    def test_create_order_errs(self, m_resp):
        self.data_store.order = {
            "100": FakeUbersmithError(code=999, message='epic fail')
        }

        m_resp.return_value = '{"data": None, ' \
                              '"error_code": 999, ' \
                              '"error_message": "epic fail", "status": false}'

        self.assertEqual(
            self.order.create_order(
                form_data=ImmutableMultiDict([('order_id', '100')])
            ),
            '{"data": None, "error_code": 999, '
            '"error_message": "epic fail", "status": false}'
        )

        m_resp.assert_called_once_with(error_code=999, message='epic fail')

    @patch('fake_ubersmith.api.methods.order.response')
    def test_order_respond_responds(self, m_response):
        self.order.order_respond(form_data=ImmutableMultiDict([]))
        m_response.assert_called_once_with(data=8)

    @patch('fake_ubersmith.api.methods.order.response')
    def test_submit_order_is_successful(self, m_resp):
        self.data_store.order_submit = {"100": {"order_id": "100"}}

        m_resp.return_value = '{"data": {"order_id": "100"}, ' \
                              '"error_code": null, ' \
                              '"error_message": "", "status": true}'

        self.assertEqual(
            self.order.submit_order(
                form_data=ImmutableMultiDict([('order_id', '100')])
            ),
            '{"data": {"order_id": "100"}, "error_code": null, '
            '"error_message": "", "status": true}'
        )

        m_resp.assert_called_once_with(data={"order_id": "100"})

    @patch('fake_ubersmith.api.methods.order.response')
    def test_submit_order_errs(self, m_resp):
        self.data_store.order_submit = {
            "100": FakeUbersmithError(code=999, message='epic fail')
        }

        m_resp.return_value = '{"data": None, ' \
                              '"error_code": 999, ' \
                              '"error_message": "epic fail", "status": false}'

        self.assertEqual(
            self.order.submit_order(
                form_data=ImmutableMultiDict([('order_id', '100')])
            ),
            '{"data": None, "error_code": 999, '
            '"error_message": "epic fail", "status": false}'
        )

        m_resp.assert_called_once_with(error_code=999, message='epic fail')

    @patch('fake_ubersmith.api.methods.order.response')
    def test_cancel_order_is_successful(self, m_resp):
        self.data_store.order_cancel = {"100": {"order_id": "100"}}

        m_resp.return_value = '{"data": {"order_id": "100"}, ' \
                              '"error_code": null, ' \
                              '"error_message": "", "status": true}'

        self.assertEqual(
            self.order.cancel_order(
                form_data=ImmutableMultiDict([('order_id', '100')])
            ),
            '{"data": {"order_id": "100"}, "error_code": null, '
            '"error_message": "", "status": true}'
        )

        m_resp.assert_called_once_with(data={"order_id": "100"})

    @patch('fake_ubersmith.api.methods.order.response')
    def test_cancel_order_errs(self, m_resp):
        self.data_store.order_cancel = {
            "100": FakeUbersmithError(code=999, message='epic fail')
        }

        m_resp.return_value = '{"data": None, ' \
                              '"error_code": 999, ' \
                              '"error_message": "epic fail", "status": false}'

        self.assertEqual(
            self.order.cancel_order(
                form_data=ImmutableMultiDict([('order_id', '100')])
            ),
            '{"data": None, "error_code": 999, '
            '"error_message": "epic fail", "status": false}'
        )

        m_resp.assert_called_once_with(error_code=999, message='epic fail')
