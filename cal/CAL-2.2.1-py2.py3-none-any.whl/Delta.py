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
#    CAL.Delta
#
# Purpose
#    Wrapper around `datetime.timedelta`
#
# Revision Dates
#    14-Oct-2004 (CT) Creation (`Delta` just an alias for `datetime.timedelta`)
#    17-Oct-2004 (CT) `Time_Delta`, `Date_Delta`, and `Date_Time_Delta`
#                     implemented
#    17-Oct-2004 (CT) `Month_Delta` added
#    17-Oct-2004 (CT) `Month_Delta` renamed to `MY_Delta` and `years` added
#    17-Oct-2004 (CT) Getters of `Time_Delta` renamed to `h`, `m`, and `s` to
#                     allow `seconds` to return `_body.seconds` unchanged
#    19-Oct-2004 (CT) s/MY_Delta/Month_Delta/
#    23-Oct-2004 (CT) `__neg__` added
#    25-Oct-2004 (CT) `__abs__` added
#    26-Oct-2004 (CT) `__abs__` changed to return `self` for positive values
#    12-Dec-2004 (CT) `_init_arg_map` added
#     7-Nov-2007 (CT) Use `Getter` instead of `lambda`
#     1-Jan-2008 (CT) `Time_Delta.hh_mm` added
#     3-May-2011 (CT) `from_string` added
#     3-May-2011 (CT) CAO argument/option types added for `Date_Delta`,
#                     `Date_Time_Delta`, and `Time_Delta`
#    15-Apr-2012 (CT) Fix `_from_string_match_kw` (use `+=` instead of `=` in
#                     `else` of `k.startswith ("sub")`)
#    28-Feb-2014 (CT) Use future `print_function`
#    28-Feb-2014 (CT) Add support for negative values to `from_string`
#    28-Feb-2014 (CT) Add `from_string`, `week`, `days` to `Month_Delta`
#     4-Mar-2014 (CT) Make `str (Month_Delta)` unique and sortable
#     4-Mar-2014 (CT) Fix `Month_Delta.dt_op` to support subtraction
#     4-Mar-2014 (CT) Change `_DT_Delta_.dt_op` to support `datetime` instances
#     4-Mar-2014 (CT) Change `Month_Delta.__add__` and `.__sub__` to support
#                     `datetime` instances; add `__radd__`, `__rsub__`
#     7-Mar-2014 (CT) Change `Month_Delta` operators to include `days`
#    17-Jun-2014 (RS) Fix parsing of `Date_Time_Delta` (didn't roundtrip)
#                     semantic change: single number, e.g., `2` is now invalid
#    11-Feb-2016 (CT) Use `CAL.G8R.Units` to allow localized delta units
#    11-Feb-2016 (CT) Factor `_Delta_Mixin_`
#    19-Apr-2016 (CT) Add `Month_Delta.__mul__`
#    26-Jun-2016 (CT) Add `Time_Delta.__float__`
#    ««revision-date»»···
#--

from   __future__                 import print_function

from   _CAL                       import CAL
from   _TFL                       import TFL

import _CAL._DTW_
import _CAL.G8R

import _TFL.Accessor
import _TFL.CAO
import _TFL.defaultdict
import _TFL.Math_Func

from   _TFL._Meta.Once_Property   import Once_Property
from   _TFL.Regexp                import *
from   _TFL.pyk                   import pyk
from   _TFL._Meta.totally_ordered import totally_ordered

import datetime
import operator

