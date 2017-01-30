"""
tmpld.core.util
~~~~~~~~~~~~~~

Utility methods for tmpld.

:copyright: (c) 2016 by Joe Black.
:license: Apache2.
"""

import os
import pwd
import grp
import io
import subprocess

import lxml.etree


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
    doc = lxml.etree.parse(io.StringIO(xml))
    return doc.xpath(expression)
