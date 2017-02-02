# -*- coding: utf-8 -*-
"""
You can import all fabutils functions from here. If you just want stuff from
one module it might be easier to import it directly, ie:

.. code-block:: python

    from fabutils.fs import rm_glob

But if you import from more than one module, it might be easier to import from
here:

.. code-block:: python

    from fabutils.api import rm_glob, get_staged_files

    # instead of

    from fabutils.fs import rm_glob
    from fabutils.git import get_staged_files
"""
from __future__ import absolute_import
from .fs import rm_glob, write_file
from .git import get_changed_files, get_staged_files
from .lint import lint_files
from .util import errmsg, infomsg, sysmsg
from .versioning import bump_version, bump_version_file


__all__ = [
    'bump_version',
    'bump_version_file',
    'get_changed_files',
    'get_staged_files',
    'lint_files',
    'rm_glob',
    'write_file',

    # Helpers for status messages
    'sysmsg',
    'infomsg',
    'errmsg',
]
