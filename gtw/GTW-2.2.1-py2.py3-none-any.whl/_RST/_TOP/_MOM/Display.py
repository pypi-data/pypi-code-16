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
#    GTW.RST.TOP.MOM.Display
#
# Purpose
#    Display instances of MOM E-types
#
# Revision Dates
#    15-Jul-2012 (CT) Creation
#    18-Jul-2012 (CT) Factor properties from `_E_Type_` to `E_Type_Mixin`
#    25-Jul-2012 (CT) Simplify `_admin_page`
#    25-Aug-2012 (CT) Change `_E_Type_Archive_.entries` to update `_old_cid`
#     9-Nov-2012 (CT) Redefine `page_from_obj` for `E_Type_Archive_DSY` and
#                     `E_Type_Archive_Y`
#     7-Dec-2012 (CT) Consider `dont_et_map`
#     7-Dec-2012 (CT) Rename `query_filters` to `query_filters_s`
#    17-Dec-2012 (CT) Redefine `et_map_name`, remove init-code for `ET_Map`
#    22-Jan-2014 (CT) Add `E_Type.creator`
#    29-Jan-2014 (CT) Locally cache `year` in `_E_Type_Archive_.entries`
#    29-Jan-2014 (CT) Add support for `Referral` to `_E_Type_`
#    29-Jan-2014 (CT) Redefine `_effective` to check `count`
#     5-Feb-2014 (CT) Call `_add_other_entries` in `_E_Type_Archive_.entries`
#    14-May-2014 (CT) Add `sort_key` to `_E_Type_Archive_.Year`
#    25-Jun-2014 (CT) Factor `referral_query` and friends to `...Mixin`
#    27-Apr-2015 (CT) Redefine `_E_Type_Archive_.Year._default_title`
#    14-Oct-2015 (CT) Fix `Entity.changer` (pass `...pid` through `text_type`)
#    17-Nov-2015 (CT) Set `_E_Type_Archive_.static_p`
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
from   _TFL.pyk                 import pyk

from   posixpath                import join  as pp_join

import datetime

_Ancestor = GTW.RST.TOP.Page

class TOP_MOM_Entity (GTW.RST.TOP.MOM.Entity_Mixin, _Ancestor) :
    """Display page for one instance of a E_Type."""

    _real_name      = "Entity"

    @property
    @getattr_safe
    def contents (self) :
        return self.obj.contents
    # end def contents

    @property
    @getattr_safe
    def changer (self) :
        admin = self.admin
        if admin :
            return admin._get_child ("change", pyk.text_type (self.obj.pid))
    # end def changer

    def href_change (self) :
        admin = self.admin
        if admin :
            return admin.href_change (self.obj)
    # end def href_change

    def href_delete (self) :
        admin = self.admin
        if admin :
            return admin.href_delete (self.obj)
    # end def href

Entity = TOP_MOM_Entity # end class

_Ancestor = GTW.RST.TOP.Dir

class _TOP_MOM_E_Type_ (GTW.RST.TOP.MOM.E_Type_Mixin, _Ancestor) :
    """Directory displaying the instances of one E_Type."""

    _real_name      = "_E_Type_"

    Entity          = Entity

    @property
    @getattr_safe
    def creator (self) :
        admin = self.admin
        if admin :
            return admin._get_child ("create")
    # end def creator

    def _add_other_entries (self) :
        self._add_referral_entries      ()
        self.__super._add_other_entries ()
    # end def _add_other_entries

    @property
    @getattr_safe
    def _effective (self) :
        if self.count :
            return self.__super._effective
        else :
            ### support referrals even if not objects are available
            return self
    # end def _effective

_E_Type_ = _TOP_MOM_E_Type_ # end class

