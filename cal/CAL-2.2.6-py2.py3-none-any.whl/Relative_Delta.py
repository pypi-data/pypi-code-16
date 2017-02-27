# -*- coding: utf-8 -*-
# Copyright (C) 2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package CAL.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    CAL.Relative_Delta
#
# Purpose
#    Wrapper around `dateutil.relativedelta.relativedelta`
#
# Revision Dates
#     2-Feb-2016 (CT) Creation
#    11-Feb-2016 (CT) Derive from `_Delta_Mixin_`, add `delta_pattern`
#    11-Feb-2016 (CT) Add `from_string` and plus/minus operators
#    15-Feb-2016 (CT) Add `as_string`, `__str__`, weekday aliases
#    29-Mar-2016 (CT) Change `delta_pattern` to interpret `m` as `month`
#                     (not `minutes`); allow `min` and `sec` for `minutes` and
#                     `seconds`
#    20-Apr-2016 (CT) Change `month_pattern` to allow digits, too
#    20-Apr-2016 (CT) Use `CAL.Date.month_from_string`, not home-grown code
#    14-May-2016 (CT) Add `_Relative_Delta_Arg_`
#    30-Nov-2016 (CT) Use `.LC` of `G8R`
#     1-Dec-2016 (CT) Use `CAL.G8R.Units...words`, not home-grown definitions
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _CAL                       import CAL
from   _TFL                       import TFL
from   _TFL.pyk                   import pyk

import _CAL.Date_Time
import _CAL.Delta
import _CAL.G8R

from   _TFL.I18N                  import _
from   _TFL.Regexp                import *

import _TFL._Meta.Object
import _TFL._Meta.Once_Property

import datetime
import operator

