# -*- coding: utf-8 -*-
# Copyright (C) 2016-2017 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package _CAL.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    CAL.Period
#
# Purpose
#    Classes modelling calendary periods, like `Month`, `Quarter`, or `Year`
#
# Revision Dates
#    19-Apr-2016 (CT) Creation
#    17-Jun-2016 (CT) Fix `__iter__`, add tests
#     5-Jan-2017 (CT) Fix doctest of `Week` (set `Week.now`)
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _CAL                       import CAL
from   _TFL                       import TFL

import _CAL.Date
import _CAL.Delta
from   _CAL.Year                  import _Ordinal_


from   _TFL.pyk                   import pyk
from   _TFL.Regexp                import *
import _TFL._Meta.Object
import _TFL._Meta.Once_Property
from   _TFL._Meta.Property        import Alias_Property, Class_Property

@pyk.adapt__str__
class _Period_ (_Ordinal_) :
    """Base class for calendary periods."""

    @TFL.Meta.Once_Property
    def days (self) :
        """Number of days in period."""
        return (self.finis - self.start).days + 1
    # end def days

    @TFL.Meta.Once_Property
    def finis (self) :
        """End date of period."""
        return self.start + self._delta - 1
    # end def finis

    @Class_Property
    def now (self) :
        return CAL.Date ()
    # end def now

    @TFL.Meta.Once_Property
    def ordinal (self) :
        """Ordinal of period instance; used for comparison. """
        return self.start.ordinal
    # end def ordinal

    @TFL.Meta.Once_Property
    def start (self) :
        """Start date of period."""
        return CAL.Date (self.year, self.month, 1)
    # end def start

    @classmethod
    def from_date (cls, date) :
        """Create instance from `date`."""
        return cls (date.year, getattr (date, cls.kind))
    # end def from_date

    @classmethod
    def from_string (cls, s, add_year = False, future_p = False) :
        """Create instance from string representation `s` of period.

           If `year` is missing from `s`, use current year if a true value is
           passed for `add_year`; for true `future_p`, use next year if that is
           necessary to move the result to the future.
        """
        result = cls.from_string_p (s, add_year = add_year, future_p = future_p)
        if result is None :
            date   = CAL.Date.from_string (s)
            result = cls.from_date (date)
        return result
    # end def from_string

    @classmethod
    def from_string_p (cls, s, add_year = False, future_p = False) :
        """Create instance from string representation `s` using only `pattern`
           for matching. If there is no match, return `None`.
        """
        pat = cls._pattern
        if pat is not None :
            match = pat.match (s)
            if match :
                kw = cls._from_string_match_kw (s, match, add_year, future_p)
                return cls (** kw)
    # end def from_string_p

    @classmethod
    def _from_string_match_kw \
            (cls, s, match, add_year = False, future_p = False) :
        result = CAL.Date._from_string_match_kw (s, match)
        if "year" not in result :
            if add_year :
                now = cls.now
                y   = now.year
                if future_p and getattr (now, cls.kind) >= result [cls.kind] :
                    y += 1
                result ["year"] = y
            else :
                raise ValueError (s)
        return result
    # end def _from_string_match_kw

    def __add__ (self, rhs) :
        d = self.start + self._delta * rhs
        return self.from_date (d)
    # end def __add__

    def __iter__ (self) :
        d = CAL.Date_Delta (1)
        f = self.finis
        s = self.start
        while s <= f :
            yield s
            s += d
    # end def __iter__

    def __len__ (self) :
        return self.days
    # end def __len__

    def __repr__ (self) :
        return "%s (%s, %s)" % \
            (self.__class__.__name__, self.year, self.number)
    # end def __repr__

    def __str__ (self) :
        return self.format % (self.year, self.number)
    # end def __str__

    def __sub__ (self, rhs) :
        d = self.start - self._delta * rhs
        return self.from_date (d)
    # end def __sub__

# end class _Period_

