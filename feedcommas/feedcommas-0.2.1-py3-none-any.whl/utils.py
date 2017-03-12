# Copyright (C) 2017 Michał Góral.
#
# This file is part of Feed Commas
#
# Feed Commas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Feed Commas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Feed Commas. If not, see <http://www.gnu.org/licenses/>.

'''Utility functions'''

import os
import sys
import errno
from subprocess import Popen, PIPE


def eprint(*args, **kwargs):
    '''Print to stderr.'''
    print(*args, file=sys.stderr, **kwargs)


def get_password_cmd(cmd, err_cb=None):
    '''Returns an output of password-cmd. If command returned failure (non-zero
    status, calls err_cb with a collected stderr.'''
    enc = sys.stdout.encoding
    proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()

    out = out.decode(enc).rstrip('\r\n')
    err = err.decode(enc).rstrip('\r\n')

    if proc.returncode != 0:
        if err_cb:
            err_cb('%s: %s' % (proc.returncode, err))
            return None
    return out


def mkdir_p(path):
    '''Works like `mkdir -p`: creates all (not yet existing) directories in a
    given path.'''
    if not path:
        return

    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
