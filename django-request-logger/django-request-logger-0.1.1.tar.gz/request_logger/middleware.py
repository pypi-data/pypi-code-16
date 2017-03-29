#!/usr/bin/env python
# vi: et sw=2 fileencoding=utf-8

#============================================================================
# Request logger
# Copyright (c) 2017 Pispalan Insinööritoimisto Oy (http://www.pispalanit.fi)
#
# All rights reserved.
# Redistributions of files must retain the above copyright notice.
#
# @description [File description]
# @created     24.03.2017
# @author      Joni Saarinen <joni.saarinen@pispalanit.fi>
# @copyright   Copyright (c) Pispalan Insinööritoimisto Oy
# @license     All rights reserved
#============================================================================

from __future__ import unicode_literals

import json

from .models import UserRequest


class LoggerMiddleware(object):


  def process_request(self, request):
    UserRequest.objects.create(
      user=request.user if request.user.is_authenticated() else None,
      path=request.get_full_path(),
      method=request.method,
      scheme=request.scheme,
      body=request.body,
      content_length = request.META["CONTENT_LENGTH"],
      content_type = request.META["CONTENT_TYPE"],
      http_accept = request.META["HTTP_ACCEPT"],
      http_accept_encoding = request.META["HTTP_ACCEPT_ENCODING"],
      http_accept_language = request.META["HTTP_ACCEPT_LANGUAGE"],
      http_host = request.META["HTTP_HOST"],
      http_referer = request.META["HTTP_REFERER"] if "HTTP_REFERER" in request.META else "",
      http_user_agent = request.META["HTTP_USER_AGENT"],
      remote_addr = request.META["REMOTE_ADDR"],
      remote_host = request.META["REMOTE_HOST"],
      remote_user = request.META["REMOTE_USER"] if "REMOTE_USER" in request.META else "",
      server_name = request.META["SERVER_NAME"],
      server_port = request.META["SERVER_PORT"],
      post_data=json.dumps(request.POST),
      get_data=json.dumps(request.GET),
      cookies=json.dumps(request.COOKIES),
      encoding=request.encoding or "",
      is_ajax=request.is_ajax(),
    )
    # def process_request


  # class LoggerMiddleware


