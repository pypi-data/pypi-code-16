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
from fake_ubersmith.api.base import Base
from fake_ubersmith.api.ubersmith import FakeUbersmithError
from fake_ubersmith.api.utils.response import response


class Uber(Base):
    def __init__(self, data_store):
        super().__init__(data_store)

        self.service_plan_error = None

    def hook_to(self, entity):
        entity.register_endpoints(
            ubersmith_method='uber.service_plan_get',
            function=self.service_plan_get
        )
        entity.register_endpoints(
            ubersmith_method='uber.service_plan_list',
            function=self.service_plan_list
        )
        entity.register_endpoints(
            ubersmith_method='uber.check_login',
            function=self.check_login
        )

    def check_login(self, form_data):
        data = self._get_client(form_data['login'], form_data['pass'])

        if data:
            data['type'] = 'client'
            return response(data=data)

        return response(
            error_code=3, message="Invalid login or password."
        )

    def service_plan_get(self, form_data):
        if isinstance(self.service_plan_error, FakeUbersmithError):
            return response(
               error_code=self.service_plan_error.code,
               message=self.service_plan_error.message
            )

        service_plan = next(
            (
                plan for plan in self.data_store.service_plans
                if plan["plan_id"] == form_data["plan_id"]
            ),
            None
        )

        if service_plan is not None:
            return response(data=service_plan)
        else:
            return response(
                error_code=3,
                message="No Service Plan found"
            )

    def service_plan_list(self, form_data):
        if 'code' in form_data:
            plan_code = form_data['code']
            return response(
                data={
                    plan['plan_id']: plan
                    for plan in self.data_store.service_plans_list.values()
                    if plan['code'] == plan_code
                }
            )
        return response(data=self.data_store.service_plans_list)

    def _get_client(self, username, password):
        def _build_payload(client_id, contact_id, login):
            return {"client_id": client_id, "contact_id": contact_id, "login": login}

        def _get_contact():
            return next(
                (_build_payload(c['client_id'], c["contact_id"], c["login"]) for c in self.data_store.contacts if
                 c['login'] == username and c['password'] == password), None
            )

        return next(
            (_build_payload(c['clientid'], int(c["contact_id"]), c["login"]) for c in self.data_store.clients if
             c['login'] == username and c['uber_pass'] == password),
            _get_contact()
        )
