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
#    CAL.Date
#
# Purpose
#    Wrapper around `datetime.date`
#
# Revision Dates
#    14-Oct-2004 (CT) Creation
#                     (derived from MG's CAL.Date_Time and CT's Date_Time)
#    17-Oct-2004 (CT) `__add__` and `__sub__` changed to use `Delta.dt_op`
#    17-Oct-2004 (CT) Doctest for `Month_Delta` added
#    17-Oct-2004 (CT) s/Month_Delta/MY_Delta/
#    19-Oct-2004 (CT) s/MY_Delta/Month_Delta/
#    23-Oct-2004 (CT) `_default_format` added
#    23-Oct-2004 (CT) `_new_object` redefined to handle negative values for
#                     `day`
#    26-Oct-2004 (CT) `is_weekday` added
#     2-Nov-2004 (CT) `from_string` added
#    10-Nov-2004 (CT) `from_ordinal` added
#    15-Nov-2004 (CT) `wk_ordinal` added
#     6-Jan-2005 (CT) `__main__` script added
#    01-Sep-2005 (MG) Use new decorator syntax for defining classmethod
#    30-Nov-2006 (CT) `__getattr__` changed to delegate to
#                     `__super.__getattr__`
#    30-Nov-2006 (CT) `CJD`, `MJD`, and `TJD` added
#    10-Dec-2006 (CT) `JD_offset` factored
#    10-Dec-2006 (CT) `from_julian` added
#    12-Dec-2006 (CT) `from_ordinal` changed to use `cls._kind` and
#                     `cls._Type` instead of `date` and `datetime.date`
#    12-Jan-2007 (CT) Imports fixed
#                     (import `Command_Line` and `Regexp` from _TFL)
#    11-Aug-2007 (CT) `quarter` added
#     7-Nov-2007 (CT) Use `Getter` instead of `lambda`
#     8-Nov-2007 (CT) `JD2000`, `JC_J2000`, and `julian_epoch` added
#     9-Nov-2007 (CT) Use `Once_Property` instead of `__getattr__`
#    11-Nov-2007 (CT) `sidereal_time` added
#    11-Nov-2007 (CT) `delta_T` added
#    12-Nov-2007 (CT) `JD` added, coverage of `delta_T` extended
#    23-Dec-2007 (CT) Command_Line options `-regexp` and `-xformat` added
#     3-Jan-2008 (CT) `_from_string_match_kw` factored
#     3-Jan-2008 (CT) `date_pattern` changed to make `year` mandatory
#    10-Feb-2008 (CT) `Date_Opt` added (and used for option `delta_to`)
#    15-Feb-2008 (CT) `Date_Opt` corrected (up-call to `__init__`)
#     8-May-2008 (CT) `Date_Opt` changed to use `__super`
#     4-Jan-2010 (CT) `_Date_Arg_` based on `TFL.CAO` added, `Date_Opt` removed
#    28-Feb-2014 (CT) Use future `print_function`
#     4-Mar-2014 (CT) Add subtraction test cases for `Month_Delta`
#     6-May-2015 (CT) Add tests for `jsonified`
#    29-Jan-2016 (CT) Change `_default_format` to "%Y-%m-%d"
#     2-Feb-2016 (CT) Add translation markup `_`
#     3-Feb-2016 (CT) Add `periods`, `inc_month`
#    15-Feb-2016 (CT) Use `CAL.G8R.Months` to support localized month names
#    29-Mar-2016 (CT) Add support for delta to `_Date_Arg_`
#    19-Apr-2016 (CT) DRY `_from_string_match_kw`
#    20-Apr-2016 (CT) Factor `month_from_string`
#    21-Apr-2016 (CT) Add check for tail to `from_string`
#    14-May-2016 (CT) Strip leading `+` from delta arg for `_Date_Arg_`
#    26-Sep-2016 (CT) Move `sidereal_time` to `CAL.Sky`
#    30-Nov-2016 (CT) Use `CAL.G8R.Months.LC`, not `CAL.G8R.Months`
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _CAL                     import CAL
from   _TFL                     import TFL

import _CAL._DTW_
import _CAL.G8R