class _Delta_Mixin_ (TFL.Meta.Object) :
    """Mixin for delta classes"""

    @classmethod
    def from_string (cls, s) :
        match = cls.delta_pattern.match (CAL.G8R.Units.LC (s))
        if match :
            return cls (** cls._from_string_match_kw (s, match))
        else :
            raise ValueError (s)
    # end def from_string

    @classmethod
    def _from_string_match_kw (cls, s, match) :
        assert match
        kw   = TFL.defaultdict (int)
        mdct = match if isinstance (match, dict) \
            else match.groupdict ()
        for k, v in pyk.iteritems (mdct) :
            if v :
                if k.startswith ("sub") :
                    n    = k [3:]
                    neg  = "-" in match.group (n)
                    f    = float ("%s0.%s" % (("-" if neg else ""), v))
                    if n == "days" :
                        h, m   = divmod (f * 24 * 60, 60)
                        m, s   = divmod (m * 60,      60)
                        kw ["hours"]        += int (h)
                        kw ["minutes"]      += int (m)
                        kw ["seconds"]      += int (s)
                    elif n == "hours" :
                        m, s   = divmod (int (f * 3600), 60)
                        kw ["minutes"]      += int (m)
                        kw ["seconds"]      += int (s)
                    elif n == "minutes" :
                        s, us  = divmod (int (f * 60 * 1e6), 1e6)
                        kw ["seconds"]      += int (s)
                        kw ["microseconds"] += int (us)
                    elif n == "seconds" :
                        ms, us = divmod (int (f * 1e6), 1000)
                        kw ["milliseconds"] += int (ms)
                        kw ["microseconds"] += int (us)
                    elif n == "weeks" :
                        d, h   = divmod (f * 7 * 24,  24)
                        h, m   = divmod (h * 60,      60)
                        m, s   = divmod (m * 60,      60)
                        kw ["days"]         += int (d)
                        kw ["hours"]        += int (h)
                        kw ["minutes"]      += int (m)
                        kw ["seconds"]      += int (s)
                    elif n == "years" :
                        m = f * 12
                        d = abs (m - round (m))
                        if d > 0.05 :
                            raise ValueError \
                                ( "Fractional months are not allowed for "
                                  "%s: %s --> delta %s"
                                % (cls.__name__, s, d)
                                )
                        kw ["months"]       += int (round (m))
                else :
                    kw [k] += int (v)
        return kw
    # end def _from_string_match_kw

# end class _Delta_Mixin_

class _Delta_ (_Delta_Mixin_, CAL._DTW_) :
    """Root class for delta classes"""

    def __radd__ (self, rhs) :
        return self + rhs
    # end def __radd__

    def __rsub__ (self, rhs) :
        return self - rhs
    # end def __rsub__

# end class _Delta_

class _DT_Delta_ (_Delta_) :
    """Root class for datetime.timedelta wrapping classes"""

    _Type            = datetime.timedelta
    _kind            = "delta"
    _timetuple_slice = lambda s, tt : (0, ) * len (s._init_arg_names)

    Zero             = datetime.timedelta (0)

    def delta_op (self, rhs, op) :
        """Return result of `op` applied to `self` and delta `rhs`"""
        result = op (self._body, rhs._body)
        return self.__class__ (** {self._kind : result})
    # end def delta_op

    def dt_op (self, dot, op) :
        """Return result of `op` applied to date/time value `dot` and delta
           `self`
        """
        if isinstance (dot, CAL._DTW_) :
            result = op (dot._body, self._body)
            return dot.__class__ (** {dot._kind : result})
        else :
            ### assume it is an of a `datetime` class
            return op (dot, self._body)
    # end def dt_op

    def __abs__ (self) :
        if self._body < self.Zero :
            return self.__class__ (** {self._kind : abs (self._body)})
        return self
    # end def __abs__

    def __add__ (self, rhs) :
        if isinstance (rhs, _Delta_) :
            op = self.delta_op
        else :
            op = self.dt_op
        return op (rhs, operator.add)
    # end def __add__

    def __floordiv__ (self, rhs) :
        result = self._body / rhs
        return self.__class__ (** {self._kind : result})
    # end def __floordiv__

    def __mul__ (self, rhs) :
        result = self._body * rhs
        return self.__class__ (** {self._kind : result})
    # end def __mul__

    def __neg__ (self) :
        return self.__class__ (** {self._kind : - self._body})
    # end def __neg__

    def __sub__ (self, rhs) :
        if isinstance (rhs, _Delta_) :
            op = self.delta_op
        else :
            op = self.dt_op
        return op (rhs, operator.sub)
    # end def __sub__

# end class _DT_Delta_

