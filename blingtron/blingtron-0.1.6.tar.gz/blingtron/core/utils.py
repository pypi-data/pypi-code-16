# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import subprocess

from .io import info, err


def _format_subprocess_command(command):
    return ' '.join(command) if isinstance(command, list) else command


def try_subprocess_call_and_return(command, environ=None):
    """Run `command` in a child process, capturing all stdout before returning."""
    try:
        env = os.environ.copy()
        env.update(environ or {})

        command = _format_subprocess_command(command)
        p = subprocess.Popen(
            command, stdout=subprocess.PIPE, env=env, shell=True
        )
        out, error = p.communicate()

        if p.returncode != 0:
            return False, error
        return True, out.strip('\n')
    except (OSError, subprocess.CalledProcessError) as e:
        return False, e


def try_subprocess_call(command, environ=None):
    """Run `command` in a child process."""
    info('executing cmd: %s' % command)
    try:
        env = os.environ.copy()
        env.update(environ or {})

        command = _format_subprocess_command(command)
        subprocess.check_call([command], env=env, shell=True)
        return True
    except (OSError, subprocess.CalledProcessError) as e:
        err('(subprocess) %s' % e)
        return False


def print_environ(environ):
    info('\n'.join(sorted(['%s=%s' % (k, v) for k, v in environ.iteritems()])))
