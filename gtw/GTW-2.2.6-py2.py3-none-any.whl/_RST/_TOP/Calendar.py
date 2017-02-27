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
#    GTW.RST.TOP.Calendar
#
# Purpose
#    Page displaying a calendar
#
# Revision Dates
#     2-Aug-2012 (CT) Creation (based on GTW.NAV.Calendar)
#     2-Aug-2012 (CT) Redefine `Calendar.Day.rendered` to handle `qx`
#     3-Aug-2012 (CT) Factor `_render_macro`, add `Calendar.Q`
#     6-Aug-2012 (CT) Replace `_do_change_info_skip` by `skip_etag`
#     6-Aug-2012 (MG) Consider `hidden`in  `is_current_dir`
#     9-Aug-2012 (CT) Fix `is_current_dir` (test for "/" after `startswith`)
#    10-Aug-2012 (CT) Move `_Cal_Page_.is_current_dir` to
#                     `Calendar.is_current_page`
#    22-Jan-2013 (CT) Remove spurious `handler.`
#     6-Apr-2013 (CT) Fix typo
#    24-Feb-2014 (CT) Add `_Event_Wrapper_`
#    26-Feb-2014 (CT) Remove `nav_off_canvas`
#     5-Apr-2015 (CT) Fix typo
#     8-Oct-2015 (CT) Change `__getattr__` to *not* handle `__XXX__`
#    14-Oct-2015 (CT) Change `_Event_Wrapper_` to apply `text_type` to `date`
#                     and `time`
#     1-Dec-2016 (CT) Use `CAL.G8R...words`, not home-grown definitions
#    ««revision-date»»···
#--

from   __future__ import absolute_import, division, print_function, unicode_literals

from   _CAL                       import CAL
from   _GTW                       import GTW
from   _TFL                       import TFL

import _CAL.Calendar
import _CAL.Delta
import _CAL.G8R

import _GTW._RST.HTTP_Method
import _GTW._RST._TOP.Dir
import _GTW._RST._TOP.Page

from   _TFL.defaultdict           import defaultdict_kd
from   _TFL.Decorator             import getattr_safe
from   _TFL.I18N                  import _, _T, _Tn
from   _TFL.pyk                   import pyk
from   _TFL.Regexp                import Regexp, re
from   _TFL._Meta.Once_Property   import Once_Property
from   _TFL._Meta.Single_Dispatch import Single_Dispatch

import datetime
from   posixpath                  import join  as pp_join

@Single_Dispatch
def event_short_title (ev_obj) :
    return getattr (ev_obj, "short_title", ev_obj.ui_display)
# end def event_short_title

@Single_Dispatch
def event_title (ev_obj) :
    return getattr (ev_obj, "title", "")
# end def event_title

class _Event_Wrapper_ (TFL.Meta.Object) :
    """Wrapper around `EVT.Event_occurs` instance"""

    def __init__ (self, cal, event_occurs) :
        self._cal      = cal
        self._instance = event_occurs
    # end def __init__

    @Once_Property
    def date (self) :
        return pyk.text_type (self._instance.FO.date)
    # end def date

    @Once_Property
    def detail (self) :
        result = self._instance.detail
        return result
    # end def detail

    @property
    def FO (self) :
        return self
    # end def FO

    @Once_Property
    def short_title (self) :
        result = self._instance.short_title
        if not result :
            result = event_short_title (self.essence)
        return result
    # end def short_title

    @Once_Property
    def target_href (self) :
        target_resource = self.target_resource
        if target_resource is not None :
            return target_resource.abs_href
    # end def target_href

    @Once_Property
    def target_resource (self) :
        return self._cal.page_from_obj (self.essence)
    # end def target_resource

    @Once_Property
    def time (self) :
        return pyk.text_type (self._instance.FO.time)
    # end def time

    @Once_Property
    def title (self) :
        result = event_title (self.essence)
        return result
    # end def title

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        result = getattr (self._instance, name)
        setattr (self, name, result)
        return result
    # end def __getattr__

