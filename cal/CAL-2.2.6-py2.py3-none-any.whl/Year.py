# -*- coding: utf-8 -*-
# Copyright (C) 2003-2017 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    CAL.Year
#
# Purpose
#    Class modelling a calendar year
#
# Revision Dates
#     5-Apr-2003 (CT) Creation
#    13-Apr-2003 (CT) `Year.as_cal` changed
#    13-Apr-2003 (CT) `Day.as_plan` changed
#    13-Apr-2003 (CT) `create_diary` added
#    13-Apr-2003 (CT) `write_year` factored
#    13-Apr-2003 (CT) `-force` and guard against inadvertent overwriting added
#    19-Apr-2003 (CT) `add_appointments`  added to `Day`
#    19-Apr-2003 (CT) `sort_appointments` added to `Day` and `Year`
#    20-Apr-2003 (CT) `easter_date` added
#    15-Dec-2003 (CT) Computation of `w_head` corrected in `Year.__init__`
#     5-Jan-2004 (CT) `Week.__int__` added
#     8-Jan-2004 (CT) `Week.__nonzero__` and `Day.__nonzero__` added
#     8-Jan-2004 (CT) Doctest added to `Year`
#     6-Feb-2004 (CT) Made `Week` lazy and central to `Year`s working
#     6-Feb-2004 (CT) Made `Day` shared between weeks of different years in
#                     same calendar (concerns weeks 0, 1, 52, 53)
#     9-Feb-2004 (CT) Made `Month` and `Year` lazy, too
#    11-Feb-2004 (MG) `_day_names` added
#    15-Oct-2004 (CT) Adapted to use `CAL.Date` instead of
#                     `lib/python/Date_Time`
#    26-Oct-2004 (CT) `Year.__new__` added to cache years
#    26-Oct-2004 (CT) `is_weekday` changed to just delegate to `Date`
#     2-Nov-2004 (CT) Use `Date.from_string` instead of home-grown code
#     4-Nov-2004 (CT) `Week.ordinal` added
#    10-Nov-2004 (CT) `Day.__new__` changed to use `from_ordinal` to convert
#                     int/long to `datetime.date`
#    10-Nov-2004 (CT) `__cmp__` and `__hash__` added to `Day`
#    10-Nov-2004 (CT) `__cmp__` and `__hash__` added to `Week`
#    10-Nov-2004 (CT) `Year._week_creation_iter` factored
#    14-Nov-2004 (CT) `Day.wk_ordinal` added and used
#    14-Nov-2004 (CT) `Year._init_` changed to put weeks into `cal._weeks`
#    15-Nov-2004 (CT) `Day.wk_ordinal` moved to `Date`
#    10-Dec-2004 (CT) `_Cal_` removed (always use `CAl.Calendar`)
#    10-Dec-2004 (CT) Use `cal.day` to create days (instead of calling `Day`
#                     directly)
#    17-Jun-2005 (MG) `Day.is_weekday` fixed
#    11-Aug-2007 (CT) Imports corrected
#     7-Nov-2007 (CT) Use `Getter` instead of `lambda`
#     9-Mar-2010 (CT) `day_abbr`, `day_name`, `month_abbr`, and `month_name`
#                     added
#    10-Mar-2010 (CT) `Day.is_holiday` turned into property
#    15-Jun-2010 (CT) Use `CAO` instead of `Command_Line`
#    16-Jun-2010 (CT) Encode holiday names with `TFL.I18N.Config.encoding`
#    17-Jun-2010 (CT) Use `TFL.I18N.encode_o` instead of home-grown code
#    28-Feb-2014 (CT) Use future `print_function`
#     6-May-2015 (CT) Add `_import_cb_json_dump`
#     8-Oct-2015 (CT) Change `__getattr__` to *not* handle `__XXX__`
#    29-Jan-2016 (CT) Add `__add__`, `__sub__`
#    29-Jan-2016 (CT) Use Once_Property, not manually managed `populate`
#    29-Jan-2016 (CT) Change signature of `Day` to resemble `Year`
#    29-Jan-2016 (CT) Add `Quarter`
#     1-Feb-2016 (CT) Pass `cal.country` to `CAL.holidays`
#     2-Feb-2016 (CT) Add translation markup `_`
#    19-Apr-2016 (CT) Export `Year` only, not `*`;
#                     add `Day`, ..., `Week` to `Year`
#     1-Dec-2016 (CT) Use `CAL.G8R.Week_Day_Abbrs_2.words`, not home-grown
#                     definitions
#    16-Dec-2016 (CT) Add property `Day.Week`
#     5-Jan-2017 (CT) Fix doctest of `Quarter` (explicit `Year (2016)`!)
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _CAL                       import CAL
from   _TFL                       import TFL

