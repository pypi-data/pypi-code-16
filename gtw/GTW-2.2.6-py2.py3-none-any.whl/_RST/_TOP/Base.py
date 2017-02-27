# -*- coding: utf-8 -*-
# Copyright (C) 2012-2017 Mag. Christian Tanzer All rights reserved
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
#    GTW.RST.TOP.Base
#
# Purpose
#    Basic classes for Tree-of-Page framework
#
# Revision Dates
#     5-Jul-2012 (CT) Creation (based on GTW.NAV.Base)
#     9-Jul-2012 (CT) Add and use `HTTP_Method_Mixin.template_name`
#     9-Jul-2012 (CT) Add `RST_TOP_HTML`, define `.rendered`
#    18-Jul-2012 (CT) Add `Index`, `next`, and `prev`
#    20-Jul-2012 (CT) Add `request.original_resource`
#     2-Aug-2012 (CT) Add `response` to result of `_render_context`
#     2-Aug-2012 (CT) Add missing import, fix typo
#     3-Aug-2012 (CT) Add `http_method` to `_render_context`
#     4-Aug-2012 (MG) Add missing import
#     6-Aug-2012 (MG) Enhance `is_current_page`
#     6-Aug-2012 (MG) Consider `hidden`in  `is_current_page`
#     7-Aug-2012 (CT) Factor `own_links` to `RST.Base`
#    26-Sep-2012 (CT) Remove `hidden` from `is_current_page`
#    15-Jan-2013 (CT) Add `cc_href`
#     2-Mar-2013 (CT) Redefine `_handle_method` to add `next`, `prev` links
#     3-May-2013 (CT) Rename `login_required` to `auth_required`
#     3-May-2013 (CT) Factor `auth_required` and `allow_method` to
#                     `GTW.RST.Base`
#     9-Dec-2013 (CT) Add `csrf_check`
#    11-Dec-2013 (CT) Improve error message from `csrf_check`
#    18-Dec-2013 (CT) Add `x_signature` to error message from `csrf_check`
#    24-Jan-2014 (CT) Add `a_attr_dict`
#    24-Jan-2014 (CT) Factor `_Mixin_`
#    11-Feb-2014 (CT) Use `response`, not `request`, in `_new_edit_session`
#    24-Feb-2014 (CT) Apply `pyk.decoded` to `repr (csrf_token)` in `csrf_check`
#    13-Mar-2014 (CT) Factor `response.add_rel_links` from `_handle_method`
#    14-Mar-2014 (CT) Add properties `first`, `last`,
#                     `first_child`, `last_child`
#    14-Mar-2014 (CT) Use `proper_entries` for relative links
#    29-Apr-2014 (CT) Robustify `first_child` and `last_child`
#    12-Dec-2014 (CT) Add `HTTP_POST_CRSF_Mixin`
#                     (factored from `GTW.RST.TOP.Auth._Form_Cmd_.POST`)
#    20-Mar-2015 (CT) Use `request.language` in `render_context`
#    28-Apr-2015 (CT) Skip `hidden`  entries in `Index.next`, `.prev`
#    17-Nov-2015 (CT) Add `as_static_page`
#    18-Nov-2015 (CT) Remove redundant redefinition of `permalink`
#    11-Oct-2016 (CT) Use `CHJ.Media`, not `GTW.Media`
#     8-Feb-2017 (CT) Change `Index.next`, `.prev`, to use `show_in_nav`
#                     instead of `hidden`
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

from   _CHJ                     import CHJ
from   _GTW                     import GTW
from   _TFL                     import TFL
from   _TFL.pyk                 import pyk

import _CHJ.Media
import _GTW._RST.Mime_Type
import _GTW._RST.Resource
import _GTW._RST._TOP

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL                     import sos
from   _TFL.Decorator           import getattr_safe
from   _TFL.I18N                import _, _T, _Tn
from   _TFL.predicate           import uniq

from   posixpath                import join as pp_join

import time
import uuid

class RST_TOP_HTML (GTW.RST.Mime_Type.HTML) :

    _real_name                 = "HTML"

    def rendered (self, request, response, body) :
        ### `body` is already rendered as HTML
        return body
    # end def rendered

HTML = RST_TOP_HTML # end class

