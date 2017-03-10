# -*- coding: utf-8 -*-

# This work was created by participants in the DataONE project, and is
# jointly copyrighted by participating institutions in DataONE. For
# more information on DataONE, see our web site at http://dataone.org.
#
#   Copyright 2009-2016 DataONE
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Startup configuration and checks
"""

from __future__ import absolute_import

# Django
import django.apps
import django.conf

# App
import app.util


class GMNStartupChecks(django.apps.AppConfig):
  name = u'GMN'
  verbose_name = u'DataONE Generic Member Node'

  def ready(self):
    self._check_cert_file(django.conf.settings.CLIENT_CERT_PATH)
    self._check_cert_file(django.conf.settings.CLIENT_CERT_PRIVATE_KEY_PATH)
    self._check_secret_key()

  def _check_cert_file(self, cert_path):
    if cert_path is None:
      return
    try:
      app.util.assert_readable_file(cert_path)
    except ValueError as e:
      raise ValueError(u'Invalid certificate: {}'.format(e.message))

  def _check_secret_key(self):
    if django.conf.settings.SECRET_KEY not in (u'MySecretKey', None):
      raise ValueError(u'SECRET_KEY is unset. See install documentation.')
