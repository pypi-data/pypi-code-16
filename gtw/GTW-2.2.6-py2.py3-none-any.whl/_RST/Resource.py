# -*- coding: utf-8 -*-
# Copyright (C) 2012-2017 Mag. Christian Tanzer All rights reserved
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
#    GTW.RST.Resource
#
# Purpose
#    Model a RESTful resource
#
# Revision Dates
#     8-Jun-2012 (CT) Creation
#    22-Jun-2012 (CT) Set `parent` in `_RST_Meta_.__call__` before `.__init__`
#    26-Jun-2012 (CT) Factor `_Dir_Base_`, add `Dir_V`
#    27-Jun-2012 (CT) Add empty `Leaf._get_child`
#    28-Jun-2012 (CT) Fix `url_template`, use `_response_dict`
#    28-Jun-2012 (CT) Use `request.verbose`
#     1-Jul-2012 (CT) Add `href_pat`, use it in `resource_from_href`
#     2-Jul-2012 (CT) Refactor `href_pat_frag`
#     2-Jul-2012 (CT) Change `resource_from_href` to ignore extension
#     3-Jul-2012 (CT) Use `TFL.Context.relaxed` as alternative to `.time_block`
#     5-Jul-2012 (CT) Add `_m_after__init__`
#     8-Jul-2012 (CT) Rename `template` to `page_template`,
#                     add Alias_Property `template`
#     9-Jul-2012 (CT) Factor `get_template`, add `HTTP_Method.template_name`
#     9-Jul-2012 (CT) Factor `_Dir_._get_child` to `_Dir_Base_`
#     9-Jul-2012 (CT) Add `Dir_V._get_child`, use `Dir_V._entry_type_map`
#     9-Jul-2012 (CT) Add `Dir_V.template_iter`
#     9-Jul-2012 (CT) Add and use `Dir_V._greet_entry`
#    17-Jul-2012 (CT) Fix `Root.href_pat`, `.resource_from_href`
#    18-Jul-2012 (CT) Move `add_entries` from `_Dir_` to `_Dir_Base_`
#    19-Jul-2012 (CT) Add `self.entries` to `_Dir_Base_._get_child` to
#                     trigger necessary updates
#    19-Jul-2012 (CT) Add `_change_infos`, `LET` it in `wsgi_app`
#    20-Jul-2012 (CT) Add `Alias`, factor `_get_method`
#    23-Jul-2012 (CT) Add argument `response` to `_handle_method`,
#                     `_handle_method_context`, `_http_response`, and
#                     `_http_response_error`
#    24-Jul-2012 (CT) Add `Root.Cacher`
#    24-Jul-2012 (CT) Add `lang_pat`, `_request_href`
#    25-Jul-2012 (CT) Remove obsolete `base` and `file_stem`
#    25-Jul-2012 (CT) Fix `Alias`: delegate `page_template_name`,
#                     `template_name` to `target`
#    30-Jul-2012 (CT) Add properties `Auth_Required` and `permission`,
#                     factor `_http_response_need_auth`
#     1-Aug-2012 (CT) Fix cold-start behavior of `Root.resource_from_href`
#     4-Aug-2012 (MG) `Alias`: add `top` to the `_parent_attr` set
#     6-Aug-2012 (CT) Add `blackboard` to `_handle_method_context`
#     6-Aug-2012 (CT) Add `get_etag`, `get_last_modified`, `rst_etag`, and
#                     `skip_etag`
#     7-Aug-2012 (CT) Factor `own_links` and `own_links_transitive` in here
#     8-Aug-2012 (MG) Use a dict for `blackboard`
#    10-Aug-2012 (CT) Define `name` as `property`, split off `ext` there
#    10-Aug-2012 (CT) Rename `Permission.rank` to `_rank`
#    16-Aug-2012 (MG) Guard against empty languages in `_request_href`
#    24-Aug-2012 (CT) Set `Raiser.skip_etag` to `True`
#    24-Aug-2012 (CT) Change `wsgi_app` to `send_error_email` for `Server_Error`
#    24-Aug-2012 (CT) Change `send_error_email` to display `req_data`, too
#    26-Sep-2012 (CT) Add argument `resource` to `_http_response`
#                     (move some code from `_http_response` to `wsgi_app`)
#    26-Sep-2012 (CT) Add `show_in_nav`
#    28-Sep-2012 (CT) Protect `%` in `fmt` of `_http_response`
#     4-Oct-2012 (CT) Change `_Dir_Base_.GET` to use `request.brief`
#     5-Oct-2012 (CT) Fix `_Base_.allow_user` (`self.GET`, not `"GET"`)
#    18-Oct-2012 (CT) Factor `E_Type_Desc`, `ET_Map` in here from `.TOP.Root`
#    20-Oct-2012 (CT) Add `E_Type_Desc.type_name`, `_find_missing`, `._prop_map`
#     7-Dec-2012 (CT) Let `request` and `user` in `_http_response`
#    11-Dec-2012 (CT) Factor `_http_response_context` to let `scope.user`, too
#    12-Dec-2012 (CT) Change `_http_response_context` to always `LET`
#    14-Dec-2012 (CT) Add `child_permission_map`
#    14-Dec-2012 (CT) Auto-instantiate permissions in `_get_permissions`
#    25-Apr-2013 (CT) Add `postconditions`, `check_postconditions`,
#                     `commit_scope`
#    25-Apr-2013 (CT) Add `child_postconditions_map`
#    30-Apr-2013 (CT) Don't check `postconditions` for superuser
#     2-May-2013 (CT) Make `hash_fct` a configurable parameter
#     2-May-2013 (CT) Factor `b64_encoded`
#     3-May-2013 (CT) Fix call of `Status.Method_Not_Allowed`
#     3-May-2013 (CT) Add `auth_required` and use in `allow_method`
#     6-May-2013 (CT) Add optional argument `xtra` to `send_error_email`
#     6-May-2013 (CT) Add and use `_password_elider`, `_error_email_cleaner`
#    31-May-2013 (CT) Add `HTTP method` to `send_error_email`
#    31-May-2013 (CT) Add guard against unknown HTTP method to `allow_method`
#    14-Jun-2013 (CT) Add guard against unsupported `method` to `allow_method`
#    23-Aug-2013 (CT) Add `or False` to property `auth_required`
#    29-Aug-2013 (CT) Don't pass `exc` to `Internal_Server_Error` in
#                     `_http_response_error` (shows up in webbrowser otherwise)
#    18-Nov-2013 (CT) Change default `input_encoding` to `utf-8`
#     5-Dec-2013 (CT) Make `tbi` optional argument of `send_error_email`
#     9-Dec-2013 (CT) Add `request.environ` to `send_error_email`
#    10-Dec-2013 (CT) Add `s_domain` and `secure_url`
#    11-Dec-2013 (CT) Add `sane_referrer`
#    10-Jan-2014 (CT) Change `send_email` to encode arguments to `logging`
#    16-Jan-2014 (CT) Fix `Alias.SUPPORTED_METHODS`
#    20-Jan-2014 (CT) Show `url_x`, not `url`, in `time_block`
#    22-Jan-2014 (CT) Add `empty_template` to gracefully support empty `Dir`
#    22-Jan-2014 (CT) Change `Root._http_response_context` to set
#                     `scope.user` to `.person`, if any
#    24-Jan-2014 (CT) Add `a_attr_dict`
#    24-Jan-2014 (CT) Add `A_Link`
#    29-Jan-2014 (CT) Add stub for `_add_other_entries`
#    17-Feb-2014 (CT) Add exception handler to `send_error_email`
#    17-Feb-2014 (CT) Use `pyk.decoded` in `send_error_email`
#    17-Feb-2014 (CT) Use `pyk.encoded` instead of home-grown code
#     7-Mar-2014 (CT) Change `Root._http_response_context` to NOT set
#                     `scope.user` to `.person`, i.e., set it to `account`
#    12-Mar-2014 (CT) Add `Alias.independent_permissions_p`
#    13-Mar-2014 (CT) Show `url`, not `url_x`, in `time_block`
#    13-Mar-2014 (CT) Call `_handle_method_context` in `_http_response`,
#                     not in `_handle_method`;
#                     redefine `Alias._handle_method_context` to delegate
#    14-Mar-2014 (CT) Add alias property `proper_entries`
#    14-Mar-2014 (CT) Add `response` to `_http_response_context`
#     7-Apr-2014 (CT) Add support for `Access-Control-Allow-Origin`
#    17-Apr-2014 (CT) Add `entry_map`
#    19-Apr-2014 (CT) Catch `Not_Found` in `resource_from_href`
#                     (factor `_resource_from_href`)
#    29-Apr-2014 (CT) Add `Root._old_cids`
#    30-Apr-2014 (CT) Move `_new_child` from `Dir_V` to `_Dir_Base_`
#    12-Oct-2014 (CT) Use `TFL.Secure_Hash`
#    20-Jan-2015 (CT) Add `** kw` to `allow_method`, `allow_user`
#    20-Jan-2015 (CT) Add `allow_child`
#    30-Jan-2015 (CT) Add `_RST_Base_.target` returning `self`
#    10-Feb-2015 (CT) Add property `RST_Types` to ease introspection
#    17-Mar-2015 (CT) Add `_objects_cache`
#    20-Mar-2015 (CT) Use `request.language`
#    20-Mar-2015 (CT) Change `lang_pat` to `property`
#    24-Mar-2015 (CT) Call `I18N.use` in `_http_response_context`
#    24-Mar-2015 (CT) Use `_http_response_context` for error renderings, too
#    21-Sep-2015 (CT) Change `auth_required` to consider
#                     `permission.auth_required`
#    21-Sep-2015 (CT) Change `allow_method` to consider `p.auth_required`
#     8-Oct-2015 (CT) Change `__getattr__` to *not* handle `__XXX__`
#    20-Oct-2015 (CT) Run `logging` arguments through `pyk.as_str`
#    21-Oct-2015 (CT) Print `request.body`, not `request.data`,
#                     in `send_error_email`
#    17-Nov-2015 (CT) Add `dynamic_p` and `static_p`
#    17-Nov-2015 (CT) Remove `isinstance` guard from `_Dir_.entries_transitive`
#    18-Nov-2015 (CT) Split `href` into `href_dynamic` and `href_static`
#                     + Split `abs_href` into `abs_href_dynamic` and
#                       `abs_href_static`
#                     + Add `static_page_suffix`
#    18-Nov-2015 (CT) Add  `_Base_.static_pages`, `.static_roots`
#    18-Nov-2015 (CT) Redefine `A_Link.permalink`
#     3-Dec-2015 (CT) Consider `dynamic_p`, `static_p` in `template_iter`
#    19-Dec-2016 (CT) Move `LET` of `user` to `wsgi_app`
#                     + Makes `user` available in `_http_response_context`
#    19-Dec-2016 (CT) Add info about resource to `__getattr__` error
#     8-Feb-2017 (CT) Make argument `nav_page` of `show_in_nav` optional
#     8-Feb-2017 (CT) Change `show_in_nav` to check `short_title`
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

