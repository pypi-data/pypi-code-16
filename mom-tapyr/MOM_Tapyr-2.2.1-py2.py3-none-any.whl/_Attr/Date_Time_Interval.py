# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package MOM.Attr.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    MOM.Attr.Date_Time_Interval
#
# Purpose
#    Composite attribute type for date interval (start, finish)
#
# Revision Dates
#    11-Jan-2013 (CT) Creation
#    25-Feb-2013 (CT) Remove `alive.auto_up_depends`
#    17-Apr-2013 (CT) Use `Computed_Set_Mixin`, not `Computed_Mixin`
#     5-Jun-2013 (CT) Use `is_attr_type`, not home-grown code
#    11-Dec-2015 (CT) Use `attr_types_of_module`, not home-grown code
#    ««revision-date»»···
#--

from   __future__            import unicode_literals

from   _MOM.import_MOM       import *
from   _MOM.import_MOM       import _A_Composite_

from   _TFL.I18N             import _, _T, _Tn
from   _TFL.pyk              import pyk

_Ancestor_Essence = MOM.An_Entity

@pyk.adapt__bool__
class Date_Time_Interval (_Ancestor_Essence) :
    """Model a date interval (start, finish)."""

    ui_display_sep = " - "

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class alive (A_Boolean) :
            """Specifies whether entity is currently alive, i.e., the current
               date lies between `start` and `finish`.
            """

            kind               = Attr.Query
            ### need to recompute each time `alive` is accessed
            Kind_Mixins        = (Attr.Computed, )

            def query_fct (self) :
                now = A_Date_Time.now ()
                return \
                    ( ((Q.start  == None) | (Q.start <= now))
                    & ((Q.finish == None) | (now <= Q.finish))
                    )
            # end def query_fct

        # end class alive

        class days (A_Int) :
            """Length of interval in days."""

            kind               = Attr.Cached
            Kind_Mixins        = (Attr.Computed_Set_Mixin, )
            auto_up_depends    = ("finish", "start")

            def computed (self, obj) :
                if obj.start :
                    result = 1
                    if obj.finish :
                        result += (obj.finish - obj.start).days
                    return result
            # end def computed

        # end class days

        class finish (A_Date_Time) :
            """Finish date of interval"""

            kind               = Attr.Optional
            example            = "2038-01-19"
            rank               = 2

        # end class finish

        class start (A_Date_Time) :
            """Start date of interval"""

            kind               = Attr.Necessary
            example            = "1970-01-01"
            rank               = 1

        # end class start

    # end class _Attributes

    class _Predicates (_Ancestor_Essence._Predicates) :

        _Ancestor = _Ancestor_Essence._Predicates

        class finish_after_start (Pred.Condition) :
            """The finish date must be later than the start date"""

            kind               = Pred.Object
            assertion          = "start <= finish"
            attributes         = ("start", "finish")

        # end class finish_after_start

    # end class _Predicates

    @property
    def ui_display_format (self) :
        attrs = [self.__class__.start]
        if self.finish and self.finish != self.start :
            attrs.append (self.__class__.finish)
        return self.ui_display_sep.join ("%%(%s)s" % a.name for a in attrs)
    # end def ui_display_format

    def __bool__ (self) :
        return self.start is not None
    # end def __bool__

# end class Date_Time_Interval

class A_Date_Time_Interval (_A_Composite_) :
    """Date-time interval (start, finish)."""

    P_Type         = Date_Time_Interval
    typ            = "Date_Time_Interval"

# end class A_Date_Time_Interval

class A_Date_Time_Interval_C (A_Date_Time_Interval) :
    """Date-time interval (start, finish [default: `start`])."""

    class _Attributes :

        def computed__finish (self, obj) :
            if obj and obj.start :
                return obj.start
        # end def computed__finish

        _Overrides = dict \
            ( finish = dict
                ( Kind_Mixins = (Attr.Computed_Set_Mixin, )
                , computed    = computed__finish
                )
            )

    # end class _Attributes

# end class A_Date_Time_Interval_C

class A_Date_Time_Interval_N (A_Date_Time_Interval) :
    """Date-time interval (start [default: now], finish)."""

    class _Attributes :

        _Overrides = dict \
            ( start  = dict
                ( Kind_Mixins      = (Attr.Sticky_Mixin, )
                , computed_default = A_Date_Time.now
                )
            )

    # end class _Attributes

# end class A_Date_Time_Interval_N

__attr_types      = Attr.attr_types_of_module ()
__sphinx__members = ("Date_Time_Interval", ) + __attr_types

if __name__ != "__main__" :
    MOM.Attr._Export (* __attr_types)
### __END__ MOM.Attr.Date_Interval
