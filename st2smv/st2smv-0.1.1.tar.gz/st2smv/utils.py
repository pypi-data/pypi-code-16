## Copyright (c) 2015-2016, Blake C. Rawlings.
##
## This file is part of `st2smv`.

from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

import logging
import time

import six

logger = logging.getLogger(__name__)


def timing(log_fun=logger.debug, log_text='{}'):
    """Use this function as a decorator to log timing information.

    `log_text` should be a format string with a single placeholder,
    which will be replaced with the time it took to call the function.

    """
    def decorator(f):
        def wrapped(*args, **kwargs):
            t0 = time.time()
            retval = f(*args, **kwargs)
            t1 = time.time()
            log_fun(log_text.format(t1 - t0))
            return retval
        return wrapped
    return decorator


def try_incr(d, key, delta):
    """Try to increment `d[key]` by `delta`.

    If `key` is not in `d`, then add it to `d` with the value `delta`.

    """
    if key in d:
        d[key] += delta
    else:
        d[key] = delta


def flatten(nested):
    """Flatten a nested list."""
    ## Base case.
    if not isinstance(nested, (list, tuple)):
        return [nested]
    ## Recursive case.
    flat = []
    for n in nested:
        f = flatten(n)
        if isinstance(f, (list, tuple)):
            flat += f
        else:
            flat.append(f)
    return flat


def get_locations(tree, rule=None, root=None):
    """Get the (list of) locations in `tree` that meet `rule`.

    `tree` should have a nested iterable (`tuple` or `list`)
    structure.

    """
    if rule is None:
        rule = lambda x: True
    if root is None:
        root = []
    ##
    if rule(tree):
        return [root]
    elif isinstance(tree, (tuple, list)):
        retval = []
        for idx, subtree in enumerate(tree):
            subroot = root + [idx]
            subretval = get_locations(subtree, rule=rule, root=subroot)
            if subretval is not None:
                retval += subretval
        return retval
    else:
        return None


def get_value_at_location(tree, location):
    reference = tree
    for idx in location:
        reference = reference[idx]
    return reference


def set_value_at_location(tree, location, value):
    reference = tree
    max_depth = len(location)
    for depth, idx in enumerate(location):
        if depth < max_depth - 1:
            reference = reference[idx]
        else:
            reference[idx] = value


def invert_mapping(mapping):
    """Invert a mapping.

    The input should be a `dict` with a 1:1 mapping from key to value.

    """
    return {value: key for (key, value) in mapping.items()}
