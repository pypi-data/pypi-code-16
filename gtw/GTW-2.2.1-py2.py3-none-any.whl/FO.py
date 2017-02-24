# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package GTW.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.FO
#
# Purpose
#    Formatter for attributes of Objects
#
# Revision Dates
#    20-Jan-2010 (CT) Creation
#    10-Feb-2010 (CT) `MOM.Entity.FO` factored
#     5-Aug-2010 (CT) `_get_nested` added to support `composite.field`
#    10-Dec-2012 (CT) Change `_get_nested` to delegate to `obj.FO`
#     3-Mar-2014 (CT) Factor `_get_attr`; add support for `tuple, list`
#     8-Oct-2015 (CT) Change `__getattr__` to *not* handle `__XXX__`
#    ««revision-date»»···
#--

from   __future__               import unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL
from   _TFL.pyk                 import pyk

import _TFL._Meta.Object

class FO (TFL.Meta.Object) :
    """Formatter for attributes of Objects."""

    def __init__ (self, obj, enc = None) :
        self.__obj    = obj
        self.__fo     = obj.FO
        self.__enc    = enc
        self.__cache  = {}
    # end def __init__

    def _get_attr (self, name) :
        result = getattr (self.__fo, name)
        if result is None :
            result = ""
        elif isinstance (result, (tuple, list)) :
            result = "<br>".join \
                (   pyk.decoded (r if r is not None else "", self.__enc)
                for r in result
                )
        return pyk.decoded (result, self.__enc)
    # end def _get_attr

    def _get_nested (self, name) :
        try :
            result = self.__cache [name]
        except KeyError :
            self.__cache [name] = result = self._get_attr (name)
        return result
    # end def _get_nested

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        if "." in name :
            result = self._get_nested (name)
        else :
            result = self._get_attr   (name)
        setattr (self, name, result)
        return result
    # end def __getattr__

# end class FO

if __name__ != "__main__" :
    GTW._Export ("*")
### __END__ GTW.FO
