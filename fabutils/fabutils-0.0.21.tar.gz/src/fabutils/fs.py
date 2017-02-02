# -*- coding: utf-8 -*-
"""
File system related helpers.
"""
from __future__ import absolute_import

from os import makedirs, remove
from os.path import dirname, exists, isdir
from shutil import rmtree

from fabric.api import local, quiet

from .util import infomsg


def write_file(path, text):
    """ Write **text** to a file pointed by **path**.

    This will ensure that the parent directories for the file exist. If
    not, they will be created.
    """
    parent = dirname(path)
    if not exists(parent):
        makedirs(parent)

    with open(path, 'w') as fp:
        fp.write(text)


def rm_glob(pattern):
    """ Remove all files matching the given glob *pattern*. """
    infomsg("Removing files matching {}", pattern)

    with quiet():
        cmd = ' '.join([
            'find . -name "{}"'.format(pattern),
            "| sed '/^\.\/env/d'",   # Remove entries starting with ./env
            "| sed '/^\.\/\.tox/d'"  # Remove entries starting with ./.tox
        ])
        matches = local(cmd, capture=True)

    for path in matches.splitlines():
        # might be a child of a dir deleted in an earlier iteration
        if not exists(path):
            continue

        if isdir(path):
            rmtree(path)
        else:
            remove(path)
