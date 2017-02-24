# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.Werkzeug.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.Werkzeug.Response
#
# Purpose
#    Extend werkzeug's Response class
#
# Revision Dates
#    20-Jun-2012 (CT) Creation
#     2-Mar-2013 (CT) Add `add_header` and `set_header` (both encode `key`)
#    14-Mar-2014 (CT) Add `encoded_url`
#    13-Apr-2015 (CT) Use `TFL.json_dump.default`
#     6-May-2015 (CT) Use `TFL.json_dump.to_string`
#    21-Oct-2015 (CT) Use `as_str`, node `encoded`, for header `key`
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _GTW                       import GTW
from   _TFL                       import TFL

import _GTW._Werkzeug

from   _TFL._Meta.Once_Property   import Once_Property
from   _TFL.pyk                   import pyk

import _TFL._Meta.M_Class
import _TFL.json_dump

from   werkzeug.wrappers          import Response
from   werkzeug.contrib.wrappers  import DynamicCharsetResponseMixin
from   werkzeug.urls              import Href

class _WZG_Response_ \
          ( TFL.Meta.BaM
              ( DynamicCharsetResponseMixin, Response
              , metaclass = TFL.Meta.M_Class
              )
          ) :
    """Extend werkzeug's Response class."""

    _real_name           = "Response"

    default_charset      = "utf-8"

    def add_header (self, key, value, ** kw) :
        key = pyk.as_str (key, "ascii")
        return self.headers.add (key, value, ** kw)
    # end def add_header

    def clear (self) :
        self.headers.clear ()
        self.response = []
        self.status   = self.default_status
    # end def clear

    def encoded_url (self, * args, ** kw) :
        if args :
            result = Href (args [0])
            return result (* args [1:], ** kw)
        else :
            result = Href ()
            return result (** kw) [2:]
    # end def encoded_url

    def write (self, data) :
        self.response.append (data)
    # end def write

    def set_header (self, key, value, ** kw) :
        key = pyk.as_str (key, "ascii")
        return self.headers.set (key, value, ** kw)
    # end def set_header

    def write_json (self, __data = None, ** kw) :
        data = dict (kw)
        if __data is not None :
            data.update (__data)
        self.set_header ("Content-Type", "text/javascript; charset=UTF-8")
        self.write      (TFL.json_dump.to_string (data))
    # end def write_json

Response = _WZG_Response_ # end class

if __name__ != "__main__" :
    GTW.Werkzeug._Export ("Response")
### __END__ GTW.Werkzeug.Response