@pyk.adapt__str__
class Day (_Period_) :
    """Model a calendary day.

    >>> from _TFL.json_dump import to_string as jsonified
    >>> p = Day (2016, 2, 27)
    >>> print (p, p.days, p.start, p.finis)
    2016-02-27 1 2016-02-27 2016-02-27

    >>> print (jsonified ([p]))
    ["2016-02-27"]

    >>> for d in p :
    ...     print (d)
    2016-02-27

    >>> for i in range (5) :
    ...     r = p + i
    ...     print (r, r.days, r.start, r.finis)
    ...
    2016-02-27 1 2016-02-27 2016-02-27
    2016-02-28 1 2016-02-28 2016-02-28
    2016-02-29 1 2016-02-29 2016-02-29
    2016-03-01 1 2016-03-01 2016-03-01
    2016-03-02 1 2016-03-02 2016-03-02

    >>> p > r
    False
    >>> p < r
    True
    >>> p == r
    False
    >>> p == p
    True

    """

    days             = property (lambda s : 1)
    finis            = Alias_Property ("start")
    format           = "%4.4d-%2.2d-%2.2d"
    kind             = "day"
    number           = Alias_Property (kind)

    _delta           = CAL.Date_Delta (1)
    _pattern         = None

    def __init__ (self, year, month, day) :
        self.year  = year
        self.month = month
        self.day   = day
    # end def __init__

    @classmethod
    def from_date (cls, date) :
        return cls (date.year, date.month, date.day)
    # end def from_date

    @TFL.Meta.Once_Property
    def start (self) :
        return CAL.Date (self.year, self.month, self.day)
    # end def start

    def __repr__ (self) :
        return "%s (%s, %s, %s)"  % \
            (self.__class__.__name__, self.year, self.month, self.day)
    # end def __repr__

    def __str__ (self) :
        return self.format % (self.year, self.month, self.day)
    # end def __str__

# end class Day

@pyk.adapt__str__
class Interval (_Period_) :
    """Model an arbitrary calendary interval.

    >>> from _TFL.json_dump import to_string as jsonified

    >>> s = CAL.Date (2016, 4, 11)
    >>> f = CAL.Date (2016, 4, 14)

    >>> p = Interval (s, f)

    >>> print (p, p.days, p.start, p.finis)
    2016-04-11..2016-04-14 4 2016-04-11 2016-04-14

    >>> print (jsonified ([p]))
    ["2016-04-11..2016-04-14"]

    >>> for d in p :
    ...     print (d)
    2016-04-11
    2016-04-12
    2016-04-13
    2016-04-14

    >>> for i in range (5) :
    ...     r = p + i
    ...     print (r, r.days, r.start, r.finis)
    ...
    2016-04-11..2016-04-14 4 2016-04-11 2016-04-14
    2016-04-12..2016-04-15 4 2016-04-12 2016-04-15
    2016-04-13..2016-04-16 4 2016-04-13 2016-04-16
    2016-04-14..2016-04-17 4 2016-04-14 2016-04-17
    2016-04-15..2016-04-18 4 2016-04-15 2016-04-18

    >>> Interval.from_string ("2016-04-18")
    Interval (Date (2016, 4, 18), Date (2016, 4, 18))

    >>> print (Interval.from_string ("2016-04-18 - 2016-04-19"))
    2016-04-18..2016-04-19

    >>> print (Interval.from_string ("2016-04-18 – 2016-04-19"))
    2016-04-18..2016-04-19

    >>> print (Interval.from_string ("2016-04-18–2016-04-19"))
    2016-04-18..2016-04-19

    >>> print (Interval.from_string ("2016-04-18 .. 2016-04-19"))
    2016-04-18..2016-04-19

    >>> print (Interval.from_string ("2016-04-18..2016-04-19"))
    2016-04-18..2016-04-19

    """

    format           = "%s..%s"
    kind             = ""
    number           = Alias_Property (kind)

    _delta           = CAL.Date_Delta (1)
    _pattern         = Regexp \
        ( r"(?P<start>[^ –]+)(?: - | ?(?:–|\.\.) ?)(?P<finis>[^ ]+)$"
        )

    def __init__ (self, start, finis) :
        self.start = start
        self.finis = finis
    # end def __init__

    @property
    def finis (self) :
        return self._finis
    # end def finis

    @finis.setter
    def finis (self, value) :
        self._finis = value
    # end def finis

    @TFL.Meta.Once_Property
    def month (self) :
        return self.start.month
    # end def month

    @property
    def start (self) :
        return self._start
    # end def start

    @start.setter
    def start (self, value) :
        self._start = value
    # end def start

    @classmethod
    def from_date (cls, date) :
        return cls (date, date)
    # end def from_date

    @classmethod
    def _from_string_match_kw \
            (cls, s, match, add_year = False, future_p = False) :
        s      = CAL.Date.from_string (match.group ("start"))
        f      = CAL.Date.from_string (match.group ("finis"))
        result = dict (start = s, finis = f)
        return result
    # end def _from_string_match_kw

    def __add__ (self, rhs) :
        delta = self._delta * rhs
        return self.__class__ (self.start + delta, self.finis + delta)
    # end def __add__

    def __repr__ (self) :
        return "%s (%r, %r)" % \
            (self.__class__.__name__, self.start, self.finis)
    # end def __repr__

    def __str__ (self) :
        return self.format % (self.start, self.finis)
    # end def __str__

    def __sub__ (self, rhs) :
        delta = self._delta * rhs
        return self.__class__ (self.start - delta, self.finis - delta)
    # end def __sub__

