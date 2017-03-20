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
import json
import unittest

from flask import Flask

from fake_ubersmith.api.adapters.data_store import DataStore
from fake_ubersmith.api.methods.uber import Uber
from fake_ubersmith.api.ubersmith import FakeUbersmithError, UbersmithBase


class TestUberModule(unittest.TestCase):

    def setUp(self):
        self.data_store = DataStore()
        self.uber = Uber(self.data_store)

        self.app = Flask(__name__)
        self.base_uber_api = UbersmithBase(self.data_store)

        self.uber.hook_to(self.base_uber_api)
        self.base_uber_api.hook_to(self.app)

    def test_service_plan_get_returns_if_service_plan_found(self):
        self.data_store.service_plans = [{"plan_id": "1"}]

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={"method": "uber.service_plan_get", "plan_id": "1"}
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": {"plan_id": "1"},
                "error_code": None,
                "error_message": "",
                "status": True
            }
        )

    def test_service_plan_get_errs_if_service_plan_not_found(self):
        self.data_store.service_plans = [{"plan_id": 1}]

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={"method": "uber.service_plan_get", "plan_id": "100"}
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": "",
                "error_code": 3,
                "error_message": "No Service Plan found",
                "status": False
            }
        )

    def test_service_plan_get_errs_with_service_plan_error(self):
        self.uber.service_plan_error = FakeUbersmithError(
            999, 'some error'
        )

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={"method": "uber.service_plan_get", "plan_id": "100"}
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": "",
                "error_code": 999,
                "error_message": "some error",
                "status": False
            }
        )

    def test_service_plan_list_returns_all_plans(self):

        self.data_store.service_plans_list = {
            "1": {"code": "42"},
            "2": {"code": "99"}
        }

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={"method": "uber.service_plan_list"}
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": {"1": {"code": "42"}, "2": {"code": "99"}},
                "error_code": None,
                "error_message": "",
                "status": True
            }
        )

    def test_service_plan_list_returns_plans_matching_code(self):
        self.data_store.service_plans_list = {
            "1": {"plan_id": "1", "code": "42"},
            "2": {"plan_id": "1", "code": "99"}
        }

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={"method": "uber.service_plan_list", 'code': '42'}
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": {"1": {"code": "42", "plan_id": "1"}},
                "error_code": None,
                "error_message": "",
                "status": True
            }
        )

    def test_check_login_succesfully_for_client(self):
        self.data_store.clients = [
            {
                'clientid': '1',
                'contact_id': '0',
                'first': 'John',
                'last': 'Smith',
                'email': 'john.smith@invalid.com',
                'login': 'john',
                'uber_pass': 'smith',
            }
        ]

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={
                    "method": "uber.check_login",
                    "login": "john",
                    "pass": "smith"
                }
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": {
                    "client_id": "1", "contact_id": 0, "type": "client", "login": "john"
                },
                "error_code": None,
                "error_message": "", "status": True
            }
        )

    def test_check_login_failed(self):
        self.data_store.clients = [
            {
                'clientid': '1',
                'first': 'John',
                'last': 'Smith',
                'email': 'john.smith@invalid.com',
                'login': 'john',
                'uber_pass': 'smith',
            }
        ]

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={
                    "method": "uber.check_login",
                    "login": "john",
                    "pass": "doe"
                }
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": "",
                "error_code": 3,
                "error_message": "Invalid login or password.",
                "status": False
            }
        )

    def test_check_login_sucessfully_for_contact(self):
        self.data_store.contacts = [
            {
                'client_id': '1234',
                'contact_id': '1',
                'real_name': 'Line Doe',
                'email': 'line.doe@invalid.com',
                'login': 'line',
                'password': 'doe',
            }
        ]

        with self.app.test_client() as c:
            resp = c.post(
                'api/2.0/',
                data={
                    "method": "uber.check_login",
                    "login": "line",
                    "pass": "doe"
                }
            )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            json.loads(resp.data.decode('utf-8')),
            {
                "data": {"client_id": "1234", "contact_id": "1", "type": "client", "login": "line"},
                "error_code": None,
                "error_message": "",
                "status": True
            }
        )
