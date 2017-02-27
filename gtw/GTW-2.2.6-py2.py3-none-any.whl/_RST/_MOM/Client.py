# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.RST.MOM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.RST.MOM.Client
#
# Purpose
#    Generic client for a RESTful Api as implemented by GTW.RST.MOM
#
# Revision Dates
#     6-Jan-2013 (CT) Creation
#     3-May-2013 (CT) Add `Requester.add_cookies`
#     3-May-2013 (CT) Add exception handler to `Resource._json`
#    13-Apr-2015 (CT) Use `TFL.json_dump.default`
#     6-May-2015 (CT) Use `TFL.json_dump.to_string`
#     8-Oct-2015 (CT) Change `__getattr__` to *not* handle `__XXX__`
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

import _GTW._RST._MOM

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL.Decorator           import getattr_safe
from   _TFL.pyk                 import pyk
from   _TFL.predicate           import callable

import _TFL._Meta.Object
import _TFL.json_dump

from   posixpath                import join as pp_join

import json
import requests

@pyk.adapt__bool__
class _Entity_ (TFL.Meta.Object) :
    """Base class for Object and Resource"""

    def __init__ (self, requester, result) :
        self._requester = requester
        self._result    = result
    # end def __init__

    @TFL.Meta.Once_Property
    @getattr_safe
    def _ad_name (self) :
        return "attributes_raw" if self._requester.raw else "attributes"
    # end def _ad_name

    @TFL.Meta.Once_Property
    @getattr_safe
    def _attrs (self) :
        json = self._json
        if json :
            return dict (json.get (self._ad_name) or {})
        return {}
    # end def _attrs

    @TFL.Meta.Once_Property
    @getattr_safe
    def _attrs_orig (self) :
        json = self._json
        if json :
            return json.get (self._ad_name, {})
        return {}
    # end def _attrs_orig

    @property
    @getattr_safe
    def _changed_p (self) :
        return self._attrs != self._attrs_orig
    # end def _changed_p

    @TFL.Meta.Once_Property
    @getattr_safe
    def _entries (self) :
        json = self._json
        if json :
            entries = json.get ("entries", [])
            if entries :
                def gen (requester, entries) :
                    for e in entries :
                        if isinstance (e, dict) :
                            yield self._wrap_dict (requester, e)
                        else :
                            yield requester.get (e)
                return list (gen (self._requester, entries))
        return []
    # end def _entries

    def PUT (self) :
        if self._changed_p :
            cargo = TFL.json_dump.to_string \
                ( { self._ad_name : self._attrs
                  , "cid"         : self._json ["cid"]
                  }
                )
            return self._requester.put (self._url, data = cargo)
    # end def PUT

    def _wrap_dict (self, requester, result) :
        if self._ad_name in result :
            result = requester.Object (requester, result)
        elif "url" not in result :
            result = requester.Composite (requester, result)
        else :
            result = requester.get \
                (result ["url"], params = dict (closure = True))
        return result
    # end def _wrap_dict

    def __getattr__ (self, name) :
        attrs = self._attrs
        if attrs and name in attrs :
            result = attrs [name]
            if isinstance (result, dict) :
                result = self._wrap_dict (self._requester, result)
            setattr (self, name, result)
            return result
        raise AttributeError (name)
    # end def __getattr__

    def __getitem__ (self, key) :
        entries = self._entries
        if entries :
            return entries [key]
    # end def __getitem__

    def __iter__ (self) :
        entries = self._entries
        if entries :
            return iter (entries)
    # end def __iter__

    def __bool__ (self) :
        return bool (self._result)
    # end def __bool__

    def __setattr__ (self, name, value) :
        if name.startswith ("_") :
            self.__super.__setattr__ (name, value)
        else :
            attrs = self._attrs
            if attrs is not None :
                attrs [name] = value
            else :
                raise TypeError (name)
    # end def __setattr__

# end class _Entity_

class Composite (_Entity_) :
    """Encapsulate a composite attribute"""

    _url = None

    @TFL.Meta.Once_Property
    @getattr_safe
    def _json (self) :
        return self._result
    # end def _json

    @TFL.Meta.Once_Property
    @getattr_safe
    def _attrs (self) :
        return self._json
    # end def _attrs

# end class Composite

class Object (_Entity_) :
    """Encapsulate a nested object"""

    @TFL.Meta.Once_Property
    @getattr_safe
    def _json (self) :
        return self._result
    # end def _json

    @TFL.Meta.Once_Property
    @getattr_safe
    def _url (self) :
        return self._result.get ("url")
    # end def _url

# end class Object

class Resource (_Entity_) :
    """Encapsulate a RESTful resource"""

    @TFL.Meta.Once_Property
    @getattr_safe
    def _json (self) :
        result = self._result.json
        if callable (result) :
            try :
                result = result ()
            except Exception as exc :
                result = {}
        return result
    # end def _json

    @TFL.Meta.Once_Property
    @getattr_safe
    def _url (self) :
        json = self._json
        try :
            return json ["url"]
        except KeyError :
            return self._result.url
    # end def _url

# end class Resource

class Requester (TFL.Meta.Object) :
    """Wrapper for `requests`"""

    Composite = Composite
    Object    = Object
    Resource  = Resource

    class Wrapper (TFL.Meta.Object) :

        def __init__ (self, name, requester) :
            self.method    = getattr (requester.session, name)
            self.requester = requester
        # end def __init__

        def __call__ (self, path, * args , ** kw) :
            requester = self.requester
            url       = pp_join (requester.prefix, path.lstrip ("/"))
            return requester.Resource \
                (requester, self.method (url, * args, ** kw))
        # end def __call__

    # end class W

    def __init__ (self, prefix, raw = False, ** kw) :
        params = kw.pop ("params", {})
        if raw :
            params.update (raw = True)
        self.prefix  = prefix
        self.raw     = raw
        self.session = s = requests.Session ()
        if params :
            s.params.update (params)
        for k, v in pyk.iteritems (kw) :
            setattr (s, k, v)
        s.headers.update ({ "Content-Type" : "application/json" })
    # end def __init__

    def add_cookies (self, ** kw) :
        self.session.cookies.update (kw)
    # end def add_cookies

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        return self.Wrapper (name, self)
    # end def __getattr__

# end class Requester

if __name__ != "__main__" :
    GTW.RST.MOM._Export_Module ()
### __END__ GTW.RST.MOM.Client
