# -*- coding: utf-8 -*-
# Copyright (C) 2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.RST.TOP.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.RST.TOP.Literal
#
# Purpose
#    Model a tree-of-pages leaf with literal content
#
# Revision Dates
#    22-Apr-2015 (CT) Creation
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

import _GTW._RST.Resource
import _GTW._RST._TOP.Page

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL.Decorator           import getattr_safe

_Ancestor = GTW.RST.TOP.Page

class _Literal_ (_Ancestor) :
    """Page with literal contents."""

    ignore_picky_accept        = True

    class _Literal_GET (_Ancestor.GET) :

        _real_name             = "GET"

        def _response_body (self, resource, request, response) :
            return resource.contents
        # end def _response_body

    GET = _Literal_GET # end class

# end class _Literal_

_Ancestor = _Literal_

class HTML (_Ancestor) :
    """Page with literal HTML contents."""

    class HTML_Get (_Ancestor.GET) :

        _real_name             = "GET"
        _renderers             = (GTW.RST.TOP.HTML, )

    GET = HTML_Get # end class

# end class HTML

class TXT (_Ancestor) :
    """Page with literal text contents."""

    class TXT_Get (_Ancestor.GET) :

        _real_name             = "GET"
        _renderers             = (GTW.RST.Mime_Type.TXT, )

    GET = TXT_Get # end class

# end class TXT

if __name__ != "__main__" :
    GTW.RST.TOP._Export_Module ()
### __END__ GTW.RST.TOP.Literal
