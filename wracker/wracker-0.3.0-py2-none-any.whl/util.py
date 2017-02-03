"""Tiny utilities too small for their own modules."""
from __future__ import (
    absolute_import, division, print_function, unicode_literals)

import contextlib
import os
import shutil
import tempfile


@contextlib.contextmanager
def temp_dir():
    """A context manager that provides a temporary directory.

    The directory is destroyed at the end of the context.
    """
    dir_path = tempfile.mkdtemp()
    try:
        yield dir_path
    finally:
        shutil.rmtree(dir_path)


def try_makedirs(path):
    """Try os.makedirs(), return True on success or False if it exists.

    Other issues raise exceptions.
    """
    try:
        os.makedirs(path)
    except OSError as err:
        if err.errno == 17:  # File already exists
            return False
        else:
            raise
    return True


def prepend_path(pathvar, vals, sep=':'):
    """Take a list of e.g. PATH entries and prepend them to $PATH.

    >>> os.environ['PYTHONPATH'] = '/usr/bin'
    >>> prepend_path('PYTHONPATH', ['/usr/local/bin'])
    >>> os.environ['PYTHONPATH']
    '/usr/local/bin:/usr/bin'
    """
    prefix = sep.join(vals)
    postfix = os.environ.get(pathvar)
    if postfix:
        new_val = prefix + sep + postfix
    else:
        new_val = prefix
    os.environ[pathvar] = new_val