import _CAL.Appointment
import _CAL.Date
import _CAL.G8R
import _CAL.Holiday

from   _TFL.I18N                  import _, _T, _Tn
from   _TFL.predicate             import *
from   _TFL.pyk                   import pyk
from   _TFL                       import sos
from   _TFL._Meta.totally_ordered import totally_ordered

import _TFL._Meta.Object
import _TFL._Meta.Once_Property
import _TFL.Accessor
import _TFL.CAO
import _TFL.I18N

import itertools

@totally_ordered
class _Ordinal_ (TFL.Meta.Object) :

    def __eq__ (self, rhs) :
        return self.ordinal == getattr (rhs, "ordinal", rhs)
    # end def __eq__

    def __hash__ (self) :
        return hash (self.ordinal)
    # end def __hash__

    def __lt__ (self, rhs) :
        return self.ordinal < getattr (rhs, "ordinal", rhs)
    # end def __lt__

# end class _Ordinal_

class Day (_Ordinal_) :
    """Model a single day in a calendar

       >>> y = Year (2016)
       >>> d = y.weeks [4].fri
       >>> for i in range (0, 70, 7) :
       ...   print ("%2d" % i, d + i, d + i + 3)
        0 2016/01/29 2016/02/01
        7 2016/02/05 2016/02/08
       14 2016/02/12 2016/02/15
       21 2016/02/19 2016/02/22
       28 2016/02/26 2016/02/29
       35 2016/03/04 2016/03/07
       42 2016/03/11 2016/03/14
       49 2016/03/18 2016/03/21
       56 2016/03/25 2016/03/28
       63 2016/04/01 2016/04/04

       >>> for i in range (0, 70, 7) :
       ...   print ("%2d" % i, d - i, d - i + 3)
        0 2016/01/29 2016/02/01
        7 2016/01/22 2016/01/25
       14 2016/01/15 2016/01/18
       21 2016/01/08 2016/01/11
       28 2016/01/01 2016/01/04
       35 2015/12/25 2015/12/28
       42 2015/12/18 2015/12/21
       49 2015/12/11 2015/12/14
       56 2015/12/04 2015/12/07
       63 2015/11/27 2015/11/30

    """

    day_abbr   = property (lambda s : s.date.formatted ("%a"))
    day_name   = property (lambda s : s.date.formatted ("%A"))
    id         = property (lambda s : s.date.tuple [:3])
    is_weekday = property (TFL.Getter.date.is_weekday)
    month_abbr = property (lambda s : s.date.formatted ("%b"))
    month_name = property (lambda s : s.date.formatted ("%B"))
    number     = property (TFL.Getter.date.day)

    def __new__ (cls, date, cal) :
        Table = cal._days
        if isinstance (date, pyk.string_types) :
            date = CAL.Date.from_string (date)
        elif isinstance (date, pyk.int_types) :
            date = CAL.Date.from_ordinal (date)
        id = date.ordinal
        if id in Table :
            return Table [id]
        self = Table [id] = TFL.Meta.Object.__new__ (cls)
        self._cal = cal
        self._init_ (id, date)
        return self
    # end def __new__

    def _init_ (self, id, date) :
        self.date         = date
        self.appointments = []
        self._utilization = []
    # end def __init__

    def add_appointments (self, * apps) :
        self.appointments.extend (apps) ### XXX use dict_from_list
    # end def add_appointments

    def as_plan (self) :
        self.sort_appointments ()
        d = self.date
        l = CAL.Date (d.year, 12, 31)
        holi = self.is_holiday or ""
        if holi :
            holi = "%26s" % ("=%s=" % (TFL.I18N.encode_o (holi), ),)
        return "\n".join \
            ( [ "# %s      %s#%2.2d, %s, day %d/-%d %s"
              % ( self
                , d.formatted ("%a")
                , d.week
                , d.formatted ("%d-%b-%Y")
                , d.rjd
                , l.rjd - d.rjd + 1
                , holi
                )
              ]
            + (map (str, self.appointments) or [""])
            )
    # end def as_plan

    @property
    def is_holiday (self) :
        return self.Year.holidays.get (self.ordinal)
    # end def is_holiday

    def sort_appointments (self) :
        self.appointments.sort ()
    # end def sort_appointments

    @TFL.Meta.Once_Property
    def Week (self) :
        return self._cal.week [self.wk_ordinal]
    # end def Week

    @TFL.Meta.Once_Property
    def Year (self) :
        return self._cal.year [self.year]
    # end def Year

    def __add__ (self, rhs) :
        return self.__class__ (self.date + rhs, self._cal)
    # end def __add__

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        return getattr (self.date, name)
    # end def __getattr__

    def __repr__ (self) :
        return """%s ("%s")""" % \
               (self.__class__.__name__, self.date.formatted ("%Y/%m/%d"))
    # end def __repr__

    def __str__ (self) :
        return self.date.formatted ("%Y/%m/%d")
    # end def __str__

    def __sub__ (self, rhs) :
        return self + - rhs
    # end def __sub__

