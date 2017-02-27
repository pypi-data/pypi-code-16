# -*- coding: utf-8 -*-
# Copyright (C) 2010-2016 Mag. Christian Tanzer All rights reserved
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
#    MOM.Attr.Recurrence_Rule
#
# Purpose
#    Composite attribute type for recurrence rule
#
# Revision Dates
#    10-Mar-2010 (CT) Creation
#    10-Mar-2010 (MG) `unit.C_Type` added
#    12-Mar-2010 (CT) `A_Weekday_RR_List` added and used
#    15-Mar-2010 (CT) Interface of `attr.Pickler` changed again (`attr_type`)
#    15-Mar-2010 (CT) `A_Weekday_RR._from_string_eval` redefined
#    16-Mar-2010 (CT) Bugs fixed (`__nonzero__`, `easter_offset.rrule_name`,
#                     `finish` or `count`, ...)
#    27-Apr-2010 (CT) Default for `glob` and `locl` changed from `None` to `{}`
#     7-Jun-2010 (CT) `A_Weekday_RR.Pickler` methods guarded against `None`
#    18-Aug-2010 (CT) Attributes `dates`, `finish`, and `start` added; method
#                     `rule` removed
#    18-Aug-2010 (CT) `unit.default` changed from `Weekly` to `Daily`
#    18-Aug-2010 (CT) `Recurrence_Rule_Set` added
#    19-Aug-2010 (CT) `_Recurrence_Rule_Mixin_` added to define `ui_display`
#    19-Aug-2010 (CT) `__nonzero__` factored to `An_Entity`
#    19-Aug-2010 (CT) `count_default` added
#     2-Sep-2010 (CT) Signatures of `Pickler.as_cargo` and `.from_cargo` changed
#     4-Sep-2010 (CT) s/owner/owner.owner/ where necessary (change of
#                     _A_Composite_Collection_)
#    13-Oct-2010 (CT) `example` added
#    18-Nov-2011 (CT) Import `unicode_literals` from `__future__`
#     7-Jun-2012 (CT) Use `TFL.r_eval`
#     5-Jun-2013 (CT) Use `is_attr_type`, not home-grown code
#    11-Dec-2015 (CT) Use `attr_types_of_module`, not home-grown code
#     7-Feb-2016 (CT) Derive `A_Weekday_RR.Pickler` from `Pickler_As_String`
#    15-Feb-2016 (CT) Remove spurious import of `datetime`
#    15-Feb-2016 (CT) Use `CAL.G8R.Week_Days` to allow localized weekday names
#    28-Apr-2016 (CT) Remove `glob`, `locl` from `from_string`, `_from_string`
#    28-Apr-2016 (CT) Convert `_from_string` to `Class_and_Instance_Method`
#    28-Apr-2016 (CT) Add `value_range`
#    15-Jun-2016 (CT) Add `A_Unit_RR`
#    30-Nov-2016 (CT) Use `CAL.G8R.Months.LC`, not `CAL.G8R.Months`
#     1-Dec-2016 (CT) Use `CAL.G8R.Recurrence_Units.words`, not home-grown
#                     definitions
#    ««revision-date»»···
#--

from   __future__            import unicode_literals

from   _CAL                  import CAL
from   _MOM.import_MOM       import *
from   _MOM.import_MOM       import \
     ( _A_Binary_String_
     , _A_Named_Value_
     , _A_Typed_List_
     )

import _CAL.G8R

from   _TFL.I18N             import _, _T, _Tn
from   _TFL.pyk              import pyk
import _TFL.r_eval

import dateutil.rrule

class A_Unit_RR (_A_Named_Value_) :
    """Unit of recurrence. """

    P_Type             = int
    C_Type             = A_Int
    Table              = dict \
        (  (k, getattr (dateutil.rrule, k.upper ()))
        for k in CAL.G8R.Recurrence_Units.words
        )
    typ                = "Unit"
    default            = Table ["Daily"]
    max_value          = len (Table)

    @TFL.Meta.Class_and_Instance_Method
    def _from_string (soc, s, obj = None) :
        v = CAL.G8R.Recurrence_Units.LC.globalized (s).capitalize ()
        ### when called for the class, `soc.__super` doesn't
        ### work while `super (A_Unit_RR, soc)` does
        return super (A_Unit_RR, soc)._from_string (v)
    # end def _from_string

# end class A_Unit_RR

class A_Weekday_RR (A_Attr_Type) :
    """Weekday specification in recurrence rule."""

    example            = u"Tu"
    typ                = "Weekday_RR"

    P_Type             = dateutil.rrule.weekday
    Names              = CAL.G8R.Week_Day_Abbrs_2.words
    Table              = dict \
        ((k, getattr (dateutil.rrule, k.upper ())) for k in Names)

    class Pickler (Pickler_As_String) :

        class Type (_A_Binary_String_) :
            max_length = 8
        # end class Type

    # end class Pickler

    @TFL.Meta.Class_and_Instance_Method
    def as_string (soc, value) :
        if value is not None :
            return repr (value)
        return u""
    # end def as_string

    as_code = as_string

    @TFL.Meta.Class_and_Instance_Method
    def cooked (soc, value) :
        if isinstance (value, int) :
            value = soc.Table [soc.Names [value]]
        elif isinstance (value, pyk.string_types) :
            v = CAL.G8R.Week_Days.LC.globalized (value)
            value = soc.Table [v]
        if value is not None and not isinstance (value, soc.P_Type) :
            raise ValueError \
                ( _T ("Value `%r` is not of type %s") % (value, soc.P_Type)
                + "\n    %s" % ", ".join (soc.Names)
                )
        return value
    # end def cooked

    @TFL.Meta.Class_and_Instance_Method
    def value_range (soc, h, t, obj) :
        Names = soc.Names
        l     = len (Names)
        n     = h.weekday
        tail  = (t.weekday + 1) % l ### `value_range` is inclusive
        while n != tail :
            yield n
            n = (n + 1) % l
    # end def value_range

    @TFL.Meta.Class_and_Instance_Method
    def _from_string (soc, s, obj = None) :
        if s :
            v = CAL.G8R.Week_Days.LC.globalized (s).capitalize ()
            return soc.cooked (soc._call_eval (v, ** soc.Table))
    # end def _from_string

# end class A_Weekday_RR

class A_Weekday_RR_List (_A_Typed_List_) :
    """A list of weekday specifications in recurrence rule"""

    typ         = "Weekday_RR_List"
    C_Type      = A_Weekday_RR

# end class A_Weekday_RR_List

__attr_types      = Attr.attr_types_of_module ()
__sphinx__members = __attr_types

if __name__ != "__main__" :
    MOM.Attr._Export (* __attr_types)
### __END__ MOM.Attr.Recurrence_Rule
