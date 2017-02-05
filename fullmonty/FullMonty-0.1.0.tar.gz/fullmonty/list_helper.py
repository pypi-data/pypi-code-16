# coding=utf-8
"""
Helpers for list manipulation.  Basically modelled from ruby's Array.compress, Array.uniq

Add the following to your *requirements.txt* file:

* ordereddict; python_version < '3.1'

"""
import collections

__docformat__ = 'restructuredtext en'

try:
    try:
        # noinspection PyUnresolvedReferences
        from ordereddict import OrderedDict
    except ImportError:
        # noinspection PyUnresolvedReferences
        from collections import OrderedDict

    def unique_list(src_list):
        """
        returns a new list without any duplicates

        :param src_list: source list
        :type src_list: list
        :return: unique list
        :rtype: list
        """
        return list(OrderedDict.fromkeys(src_list).keys())

except ImportError:
    print("ordereddict not installed!")
    exit(1)


def compress_list(src_list):
    """
    Removes None or empty items from the list

    :param src_list: source list
    :type src_list: list
    :return: compressed list
    :rtype: list
    """
    return [item for item in src_list if item]


def is_sequence(item):
    """
    tests if an item behaves like a list, but is not a string

    :param item: the item to test
    :type item: object
    :return: Asserted if the item behaves like a list but is not a string
    :rtype: bool
    """
    return (not hasattr(item, "strip") and
            (hasattr(item, "__getitem__") or hasattr(item, "__iter__")))


# noinspection PyShadowingBuiltins
def flatten(l):
    try:
        # noinspection PyUnboundLocalVariable
        basestring = basestring
    except NameError:
        basestring = (str, bytes)

    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, basestring):
            for sub in flatten(el):
                yield sub
        else:
            yield el