# end class Day

@pyk.adapt__bool__
class Week (_Ordinal_) :
    """Model a single week in a calendar

       >>> y = Year (2016)
       >>> w = y.weeks [39]
       >>> for i in range (20) :
       ...   v = w + i
       ...   print ("%2d" % i, v, v.mon, v.sun)
        0 Wk 39/2016 2016/09/26 2016/10/02
        1 Wk 40/2016 2016/10/03 2016/10/09
        2 Wk 41/2016 2016/10/10 2016/10/16
        3 Wk 42/2016 2016/10/17 2016/10/23
        4 Wk 43/2016 2016/10/24 2016/10/30
        5 Wk 44/2016 2016/10/31 2016/11/06
        6 Wk 45/2016 2016/11/07 2016/11/13
        7 Wk 46/2016 2016/11/14 2016/11/20
        8 Wk 47/2016 2016/11/21 2016/11/27
        9 Wk 48/2016 2016/11/28 2016/12/04
       10 Wk 49/2016 2016/12/05 2016/12/11
       11 Wk 50/2016 2016/12/12 2016/12/18
       12 Wk 51/2016 2016/12/19 2016/12/25
       13 Wk 52/2016 2016/12/26 2017/01/01
       14 Wk 01/2017 2017/01/02 2017/01/08
       15 Wk 02/2017 2017/01/09 2017/01/15
       16 Wk 03/2017 2017/01/16 2017/01/22
       17 Wk 04/2017 2017/01/23 2017/01/29
       18 Wk 05/2017 2017/01/30 2017/02/05
       19 Wk 06/2017 2017/02/06 2017/02/12

       >>> w = y.weeks [13]
       >>> for i in range (20) :
       ...   v = w - i
       ...   print ("%2d" % i, v, v.mon, v.sun)
        0 Wk 13/2016 2016/03/28 2016/04/03
        1 Wk 12/2016 2016/03/21 2016/03/27
        2 Wk 11/2016 2016/03/14 2016/03/20
        3 Wk 10/2016 2016/03/07 2016/03/13
        4 Wk 09/2016 2016/02/29 2016/03/06
        5 Wk 08/2016 2016/02/22 2016/02/28
        6 Wk 07/2016 2016/02/15 2016/02/21
        7 Wk 06/2016 2016/02/08 2016/02/14
        8 Wk 05/2016 2016/02/01 2016/02/07
        9 Wk 04/2016 2016/01/25 2016/01/31
       10 Wk 03/2016 2016/01/18 2016/01/24
       11 Wk 02/2016 2016/01/11 2016/01/17
       12 Wk 01/2016 2016/01/04 2016/01/10
       13 Wk 53/2015 2015/12/28 2016/01/03
       14 Wk 52/2015 2015/12/21 2015/12/27
       15 Wk 51/2015 2015/12/14 2015/12/20
       16 Wk 50/2015 2015/12/07 2015/12/13
       17 Wk 49/2015 2015/11/30 2015/12/06
       18 Wk 48/2015 2015/11/23 2015/11/29
       19 Wk 47/2015 2015/11/16 2015/11/22

    """

    tue        = property (TFL.Getter.days [1])
    wed        = property (TFL.Getter.days [2])
    thu        = property (TFL.Getter.days [3])
    fri        = property (TFL.Getter.days [4])
    sat        = property (TFL.Getter.days [5])
    sun        = property (TFL.Getter.days [6])

    cal        = property (TFL.Getter.year.cal)
    ordinal    = property (TFL.Getter.mon.wk_ordinal)

    _day_names = CAL.G8R.Week_Day_Abbrs_2.words

    def __init__ (self, year, number, mon) :
        self.year   = year
        self.number = number
        self.mon    = mon
        if number == 1 and int (year) != int (self.thu.year) :
            self.number = 53
        elif number == 53 and int (year) != int (self.thu.year) :
            self.number = 0
    # end def _init_

    @TFL.Meta.Once_Property
    def days (self) :
        d      = self.mon
        cal    = self.year.cal
        result = [d]
        result.extend (cal.day [d.date + i] for i in range (1, 7))
        return result
    # end def days

    def as_cal (self) :
        line = " ".join (("%2d" % d.day) for d in self.days)
        return "%2.2d %s" % (self.number, line)
    # end def as_cal

    def __add__ (self, rhs) :
        cal  = self.cal
        mon  = cal.day    [self.mon.date + (7 * rhs)]
        thu  = mon + 3
        year = cal.year   [thu.year]
        week = year.wmap [thu.week]
        return self.__class__ (year, week, mon)
    # end def __add__

    def __bool__ (self) :
        n = self.number
        return (   (n > 0)
               and (  (n < 53)
                   or (int (self.year) == int (self.thu.year))
                   )
               )
    # end def __bool__

    def __int__ (self) :
        return self.number
    # end def __int__

    def __str__ (self) :
        return "%s %2.2d/%4d" % (_T ("Wk"), self.number, self.year.number)
    # end def __str__

    def __repr__ (self) :
        return "%s <%s %s %s>" % (self, self.mon, _T ("to"), self.sun)
    # end def __repr__

    def __sub__ (self, rhs) :
        return self + - rhs
    # end def __sub__

