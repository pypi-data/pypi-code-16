#!/usr/bin/env python3

import logging
import os
import re
import sys
import tempfile
from shutil import move

from api2sshallowedusers.helpers import Command

logger = logging.getLogger(__name__)


def find_daemon():
    if Command('systemd', 'sshd').check():
        return Command('systemd', 'sshd')
    elif Command('init', 'ssh').check():
        return Command('init', 'ssh')
    elif Command('init', 'sshd').check():
        return Command('init', 'sshd')
    else:
        logger.error('is sshd running ? (i can only reload)')
        logger.error('exiting..')
        sys.exit(1)


class SSHConfig(object):
    def __init__(self, file):

        self.sshd = find_daemon()
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
                    new.write('AllowUsers {users}\n'.format(
                        users=' '.join(self.users)))
                    self.restricted_users = True
        try:
            move(new_config_name, self.filename)
        except Exception:
            logger.error('cant write new sshd_config file')
            return False
        return True
