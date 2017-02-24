# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.RST.
# 
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.RST.R_Map
#
# Purpose
#    Resource map
#
# Revision Dates
#    18-Oct-2012 (CT) Creation
#    20-Oct-2012 (CT) Add and use `_find_missing`
#    ««revision-date»»···
#--

from   __future__ import absolute_import, division, print_function, unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL
from   _TFL.pyk                 import pyk

import _TFL._Meta.Object

class _M_R_Map_ (TFL.Meta.Object.__class__) :
    """Meta class for resource maps"""

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        cls.add_properties (* dct.get ("_prop_names", ()))
    # end def __init__

    def add_properties (cls, * names) :
        for name in names :
            cls.add_property (name)
    # end def add_properties

    def add_property (cls, name) :
        _name = "_" + name
        def _get (self) :
            result = getattr (self, _name)
            if result is None and self._find_missing is not None :
                result = self._find_missing (name)
            return result
        def _set (self, value) :
            setattr (self, _name, value)
        def _del (self) :
            setattr (self, _name, None)
        setattr (cls, name, property (_get, _set, _del))
        setattr (cls, _name, None)
    # end def add_property

# end class _M_R_Map_

class R_Map (TFL.Meta.BaM (TFL.Meta.Object, metaclass = _M_R_Map_)) :
    """Resource map"""

    _find_missing = None
    _prop_names   = ()

    def __repr__ (self) :
        name  = self.__class__.__name__
        attrs = sorted \
            (  (k.strip ("_"), v)
            for k, v in sorted (pyk.iteritems (self.__dict__))
            )
        return "%s (%s)" % \
            (name, ", ".join (("%s = %s" % (k, v)) for k, v in attrs))
    # end def __repr__

# end class R_Map

if __name__ != "__main__" :
    GTW.RST._Export ("*")
### __END__ GTW.RST.R_Map
