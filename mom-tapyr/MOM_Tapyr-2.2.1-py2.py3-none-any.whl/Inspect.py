# -*- coding: utf-8 -*-
# Copyright (C) 2012-2017 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package MOM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    MOM.Inspect
#
# Purpose
#    Provide functions for introspection of MOM meta object model
#
# Revision Dates
#    14-May-2012 (CT) Creation
#     3-Aug-2012 (CT) Add `show_ref_map` and `show_ref_maps`
#     7-Aug-2012 (CT) Rename `parents` to `ancestors`
#    25-Aug-2012 (CT) Add `definers`
#    20-Sep-2012 (CT) Add `children_trans_iter`
#     6-Mar-2013 (CT) Add optional argument `sort_key` to `children_trans_iter`
#    25-Jun-2013 (CT) Use `__mro__`, not `mro ()`
#    24-Feb-2017 (CT) Rename to `Inspect` (`inspect` breaks setuptools)
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _TFL                  import TFL
from   _MOM                  import MOM

from   _TFL.portable_repr    import portable_repr
from   _TFL.pyk              import pyk

import _MOM._Meta.M_Entity
import _TFL.Accessor

def ancestors (T) :
    """Return the essential ancestors of essential type `T`."""
    return list (p for p in T.__mro__ if isinstance (p, MOM.Meta.M_E_Type))
# end def ancestors

def children_trans_iter (T, level = 0, seen = None, sort_key = None) :
    if seen is None :
        seen = set ()
    if sort_key is None :
        sort_key = TFL.Getter.i_rank
    yield T, level
    for c in sorted (pyk.itervalues (T.children), key = sort_key) :
        if c not in seen :
            seen.add (c)
            for cc, l in children_trans_iter (c, level + 1, seen, sort_key) :
                yield cc, l
# end def children_trans_iter

def definers (ioc, name) :
    """Return the classes defining `name` in `mro` of `ioc`"""
    try :
        mro = ioc.__mro__
    except AttributeError :
        mro = ioc.__class__.__mro__
    def _gen (mro, name) :
        for c in mro :
            v = c.__dict__.get (name)
            if v is not None :
                yield c, v
    return tuple (_gen (mro, name))
# end def definers

def show_children (T, bi = "  ", level = 0, seen = None) :
    """Display tree of children of essential type `T`."""
    if seen is None :
        seen = set ()
    print ("%s%s" % (bi * level, T.type_name))
    l1 = level + 1
    for c in sorted (pyk.itervalues (T.children), key = TFL.Getter.i_rank) :
        if c not in seen :
            show_children (c, bi, l1, seen)
            seen.add (c)
# end def show_children

def show_ref_map (T, name) :
    map = getattr (T, name, None)
    if map :
        print (T.type_name)
        print \
            ( "   "
            , "\n    ".join
                ( sorted
                    (   portable_repr ((c.type_name, sorted (eias)))
                    for c, eias in pyk.iteritems (map)
                    )
                )
            )
# end def show_ref_map

def show_ref_maps (scope, name = "Ref_Req_Map") :
    for T in scope.app_type._T_Extension :
        show_ref_map (T, name)
# end def show_ref_maps

if __name__ != "__main__" :
    MOM._Export_Module ()
### __END__ MOM.Inspect
