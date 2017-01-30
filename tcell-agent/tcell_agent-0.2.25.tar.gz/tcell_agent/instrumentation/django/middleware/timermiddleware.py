# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

import datetime
import logging

from tcell_agent.agent import TCellAgent
from tcell_agent.instrumentation import safe_wrap_function

LOGGER = logging.getLogger('tcell_agent').getChild(__name__)

class TimerMiddleware(object):

    def process_request(self, request):
        def start():
            request._tcell_context.start_time = datetime.datetime.now()#
        safe_wrap_function("Start Request Timer", start)

    def process_response(self, request, response):
        def stop():
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
        safe_wrap_function("Stop Request Timer", stop)
        return response
