# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Martin Glueck All rights reserved
# Langstrasse 4, A--2244 Spannberg, Austria. martin@mangari.org
# ****************************************************************************
# This module is part of the package GTW.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.Request_Data
#
# Purpose
#    Wrapper around ddict like data where the values are lists but should not
#    be lists
#
# Revision Dates
#    19-Jan-2010 (MG) Creation
#    20-Jan-2010 (MG) Check's added to make sure the values in the original
#                     data dict contains exactly one element
#    20-Jan-2010 (MG) Support dict's which don't have lists as value's
#    29-Jan-2010 (MG) `__getitem__` and `get` fixed
#     3-Feb-2010 (MG) `iteritems` added
#    10-Feb-2010 (MG) Convert the data into unicode
#    21-Feb-2010 (MG) `pop` added
#    20-Mar-2010 (MG) Moved into `GTW` package
#    28-Jun-2010 (MG) `iterkeys` added
#    14-Nov-2011 (CT) Change `iteritems` to `_convert_element`
#    14-Nov-2011 (CT) Add `__nonzero__`
#    21-Nov-2011 (CT) Change `_convert_element` to `logging` instead of `assert`
#    20-Jun-2012 (CT) Add `Request_Data_List`; factor/rewrite `_normalized`
#     2-Jul-2012 (CT) Add `has_option`
#     3-Jul-2012 (CT) Redefine `Request_Data_List.get` to fix `default`
#     5-Oct-2012 (CT) Change `Request_Data_List.get` to use `.getlist`
#    17-May-2013 (CT) Change `has_option` to return default `False`
#    29-Apr-2014 (CT) Add guard against `data is not None`
#    16-Oct-2015 (CT) Use `portable_repr` for arguments of `logging.warning`
#    ««revision-date»»···
#--

from   _TFL               import TFL
from   _TFL.pyk           import pyk

from   _TFL.portable_repr import portable_repr

import _TFL._Meta.Object

from   _GTW               import GTW

import  logging

@pyk.adapt__bool__
class _GTW_Request_Data_ (TFL.Meta.Object) :
    """Convert the list values into no lists during access."""

    _real_name = "Request_Data"

    def __init__ (self, data) :
        self.data = data if data is not None else {}
    # end def __init__

    def get (self, key, default = None) :
        return self._convert_element (key, self.data.get (key, default))
    # end def get

    def has_option (self, key) :
        """Return value of `key` or True, if `key` was specified with empty
           value.
        """
        result = self.get (key, False)
        if isinstance (result, (list, tuple)) and result :
            result = result [-1]
        if result == "" :
            result = True
        elif result and result.lower () in ("no", "false", "0") :
            result = False
        return result
    # end def has_option

    def iteritems (self) :
        convert = self._convert_element
        for key in pyk.iterkeys (self.data) :
            yield key, convert (key, self [key])
    # end def iteritems

    def iterkeys (self) :
        return pyk.iterkeys (self.data)
    # end def iterkeys

    def pop (self, key, default = None) :
        return self._convert_element (key, self.data.pop (key, default))
    # end def pop

    def _convert_element (self, key, value) :
        if isinstance (value, (list, tuple)) :
            if len (value) != 1 :
                logging.warning \
                    ( "Got multiple values for '%s', using '%s', ignoring: %s"
                    , key, portable_repr (value [0]), portable_repr (value [1:])
                    )
            value = value [0]
        return self._normalized (value)
    # end def _convert_element

    def _normalized (self, value) :
        if isinstance (value, pyk.byte_types) :
            return pyk.text_type (value, "utf8", "replace")
        return value
    # end def _normalized

    def __contains__ (self, item) :
        return item in self.data
    # end def __contains__

    def __getitem__ (self, key) :
        return self._convert_element (key, self.data [key])
    # end def __getitem__

    def __iter__ (self) :
        return iter (self.data)
    # end def __iter__

    def __bool__ (self) :
        return bool (self.data)
    # end def __bool__

    def __repr__ (self) :
        return repr (self.data)
    # end def __repr__

Request_Data = _GTW_Request_Data_ # end class

class _GTW_Request_Data_List_ (_GTW_Request_Data_) :
    """Convert all values into lists during access."""

    _real_name = "Request_Data_List"

    def __init__ (self, data) :
        if isinstance (data, dict) :
            from werkzeug.datastructures import MultiDict
            data = MultiDict (data)
        self.data = data
    # end def __init__

    def get (self, key, default = []) :
        normalized = self._normalized
        return list (normalized (x) for x in self.data.getlist (key))
    # end def get

    def _convert_element (self, key, value) :
        normalized = self._normalized
        if isinstance (value, (list, tuple)) :
            return list (normalized (x) for x in value)
        return [normalized (value)]
    # end def _convert_element

Request_Data_List = _GTW_Request_Data_List_ # end class

if __name__ != "__main__" :
    GTW._Export ("*")
### __END__ GTW.Request_Data