# end class Week

class Month (TFL.Meta.Object) :
    """Model a single month in a calendar.

       >>> y = Year (2016)
       >>> m = y.months [5]
       >>> for i in range (20) :
       ...   print ("%2d" % i, m + i)
       ...
        0 2016/06
        1 2016/07
        2 2016/08
        3 2016/09
        4 2016/10
        5 2016/11
        6 2016/12
        7 2017/01
        8 2017/02
        9 2017/03
       10 2017/04
       11 2017/05
       12 2017/06
       13 2017/07
       14 2017/08
       15 2017/09
       16 2017/10
       17 2017/11
       18 2017/12
       19 2018/01

       >>> for i in range (20) :
       ...   print ("%2d" % i, m - i)
       ...
        0 2016/06
        1 2016/05
        2 2016/04
        3 2016/03
        4 2016/02
        5 2016/01
        6 2015/12
        7 2015/11
        8 2015/10
        9 2015/09
       10 2015/08
       11 2015/07
       12 2015/06
       13 2015/05
       14 2015/04
       15 2015/03
       16 2015/02
       17 2015/01
       18 2014/12
       19 2014/11

    """

    abbr   = property (lambda s : s.head.formatted ("%b"))
    head   = property (TFL.Getter.days [0])
    name   = property (lambda s : s.head.formatted ("%B"))
    number = property (TFL.Getter.month)
    tail   = property (TFL.Getter.days [-1])

    def __init__ (self, year, month) :
        self.year  = year
        self.month = month
    # end def __init__

    @TFL.Meta.Once_Property
    def days (self) :
        Y = self.year
        n = self.month
        d = Y.dmap [(Y.number, n, 1)]
        i = d.rjd - 1
        result = days = []
        while d.month == n :
            days.append (d)
            i += 1
            try :
                d = Y.days [i]
            except IndexError :
                break
        return result
    # end def days

    def __add__ (self, rhs) :
        yd, m = divmod (self.month + rhs, 12)
        y     = self.year + yd if yd else self.year
        if m == 0 :
            m  = 12
            y -= 1
        return self.__class__ (y, m)
    # end def __add__

    def __len__ (self) :
        return len (self.days)
    # end def __len__

    def __repr__ (self) :
        return "%s (%s, %s)" % \
            (self.__class__.__name__, self.year.number, self.month)
    # end def __repr__

    def __str__ (self) :
        return self.head.formatted ("%Y/%m")
    # end def __str__

    def __sub__ (self, rhs) :
        return self + - rhs
    # end def __sub__

# end class Month