# end class Interval

class Month (_Period_) :
    """Model a calendary month.

    >>> from _TFL.json_dump import to_string as jsonified
    >>> p = Month (2016, 1)
    >>> print (p, p.days, p.start, p.finis)
    2016-01 31 2016-01-01 2016-01-31

    >>> print (jsonified ([p]))
    ["2016-01"]

    >>> p_days = list (p)
    >>> print (p_days [0], "..", p_days [-1], ":", len (p_days))
    2016-01-01 .. 2016-01-31 : 31

    >>> for i in range (8) :
    ...     r = p + i
    ...     print (r, r.days, r.start, r.finis)
    ...
    2016-01 31 2016-01-01 2016-01-31
    2016-02 29 2016-02-01 2016-02-29
    2016-03 31 2016-03-01 2016-03-31
    2016-04 30 2016-04-01 2016-04-30
    2016-05 31 2016-05-01 2016-05-31
    2016-06 30 2016-06-01 2016-06-30
    2016-07 31 2016-07-01 2016-07-31
    2016-08 31 2016-08-01 2016-08-31

    >>> p > r
    False
    >>> p < r
    True
    >>> p == r
    False
    >>> p == p
    True

    >>> Month.from_string ("2014/02")
    Month (2014, 2)

    >>> Month.from_string ("2014/03/28")
    Month (2014, 3)

    >>> with TFL.I18N.test_language ("de") :
    ...     Month.from_string ("2014-mai")
    Month (2014, 5)

    >>> Month.from_string ("2014/Q1")
    Traceback (most recent call last):
      ...
    ValueError: 2014/Q1

    """

    format           = "%4.4d-%2.2d"
    kind             = "month"
    number           = Alias_Property (kind)

    _delta           = CAL.Month_Delta (1)
    _pattern         = Multi_Regexp \
        ( r"(?P<year>  \d{4,4})    (?:     [-/])  (?P<month> \d{2,2})   $"
        , r"(?P<year>  \d{4,4})    (?: \s+|[-/])  (?P<month> [a-z]+)    $"
        , r"(?P<month> [a-z]+) (?: (?: \s+|[-/.]) (?P<year>  \d{4,4}))? $"
        , flags      = re.VERBOSE | re.IGNORECASE
        )

    def __init__ (self, year, month) :
        self.year    = year
        self.month   = month
    # end def __init__

# end class Month

class Quarter (_Period_) :
    """Model a calendary quarter.

    >>> from _TFL.json_dump import to_string as jsonified
    >>> p = Quarter (2000, 1)
    >>> print (p, p.days, p.start, p.finis)
    2000/Q1 91 2000-01-01 2000-03-31

    >>> print (jsonified ([p]))
    ["2000/Q1"]

    >>> p_days = list (p)
    >>> print (p_days [0], "..", p_days [-1], ":", len (p_days))
    2000-01-01 .. 2000-03-31 : 91

    >>> for i in range (8) :
    ...     r = p + i
    ...     print (r, r.days, r.start, r.finis)
    ...
    2000/Q1 91 2000-01-01 2000-03-31
    2000/Q2 91 2000-04-01 2000-06-30
    2000/Q3 92 2000-07-01 2000-09-30
    2000/Q4 92 2000-10-01 2000-12-31
    2001/Q1 90 2001-01-01 2001-03-31
    2001/Q2 91 2001-04-01 2001-06-30
    2001/Q3 92 2001-07-01 2001-09-30
    2001/Q4 92 2001-10-01 2001-12-31

    >>> p > r
    False
    >>> p < r
    True
    >>> p == r
    False
    >>> p == p
    True

    >>> Quarter.from_string ("2014/Q1")
    Quarter (2014, 1)

    >>> Quarter.from_string ("Q1 2015")
    Quarter (2015, 1)

    >>> Quarter.from_string ("2016-01-29")
    Quarter (2016, 1)

    >>> Quarter.from_string ("2015-01")
    Traceback (most recent call last):
      ...
    ValueError: 2015-01

    """

    format           = "%4.4d/Q%d"
    kind             = "quarter"
    number           = Alias_Property (kind)

    _delta           = CAL.Month_Delta (3)
    _pattern         = Multi_Regexp \
        ( r"(?P<year>     \d{4,4})     (?:     [-/]) Q(?P<quarter> \d{1,1})   $"
        , r"Q(?P<quarter> \d{1,1}) (?: (?: \s+|[-/]) (?P<year>     \d{4,4}))? $"
        , flags      = re.VERBOSE | re.IGNORECASE
        )

    def __init__ (self, year, quarter) :
        if not (1 <= quarter <= 4) :
            raise ValueError ("Illegal value for quarter: '%s'" % (quarter, ))
        self.year    = year
        self.quarter = quarter
    # end def __init__

    @TFL.Meta.Once_Property
    def month (self) :
        return 1 + 3 * (self.quarter - 1)
    # end def month

