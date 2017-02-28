# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

import json

from tcell_agent.appsensor import params
from tcell_agent.config import CONFIGURATION
from tcell_agent.sanitize.sanitize_utils import ensure_str_or_unicode


class AppSensorMeta(object):
    def __init__(self):
        self.encoding = 'utf-8'

        self.remote_address = None
        self.raw_remote_address = None
        self.method = None
        self.location = None
        self.route_id = None
        self.session_id = None
        self.user_id = None

        self.get_dict = None
        self.post_dict = None
        self.cookie_dict = None
        self.files_dict = None
        self.json_body_str = None
        self.request_content_bytes_len = 0
        self.user_agent_str = None

        self.path_dict = {}

        self.response_content_bytes_len = 0
        self.response_code = 200

        self.request_processed = False
        self.response_processed = False

    def set_raw_remote_address(self, raw_remote_address):
        self.raw_remote_address = raw_remote_address
        self.remote_address = raw_remote_address
        if CONFIGURATION.hipaa_safe_mode:
            self.remote_address = "hmac:{ip}".format(ip=raw_remote_address)

    def path_parameters_data(self, path_dict):
        self.path_dict = path_dict or {}

    def set_request(self, request):
        if self.request_processed:
            return
        self.request_processed = True

        request_len = 0

        try:
            request_len = int(request.META.get("CONTENT_LENGTH", 0))
        except:
            pass

        post_dict = {}
        request_json_body = None

        try:
            if request_len is not None and request_len > 0:
                post_dict = request.POST
                content_type = request.META.get("CONTENT_TYPE", "")
                if content_type.startswith("multipart/form-data") == False:
                    # Can't just say post as it may be PUT or maybe something else
                    # We're going to make sure some crazy client didn't submit json by mistake
                    request_body = request.body
                    if request_len < 2000000 and len(request_body) < 2000000:
                        if content_type.startswith("application/json"):
                            request_json_body = request_body
                        else:
                            request_body = ensure_str_or_unicode(self.encoding, request_body)
                            if request_body[0] == '{' or request_body[0] == '[':
                                try:
                                    json.loads(request_body)
                                    post_dict = {}
                                    request_json_body = request_body
                                except ValueError:
                                    pass
        except:
            pass

        self.get_dict = request.GET
        self.cookie_dict = request.COOKIES
        self.json_body_str = request_json_body
        self.request_content_bytes_len = request_len

        filenames_dict = {}
        for param_name in (request.FILES or {}).keys():
            filenames_dict[param_name] = []
            for file_obj in request.FILES.getlist(param_name):
                filenames_dict[param_name].append(file_obj.name)

        self.files_dict = params.flatten_clean(self.encoding, filenames_dict)
        self.post_dict = params.flatten_clean(self.encoding, post_dict)

    def set_response(self, django_response_class, response):
        if self.response_processed:
            return
        self.response_processed = True

        response_content_len = 0
        try:
            if isinstance(response, django_response_class):
                response_content_len = len(response.content)
        except:
            pass

        self.response_content_bytes_len = response_content_len
        self.response_code = response.status_code

    def __str__(self):
        s = "<{}"
        s = s + " remote_address: {}"
        s = s + " method: {}"
        s = s + " location: {}"
        s = s + " route_id: {}"
        s = s + " session_id: {}"
        s = s + " user_id: {}"
        s = s + " get_dict: {}"
        s = s + " post_dict: {}"
        s = s + " cookie_dict: {}"
        s = s + " files_dict: {}"
        s = s + " json_body_str: {}"
        s = s + " request_content_bytes_len: {}"
        s = s + " user_agent_str: {}"
        s = s + " path_dict: {}"
        s = s + " response_content_bytes_len: {}"
        s = s + " response_code: {}"
        s = s + " request_processed: {}"
        s = s + " response_processed: {}>"

        return s.format(
            type(self).__name__,
            self.remote_address,
            self.method,
            self.location,
            self.route_id,
            self.session_id,
            self.user_id,
            self.get_dict,
            self.post_dict,
            self.cookie_dict,
            self.files_dict,
            self.json_body_str,
            self.request_content_bytes_len,
            self.user_agent_str,
            self.path_dict,
            self.response_content_bytes_len,
            self.response_code,
            self.request_processed,
            self.response_processed,
        )