class Quarter (TFL.Meta.Object) :
    """Model a single quarter (year) in a calendar.

       >>> y = Year (2016)
       >>> q = y.Q1
       >>> q
       Quarter (2016, 1)

       >>> q.head
       Day ("2016/04/01")

       >>> q.tail
       Day ("2016/06/30")

       >>> for i in range (-5, 6) :
       ...   print ("%2d" % i, q + i)
       ...
       -5 2014/Q4
       -4 2015/Q1
       -3 2015/Q2
       -2 2015/Q3
       -1 2015/Q4
        0 2016/Q1
        1 2016/Q2
        2 2016/Q3
        3 2016/Q4
        4 2017/Q1
        5 2017/Q2
    """

    abbr   = TFL.Meta.Once_Property (lambda s : "Q%s" % (s.quarter))
    name   = TFL.Meta.Once_Property \
        (lambda s : "%4s/%s" % (s.year.number, s.abbr))

    head   = property (TFL.Getter.days [0])
    number = property (TFL.Getter.quarter)
    tail   = property (TFL.Getter.days [-1])

    def __init__ (self, year, quarter) :
        self.year    = year
        self.quarter = quarter
    # end def __init__

    @TFL.Meta.Once_Property
    def days (self) :
        return list (itertools.chain (* tuple (m.days for m in self.months)))
    # end def days

    @TFL.Meta.Once_Property
    def months (self) :
        m = self.number * 3
        return self.year.months [m:m+3]
    # end def months

    def __add__ (self, rhs) :
        yd, q = divmod (self.quarter + rhs, 4)
        y     = self.year + yd if yd else self.year
        if q == 0 :
            q  = 4
            y -= 1
        return self.__class__ (y, q)
    # end def __add__

    def __len__ (self) :
        return len (self.days)
    # end def __len__

    def __repr__ (self) :
        return "%s (%s, %s)" % \
            (self.__class__.__name__, self.year.number, self.quarter)
    # end def __repr__

    def __str__ (self) :
        return self.name
    # end def __str__

    def __sub__ (self, rhs) :
        return self + - rhs
    # end def __sub__

# end class Quarter

class Year (TFL.Meta.Object) :
    """Model a single year in a calendar.

       >>> for d in Year (2004).weeks [0].days :
       ...   print (d, d.year == 2004)
       ...
       2003/12/29 False
       2003/12/30 False
       2003/12/31 False
       2004/01/01 True
       2004/01/02 True
       2004/01/03 True
       2004/01/04 True
       >>> for d in Year (2004).weeks [-1].days :
       ...   print (d, d.year == 2004)
       ...
       2004/12/27 True
       2004/12/28 True
       2004/12/29 True
       2004/12/30 True
       2004/12/31 True
       2005/01/01 False
       2005/01/02 False
       >>> for y in range (2003, 2006) :
       ...   Y  = Year (y)
       ...   w0, w1 = Y.weeks [0], Y.weeks [-1]
       ...   print ("%4.4d: %r %s, %r %s" % (y, w0, bool (w0), w1, bool (w1)))
       ...
       2003: Wk 01/2003 <2002/12/30 to 2003/01/05> True, Wk 53/2003 <2003/12/29 to 2004/01/04> False
       2004: Wk 01/2004 <2003/12/29 to 2004/01/04> True, Wk 53/2004 <2004/12/27 to 2005/01/02> True
       2005: Wk 00/2005 <2004/12/27 to 2005/01/02> False, Wk 52/2005 <2005/12/26 to 2006/01/01> True
    """

    number          = property (TFL.Getter.year)
    q1 = Q1         = property (TFL.Getter.quarters [0])
    q2 = Q2         = property (TFL.Getter.quarters [1])
    q3 = Q3         = property (TFL.Getter.quarters [2])
    q4 = Q4         = property (TFL.Getter.quarters [3])

    Day             = Day
    Month           = Month
    Quarter         = Quarter
    Week            = Week

    def __new__ (cls, year = None, cal = None) :
        if cal is None :
            import _CAL.Calendar
            cal = CAL.Calendar ()
        D     = CAL.Date
        Table = cal._years
        if year is None :
            year = D ().year
        if year in Table :
            return Table [year]
        self = Table [year] = TFL.Meta.Object.__new__ (cls)
        self._init_ (year, cal)
        return self
    # end def __new__

    def _init_ (self, year, cal) :
        D             = CAL.Date
        self.year     = year
        self.cal      = cal
        self.head     = h = cal.day [D (year = year, month = 1,  day = 1)]
        self.tail     = t = cal.day [D (year = year, month = 12, day = 31)]
        self.months   = [Month (self, m) for m in range (1, 13)]
        self.mmap     = {m.number : m for m in self.months}
        self.quarters = [Quarter (self, q) for q in range (1, 5)]
        self.qmap     = {q.number : q for q in self.quarters}
        self.weeks    = weeks  = []
        self.wmap     = wmap   = {}
        for w, d in self._week_creation_iter (D, cal, year, h) :
            week = Week (self, w, d)
            wmap [week.number] = week
            weeks.append (week)
            if week :
                cal.week [week.ordinal] = week
        self.holidays = CAL.holidays (year, cal.country)
    # end def _init_

    @TFL.Meta.Once_Property
    def days (self) :
        result =  [d for d in self.weeks  [0].days [self.head.weekday:]]
        for w in self.weeks [1:-1] :
            result.extend (w.days)
        result.extend (d for d in self.weeks [-1].days [:self.tail.weekday + 1])
        return result
    # end def days

    @TFL.Meta.Once_Property
    def dmap (self) :
        return {d.id : d for d in self.days}
    # end def dmap

    def as_plan (self) :
        return "\n\n".join \
            ( ["###  Plan for %s %s" % (self.year, "#" * 35)]
            + [d.as_plan () for d in self.days]
            + ["### End of plan for %s %s\n" % (self.year, "#" * 35)]
            )
    # end def as_plan

    def as_cal (self) :
        result = [   "%s %s" % (w.as_cal (), w.sun.formatted ("%b"))
                 for w in self.weeks
                 ] + [""]
        return "\n".join (result)
    # end def as_cal

    def sort_appointments (self) :
        for d in self.days :
            d.sort_appointments ()
    # end def sort_appointments

    def _week_creation_iter (self, D, cal, year, h) :
        if h.weekday == 0 :
            d = h
        else :
            d = cal.day [h.date - h.weekday]
        yield h.week, d
        d = cal.day [d.date + 7]
        while d.year == year :
            yield d.week, d
            d = cal.day [d.date + 7]
    # end def _week_creation_iter

    def __add__ (self, rhs) :
        return self.__class__ (self.year + rhs, cal = self.cal)
    # end def __add__

    def __int__ (self) :
        return self.year
    # end def __int__

    def __len__ (self) :
        return len (self.days)
    # end def __len__

    def __repr__ (self) :
        return "%s (%s)" % (self.__class__.__name__, self.year)
    # end def __repr__

    def __str__ (self) :
        return "%s" % (self.year, )
    # end def __str__

    def __sub__ (self, rhs) :
        return self + - rhs
    # end def __sub__

