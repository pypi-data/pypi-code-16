# -*- coding: utf-8 -*-

# Copyright 2016 juxor <ju@riseup.net>

# This file is part of afaq-dl.
#
# afaq-dl is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# afaq-dl is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with afaq-dl.  If not, see <http://www.gnu.org/licenses/>.

DEBUG = False
# spider
#######################################################################
URL = 'http://anarchism.pageabode.com/afaq/index.html'
DOMAIN = 'anarchism.pageabode.com'
XPATH_CONTENT = "//div[@class='node']/div[@class='content clear-block']"
XPATH_NEXT = '//link[@rel="next"]/@href'

# FS dirs
#######################################################################
DATA_LOCAL_REPO_DIR = 'afaq'
LOG_DIR = 'log'
HTML_DIR = 'html'

BIN_DIR = 'bin'
MD_DIR = 'markdown'
TXT_BS_DIR = 'txtbs'
HTML2TXT_SCRIPT = 'html2txt'

# repo
#######################################################################
DATA_REMOTE_REPO = {'name': 'origin',
                    'url': 'https://0xacab.org/ju/afaq',
                    'branch': 'master'}
# NOTE: only for DEBUG!
# DATA_REMOTE_REPO = {'name': 'local',
#                     'url': 'file://%s' % join(dirname(PR_PATH),
#                                               DATA_LOCAL_REPO_DIR),
#                     'branch': 'master'}
METADATA_FILE = 'metadata.yml'
GIT_AUTHOR_NAME = 'afaq scraper'
GIT_AUTHOR_EMAIL = 'ju@riseup.net'


# ssh
#######################################################################
SSH_DIR = 'ssh'
GIT_SSH_COMMAND_FILE = 'ssh_command.sh'
MORPH_SSH_PRIV_KEY_ENV = 'MORPH_SSH_PRIV_KEY'
MORPH_SSH_PUB_KEY_ENV = 'MORPH_SSH_PUB_KEY'
GITHUB_SSH_PUB_KEY = u'github.com ssh-rsa xxx'
GITLAB_SSH_PUB_KEY = u'SHA256:28ZOG/QSJ2JGifFFYrCfllWmhJGBo1GX1m19voRsEm8'
SSH_PUB_KEY = u'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCqFOCm4EDMCM9AXxTfRjeWETPd9NBe7JWS4OGXwsV7I7UvHRZOBcLRj7ehsjwdLTVuUd4aFha7h/+qTWMBWXhEg2CuDx89ZVt5TdyFLJo5ZYFwMRyOuQ939SnW4vxoUC+N9utlooE6tGfr8jLZ+Tam2np2LfK+fQ5GcS5c6puGwBJggUaF2cmqRUIKF4lBxx7r6xr+Ha+oviPmfGXetQHcxsC6rmqLW6t09D1txr5SlgKL7mR/V1DoOerAtL93W7zBaE1DA9Ezx+aIZSy3gktsdrdscqkVKEDTCvWVfzVJ/ecGASwRrNMLH4x1+7mNmv0nWigr8cKXy5lKSOSUn5AN'

# FS paths
#######################################################################
import logging
from datetime import datetime
import os
from os.path import dirname, join, abspath

NOW = datetime.utcnow().replace(microsecond=0).isoformat().replace(':', '-')

MODULE_PATH = dirname(abspath(__file__))
PR_PATH = dirname(MODULE_PATH)

LOG_LEVEL = logging.DEBUG if DEBUG is True else logging.INFO
LOG_FORMAT = '%(asctime)s [%(module)s] %(levelname)s: %(message)s'
LOG_FILENAME = NOW + '.log'
LOG_FULLPATH = join(PR_PATH, LOG_DIR, LOG_FILENAME)
LOG_FILENAME = LOG_FULLPATH

DATA_LOCAL_REPO_PATH = join(os.getcwd(), DATA_LOCAL_REPO_DIR)
HTML_PATH = join(DATA_LOCAL_REPO_PATH, HTML_DIR)

MD_PATH = join(DATA_LOCAL_REPO_PATH, MD_DIR)
METADATA_PATH = join(DATA_LOCAL_REPO_PATH, METADATA_FILE)
TXT_BS_PATH = join(DATA_LOCAL_REPO_PATH, TXT_BS_DIR)
HTML2TXT_COMMAND = join(PR_PATH, BIN_DIR, HTML2TXT_SCRIPT)

# ssh
SSH_PATH = join(os.getcwd(), SSH_DIR)
SSH_PRIV_KEY_PATH = join(SSH_PATH, 'id_rsa')
SSH_PUB_KEY_PATH = join(SSH_PATH, 'id_rsa.pub')
SSH_PUB_KEY_SERVER_PATH = join(SSH_PATH, 'ssh_pub_key_server')
GIT_SSH_COMMAND_PATH = join(SSH_PATH, GIT_SSH_COMMAND_FILE)

GIT_SSH_COMMAND = u'#!/bin/sh\nssh -i ' + SSH_PRIV_KEY_PATH + \
    ' -o "UserKnownHostsFile ' + SSH_PUB_KEY_SERVER_PATH + \
    '" "$@"\n'

GIT_SSH_COMMAND_MORPHIO = u'#!/bin/sh\nssh -i ' + SSH_PRIV_KEY_PATH + \
    ' -o "UserKnownHostsFile ' + SSH_PUB_KEY_SERVER_PATH + \
    '" -o "StrictHostKeyChecking no"' + \
    ' "$@"\n'

try:
    from config_local import *
except:
    pass
