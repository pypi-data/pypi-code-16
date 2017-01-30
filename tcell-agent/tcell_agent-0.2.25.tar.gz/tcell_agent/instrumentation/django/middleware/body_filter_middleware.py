# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved
import re

from django.http import HttpResponse

from tcell_agent.agent import TCellAgent, PolicyTypes
from tcell_agent.config import CONFIGURATION
from tcell_agent.instrumentation import safe_wrap_function


class BodyFilterMiddleware(object):

    def add_tag(self, request, response):
        if isinstance(response, HttpResponse) and response.has_header("Content-Type"):
            if response["Content-Type"] and response["Content-Type"].startswith("text/html"):
                response_type = type(response.content)
                tag_policy = TCellAgent.get_policy(PolicyTypes.CSP)
                if tag_policy and tag_policy.js_agent_api_key:
                    if CONFIGURATION.js_agent_api_base_url:
                        replace = "<head><script src=\"" + CONFIGURATION.js_agent_url + "\" tcellappid=\"" + CONFIGURATION.app_id + "\" tcellapikey=\"" + tag_policy.js_agent_api_key + "\" tcellbaseurl=\""+ CONFIGURATION.js_agent_api_base_url +"\"></script>"
                    else:
                        replace = "<head><script src=\"" + CONFIGURATION.js_agent_url + "\" tcellappid=\"" + CONFIGURATION.app_id + "\" tcellapikey=\"" + tag_policy.js_agent_api_key + "\"></script>"

                    if isinstance(response.content, str) is False:
                        replace = replace.encode("utf-8")

                    try:
                        if response_type == str:
                            response.content = re.sub(b"<head>", replace, response.content.decode('utf8'))

                        else:
                            response.content = re.sub(b"<head>", replace, response.content)
                    except UnicodeDecodeError:
                        pass


    def process_request(self, request):
        pass

    def process_response(self, request, response):
        safe_wrap_function("Insert Body Tag", self.add_tag, request, response)
        return response