# end class Year

@TFL._Add_Import_Callback ("_TFL.json_dump")
def _import_cb_json_dump (module) :
    @module.default.add_type (_Ordinal_, Year)
    def json_encode_ordinal_or_year (o) :
        return pyk.text_type (o)
# end def _import_cb_json_dump

def create_diary (Y, path) :
    for m in Y.months :
        mp = sos.path.join (path, "%2.2d" % (m.number, ))
        if not sos.path.isdir (mp) :
            sos.mkdir (mp)
            for d in m.days :
                f = sos.path.join (mp, "%2.2d.%s" % (d.day, "diary"))
                if not sos.path.isfile (f) :
                    open (f, "w").close ()
# end def create_diary

def write_year (Yf, file_name, force = 0) :
    if sos.path.isfile (file_name) and not force:
        print ("%s already exists, not overwritten" %(file_name, ))
    else :
        f = open (file_name, "w")
        f.write  (Yf ())
        f.close  ()
# end def write_year

def _main (cmd) :
    year = cmd.year
    path = sos.path.join (sos.expanded_path (cmd.path), "%4.4d" % year)
    Y    = Year (year)
    pfil = sos.path.join (path, cmd.Plan)
    vfil = sos.path.join (path, cmd.View)
    if cmd.create or cmd.diary :
        if not sos.path.isdir (path) :
            sos.mkdir (path)
        if cmd.diary :
            create_diary (Y, path)
        if cmd.create :
            if cmd.Plan :
                write_year (Y.as_plan, pfil, cmd.force)
            if cmd.View :
                write_year (Y.as_cal,  vfil, cmd.force)
# end def _main

_Command = TFL.CAO.Cmd \
    ( handler     = _main
    , opts        =
        ( "create:B?Write files"
        , "diary:B?Create a diary file per day"
        , "force:B?Overwrite existing files if any"
        , "path:S=~/diary?Path for calendar files"
        , "Plan:S=plan?Filename of plan for `year`"
        , "View:S=view?Filename of view for `year`"
        , "year:I=%d?Year for which to process calendar" % (CAL.Date ().year, )
        )
    , max_args    = 0
    )

if __name__ != "__main__" :
    CAL._Export ("Year")
else :
    _Command ()
### __END__ CAL.Year
