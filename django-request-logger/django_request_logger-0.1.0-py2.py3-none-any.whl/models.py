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

from django.db import models
from django.conf import settings


class UserRequest(models.Model):
  user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    null=True,
  )
  timestamp = models.DateTimeField(auto_now_add=True)
  path = models.CharField(max_length=2047)
  method = models.CharField(max_length=255)
  scheme = models.CharField(max_length=255)
  body = models.TextField()
  content_length = models.CharField(max_length=255)
  content_type = models.CharField(max_length=255)
  http_accept = models.CharField(max_length=255)
  http_accept_encoding = models.CharField(max_length=255)
  http_accept_language = models.CharField(max_length=255)
  http_host = models.CharField(max_length=255)
  http_referer = models.CharField(max_length=2047)
  http_user_agent = models.CharField(max_length=255)
  remote_addr = models.CharField(max_length=255)
  remote_host = models.CharField(max_length=255)
  remote_user = models.CharField(max_length=255)
  server_name = models.CharField(max_length=255)
  server_port = models.CharField(max_length=255)
  post_data = models.TextField()
  get_data = models.TextField()
  cookies = models.TextField()
  encoding = models.CharField(max_length=255)
  is_ajax = models.BooleanField()


  # class UserRequest


