# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

from tcell_agent.agent import TCellAgent, PolicyTypes
from tcell_agent.appsensor.manager import app_sensor_manager
from tcell_agent.instrumentation.django import _default_charset as DEFAULT_CHARSET


def django_meta(request):
    appsensor_meta = request._tcell_context.appsensor_meta
    appsensor_meta.set_raw_remote_address(request._tcell_context.raw_remote_addr)
    appsensor_meta.method = request.META.get("REQUEST_METHOD")
    appsensor_meta.user_agent_str = request.META.get("HTTP_USER_AGENT")
    appsensor_meta.location = request.build_absolute_uri()
    appsensor_meta.route_id = request._tcell_context.route_id
    appsensor_meta.session_id = request._tcell_context.session_id
    appsensor_meta.user_id = request._tcell_context.user_id
    appsensor_meta.encoding = request.encoding or DEFAULT_CHARSET

    return appsensor_meta


def django_request_response_appsensor(django_response_class, request, response):
    if request._tcell_context.ip_blocking_triggered:
        return

    appsensor_policy = TCellAgent.get_policy(PolicyTypes.APPSENSOR)
    if appsensor_policy is None:
        return

    meta = django_meta(request)
    meta.set_request(request)
    meta.set_response(django_response_class, response)

    app_sensor_manager.send_appsensor_data(meta)
