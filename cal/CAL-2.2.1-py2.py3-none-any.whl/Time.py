# -*- coding: utf-8 -*-
# Copyright (C) 2004-2016 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    CAL.Time
#
# Purpose
#    Wrapper around `datetime.time`
#
# Revision Dates
#    15-Oct-2004 (CT) Creation
#    17-Oct-2004 (CT) `Time.Delta` defined as `Time_Delta`
#    17-Oct-2004 (CT) Adapted to renaming of accessor-functions of `Time_Delta`
#    30-Nov-2006 (CT) `__getattr__` for `seconds` added
#     7-Nov-2007 (CT) Use `Getter` instead of `lambda`
#     9-Nov-2007 (CT) Use `Once_Property` instead of `__getattr__`
#    11-Nov-2007 (CT) `from_degrees` added
#    11-Nov-2007 (CT) `from_decimal_hours` factored
#    13-Nov-2007 (CT) `as_degrees` added
#    14-Nov-2007 (CT) `hh_mm` added
#     4-Aug-2008 (MG) `from_string` added
#    29-Mar-2012 (CT) Add support for `tzinfo`, factor `_from_string_match_kw`
#    28-Feb-2014 (CT) Use future `print_function`
#    17-Jun-2016 (CT) Change `__sub__` to allow delta values, too
#    20-Jul-2016 (CT) Change `Time.pattern` to bare `hour` without any `minute`
#    26-Sep-2016 (CT) Correct `microsecond` in `from_decimal_hours`, `seconds`
#    ««revision-date»»···
#--

from   __future__               import print_function

from   _CAL                     import CAL
from   _TFL                     import TFL

import _CAL._DTW_
import _TFL.Accessor

from   _TFL.pyk                 import pyk
from   _TFL.Regexp              import *
from   _TFL._Meta.Once_Property import Once_Property

import  datetime