class HTTP_Method_Mixin (GTW.RST.HTTP_Method) :

    _renderers             = (HTML, )

    template_name          = None

    def _render_context (self, resource, request, response, ** kw) :
        result = dict \
            ( http_method   = self
            , request       = request
            , response      = response
            , notifications = response.session.notifications
            , ** kw
            )
        if request.original_resource is not None :
            result.setdefault ("nav_page", request.original_resource)
        return result
    # end def _render_context

    def _response_body (self, resource, request, response) :
        template = None
        if self.template_name :
            template = resource.get_template (self.template_name)
        context  = resource.render_context \
            (** self._render_context (resource, request, response))
        result = resource.rendered (context, template = template)
        if result is None :
            raise resource.Status.Not_Found ()
        return result
    # end def _response_body

# end class HTTP_Method_Mixin

class HTTP_POST_CRSF_Mixin (HTTP_Method_Mixin) :
    """Mixin for HTTP POST methods to check anti crsf token"""

    def _skip_render (self, resource, request, response) :
        result = self.__super._skip_render (resource, request, response)
        if not result :
            resource.csrf_check (request, response)
        return result
    # end def _skip_render

# end class HTTP_POST_CRSF_Mixin

_Ancestor = GTW.RST._Base_

class _TOP_Mixin_ (_Ancestor) :
    """Mixin class for TOP classes."""

    _real_name                 = "_Mixin_"

    session_ttl_name           = "user_session_ttl"
    short_title                = ""
    title                      = ""

    _exclude_robots            = False
    _index                     = None
    _Media                     = CHJ.Media ()

    class _TOP_Base_GET_ (HTTP_Method_Mixin, _Ancestor.GET) :

        _real_name             = "GET"

    GET = _TOP_Base_GET_ # end class

    @property
    @getattr_safe
    def a_attr_dict (self) :
        result = self.__super.a_attr_dict
        title  = self.title
        if title :
            result.update (title = title)
        return result
    # end def a_attr_dict

    @property
    @getattr_safe
    def has_children (self) :
        return bool (getattr (self, "entries", []))
    # end def has_children

    def is_current_dir (self, page) :
        return False
    # end def is_current_dir

    def is_current_page (self, page) :
        return \
            (  (self.permalink    == page.permalink)
            or (self.href_dynamic == page.href_dynamic)
            )
    # end def is_current_page

_Mixin_ = _TOP_Mixin_ # end class

_Ancestor = _Mixin_

