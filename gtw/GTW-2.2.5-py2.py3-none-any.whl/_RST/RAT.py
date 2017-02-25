# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Mag. Christian Tanzer All rights reserved
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
#    GTW.RST.RAT
#
# Purpose
#    RESTful resource for REST authentication token
#
# Revision Dates
#     1-May-2013 (CT) Creation
#     3-May-2013 (CT) Use `request.rat_secret`, not home-grown code
#     6-May-2013 (CT) Add `send_error_email` to `RAT.POST._response_body`
#     9-Dec-2013 (CT) Factor `Signed_Token`
#     1-Apr-2014 (CT) Set `secure` to `request.is_secure`
#    ««revision-date»»···
#--

from   __future__ import absolute_import, division, print_function, unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

import _GTW._RST.Auth_Mixin
import _GTW._RST.HTTP_Method
import _GTW._RST.Mime_Type
import _GTW._RST.Resource
import _GTW._RST.Signed_Token

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL.Decorator           import getattr_safe

import _TFL.Password_Hasher

import datetime
import time

_Ancestor = GTW.RST.Leaf

class RAT (GTW.RST.Auth_Mixin, _Ancestor) :
    """RESTful resource for REST authentication token"""

    cookie_kw                  = dict \
        ( expires              = None
        , httponly             = True
        , secure               = True
        )
    exclude_robots             = True
    hidden                     = True
    ignore_picky_accept        = True
    pid                        = "RAT"
    use_name_for_cookie        = True

    GET                        = None
    HEAD                       = None

    class RAT_POST (GTW.RST.Auth_Mixin.POST) :

        _real_name             = "POST"
        _renderers             = (GTW.RST.Mime_Type.JSON, )

        def _response_body (self, resource, request, response) :
            debug    = getattr (resource.top, "DEBUG", False)
            req_data = request.req_data
            result   = {}
            self.errors = GTW.RST.Errors ()
            username, password = self._credentials_validation \
                (resource, request, debug = debug)
            if self.errors :
                from _TFL.formatted_repr import formatted_repr as formatted
                result ["errors"]    = self.errors
                response.status_code = 400
                resource.send_error_email \
                    ( request
                    , "RAT Authorization error"
                    , None
                    , "Errors:\n%s" % (formatted (self.errors), )
                    )
            else :
                account = self.account
                cn      = resource.pid
                scope   = account.home_scope
                data    = account.name \
                    if resource.use_name_for_cookie else str (account.pid)
                token   = GTW.RST.Signed_Token.REST_Auth \
                    ( request, account = account, data = data)
                rat     = result [cn] = token.value
                kw      = dict \
                    ( resource.cookie_kw
                    , max_age = resource.session_ttl
                    , secure  = request.is_secure
                    )
                response.set_secure_cookie (cn, rat, ** kw)
            return result
        # end def _response_body

    POST = RAT_POST # end class

# end class RAT

if __name__ != "__main__" :
    GTW.RST._Export ("*")
### __END__ GTW.RST.RAT
