# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Mag. Christian Tanzer All rights reserved
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
#    GTW.RST.Request
#
# Purpose
#    Wrap and extend wsgi-specific Request class
#
# Revision Dates
#    19-Jun-2012 (CT) Creation
#    28-Jun-2012 (CT) Add `verbose`
#     2-Jul-2012 (CT) Factor `has_option` to `GTW.Request_Data`
#    17-Jul-2012 (CT) Add property `user`
#    24-Jul-2012 (CT) Add `use_language`
#     6-Aug-2012 (CT) Add attribute `lang`
#     2-Oct-2012 (CT) Add property `brief`
#    16-Oct-2012 (CT) Add properties `ckd` and `raw`
#    16-Jan-2013 (CT) Add `ssl_authorized_user` and `ssl_client_verified`
#    26-Jan-2013 (CT) Add and use `http_server_authorized_user`
#     2-May-2013 (CT) Factor in `cookie_encoding`, `cookie`, `secure_cookie`,
#                     `_cookie_signature` from `GTW.RST.TOP.Request`
#     2-May-2013 (CT) Factor `new_secure_cookie` from `GTW.RST.Response`
#     3-May-2013 (CT) Factor `rat_secret` and add `remote_addr` to it
#     4-May-2013 (CT) Add `cookies_to_delete`, use for failing `RAT`
#     4-May-2013 (CT) Factor `apache_authorized_user`
#     5-May-2013 (CT) Fix `signature` warning of `secure_cookie`
#     5-May-2013 (CT) Factor `_auth_user_name`, turn `username` into `property`
#     6-Dec-2013 (CT) Define `current_time` as property, not method
#     9-Dec-2013 (CT) Factor `Signed_Token`; add `cookie_salt`, `is_secure`
#     9-Dec-2013 (CT) Add properties `origin`, `origin_host`, `same_origin`,
#                     `server_name`, and `server_port`
#     7-Apr-2014 (CT) Change `rat_authorized_user` to look at `req_data ["RAT"]`
#    26-Apr-2014 (CT) Remove stale imports
#    29-Apr-2014 (CT) Add `getattr_safe` to several properties
#    20-Mar-2015 (CT) Add property `language`
#     8-Oct-2015 (CT) Change `__getattr__` to *not* handle `__XXX__`
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

from   _GTW                      import GTW
from   _TFL                      import TFL

import _GTW._RST
import _GTW._RST.Signed_Token

from   _TFL                      import I18N
from   _TFL.Decorator            import getattr_safe
from   _TFL._Meta.Once_Property  import Once_Property

import _TFL._Meta.Object

import time

### XXX replace home-grown code by werkzeug supplied functions
### XXX     werkzeug.utils, werkzeug.HTTP, ...

