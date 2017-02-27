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

import logging
import hashlib
import os
import os.path
import yaml
import shutil
import socket
from urllib2 import urlopen
from datetime import datetime
from pkg_resources import get_distribution, DistributionNotFound

logger = logging.getLogger(__name__)


def rm_data(datapath):
    logger.debug('Removing %s contents.', datapath)
    [shutil.rmtree(os.path.abspath(os.path.join(datapath, i)),
                   ignore_errors=True)
        for i  in os.listdir(datapath) if not i.startswith('.')]
    logger.debug('Content of %s after rm.', os.listdir(datapath))


def generate_hash(text):
    sha = hashlib.sha256(text).hexdigest()
    logger.debug(sha)
    return sha


def obtain_script_version():
    try:
        _dist = get_distribution('afaq-dl')
    except DistributionNotFound:
        __version__ = 'Please install this project with setup.py'
    else:
        __version__ = _dist.version
    logger.debug(__version__)


def obtain_script_commit_hash(script_path):
    from git import Repo, GitCmdObjectDB
    # FIXME: ROOT_PATH
    script_repo = Repo(script_path, odbt=GitCmdObjectDB)
    try:
        commit_hash = script_repo.head.commit.hexsha
    except ValueError as e:
        logger.error('Unable to obtain last commit'
                     ', maybe the repo was just created: %s', e)
    logger.debug(commit_hash)
    return commit_hash


def obtain_os():
    kernel_version = ' '.join(os.uname())
    logger.debug(kernel_version)
    return kernel_version


def obtain_home():
    home = os.path.expanduser('~')
    logger.debug('home %s' % home)
    return home


def obtain_environ():
    logger.debug('os.environ %s' % os.environ)
    return os.environ


def ls(dir_path):
    ls = os.listdir(dir_path)
    logger.debug('ls %s' % ls)
    return ls


def generate_host_identifier():
    hostid = generate_hash(obtain_os())
    logger.debug(hostid)
    return hostid


def obtain_ip():
    ip = socket.gethostbyname(socket.gethostname())
    logger.debug('ip %s' % ip)
    return ip


def obtain_public_ip():
    my_ip = urlopen('http://ip.42.pl/raw').read()
    logger.debug('public ip %s' % my_ip)
    return str(my_ip)


def now():
    now = datetime.now()
    logger.debug(now)
    return now


def ismorpio():
    if os.environ['HOME'] == '/app':
        logger.debug('running in morph.io')
        return True
    logger.debug('not running in morph.io')
    return False


def hasproxy():
    # FIXME: http proxy might not change the public address,
    # assuming it does for now
    if os.environ.get('HTTP_PROXY'):
        logger.debug('there is an HTTP_PROXY')
        return True
    logger.debug('there is not an HTTP_PROXY')
    return False


def write_metadata_file(metadata_path, local_repo_path):
    metadata = generate_metadata(local_repo_path)
    metadata_yaml = generate_yaml(metadata)
    with open(metadata_path, 'w') as f:
        f.write(metadata_yaml)
        logger.debug('wroten %s with %s' % (metadata_path, metadata_yaml))


def generate_metadata(local_repo_path):
    # ADVICE: system information is sensitive
    # in morph.io or running with tor, the ip will change all the time
    # FIXME: in morph.io cant obtain the current git revision this way
    # in morph.io host name will change all the time
    # an env variable that doesnt change is HOME=/app
    if ismorpio():
        ip = obtain_public_ip()
        os.uname = obtain_os()
        commit_revision = None
        host = 'morph.io'
    elif hasproxy():
        ip = obtain_public_ip()
        os.uname = generate_hash(obtain_os())
        commit_revision = obtain_script_commit_hash(local_repo_path)
        host = 'local'
    else:
        ip = generate_hash(obtain_public_ip())
        os.uname = generate_hash(obtain_os())
        commit_revision = obtain_script_commit_hash(local_repo_path)
        host = 'dev server'
    metadata = {
        'timestamp': str(now()),
        'ip': ip,
        'os.uname': os.uname,
        'commit_revision': commit_revision,
        'host': host
    }
    logger.debug(metadata)
    return metadata


def generate_yaml(dict_data):
    data_yaml = yaml.safe_dump(dict_data)
    logger.debug(data_yaml)
    return data_yaml
