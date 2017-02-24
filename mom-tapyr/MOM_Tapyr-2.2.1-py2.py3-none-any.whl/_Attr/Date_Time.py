# -*- coding: utf-8 -*-
# Copyright (C) 2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package MOM.Attr.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    MOM.Attr.Date_Time
#
# Purpose
#    Attribute types for date, datetime, and time
#
# Revision Dates
#    19-Jul-2016 (CT) Creation
#    29-Jul-2016 (CT) Add `A_Time.Pickler` to convert `datetime.time`
#     9-Sep-2016 (CT) Add `A_Time.completer`
#    21-Sep-2016 (CT) Add `A_Time_X`, factor `_A_DT_`, `_A_Time_`
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _MOM                  import MOM
from   _TFL                  import TFL
from   _TFL.pyk              import pyk

from   _MOM._Attr.Type       import *
from   _MOM._Attr.Structured import *
from   _MOM._Attr            import Attr

from   _TFL.I18N             import _, _T
from   _TFL.Regexp           import *

import datetime
import itertools
import logging
import time

class _A_DT_ (_A_Structured_) :
    """Common base class for date-valued and time-valued attributes of an object."""

    needs_raw_value    = False
    range_inclusive_p  = True
    _tuple_off         = 0

    @property
    def output_format (self) :
        return self._output_format ()
    # end def output_format

    def as_code (self, value) :
        return self.__super.as_code (self.as_string (value))
    # end def as_code

    @TFL.Meta.Class_and_Instance_Method
    def as_string (soc, value) :
        if value is not None :
            return pyk.text_type (value.strftime (soc._output_format ()))
        return ""
    # end def as_string

    @TFL.Meta.Class_and_Instance_Method
    def value_range (soc, head, tail, obj) :
        ### `value_range` is inclusive
        from _CAL._DTW_ import _DTW_
        import _CAL.Date_Time
        d = soc.value_range_delta (obj)
        n = _DTW_.new_dtw (head)
        t = _DTW_.new_dtw (tail)
        if not soc.range_inclusive_p :
            t -= d
        while n <= t :
            yield n._body
            try :
                n += d
            except OverflowError :
                break
    # end def value_range

    @TFL.Meta.Class_and_Instance_Method
    def _from_string (soc, s, obj = None) :
        s = s.strip ()
        if s :
            for f in soc.input_formats :
                try :
                    result = time.strptime (s, f)
                except ValueError :
                    pass
                else :
                    break
            else :
                raise MOM.Error.Attribute_Syntax (obj, soc, s)
            return soc.P_Type (* result [soc._tuple_off:soc._tuple_len])
    # end def _from_string

    @TFL.Meta.Class_and_Instance_Method
    def _output_format (soc) :
        return soc.input_formats [0]
    # end def _output_format

# end class _A_DT_

