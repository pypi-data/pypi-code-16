"""Simple, pure-Python implementation of the `which` utility."""
from __future__ import (
    absolute_import, division, print_function, unicode_literals)

import os


class ExecutableNotFound(Exception):
    pass


def which(program):
    if os.path.dirname(program):
        return os.path.abspath(program)
    for path in os.environ['PATH'].split(os.pathsep):
        target = os.path.join(path, program)
        if os.path.isfile(target) and os.access(target, os.X_OK):
            return target
    raise ExecutableNotFound()
