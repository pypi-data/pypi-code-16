# -*- coding: utf-8 -*-
# Copyright (C) 2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package TFL.Meta.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    TFL.Meta.M_Auto_Update_Combined
#
# Purpose
#    Metaclass that automatically applies `update_combined` to a
#    class's attribute and the corresponding attribute of all its base classes
#
# Revision Dates
#    26-Jan-2015 (CT) Creation
#     6-Mar-2015 (CT) Add `except` to `_m_update_combine`
#     5-Aug-2015 (CT) Improve `__doc__`
#    ««revision-date»»···
#--

"""
Metaclass that automatically applies
:func:`~_TFL.update_combined.update_combined_many` to a class's attribute and
the corresponding attribute of all its base classes.

One specifies the attributes to be automatically combined by listing
their names in either :attr:`_attrs_to_update_combine` or
:attr:`_attrs_uniq_to_update_combine`.

::

    >>> from   _TFL.portable_repr import portable_repr

    >>> class A (TFL.Meta.BaM (object, metaclass = M_Auto_Update_Combined)) :
    ...     _attrs_to_update_combine      = ("foo", "bar", "qux")
    ...     _attrs_uniq_to_update_combine = ("quux", )
    ...     foo                           = set ([1, 2, 3])
    ...     qux = quux                    = [(0, ), (1, )]
    ...
    >>> class B (A) :
    ...     _attrs_to_update_combine      = ("baz", )
    ...     foo                           = set ([5, 4, 3])
    ...     bar                           = set ("ab")
    ...     qux = quux                    = [(2, ), (0, )]
    ...
    >>> class C (B) :
    ...     bar                           = set ("xyz")
    ...     qux = quux                    = [(0, 1, ), (3, )]

    >>> print (portable_repr (A.foo), portable_repr (A.bar), portable_repr (A.qux), portable_repr (A.quux))
    {1, 2, 3} <Undef/value> [(0,), (1,)] [(0,), (1,)]
    >>> print (portable_repr (B.foo), portable_repr (B.bar), portable_repr (B.qux), portable_repr (B.quux), portable_repr (B.baz))
    {1, 2, 3, 4, 5} {'a', 'b'} [(0,), (1,), (2,), (0,)] [(0,), (1,), (2,)] <Undef/value>
    >>> print (portable_repr (C.foo), portable_repr (C.bar), portable_repr (C.qux), portable_repr (C.quux), portable_repr (C.baz))
    {1, 2, 3, 4, 5} {'a', 'b', 'x', 'y', 'z'} [(0,), (1,), (2,), (0,), (0, 1), (3,)] [(0,), (1,), (2,), (0, 1), (3,)] <Undef/value>

    >>> class P (TFL.Meta.BaM (object, metaclass = M_Auto_Update_Combined)) :
    ...     _attrs_to_update_combine      = ("foo", "bar")
    ...     bar                           = dict (x = 1, y = 2)
    >>> class R (object) :
    ...     foo                           = dict (u = 1, v = "a")
    ...     bar                           = dict (y = 3, z = 42)
    ...     baz                           = dict (a = 0)
    >>> class PR (P, R) :
    ...     _attrs_to_update_combine      = ("baz", )
    ...     baz                           = dict (b = 42)
    >>> class RP (R, P) :
    ...     foo                           = dict (v = "b", w = "a")
    ...     bar                           = dict (x = "z", z = -42)
    ...     baz                           = dict (c = 137)

    >>> print (portable_repr (P.foo),  portable_repr (P.bar))
    <Undef/value> {'x' : 1, 'y' : 2}
    >>> print (portable_repr (R.foo),  portable_repr (R.bar), portable_repr (R.baz))
    {'u' : 1, 'v' : 'a'} {'y' : 3, 'z' : 42} {'a' : 0}
    >>> print (portable_repr (PR.foo), portable_repr (PR.bar), portable_repr (PR.baz))
    {'u' : 1, 'v' : 'a'} {'x' : 1, 'y' : 2, 'z' : 42} {'a' : 0, 'b' : 42}
    >>> print (portable_repr (RP.foo), portable_repr (RP.bar), portable_repr (RP.baz))
    {'u' : 1, 'v' : 'b', 'w' : 'a'} {'x' : 'z', 'y' : 3, 'z' : -42} {'c' : 137}

"""

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _TFL                           import TFL
from   _TFL.pyk                       import pyk

from   _TFL.predicate                 import uniq
from   _TFL.update_combined           import update_combined_many

import _TFL._Meta.M_Auto_Combine_Sets
import _TFL._Meta.M_Class

import itertools

class M_Auto_Update_Combined (TFL.Meta.M_Auto_Combine_Sets, TFL.Meta.M_Class) :

    _attrs_to_update_combine      = ()
    _attrs_uniq_to_update_combine = ()

    _sets_to_combine              = \
        ("_attrs_to_update_combine", "_attrs_uniq_to_update_combine")

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        cls._m_update_combine  (bases, dct)
    # end def __init__

    def _m_update_combine (cls, bases, dct) :
        def _gen (cls, bases, name) :
            undef = update_combined_many.Undef
            for c in reversed ((cls, ) + bases) :
                yield getattr (c, name, undef)
        for name in cls._attrs_to_update_combine :
            try :
                v = update_combined_many (* _gen (cls, bases, name))
            except Exception as exc :
                print \
                    ( "*** Exception when trying to update/combined", name
                    , "for class", cls
                    )
                raise
            setattr (cls, name, v)
        for name in cls._attrs_uniq_to_update_combine :
            v = update_combined_many (* _gen (cls, bases, name))
            setattr (cls, name, v.__class__ (uniq (v)))
    # end def _m_update_combine

# end class M_Auto_Update_Combined

if __name__ != "__main__" :
    TFL.Meta._Export ("*")
### __END__ TFL.Meta.M_Auto_Update_Combined