import _GTW._RST.import_RST
import _GTW._RST.R_Map
import _GTW._RST.Template_Media_Cache

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL._Meta.Property      import Alias_Property
from   _TFL.Decorator           import getattr_safe
from   _TFL.Filename            import Filename
from   _TFL.I18N                import _, _T, _Tn
from   _TFL.predicate           import callable, first, uniq
from   _TFL.pyk                 import pyk
from   _TFL.Regexp              import \
    Regexp, Re_Replacer, Multi_Re_Replacer, re

import _TFL._Meta.M_Class
import _TFL._Meta.Object
import _TFL.Accessor
import _TFL.Context
import _TFL.defaultdict
import _TFL.Environment
import _TFL.Record
import _TFL.User_Config

from   posixpath import \
    ( join          as pp_join
    , normpath      as pp_norm
    , split         as pp_split
    , splitext      as pp_splitext
    , commonprefix
    )

import datetime
import base64
import logging
import re
import sys
import time
import traceback

_password_elider = Re_Replacer \
    ( "'password' *: *'[^']+'"
    , "'password' : '...'"
    )
_error_email_cleaner = Multi_Re_Replacer (_password_elider)

class _RST_Meta_ (TFL.Meta.M_Class) :

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        cls._SUPPORTED_METHODS = sms = {}
        for k in GTW.RST.HTTP_Method.Table :
            v = getattr (cls, k, None)
            if callable (v) :
                sms [k] = v
                tn = getattr (v, "template_name", None)
                if isinstance (tn, pyk.string_types) : ### beware of `property`
                    cls._template_names.add (tn)
        for k in ("page_template_name", "dir_template_name") :
            tn = dct.get (k)
            if isinstance (tn, pyk.string_types) : ### beware of `property`
                cls._template_names.add (tn)
        cls._m_after__init__ (name, bases, dct)
    # end def __init__

    def __call__ (cls, * args, ** kw) :
        parent = kw.pop ("parent", None)
        if cls._needs_parent and parent is None :
            return (cls, args, kw)
        ### set `result.parent` before calling `result.__init__` so
        ### that `result.__getattr__` can use it right from the beginning
        result = cls.__new__   (cls, * args, ** kw)
        result.parent = parent
        result.__init__        (* args, ** kw)
        result._after__init__  (kw)
        if parent :
            try :
                greet = parent._greet_entry
            except AttributeError :
                pass
            else :
                if greet is not None :
                    greet (result)
        return result
    # end def __call__

# end class _RST_Meta_

