# -*- coding: utf-8 -*-
# Copyright (C) 2012-2016 Mag. Christian Tanzer All rights reserved
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
#    GTW.RST.TOP.Root
#
# Purpose
#    Root class of tree of pages
#
# Revision Dates
#     5-Jul-2012 (CT) Creation (based on GTW.NAV.Base)
#     9-Jul-2012 (CT) Add `static_handler`
#    23-Jul-2012 (CT) Redefine `_http_response` to call `_http_response_finish`
#    30-Jul-2012 (CT) Redefine `Auth_Required`
#     4-Aug-2012 (MG) Set session cookie before saving the session
#     8-Aug-2012 (MG) Consider `hidden` in `home`
#    17-Aug-2012 (MG) Clear Etag if notifications are part of the response
#    26-Sep-2012 (CT) Add argument `resource` to `_http_response`
#    18-Oct-2012 (CT) Factor `E_Type_Desc`, `ET_Map` to `GTW.RST.Root`
#    15-Jan-2013 (CT) Add `cc_domain`
#     2-May-2013 (CT) Add argument `resource` to `_http_response_finish`...
#    10-Dec-2013 (CT) Add `href_login`; add `s_domain` to `login_url`
#    11-Dec-2013 (CT) Add default for `csrf_check_p`
#    10-Jun-2015 (CT) Use `response.indicate_notifications`, not home-grown code
#    17-Nov-2015 (CT) Add `test_client`
#    15-Jan-2016 (CT) Add imports for `GTW.jQuery` and `.V5a`
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

import _GTW._RST.Resource
import _GTW._RST._TOP.Dir

import _GTW.jQuery
import _GTW.V5a

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL.Decorator           import getattr_safe
from   _TFL.pyk                 import pyk

import _TFL._Meta.Object

import datetime
import time

GTW.RST.Root.E_Type_Desc.add_properties \
    ("admin", "doc", "manager", "rest_api", "rest_doc")

class TOP_Root (GTW.RST.TOP._Dir_, GTW.RST.Root) :
    """Root of tree of pages."""

    _real_name                 = "Root"

    Auth_Required              = GTW.RST.HTTP_Status.Login_Required
    Media_Parameters           = None

    cc_domain                  = None
    cert_auth_path             = None
    copyright_start            = None
    copyright_url              = None
    csrf_check_p               = True
    owner                      = None
    q_prefix                   = "q"
    qx_prefix                  = "qx"
    translator                 = None

    _exclude_robots            = False
    _static_handler            = None

    from _GTW._RST._TOP.Request  import Request  as Request_Type
    from _GTW._RST._TOP.Response import Response as Response_Type

    def __init__ (self, HTTP, ** kw) :
        self.pop_to_self (kw, "static_handler", prefix = "_")
        if "copyright_start" not in kw :
            kw ["copyright_start"] = time.localtime ().tm_year
        self.__super.__init__ (HTTP = HTTP, ** kw)
    # end def __init__

    @classmethod
    def allow (cls, link, user) :
        try :
            allow_user = link.allow_user
        except Exception :
            return True
        else :
            return allow_user (user)
    # end def allow

    @Once_Property
    @getattr_safe
    def home (self) :
        if self.dir_template is None :
            try :
                return first (l for l in self.own_links if not l.hidden)
            except IndexError :
                pass
        return self
    # end def home

    @Once_Property
    @getattr_safe
    def href_login (self) :
        if "Auth" in self.SC :
            return self.SC.Auth.href_login
    # end def href_login

    @property
    @getattr_safe
    def h_title (self) :
        return pyk.text_type (self.owner or self.name)
    # end def h_title

    @Once_Property
    @getattr_safe
    def login_url (self) :
        result = self.href_login
        if result and self.s_domain :
            result = self._get_secure_url (result)
        return result
    # end def login_url

    @Once_Property
    @getattr_safe
    def static_handler (self) :
        result = self._static_handler
        if result is None :
            p = sos.path.normpath \
                (sos.path.join (sos.path.dirname (__file__), "../..", "media"))
            result = self._static_handler = self.HTTP.Static_File_App ("GTW", p)
        return result
    # end def static_handler

    @Once_Property
    @getattr_safe
    def test_client (self) :
        from werkzeug.test import Client
        return Client (self, use_cookies = False)
    # end def test_client

    def _http_response (self, resource, request, response) :
        Status = self.Status
        try :
            result = self.__super._http_response (resource, request, response)
        except (Status.Informational, Status.Redirection, Status.Successful) :
            self._http_response_finish (resource, request, response)
            raise
        except Exception :
            self._http_response_finish_error (resource, request, response)
            raise
        else :
            self._http_response_finish (resource, request, response)
            return result
    # end def _http_response

    def _http_response_finish (self, resource, request, response) :
        response.indicate_notifications ()
        response._set_session_cookie    ()
        response.session.save           ()
        scope = self.scope
        if scope :
            scope.commit ()
    # end def _http_response_finish

    def _http_response_finish_error (self, resource, request, response) :
        scope = self.scope
        if scope :
            try :
                scope.rollback ()
            except Exception :
                pass
    # end def _http_response_finish_error

Root = TOP_Root # end class

if __name__ != "__main__" :
    GTW.RST.TOP._Export ("*")
### __END__ GTW.RST.TOP.Root
