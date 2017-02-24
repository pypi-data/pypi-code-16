# -*- coding: utf-8 -*-
# Copyright (C) 2010-2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package GTW.OMP.EVT.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.OMP.EVT.Recurrence_Spec
#
# Purpose
#    Specification for recurrency of events
#
# Revision Dates
#     6-Sep-2010 (CT) Creation
#     7-Sep-2010 (CT) `_change_callback` added
#    18-Nov-2011 (CT) Import `unicode_literals` from `__future__`
#    14-May-2012 (CT) Replace `unit.C_Type` by `unit.P_Type`
#    17-Apr-2013 (CT) Use `Computed_Set_Mixin`, not `Computed_Mixin`
#    10-May-2013 (CT) Replace `auto_cache` by `link_ref_attr_name`
#    27-Jun-2013 (CT) Add `unit.C_Type`
#    ««revision-date»»···
#--

from   __future__            import unicode_literals

from   _MOM.import_MOM            import *
from   _MOM.import_MOM            import _A_Named_Value_
from   _MOM._Attr.Recurrence_Rule import \
    A_Unit_RR, A_Weekday_RR, A_Weekday_RR_List

from   _GTW                       import GTW

import _GTW._OMP._EVT.Entity
import _GTW._OMP._EVT.Event

from   _TFL.I18N                  import _, _T, _Tn
from   _TFL.pyk                   import pyk

import datetime
import dateutil.rrule

_Ancestor_Essence = GTW.OMP.EVT.Link1

class _Recurrence_Mixin_ (_Ancestor_Essence) :
    """Mixin for classes modelling recurrence rules."""

    occurrence_format = "%Y%m%d"
    is_partial        = True

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class ui_display (_Ancestor.ui_display) :

            def computed (self, obj) :
                if obj :
                    fmt = obj.occurrence_format
                    return ", ".join (o.strftime (fmt) for o in obj.occurrences)
            # end def computed

        # end class ui_display

    # end class _Attributes

# end class _Recurrence_Mixin_

_Ancestor_Essence = _Recurrence_Mixin_

class Recurrence_Spec (_Ancestor_Essence) :
    """Specification for recurrency of event."""

    ### http://labix.org/python-dateutil

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        ### Primary attributes

        class left (_Ancestor.left) :
            """Event that recurs"""

            role_type          = GTW.OMP.EVT.Event
            link_ref_attr_name = "recurrence"
            link_ref_singular  = True
            max_links          = 1

        # end class left

        ### Non-primary attributes

        class dates (A_Date_List) :
            """Dates included in the recurrence rule set."""

            kind               = Attr.Optional

        # end class dates

        class finish (A_Date) :

            kind               = Attr.Computed

            def computed (self, obj) :
                try :
                    result = obj.finish_getter (obj)
                except AttributeError as exc :
                    pass
                else :
                    if isinstance (result, MOM.Date_Interval) :
                        result = result.finish
                    return result
            # end def computed

        # end class finish

        class date_exceptions (A_Date_List) :
            """Dates excluded from the recurrence rule set."""

            kind               = Attr.Optional

        # end class date_exceptions

        class occurrences (A_Blob) :

            ### needs to be `Computed`, not `Auto_Cached` because result
            ### depends on `start_getter` and `finish_getter`
            kind      = Attr.Computed

            def computed (self, obj) :
                if obj :
                    result = dateutil.rrule.rruleset (cache = True)
                    for r in obj.rules :
                        m = (result.exrule if r.is_exception else result.rrule)
                        m (r.occurrences)
                    for d in obj.dates :
                        result.rdate \
                            (datetime.datetime.fromordinal (d.toordinal ()))
                    for x in obj.date_exceptions :
                        result.exdate \
                            (datetime.datetime.fromordinal (x.toordinal ()))
                    return result
            # end def computed

        # end class occurrences

        class start (A_Date) :

            kind               = Attr.Computed

            def computed (self, obj) :
                try :
                    result = obj.start_getter (obj)
                except AttributeError as exc :
                    pass
                else :
                    if isinstance (result, MOM.Date_Interval) :
                        result = result.start
                    return result
            # end def computed

        # end class start

    # end class _Attributes

    start_getter  = finish_getter = TFL.Getter.left.date

    _event_change_triggers = ("dates", "date_exceptions")

    def compute_occurrences (self) :
        self.event.compute_occurrences ()
    # end def compute_occurrences

    @classmethod
    def _change_callback (cls, scope, change) :
        if change.attr_changes.intersection (cls._event_change_triggers) :
            self = change.entity (scope)
            self.compute_occurrences ()
    # end def _change_callback

# end class Recurrence_Spec

MOM.SCM.Change.Create.add_callback \
    (Recurrence_Spec, Recurrence_Spec._change_callback)
MOM.SCM.Change.Attr.add_callback \
    (Recurrence_Spec, Recurrence_Spec._change_callback)

_Ancestor_Essence = _Recurrence_Mixin_

