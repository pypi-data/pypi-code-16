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
#    GTW.RST.Response
#
# Purpose
#    Wrap and extend wsgi-specific Response class
#
# Revision Dates
#    20-Jun-2012 (CT) Creation
#     2-Mar-2013 (CT) Add `add_link`, change `__call__` to add link headers
#    28-Mar-2013 (CT) Add `_auto_headers` with `X-Frame-Options`
#     2-May-2013 (CT) Factor in `clear_cookie`, `set_cookie`, and
#                     `set_secure_cookie` (from GTW.RST.TOP.Response)
#     4-May-2013 (CT) Add `cookies_to_delete`
#     4-May-2013 (CT) Don't use werkzeug's `delete_cookie`
#    17-May-2013 (CT) Change `__call__` to sort link headers
#    26-Nov-2013 (CT) DRY `__call__`, `set_cookie`
#     4-Dec-2013 (CT) Add `httponly` to `set_secure_cookie`
#     9-Dec-2013 (CT) Change signature of `set_secure_cookie`
#                     (to that of `set_cookie`)
#     9-Dec-2013 (CT) Add `anti_csrf_token`
#    11-Feb-2014 (CT) Add `user`
#    13-Mar-2014 (CT) Add `add_rel_links`, `rel_{first,last,next,parent,prev}`
#    26-Jan-2015 (CT) Derive `_M_Response_` from `M_Auto_Update_Combined`,
#                     not `M_Auto_Combine_Sets`
#     8-Oct-2015 (CT) Change `__getattr__` to *not* handle `__XXX__`
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

from   _GTW                      import GTW
from   _TFL                      import TFL
from   _TFL.pyk                  import pyk

import _GTW._RST

from   _TFL._Meta.Once_Property  import Once_Property
from   _TFL.pyk                  import pyk

import _TFL._Meta.M_Auto_Update_Combined
import _TFL._Meta.M_Class
import _TFL._Meta.Object

from   posixpath                 import join as pp_join

import urllib

class _M_Response_ (TFL.Meta.M_Auto_Update_Combined) :
    """Meta class for Response"""

# end class _M_Response_

class _RST_Response_ \
          (TFL.Meta.BaM (TFL.Meta.Object, metaclass = _M_Response_)) :
    """Wrap and extend wsgi-specific Response class."""

    _auto_headers            = \
        { "X-Frame-Options" : "SAMEORIGIN"
        }

    _own_vars                = set \
        (("root", "_auto_headers", "_links", "_request", "_response"))

    _attrs_to_update_combine = ("_own_vars", )

    anti_csrf_token          = None

    def __init__ (self, _root, _request, * args, ** kw) :
        self.root          = _root
        self._auto_headers = dict (self._auto_headers) # allow instance changes
        self._links        = {}
        self._request      = _request
        self._response     = _root.HTTP.Response (* args, ** kw)
    # end def __init__

    def __call__ (self, * args, ** kw) :
        _request  = self._request
        _response = self._response
        for c in list (_request.cookies_to_delete) :
            self.clear_cookie (c)
        _request.cookies_to_delete.clear ()
        for k, v in pyk.iteritems (self._auto_headers) :
            _response.add_header (k, v)
        for rel, (value, kw) in sorted (pyk.iteritems (self._links)) :
            _response.add_header ("link", value, rel = rel, ** kw)
        return _response.__call__ (* args, ** kw)
    # end def __call__

    @Once_Property
    def rel_first (self) :
        return self._get_rel ("first")
    # end def rel_first

    @Once_Property
    def rel_first_child (self) :
        return self._get_rel ("first_child")
    # end def rel_first_child

    @Once_Property
    def rel_last (self) :
        return self._get_rel ("last")
    # end def rel_last

    @Once_Property
    def rel_last_child (self) :
        return self._get_rel ("last_child")
    # end def rel_last_child

    @Once_Property
    def rel_next (self) :
        return self._get_rel ("next")
    # end def rel_next

    @Once_Property
    def rel_parent (self) :
        return self._get_rel ("parent")
    # end def rel_parent

    @Once_Property
    def rel_prev (self) :
        return self._get_rel ("prev")
    # end def rel_prev

    @property
    def resource (self) :
        return self._request.resource
    # end def resource

    @property
    def user (self) :
        return self._request.user
    # end def user

    def add_link (self, rel, value, ** kw) :
        self._links [rel] = value, kw
    # end def add_link

    def add_rel_links (self, * names) :
        if not names :
            names = ("next", "prev", "parent", "first_child")
        for name in names :
            value = getattr (self, "rel_" + name, None)
            if value is not None :
                self.add_link (name, value)
    # end def add_rel_links

    def clear_cookie (self, name, ** kw) :
        ### Don't use werkzeug's `delete_cookie`: sends `max_age = 0`
        self._response.set_cookie (name, "", max_age = -1, ** kw)
    # end def clear_cookie

    def set_cookie (self, name, value = "", ** kw) :
        _request  = self._request
        _request.cookies_to_delete.discard (name)
        if isinstance (value, pyk.text_type) :
            value = value.encode (_request.cookie_encoding)
        return self._response.set_cookie (name, value, ** kw)
    # end def set_cookie

    def set_secure_cookie (self, name, value = "", ** kw) :
        request = self._request
        kw.setdefault ("httponly", True)
        if request.is_secure :
            kw ["secure"] = True
        self.set_cookie (name, value, ** kw)
        return value
    # end def set_secure_cookie

    def _get_rel (self, name) :
        try :
            result = getattr (self.resource._effective, name)
        except AttributeError :
            pass
        else :
            if isinstance (result, dict) :
                ### use `result` as query parameters (url relative to resource)
               return self._response.encoded_url (** result)
            elif isinstance (result, pyk.string_types) :
                return result
            elif result is not None :
                return result.abs_href
    # end def _get_rel

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        if name not in self._own_vars :
            return getattr (self._response, name)
        raise AttributeError (name)
    # end def __getattr__

    def __setattr__ (self, name, value) :
        if name in self._own_vars :
            return self.__super.__setattr__ (name, value)
        else :
            return setattr  (self._response, name, value)
    # end def __setattr__

Response = _RST_Response_ # end class

if __name__ != "__main__" :
    GTW.RST._Export ("Response")
### __END__ GTW.RST.Response
