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

from flask import make_response, request

from fake_ubersmith.fake_server import FlaskServer


def record(method):
    def wrap(fn):
        def wrapper(*args, **kwargs):
            self = args[0]
            if method not in self.records:
                self.records[method] = []
            self.records[method].append({'args': args, 'kwargs': kwargs})
            return fn(*args, **kwargs)

        return wrapper
    return wrap


class FakeUbersmithError(object):
    def __init__(self, code=None, message=None):
        self.code = code
        self.message = message


class FakeUbersmith(FlaskServer):

    def __init__(self, port=9131, *args, **kwargs):
        super(FakeUbersmith, self).__init__("fake-ubersmith", port, *args, **kwargs)

        self.post_methods = {}
        self.service_plans = []
        self.service_plans_list = None
        self.credit_cards = []
        self.coupons = []
        self.countries = {}
        self.order = {}
        self.order_submit = {}
        self.order_cancel = {}
        self.records = {}
        self.clients = []
        self.credit_card_response = 1
        self.credit_card_delete_response = True
        self.service_plan_error = None

        self.server.add_url_rule('/api/2.0/', view_func=self._route_post_method, methods=["POST"])

        self._register_post_endpoints()

    def start(self):
        r = super(FakeUbersmith, self).start()
        self.records = {}
        return r

    def _register_post_endpoints(self):
        self._add_post_endpoint(ubersmith_method='uber.service_plan_get', function=self.service_plan_get)
        self._add_post_endpoint(ubersmith_method='uber.service_plan_list', function=self.service_plan_list)
        self._add_post_endpoint(ubersmith_method='order.coupon_get', function=self.coupon_get)
        self._add_post_endpoint(ubersmith_method='order.create', function=self.create_order)
        self._add_post_endpoint(ubersmith_method='order.respond', function=self.order_respond)
        self._add_post_endpoint(ubersmith_method='order.submit', function=self.submit_order)
        self._add_post_endpoint(ubersmith_method='order.cancel', function=self.cancel_order)
        self._add_post_endpoint(ubersmith_method='client.cc_add', function=self.client_cc_add)
        self._add_post_endpoint(ubersmith_method='client.cc_update', function=self.client_cc_update)
        self._add_post_endpoint(ubersmith_method='client.cc_info', function=self.client_cc_info)
        self._add_post_endpoint(ubersmith_method='client.cc_delete', function=self.client_cc_delete)
        self._add_post_endpoint(ubersmith_method='client.get', function=self.client_get)

    def _route_post_method(self):
        return self.post_methods[request.form['method']](request.form)

    def _add_post_endpoint(self, ubersmith_method, function):
        self.post_methods[ubersmith_method] = function

    @record(method='plan.get')
    def service_plan_get(self, form_data):
        if self.service_plan_error and isinstance(self.service_plan_error, FakeUbersmithError):
            return error(self.service_plan_error.code, self.service_plan_error.message)

        service_plan = next((plan for plan in self.service_plans if plan["plan_id"] == form_data["plan_id"]), None)
        if service_plan is not None:
            return response(service_plan)
        else:
            return error(3, "No Service Plan found")

    def coupon_get(self, form_data):
        coupon = next((couponfull for couponfull in self.coupons if couponfull["coupon"]["coupon_code"] == form_data["coupon_code"]), None)
        if coupon is not None:
            return response(coupon)
        else:
            return error(1, "could not get coupon info for")

    @record(method='plan.list')
    def service_plan_list(self, form_data):
        if 'code' in form_data:
            plan_code = form_data['code']
            return response({plan['plan_id']: plan for plan in self.service_plans_list.values()
                             if plan['code'] == plan_code})
        return response(self.service_plans_list)

    @record(method='order.create')
    def create_order(self, form_data):
        order = self.order.get(form_data['order_queue_id'])
        if isinstance(order, FakeUbersmithError):
            return error(order.code, order.message)
        return response(order)

    @record(method='order.respond')
    def order_respond(self, form_data):
        return response(8)

    @record(method='order.submit')
    def submit_order(self, form_data):
        order_submit = self.order_submit.get(form_data['order_id'])
        if isinstance(order_submit, FakeUbersmithError):
            return error(order_submit.code, order_submit.message)
        return response(order_submit)

    @record(method='order.cancel')
    def cancel_order(self, form_data):
        order_cancel = self.order_cancel.get(form_data['order_id'])
        if isinstance(order_cancel, FakeUbersmithError):
            return error(order_cancel.code, order_cancel.message)
        return response(order_cancel)

    def client_get(self, form_data):
        client_id = form_data["client_id"]
        client = next((client for client in self.clients if client["clientid"] == client_id), None)
        if client is not None:
            return response(client)
        else:
            return error(1, "Client ID '%s' not found." % client_id)

    @record(method='client.cc_add')
    def client_cc_add(self, form_data):
        if isinstance(self.credit_card_response, FakeUbersmithError):
            return error(self.credit_card_response.code, self.credit_card_response.message)
        return response(self.credit_card_response)

    @record(method='client.cc_update')
    def client_cc_update(self, form_data):
        if isinstance(self.credit_card_response, FakeUbersmithError):
            return error(self.credit_card_response.code, self.credit_card_response.message)
        return response(True)

    def client_cc_info(self, form_data):
        # This call returns no error if proivided parameters, only empty list
        if "billing_info_id" in form_data:
            return response({
                                cc["billing_info_id"]: cc for cc in self.credit_cards
                                if cc["billing_info_id"] == form_data["billing_info_id"]
                                })

        elif "client_id" in form_data:
            return response({
                                cc["billing_info_id"]: cc for cc in self.credit_cards
                                if cc["clientid"] == form_data["client_id"]
                                })

        else:
            return error(1, "request failed: client_id parameter not supplied")

    @record(method='client.cc_delete')
    def client_cc_delete(self, form_data):
        if isinstance(self.credit_card_delete_response, FakeUbersmithError):
            return error(self.credit_card_delete_response.code, self.credit_card_delete_response.message)
        return response(True)


def error(code, message):
    r = json.dumps({
        "status": False,
        "error_code": code,
        "error_message": message,
        "data": None
    })
    return make_response((r, 200, {'Content-Type': 'application/json'}))


def response(data):
    r = json.dumps({
        "status": True,
        "error_code": None,
        "error_message": "",
        "data": data
    })
    return make_response((r, 200, {'Content-Type': 'application/json'}))


def run():
    server = FakeUbersmith()
    server.run()

if __name__ == '__main__':
    run()