# end class _Event_Wrapper_

class _Mixin_ (GTW.RST.TOP._Base_) :

    @property
    @getattr_safe
    def weeks (self) :
        n = self.week_roller_size
        w = self.anchor.wk_ordinal
        return [self._cal.week [i] for i in range (w - 1, w + n - 1)]
    # end def weeks

# end class _Mixin_

_Ancestor = GTW.RST.TOP.Page

class _Cal_Page_ (_Ancestor) :

    args               = (None, )
    implicit           = True
    nav_off_canvas     = False
    skip_etag          = True

    _exclude_robots    = True

    def _render_macro (self, t_name, m_name, * args) :
        T          = self.top.Templateer
        template   = T.get_template (t_name)
        call_macro = template.call_macro
        result     = call_macro (m_name, self, * args)
        return result
    # end def _render_macro

# end class _Cal_Page_

class _Day_ (_Cal_Page_) :
    """Page displaying calendary events for a specific day."""

    macro_name         = "day"
    page_template_name = "calendar_day"
    template_qx_name   = "calendar_day_qx"

    def rendered (self, context, template = None) :
        if self.qx_p :
            result = self._render_macro \
                (self.template_qx_name, self.macro_name, self.day)
        else :
            result = self.__super.rendered (context, template)
        return result
    # end def rendered

# end class _Day_

class _Q_ (_Mixin_, _Cal_Page_) :
    """Pseudo page handling queries."""

    args               = 0
    macro_name         = "week_roller_body"
    page_template_name = "calendar"
    template_qx_name   = "calendar_qx"

    def rendered (self, context, template = None) :
        anchor   = self.anchor
        method   = context ["http_method"]
        request  = context ["request"]
        response = context ["response"]
        try :
            qa   = self._q_args (anchor, request)
        except Exception as exc :
            raise self.Status.Not_Found (exc)
        if qa.anchor == self.anchor :
            this = self
        else :
            this = context ["page"] = self.__class__ \
                ( parent = self
                , anchor = qa.anchor
                )
        with this.LET (week_roller_size = qa.week_roller_size) :
            if this.qx_p :
                response.renderer = GTW.RST.Mime_Type.JSON (method, this)
                result = dict \
                    ( calendar = this._render_macro
                        (this.template_qx_name, this.macro_name, this.weeks)
                    , day      = anchor.day
                    , month    = anchor.month
                    , weeks    = this.week_roller_size
                    , year     = anchor.year
                    )
            else :
                result = this.__super.rendered (context, template)
        return result
    # end def rendered

    def _q_args (self, anchor, request) :
        req_data   = request.req_data
        if req_data.get ("Today") :
            anchor = self.today
        else :
            y      = int (req_data.get ("year")  or anchor.year)
            m      = int (req_data.get ("month") or anchor.month)
            d      = int (req_data.get ("day")   or anchor.day)
            anchor = self._cal.day ["%4.4d/%2.2d/%2.2d" % (y, m, d)]
            if req_data.get ("delta") :
                delta  = self._q_delta (req_data)
                anchor = self._cal.day [(anchor.date + delta).ordinal]
        wrs = int (req_data.get ("weeks") or self.week_roller_size)
        return TFL.Record \
            ( anchor           = anchor
            , week_roller_size = wrs
            )
    # end def _q_args

    def _q_delta (self, req_data) :
        number = int (req_data.get ("delta"))
        unit   = req_data.get ("delta_unit", "week").rstrip ("s")
        if unit in ("month", "year") :
            DT = CAL.Month_Delta
            if unit == "year" :
                number *= 12
        elif unit in ("week", "day") :
            DT = CAL.Date_Delta
            if unit == "week" :
                number *= 7
        else :
            raise ValueError (unit)
        return DT (number)
    # end def _q_delta

# end class _Q_

_Ancestor = GTW.RST.TOP.Dir_V