class _A_Date_ (_A_DT_) :
    """Common base class for date-valued attributes of an object."""

    not_in_future      = False
    not_in_past        = False

    class _Attributes (_A_DT_._Attributes) :

        class day (A_Int) :
            """Day specified by date."""

            kind               = Attr.Query
            query              = Q.day

        # end class day

        class month (A_Int) :
            """Month specified by date."""

            kind               = Attr.Query
            query              = Q.month

        # end class month

        class year (A_Int) :
            """Year specified by date."""

            kind               = Attr.Query
            query              = Q.year

        # end class year

    # end class _Attributes

    class _Doc_Map_ (_A_DT_._Doc_Map_) :

        not_in_future = """
            A true value of `not_in_future` means that the date/time value of
            the attribute must not lie in the future at the moment it is set.
        """

        not_in_past = """
            A true value of `not_in_past` means that the date/time value of
            the attribute must not lie in the past at the moment it is set.
        """

    # end class _Doc_Map_

    def _checkers (self, e_type, kind) :
        for c in self.__super._checkers (e_type, kind) :
            yield c
        if self.not_in_future :
            name   = self.name
            p_name = "%s__not_in_future" % name
            check  = MOM.Pred.Condition.__class__ \
                ( p_name, (MOM.Pred.Condition, )
                , dict
                    ( assertion  = "%s <= now" % (name, )
                    , attributes = (name, )
                    , bindings   = dict
                        ( now    = "Q.%s.NOW" % (self.Q_Name, )
                        )
                    , kind       = MOM.Pred.Object
                    , name       = p_name
                    , __doc__    = _ ("Value must not be in the future")
                    )
                )
            yield check
        if self.not_in_past :
            name   = self.name
            p_name = "%s__not_in_past" % name
            check  = MOM.Pred.Condition.__class__ \
                ( p_name, (MOM.Pred.Condition, )
                , dict
                    ( assertion  = "%s >= now" % (name, )
                    , attributes = (name, )
                    , bindings   = dict
                        ( now    = "Q.%s.NOW" % (self.Q_Name, )
                        )
                    , guard      = "not playback_p"
                    , guard_attr = ("playback_p", )
                    , kind       = MOM.Pred.Object_Init
                    , name       = p_name
                    , __doc__    =
                        _ ("Value must be in the future, not the past")
                    )
                )
            yield check
    # end def _checkers

# end class _A_Date_

class _A_Time_ (_A_DT_) :
    """Common base class for time-valued attributes of an object."""

    example        = "06:42"
    completer      = MOM.Attr.Completer_Spec (2)
    typ            = _ ("Time")
    P_Type         = datetime.time
    Q_Ckd_Type     = MOM.Attr.Querier.Time
    Q_Name         = "TIME"
    ui_length      = 8
    _midnight_pat  = Regexp (r"^24(:00){0,2}$")
    _tuple_len     = 6
    _tuple_off     = 3

    class _Attributes (_A_DT_._Attributes) :

        class hour (A_Int) :
            """Hour specified by time."""

            kind               = Attr.Query
            query              = Q.hour

        # end class hour

        class minute (A_Int) :
            """Minute specified by time."""

            kind               = Attr.Query
            query              = Q.minute

        # end class minute

        class second (A_Int) :
            """Second specified by time."""

            kind               = Attr.Query
            query              = Q.second

        # end class second

    # end class _Attributes

    class Pickler (TFL.Meta.Object) :

        Type = datetime.time

        @classmethod
        def as_cargo (cls, attr_kind, attr_type, value) :
            return value
        # end def as_cargo

        @classmethod
        def from_cargo (cls, scope, attr_kind, attr_type, cargo) :
            if cargo is not None :
                if isinstance (cargo, datetime.datetime) :
                    cargo = cargo.time ()
                return cargo
        # end def from_cargo

    # end class Pickler

    def as_rest_cargo_ckd (self, obj, * args, ** kw) :
        value = self.kind.get_value (obj)
        if value is not None :
            return pyk.text_type (value.strftime ("%H:%M:%S"))
    # end def as_rest_cargo_ckd

    @TFL.Meta.Class_and_Instance_Method
    def as_string (soc, value) :
        if value is not None and value == soc.P_Type.max :
            result = "24:00"
        else :
            ### when called for the class, `soc.__super` doesn't
            ### work while `super (_A_Time_, soc)` does
            result = super (_A_Time_, soc).as_string (value)
            if result.endswith (":00") :
                result = result [:-3]
        return result
    # end def as_string

    @TFL.Meta.Class_and_Instance_Method
    def cooked (soc, value) :
        if isinstance (value, datetime.datetime) :
            value = value.time ()
        elif isinstance (value, pyk.string_types) :
            try :
                value = soc._from_string (value)
            except ValueError :
                raise TypeError (_T ("Time expected, got %r") % (value, ))
        elif not isinstance (value, datetime.time) :
            raise TypeError (_T ("Time expected, got %r") % (value, ))
        return value
    # end def cooked

    @classmethod
    def now (cls) :
        return datetime.datetime.now ().time ()
    # end def now

    @TFL.Meta.Class_and_Instance_Method
    def value_range_delta (soc, obj) :
        from _CAL.Delta import Time_Delta
        return Time_Delta (1)
    # end def value_range_delta

    @TFL.Meta.Class_and_Instance_Method
    def _from_string (soc, value, obj = None) :
        try :
            return super (_A_Time_, soc)._from_string (value, obj)
        except Exception :
            if soc._midnight_pat.match (value) :
                return soc.P_Type.max
            raise
    # end def _from_string

