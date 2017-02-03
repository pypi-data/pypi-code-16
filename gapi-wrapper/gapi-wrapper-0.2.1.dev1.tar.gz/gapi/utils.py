# -*- coding: utf-8 -*-
from itertools import izip_longest

from suds.sudsobject import asdict
from suds.sax.text import Text as SudsText

__all__ = ['to_list']


class Bunch(dict):
    def __getattr__(self, k):
        try:
            return self.__getitem__(k)
        except KeyError:
            raise AttributeError(k)
    __setattr__ = dict.__setitem__

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__ = state


def to_list(value, default=None):
    if value is None:
        return default if default else []
    if isinstance(value, basestring):
        return value.split(',')
    if isinstance(value, (list, tuple, set)):
        return map(str, value)
    return [str(value), ]


def suds_to_dict(data):
    """Convert Awdords API Suds object into serializable format."""
    if isinstance(data, list):
        return [suds_to_dict(x) for x in data]
    result = Bunch()
    for k, v in (asdict(data) if not isinstance(data, dict) else data).iteritems():
        if hasattr(v, '__keylist__'):
            result[k] = suds_to_dict(v)
        elif isinstance(v, list):
            result[k] = []
            for item in v:
                if hasattr(item, '__keylist__'):
                    result[k].append(suds_to_dict(item))
                else:
                    if isinstance(item, SudsText):
                        result[k].append(unicode(item))
        else:
            if isinstance(v, SudsText):
                result[k] = unicode(v)
            else:
                result[k] = v
    return result


def to_google_camel_case(text):
    return text[0].lower() + text[1:]


def chunked(iterable, n, marker=None):
    """Break an iterable into lists of a given length::
    >>> list(chunked([1, 2, 3, 4, 5, 6, 7], 3))
    [[1, 2, 3], [4, 5, 6], [7]]

    If the length of ``iterable`` is not evenly divisible by ``n``, the last
    returned list will be shorter.

    This is useful for splitting up a computation on a large number of keys
    into batches, to be pickled and sent off to worker processes. One example
    is operations on rows in MySQL, which does not implement server-side
    cursors properly and would otherwise load the entire dataset into RAM on
    the client.

    """
    if marker is None:
        marker = object()
    # Doesn't seem to run into any number-of-args limits.
    for group in (list(g) for g in izip_longest(*[iter(iterable)] * n,
                                                fillvalue=marker)):
        if group[-1] is marker:
            # If this is the last group, shuck off the padding:
            del group[group.index(marker):]
        yield group