class _TOP_Base_ (_Ancestor) :
    """Base class for TOP."""

    _real_name                 = "_Base_"

    class Index (TFL.Meta.Object) :

        wrap = False

        def __init__ (self, number) :
            self.number = number
        # end def __init__

        def next (self, resource) :
            i = self.number + 1
            entries = resource.parent.proper_entries
            if i >= len (entries) and self.wrap :
                i = 0
            try :
                result = entries [i]
            except IndexError :
                pass
            else :
                while (not result.show_in_nav ()) and i+1 < len (entries) :
                    i += 1
                    result = entries [i]
                if result.show_in_nav () :
                    return result
        # end def next

        def prev (self, resource) :
            i = self.number - 1
            entries = resource.parent.proper_entries
            if i >= 0 or self.wrap :
                try :
                    result = entries [i]
                except IndexError :
                    pass
                else :
                    while (not result.show_in_nav ()) and i > 0 :
                        i -= 1
                        result = entries [i]
                    if result.show_in_nav () :
                        return result
        # end def prev

    # end class Index

    class Index_W (Index) :

        wrap = True

    # end class Index_W

    Index_Type = Index

    def __init__ (self, ** kw) :
        self.pop_to_self (kw, "Media", prefix = "_")
        self.__super.__init__ (** kw)
    # end def __init__

    @property
    @getattr_safe
    def cc_href (self) :
        if self.cc_domain :
            return "https://" + pp_join (self.cc_domain, self.href)
    # end def cc_href

    @Once_Property
    @getattr_safe
    def copyright (self) :
        year  = time.localtime ().tm_year
        start = int (self.copyright_start)
        yr    = str (year) if year == start else "%4.4d-%4.4d" % (start, year)
        return dict \
            ( holder = self.owner
            , url    = self.copyright_url or "/"
            , year   = yr
            )
    # end def copyright

    @property
    @getattr_safe
    def first (self) :
        if self.parent :
            return self.parent.first_child
    # end def first

    @property
    @getattr_safe
    def first_child (self) :
        try :
            return self.proper_entries [0]
        except (AttributeError, LookupError, TypeError) :
            pass
    # end def first_child

    @property
    @getattr_safe
    def h_title (self) :
        name = self.short_title or self.name or self.href
        if self.parent :
            return "/".join ((name, self.parent.h_title))
        else :
            if self is self.top.home :
                return self.top.h_title
            else :
                return "%s [%s]" % (name, self.top.h_title)
    # end def h_title

    @property
    @getattr_safe
    def last (self) :
        if self.parent :
            return self.parent.last_child
    # end def last

    @property
    @getattr_safe
    def last_child (self) :
        try :
            return self.proper_entries [-1]
        except (AttributeError, LookupError, TypeError) :
            pass
    # end def last_child

    @Once_Property
    @getattr_safe
    def Media (self) :
        return self._get_media ()
    # end def Media

    @property
    @getattr_safe
    def next (self) :
        index = self._index
        if index is not None :
            return index.next (self)
    # end def next

    @property
    @getattr_safe
    def prev (self) :
        index = self._index
        if index is not None :
            return index.prev (self)
    # end def prev

    @property
    @getattr_safe
    def q_href (self) :
        return pp_join (self.abs_href_dynamic, self.q_prefix)
    # end def q_href

    def as_static_page (self) :
        """Return static HTML page for this resource."""
        top = self.top
        with top.LET (dynamic_p = False) :
            app_iter, status, headers = top.test_client.get \
                (self.abs_href_dynamic)
            if status.startswith ("200") :
                return "".join (pyk.decoded (chunk) for chunk in app_iter)
    # end def as_static_page

    def csrf_check (self, request, response) :
        if self.csrf_check_p :
            error = None
            if not request.same_origin :
                error = \
                    ( _T ("Incorrect origin `%s` for request, expected `%r`")
                    % (request.origin_host, request.server_name)
                    )
            else :
                csrf_token = request.csrf_token
                if not csrf_token :
                    if self.DEBUG :
                        error  = "\n".join \
                            ( ( pyk.decoded (repr (csrf_token))
                              , "Client sig  : %s" % (csrf_token.x_signature, )
                              , "Client value: %s" % (csrf_token.x_value, )
                              , "Server value: %s" % (csrf_token.value, )
                              , "Session sid : %s" % (request.session.sid, )
                              )
                            )
                    else :
                        error  = csrf_token._invalid
            if error :
                exc = self.top.Status.See_Other (self.abs_href)
                self.send_error_email (request, "CSRF", xtra = error)
                raise exc
    # end def csrf_check

    def etype_manager (self, obj) :
        etn = getattr (obj, "type_name", None)
        if etn :
            return self.top.ET_Map [etn].manager
    # end def etype_manager

    def formatted (self, sep = "\n    ") :
        kvs = \
            (   "%s : %r" % (k, v)
            for (k, v) in sorted (pyk.iteritems (self._kw))
            )
        return "<%s %s\n    %s\n  >" % (self.Type, self.name, sep.join (kvs))
    # end def formatted

    def obj_href (self, obj) :
        man = self.etype_manager (obj)
        if man :
            return man.href_display (obj)
    # end def obj_href

    def page_from_obj (self, obj) :
        man = self.etype_manager (obj)
        if man :
            return man.page_from_obj (obj)
    # end def page_from_obj

    def render_context (self, nav_page = None, ** kw) :
        if nav_page is None :
            nav_page = self
        return self.top.Templateer.Context \
            ( NAV           = self.top
            , lang          = nav_page.request.language
            , nav_page      = nav_page
            , page          = self
            , ** kw
            )
    # end def render_context

    def rendered (self, context, template = None) :
        result = self.top.Templateer.render \
            (template or self.template, context)
        if self.translator :
            result = self.translator (result)
        return result
    # end def rendered

    def _get_media (self, head = None) :
        medias   = []
        parent   = self.parent
        template = getattr (self, "template")
        if head is not None :
            medias.append (head)
        if self._Media is not _TOP_Base_._Media :
            medias.append (self._Media)
        if getattr (template, "Media", None) :
            medias.append (template.Media)
        if parent and parent.Media is not _TOP_Base_._Media :
            medias.append (parent.Media)
        if medias :
            return CHJ.Media (children = medias)
        return self._Media
    # end def _get_media

    def _handle_method (self, method, request, response) :
        result = self.__super._handle_method (method, request, response)
        response.add_rel_links ()
        return result
    # end def _handle_method

    def _new_edit_session (self, response, ttl = None) :
        dbmd = self.top.scope.db_meta_data
        user = response.user
        if user is None :
            u_hash = response.username = uuid.uuid1 ().hex
        else :
            u_hash = user.password
        return response.session.new_edit_session \
            ((u_hash, dbmd.dbv_hash, dbmd.dbid, sos.getpid ()), ttl)
    # end def _new_edit_session

_Base_ = _TOP_Base_ # end class

if __name__ != "__main__" :
    GTW.RST.TOP._Export ("*", "_Base_", "_Mixin_")
### __END__ GTW.RST.TOP.Base