class _RST_Base_ (TFL.Meta.BaM (TFL.Meta.Object, metaclass = _RST_Meta_)) :
    """Base class for RESTful resources."""

    _real_name                 = "_Base_"

    Status                     = GTW.RST.HTTP_Status
    Auth_Required              = Status.Unauthorized

    b64_altchars               = b"_-"
    child_permission_map       = {}
    child_postconditions_map   = {}
    cls_postconditions         = ()
    ext                        = None
    hidden                     = False
    implicit                   = False
    pid                        = None
    session_ttl_name           = "edit_session_ttl"
    static_page_suffix         = ""
    template                   = Alias_Property ("page_template")
    template_name              = Alias_Property ("page_template_name")

    _auth_required             = False
    _greet_entry               = None
    _needs_parent              = True
    _r_permission              = None             ### read  permission
    _w_permission              = None             ### write permission
    _page_template             = None
    _postconditions            = ()
    _scheme_pat                = TFL.Regexp ("^https?://")
    _template_names            = set ()

    DELETE                     = None             ### redefine if necessary
    GET                        = GTW.RST.GET      ### needs    to be redefined
    HEAD                       = GTW.RST.HEAD     ### needs    to be redefined
    OPTIONS                    = GTW.RST.OPTIONS  ### unlikely to be redefined
    POST                       = None             ### redefine if necessary
    PUT                        = None             ### redefine if necessary

    def __init__ (self, ** kw) :
        parent   = self.parent                    ### set by meta class
        self._kw = dict (kw)
        self.pop_to_self \
            ( kw
            , "auth_required"
            , "login_required"             ### just for backwards compatibility
            , "exclude_robots", "postconditions"
            , "r_permission", "w_permission"
            , prefix = "_"
            )
        encoding = kw.get ("input_encoding") or \
            getattr (parent, "input_encoding", Root.input_encoding)
        for k, v in pyk.iteritems (kw) :
            if isinstance (v, pyk.byte_types) :
                v = pyk.decoded (v, encoding)
            try :
                setattr (self, k, v)
            except AttributeError (exc) :
                print (self.href_dynamic or "/{ROOT}", k, v, "\n   ", exc)
        if self.implicit :
            self.hidden = True
        if parent :
            name = self.name
            if (not self.permission) and name in parent.child_permission_map :
                self.permission = parent.child_permission_map [name]
            if (   (not self._postconditions)
               and name in parent.child_postconditions_map
               ) :
                self._postconditions = tuple \
                    (parent.child_postconditions_map [name])
    # end def __init__

    def _after__init__ (self, kw) :
        ### called by meta class after `__init__` has finished
        ### redefine as necessary
        self._orig_kw = dict (kw)
        top = self.top
        if not self.implicit :
            href = self.href_dynamic
            pid  = self.pid
            if href is not None :
                Table = top.Table
                Table [href] = self
                try :
                    perma = self.permalink.lstrip ("/")
                except Exception :
                    pass
                else :
                    if perma != href :
                        if (  perma not in Table
                           or Table [perma].href_dynamic == href
                           ) :
                            Table [perma] = self
            if pid is not None :
                setattr (top.SC, pid, self)
        if top.dynamic_p or self.static_p :
            for k in ("page_template_name", "dir_template_name") :
                tn = getattr (self, k, None)
                if tn :
                    top._template_names.add (tn)
    # end def _after__init__

    @classmethod
    @getattr_safe
    def _m_after__init__ (cls, name, bases, dct) :
        """Called by metaclass's __init__: redefine as necessary."""
        pass
    # end def _m_after__init__

    @property
    @getattr_safe
    def a_attr_dict (self) :
        """Dictionary with attributes applicable to an `<a>` element
           referring to this resource.
        """
        return dict (href = self.abs_href)
    # end def a_attr_dict

    @property
    @getattr_safe
    def abs_href (self) :
        return \
            (    self.abs_href_dynamic
            if   self.top.dynamic_p
            else self.abs_href_static
            )
    # end def href

    @Once_Property
    @getattr_safe
    def abs_href_dynamic (self) :
        result = self.href_dynamic
        if not result.startswith ("/") :
            return "/%s" % (result, )
        return result
    # end def abs_href_dynamic

    @Once_Property
    @getattr_safe
    def abs_href_static (self) :
        result = self.href_static
        if not result.startswith ("/") :
            return "/%s" % (result, )
        return result
    # end def abs_href_static

    @Once_Property
    @getattr_safe
    def account_manager (self) :
        scope = self.top.scope
        if scope :
            return scope.GTW.OMP.Auth.Account
    # end def account_manager

    @Once_Property
    @getattr_safe
    def auth_required (self) :
        ### if a parent requires authorization, all children do too
        ### (even if they claim otherwise!)
        parent     = self.parent
        permission = self.permission
        return \
            (  self._auth_required
            or (permission and permission.auth_required)
            or (parent     and parent.auth_required)
            or False
            )
    # end def auth_required

    @property
    @getattr_safe
    def change_info (self) :
        ### Redefine as necessary
        pass
    # end def change_info

    @property
    @getattr_safe
    def email_from (self) :
        result = self._email_from
        if result is None :
            result = self.webmaster
            if isinstance (result, tuple) :
                result = "%s <%s>" % (result [1], result [0])
            self._email_from = result
        return result
    # end def email_from

    @email_from.setter
    def email_from (self, value) :
        self._email_from = value
    # end def email_from

    @property
    @getattr_safe
    def entries (self) :
        return ()
    # end def entries

    @property
    @getattr_safe
    def entries_a_link (self) :
        return tuple (e for e in self.entries if isinstance (e, A_Link))
    # end def entries_a_link

    @property
    @getattr_safe
    def entries_transitive (self) :
        return ()
    # end def entries_transitive

    @Once_Property
    @getattr_safe
    def exclude_robots (self) :
        return self.r_permissions or self.hidden or self._exclude_robots
    # end def exclude_robots

    @property
    @getattr_safe
    def href (self) :
        return self.href_dynamic if self.top.dynamic_p else self.href_static
    # end def href

    @Once_Property
    @getattr_safe
    def href_dynamic (self) :
        pp   = self.parent.href_dynamic if self.parent else self.prefix
        href = pp_join (pp, self.name)
        if href :
            return pp_norm (href)
        return ""
    # end def href_dynamic

    @Once_Property
    @getattr_safe
    def href_static (self) :
        return "".join ((self.href_dynamic, self.static_page_suffix))
    # end def href_static

    @property
    @getattr_safe
    def href_pat_frag (self) :
        pass ### redefine as necessary
    # end def href_pat_frag

    @Once_Property
    @getattr_safe
    def injected_templates (self) :
        ### redefine as necessary
        return set ()
    # end def injected_templates

    @property
    @getattr_safe
    def name (self) :
        return self._name
    # end def name

    @name.setter
    def name (self, value) :
        self._name, self.ext = pp_splitext (value)
    # end def name

    @property
    @getattr_safe
    def own_links (self) :
        return iter (self.entries)
    # end def own_links

    @property
    @getattr_safe
    def own_links_transitive (self) :
        for e in self.own_links :
            yield e
            if isinstance (e, _Dir_) :
                for ee in e.own_links_transitive :
                    yield ee
    # end def own_links_transitive

    @property
    @getattr_safe
    def page_template (self) :
        if self._page_template is None :
            t_name = getattr (self, "page_template_name", None)
            if t_name :
                self._page_template = self.get_template (t_name)
        return self._page_template
    # end def page_template

    @page_template.setter
    def page_template (self, value) :
        T = self.Templateer
        self._page_template = None
        if isinstance (value, pyk.string_types) :
            self.page_template_name = value
        elif T is not None and not isinstance (value, T.Template_Type) :
            self.page_template_name = value.name
        else :
            self.page_template_name = value.name
            self._page_template     = value
    # end def page_template

    @property
    @getattr_safe
    def permalink (self) :
        return self.abs_href
    # end def permalink

    @property
    @getattr_safe
    def permission (self) :
        if self._r_permission :
            return self._r_permission
        else :
            return self._w_permission
    # end def permission

    @permission.setter
    def permission (self, value) :
        self._r_permission = self._w_permission = value
    # end def permission

    @Once_Property
    @getattr_safe
    def postconditions (self) :
        def _gen (self) :
            for p in self.cls_postconditions :
                yield p
            for p in self._postconditions :
                yield p
            if self.parent :
                for p in self.parent.postconditions :
                    yield p
        return list (uniq (_gen (self)))
    # end def postconditions

    @Once_Property
    @getattr_safe
    def r_permissions (self) :
        return sorted \
            (self._get_permissions ("r_permission"), key = TFL.Getter._rank)
    # end def r_permissions

    @Once_Property
    @getattr_safe
    def RST_Types (self) :
        def _gen (self) :
            seen = set ()
            for e in self.entries_transitive :
                T = e.__class__
                if T not in seen :
                    seen.add (T)
                    yield T
        return tuple (_gen (self))
    # end def RST_Types

    @Once_Property
    @getattr_safe
    def secure_url (self) :
        return self._get_secure_url (self.abs_href)
    # end def secure_url

    @Once_Property
    @getattr_safe
    def session_ttl (self) :
        result = getattr (self.top, self.session_ttl_name)
        if not isinstance (result, datetime.timedelta) :
            result = datetime.timedelta (seconds = result)
        return result
    # end def session_ttl

    @Once_Property
    @getattr_safe
    def session_ttl_s (self) :
        ttl = self.session_ttl
        try :
            return ttl.total_seconds ()
        except AttributeError :
            return (ttl.days * 86400 + ttl.seconds)
    # end def session_ttl_s

    @property
    @getattr_safe
    def static_pages (self) :
        for e in self.entries_transitive :
            if e.static_p and not e.auth_required :
                yield e
    # end def static_pages

    @property
    @getattr_safe
    def static_roots (self) :
        for p in self.static_pages :
            if isinstance (p, _Dir_) and not (p.parent and p.parent.static_p) :
                yield p
    # end def static_roots

    @property
    @getattr_safe
    def SUPPORTED_METHODS (self) :
        return self._SUPPORTED_METHODS
    # end def SUPPORTED_METHODS

    @Once_Property
    @getattr_safe
    def target (self) :
        return self
    # end def target

    @property
    @getattr_safe
    def Type (self) :
        return self.__class__.__name__
    # end def Type

    @Once_Property
    @getattr_safe
    def w_permissions (self) :
        return sorted \
            (self._get_permissions ("w_permission"), key = TFL.Getter._rank)
    # end def w_permissions

    @Once_Property
    @getattr_safe
    def _effective (self) :
        return self
    # end def _effective

    @property
    def _login_required (self) :
        ### just for backwards compatibility
        return self._auth_required
    # end def _login_required

    @_login_required.setter
    def _login_required (self, value) :
        ### just for backwards compatibility
        self._auth_required = value
    # end def _login_required

    def allow_child (self, name, user, obj, ** kw) :
        """Returns True if child `name` allows `obj` for `user`."""
        try :
            p = self.child_permission_map [name]
        except KeyError :
            return True
        else :
            return p.instance (user, self, obj = obj, ** kw)
    # end def allow_child

    def allow_method (self, method, user, ** kw) :
        """Returns True if `self` allows `method` for `user`."""
        if self.auth_required and not \
               (user and user.authenticated and user.active) :
            return False
        if isinstance (method, pyk.string_types) :
            try :
                method = GTW.RST.HTTP_Method.Table [method]
            except KeyError :
                raise self.Status.Method_Not_Allowed \
                    ( _T ("Unknown HTTP method `%s` requested") % (method, )
                    , valid_methods = sorted (self.SUPPORTED_METHODS)
                    )
        if method and not (user and user.superuser) :
            pn = method.mode + "_permissions"
            permissions = getattr (self, pn)
            for p in permissions :
                if not p (user, self, ** kw) :
                    if p.auth_required :
                        return False
                    else :
                        raise self.Status.Forbidden \
                            (p.message (user, self, ** kw))
        return True
    # end def allow_method

    def allow_user (self, user, ** kw) :
        return self.allow_method (self.GET, user, ** kw)
    # end def allow_user

    def check_postconditions (self, request, response) :
        if not self.postconditions_checked :
            self.postconditions_checked = True
            for p in self.postconditions :
                if isinstance (p, TFL.Meta.Object.__class__) :
                    p = p ()
                p (self, request, response)
    # end def check_postconditions

    def commit_scope (self, request, response) :
        self.check_postconditions (request, response)
        self.top.scope.commit     ()
    # end def commit_scope

    def get_etag (self, request) :
        ci = self.change_info
        result = list \
            (  x for x in (self.rst_etag, request.language, request.username)
            if x
            )
        if ci :
            ci_etag = getattr (ci, "etag", None)
            if ci_etag :
                result.append (ci_etag)
        if result :
            return self.hash_fct (result).b64digest ()
    # end def get_etag

    def get_last_modified (self, request) :
        ci = self.change_info
        if ci :
            return getattr (ci, "last_modified", None)
    # end def get_last_modified

    def get_template (self, template_name, injected = None) :
        if self.Templateer is not None :
            if injected is None :
                injected = self.injected_templates
            return self.Templateer.get_template (template_name, injected)
    # end def get_template

    def sane_referrer (self, request) :
        result = self._scheme_pat.sub \
            (request.scheme + "://", request.referrer or "/", 1)
        return result
    # end def sane_referrer

    def send_error_email (self, request, exc, tbi = None, xtra = None) :
        from _TFL.formatted_repr import formatted_repr as formatted
        try :
            email     = self.email_from
            enc       = self.encoding
            headers   = request.headers
            message   = \
                ( "HTTP method: %s"
                  "\n\nHeaders:\n%s"
                  "\n\nBody:\n  %s"
                  "\n\nRequest data:\n%s"
                  "\n\nRequest environment:\n%s"
                %   ( request.method
                    , formatted (dict (headers.items ()), 1)
                    , formatted (request.body,            1)
                    , formatted (request.req_data.data,   1)
                    , formatted (request.environ,         1)
                    )
                )
            if tbi :
                message = "\n\n=====\n\n".join \
                    ((message, pyk.decoded (tbi, enc)))
            if xtra :
                message = "\n\n#####\n\n".join \
                    ((message, pyk.decoded (xtra, enc)))
            message = _error_email_cleaner (message)
            if not self.Templateer :
                pyk.fprint ("Exception:", exc)
                pyk.fprint ("Request path", request.path)
                pyk.fprint ("Email", email)
                pyk.fprint (message)
                pyk.fprint (request.body)
                pyk.fprint (request.environ)
            else :
                kw = {}
                if self.DEBUG :
                    from _TFL.SMTP import SMTP_Logger
                    kw = dict (smtp = SMTP_Logger ())
                self.send_email \
                    ( self.error_email_template
                    , email_from    = email
                    , email_to      = email
                    , email_subject = ("Error: %s") % (exc, )
                    , message       = message
                    , NAV           = self.top
                    , page          = self
                    , request       = request
                    , ** kw
                    )
        except Exception as xxx :
            logging.exception \
                ( pyk.as_str ("Exception `%r` during `send_error_email`", enc)
                , pyk.as_str (xxx, enc)
                )
    # end def send_error_email

    def send_email (self, template, ** context) :
        email_from = context.get ("email_from")
        if not email_from :
            context ["email_from"] = email_from = self.email_from
        enc  = self.encoding
        smtp = context.pop ("smtp", self.smtp)
        text = self.top.Templateer.render (template, context)
        try :
            smtp (text)
        except Exception as exc :
            logging.exception \
                ( pyk.as_str
                    ( "Exception: %s"
                      "\n  When trying to send email from %s to %s"
                      "\n  %s"
                    , enc
                    )
                , pyk.as_str (exc.__class__.__name__, enc)
                , pyk.as_str (email_from, enc)
                , pyk.as_str (context.get ("email_to", "<Unkown>"), enc)
                , pyk.as_str (text, enc)
                )
            try :
                kw = dict \
                    ( context
                    , email_from    = self.email_from
                    , email_to      = self.email_from
                    , email_subject =
                        ( "Error when trying to send email from %s: %s"
                        % (email_from, exc)
                        )
                    , message       = text
                    , NAV           = self.top
                    , page          = self
                    )
                self.send_email (self.error_email_template, ** kw)
            except Exception :
                pass
    # end def send_email

    def show_in_nav (self, nav_page = None) :
        return (not self.hidden) and getattr (self, "short_title", None)
    # end def show_in_nav

    def template_iter (self) :
        if self.top.dynamic_p or self.static_p :
            t = self.page_template
            if t :
                yield t
    # end def template_iter

    def _add_other_entries (self) :
        pass ### just as grounding for __super calls
    # end def _add_other_entries

    def _get_method (self, name) :
        return getattr (self, name)
    # end def _get_method

    def _get_permissions (self, name) :
        def _gen (self, name) :
            p = getattr (self, "_" + name, None)
            if p is not None :
                yield getattr (p, "instance", p)
            if self.parent :
                pps = getattr (self.parent, name + "s", ())
                for p in pps or () :
                    yield p
        return uniq (_gen (self, name))
    # end def _get_permissions

    def _get_secure_url (self, href) :
        s_domain = self.s_domain
        if s_domain :
            return "".join (("https://", s_domain, href))
    # end def _get_secure_url

    def _get_user (self, username) :
        result = None
        if username :
            try :
                result = self.account_manager.query (name = username).one ()
            except IndexError :
                pass
            except Exception as exc :
                enc  = self.encoding
                logging.error \
                    ( pyk.as_str
                        ("Exception %s when trying to determine the user")
                    , pyk.as_str (exc, enc)
                    )
        return result
    # end def _get_user

    def _handle_method (self, method, request, response) :
        return method (self, request, response)
    # end def _handle_method

    @TFL.Contextmanager
    def _handle_method_context (self, method, request, response) :
        ### Redefine to setup context for handling `method` for `request`,
        ### for instance, `self.change_info`
        user = request.user
        with self.LET (postconditions_checked = (user and user.superuser)) :
            T = self.Templateer
            if T :
                with T.GTW.LET (blackboard = dict ()) :
                    yield
            else :
                yield
    # end def _handle_method_context

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        if self.parent is not None :
            try :
                return getattr (self.parent, name)
            except AttributeError :
                pass ### following `raise` provides additional context info
        raise AttributeError \
            ("Resource %s has not attribute named %s" % (self, name))
    # end def __getattr__

    def __repr__ (self) :
        return "<%s %s: %s>" % (self.Type, self.name, self.abs_href)
    # end def __repr__

