# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.RST.TOP.MOM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.RST.TOP.MOM.Aggregator
#
# Purpose
#    Page aggregating the most recent instances of one or more E_Types
#
# Revision Dates
#    17-Jul-2012 (CT) Creation
#     7-Aug-2012 (CT) Change `GTW.RST.MOM.RST_` to `GTW.RST.MOM.`
#     7-Dec-2012 (CT) Rename `query_filters` to `query_filters_s`
#    20-May-2014 (CT) Fix `query`
#    13-Sep-2014 (CT) Change `change_query_filters` to `change_query_types`
#    15-Sep-2014 (CT) Re-introduce `change_query_filters`,
#                     fix `change_query_types`
#     8-Oct-2015 (CT) Change `__getattr__` to *not* handle `__XXX__`
#    17-Nov-2015 (CT) Set `static_p`
#    18-Nov-2015 (CT) Change `Instance.__getattr__` to return `permalink` for
#                     `link_to`
#    14-Dec-2015 (CT) Add `random_picture`
#    ««revision-date»»···
#--

from   __future__ import absolute_import, division, print_function, unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

import _GTW._RST._TOP._MOM.Mixin
import _GTW._RST._TOP.Dir
import _GTW._RST._TOP.Page

from   _MOM.import_MOM          import MOM, Q

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL.Decorator           import getattr_safe
from   _TFL.I18N                import _, _T, _Tn
from   _TFL.predicate           import first
from   _TFL.pyk                 import pyk

from   posixpath                import join as pp_join

_Ancestor = GTW.RST.TOP.Page

class Aggregator (GTW.RST.MOM.Mixin, _Ancestor) :
    """Page aggregating the most recent instances of one or more E_Types."""

    css_class             = "news-clip"
    page_template_name    = "e_type_aggregator"
    query_limit           = 25
    sort_key              = TFL.Sorted_By ("-date.start", "-prio")
    static_p              = True

    _exclude_robots       = False
    _old_objects          = None

    class Aggregator_GET (_Ancestor.GET) :

        _real_name             = "GET"

        def _render_context (self, resource, request, response, ** kw) :
            return self.__super._render_context \
                ( resource, request, response
                , calendar       = resource.calendar
                , clips          = resource.clips
                , random_picture = None
                    if resource.clips else resource.random_picture
                , ** kw
                )
        # end def _render_context

    GET = Aggregator_GET # end class

    class Instance (TFL.Meta.Object) :

        def __init__ (self, obj, parent) :
            self.obj    = obj
            self.parent = parent
            self.top    = parent.top
            self.FO     = GTW.FO (obj, parent.top.encoding)
        # end def __init__

        def __getattr__ (self, name) :
            if name.startswith ("__") and name.endswith ("__") :
                ### Placate inspect.unwrap of Python 3.5,
                ### which accesses `__wrapped__` and eventually throws
                ### `ValueError`
                return getattr (self.__super, name)
            if name == "link_to" :
                top    = self.top
                result = getattr (self.obj, name, None)
                if not result :
                    left = getattr (self.obj, "left", None)
                    if left is not None :
                        result = top.obj_href (left)
                if result :
                    page   = top.resource_from_href (result)
                    result = page.permalink
            else :
                result = getattr (self.FO, name)
            return result
        # end def __getattr__

    # end class Instance

    def __init__ (self, ** kw) :
        kw ["_ETMS"] = kw.pop ("ETMS")
        self.__super.__init__ (** kw)
    # end def __init__

    @Once_Property
    @getattr_safe
    def calendar (self) :
        return getattr (self.top.SC, "Cal", None)
    # end def calendar

    @Once_Property
    @getattr_safe
    def change_query_filters (self) :
        return (Q.type_name.IN (sorted (self.change_query_types)), )
    # end def change_query_filters

    @Once_Property
    @getattr_safe
    def change_query_types (self) :
        result = set ()
        for ETM in self.ETMS :
            E_Type = ETM.E_Type
            result.update (self._change_query_types (E_Type))
        return result
    # end def change_query_types

    @property
    @getattr_safe
    def clips (self) :
        objects = self.objects
        if self._old_objects is not objects :
            self._clips = \
                [self.Instance (obj = o, parent = self) for o in objects]
            if objects :
                self._old_objects = objects
        return self._clips
    # end def clips

    @Once_Property
    @getattr_safe
    def ETMS (self) :
        result = []
        for etm in self._kw ["_ETMS"] :
            if isinstance (etm, pyk.string_types) :
                etm = self.top.scope [etm]
            result.append (etm)
        return result
    # end def ETMS

    @Once_Property
    @getattr_safe
    def query_filters_s (self) :
        return self.__super.query_filters_s + (Q.date.alive, )
    # end def query_filters_s

    @Once_Property
    @getattr_safe
    def Random_Picture (self) :
        return getattr (self.top.SC, "Random_Picture", None)
    # end def Random_Picture

    @property
    @getattr_safe
    def random_picture (self) :
        RP = self.Random_Picture
        if RP is not None :
            return RP.picture.left
    # end def random_picture

    def query (self) :
        qs = []
        ql = self.query_limit
        sk = self.sort_key
        for ETM in self.ETMS :
            q = ETM.query (* self.query_filters, sort_key = sk)
            if ql :
                q = q.limit (ql)
            qs.append (q)
        result = TFL.Q_Result_Composite (qs, order_by = sk)
        if ql :
            result.limit (ql)
        return result
    # end def query

# end class Aggregator

if __name__ != "__main__" :
    GTW.RST.TOP.MOM._Export ("*")
### __END__ GTW.RST.TOP.MOM.Aggregator
