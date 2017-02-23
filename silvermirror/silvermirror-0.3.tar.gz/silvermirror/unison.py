"""
unison backend for silvermirror
"""

import pexpect
import subprocess
from interface import Reflector

class unison(Reflector):

    def sync(self, host, resource, ignore=(), password=None, test=False):
        command = ['unison', '-auto', '-batch', resource, 'ssh://%s/%s' % (host, resource)]
        for i in ignore:
            command.extend(('-ignore', "'Name %s'" % i))

        command = ' '.join(command)
        print command # XXX debug -- should go to logging
        if not test:
            if password:
                child = pexpect.spawn(command, timeout=36000, maxread=1)
                child.expect('password: ')
                child.sendline(password)
                print child.read() # XXX -> logging
            else:
                # XXX should not use shell=True
                subprocess.call(command, shell=True)
