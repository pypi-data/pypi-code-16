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
"""Global settings for GMN

This file contains settings that are specific to an instance of GMN.
"""

from __future__ import absolute_import

# D1
import d1_common.util

DEBUG = True
DEBUG_GMN = True
DEBUG_PYCHARM = False

PYCHARM_BIN = '~/bin/JetBrains/pycharm'
ECHO_REQUEST_OBJECT = False
ALLOW_INTEGRATION_TESTS = True
STAND_ALONE = True # ################
TRUST_CLIENT_SUBMITTER = False
TRUST_CLIENT_ORIGINMEMBERNODE = False
TRUST_CLIENT_AUTHORITATIVEMEMBERNODE = False
TRUST_CLIENT_DATESYSMETADATAMODIFIED = False
TRUST_CLIENT_SERIALVERSION = False
TRUST_CLIENT_DATEUPLOADED = False
MONITOR = True

NODE_IDENTIFIER = 'urn:node:mnDevGMN'
NODE_NAME = 'GMN Dev'
NODE_DESCRIPTION = u'Test Member Node operated by DataONE'
NODE_BASEURL = 'https://localhost/mn'
NODE_SYNCHRONIZE = True
NODE_SYNC_SCHEDULE_YEAR = '*'
NODE_SYNC_SCHEDULE_MONTH = '*'
NODE_SYNC_SCHEDULE_WEEKDAY = '?'
NODE_SYNC_SCHEDULE_MONTHDAY = '*'
NODE_SYNC_SCHEDULE_HOUR = '*'
NODE_SYNC_SCHEDULE_MINUTE = '0/3'
NODE_SYNC_SCHEDULE_SECOND = '0'
NODE_REPLICATE = True

REPLICATION_MAXOBJECTSIZE = -1
REPLICATION_SPACEALLOCATED = 10 * 1024**4
REPLICATION_ALLOWEDNODE = ()
REPLICATION_ALLOWEDOBJECTFORMAT = ()
REPLICATION_MAX_ATTEMPTS = 1 # ############################################### 1 for reptest 24

SYSMETA_REFRESH_MAX_ATTEMPTS = 2

NODE_SUBJECT = 'CN=urn:node:mnDevGMN,DC=dataone,DC=org'
NODE_CONTACT_SUBJECT = 'CN=MyName,O=Google,C=US,DC=cilogon,DC=org'
NODE_STATE = 'up'

SECRET_KEY = '7782523t8ygwhoiughgeoghw289575y89'
CLIENT_CERT_PATH = d1_common.util.abs_path('./certificates/server.crt')
CLIENT_CERT_PRIVATE_KEY_PATH = d1_common.util.abs_path(
  './certificates/server.nopassword.key'
)

if DEBUG or DEBUG_GMN:
  LOG_LEVEL = 'DEBUG'
else:
  LOG_LEVEL = 'WARNING'

DATAONE_ROOT = 'http://localhost:8181'

DATAONE_TRUSTED_SUBJECTS = {
  'gmn_test_subject_trusted',
  #'public', #####################################
}

ADMINS = (('Roger Dahl', 'dahl@unm.edu'),)
PUBLIC_OBJECT_LIST = True
PUBLIC_LOG_RECORDS = True
REQUIRE_WHITELIST_FOR_UPDATE = False

DATABASES = {
  'default': {
    # Postgres
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'dahl',
    'USER': 'dahl',
    'PASSWORD': 'dahl', # Not used in the default Peer authentication
    'HOST': '', # Set to empty string for localhost.
    'PORT': '', # Set to empty string for default.
    # Do not change ATOMIC_REQUESTS from "True", as implicit transactions form
    # the basis of concurrency control in GMN.
    'ATOMIC_REQUESTS': True,
  }
}

OBJECT_STORE_PATH = d1_common.util.abs_path('./object_store')

PROXY_MODE_BASIC_AUTH_ENABLED = True
PROXY_MODE_BASIC_AUTH_USERNAME = ''
PROXY_MODE_BASIC_AUTH_PASSWORD = ''
PROXY_MODE_STREAM_TIMEOUT = 10

# Path to the log file.
LOG_PATH = d1_common.util.abs_path('./gmn.log')

# Set up logging.
LOGGING = {
  'version': 1,
  'disable_existing_loggers': True,
  'formatters': {
    'verbose': {
      'format':
        '%(asctime)s %(levelname)-8s %(name)s %(module)s '
        '%(process)d %(thread)d %(message)s',
      'datefmt': '%Y-%m-%d %H:%M:%S'
    },
    'simple': {
      'format': '%(levelname)s %(message)s'
    },
  },
  'handlers': {
    'file': {
      'level': 'DEBUG',
      'class': 'logging.FileHandler',
      'filename': LOG_PATH,
      'formatter': 'verbose'
    },
    'null': {
      'level': 'DEBUG',
      'class': 'logging.NullHandler',
    },
  },
  'loggers': {
    # The "catch all" logger is denoted by ''.
    '': {
      'handlers': ['file'],
      'propagate': True,
      'level': 'DEBUG',
    },
    # Django uses this logger.
    'django': {
      'handlers': ['file'],
      'propagate': False,
      'level': 'DEBUG', # LOG_LEVEL,
    },
    # Messages relating to the interaction of code with the database. For
    # example, every SQL statement executed by a request is logged at the DEBUG
    # level to this logger.
    'django.db.backends': {
      'handlers': ['null'],
      # Set logging level to "WARNING" to suppress logging of SQL statements.
      'level': 'WARNING',
      'propagate': False
    },
  }
}
