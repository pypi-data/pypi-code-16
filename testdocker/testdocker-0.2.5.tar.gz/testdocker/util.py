"""
testdocker.util
~~~~~~~~~~~~~~

Generic functions for testing docker containers.

:copyright: (c) 2016 by Joe Black.
:license: Apache2.
"""


import re
import itertools


def format_flag(name):
    return '--{}'.format(name.replace('_', '-'))


def set_defaults(obj1, obj2):
    assert type(obj1) is type(obj2)
    obj_class = type(obj1)

    if isinstance(obj1, (tuple, list)):
        obj1 = filter_dupes(obj1 + obj2)
    elif isinstance(obj1, dict):
        for key, val in obj2.items():
            if isinstance(val, (list, tuple)):
                obj1[key] = list(val) + obj1.get(key, [])
            elif isinstance(val, dict):
                obj1.setdefault(key, val)
    return obj_class(obj1)


def filter_dupes(iterable, key=None):
    "List unique elements, preserving order. Remember all elements ever seen."
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in itertools.filterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element


def match(pattern, obj):
    if isinstance(obj, str):
        return bool(re.search(pattern, obj))
    elif isinstance(obj, list):
        pattern = re.compile(pattern)
        for line in obj:
            if pattern.search(line):
                return True


def select_one(iterable, where, equals):
    for item in iterable:
        if getattr(item, where, None) == equals:
            return item
            break


def filter_lines(lines, pattern):
    if isinstance(lines, str):
        lines = lines.split('\n')
    regex = re.compile(pattern)
    lines = [line for line in lines if not regex.match(line)]
    return '\n'.join(lines)