# end class Quarter

class Week (_Period_) :
    """Model a calendary week.

    >>> from _TFL.json_dump import to_string as jsonified

    >>> p = Week (2016, 16)
    >>> print (p, p.days, p.start, p.finis)
    2016/W16 7 2016-04-18 2016-04-24

    >>> print (jsonified ([p]))
    ["2016/W16"]

    >>> p_days = list (p)
    >>> print (p_days [0], "..", p_days [-1], ":", len (p_days))
    2016-04-18 .. 2016-04-24 : 7

    >>> print (", ".join (str (d) for d in p))
    2016-04-18, 2016-04-19, 2016-04-20, 2016-04-21, 2016-04-22, 2016-04-23, 2016-04-24

    >>> for i in range (5) :
    ...     r = p + i
    ...     print (r, r.days, r.start, r.finis)
    ...
    2016/W16 7 2016-04-18 2016-04-24
    2016/W17 7 2016-04-25 2016-05-01
    2016/W18 7 2016-05-02 2016-05-08
    2016/W19 7 2016-05-09 2016-05-15
    2016/W20 7 2016-05-16 2016-05-22

    >>> p > r
    False
    >>> p < r
    True
    >>> p == r
    False
    >>> p == p
    True

    >>> Week.from_string ("2016/W1")
    Week (2016, 1)

    >>> Week.now = CAL.Date (2016, 4, 19)
    >>> Week.from_string ("W13", add_year = True)
    Week (2016, 13)

    """

    format           = "%4.4d/W%d"
    kind             = "week"
    number           = Alias_Property (kind)
    start            = Alias_Property ("monday")

    _delta           = CAL.Date_Delta (7)
    _pattern         = Multi_Regexp \
        ( r"(?P<year>  \d{4,4})     (?:     [-/]) W(?P<week> \d{1,2})   $"
        , r"W(?P<week> \d{1,2}) (?: (?: \s+|[-/])  (?P<year> \d{4,4}))? $"
        , flags      = re.VERBOSE | re.IGNORECASE
        )

    def __init__ (self, * args, ** kw) :
        if kw :
            date    = kw.pop ("date")
            if args or kw :
                raise TypeError \
                    ("Need a single `date` arg or two args (year, week)")
        elif len (args) == 1 :
            date    = args [0]
            date   -= date.weekday
        else :
            date    = self._monday (* args)
        self.monday = date
        self.year   = date.year
        self.week   = date.week
    # end def __init__

    @TFL.Meta.Once_Property
    def month (self) :
        return self.monday.month
    # end def month

    @classmethod
    def from_date (cls, date) :
        return cls (date)
    # end def from_date

    @classmethod
    def _from_string_match_kw \
            (cls, s, match, add_year = False, future_p = False) :
        result = CAL.Date._from_string_match_kw (s, match)
        week   = result.pop ("week")
        year   = result.get ("year")
        if year is None :
            if add_year :
                now  = cls.now
                year = now.year
                if future_p and getattr (now, cls.kind) >= week :
                    year += 1
            else :
                raise ValueError (s)
        return dict (date = cls._monday (year, week))
    # end def _from_string_match_kw

    @classmethod
    def _monday (cls, year, week) :
        from _CAL.Year import Year as Y
        try :
            return Y (year).weeks [week].mon.date
        except IndexError :
            raise ValueError ("Invalid value for week: '%s'" % (week, ))
        except Exception :
            raise ValueError (cls.format % (year, week))
    # end def _monday

# end class Week

