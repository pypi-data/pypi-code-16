#!/usr/bin/env python3

import logging
import os
import re
import subprocess
import sys
import tempfile
from shutil import move

logger = logging.getLogger(__name__)


def reload_daemon():
    try:
        subprocess.check_call(['systemctl', 'status', 'sshd'],
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
        try:
            subprocess.run(['systemctl', 'reload', 'sshd'], check=True,
                           stdin=subprocess.DEVNULL,
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
            logger.info('daemon reloaded')
            return True
        except subprocess.CalledProcessError:
            logger.error('cannot reload daemon')
            return False
    except subprocess.CalledProcessError:
        logger.error('systemctl support for sshd not found')
        logger.info('to be implemented...')
        return False


class SSHConfig(object):
    def __init__(self, file):

        self.users = []
        self.restricted_users = False
        self.regex_users = re.compile('^AllowUsers (\w+ ?)*$')

        try:
            self.filename = os.path.abspath(file)
            logger.info('using ssh config file : %s' % self.filename)
            with open(self.filename, 'r+'):
                pass
        except PermissionError:
            logger.error('cant open file for modifications, exiting..')
            sys.exit(1)
        except FileNotFoundError:
            logger.error('cant find file, exiting..')
            sys.exit(1)

        with open(self.filename, 'r') as f:
            for line in f:
                if self.regex_users.match(line):
                    self.users = line.split()
                    self.users.remove('AllowUsers')
                    self.restricted_users = True

        logger.info('users: %s' % self.users)

    def add_user(self, user):
        if user not in self.users:
            logger.info('adding user %s' % user)
            self.users.append(user)
            return self.commit()
        return False

    def del_user(self, user):
        if user in self.users:
            logger.info('removing user %s' % user)
            self.users.remove(user)
            return self.commit()
        return False

    def commit(self):
        new_config, new_config_name = tempfile.mkstemp(dir=os.getcwd())
        with open(new_config, 'w') as new:
            with open(self.filename, 'r') as old:
                for line in old:
                    if self.regex_users.match(line):
                        new.write('AllowUsers {users}'.format(
                            users=' '.join(self.users)))
                    else:
                        new.write(line)
                if not self.restricted_users:
                    new.write('AllowUsers {users}'.format(
                        users=' '.join(self.users)))
                    self.restricted_users = True
        try:
            move(new_config_name, self.filename)
        except Exception:
            logger.error('cant write new sshd_config file')
            return False
        return True
