#!/usr/bin/env python3

import logging
import re
import subprocess
from functools import wraps
from string import Template

from flask import abort, request

TOKENS = []
REGEX_USERNAME = re.compile('^\w{1,20}$')

logger = logging.getLogger(__name__)


def authorize_badtoken(f):
    @wraps(f)
    def check_token(*args, **kwargs):
        magic_header = request.environ.get('HTTP_BADTOKEN')
        if magic_header in TOKENS:
            return f(*args, **kwargs)
        else:
            return abort(403)
    return check_token


def sanitize_user():
    def decorator(f):
        @wraps(f)
        def check_user(*args, **kwargs):
            if REGEX_USERNAME.match(kwargs.get('user')):
                return f(*args, **kwargs)
            else:
                return abort(400)
        return check_user
    return decorator


class Command(object):
    def __init__(self, sysinit=None, service=None):
        self.sysinit = sysinit
        self.service = service
        self.cli = self.format_cli()

    def format_cli(self):
        if 'system' in self.sysinit:
            return Template('systemctl $action %s' % self.service)
        if 'init' in self.sysinit:
            return Template('/etc/init.d/%s $action' % self.service)
        return '/bin/false'

    def check(self):
        cmd = self.cli.substitute(action='status')
        try:
            subprocess.check_call(cmd.split(),
                                  stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL)
            return True
        except Exception as e:
            logger.debug(e)
            logger.debug('cannot interact with daemon "%s"' % cmd)
        return False

    def reload(self):
        cmd = self.cli.substitute(action='reload')
        try:
            subprocess.run(cmd.split(), check=True,
                           stdin=subprocess.DEVNULL,
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
            logger.info('daemon reloaded')
            return True
        except subprocess.CalledProcessError:
            logger.error('cannot interact with daemon "%s"' % cmd)
        return False