_Base_ = _RST_Base_ # end class

class RST_Leaf (_Base_) :
    """Base class for RESTful leaves."""

    _real_name                 = "Leaf"

    static_page_suffix         = ".html"

    def _get_child (self, child, * grandchildren) :
        pass
    # end def _get_child

Leaf = RST_Leaf # end class

_Ancestor = Leaf

class RST_Alias (_Ancestor) :
    """Alias for another RESTful resource"""

    _real_name                 = "Alias"

    _target_href               = None
    _target_page               = None
    _parent_attr               = set (("prefix", "top"))

    independent_permissions_p  = False

    page_template_name         = property \
        ( lambda s    : s.target.page_template_name
        , lambda s, v : setattr (s.target, "page_template_name", v)
        )
    template_name              = property \
        ( lambda s    : s.target.template_name
        , lambda s, v : setattr (s.target, "template_name", v)
        )

    def __init__ (self, ** kw) :
        self.target = kw.pop  ("target")
        self.__super.__init__ (** kw)
    # end def __init__

    @property
    @getattr_safe
    def SUPPORTED_METHODS (self) :
        target = self.target
        if target :
            result = target.SUPPORTED_METHODS
        else :
            result = self.__super.SUPPORTED_METHODS
        return result
    # end def SUPPORTED_METHODS

    @property
    @getattr_safe
    def target (self) :
        result = self._target_page
        t_href = self._target_href
        if result is None :
            if t_href :
                result = self._target_page = self.top.resource_from_href \
                    (t_href)
        if result is not None and t_href is None :
            self._target_href = result.href
        return result
    # end def target

    @target.setter
    def target (self, value) :
        if isinstance (value, pyk.string_types) :
            self._target_href = value
            self._target_page = None
        else :
            self._target_href = value.href
            self._target_page = value
    # end def target

    def allow_method (self, method, user) :
        if self.independent_permissions_p :
            return self.__super.allow_method (method, user)
        else :
            return (not self.target) or self.target.allow_method (method, user)
    # end def allow_method

    def _get_method (self, name) :
        target = self.target
        if target :
            return target._get_method (name)
    # end def _get_method

    def _handle_method (self, method, request, response) :
        target = self.target
        if target :
            request.original_resource = self
            return target._handle_method (method, request, response)
    # end def _handle_method

    @TFL.Contextmanager
    def _handle_method_context (self, method, request, response) :
        target = self.target
        if target :
            hmc = target._handle_method_context
        else :
            hmc = self.__super._handle_method_context
        with hmc (method, request, response) :
            yield
    # end def _handle_method_context

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        if name not in self._parent_attr :
            target = self.target
            if target is not None :
                return getattr (target, name)
        return self.__super.__getattr__ (name)
    # end def __getattr__