@pyk.adapt__str__
class Relative_Delta (CAL._Delta_Mixin_) :
    """Relative delta based on `dateutil.relativedelta`

    >>> G8R = CAL.G8R.All.LC
    >>> RD  = Relative_Delta
    >>> d   = datetime.date (2016, 2, 11)
    >>> dt  = datetime.datetime (2016, 2, 11)

    >>> rd0 = RD.from_string ("yearday = 84, FRI (+1)")
    >>> print (rd0)
    yearday = 84, FR(+1)
    >>> rd0
    Relative_Delta (weekday = FR(+1), yearday = 84)

    >>> dt, dt + rd0
    (datetime.datetime(2016, 2, 11, 0, 0), Date_Time (2016, 3, 25, 0, 0, 0, 0))

    >>> rd1 = RD.from_string ("RD.MO(-2)")
    >>> print (rd1)
    MO(-2)
    >>> rd1
    Relative_Delta (weekday = MO(-2))

    >>> d + rd1
    Date (2016, 2, 1)

    >>> dt + rd1
    Date_Time (2016, 2, 1, 0, 0, 0, 0)

    >>> (dt - rd1)
    Date_Time (2016, 2, 1, 0, 0, 0, 0)

    >>> rd2 = RD.from_string ("2 years 3 months")
    >>> print (rd2)
    +2 years, +3 months
    >>> rd2
    Relative_Delta (months = 3, years = 2)
    >>> rd2._body
    relativedelta(years=+2, months=+3)

    >>> (dt + rd2)
    Date_Time (2018, 5, 11, 0, 0, 0, 0)

    >>> (dt - rd2)
    Date_Time (2013, 11, 11, 0, 0, 0, 0)

    >>> rd3 = RD.from_string ("10:42:23 +2 years")
    >>> print (rd3)
    hour = 10, minute = 42, second = 23, +2 years
    >>> rd3
    Relative_Delta (hour = 10, minute = 42, second = 23, years = 2)

    >>> (dt + rd3)
    Date_Time (2018, 2, 11, 10, 42, 23, 0)

    >>> rd4 = RD.from_string ("year = 2019, hour=23, +1 month")
    >>> print (rd4)
    year = 2019, hour = 23, +1 month
    >>> rd4
    Relative_Delta (hour = 23, months = 1, year = 2019)
    >>> (dt, dt + rd4)
    (datetime.datetime(2016, 2, 11, 0, 0), Date_Time (2019, 3, 11, 23, 0, 0, 0))

    >>> rd3 + rd4
    Relative_Delta (hour = 23, minute = 42, months = 1, second = 23, year = 2019, years = 2)

    >>> rd3 + rd4._body
    Relative_Delta (hour = 23, minute = 42, months = 1, second = 23, year = 2019, years = 2)

    >>> rd3 - rd4
    Relative_Delta (hour = 10, minute = 42, months = -1, second = 23, year = 2019, years = 2)

    >>> rd3 - rd4._body
    Relative_Delta (hour = 10, minute = 42, months = -1, second = 23, year = 2019, years = 2)

    >>> rd4 + rd3
    Relative_Delta (hour = 10, minute = 42, months = 1, second = 23, year = 2019, years = 2)

    >>> rd4 - rd3
    Relative_Delta (hour = 23, minute = 42, months = 1, second = 23, year = 2019, years = -2)

    >>> rd5 = RD.from_string ("month = april, +1 year")
    >>> print (rd5)
    month = 4, +1 year
    >>> rd5
    Relative_Delta (month = 4, years = 1)

    >>> with TFL.I18N.test_language ("de") :
    ...     rd = RD.from_string ("Jahrtag = 84, Freitag (+1)")
    ...     print (rd)
    ...     rd
    ...     rd = RD.from_string ("Jahr = 2019, Stunde=23, +1 Monat")
    ...     print (rd)
    ...     rd
    ...     rd = RD.from_string ("monat = Oktober, +1 Monat -1 Tag")
    ...     print (rd)
    ...     rd
    ...     rd = RD.from_string ("monat = mai")
    ...     print (rd)
    ...     rd
    ...     print (rd0, "-->", G8R.localized (rd0.as_string))
    ...     print (rd1, "-->", G8R.localized (rd1.as_string))
    ...     print (rd2, "-->", G8R.localized (rd2.as_string))
    ...     print (rd3, "-->", G8R.localized (rd3.as_string))
    ...     print (rd4, "-->", G8R.localized (rd4.as_string))
    yearday = 84, FR(+1)
    Relative_Delta (weekday = FR(+1), yearday = 84)
    year = 2019, hour = 23, +1 month
    Relative_Delta (hour = 23, months = 1, year = 2019)
    month = 10, +1 month, -1 days
    Relative_Delta (days = -1, month = 10, months = 1)
    month = 5
    Relative_Delta (month = 5)
    yearday = 84, FR(+1) --> jahrtag = 84, fr(+1)
    MO(-2) --> mo(-2)
    +2 years, +3 months --> +2 jahre, +3 monate
    hour = 10, minute = 42, second = 23, +2 years --> stunde = 10, minute = 42, sekunde = 23, +2 jahre
    year = 2019, hour = 23, +1 month --> jahr = 2019, stunde = 23, +1 monat

    """

    _CIOP    = TFL.Meta.Class_and_Instance_Once_Property
    MO = MON = MONDAY    = _CIOP (lambda soc : soc.RD.MO)
    TU = TUE = TUESDAY   = _CIOP (lambda soc : soc.RD.TU)
    WE = WED = WEDNESDAY = _CIOP (lambda soc : soc.RD.WE)
    TH = THU = THURSDAY  = _CIOP (lambda soc : soc.RD.TH)
    FR = FRI = FRIDAY    = _CIOP (lambda soc : soc.RD.FR)
    SA = SAT = SATURDAY  = _CIOP (lambda soc : soc.RD.SA)
    SU = SUN = SUNDAY    = _CIOP (lambda soc : soc.RD.SU)

    absolute_units = CAL.G8R.Units_Abs.words + CAL.G8R.Units_YD.words

    absolute_pattern = Regexp \
        ( r",?\s*"
          r"(?P<unit> "
        +  "|".join (sorted (absolute_units, key = lambda u : (- len (u), u)))
        + r")"
          r"\s*=\s* "
          r"(?P<value> \d+)"
        , flags = re.VERBOSE | re.IGNORECASE
        )

    delta_pattern    = Regexp \
        ( r",?\s*"
          r"(?:(?P<years> [-+]? \d+) (?: \. (?P<subyears> \d+) )?\s* y(?:ears?)?)?"
          r",?\s*"
          r"(?:(?P<months>[-+]? \d+) \s* m(?:onths?)? )?"
          r",?\s*"
          r"(?:(?P<weeks> [-+]? \d+) \s* w(?:eeks?)?  )?"
          r",?\s*"
          r"(?:(?P<days>  [-+]? \d+) \s* d(?:ays?)?   )?"
          r"(?:(?P<hours>   [-+]?\d+) (?: \. (?P<subhours> \d+) )?\s* h(?:ours?)?)?"
          r",?\s*"
          r"(?:(?P<minutes> [-+]?\d+) (?: \. (?P<subminutes> \d+) )?\s* min(?:utes?)?)?"
          r",?\s*"
          r"(?:(?P<seconds> [-+]?\d+) (?: \. (?P<subseconds> \d+) )?\s* s(?:ec(?:onds?)?)?)?"
          r"$"
        , flags = re.VERBOSE | re.IGNORECASE
        )

    delta_units = CAL.G8R.Units_Delta.words

    month_pattern = Regexp \
        ( r",?\s*"
          r"(?P<unit> month)"
          r"\s*=\s* "
          r"(?P<value> (?: [a-z]+|[0-9]{1,2}))"
        , flags = re.VERBOSE | re.IGNORECASE
        )

    units = absolute_units + delta_units + (_ ("weekday"), )

    weekday_pattern = Regexp \
        ( r",?\s*"
        + r"\b"
        +   r"(?P<wkd> "
        +    "|".join (CAL.G8R.Week_Days.LC.words)
        +   r")"
        + r"\b\s*"
        + r"(?: \( (?P<n> [-+]?\d+) \))?"
        , flags = re.VERBOSE | re.IGNORECASE
        )

    def __init__ (self, _body = None, ** kw) :
        if _body is not None :
            if not isinstance (_body, self.RD.relativedelta) :
                raise TypeError \
                    ("Expected relativedelta instance, got %r" % _body)
            self.__dict__ ["_body"] = _body
            if not kw :
                kw = self._kw_from_relativedelta (_body)
        self._kw = kw
    # end def __init__

    @classmethod
    def from_string (cls, s) :
        orig_s = s
        kw     = {}
        ### Absolute date value (year + month + day)
        dp     = CAL.Date.date_pattern
        match  = dp.match (s)
        if match :
            kw.update (CAL.Date._from_string_match_kw (s, match))
            s  = s [match.end () :].lstrip ().lstrip ("T")
        ### Absolute time value (hour + minute, optionally seconds)
        tp     = CAL.Date_Time.time_pattern
        match  = tp.match (s)
        if match :
            kw.update (CAL.Time._from_string_match_kw (s, match))
            s  = s [match.end () :]
        ### Absolute units (any of `absolute_units`)
        s      = CAL.G8R.Units.LC (s)
        spans  = []
        for match in cls.absolute_pattern.search_iter (s) :
            kw [match.group ("unit")] = int (match.group ("value"))
            spans.append (match.span ())
        match = cls.month_pattern.search (s)
        if match :
            kw ["month"] = CAL.Date.month_from_string (match.group ("value"))
            spans.append (match.span ())
        ### Weekday instance
        s      = CAL.G8R.Week_Days.LC (s)
        match  = cls.weekday_pattern.search (s)
        if match :
            wkd = getattr (cls, match.group ("wkd").upper ())
            n   = match.group ("n")
            if n :
                wkd = wkd (int (n))
            kw ["weekday"] = wkd
            spans.append (match.span ())
        for h, t in sorted (spans, key = lambda s : -s[1]) :
            s  = s [:h] + s [t:]
        s      = s.strip (",").strip ()
        ### Delta units
        match  = cls.delta_pattern.match (s)
        if match :
            kw.update (cls._from_string_match_kw (s, match))
        ### Create new Relative_Delta instance
        if kw :
            return cls (** kw)
        else :
            raise ValueError (orig_s)
    # end def from_string

    @classmethod
    def new_dtw (cls, body) :
        if body.__class__ in CAL._DTW_._Type_Table :
            return CAL._DTW_.new_dtw (body)
        else :
            kw  = cls._kw_from_relativedelta (body)
            return cls (body)
    # end def new_dtw

    @classmethod
    def _from_string_match_kw (cls, s, match) :
        mdct = match.groupdict ()
        result = cls.__c_super._from_string_match_kw (s, mdct)
        if "milliseconds" in result :
            ### `relativedelta` supports `microseconds` but not `milliseconds`
            result ["microseconds"] += (result.pop ("milliseconds") * 1000)
        return result
    # end def _from_string_match_kw

    @classmethod
    def _kw_from_relativedelta (cls, rd) :
        result = {}
        for k in cls.units :
            v = getattr (rd, k, None)
            if v :
                result [k] = v
        return result
    # end def _kw_from_relativedelta

    @TFL.Meta.Once_Property
    def as_string (self) :
        parts = []
        kw    = self._kw
        for u in self.absolute_units :
            v = kw.get (u)
            if v :
                parts.append ("%s = %s" % (u, v))
        wkd = kw.get ("weekday")
        if wkd is not None :
            parts.append ("%s" % (wkd, ))
        for u in self.delta_units :
            v = kw.get (u)
            if v :
                parts.append ("%+d %s" % (v, u[:-1] if v == 1 else u))
        return ", ".join (parts)
    # end def as_string

    @TFL.Meta.Class_and_Instance_Once_Property
    def RD (soc) :
        from dateutil import relativedelta
        return relativedelta
    # end def RD

    @TFL.Meta.Once_Property
    def _body (self) :
        return self.RD.relativedelta (** self._kw)
    # end def _body

    def dt_op (self, dot, op) :
        if isinstance (dot, CAL._DTW_) :
            result = op (dot._body, self._body)
            return dot.new_dtw (result)
        else :
            body   = dot._body if isinstance (dot, Relative_Delta) else dot
            result = op (self._body, body)
            result = self.new_dtw (result)
            return result
    # end def dt_op

    def __add__ (self, rhs) :
        return self.dt_op (rhs, operator.add)
    __radd__ = __add__ # end def __add__

    def __neg__ (self) :
        return self.__class__ (- self._body)
    # end def __neg__

    def __repr__ (self) :
        args = ", ".join \
            ("%s = %r" % (k, v) for k, v in sorted (pyk.iteritems (self._kw)))
        return pyk.reprify ("%s (%s)" % (self.__class__.__name__, args))
    # end def __repr__

    def __rsub__ (self, rhs) :
        if isinstance (rhs, CAL._DTW_) :
            return self.dt_op (rhs, operator.sub)
        elif isinstance (rhs, (datetime.date, datetime.datetime)) :
            return self.new_dtw (rhs - self._body)
        else :
            return self.dt_op (-rhs, operator.add)
    # end def __rsub__

    def __str__ (self) :
        return self.as_string
    # end def __str__

    def __sub__ (self, rhs) :
        return self.dt_op (rhs, operator.sub)
    # end def __sub__

# end class Relative_Delta

class _Relative_Delta_Arg_ (TFL.CAO.Str) :
    """Argument or option with a (calendary) relative-delta value"""

    _real_name = "Relative_Delta"

    def cook (self, value, cao = None) :
        return Relative_Delta.from_string (value)
    # end def cook

# end class _Delta_Arg_

if __name__ != "__main__" :
    CAL._Export ("*")
### __END__ CAL.Relative_Delta
