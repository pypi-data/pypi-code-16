"""A module that handles installing entrypoints for a distribution."""
from __future__ import (
    absolute_import, division, print_function, unicode_literals)

import logging
import os
import stat

import wracker
from .util import try_makedirs
from .which import which


LOGGER = logging.getLogger(__name__)


# Super hack to have a "variable" shebang...
# TEMPLATE is both valid Python and valid sh.  All the sh script does is choose
# the right Python and then execute itself as Python instead of as shell.
#
# Thanks to http://unix.stackexchange.com/a/20895
TEMPLATE = """\
#!/bin/sh
if "true" : '''\'
then

    if [ -n "$WRACKER_PYTHON" ]
    then exec "$WRACKER_PYTHON" "$0" "$@"
    else exec /usr/bin/env python "$0" "$@"
    fi

exit 1  # shouldn't get here
fi
'''

# -*- coding: utf-8 -*-
import re
import sys

from {package} import {entry_func}

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit({entry_func}())
"""


PYTHON_PATH = None


def bin_path_for(platform, requirement):
    return os.path.join(wracker.local_path_for(platform, requirement), 'bin')


def install_for(platform, dist):
    """Install all entrypoints for the given dist."""
    global PYTHON_PATH
    if PYTHON_PATH is None:
        PYTHON_PATH = which(wracker.PYTHON)

    req = dist.as_requirement()
    python_bin = which(wracker.PYTHON)
    bin_path = bin_path_for(platform, req)
    try_makedirs(bin_path)  # Don't care if it already exists.

    for category, entrypoints in dist.get_entry_map().items():
        if category != 'console_scripts':
            LOGGER.warning('NotImplemented: entrypoint type %s for %s',
                           category, req)
            continue

        # name is a string, info is a pkg_resources.EntryPoint
        for name, info in entrypoints.items():
            if len(info.attrs) != 1:
                raise NotImplementedError(
                    "Multiple entrypoint attrs for %s" % req)
            params = {
                'python': python_bin,
                'package': info.module_name,
                'entry_func': info.attrs[0],
            }
            target = os.path.join(bin_path, name)
            with open(target, 'w') as executable:
                executable.write(TEMPLATE.format(**params))
            executable_for_all = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH

            # Basically chmod +x
            os.chmod(target, os.stat(target).st_mode | executable_for_all)