# end class _A_Time_

class A_Date (_A_Date_) :
    """Date value."""

    example        = "2010-10-10"
    completer      = MOM.Attr.Completer_Spec  (4)
    typ            = _ ("Date")
    P_Type         = datetime.date
    Q_Ckd_Type     = MOM.Attr.Querier.Date
    Q_Name         = "DATE"
    syntax         = _ ("yyyy-mm-dd")
    ui_length      = 12
    input_formats  = \
        ( "%Y-%m-%d", "%Y/%m/%d", "%Y%m%d", "%Y %m %d"
        , "%d/%m/%Y", "%d.%m.%Y", "%d-%m-%Y"
        )
    _tuple_len     = 3

    class _Doc_Map_ (_A_Date_._Doc_Map_) :

        input_formats = """
            The possible strftime-formats used to convert raw values to cooked
            values.
        """

    # end class _Doc_Map_

    def as_rest_cargo_ckd (self, obj, * args, ** kw) :
        value = self.kind.get_value (obj)
        if value is not None :
            return pyk.text_type (value.strftime ("%Y-%m-%d"))
    # end def as_rest_cargo_ckd

    @TFL.Meta.Class_and_Instance_Method
    def cooked (soc, value) :
        if isinstance (value, datetime.datetime) :
            value = value.date ()
        elif isinstance (value, pyk.string_types) :
            try :
                value = soc._from_string (value)
            except ValueError :
                msg = "Date expected, got %r" % (value, )
                raise MOM.Error.Attribute_Syntax (None, soc, value, msg)
        elif not isinstance (value, datetime.date) :
            raise TypeError ("Date expected, got %r" % (value, ))
        return value
    # end def cooked

    @classmethod
    def now (cls) :
        return datetime.datetime.now ().date ()
    # end def now

    @TFL.Meta.Class_and_Instance_Method
    def value_range_delta (self, obj) :
        from _CAL.Delta import Date_Delta
        return Date_Delta (1)
    # end def value_range_delta

# end class A_Date

class A_Date_List (_A_Typed_List_) :
    """List of dates."""

    typ            = _ ("Date_List")
    C_Type         = A_Date

# end class A_Date_List

class A_Time (_A_Time_) :
    """Time value."""

    syntax         = _ ("hh:mm:ss, the seconds `ss` are optional")
    input_formats  = ("%H:%M:%S", "%H:%M")

# end class A_Time

class A_Time_X (_A_Time_) :
    """Time value."""

    syntax         = _ \
        ("hh:mm:ss, the minutes `mm` and seconds `ss` are optional")
    input_formats  = ("%H:%M:%S", "%H:%M", "%M")

# end class A_Time_X

class A_Time_List (_A_Typed_List_) :
    """List of times."""

    typ            = _ ("Time_List")
    C_range_sep    = Regexp (r"(?: ?(?:-|–|\.\.) ?)")
    C_Type         = A_Time

# end class A_Time_List

