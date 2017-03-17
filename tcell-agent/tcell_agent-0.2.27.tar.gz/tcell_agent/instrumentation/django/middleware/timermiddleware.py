# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

import datetime
import logging

from tcell_agent.agent import TCellAgent
from tcell_agent.instrumentation import safe_wrap_function


LOGGER = logging.getLogger('tcell_agent').getChild(__name__)


def end_timer(request):
    endtime = datetime.datetime.now()
    if request._tcell_context.start_time != 0:
        request_time = int((endtime - request._tcell_context.start_time).total_seconds() * 1000)
        TCellAgent.request_metric(
            request._tcell_context.route_id,
            request_time,
            request._tcell_context.remote_addr,
            request._tcell_context.user_agent,
            request._tcell_context.session_id,
            request._tcell_context.user_id
        )
        LOGGER.debug("request took {time}".format(time=request_time))


def start_timer(request):
    request._tcell_context.start_time = datetime.datetime.now()


class TimerMiddleware(object):

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)

        response = self.get_response(request)

        return self.process_response(request, response)

    def process_request(self, request):
        safe_wrap_function("Start Request Timer", start_timer, request)

    def process_response(self, request, response):
        safe_wrap_function("Stop Request Timer", end_timer, request)
        return response
