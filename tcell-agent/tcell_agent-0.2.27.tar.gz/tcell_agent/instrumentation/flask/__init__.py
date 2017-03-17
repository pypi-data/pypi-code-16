# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

import logging
import sys
import threading

from future.utils import iteritems

from tcell_agent.agent import TCellAgent, PolicyTypes
from tcell_agent.appsensor.params import flatten_clean
from tcell_agent.appsensor.manager import app_sensor_manager
from tcell_agent.appsensor.meta import AppSensorMeta
from tcell_agent.instrumentation import safe_wrap_function
from tcell_agent.instrumentation.better_ip_address import better_ip_address

LOGGER = logging.getLogger('tcell_agent').getChild(__name__)


def create_meta(request):
    from tcell_agent.instrumentation.flask.routes import calculate_route_id
    appsensor_meta = AppSensorMeta()
    request._appsensor_meta = appsensor_meta
    appsensor_meta.set_raw_remote_address(better_ip_address(request.environ))
    appsensor_meta.method = request.environ.get("REQUEST_METHOD")
    appsensor_meta.user_agent_str = request.environ.get("HTTP_USER_AGENT")
    appsensor_meta.location = request.url
    if request.url_rule is not None:
        appsensor_meta.route_id = calculate_route_id(appsensor_meta.method, request.url_rule.rule)

    appsensor_meta.get_dict = request.args
    appsensor_meta.cookie_dict = request.cookies
    try:
        appsensor_meta.json_body_str = request.get_json() or {}
    except:
        appsensor_meta.json_body_str = None
    appsensor_meta.request_content_bytes_len = request.content_length or 0

    appsensor_meta.post_dict = flatten_clean(request.charset, request.form)
    appsensor_meta.path_dict = request.view_args

    files_dict = {}
    for param_name, file_obj in iteritems(request.files or {}):
        files_dict[param_name] = file_obj.filename

    appsensor_meta.files_dict = flatten_clean(request.charset, files_dict)

    request._appsensor_meta = appsensor_meta


def update_meta_with_response(appsensor_meta, response, response_code):
    appsensor_meta.response_code = response_code
    if response is not None:
        appsensor_meta.response_content_bytes_len = response.content_length or 0


def check_ip_blocking(request):
    request._ip_blocking_triggered = False
    patches_policy = TCellAgent.get_policy(PolicyTypes.PATCHES)
    if patches_policy:
        resp = patches_policy.check_ip_blocking(request._appsensor_meta)
        if resp:
            request._ip_blocking_triggered = True
            return '', resp

    return None


def run_appsensor_check(request, response, response_code):
    appsensor_policy = TCellAgent.get_policy(PolicyTypes.APPSENSOR)
    if appsensor_policy and not request._ip_blocking_triggered:
        appsensor_meta = request._appsensor_meta
        update_meta_with_response(appsensor_meta, response, response_code)
        app_sensor_manager.send_appsensor_data(appsensor_meta)


def set_csp_headers(result):
    csp_headers = TCellAgent.get_policy(PolicyTypes.CSP).headers()
    if csp_headers:
        for csp_header in csp_headers:
            result.headers[csp_header[0]] = csp_header[1]


def check_location_redirect(request, response):
    redirect_policy = TCellAgent.get_policy(PolicyTypes.HTTP_REDIRECT)

    if redirect_policy and response.location:
        from tcell_agent.instrumentation.flask.routes import calculate_route_id
        route_id = None
        if request.url_rule is not None:
            route_id = calculate_route_id(request.environ.get("REQUEST_METHOD", None), request.url_rule.rule)
        response.headers['location'] = redirect_policy.process_location(
            better_ip_address(request.environ),
            request.environ.get("REQUEST_METHOD", None),
            request.host,
            request.path,
            response.status_code,
            response.location,
            user_id=None,
            session_id=None,
            route_id=route_id)


def _instrument():
    from tcell_agent.instrumentation.flask.routes import instrument_routes
    instrument_routes()

    from flask.globals import _request_ctx_stack

    tcell_func = Flask.__init__

    def init(*args):
        TCellAgent.get_agent().ensure_polling_thread_running()
        return tcell_func(*args)

    Flask.__init__ = init

    tcell_preprocess_request = Flask.preprocess_request

    def preprocess_request(self):
        result = tcell_preprocess_request(self)

        safe_wrap_function("Create Context Info", create_meta, _request_ctx_stack.top.request)
        block_ip_response = safe_wrap_function(
            "Checking for block rules",
            check_ip_blocking,
            _request_ctx_stack.top.request)
        if block_ip_response:
            return block_ip_response

        return result

    Flask.preprocess_request = preprocess_request

    tcell_process_response = Flask.process_response

    def process_response(self, response):
        result = tcell_process_response(self, response)
        safe_wrap_function(
            "AppFirewall Request/Response",
            run_appsensor_check,
            _request_ctx_stack.top.request,
            response,
            response.status_code)
        safe_wrap_function("Set CSP Headers", set_csp_headers, result)
        safe_wrap_function(
            "Check Location Header",
            check_location_redirect,
            _request_ctx_stack.top.request,
            response)

        return result

    Flask.process_response = process_response

    tcell_handle_user_exception = Flask.handle_user_exception

    def handle_user_exception(self, e):
        try:
            return tcell_handle_user_exception(self, e)
        except Exception as e:
            safe_wrap_function("AppFirewall Request/Response", run_appsensor_check, _request_ctx_stack.top.request,
                               None, 500)

            from flask._compat import reraise
            exc_type, exc_value, tb = sys.exc_info()
            reraise(exc_type, exc_value, tb)

    Flask.handle_user_exception = handle_user_exception


try:
    from flask import Flask

    if TCellAgent.get_agent():
        _instrument()
except ImportError as ie:
    pass
except Exception as e:
    LOGGER.debug("Could not instrument flask: {e}".format(e=e))
    LOGGER.debug(e, exc_info=True)
