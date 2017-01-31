# Copyright 2014-2016 Morgan Delahaye-Prat. All Rights Reserved.
#
# Licensed under the Simplified BSD License (the "License");
# you may not use this file except in compliance with the License.
"""Hypr Mini Query (HMQ) DSL

HMQ is a language to search and filter resources, fitted to the query string
of an URL. It supports unconstrained intervals, the logical negation and allows
to express complex logical expressions with the use of clausal normal form.


Predicates
----------

The HMQ provides the following predicates with x is a property of the
resources:

x=y         x is equal to y
x=!y        x is different from y
x=[y,z]     x is greater or equal to y and x is lower or equal to z
x=[y,]      x is greater or equal to y
x=[,z]      x is lower or equal to z
x=![y,z]    x is lower than y or x is greater than z
x=![y,]     x is lower than y
x=![,z]     x is greater than z

The following predicates are available when y and z are strings:

x=y*        x starts with y
x=*y        x ends with y
x=*y*       x contains y


Query construction
------------------

Each field-value pair in the query string is a clause with the field used as a
the property of the predicate.

URL: /path/to/resources?prop0=val0&prop1=val1
stands for: (resource.prop0 = val0) ∧ (resource.prop1 = val1)

It is possible to use multiple predicates on the same property in the same
clause with a logical OR:

URL: /path/to/resources?prop0=val0|val1
stands for: (resource.prop0 = val0 ∨ resource.prop0 = val1)

It is possible to group multiple predicates on different properties in the same
clause with the use of named group:

URL: /path/to/resources?prop0:group0=val0&prop1:group0=val1
stands for: (resource.prop0 = val0 ∨ resource.prop1 = val1)

Any query string complying to this scheme is a valid query:

?property[:group]=predicate[|predicate...][&clause...]


Python notation
---------------

Each query is writable in python with each predicate described in the form of
a tuple of three elements also known as the full notation:

(negation, predicate, group)

it also exists the partial notation `(negation, predicate)` and the simple
notation `(predicate,)` or `predicate`

Each predicates associated to a same property are grouped in a tuple:

resource.get(prop0=val0, prop1=val1)
stands for: (resource.prop0 = val0) ∧ (resource.prop1 = val1)

resource.get(prop0=(val0, val1))
resource.get(prop0=((True, val0), (True, val1)))
stands for: (resource.prop0 = val0 ∨ resource.prop0 = val1)

resources.get(prop0=(True, val0, 'group0'), prop1=(True, val1, 'group1'))
stands for: (resource.prop0 = val0 ∨ resource.prop1 = val1)

The normalized form is a tuple of full notations.


Known limitations
-----------------

A partial notation of two boolean values is not discernible from a tuple of two
simple boolean notations and will raise a RuntimeError as a non deterministic
query.
"""


import re
from datetime import datetime


DATE = re.compile('(\d{4}-\d{2}-\d{2})(?:T(\d{2}:\d{2}:\d{2})(?:.(\d+))?Z)?')
RANGE = re.compile('\[(.+)?(?(1),(.+)?|,(.+))\]')


class Range:
    """A custom range object with no type constaints."""

    def __init__(self, start=None, stop=None):
        """Initialization."""
        self.start = start
        self.stop = stop

    def __eq__(self, other):
        """Compare two range objects."""
        if not hasattr(other, 'start') or not hasattr(other, 'stop'):
            return False
        return self.start == other.start and self.stop == other.stop


def autocast(string):
    """Automatically cast a string to the best type."""
    if string is None:
        return None

    l_string = string.lower()

    if l_string == 'null':
        return None

    if l_string in ('true', 'on', 'yes'):
        return True

    if l_string in ('false', 'off', 'no'):
        return False

    try:
        numeric = float(string)
        integer = int(numeric)
        return (numeric, integer)[integer == numeric]
    except ValueError:
        pass

    re_match = DATE.match(string)
    if re_match is not None:
        val = re_match.groups()
        try:
            return datetime.strptime(
                '%sT%s.%sZ' % (val[0], val[1] or '00:00:00', val[2] or '0'),
                '%Y-%m-%dT%H:%M:%S.%fZ'
            )
        except ValueError:
            pass

    return string


def parse_predicate(string, group=None):
    """Parse a predicate string."""
    positive = string[0] != '!'
    value = string[not positive:]                    # >:-) pythonic ta mère !

    match = RANGE.match(value)
    if match is not None:
        start, stop = match.group(1), match.group(2) or match.group(3)
        value = Range(autocast(start), autocast(stop))
    elif '*' in value:
        value = re.compile('^%s$' % value.replace('*', '.*'))
    else:
        value = autocast(value)

    return positive, value, group


def parse_clause(string, group=None):
    """Parse a clause string."""
    return tuple(parse_predicate(p, group) for p in string.split('|') if p)


def normalize_query(query, key=None):
    """Normalize a query.

    A normalized query is expressed with a tuple of full notations.
    """
    if not isinstance(query, tuple):
        return ((True, query, key),)           # simple value

    query_length = len(query)

    if query_length == 0:                       # empty query
        return query

    if isinstance(query[0], bool):              # tuple start with a bool
        if 1 < query_length < 4 and isinstance(query[1], bool):
            raise RuntimeError('non determinist query.')
        elif 1 < query_length < 4:              # bool, other[, other]
            return ((query + (key,))[:3],)      # is a [partial] complexe value

    rv = []
    for value in query:
        if not isinstance(value, tuple):
            rv.append((True, value, key))
        else:
            rv.append((value + (key,))[:3])

    return tuple(rv)