class _RST_Request_ (TFL.Meta.Object) :
    """Wrap and extend wsgi-specific Request class."""

    _real_name        = "Request"
    _resource         = None
    _user             = None

    allow_login       = False
    lang              = None
    original_resource = None

    def __init__ (self, root, environ) :
        self.root     = root
        self._request = root.HTTP.Request (environ)
        self.cookies_to_delete = set ()
    # end def __init__

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        if name == "request" : ### XXX remove after porting of GTW.Werkzeug.Error
            return self._request
        elif name != "_request" :
            result = getattr (self._request, name)
            setattr (self, name, result)
            return result
        raise AttributeError (name)
    # end def __getattr__

    @Once_Property
    @getattr_safe
    def apache_authorized_user (self) :
        return self.environ.get ("REMOTE_USER")
    # end def apache_authorized_user

    @Once_Property
    def brief (self) :
        return self.req_data.has_option ("brief")
    # end def brief

    @Once_Property
    def ckd (self) :
        req_data = self.req_data
        if "ckd" in req_data :
            return req_data.has_option ("ckd")
        elif self.method == "GET" :
            ### for `GET`, `ckd` is default
            return not req_data.has_option ("raw")
    # end def ckd

    @Once_Property
    def cookie_encoding (self) :
        return self.settings.get ("cookie_encoding", "utf-8")
    # end def cookie_encoding

    @Once_Property
    def cookie_salt (self) :
        return self.settings.get ("cookie_salt")
    # end def cookie_salt

    @property
    def current_time (self) :
        return time.time ()
    # end def current_time

    @Once_Property
    @getattr_safe
    def http_server_authorized_user (self) :
        result = self.ssl_authorized_user
        if result is None :
            result = self.apache_authorized_user
        return result
    # end def http_server_authorized_user

    @Once_Property
    def is_secure (self) :
        return self.scheme == "https"
    # end def is_secure

    @property
    def language (self) :
        result = self.lang
        if result is None :
            result = self.locale_codes
        return result [0] if result else None
    # end def language

    @Once_Property
    @getattr_safe
    def locale_codes (self) :
        """The locale-code for the current session."""
        return self.get_browser_locale_codes ()
    # end def locale_codes

    @Once_Property
    def origin (self) :
        result   = self.environ.get ("HTTP_ORIGIN")
        if result is None :
            referrer = self.referrer
            if referrer :
                url   = TFL.Url (referrer)
                parts = []
                if url.scheme :
                    parts.extend ((url.scheme, "://"))
                parts.append (url.authority)
                result = "".join (parts)
        return result
    # end def origin

    @Once_Property
    def origin_host (self) :
        origin = self.origin
        if origin :
            return origin.split ("//", 1) [-1]
    # end def origin_host

    @Once_Property
    @getattr_safe
    def rat_authorized_user (self) :
        rat = getattr (self.root.SC, "RAT", None)
        if rat is not None :
            cookie = self.cookies.get ("RAT") or self.req_data.get ("RAT", "")
            if cookie :
                token  = GTW.RST.Signed_Token.REST_Auth.recover \
                    (self, cookie, ttl_s = rat.session_ttl_s)
                if token :
                    return token.account.name
                else :
                    self.cookies_to_delete.add ("RAT")
    # end def rat_authorized_user

    @Once_Property
    def raw (self) :
        req_data = self.req_data
        if "raw" in req_data :
            return req_data.has_option ("raw")
        elif self.method != "GET" :
            ### for all methods but `GET`, `raw` is default
            return not req_data.has_option ("ckd")
    # end def raw

    @property
    def resource (self) :
        result = self._resource
        if result is None :
            result = self.root
        return result
    # end def resource

    @resource.setter
    def resource (self, value) :
        self._resource = value
    # end def resource

    @Once_Property
    def same_origin (self) :
        return self.server_name == self.origin_host
    # end def same_origin

    @Once_Property
    def server_name (self) :
        env = self.environ
        return env.get ("HTTP_HOST") or env.get ("SERVER_NAME")
    # end def server_name

    @Once_Property
    def server_port (self) :
        return self.environ.get ("SERVER_PORT")
    # end def server_port

    @property
    def settings (self) :
        return dict (self.root._kw, hash_fct = self.root.hash_fct)
    # end def settings

    @Once_Property
    @getattr_safe
    def ssl_authorized_user (self) :
        return self.environ.get ("SSL_CLIENT_S_DN_Email")
    # end def ssl_authorized_user

    @Once_Property
    @getattr_safe
    def ssl_client_verified (self) :
        return self.environ.get ("SSL_CLIENT_VERIFY") == "SUCCESS"
    # end def ssl_client_verified

    @property
    @getattr_safe
    def user (self) :
        result = self._user
        if result is None and self.username :
            self._user = self.root._get_user (self.username)
        return self._user
    # end def user

    @user.setter
    def user (self, value) :
        self._user = value
    # end def user

    @property
    @getattr_safe
    def username (self) :
        ### `username` is `property` not `Once_Property` to allow
        ### descendent to change redefine `username.setter` (to support `login`)
        ### `_auth_user_name` is `Once_Property` to improve performance
        return self._auth_user_name
    # end def username

    @Once_Property
    def verbose (self) :
        return self.req_data.has_option ("verbose")
    # end def verbose

    @Once_Property
    def _auth_user_name (self) :
        result = self.http_server_authorized_user
        if result is None :
            result = self.rat_authorized_user
        if result is None :
            auth   = self.authorization
            result = auth and auth.username
        return result
    # end def _auth_user_name

    def cookie (self, name) :
        return self.cookies.get (name)
    # end def cookie

    def get_browser_locale_codes (self) :
        """Determines the user's locale from Accept-Language header."""
        languages = self.accept_languages
        supported = getattr (self.root, "languages", set ())
        if supported :
            locales   = list (l for l, p in languages if l in supported)
            if locales :
                return locales
        return getattr (self.root, "default_locale_code", "en")
    # end def get_browser_locale_codes

    def new_secure_cookie (self, data, ** kw) :
        token = GTW.RST.Signed_Token.Cookie (self, data, ** kw)
        return token.value
    # end def new_secure_cookie

    def secure_cookie (self, name, ttl_s = None) :
        cookie = self.cookies.get (name)
        if cookie :
            token = GTW.RST.Signed_Token.Cookie.recover \
                (self, cookie, ttl_s = ttl_s)
            if token :
                return token.data
            else :
                self.cookies_to_delete.add (name)
    # end def secure_cookie

    def use_language (self, langs) :
        self.lang = langs
        I18N.use (* langs)
    # end def use_language

Request = _RST_Request_ # end class

if __name__ != "__main__" :
    GTW.RST._Export ("Request")
### __END__ GTW.RST.Request