class Time_Delta (_DT_Delta_) :
    """Model a time delta

    >>> t = Time_Delta (3)
    >>> print (t)
    3:00:00
    >>> t.h, t.m, t.s, t.seconds
    (3, 0, 0, 10800)
    >>> abs (t) is t
    True
    >>> abs (t) == t
    True
    >>> t = Time_Delta (-3)
    >>> abs (t) is t
    False
    >>> abs (t) == - t
    True
    >>> hms = Time_Delta (2, 15, 42)
    >>> print (hms)
    2:15:42
    >>> hms.h, hms.m, hms.s, hms.seconds
    (2, 15, 42, 8142)
    >>> md = Time_Delta (minutes = 42)
    >>> print (md)
    0:42:00

    >>> Time_Delta.from_string("7")
    Time_Delta (7, 0, 0, 0, 0)
    >>> Time_Delta.from_string("7:42")
    Time_Delta (7, 42, 0, 0, 0)
    >>> Time_Delta.from_string("7:42:37")
    Time_Delta (7, 42, 37, 0, 0)
    >>> Time_Delta.from_string("7:42:37.25")
    Time_Delta (7, 42, 37, 250, 0)
    >>> Time_Delta.from_string("7:42:37.00025")
    Time_Delta (7, 42, 37, 0, 250)
    >>> Time_Delta.from_string ("1.5h10.25m7.125s")
    Time_Delta (1, 40, 22, 125, 0)
    >>> Time_Delta.from_string ("1.5 hours 10.25 minutes 7.125 seconds")
    Time_Delta (1, 40, 22, 125, 0)

    >>> Time_Delta.from_string ("1.5 Stunden 10.25 Minuten 7.125 sekunden")
    Traceback (most recent call last):
      ...
    ValueError: 1.5 Stunden 10.25 Minuten 7.125 sekunden

    >>> with TFL.I18N.test_language ("de") :
    ...     Time_Delta.from_string ("1.5 Stunden 10.25 Minuten 7.125 sekunden")
    Time_Delta (1, 40, 22, 125, 0)

    """

    seconds          = property (TFL.Getter._body.seconds)
    microseconds     = property (TFL.Getter._body.microseconds)
    h                = property (lambda s : (s.seconds // 3600))
    m                = property (lambda s : (s.seconds  % 3600) // 60)
    s                = property (lambda s : (s.seconds  %   60))

    _init_arg_names  = \
        ("hours", "minutes", "seconds", "milliseconds", "microseconds")
    _init_arg_map    = dict \
        ( hours      = "h"
        , minutes    = "m"
        , seconds    = "s"
        )
    _kind            = "time_delta"

    delta_pattern    = Multi_Regexp \
        ( r"^"
          r"(?P<hours> \d{1,2})"
          r"(?:"
            r": (?P<minutes> \d{1,2})"
            r"(?:"
              r": (?P<seconds> \d{1,2}) (?: \. (?P<subseconds> \d+) )?"
            r")?"
          r")?"
          r"$"
        , r"^"
          r"(?:(?P<hours>   [-+]?\d+) (?: \. (?P<subhours> \d+) )?\s* h(?:ours?)?)?"
          r",?\s*"
          r"(?:(?P<minutes> [-+]?\d+) (?: \. (?P<subminutes> \d+) )?\s* m(?:inutes?)?)?"
          r",?\s*"
          r"(?:(?P<seconds> [-+]?\d+) (?: \. (?P<subseconds> \d+) )?\s* s(?:econds?)?)?"
          r"$"
        , flags = re.VERBOSE | re.IGNORECASE
        )

    def delta_op (self, rhs, op) :
        result = self.__super.delta_op (rhs, op)
        if result._body.days :
            raise OverflowError (result)
        return result
    # end def delta_op

    @Once_Property
    def hh_mm (self) :
        """Return tuple of (hour, minute) with `minute` rounded."""
        hh = self.h
        mm = self.m + (self.s + 30) // 60
        if mm >= 60 :
            mm -= 60
            hh += 1
        return (hh, mm)
    # end def hh_mm

    def __float__ (self) :
        return self.seconds + self.microseconds / 1e6
    # end def __float__

# end class Time_Delta

class Date_Delta (_DT_Delta_) :
    """Model a date delta

    >>> d = Date_Delta (42)
    >>> print (d)
    42 days, 0:00:00
    >>> d.days, d.weeks
    (42, 6)
    >>> d2 = Date_Delta (5)
    >>> x = d - d2
    >>> print (x)
    37 days, 0:00:00
    >>> x.__class__
    <class 'Delta.Date_Delta'>
    >>> t = Time_Delta (3)
    >>> s = d + t
    >>> print (s)
    42 days, 3:00:00
    >>> print (s.__class__)
    <class 'Delta.Date_Time_Delta'>
    >>> s.days, s.h, s.m, s.s
    (42, 3, 0, 0)
    >>> d3 = Date_Delta (weeks = 2, days = 5)
    >>> print (d3)
    19 days, 0:00:00
    >>> print (d3.days, d3.weeks)
    19 2
    >>> Date_Delta.from_string ("2.5 weeks")
    Date_Delta (3, 2)
    >>> Date_Delta.from_string ("-2.5 weeks")
    Date_Delta (-4, -2)
    >>> print (Date_Delta.from_string ("-2.5 weeks"))
    -18 days, 0:00:00

    >>> print (Date_Delta.from_string ("2 weeks -3 days"))
    11 days, 0:00:00
    >>> print (Date_Delta.from_string ("-2 weeks -3 days"))
    -17 days, 0:00:00
    >>> print (Date_Delta.from_string ("-2 weeks +3 days"))
    -11 days, 0:00:00

    >>> print (Date_Delta.from_string ("42 days") + datetime.date (2014,  3,  4))
    2014-04-15
    >>> print (Date_Delta.from_string ("-28 days") + datetime.date (2014,  3,  4))
    2014-02-04

    >>> print (datetime.date (2014,  3,  4) + Date_Delta.from_string ("42 days"))
    2014-04-15
    >>> print (datetime.date (2014,  3,  4) + Date_Delta.from_string ("-28 days"))
    2014-02-04

    >>> with TFL.I18N.test_language ("de") :
    ...     print (Date_Delta.from_string ("2 Wochen -3 Tage"))
    ...     print (Date_Delta.from_string ("-2 Wochen -3 Tage"))
    11 days, 0:00:00
    -17 days, 0:00:00

    """

    days             = property (TFL.Getter._body.days)
    weeks            = property (lambda s : s._body.days // 7)

    _init_arg_names  = ("days", "weeks")
    _kind            = "date_delta"

    delta_pattern    = Multi_Regexp \
        ( r"^"
          r"(?P<days> [-+]? \d+) (?: \. (?P<subdays>  \d+) )?"
          r"$"
        , r"^"
          r"(?:(?P<weeks> [-+]? \d+) (?: \. (?P<subweeks> \d+) )?\s* w(?:eeks?)?)?"
          r",?\s*"
          r"(?:(?P<days>  [-+]? \d+) (?: \. (?P<subdays>  \d+) )?\s* d(?:ays?)?)?"
          r"$"
        , flags = re.VERBOSE | re.IGNORECASE
        )

    def delta_op (self, rhs, op) :
        return self._date_time_delta_maybe (self.__super.delta_op (rhs, op))
    # end def delta_op

    def _date_time_delta_maybe (self, result) :
        if result._body.seconds or result._body.microseconds :
            result = Date_Time_Delta \
                (** {Date_Time_Delta._kind : result._body})
        return result
    # end def _date_time_delta_maybe

# end class Date_Delta

class Date_Time_Delta (Date_Delta, Time_Delta) :
    """Model a date_time delta

    >>> d = Date_Time_Delta (5, 8, 3, 33)
    >>> print (d)
    5 days, 8:03:33
    >>> d.days, d.h, d.m, d.s
    (5, 8, 3, 33)
    >>> d2 = Date_Time_Delta (days = 2, hours = 12)
    >>> print (d2)
    2 days, 12:00:00
    >>> print (d2.days, d2.seconds)
    2 43200
    >>> print (d2.weeks)
    0

    >>> Date_Time_Delta.from_string ("2")
    Traceback (most recent call last):
        ...
    ValueError: 2

    >>> Date_Time_Delta.from_string ("2.5 weeks")
    Date_Time_Delta (3, 12, 0, 0, 0, 0, 2)
    >>> print (Date_Time_Delta.from_string ("2.5 weeks"))
    17 days, 12:00:00
    >>> print (Date_Time_Delta.from_string ("2.5 d"))
    2 days, 12:00:00
    >>> print (Date_Time_Delta.from_string ("2.5 d 15.25m"))
    2 days, 12:15:15
    >>> print (Date_Time_Delta.from_string ("2.5 d -5h -15.25m"))
    2 days, 6:44:45
    >>> print (Date_Time_Delta.from_string ("2.5 d -5h 15.25m"))
    2 days, 7:15:15
    >>> print (Date_Time_Delta.from_string ("2.5 d 5h -15.25m"))
    2 days, 16:44:45
    >>> print (Date_Time_Delta.from_string ("2 days16:4:45"))
    2 days, 16:04:45
    >>> print (Date_Time_Delta.from_string ("2 days, 16:44:45"))
    2 days, 16:44:45
    >>> print (Date_Time_Delta.from_string ("2w2 days 16:44:45"))
    16 days, 16:44:45
    >>> print (Date_Time_Delta.from_string ("1w 2d 16:44:45"))
    9 days, 16:44:45
    >>> print (Date_Time_Delta.from_string ("2d 16:44:45"))
    2 days, 16:44:45
    >>> print (Date_Time_Delta.from_string ("2w 16:44:45"))
    14 days, 16:44:45
    >>> print (Date_Time_Delta.from_string ("16:44:45"))
    16:44:45
    >>> print (Date_Time_Delta.from_string ("2w"))
    14 days, 0:00:00
    >>> print (Date_Time_Delta.from_string ("2d"))
    2 days, 0:00:00
    >>> print (Date_Time_Delta.from_string ("2,"))
    2 days, 0:00:00
    >>> print (Date_Time_Delta.from_string ("2:0"))
    2:00:00
    >>> print (Date_Time_Delta.from_string ("2d2:0"))
    2 days, 2:00:00

    >>> with TFL.I18N.test_language ("de") :
    ...     print (Date_Time_Delta.from_string ("2wochen 2 Tage 16:44:45"))
    ...     print (Date_Time_Delta.from_string ("2wochen 2 Tage 16 Stunden 44 minuten 45 sekunden"))
    16 days, 16:44:45
    16 days, 16:44:45

    """

    _init_arg_names = ("days", ) + Time_Delta._init_arg_names + ("weeks", )
    _kind           = "date_time_delta"

    delta_op        = _DT_Delta_.delta_op

    delta_pattern    = Multi_Regexp \
        ( r"^"
          r"(?: (?P<weeks> \d+) \s* w(?:eeks?,?)?\s*)?"
          r"(?: (?P<days>  \d+) (?: , \s*  | \s* d(?:ays?,?)?\s*))?"
          r"(?:"
            r"(?P<hours> \d{1,2})"
            r"(?:"
              r": (?P<minutes> \d{1,2})"
              r"(?:"
                r": (?P<seconds> \d{1,2}) (?: \. (?P<subseconds> \d+) )?"
              r")?"
            r")"
          r")?"
          r"$"
        , r"^"
          r"(?:(?P<weeks>   [-+]?\d+) (?:\.(?P<subweeks>   \d+) )?\s* w(?:eeks?)?)?"
          r",?\s*"
          r"(?:(?P<days>    [-+]?\d+) (?:\.(?P<subdays>    \d+) )?\s* d(?:ays?)?)?"
          r",?\s*"
          r"(?:(?P<hours>   [-+]?\d+) (?:\.(?P<subhours>   \d+) )?\s* h(?:ours?)?)?"
          r",?\s*"
          r"(?:(?P<minutes> [-+]?\d+) (?:\.(?P<subminutes> \d+) )?\s* m(?:inutes?)?)?"
          r",?\s*"
          r"(?:(?P<seconds> [-+]?\d+) (?:\.(?P<subseconds> \d+) )?\s* s(?:econds?)?)?"
          r"$"
        , flags = re.VERBOSE | re.IGNORECASE
        )


# end class Date_Time_Delta

@totally_ordered
class Month_Delta (_Delta_) :
    """Model month-stepping delta

    >>> print (Month_Delta (1))
    +1 month
    >>> print (Month_Delta (2))
    +2 months
    >>> print (Month_Delta (-3))
    -3 months
    >>> print (Month_Delta (years = 1))
    +12 months
    >>> print (Month_Delta (years = 5))
    +60 months
    >>> print (Month_Delta (3, 1))
    +15 months
    >>> print (Month_Delta (1, 2))
    +25 months
    >>> print (Month_Delta (-1, 2))
    +23 months
    >>> md = Month_Delta (13)
    >>> print (md)
    +13 months
    >>> print (md + 1)
    +14 months
    >>> md = Month_Delta (1)
    >>> abs (md) is md
    True
    >>> print (abs (md))
    +1 month
    >>> md = Month_Delta (-1)
    >>> abs (md) is md
    False
    >>> abs (md) == -md
    True
    >>> print (md, abs (md))
    -1 months +1 month
    >>> print (md * 3, abs (md) * 15)
    -3 months +15 months

    >>> print (Month_Delta.from_string ("1y3m"))
    +15 months
    >>> print (Month_Delta.from_string ("1y3d"))
    +12 months, +3 days
    >>> print (Month_Delta.from_string ("1y3w3d"))
    +12 months, +24 days
    >>> print (Month_Delta.from_string ("-1y3w3d"))
    -12 months, +24 days
    >>> print (Month_Delta.from_string ("-1y3w-3d"))
    -12 months, +18 days

    >>> with TFL.I18N.test_language ("de") :
    ...     print (Month_Delta.from_string ("-1j3w-3t"))
    -12 months, +18 days

    >>> print (Month_Delta.from_string ("+2 years 3 months, 2 weeks -3 days"))
    +27 months, +11 days

    >>> with TFL.I18N.test_language ("de") :
    ...     print (Month_Delta.from_string ("+2 Jahre 3 Monate, 2 Wochen -3 Tage"))
    +27 months, +11 days

    >>> md1 = Month_Delta.from_string ("+2 years 3 months, 2 weeks -3 days")
    >>> md2 = Month_Delta.from_string (str (md1))

    >>> print (md2) ### "+2 years 3 months, 2 weeks -3 days"
    +27 months, +11 days
    >>> md1 == md2
    True
    >>> str (md1) == str (md2)
    True

    >>> print (Month_Delta (days = 42))
    +0 months, +42 days
    >>> print (Month_Delta (1, days = 23))
    +1 month, +23 days
    >>> print (Month_Delta (2, days = 23))
    +2 months, +23 days

    >>> print (Month_Delta (3, days = 42))
    Traceback (most recent call last):
      ...
    ValueError: Can't specify `months` and `days > 28` simultaneously: Month_Delta (months = 3, days = 42) --> +3 months, +42 days

    >>> import datetime
    >>> d = datetime.date (2014,  3,  4)
    >>> print (d, "+ +5", d + Month_Delta (5))
    2014-03-04 + +5 2014-08-04
    >>> print (d, "+ -5", d + Month_Delta (-5))
    2014-03-04 + -5 2013-10-04
    >>> print (d, "+5 +", Month_Delta (5) + d)
    2014-03-04 +5 + 2014-08-04
    >>> print (d, "+5 -", Month_Delta (5) - d)
    2014-03-04 +5 - 2013-10-04
    >>> print (d, "- -5", d - Month_Delta(-5))
    2014-03-04 - -5 2014-08-04
    >>> print (d, "- +5", d - Month_Delta(5))
    2014-03-04 - +5 2013-10-04

    >>> md1 = Month_Delta (days = 90)
    >>> md2 = Month_Delta (weeks = 4)

    >>> md1 == md2
    False
    >>> md1 != md2
    True

    >>> md1 > md2
    True
    >>> md1 < md2
    False

    """

    delta_pattern    = Multi_Regexp \
        ( r"^"
          r"(?P<months> [-+]? \d+)"
          r"$"
        , r"^"
          r"(?:(?P<years> [-+]? \d+) (?: \. (?P<subyears> \d+) )?\s* y(?:ears?)?)?"
          r",?\s*"
          r"(?:(?P<months>[-+]? \d+) \s* m(?:onths?)? )?"
          r",?\s*"
          r"(?:(?P<weeks> [-+]? \d+) \s* w(?:eeks?)?  )?"
          r",?\s*"
          r"(?:(?P<days>  [-+]? \d+) \s* d(?:ays?)?   )?"
          r"$"
        , flags = re.VERBOSE | re.IGNORECASE
        )

    _date_delta      = None
    _init_arg_names  = ("months", "years") + Date_Delta._init_arg_names

    def __init__ (self, months = 0, years = 0, days = 0, weeks = 0) :
        self._setup_init_kw \
            (months = months, years = years, days = days, weeks = weeks)
        self.months = md = months + years * 12
        if days or weeks :
            self._date_delta = dd = Date_Delta (days = days, weeks = weeks)
            if md and dd.days > 28 :
                raise ValueError \
                    ( "Can't specify `months` and `days > 28` simultaneously: "
                      "%r --> %s" % (self, self)
                    )
    # end def __init__

    @property
    def days (self) :
        dd     = self._date_delta
        result = dd.days if dd is not None else 0
        return result
    # end def days

    def dt_op (self, date, op) :
        """Return result of `op` applied to date(_time) value `date` and delta
           `self`
        """
        sign  = TFL.sign (self.months)
        yd, m = 0, op (date.month, self.months)
        if sign :
            if m == 0 :
                yd, m = -1, 12
            elif not (1 <= m <= 12) :
                yd, m = divmod (m, 12)
                yd    = op (0, yd) ### for subtraction, need to change sign
        result = date.replace (month = m, year = op (date.year, yd))
        if self._date_delta :
            result = result + self._date_delta
        return result
    # end def dt_op

    def _setup_init_kw (self, ** kw) :
        self._init_kw = dict ((k, v) for k, v in pyk.iteritems (kw) if v)
    # end def _setup_init_kw

    def __abs__ (self) :
        if self.months < 0 :
            return self.__class__ (abs (self.months), days = abs (self.days))
        return self
    # end def __abs__

    def __add__ (self, rhs) :
        if isinstance (rhs, (datetime.date, datetime.datetime)) :
            return self.dt_op (rhs, operator.add)
        else :
            return self.__class__ (self.months + rhs, days = abs (self.days))
    # end def __add__

    def __eq__ (self, rhs) :
        try :
            rhs = rhs.months, rhs.days
        except AttributeError :
            pass
        return (self.months, self.days) == rhs
    # end def __eq__

    def __hash__ (self) :
        return hash ((self.months, self.days))
    # end def __hash__

    def __lt__ (self, rhs) :
        try :
            return (self.months, self.days) < (rhs.months, rhs.days)
        except AttributeError :
            return False
    # end def __lt__

    def __mul__ (self, rhs) :
        return self.__class__ (self.months * rhs, days = self.days * rhs)
    # end def __mul__

    def __neg__ (self) :
        return self.__class__ (months = - self.months, days = - self.days)
    # end def __neg__

    def __repr__ (self) :
        return "%s (%s)" % \
            ( self.__class__.__name__
            , ", ".join
                ( "%s = %s" %(a, self._init_arg (a))
                for a in self._init_arg_names if a in self._init_kw
                )
            )
    # end def __repr__

    def __str__ (self) :
        result = []
        months = self.months
        days   = self.days
        result.append     ("%+d month%s" % (months, ("", "s") [months != 1]))
        if days :
            result.append ("%+d day%s"   % (days,   ("", "s") [days   != 1]))
        return ", ".join (result)
    # end def __str__

    def __sub__ (self, rhs) :
        if isinstance (rhs, (datetime.date, datetime.datetime)) :
            return self.dt_op (rhs, operator.sub)
        else :
            return self.__class__ (self.months - rhs, days = abs (self.days))
    # end def __sub__

# end class Month_Delta

Delta = Date_Time_Delta

class _Delta_Arg_ (TFL.CAO.Str) :
    """Argument or option with a (calendary) date or time delta value"""

    def cook (self, value, cao = None) :
        return self.D_Type.from_string (value)
    # end def cook

# end class _Delta_Arg_

class _Date_Delta_Arg_ (_Delta_Arg_) :
    """Argument or option with a (calendary) date-delta value"""

    _real_name = "Date_Delta"
    D_Type     = Date_Delta

# end class _Date_Delta_Arg_

class _Date_Time_Delta_Arg_ (_Delta_Arg_) :
    """Argument or option with a (calendary) datetime-delta value"""

    _real_name = "Date_Time_Delta"
    D_Type     = Date_Time_Delta

# end class _Date_Time_Delta_Arg_

class _Time_Delta_Arg_ (_Delta_Arg_) :
    """Argument or option with a (calendary) time-delta value"""

    _real_name = "Time_Delta"
    D_Type     = Time_Delta

# end class _Time_Delta_Arg_

if __name__ != "__main__" :
    CAL._Export ("*", "_Delta_Mixin_", "_Delta_", "Delta")
### __END__ CAL.Delta
