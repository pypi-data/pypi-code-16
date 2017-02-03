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


def _manip_path(arrange_parts, pathvar, vals, sep=':'):
    new = sep.join(vals)
    old = os.environ.get(pathvar)
    if old:
        new = sep.join(arrange_parts(old, new))
    os.environ[pathvar] = new


def _prepend_order(old, new):
    return new, old


def _append_order(old, new):
    return old, new


def prepend_path(pathvar, vals, sep=':'):
    """Take a list of e.g. PATH entries and prepend them to $PATH.

    >>> os.environ['PYTHONPATH'] = '/usr/bin'
    >>> prepend_path('PYTHONPATH', ['/usr/local/bin'])
    >>> os.environ['PYTHONPATH']
    '/usr/local/bin:/usr/bin'
    """
    return _manip_path(_prepend_order, pathvar, vals, sep)


def append_path(pathvar, vals, sep=':'):
    """Take a list of strs and append them to an env var (e.g. $PATH).

    >>> os.environ['PYTHONPATH'] = '/usr/bin'
    >>> append_path('PYTHONPATH', ['/usr/local/bin'])
    >>> os.environ['PYTHONPATH']
    '/usr/bin:/usr/local/bin'
    """
    return _manip_path(_append_order, pathvar, vals, sep)