@pyk.adapt__str__
class Year (_Period_) :
    """Model a calendary year.

    >>> from _TFL.json_dump import to_string as jsonified
    >>> p = Year (2012)
    >>> print (p, p.days, p.start, p.finis)
    2012 366 2012-01-01 2012-12-31

    >>> print (jsonified ([p]))
    ["2012"]

    >>> p_days = list (p)
    >>> print (p_days [0], "..", p_days [-1], ":", len (p_days))
    2012-01-01 .. 2012-12-31 : 366

    >>> for i in range (5) :
    ...     r = p + i
    ...     print (r, r.days, r.start, r.finis)
    ...
    2012 366 2012-01-01 2012-12-31
    2013 365 2013-01-01 2013-12-31
    2014 365 2014-01-01 2014-12-31
    2015 365 2015-01-01 2015-12-31
    2016 366 2016-01-01 2016-12-31

    >>> p > r
    False
    >>> p < r
    True
    >>> p == r
    False
    >>> p == p
    True

    """

    format           = "%4.4d"
    kind             = "year"
    number           = Alias_Property (kind)
    month            = property (lambda s : 1)

    _delta           = CAL.Month_Delta (12)
    _pattern         = Regexp \
        ( r"(?P<year> \d{4,4})"
          r"$"
        , flags      = re.VERBOSE
        )

    def __init__ (self, year, _ = None) :
        self.year = year
    # end def __init__

    @classmethod
    def from_date (cls, date) :
        return cls (date.year)
    # end def from_date

    def __repr__ (self) :
        return "%s (%s)"  % (self.__class__.__name__, self.number)
    # end def __repr__

    def __str__ (self) :
        return self.format % (self.number, )
    # end def __str__

# end class Year

def from_string (s, add_year = False, future_p = False) :
    """Return instance of the period matching `s`.

    >>> from_string ("2016/Apr")
    Month (2016, 4)

    >>> from_string ("2016 April")
    Month (2016, 4)

    >>> from_string ("Apr 2016")
    Month (2016, 4)

    >>> from_string ("Apr.2016")
    Month (2016, 4)

    >>> from_string ("Mar")
    Traceback (most recent call last):
      ...
    ValueError: Mar

    ### assign `now` to literal to make the following tests with `add_year`
    ### deterministic
    >>> _Period_.now = CAL.Date (2016, 4, 20)
    >>> for m in ("Mar", "Apr", "May") :
    ...     from_string (m, add_year = True)
    ...     from_string (m, add_year = True, future_p = True)
    Month (2016, 3)
    Month (2017, 3)
    Month (2016, 4)
    Month (2017, 4)
    Month (2016, 5)
    Month (2016, 5)

    >>> from_string ("2016/Dek")
    Traceback (most recent call last):
      ...
    ValueError: Illegal value for month: 'Dek'

    >>> from_string ("2016/13")
    Traceback (most recent call last):
      ...
    ValueError: Illegal value for month: '13'

    >>> from_string ("2016/Q3")
    Quarter (2016, 3)

    >>> from_string ("2016/Q5")
    Traceback (most recent call last):
      ...
    ValueError: Illegal value for quarter: '5'

    >>> from_string ("Q2", add_year = True)
    Quarter (2016, 2)

    >>> from_string ("Q2", add_year = True, future_p = True)
    Quarter (2017, 2)

    >>> from_string ("Q3 2018")
    Quarter (2018, 3)

    >>> from_string ("2018")
    Year (2018)

    >>> from_string ("2016-04-20")
    Day (2016, 4, 20)

    >>> from_string ("2016/W42")
    Week (2016, 42)

    >>> from_string ("2016/W54")
    Traceback (most recent call last):
      ...
    ValueError: Invalid value for week: '54'

    >>> print (from_string ("2016-12-29..2017-01-03"))
    2016-12-29..2017-01-03

    >>> print (from_string ("2016-13-29..2016-01-03"))
    Traceback (most recent call last):
      ...
    ValueError: Illegal value for month: '13'

    >>> print (from_string ("2016-12-29..2016-13-03"))
    Traceback (most recent call last):
      ...
    ValueError: Illegal value for month: '13'

    """
    error = None
    for T in (Week, Month, Quarter, Year, Interval) :
        try :
            result = T.from_string_p \
                (s, add_year = add_year, future_p = future_p)
        except ValueError as exc :
            error = exc
        else :
            if result is not None :
                break
    else :
        try :
            result = Day.from_string (s)
        except Exception as exc :
            if error is not None :
                raise error
            raise
    return result
# end def from_string

if __name__ != "__main__" :
    CAL._Export_Module ()
### __END__ CAL.Period