Alias = RST_Alias # end class

_Ancestor = Leaf

class RST_A_Link (_Ancestor) :
    """A link to another URL"""

    _real_name = "A_Link"

    download   = False

    def __init__ (self, ** kw) :
        self.target_url = kw.pop ("target_url")
        self.__super.__init__ (** kw)
    # end def __init__

    @property
    @getattr_safe
    def a_attr_dict (self) :
        result = self.__super.a_attr_dict
        result.update (href = self.target_url)
        download = self.download
        if download :
            dl_target = download \
                if isinstance (download, pyk.string_types) else self.name
            result.update (download = dl_target)
        return result
    # end def a_attr_dict

    @property
    @getattr_safe
    def permalink (self) :
        return self.target_url
    # end def permalink

    def _handle_method (self, method, request, response) :
        raise self.top.Status.See_Other (self.target_url)
    # end def _handle_method

A_Link = RST_A_Link # end class

_Ancestor = _Base_

class _RST_Dir_Base_ (_Ancestor) :
    """Base class for RESTful directories (resources with children)."""

    _real_name                 = "_Dir_Base_"

    _dir_template              = None
    _entries                   = ()
    _href_pat_frag             = None

    empty_template_name        = "empty_dir"
    proper_entries             = Alias_Property ("entries")

    template                   = Alias_Property ("dir_template")
    template_name              = Alias_Property ("dir_template_name")

    class RST__Dir_Base__GET (_Ancestor.GET) :

        _real_name             = "GET"

        def _response_body (self, resource, request, response) :
            result = self._response_dict (resource, request, response)
            add    = result ["entries"].append
            for e in self._resource_entries (resource, request, response) :
                add (self._response_entry (resource, request, response, e))
            return result
        # end def _response_body

        def _response_dict (self, resource, request, response, ** kw) :
            result = dict \
                ( entries = []
                , ** kw
                )
            if request.brief :
                result ["url_template"] = pp_join \
                    (resource.abs_href_dynamic, "{entry}")
            return result
        # end def _response_dict

        def _response_entry (self, resource, request, response, entry) :
            if request.brief :
                result = entry.name
            else :
                result = pp_join (resource.abs_href_dynamic, entry.name)
            return result
        # end def _response_entry

        def _resource_entries (self, resource, request, response) :
            raise NotImplementedError
        # end def _resource_entries

    GET = RST__Dir_Base__GET # end class

    def __init__ (self, ** kw) :
        self._entry_map = {}
        for k in ("template", "template_name") :
            if k in kw :
                kw ["page_" + k] = kw.pop (k)
        self.__super.__init__ (** kw)
    # end def __init__

    @property
    @getattr_safe
    def dir_template (self) :
        if self._dir_template is None :
            t_name = getattr (self, "dir_template_name", None)
            if t_name :
                self._dir_template = self.get_template (t_name)
        return self._dir_template
    # end def dir_template

    @dir_template.setter
    def dir_template (self, value) :
        self._dir_template = None
        if isinstance (value, pyk.string_types) :
            self.dir_template_name = value
        elif not isinstance (value, self.Templateer.Template_Type) :
            self.dir_template_name = value.name
        else :
            self.dir_template_name = value.name
            self._dir_template     = value
    # end def dir_template

    @Once_Property
    @getattr_safe
    def empty_template (self) :
        t_name = getattr (self, "empty_template_name", None)
        if t_name :
            return self.get_template (t_name)
    # end def empty_template

    @property
    @getattr_safe
    def entry_map (self) :
        self.entries ### trigger recomputation/load-from-db, if necessary
        return self._entry_map
    # end def entry_map

    @property
    @getattr_safe
    def href_pat_frag (self) :
        result = self._href_pat_frag
        if result is None :
            result = self._href_pat_frag = self._add_href_pat_frag_tail \
                (re.escape (self.name))
        return result
    # end def href_pat_frag

    @Once_Property
    @getattr_safe
    def injected_dir_templates (self) :
        ### redefine as necessary
        return set ()
    # end def injected_dir_templates

    def add_entries (self, * entries) :
        add = self._entries.append
        map = self._entry_map
        for e in entries :
            if isinstance (e, tuple) :
                cls, args, kw = e
                e             = cls (* args, ** dict (kw, parent = self))
            add (e)
            map [e.name] = e
    # end def add_entries

    def template_iter (self) :
        if self.top.dynamic_p or self.static_p :
            for t in self.__super.template_iter () :
                yield t
            t = self.dir_template
            if t :
                yield t
    # end def template_iter

    def _get_child (self, child, * grandchildren) :
        try :
            result = self.entry_map [child]
        except KeyError :
            pass
        else :
            if grandchildren :
                result = result._get_child (* grandchildren)
            return result
    # end def _get_child

    def _new_child (self, T, child, grandchildren) :
        result = T (name = child, parent = self)
        if not grandchildren :
            return result
        else :
            return result._get_child (* grandchildren)
    # end def _new_child

