# -*- coding: utf-8 -*-
"""
Functionality related to versioning. This makes project version management
much easier.
"""
from __future__ import absolute_import
import re
from os.path import exists


# MAJOR.MINOR[.PATCH[-BUILD]]
RE_VERSION = re.compile(
    r'^'
    r'(?P<major>\d+)\.'
    r'(?P<minor>\d+)'
    r'(\.(?P<patch>\d+))?'
    r'$'
)


def bump_version(version, component='patch'):
    """ Bump the given version component.

    :param str version:
        The current version. The format is: MAJOR.MINOR[.PATCH].
    :param str component:
        What part of the version should be bumped. Can be one of:

        - major
        - minor
        - patch

    :return str:
        Bumped version as a string.
    """

    if component not in ('major', 'minor', 'patch'):
        raise ValueError("Invalid version component: {}".format(component))

    m = RE_VERSION.match(version)
    if m is None:
        raise ValueError("Version must be in MAJOR.MINOR[.PATCH] format")

    major = m.group('major')
    minor = m.group('minor')
    patch = m.group('patch') or None

    if patch == '0':
        patch = None

    if component == 'major':
        major = str(int(major) + 1)
        minor = '0'
        patch = None

    elif component == 'minor':
        minor = str(int(minor) + 1)
        patch = None

    else:
        patch = patch or 0
        patch = str(int(patch) + 1)

    new_ver = '{}.{}'.format(major, minor)
    if patch is not None:
        new_ver += '.' + patch

    return new_ver


def bump_version_file(version_file, component='patch'):
    """ Bump version stored in a file.

    :param str version_file:
        Path to the file storing the current version.
    :param str component:
        Version component to bump. Same as in `bump_version`.
    """
    if not exists(version_file):
        raise ValueError("VERSION file for does not exist")

    with open(version_file) as fp:
        old_ver = fp.read().strip()

    new_ver = bump_version(old_ver, component)

    with open(version_file, 'w') as fp:
        fp.write(new_ver)

    return old_ver, new_ver