class TOP_MOM_E_Type (_E_Type_) :
    """Directory displaying the instances of one E_Type."""

    _real_name      = "E_Type"

    admin_args      = {}
    et_map_name     = "manager"
    sort_key        = TFL.Sorted_By ("-date.start", "perma_name")

    _admin          = None

    def __init__ (self, ** kw) :
        self.__super.__init__ (** kw)
        if self.admin_args :
            if "sort_key" in self.admin_args :
                self.sort_key = self.admin_args ["sort_key"]
            self._admin = self._admin_page (self.admin_args)
    # end def __init__

    def _admin_page (self, admin_args) :
        m_kw        = admin_args.copy ()
        short_title = _T ("Admin")
        title       = m_kw.pop \
            ( "title"
            , "%s: %s" % (self.title.rstrip ("."), _T ("Administration"))
            )
        ETM   = m_kw.pop ("ETM", self.ETM)
        Type  = m_kw.pop ("Type", GTW.RST.TOP.MOM.Admin.E_Type)
        return Type \
            ( name        = "admin"
            , parent      = self
            , short_title = short_title
            , title       = title
            , ETM         = ETM
            , ** m_kw
            )
    # end def _admin_page

E_Type = TOP_MOM_E_Type # end class

class _TOP_MOM_E_Type_Archive_ (E_Type) :
    """Directory displaying the instances of one E_Type organized by year."""

    _real_name      = "_E_Type_Archive_"

    static_p        = True

    _old_year       = None

    class Year (_E_Type_) :
        """Display instances of a specific year."""

        sort_key        = TFL.Sorted_By ("-date.start", "perma_name")

        @Once_Property
        @getattr_safe
        def query_filters_s (self) :
            return \
                ( self.parent._year_filter (self.year)
                + self.__super.query_filters_s
                )
        # end def query_filters_s

        def _default_title (self, E_Type, name, short_title) :
            return "%s %s" % \
                (self.__super._default_title (E_Type, name, short_title), name)
        # end def _default_title

    # end class Year

    @property
    @getattr_safe
    def entries (self) :
        cid  = self._changed_cid ()
        year = self.year
        if self._old_year != year or cid is not None :
            self._entry_map = {}
            self._entries   = []
            def _years (self, year) :
                for y in pyk.xrange \
                        (year + 1, self.top.copyright_start - 1, -1) :
                    yp  = self.Year \
                        ( name      = str (y)
                        , page_args = self.page_args
                        , parent    = self
                        , year      = y
                        )
                    if yp.count or yp.referral_query.count () :
                        yield yp
            self.add_entries        (* tuple (_years (self, year)))
            self._add_other_entries ()
            if self._entries :
                self._old_cid  = cid
                self._old_year = year
        return self._entries
    # end def entries

    @property
    @getattr_safe
    def year (self) :
        return datetime.date.today ().year
    # end def year

_E_Type_Archive_ = _TOP_MOM_E_Type_Archive_ # end class

class TOP_MOM_E_Type_Archive_DSY (_E_Type_Archive_) :
    """Directory displaying the instances of one E_Type organized by
       `date.start.year`.
    """

    _real_name = "E_Type_Archive_DSY"

    def page_from_obj (self, obj) :
        year  = obj.date.start.year
        try :
            d = self._entry_map [str (year)]
        except KeyError :
            result = self.__super.page_from_obj (obj)
        else :
            result = d.page_from_obj (obj)
        return result
    # end def page_from_obj

    def _year_filter (self, y) :
        return (Q.date.start.D.YEAR (y), )
    # end def _year_filter

E_Type_Archive_DSY = TOP_MOM_E_Type_Archive_DSY # end class

class TOP_MOM_E_Type_Archive_Y (_E_Type_Archive_) :
    """Directory displaying the instances of one E_Type organized by `year`."""

    _real_name = "E_Type_Archive_Y"

    def href_display (self, obj) :
        return pp_join (self.abs_href_dynamic, str (obj.year), obj.perma_name)
    # end def href_display

    def page_from_obj (self, obj) :
        year  = obj.year
        try :
            d = self._entry_map [str (year)]
        except KeyError :
            result = self.__super.page_from_obj (obj)
        else :
            result = d.page_from_obj (obj)
        return result
    # end def page_from_obj

    def _year_filter (self, y) :
        return (Q.year == y, )
    # end def _year_filter

E_Type_Archive_Y = TOP_MOM_E_Type_Archive_Y # end class

if __name__ != "__main__" :
    GTW.RST.TOP.MOM._Export_Module ()
### __END__ GTW.RST.TOP.MOM.Display