_Dir_Base_ = _RST_Dir_Base_ # end class

_Ancestor = _Dir_Base_

class _RST_Dir_ (_Ancestor) :
    """Base class for RESTful directories (resources with children)."""

    _real_name                 = "_Dir_"

    static_page_suffix         = "/index.html"

    class RST__Dir__GET (_Ancestor.GET) :

        _real_name             = "GET"

        def _resource_entries (self, resource, request, response) :
            return resource.entries
        # end def _resource_entries

    GET = RST__Dir__GET # end class

    def __init__ (self, ** kw) :
        entries = kw.pop ("entries", [])
        self.__super.__init__ (** kw)
        self._entries = []
        if entries :
            self.add_entries (* entries)
    # end def __init__

    @property
    @getattr_safe
    def entries (self) :
        return self._entries
    # end def entries

    @property
    @getattr_safe
    def entries_transitive (self) :
        for e in self.entries :
            yield e
            for d in e.entries_transitive :
                yield d
    # end def entries_transitive

    @property
    @getattr_safe
    def template (self) :
        eff = self._effective
        if eff is self :
            result = self.dir_template
            if result is None :
                result = self.empty_template
        else :
            result = eff.template
        return result
    # end def template

    def sub_dir_iter (self) :
        for owl in self.entries :
            if isinstance (owl, _Dir_) :
                yield owl
    # end def sub_dir_iter

    def template_iter (self) :
        if self.top.dynamic_p or self.static_p :
            for t in self.__super.template_iter () :
                yield t
            eff = self._effective
            if eff is not self :
                for t in eff.template_iter () :
                    yield t
            for d in self.sub_dir_iter () :
                for t in d.template_iter () :
                    yield t
    # end def template_iter

    def _add_href_pat_frag_tail \
            (self, head, getter = TFL.Getter.href_pat_frag) :
        result  = head
        entries = sorted \
            (self.entries or (), key = lambda x : x.name, reverse = True)
        e_hpfs = tuple (x for x in (getter (e) for e in entries) if x)
        if e_hpfs :
            e_result   = "|".join (e_hpfs)
            if head :
                result = "%s(?:/(?:%s))?" % (head, e_result)
            else :
                result = e_result
        return result
    # end def _add_href_pat_frag_tail

_Dir_ = _RST_Dir_ # end class

_Ancestor = _Dir_

class RST_Dir (_Ancestor) :
    """Base class for RESTful directories (resources with children)."""

    _real_name                 = "Dir"

    def __init__ (self, ** kw) :
        self.prefix = pp_join (self.parent.prefix, kw ["name"], "")
        self.__super.__init__ (** kw)
    # end def __init__

    @Once_Property
    @getattr_safe
    def href_dynamic (self) :
        return self.prefix.rstrip ("/")
    # end def href_dynamic

Dir = RST_Dir # end class

_Ancestor = _Dir_Base_

class RST_Dir_V (_Ancestor) :
    """Base class for RESTful volatile directories (resources with children,
       without permanent `_entries`).
    """

    _entry_type_map = None

    @property
    @getattr_safe
    def entries (self) :
        return ()
    # end def entries

    def template_iter (self) :
        if self.top.dynamic_p or self.static_p :
            for t in self.__super.template_iter () :
                yield t
            if self._entry_type_map :
                for e in pyk.itervalues (self._entry_type_map) :
                    for t in e.template_iter () :
                        yield t
    # end def template_iter

    def _add_href_pat_frag_tail (self, head, getter = None) :
        return head
    # end def _add_href_pat_frag_tail

    def _get_child (self, child, * grandchildren) :
        result = self.__super._get_child (child, * grandchildren)
        if result is None and self._entry_type_map :
            try :
                T = self._entry_type_map [child]
            except KeyError :
                pass
            else :
                return self._new_child (T, child, grandchildren)
        return result
    # end def _get_child

    def _greet_entry (self, entry) :
        self._entry_map [entry.name] = entry
    # end def _greet_entry

