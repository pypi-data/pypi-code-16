# -*- coding: utf-8 -*-
# Copyright (C) 2009-2014 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package MOM.Prop.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    MOM.Prop.Kind
#
# Purpose
#    Base class for attribute and predicate kinds
#
# Revision Dates
#    24-Sep-2009 (CT) Creation
#    12-Sep-2012 (CT) Add `__init__` argument `e_type`
#     7-Jun-2013 (CT) Add `assign`
#    25-Jun-2013 (CT) Use `__mro__`, not `mro ()`
#    26-Jun-2013 (CT) Derive from `TFL.Meta.Object`, not `property`
#    ««revision-date»»···
#--

from   _MOM                  import MOM
from   _TFL                  import TFL

import _MOM._Meta.M_Prop_Kind
import _MOM._Prop

import _TFL._Meta.Object

class _Prop_Kind_ \
          ( TFL.Meta.BaM
              ( TFL.Meta.Object
              , metaclass = MOM.Meta.M_Prop_Kind
              )
          ) :
    """Base class for attribute and predicate kinds."""

    _real_name    = "Kind"

    def __init__ (self, prop, e_type) :
        self.prop    = prop
        self.name    = prop.name
        self.__doc__ = prop.description
    # end def __init__

    def assign (self, e_type, name) :
        setattr (e_type, name, self)
    # end def assign

    def __getattr__ (self, name) :
        if not name.startswith ("_") :
            return getattr (self.prop, name)
        raise AttributeError \
            ("%s [%s: %s]" % (name, self, self.__class__.__mro__))
    # end def __getattr__

Kind = _Prop_Kind_ # end class

if __name__ != "__main__" :
    MOM.Prop._Export ("*")
### __END__ MOM.Prop.Kind