class A_Date_Time (_A_Date_) :
    """Date-time value."""

    example        = "2010-10-10 06:42"
    typ            = _ ("Date-Time")
    P_Type         = datetime.datetime
    Q_Name         = "DATE_TIME"
    syntax         = _ ("yyyy-mm-dd hh:mm:ss, the time `hh:mm:ss` is optional")
    ui_length      = 22
    rfc3339_format = "%Y-%m-%dT%H:%M:%S"
    input_formats  = tuple \
        ( itertools.chain
            ( * (  (f + " %H:%M:%S", f + " %H:%M", f)
                for f in A_Date.input_formats
                )
            )
        ) + (rfc3339_format, )
    utcoffset_fmt  = "%+03d:%02d"
    utcoffset_pat  = Regexp (r" *[-+](?P<oh>\d{2}):(?P<om>\d{2}) *$")
    _tuple_len     = 6

    ### plain old inheritance doesn't work here because
    ### _M_Structured_ doesn't support that
    _Attributes = _A_Date_._Attributes.__class__ \
        ( "_Attributes"
        , (_A_DT_._Attributes, )
        , dict (_A_Date_._Attributes.__dict__, ** _A_Time_._Attributes.__dict__)
        )

    def as_rest_cargo_ckd (self, obj, * args, ** kw) :
        ### formatted according to ISO 8601, RFC 3339
        value = self.kind.get_value (obj)
        if value is not None :
            offset = TFL.user_config.time_zone.utcoffset (value)
            v      = value + offset
            oh, os = divmod (offset.total_seconds (), 3600)
            om     = os // 60
            fmt    = self.rfc3339_format + (self.utcoffset_fmt % (oh, om))
            return v.strftime (fmt)
    # end def as_rest_cargo_ckd

    @TFL.Meta.Class_and_Instance_Method
    def as_string (soc, value) :
        if value is not None :
            ### In Python 3.5, `bool (t)` is never False -> compare to `t.min`
            v   = value + TFL.user_config.time_zone.utcoffset (value)
            t   = v.time ()
            fmt = A_Date.input_formats [0] if t == t.min \
                else soc._output_format ()
            result = v.strftime (fmt)
            if result.endswith (":00") :
                result = result [:-3]
            return result
        return ""
    # end def as_string

    @TFL.Meta.Class_and_Instance_Method
    def cooked (soc, value) :
        if not isinstance (value, datetime.datetime) :
            if isinstance (value, datetime.date) :
                value = datetime.datetime (value.year, value.month, value.day)
            elif isinstance (value, pyk.string_types) :
                try :
                    value = soc._from_string (value)
                except ValueError :
                    raise TypeError \
                        (_T ("Date/time expected, got %r") % (value, ))
            else :
                raise TypeError (_T ("Date/time expected, got %r") % (value, ))
        return value
    # end def cooked

    @classmethod
    def now (cls) :
        return datetime.datetime.utcnow ()
    # end def now

    @TFL.Meta.Class_and_Instance_Method
    def value_range_delta (self, obj) :
        from _CAL.Delta import Date_Time_Delta
        return Date_Time_Delta (1)
    # end def value_range_delta

    @TFL.Meta.Class_and_Instance_Method
    def _from_string (soc, s, obj = None) :
        utcoffset     = None
        utcoffset_pat = soc.utcoffset_pat
        if utcoffset_pat.search (s) :
            oh        = int (utcoffset_pat.oh)
            om        = int (utcoffset_pat.om)
            s         = s [: utcoffset_pat.start ()]
            utcoffset = datetime.timedelta (0, (oh * 60 + om) * 60)
        result  = super (A_Date_Time, soc)._from_string (s, obj)
        if utcoffset is None :
            utcoffset = TFL.user_config.time_zone.utcoffset (result)
        result -= utcoffset
        return result
    # end def _from_string

# end class A_Date_Time

class A_Date_Time_List (_A_Typed_List_) :
    """List of date/time elements."""

    typ            = _ ("Date_Time_List")
    C_Type         = A_Date_Time

# end class A_Date_Time_List

__sphinx__members  = attr_types_of_module ()
__all__            = __sphinx__members

if __name__ != "__main__" :
    MOM.Attr._Export (* __all__)
### __END__ MOM.Attr.Date_Time