Dir_V = RST_Dir_V # end class

_Ancestor = Leaf

class RST_Raiser (_Ancestor) :
    """Resource that raises an error 500."""

    _real_name                 = "Raiser"

    hidden                     = True
    skip_etag                  = True

    class RST_Raiser_GET (_Ancestor.GET) :

        _real_name             = "GET"

        def _response_body (self, resource, request, response) :
            raise resource.Status.Internal_Server_Error \
                (RuntimeError ("Wilful raisement"))
        # end def _response_body

    GET = RST_Raiser_GET # end class

Raiser = RST_Raiser # end class

_Ancestor = _Dir_

class RST_Root (_Ancestor) :
    """Root of tree of RESTful resources."""

    _real_name                 = "Root"

    class RST_Root_Cacher (TFL.Meta.Object) :

        def __init__ (self, * args, ** kw) :
            self._args = args
            self._kw   = kw
        # end def __init__

        @Once_Property
        @getattr_safe
        def cache_rank (self) :
            return GTW.RST.Template_Media_Cache.cache_rank
        # end def cache_rank

        @Once_Property
        @getattr_safe
        def tmc (self) :
            return GTW.RST.Template_Media_Cache (* self._args, ** self._kw)
        # end def tmc

        def as_pickle_cargo (self, root) :
            result = dict (href_pat_frag = root.href_pat_frag)
            if root.Templateer :
                result ["tmc"] = self.tmc.as_pickle_cargo (root)
            return result
        # end def as_pickle_cargo

        def from_pickle_cargo (self, root, cargo) :
            root._href_pat_frag = cargo.get ("href_pat_frag")
            if root._href_pat_frag :
                root._href_pat = None ### trigger recalculation
            if root.Templateer :
                tmc_cargo = cargo.get ("tmc")
                if tmc_cargo :
                    self.tmc.from_pickle_cargo (root, tmc_cargo)
        # end def from_pickle_cargo

    Cacher = RST_Root_Cacher # end class

    Create_Scope               = None
    ACAO                       = None
    DEBUG = TEST               = False
    Templateer                 = None

    default_locale_code        = "en"
    domain                     = ""
    dynamic_p                  = True
    encoding                   = "utf-8"    ### output encoding
    error_email_template       = "error_email"
    i18n                       = False
    ignore_picky_accept        = False
    input_encoding             = "utf-8"
    language                   = "en"
    languages                  = set (("en", ))
    prefix                     = ""
    request                    = None
    s_domain                   = None
    site_url                   = ""
    skip_etag                  = False
    static_p                   = False
    use_www_debugger           = False
    user                       = None

    _dynamic_nav_p             = False
    _exclude_robots            = True
    _hash_fct                  = None
    _href_pat                  = None
    _lang_pat                  = None
    _name                      = ""
    _needs_parent              = False

    _email_from                = None   ### default from address
    _smtp                      = None
    _webmaster                 = None

    from _GTW._RST.Request  import Request  as Request_Type
    from _GTW._RST.Response import Response as Response_Type

    class E_Type_Desc (GTW.RST.R_Map) :

        _prop_map   = {}
        _prop_names = ()

        def __init__ (self, type_name) :
            self.type_name = type_name
        # end def __init__

        def _find_missing (self, name) :
            if name in self._prop_map :
                R = self._prop_map [name]
                try :
                    getter = R.resource_from_e_type
                except AttributeError :
                    pass
                else :
                    return getter (self.type_name)
        # end def _find_missing

    # end class E_Type_Desc

    def __init__ (self, HTTP, ** kw) :
        if "copyright_start" not in kw :
            kw ["copyright_start"] = time.localtime ().tm_year
        self.pop_to_self      (kw, "name", "prefix")
        self.pop_to_self      (kw, "dynamic_nav_p", "smtp", prefix = "_")
        self.E_Type_Desc    = self.E_Type_Desc.New (_prop_map  = {})
        self.ET_Map         = TFL.defaultdict_kd (self.E_Type_Desc)
        self.HTTP           = HTTP
        self.redirects      = dict (kw.pop ("redirects", {}))
        self.SC             = TFL.Record ()
        self.Table          = {}
        self._change_infos  = {}
        self._objects_cache = {}
        self._old_cids      = {}
        self.top            = self
        self.__super.__init__ (** kw)
    # end def __init__

    def __call__ (self, environ, start_response) :
        return self.wsgi_app (environ, start_response)
    # end def __call__

    @property
    @getattr_safe
    def dynamic_nav_p (self) :
        return self.dynamic_p or self._dynamic_nav_p
    # end def dynamic_nav_p

    @dynamic_nav_p.setter
    def dynamic_nav_p (self, value) :
        self._dynamic_nav_p = value
    # end def dynamic_nav_p

    @Once_Property
    @getattr_safe
    def first_time (self) :
        ### Short term hack to load all entries once to fill `Table`
        return list (self.entries_transitive)
    # end def first_time

    @property
    @getattr_safe
    def hash_fct (self) :
        result = self._hash_fct
        if result is None :
            result = self._hash_fct = TFL.user_config.sha
        return result
    # end def hash_fct

    @hash_fct.setter
    def hash_fct (self, value) :
        self._hash_fct = value
    # end def hash_fct

    @property
    @getattr_safe
    def href_pat (self) :
        result = self._href_pat
        if result is None :
            hpf = self.href_pat_frag
            if hpf :
                try :
                    result = self._href_pat = re.compile \
                        ("(?:%s)(?:/|$)" % (hpf, ))
                except Exception as exc :
                    enc  = self.encoding
                    logging.error \
                        ( pyk.as_str ("Exception in href_pat for %s: %s", enc)
                        , pyk.as_str (self, enc)
                        , pyk.as_str (exc, enc)
                        )
        return result
    # end def href_pat

    @property
    @getattr_safe
    def lang_pat (self) :
        result = self._lang_pat
        if result is None and self.i18n :
            try :
                self.SC.L10N ### only return `lang_pat` if L10N exists
                languages = self.languages
                result    = self._lang_pat = re.compile \
                    (r"(?:/?(?:%s)(?:/|$))" % ("|".join (sorted (languages))))
            except Exception as exc :
                logging.error (pyk.as_str (exc, self.encoding))
            return result
    # end def lang_pat

    @Once_Property
    @getattr_safe
    def rst_etag (self) :
        result = [self.href_pat_frag]
        T = self.Templateer
        if T is not None :
            result.append (T.etag)
        return "::".join (r for r in result if r)
    # end def rst_etag

    @property
    @getattr_safe
    def smtp (self) :
        if self._smtp is None :
            from _TFL.SMTP import SMTP_Logger
            self._smtp = SMTP_Logger ()
        return self._smtp
    # end def smtp

    @Once_Property
    @getattr_safe
    def scope (self) :
        CS = self.Create_Scope
        if CS is not None :
            result = CS (self.App_Type, self.DB_Url)
            if self.DEBUG :
                print ("Loaded", result)
            return result
    # end def scope

    @property
    @getattr_safe
    def webmaster (self) :
        result = self._webmaster
        if result is None :
            domain = self.domain or self.site_url
            if domain.startswith ("www.") :
                domain = domain [4:]
            result = self._webmaster = "webmaster@%s" % (domain, )
        return result
    # end def webmaster

    @webmaster.setter
    def webmaster (self, value) :
        self._webmaster = value
    # end def webmaster

    def allow (self, resource, user, method = "GET") :
        if isinstance (resource, pyk.string_types) :
            resource = self.resource_from_href (resource)
        if resource :
            try :
                allow_method = resource.allow_method
            except Exception :
                return True
            else :
                return allow_method (method, user)
    # end def allow

    def Request (self, environ) :
        result = self.Request_Type  (self, environ)
        result.charset = self.encoding
        return result
    # end def Request

    def Response (self, request, * args, ** kw) :
        result = self.Response_Type (self, request, * args, ** kw)
        result.charset = self.encoding
        return result
    # end def Response

    def resource_from_href (self, req_href, request = None) :
        try :
            return self._resource_from_href (req_href, request)
        except self.Status.Not_Found :
            return None
    # end def resource_from_href

    def template_iter (self) :
        seen = set ()
        gett = self.get_template
        def _gen () :
            for tn in self._template_names :
                yield gett (tn)
            if self.Templateer :
                for tn in self.Templateer.error_template_names :
                    yield gett (tn, [])
            for t in self.__super.template_iter () :
                yield t
        for t in _gen () :
            if t.id not in seen :
                yield t
                seen.add (t.id)
    # end def template_iter

    def wsgi_app (self, environ, start_response) :
        """WSGI application responding to http[s] requests."""
        Status   = self.Status
        HTTP     = self.HTTP
        request  = self.Request  (environ)
        response = self.Response (request)
        entries_transitive = self.first_time
        with self.LET (user = request.user, _change_infos = {}) :
            try :
                href     = request.path
                resource = self.resource_from_href (href, request)
                if resource :
                    request.resource = resource
                    result = self._http_response (resource, request, response)
                else :
                    raise Status.Not_Found ()
            except Status.Status as status :
                if isinstance (status, Status.Server_Error) :
                    self.send_error_email \
                        (request, status, traceback.format_exc ())
                with self._http_response_context (self, request, response) :
                    result  = status (self, request, response)
            except HTTP.HTTP_Exception as exc :
                ### works for werkzeug.exceptions.HTTPException
                return exc
            except Exception as exc :
                if self.use_www_debugger :
                    raise
                tbi     = traceback.format_exc ()
                result  = self._http_response_error \
                    (request, response, exc, tbi)
            if not result :
                exc     = ValueError ("No result")
                if self.use_www_debugger :
                    raise exc
                result  = self._http_response_error (request, response, exc)
            return result (environ, start_response)
    # end def wsgi_app

    def _http_response (self, resource, request, response) :
        Status    = self.Status
        user      = request.user
        with self._http_response_context (resource, request, response) :
            auth      = user and user.authenticated
            meth_name = request.method
            resource  = resource._effective
            if meth_name not in resource.SUPPORTED_METHODS :
                raise Status.Method_Not_Allowed \
                    (valid_methods = sorted (resource.SUPPORTED_METHODS))
            Method = resource._get_method (meth_name)
            if Method is not None :
                method = Method ()
                if resource.allow_method (method, user) :
                    if resource.ACAO :
                        response.add_header \
                            ("Access-Control-Allow-Origin", resource.ACAO)
                    if resource.DEBUG :
                        context = TFL.Context.time_block
                        fmt     = "[%s] %s %s: execution time = %%s" % \
                            ( time.strftime
                                ( "%d-%b-%Y %H:%M:%S"
                                , time.localtime (time.time ())
                                )
                            , method.name, request.url.replace ("%", "%%")
                            )
                    else :
                        context = TFL.Context.relaxed
                        fmt     = None
                    with context (fmt, sys.stderr) :
                        with resource._handle_method_context \
                                (method, request, response) :
                            return resource._handle_method \
                                (method, request, response)
                else :
                    self._http_response_need_auth \
                        (resource, request, response, auth)
    # end def _http_response

    @TFL.Contextmanager
    def _http_response_context (self, resource, request, response) :
        language  = request.language or self.language
        scope     = self.scope
        r_context = dict (request = request, response = response)
        if language :
            ### Cannot use `with TFL.I18N.context (language)` here
            ### because the final WSGI call at the end of `wsgi_app` would be
            ### outside that context
            TFL.I18N.use (language)
        with self.LET (** r_context) :
            if scope and getattr (scope, "LET", None) :
                with scope.LET (user = request.user) :
                    yield
            else :
                yield
    # end def _http_response_context

    def _http_response_error (self, request, response, exc, tbi = None) :
        Error = self.Status.Internal_Server_Error ()
        self.send_error_email (request, exc, tbi)
        with self._http_response_context (self, request, response) :
            return Error (self, request, response)
    # end def _http_response_error

    def _http_response_need_auth (self, resource, request, response, auth) :
        raise (self.Status.Forbidden if auth else self.Auth_Required) ()
    # end def _http_response_need_auth

    def _request_href (self, href, request) :
        result = href.strip ("/")
        l_pat  = self.lang_pat
        if l_pat is not None :
            langs = None
            match = l_pat.match (result)
            if match :
                prefix = match.group (0)
                langs  = (prefix.strip ("/"), )
                result = result [len (prefix):]
            if request is not None :
                request.use_language (langs or request.locale_codes or ())
        return result
    # end def _request_href

    def _resource_from_href (self, req_href, request = None) :
        Table        = self.Table
        req_href     = self._request_href (req_href, request)
        href, ext    = pp_splitext (req_href)
        match        = None
        redirects    = self.redirects
        result       = None
        if redirects :
            try :
                redirect = redirects [href]
            except KeyError :
                pass
            else :
                if isinstance (redirect, tuple) :
                    status, result = redirect
                else :
                    status, result = 302, redirect
                raise self.Status.Status [status] (result)
        if result is None :
            result = Table.get (href)
        if result is None :
            href_pat = self.href_pat
            if href_pat :
                match = href_pat.match (href)
                if match :
                    head     = match.group (0).rstrip ("/")
                    resource = Table.get (head)
                    if resource :
                        tail = href [len (head):].strip ("/")
                        if tail :
                            tail   = tail.split ("/")
                            result = resource._get_child (* tail)
                        else :
                            result = resource
        if result is None :
            head = href
            tail = []
            while head :
                head, _ = pp_split (head)
                if head or not tail : ### `not tail` covers root's entries
                    tail.append (_)
                    try :
                        d = Table [head]
                    except KeyError :
                        pass
                    else :
                        if self.DEBUG :
                            print \
                                ( "*" * 3, href, d
                                , "not in `Table`, not matched by `href_pat`"
                                )
                        result = d._get_child (* reversed (tail))
                if result :
                    break
        return result
    # end def _resource_from_href

Root = RST_Root # end class

__doc__ = """
Each supported http method is defined by a separate class of the same name
(in upper case). To disable support in a descendent class, set the
appropriate name to `None`, e.g., ::

    PUT = None

"""

if __name__ != "__main__" :
    GTW.RST._Export ("*", "_Base_", "_Dir_Base_", "_Dir_")
### __END__ GTW.RST.Resource