class _Year_ (_Cal_Page_) :
    """Page displaying calendar for a specific year."""

    nav_off_canvas      = True

    @property
    @getattr_safe
    def anchor (self) :
        return self._cal.day [datetime.date (self.year, 1, 1).toordinal ()]
    # end def anchor

# end class _Year_

_Ancestor = GTW.RST.TOP.Dir_V

class Calendar (_Mixin_, _Ancestor) :
    """Page displaying a calendar."""

    Day                = _Day_
    Q                  = _Q_
    Year               = _Year_

    dir_template_name  = "calendar"
    event_manager_name = "GTW.OMP.EVT.Event_occurs"
    page_template_name = "calendar"
    pid                = "Cal"
    skip_etag          = True
    week_roller_size   = 6
    year_window_size   = 3

    _cal               = None

    day_abbrs          = CAL.G8R.Week_Day_Abbrs_3.words
    day_names          = CAL.G8R.Week_Day_Names.words
    month_abbrs        = CAL.G8R.Month_Abbrs.words
    month_names        = CAL.G8R.Month_Names.words

    anchor             = property (TFL.Getter.today)

    def __init__ (self, ** kw) :
        self.calendar = self
        self.__super.__init__ (** kw)
        if self._cal is None :
            self.__class__._cal   = CAL.Calendar   ()
            self.__class__.events = defaultdict_kd (self._get_events)
            def _day_get_events (this) :
                return self.events [this.date.date]
            _CAL.Year.Day.events = property (_day_get_events)
    # end def __init__

    @Once_Property
    @getattr_safe
    def event_manager (self) :
        scope = self.top.scope
        if scope and self.event_manager_name :
            return scope [self.event_manager_name]
    # end def event_manager

    @property
    @getattr_safe
    def max_year (self) :
        return self.anchor.year + self.year_window_size
    # end def max_year

    @property
    @getattr_safe
    def min_year (self) :
        return self.anchor.year - self.year_window_size
    # end def min_year

    @property
    @getattr_safe
    def today (self) :
        return self._cal.day [datetime.date.today ().toordinal ()]
    # end def today

    @property
    @getattr_safe
    def year (self) :
        return self._cal.year [self.anchor.year]
    # end def year

    def day_href (self, day) :
        return pp_join (self.abs_href_dynamic, day.formatted ("%Y/%m/%d"))
    # end def day_href

    def is_current_page (self, page) :
        ### don't guard against hidden !!!
        p = page.href_dynamic
        s = self.calendar.href_dynamic
        return p == s or (p.startswith (s) and p [len (s)] == "/")
    # end def is_current_dir

    def _get_child (self, child, * grandchildren) :
        qx_p = child == self.qx_prefix
        if child in (self.q_prefix, self.qx_prefix) and not grandchildren :
            result = self.Q (name = child, parent = self, qx_p = qx_p)
        else :
            result = None
            if qx_p :
                child, grandchildren = grandchildren [0], grandchildren [1:]
            try :
                y = int (child)
            except ValueError :
                pass
            else :
                if self.min_year <= y <= self.max_year :
                    year = self._cal.year [y]
                    if not grandchildren :
                        if not qx_p :
                            result = self.Year (parent = self, year = year)
                    elif len (grandchildren) == 2 :
                        try :
                            m, d = [int (c) for c in grandchildren]
                            day  = year.dmap [y, m, d]
                        except (ValueError, LookupError) :
                            pass
                        else :
                            Day = self.Day
                            return Day \
                                ( day    = day
                                , name   = str (day)
                                , parent = self
                                , qx_p   = qx_p
                                , year   = year
                                )
        return result
    # end def _get_child

    def _get_events (self, date) :
        evm = self.event_manager
        return sorted \
            ( (_Event_Wrapper_ (self, ev) for ev in evm.query (date = date))
            , key = TFL.Sorted_By ("time", "short_title")
            )
    # end def _get_events

# end class Calendar

if __name__ != "__main__" :
    GTW.RST.TOP._Export ("*")
### __END__ GTW.RST.TOP.Calendar
