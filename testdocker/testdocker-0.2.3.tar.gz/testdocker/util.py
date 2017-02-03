"""
testdocker.util
~~~~~~~~~~~~~~

Generic functions for testing docker containers.

:copyright: (c) 2016 by Joe Black.
:license: Apache2.
"""


import re

def set_defaults(d, d2):
    d = d or {}
    d2 = d2 or {}
    for key, val in d2.items():
        d.setdefault(key, val)
    return d


def match(pattern, obj):
    if isinstance(obj, str):
        return bool(re.search(pattern, obj))
    elif isinstance(obj, list):
        pattern = re.compile(pattern)
        for line in obj:
            if pattern.search(line):
                return True
