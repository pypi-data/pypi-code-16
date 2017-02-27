# -*- coding: utf-8 -*-
# Copyright (C) 2007-2014 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    CAL.Ordinal
#
# Purpose
#    Support the use of ordinal numbers for weeks, months etc.
#
# Revision Dates
#     3-Jan-2007 (CT) Creation
#    11-Aug-2007 (CT) `Quarter` and doc-test added
#    11-Jul-2014 (CT) Add `is_first` and `to_year`
#    13-Jul-2014 (CT) Fix `Week.to_date`, `Week.is_first`
#    ««revision-date»»···
#--

from   __future__                 import print_function

"""
>>> from _CAL.Date import *
>>> d1 = Date (1958,  1, 30)
>>> d2 = Date (1960,  4, 11)
>>> d3 = Date (1959,  9, 26)
>>> d4 = Date (1997, 11, 16)
>>> d5 = Date (2007,  1, 25) ### week  4
>>> d6 = Date (2007,  4, 25) ### week 17
>>> d7 = Date (2007,  7,  4) ### week 27
>>> d8 = Date (2007, 12, 24) ### week 52
>>> for U in Month, Quarter, Week, Year :
...     print (U.__name__)
...     for d in (d1, d2, d3, d4, d5, d6, d7, d8) :
...         o = U.to_ordinal (d)
...         print ("    %s %8d %s" % (d, o, U.to_date (o)))
...
Month
    1958-01-30    23497 1958-01-01
    1960-04-11    23524 1960-04-01
    1959-09-26    23517 1959-09-01
    1997-11-16    23975 1997-11-01
    2007-01-25    24085 2007-01-01
    2007-04-25    24088 2007-04-01
    2007-07-04    24091 2007-07-01
    2007-12-24    24096 2008-12-01
Quarter
    1958-01-30     7833 1958-01-01
    1960-04-11     7842 1960-04-01
    1959-09-26     7839 1959-07-01
    1997-11-16     7992 1998-10-01
    2007-01-25     8029 2007-01-01
    2007-04-25     8030 2007-04-01
    2007-07-04     8031 2007-07-01
    2007-12-24     8032 2008-10-01
Week
    1958-01-30   102115 1958-01-30
    1960-04-11   102230 1960-04-14
    1959-09-26   102201 1959-09-24
    1997-11-16   104191 1997-11-13
    2007-01-25   104671 2007-01-25
    2007-04-25   104684 2007-04-26
    2007-07-04   104694 2007-07-05
    2007-12-24   104719 2007-12-27
Year
    1958-01-30     1958 1958-01-01
    1960-04-11     1960 1960-01-01
    1959-09-26     1959 1959-01-01
    1997-11-16     1997 1997-01-01
    2007-01-25     2007 2007-01-01
    2007-04-25     2007 2007-01-01
    2007-07-04     2007 2007-01-01
    2007-12-24     2007 2007-01-01
"""

from   _TFL                    import TFL
from   _CAL                    import CAL
import _CAL.Date
import _TFL._Meta.Object

class Month (TFL.Meta.Object) :
    """Ordinal numbers for months."""

    @classmethod
    def is_first (cls, mo) :
        y, m = divmod (mo, 12)
        return m == 1
    # end def is_first

    @classmethod
    def to_date (cls, mo) :
        """Return date corresponding to month ordinal `mo`."""
        y, m = divmod (mo, 12)
        return CAL.Date (y, m or 12, 1)
    # end def to_date

    @classmethod
    def to_ordinal (cls, d) :
        """Return month ordinal for date `d`."""
        return d.year * 12 + d.month
    # end def to_ordinal

    @classmethod
    def to_year (cls, mo) :
        """Return year corresponding to month ordinal `mo`."""
        y, m = divmod (mo, 12)
        return y
    # end def to_year

# end class Month

class Quarter (TFL.Meta.Object) :
    """Ordinal numbers for quarters"""

    @classmethod
    def is_first (cls, qo) :
        y, q = divmod (qo, 4)
        return q == 1
    # end def is_first

    @classmethod
    def to_date (cls, qo) :
        """Return date corresponding to quarter ordinal `qo`."""
        y, q = divmod (qo, 4)
        return CAL.Date (y, ((q or 4) - 1) * 3 + 1, 1)
    # end def to_date

    @classmethod
    def to_ordinal (cls, d) :
        """Return quarter ordinal for date `d`."""
        return d.year * 4 + d.quarter
    # end def to_ordinal

    @classmethod
    def to_year (cls, qo) :
        """Return year corresponding to quarter ordinal `qo`."""
        y, q = divmod (qo, 4)
        return y
    # end def to_year

# end class Quarter

class Week (TFL.Meta.Object) :
    """Ordinal numbers for weeks"""

    tick_delta = 1

    @classmethod
    def is_first (cls, wo) :
        d = cls.to_date (wo)
        return 1 <= d.week <= cls.tick_delta
    # end def is_first

    @classmethod
    def to_date (cls, wo) :
        """Return date corresponding to week ordinal `wo`."""
        return CAL.Date.from_ordinal (wo * 7 + 4)
    # end def to_date

    @classmethod
    def to_ordinal (cls, d) :
        """Return week ordinal for date `d`."""
        return d.wk_ordinal
    # end def to_ordinal

    @classmethod
    def to_year (cls, wo) :
        """Return year corresponding to week ordinal `wo`."""
        d = cls.to_date (wo)
        return d.year
    # end def to_year

# end class Week

class Year (TFL.Meta.Object) :
    """Ordinal numbers for years."""

    @classmethod
    def is_first (cls, yo) :
        return False
    # end def is_first

    @classmethod
    def to_date (cls, yo) :
        """Return date corresponding to year ordinal `yo`."""
        return CAL.Date (yo, 1, 1)
    # end def to_date

    @classmethod
    def to_ordinal (cls, d) :
        """Return year ordinal for date `d`."""
        return d.year
    # end def to_ordinal

    @classmethod
    def to_year (cls, yo) :
        """Return date corresponding to year ordinal `yo`."""
        return yo
    # end def to_year

# end class Year

if __name__ == "__main__" :
    CAL._Export_Module ()
### __END__ CAL.Ordinal