import _TFL.Accessor
import _TFL.CAO

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL.I18N                import _, _T, _Tn
from   _TFL.Math_Func           import horner
from   _TFL.pyk                 import pyk
from   _TFL.Regexp              import *

import datetime
import operator

class Date (CAL._DTW_) :
    """Model a (gregorian) date.

       >>> from _CAL.Delta import Date_Delta as Delta
       >>> d = Date (2004, 10, 14)
       >>> print (d)
       2004-10-14
       >>> d.year, d.month, d.day, d.date, d.week, d.weekday, d.ordinal
       (2004, 10, 14, datetime.date(2004, 10, 14), 42, 3, 731868)
       >>> d = d - Delta (3)
       >>> d.year, d.month, d.day, d.date, d.week, d.weekday, d.ordinal
       (2004, 10, 11, datetime.date(2004, 10, 11), 42, 0, 731865)
       >>> d = d - 1
       >>> d.year, d.month, d.day, d.date, d.week, d.weekday, d.ordinal
       (2004, 10, 10, datetime.date(2004, 10, 10), 41, 6, 731864)
       >>> from _CAL.Delta import Month_Delta
       >>> print (d, d + Month_Delta (1), d - Month_Delta (1))
       2004-10-10 2004-11-10 2004-09-10
       >>> print (d, d + Month_Delta (3), d - Month_Delta (3))
       2004-10-10 2005-01-10 2004-07-10
       >>> print (d, d + Month_Delta (12), d - Month_Delta (12))
       2004-10-10 2005-10-10 2003-10-10
       >>> print (d, d + Month_Delta (15), d - Month_Delta (15))
       2004-10-10 2006-01-10 2003-07-10
       >>> print (d, d + Month_Delta (24), d - Month_Delta (24))
       2004-10-10 2006-10-10 2002-10-10
       >>> print (d, d + Month_Delta (-1), d - Month_Delta (-1))
       2004-10-10 2004-09-10 2004-11-10
       >>> print (d, d + Month_Delta (-12), d - Month_Delta (-12))
       2004-10-10 2003-10-10 2005-10-10
       >>> MD = Month_Delta
       >>> for x in (d + MD (m) for m in range (-12, 13, 3)):
       ...     print (str (x), ":", x.quarter)
       2003-10-10 : 4
       2004-01-10 : 1
       2004-04-10 : 2
       2004-07-10 : 3
       2004-10-10 : 4
       2005-01-10 : 1
       2005-04-10 : 2
       2005-07-10 : 3
       2005-10-10 : 4
       >>> d = Date (day = 1, month = 1, year = 2004)
       >>> print (d, d + Month_Delta (11))
       2004-01-01 2004-12-01
       >>> d1 = Date (2004, 10, 14)
       >>> d2 = Date (2004, 10, 16)
       >>> print (d1 - d2)
       -2 days, 0:00:00
       >>> d = Date (day = -1, month = 1, year = 2004)
       >>> print (d, d + Month_Delta (1))
       2004-01-31 2004-02-29
       >>> print (d, d + Month_Delta (2))
       2004-01-31 2004-03-31
       >>> print (d, d + Month_Delta (3))
       2004-01-31 2004-04-30
       >>> print (d, d + Month_Delta (11))
       2004-01-31 2004-12-31
       >>> print (d, d + Month_Delta (12))
       2004-01-31 2005-01-31
       >>> print (d, d + Month_Delta (13))
       2004-01-31 2005-02-28
       >>> print (d, d + Month_Delta (-1))
       2004-01-31 2003-12-31
       >>> print (d, d + Month_Delta (-2))
       2004-01-31 2003-11-30
       >>> print (d, d + Month_Delta (-3))
       2004-01-31 2003-10-31
       >>> print (d, d + Month_Delta (-11))
       2004-01-31 2003-02-28
       >>> print (Date.from_string ("20041102"))
       2004-11-02
       >>> print (Date.from_string ("2004/11/02"))
       2004-11-02
       >>> print (Date.from_string ("20041102"))
       2004-11-02
       >>> print (Date.from_string ("31.10.2004"))
       2004-10-31
       >>> print (Date.from_string ("31/10/2004"))
       2004-10-31
       >>> print (Date.from_string ("31.Oct.2004"))
       2004-10-31
       >>> print (Date.from_string ("Oct 5, 2004"))
       2004-10-05

       >>> from _TFL.json_dump import to_string as jsonified
       >>> print (jsonified ([d]))
       ["2004-01-31"]

       >>> mjd_epoch = Date (1858, 11, 17)
       >>> tjd_epoch = Date (1968,  5, 24)
       >>> mjd_epoch.ordinal, mjd_epoch.CJD, mjd_epoch.MJD, mjd_epoch.TJD
       (678576, 2400000, 0, -40000)
       >>> tjd_epoch.ordinal, tjd_epoch.CJD, tjd_epoch.MJD, tjd_epoch.TJD
       (718576, 2440000, 40000, 0)

       >>> Date.from_julian (2400000)
       Date (1858, 11, 17)
       >>> Date.from_julian (2440000)
       Date (1968, 5, 24)
       >>> Date.from_julian (40000, kind = "MJD")
       Date (1968, 5, 24)

       >>> with TFL.I18N.test_language ("de") :
       ...     print (Date.from_string ("31-Oktober-2004"))
       2004-10-31
       >>> def _show_periods (d) :
       ...   print (d, "::")
       ...   for p, (h, t) in sorted (pyk.iteritems (d.periods)) :
       ...     print ("%-7s" % p, h, t)

       >>> d = Date (2016, 2, 3)

       >>> _show_periods (d)
       2016-02-03 ::
       month   2016-02-01 2016-02-29
       quarter 2016-01-01 2016-03-31
       week    2016-02-01 2016-02-07
       year    2016-01-01 2016-12-31

       >>> _show_periods (d + 94)
       2016-05-07 ::
       month   2016-05-01 2016-05-31
       quarter 2016-04-01 2016-06-30
       week    2016-05-02 2016-05-08
       year    2016-01-01 2016-12-31

       >>> _show_periods (d + 194)
       2016-08-15 ::
       month   2016-08-01 2016-08-31
       quarter 2016-07-01 2016-09-30
       week    2016-08-15 2016-08-21
       year    2016-01-01 2016-12-31

       >>> _show_periods (d + 294)
       2016-11-23 ::
       month   2016-11-01 2016-11-30
       quarter 2016-10-01 2016-12-31
       week    2016-11-21 2016-11-27
       year    2016-01-01 2016-12-31

       >>> for i in range (-4, 15, 3) :
       ...     print ("%s + %2d months --> %s" % (d, i, d.inc_month (i)))
       2016-02-03 + -4 months --> 2015-10-03
       2016-02-03 + -1 months --> 2016-01-03
       2016-02-03 +  2 months --> 2016-04-03
       2016-02-03 +  5 months --> 2016-07-03
       2016-02-03 +  8 months --> 2016-10-03
       2016-02-03 + 11 months --> 2017-01-03
       2016-02-03 + 14 months --> 2017-04-03

    """

    ### Julian date offsets to Rata Die (Jan 1, 1)
    ###     http://en.wikipedia.org/wiki/Julian_day_number
    ###     http://en.wikipedia.org/wiki/Epoch_%28astronomy%29
    JD_offset    = dict \
        ( CJD    =   1721424    ### Chronological JD (based on Jan  1, 4713 BC)
        , CJS    =   1721424
        , JD     =   1721424.5  ### Julian day (starts at noon)
        , JD2000 = -  730120.5  ### JD relative to J2000.0 (noon)
        , MJD    = -  678576    ### Modified      JD (based on Nov 17, 1858)
        , MJS    = -  678576
        , TJD    = -  718576    ### Truncated     JD (based on May 24, 1968)
        , TJS    = -  718576
        )

    months = \
        { _ ("jan") :  1, _ ("january")   :   1,  1 : "jan"
        , _ ("feb") :  2, _ ("february")  :   2,  2 : "feb"
        , _ ("mar") :  3, _ ("march")     :   3,  3 : "mar"
        , _ ("apr") :  4, _ ("april")     :   4,  4 : "apr"
        , _ ("may") :  5,                         5 : "may"
        , _ ("jun") :  6, _ ("june")      :   6,  6 : "jun"
        , _ ("jul") :  7, _ ("july")      :   7,  7 : "jul"
        , _ ("aug") :  8, _ ("august")    :   8,  8 : "aug"
        , _ ("sep") :  9, _ ("september") :   9,  9 : "sep"
        , _ ("oct") : 10, _ ("october")   :  10, 10 : "oct"
        , _ ("nov") : 11, _ ("november")  :  11, 11 : "nov"
        , _ ("dec") : 12, _ ("december")  :  12, 12 : "dec"
        }

    _Type            = datetime.date
    _default_format  = "%Y-%m-%d"
    _kind            = "date"
    _init_arg_names  = ("year", "month", "day")
    _timetuple_slice = lambda s, tt : tt [:3]

    date_pattern     = Multi_Regexp \
        ( r"(?P<year>  \d{4,4})"
          r"([-/]?)"
          r"(?P<month> \d{2,2})"
          r"\2"
          r"(?P<day>   \d{2,2})"
        , r"(?P<day>   \d{1,2})"
          r"([-./])"
          r"(?P<month> \d{1,2} | [a-z]{3,})"
          r"\2"
          r"(?P<year>  \d{4,4})"
        , r"(?P<month> [a-z]{3,})"
          r"\s"
          r"(?P<day>   \d{1,2})"
          r",\s*"
          r"(?P<year>  \d{4,4})"
        , flags = re.VERBOSE | re.IGNORECASE
        )

    day              = property (TFL.Getter._body.day)
    is_weekday       = property (lambda s : s.weekday < 5)
    month            = property (TFL.Getter._body.month)
    wk_ordinal       = property (lambda s : (s.ordinal - s.weekday) // 7)
    year             = property (TFL.Getter._body.year)

    yad              = None ### set for negative `day` arguments

    from _CAL.Delta import Date_Delta as Delta

    @Once_Property
    def delta_T (self) :
        """Arithmetic difference between Terrestrial Dynamical Time and UT in
           seconds.
           >>> Date (1988).delta_T
           56.0
           >>> Date (1995).delta_T
           61.0
           >>> Date (2000).delta_T
           64.0
           >>> Date (2007).delta_T
           65.0
           >>> Date (2010).delta_T
           67.0
           >>> Date (2050).delta_T
           93.0
           >>> Date (2051).delta_T
           Traceback (most recent call last):
           ...
           ValueError: Algorithm is restricted to 1800..2050, fails for 2051
           >>> [Date (y).delta_T for y in
           ... (1800, 1802, 1822, 1830, 1990, 1972, 1950)]
           [14.0, 12.0, 10.0, 7.0, 57.0, 43.0, 27.0]
        """
        ### see http://sunearth.gsfc.nasa.gov/eclipse/SEcat5/deltat.html
        ### and http://sunearth.gsfc.nasa.gov/eclipse/SEcat5/deltatpoly.html
        ### see J. Meeus, ISBN 0-943396-61-1, p.80
        y = self.year
        t = y - 2000.
        if -19 <= t < 5 :
            return round \
                ( 63.86
                + t * ( 0.3345
                      + t * ( -0.060374
                            + t * ( 0.0017275
                                  + t * ( 0.000651814
                                        + t * 0.00002373599
                                        )
                                  )
                            )
                      )
                )
        elif -200 <= t <= -3 :
            t = (self.JD - Date (1900).JD) / 36525.
            return round \
                ( horner
                    ( t
                    , ( -1.02, 91.02, 265.90, -839.16, -1545.20
                      , 3603.62, 4385.98, -6993.23, -6090.04
                      , 6298.12, 4102.86, -2137.64, -1081.51
                      )
                    )
                )
        elif 5 <= t <= 50 :
            return round (62.92 + t * (0.32217 + t * 0.005589))
        else :
            raise ValueError \
                ("Algorithm is restricted to 1800..2050, fails for %s" % (y, ))
    # end def delta_T

    @classmethod
    def from_julian (cls, jd, kind = "CJD") :
        ordinal = int (jd) - cls.JD_offset [kind]
        if kind.endswith ("S") :
            ordinal //= 86400
        return cls.from_ordinal (ordinal)
    # end def from_julian

    @classmethod
    def from_ordinal (cls, ordinal) :
        return cls (** {cls._kind : cls._Type.fromordinal (ordinal)})
    # end def from_ordinal

    @classmethod
    def from_string (cls, s, check_tail = True) :
        match = cls.date_pattern.match (s)
        if match and ((not check_tail) or match.end () == len (s.rstrip ())) :
            return cls (** cls._from_string_match_kw (s, match))
        else :
            raise ValueError (s)
    # end def from_string

    @classmethod
    def month_from_string (cls, s) :
        v = CAL.G8R.Months.LC (s)
        try :
            result = cls.months [v]
        except KeyError :
            try :
                result = int (s)
            except Exception as exc :
                error = exc
            else :
                error = None
            if error or not (1 <= result <= 12) :
                raise ValueError ("Illegal value for month: '%s'" % s)
        return result
    # end def month_from_string

    @classmethod
    def str_dates_in_range (cls, after, before, str_dates) :
        """Yield `(date, str)` for all elements of `str_dates` in `(before, after)`."""
        for sd in str_dates :
            try :
                d = cls.from_string (sd)
            except ValueError :
                pass
            else :
                if after  and d <= after  : continue
                if before and d >= before : continue
                yield d, sd
    # end def str_dates_in_range

    @Once_Property
    def JC_J2000 (self) :
        """Julian Century relative to 2000"""
        return (self.JD - 2451545.0) / 36525.0
    # end def JC_J2000

    @Once_Property
    def julian_epoch (self) :
        """Epoch based on julian years"""
        return 2000.0 + self.JD2000 / 365.25
    # end def julian_epoch

    @Once_Property
    def month_name (self) :
        return self.strftime ("%b")
    # end def month_name

    @Once_Property
    def ordinal (self) :
        """Rata Die (based on January 1, 1)"""
        return self._body.toordinal ()
    # end def ordinal

    @Once_Property
    def periods (self) :
        w = self - self.weekday
        m = self.replace (day = 1)
        q = m.replace    (month = (self.quarter - 1) * 3 + 1)
        y = m.replace    (month = 1)
        result = dict \
            ( week    = (w, w + 6)
            , month   = (m, m.inc_month (1) - 1)
            , quarter = (q, q.inc_month (3) - 1)
            , year    = (y, y.replace (year  = y.year  + 1) - 1)
            )
        return result
    # end def periods

    @Once_Property
    def quarter (self) :
        return (self.month - 1) // 3 + 1
    # end def quarter

    @Once_Property
    def rjd (self) :
        """Relative julian day (based on January 1 of `self.year`)"""
        return self._body.timetuple ().tm_yday
    # end def rjd

    @Once_Property
    def tuple (self) :
        return self._body.timetuple ()
    # end def tuple

    @Once_Property
    def week (self) :
        return self._body.isocalendar () [1]
    # end def week

    @Once_Property
    def weekday (self) :
        return self._body.weekday ()
    # end def weekday

    def inc_month (self, delta) :
        m = self.month + delta
        if 1 <= m <= 12 :
            kw = dict (month = m)
        else :
            yd, m = divmod (m - 1, 12)
            kw = dict (month = m + 1, year = self.year + yd)
        return self.replace (** kw)
    # end def inc_month

    def replace (self, ** kw) :
        if self.yad is None or "day" in kw :
            result = self.__super.replace (** kw)
        else :
            kw ["day"]   = 1
            yad          = self.yad
            result       = self.__super.replace (** kw)
            result._body = result._body.replace \
                (day = self._day_from_end (yad, result.month, result.year))
            result.yad   = yad
        return result
    # end def replace

    def _day_from_end (self, yad, month, year) :
        from _CAL.Year import Year
        return Year (year).mmap [month].days [yad].number
    # end def _day_from_end

    @classmethod
    def _from_string_match_kw (cls, s, match) :
        assert match
        kw = {}
        for k, v in pyk.iteritems (match.groupdict ()) :
            if v :
                if k == "month" :
                    v = cls.month_from_string (v)
                kw [k] = int (v)
        return kw
    # end def _from_string_match_kw

    def _new_object (self, kw) :
        d = kw ["day"]
        if d < 0 :
            kw ["day"] = self._day_from_end (d, kw ["month"], kw ["year"])
            self.yad   = d
        return self.__super._new_object (kw)
    # end def _new_object

    def __getattr__ (self, name) :
        if name in self.JD_offset :
            result = self.ordinal + self.JD_offset [name]
            if name.endswith ("S") :
                result *= 86400
            setattr (self, name, result)
        else :
            result = self.__super.__getattr__ (name)
        return result
    # end def __getattr__

    def __add__ (self, rhs) :
        delta  = self._delta (rhs)
        return delta.dt_op (self, operator.add)
    # end def __add__

    def __sub__ (self, rhs) :
        delta = self._delta (rhs)
        if isinstance (delta, CAL._Delta_) :
            result = delta.dt_op (self, operator.sub)
        else :
            if hasattr (rhs, "_body") :
                rhs = rhs._body
            result = self.Delta (** {self.Delta._kind : self._body - rhs})
        return result
    # end def __sub__

# end class Date

class Date_M (CAL._Mutable_DTW_) :
    """Mutable date object

       >>> d1 = d2 = Date_M (2004, 10, 14)
       >>> print (d1, d2)
       2004-10-14 2004-10-14
       >>> d1 += 1
       >>> print (d1, d2)
       2004-10-15 2004-10-15
    """

    Class = Date

# end class Date_M

class _Date_Arg_ (TFL.CAO.Str) :
    """Argument or option with a (calendary) date value"""

    _real_name = "Date"

    _CAL_Type  = Date
    _delta_pat = Regexp ("^[-+]")

    def cook (self, value, cao = None) :
        T = self._CAL_Type
        if value == "now" :
            result = T ()
        elif value :
            if self._delta_pat.match (value) :
                import _CAL.Relative_Delta
                delta  = CAL.Relative_Delta.from_string (value.lstrip ("+"))
                now    = T ()
                result = now + delta
                if type (result) is not T :
                    raise TypeError \
                        ( "Wrong delta %r forces Date_Time '%s', "
                          "need Date instead"
                        % (value, result)
                        )
            else :
                result = T.from_string (value)
        else :
            result = None
        return result
    # end def cook

# end class _Date_Arg_

def _main (cmd) :
    from _TFL.Caller import Scope
    ### Usage example for `-regexp` and `-xformat`::
    ### for f in *.tex; do
    ###   VCMove $f $(python /swing/python/Date.py -regexp '(?P<prefix> .*)_(?P<date> \d{2}-[A-Za-z][a-z]{2}-\d{4}|\d{8})\.?(?P<ext> .*)' -xformat '%(date)s_%(prefix)s.%(ext)s' $f)
    ### done
    if cmd.regexp :
        regexp = Regexp (cmd.regexp, re.VERBOSE)
        if regexp.search (cmd.base_date) :
            base_date  = regexp.date
            match_dict = regexp.groupdict ()
        else :
            import sys
            print \
                ( "`%s` doesn't match for `%s`"
                % (cmd.regexp, cmd.base_date)
                , file = sys.stderr
                )
            sys.exit (9)
    else :
        base_date   = cmd.base_date
        match_dict = {}
    base_date = Date.from_string (base_date)
    if cmd.offset :
        base_date += cmd.offset
    if cmd.delta_to :
        print ((base_date - cmd.delta_to).days)
    else :
        date = base_date.formatted (cmd.format)
        print (cmd.xformat % Scope (globs = match_dict, locls = vars ()))
# end def _main

_Command = TFL.CAO.Cmd \
    ( handler     = _main
    , args        =
        ( "base_date:S=%s" % Date (),)
    , opts        =
        ( TFL.CAO.Opt.Date
            ( name        = "delta_to"
            , description = "Print `base_date - delta_to`"
            )
        , "-format:S=%Y%m%d?Format for date (not used for -delta_to)"
        , "-offset:I=0?delta to `base_date` in days"
        , "-regexp:S?Use regexp to extract date from `base_date`"
        , "-xformat:S=%(date)s"
            "?Format used to format output (not used for -delta_to)"
        )
    , max_args    = 1
    )

if __name__ != "__main__" :
    CAL._Export ("*")
else :
    _Command ()
### __END__ CAL.Date
