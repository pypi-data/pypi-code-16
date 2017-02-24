# -*- coding: utf-8 -*-
# Copyright (C) 2010-2014 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package MOM.Attr.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    MOM.Attr.Coll
#
# Purpose
#    Wrapper classes around Python lists/sets... to hold collection of
#    attributes
#
# Revision Dates
#     3-Sep-2010 (CT) Creation
#     4-Sep-2010 (CT) Creation continued
#     6-Sep-2010 (CT) Creation continued..
#     7-Sep-2010 (CT) `Table` added
#     7-Sep-2010 (CT) `old` added to `_override` and passed to
#                     `record_attr_change`
#     8-Sep-2010 (CT) `M_Coll.__init__` changed to apply `_override` only once
#     3-Jun-2013 (CT) Use `.attr_prop` to get attribute descriptors
#    ««revision-date»»···
#--

from   __future__            import absolute_import, division
from   __future__            import print_function, unicode_literals

from   _MOM                  import MOM
from   _TFL                  import TFL

import _TFL._Meta.M_Class
import _TFL.Decorator

class M_Coll (TFL.Meta.M_Class) :

    _state_changers = ()
    Table           = {}

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        if cls.P_Type is not None :
            if cls.P_Type not in cls.Table :
                cls.Table [cls.P_Type] = cls
                for mn in cls._state_changers :
                    m = getattr (cls, mn, None)
                    if m is not None :
                        setattr (cls, mn, cls._override (m))
            else :
                ### sub-class overrriding `attr_name`
                assert cls.Table [cls.P_Type] is bases [0]
    # end def __init__

    @staticmethod
    @TFL.Decorator
    def _override (method) :
        def _ (self, * args, ** kw) :
            old    = self.copy ()
            result = method (self, * args, ** kw)
            if old != self :
                self.record_attr_change (old)
            return result
        return _
    # end def _override

# end class M_Coll

class _Mixin_ (TFL.Meta.BaM (object, metaclass = M_Coll)) :

    P_Type          = None

    attr_name       = None
    owner           = None
    _attr_man       = property (lambda s : s.owner and s.owner._attr_man)

    def copy (self) :
        return self.__class__ (self)
    # end def copy

    @property
    def owner_attr (self) :
        """Return the attribute (kind property) of the `owner` object that
           holds `self`.
        """
        if self.owner and self.attr_name :
            return self.owner.attr_prop (self.attr_name)
    # end def owner_attr

    def record_attr_change (self, old) :
        ### communicate change of `self` to `self.owner`
        if self.owner is not None :
            self.owner.record_attr_change \
                ({self.attr_name : self.owner_attr.as_string (old)})
    # end def record_attr_change

# end class _Mixin_

class List (_Mixin_, list) :
    """List of attribute values"""

    P_Type          = list
    _state_changers = \
        ( "__delitem__", "__delslice__"
        , "__iadd__", "__imul__"
        , "__setitem__", "__setslice__"
        , "append", "extend", "insert", "pop", "remove", "reverse", "sort"
        )

# end class List

class Set (_Mixin_, set) :
    """Set of attribute values"""

    P_Type          = set
    _state_changers = \
        ( "__iand__", "__ior__", "__isub__", "__ixor__"
        , "add", "clear", "difference_update", "discard"
        , "intersection_update", "pop", "remove"
        , "symmetric_difference_update", "update"
        )

# end class Set

if __name__ != "__main__" :
    MOM.Attr._Export ("*")
### __END__ MOM.Attr.Coll
