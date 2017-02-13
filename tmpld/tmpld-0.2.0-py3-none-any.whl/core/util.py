"""
tmpld.core.util
~~~~~~~~~~~~~~

Utility methods for tmpld.

:copyright: (c) 2016 by Joe Black.
:license: Apache2.
"""

import os
import sys
import pwd
import grp
import io
import subprocess


def get_ownership(file):
    return (
        pwd.getpwuid(os.stat(file).st_uid).pw_name,
        grp.getgrgid(os.stat(file).st_gid).gr_name
    )


def get_mode(file):
    return str(oct(os.lstat(file).st_mode)[4:])


def octalize(string):
    return int(str(string), 8)


def parse_user_group(owner):
    if len(owner.split(':')) == 2:
        user, group = owner.split(':')
    else:
        user, group = owner, None
    return user, group


def set_defaults(d, d2):
    d = d or {}
    d2 = d2 or {}
    for key, val in d2.items():
        d.setdefault(key, val)
    return d


def shell(command, return_code=False):
    code, output = subprocess.getstatusoutput(command)
    if return_code:
        return code == 0
    return output


def xpath(xml, expression):
    if not try_import('lxml.etree'):
        raise ImportError('you need to install lxml to use this feature')
    import lxml.etree
    doc = lxml.etree.parse(io.StringIO(xml))
    return doc.xpath(expression)


def jpath(string):
    if not try_import('jsonpath_rw'):
        raise ImportError('you need to install jsonpath_rw to use this feature')
    from jsonpath_rw import parse
    return parse(string)


def get_file(path, default=None, strip_comments=True, trim=True):
    contents = default or ''
    if os.path.exists(path):
        with open(path, 'rt') as fd:
            contents = fd.read()
        if strip_comments:
            contents = '\n'.join(
                [l for l in contents.split('\n') if not l.startswith('#')])
        if trim:
            contents = contents.strip()
    return contents


def get_dirs(files=None):
    files = files or []
    return [os.path.dirname(os.path.abspath(file_)) for file_ in files]


def try_import(name, alt=None):
    module_segments = name.split('.')
    last_error = None
    remainder = []

    while module_segments:
        module_name = '.'.join(module_segments)
        try:
            __import__(module_name)
        except ImportError:
            last_error = sys.exc_info()[1]
            remainder.append(module_segments.pop())
            continue
        else:
            break
    else:
        return alt
    module = sys.modules[module_name]
    nonexistent = object()
    for segment in reversed(remainder):
        module = getattr(module, segment, nonexistent)
        if module is nonexistent:
            return alt
    return module