class Recurrence_Rule (_Ancestor_Essence) :
    """Recurrence rule specifying a set of dates to include or exclude."""

    ### http://www.ietf.org/rfc/rfc2445.txt

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        ### Primary attributes

        class left (_Ancestor.left) :
            """Recurrence-spec this rule applies to."""

            role_type          = Recurrence_Spec
            link_ref_attr_name = "rules"
            link_ref_suffix    = None

        # end class left

        class is_exception (A_Boolean) :
            """If true, exclude the dates specified by this rule."""

            kind               = Attr.Primary_Optional
            rank               = 10

        # end class is_exception

        class desc (A_String) :
            """Short description of the rule"""

            kind               = Attr.Primary_Optional
            max_length         = 20
            rank               = 20
            ui_name            = "Description"

        # end class desc

        ### Non-primary attributes

        class count (A_Int) :
            """Maximum number of recurrences."""

            kind               = Attr.Optional
            min_value          = 1
            rank               = -80

            rrule_name         = "count"

        # end class count

        class easter_offset (A_Int_List) :
            """Offset to Easter sunday (positive or negative, 0 means the
               Easter sunday itself).
            """

            kind               = Attr.Optional
            rank               = 100

            rrule_name         = "byeaster"

        # end class easter_offset

        class finish (A_Date) :
            """Finish date of the recurrence."""

            kind               = Attr.Optional
            Kind_Mixins        = (Attr.Computed_Set_Mixin, )
            rank               = -105

            rrule_name         = "until"

            def computed (self, obj) :
                try :
                    result = obj.left.finish
                except AttributeError as exc :
                    pass
                else :
                    if isinstance (result, MOM.Date_Interval) :
                        result = result.finish
                    return result
            # end def computed

        # end class finish

        class first_day_of_week (A_Weekday_RR) :
            """First day of week"""

            kind               = Attr.Const
            default            = dateutil.rrule.MO.weekday

            rrule_name         = "wkst"

        # end class first_day_of_week

        class month (A_Int_List) :
            """Restrict the recurrences to the months specified (1 means
               January, ...).
            """

            kind               = Attr.Optional
            rank               = -69

            rrule_name         = "bymonth"

        # end class month

        class month_day (A_Int_List) :
            """Restrict the recurrences to the days of the month specified.
               Negative numbers count from the end of the month
               (-1 means the last day of the month).
            """

            kind               = Attr.Optional
            rank               = -70

            rrule_name         = "bymonthday"

        # end class month_day

        class occurrences (A_Blob) :

            ### needs to be `Computed`, not `Auto_Cached` because result
            ### depends on `start_getter` and `finish_getter`
            kind      = Attr.Computed

            def computed (self, obj) :
                if obj :
                    kw = dict (obj._rrule_attrs ())
                    if obj.finish is None and obj.count is None :
                        kw ["count"] = 366 if obj.is_exception else 1
                    return dateutil.rrule.rrule (cache = True, ** kw)
            # end def computed

        # end class occurrences

        class period (A_Int) :
            """The interval (measured in `units`) between
               successive recurrences of an event.
            """

            kind               = Attr.Optional
            default            = 1
            min_value          = 1
            rank               = -100

            rrule_name         = "interval"

        # end class period

        class restrict_pos (A_Int_List) :
            """Restrict recurrences to the numbers given. Negative numbers
               count from the last occurrence (-1 meaning the last occurrence).
            """

            kind               = Attr.Optional
            rank               = -80

            rrule_name         = "bysetpos"

        # end class restrict_pos

        class start (A_Date) :
            """Start date of the recurrence."""

            kind               = Attr.Optional
            Kind_Mixins        = (Attr.Computed_Set_Mixin, )
            rank               = -110

            rrule_name         = "dtstart"

            def computed (self, obj) :
                try :
                    result = obj.left.start
                except AttributeError as exc :
                    pass
                else :
                    if isinstance (result, MOM.Date_Interval) :
                        result = result.start
                    return result
            # end def computed

        # end class start

        class unit (A_Unit_RR) :
            """Unit of recurrence. `period` is interpreted in units of
               `unit`.
            """

            kind               = Attr.Optional
            Kind_Mixins        = (Attr.Sticky_Mixin, )
            rank               = -99

            rrule_name         = "freq"

        # end class unit

        class week (A_Int_List) :
            """Restrict the recurrences to the week numbers specified."""

            kind               = Attr.Optional

            rrule_name         = "byweekno"

        # end class week

        class week_day (A_Weekday_RR_List) :
            """Restrict the recurrences to the days of the week specified.
               (0 means monday, 6 means sunday).
            """

            kind               = Attr.Optional
            rank               = -90

            rrule_name         = "byweekday"

        # end class week_day

        class year_day (A_Int_List) :
            """Restrict the recurrences to the days of the year specified.
               Negative numbers count from the end of the year
               (-1 means the last day of the year).
            """

            kind               = Attr.Optional

            rrule_name         = "byyearday"

        # end class year_day

    # end class _Attributes

    @classmethod
    def _change_callback (cls, scope, change) :
        self = change.entity (scope)
        self.left.compute_occurrences ()
    # end def _change_callback

    def _rrule_attrs (self) :
        for a in pyk.itervalues (self.attributes) :
            name = getattr (a, "rrule_name", None)
            if name :
                value = a.get_value (self)
                if value is not None and value != [] :
                    yield name, value
    # end def _rrule_attrs

# end class Recurrence_Rule

MOM.SCM.Change.Create.add_callback \
    (Recurrence_Rule, Recurrence_Rule._change_callback)
MOM.SCM.Change.Attr.add_callback \
    (Recurrence_Rule, Recurrence_Rule._change_callback)

if __name__ != "__main__" :
    GTW.OMP.EVT._Export ("*")
### __END__ GTW.OMP.EVT.Recurrence_Spec