class Time (CAL._DTW_) :
    """Model a time object.

       >>> t1 = Time (21, 35, 12)
       >>> print (t1)
       21:35:12
       >>> t1.hour, t1.minute, t1.second, t1.time, t1.seconds
       (21, 35, 12, datetime.time(21, 35, 12), 77712)
       >>> t2 = Time (22, 47, 13)
       >>> print (t2, t2.seconds)
       22:47:13 82033
       >>> t1 = Time (14, 30, 0)
       >>> t2 = Time (16, 30, 0)
       >>> d  = t2 - t1
       >>> print (d)
       2:00:00
       >>> print (t1 - d)
       12:30:00
       >>> print (t2 + d)
       18:30:00
       >>> from _CAL.Delta import Time_Delta as Delta
       >>> try :
       ...     t1 + Delta (hours = 10)
       ... except OverflowError as exc :
       ...     print (exc)
       ...
       1 day, 0:30:00
       >>> t3 = Time (0, 0, 0)
       >>> print (t3, t3.seconds)
       00:00:00 0
       >>> t4 = Time (23, 59, 59)
       >>> print (t4, t4.seconds)
       23:59:59 86399

       >>> Time (0, 0, 0, 0).as_degrees
       0.0
       >>> Time (1, 0, 0, 0).as_degrees
       15.0
       >>> Time (12, 0, 0, 0).as_degrees
       180.0
       >>> Time (23, 59, 0, 0).as_degrees
       359.75

       >>> Time.from_string ("12:00")
       Time (12, 0, 0, 0)
       >>> Time.from_string ("12:01")
       Time (12, 1, 0, 0)
       >>> Time.from_string ("12:01:02")
       Time (12, 1, 2, 0)
       >>> Time.from_string ("12:01:03.12678")
       Time (12, 1, 3, 12678)
    """

    _Type            = datetime.time
    _default_format  = "%T"
    _kind            = "time"
    _init_arg_names  = ("hour", "minute", "second", "microsecond")
    _timetuple_slice = lambda s, tt : tt [3:6] + (0, )
    _xtra_arg_names  = ("tzinfo", )

    hour             = property (TFL.Getter._body.hour)
    minute           = property (TFL.Getter._body.minute)
    second           = property (TFL.Getter._body.second)
    microsecond      = property (TFL.Getter._body.microsecond)
    tzinfo           = property (TFL.Getter._body.tzinfo)

    pattern          = Regexp \
        ( r" (?P<hour>\d{1,2})"
          r"(: (?P<minute>\d{1,2})"
            r"(: (?P<second>\d{1,2})"
              r"(. (?P<microsecond>\d+))?"
            r")?"
          r")?"
          r"(?: \s"
            r"(?P<tzinfo> [-+]\d{4,4})"
          r")?"
        , re.VERBOSE
        )

    from _CAL.Delta import Time_Delta as Delta

    @Once_Property
    def as_degrees (self) :
        """Returns `self` converted to an angle in degress."""
        return (self.hour + self.minute / 60. + self.second / 3600.) * 15
    # end def as_degrees

    def as_delta (self) :
        return self.Delta \
            ( hours = self.hour, minutes = self.minute, seconds = self.second
            , microseconds = self.microsecond
            )
    # end def as_delta

    @classmethod
    def from_decimal_hours (cls, h) :
        m = (h - int (h)) * 60
        s = (m - int (m)) * 60
        u = (s - int (s)) * 1000000
        return (cls (int (h), int (m), int (s), int (u + 0.5)))
    # end def from_decimal_hours

    @classmethod
    def from_degrees (cls, degrees) :
        """Returns `degrees` converted to time instance.

           >>> Time.from_degrees (0)
           Time (0, 0, 0, 0)
           >>> Time.from_degrees (360)
           Time (0, 0, 0, 0)
           >>> Time.from_degrees (180)
           Time (12, 0, 0, 0)
           >>> Time.from_degrees (90)
           Time (6, 0, 0, 0)
           >>> Time.from_degrees (135)
           Time (9, 0, 0, 0)
        """
        return cls.from_decimal_hours ((degrees % 360.0) / 15.0)
    # end def from_degrees

    @classmethod
    def from_string (cls, s) :
        if cls.pattern.match (s) :
            kw = cls._from_string_match_kw (s, cls.pattern.last_match)
            return cls (** kw)
        raise ValueError (s)
    # end def from_string

    @Once_Property
    def hh_mm (self) :
        """Return tuple of (hour, minute) with `minute` rounded."""
        hh = self.hour
        mm = self.minute + (self.second + 30) // 60
        if mm >= 60 :
            mm -= 60
            hh += 1
            if hh == 24 :
                hh = 0
        return (hh, mm)
    # end def hh_mm

    @Once_Property
    def seconds (self) :
        """Seconds since midnight."""
        result = self.hour * 3600 + self.minute * 60 + self.second
        if self.microsecond :
            result += (self.microsecond / 1000000.)
        return result
    # end def seconds

    @classmethod
    def _from_string_match_kw (cls, s, match) :
        assert match
        kw = {}
        for k, v in pyk.iteritems (match.groupdict ()) :
            if v :
                if k == "tzinfo" :
                    from dateutil.tz import tzoffset
                    v = tzoffset \
                        (None, (int (v [:-2]) * 60 + int (v [-2:])) * 60)
                else :
                    v = int (v)
                kw [k] = v
        return kw
    # end def _from_string_match_kw

    def __add__ (self, rhs) :
        result = self.as_delta () + self._delta (rhs)
        return self.__class__ \
            (result.h, result.m, result.s, result.microseconds)
    # end def __add__

    def __sub__ (self, rhs) :
        if isinstance (rhs, Time) :
            return self.as_delta () - rhs.as_delta ()
        else :
            result = self.as_delta () - self._delta (rhs)
            return self.__class__ \
                (result.h, result.m, result.s, result.microseconds)
    # end def __sub__

# end class Time

if __name__ != "__main__" :
    CAL._Export ("*")
### __END__ CAL.Time
