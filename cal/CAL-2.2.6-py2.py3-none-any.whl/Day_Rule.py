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
#    CAL.Day_Rule
#
# Purpose
#    Provide classes to define rules specifying days
#
# Revision Dates
#     2-Feb-2016 (CT) Creation (partly factored from CAL.Holiday)
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _CAL                    import CAL
from   _TFL                    import TFL
from   _TFL.pyk                import pyk

import _CAL.Date
import _CAL.Delta
import _CAL.Relative_Delta

import _TFL.CAO
import _TFL._Meta.Object
import _TFL._Meta.Once_Property

import itertools

def easter_date (y) :
    """Returns date of easter sunday computed by Spencer Jones algorithm as
       given by Jean Meeus: Astronomical Algorithms.

       >>> easter_date (1818)
       (1818, 3, 22)
       >>> easter_date (1943)
       (1943, 4, 25)
       >>> easter_date (1981)
       (1981, 4, 19)
       >>> easter_date (2008)
       (2008, 3, 23)
       >>> easter_date (2011)
       (2011, 4, 24)
       >>> easter_date (2038)
       (2038, 4, 25)
    """
    a    = y % 19
    b, c = divmod (y, 100)
    d, e = divmod (b, 4)
    f    = (b + 8) // 25
    g    = (b - f + 1) // 3
    h    = (19*a + b - d - g + 15) % 30
    i, k = divmod (c, 4)
    l    = (32 + 2*e + 2*i - h - k) % 7
    m    = (a + 11*h + 22*l) // 451
    n, p = divmod (h + l - 7*m + 114, 31)
    return (y, n, p+1)
# end def easter_date

class _Rule_ (TFL.Meta.Object) :
    """Base class for rules."""

    RD                 = CAL.Relative_Delta
    _delta             = None
    _delta_2           = None
    _y_filter          = None

    def __init__ (self, name, countries, ** kw) :
        self.name      = name
        self.countries = set (countries)
        self.all       = not countries
        self.pop_to_self (kw, "delta", "delta_2", "y_filter", prefix = "_")
        self.__dict__.update (kw)
    # end def __init__

    def __call__ (self, year, country) :
        if self.matches (country) :
            return self.date (year)
    # end def __call__

    @TFL.Meta.Once_Property
    def delta (self) :
        result = self._delta
        if isinstance (result, dict) :
            result = self.RD (** result)
        return result
    # end def delta

    @TFL.Meta.Once_Property
    def delta_2 (self) :
        result = self._delta_2
        if isinstance (result, dict) :
            result = self.RD (** result)
        return result
    # end def delta_2

    @TFL.Meta.Once_Property
    def y_filter (self) :
        result = self._y_filter
        if result is None :
            result = lambda y : True
        return result
    # end def y_filter

    def date (self, year) :
        if self.y_filter (year) :
            delta    = self.delta
            delta_2  = self.delta_2
            result   = self._date (year)
            if delta is not None :
                result += delta
            if delta_2 is not None :
                result += delta_2
            return result
    # end def date

    def matches (self, country) :
        return self.all or country in self.countries
    # end def matches

# end class _Rule_

class Fixed (_Rule_) :
    """Day fixed to a specific date.

       >>> n1 = Fixed ("November 1st", 11, 1)
       >>> print (n1.date (1980))
       1980-11-01
       >>> print (n1.date (2016))
       2016-11-01

       >>> RD = Fixed.RD
       >>> et = Fixed ("Election day", 11, 1, delta = dict (weekday = RD.MO), delta_2 = 1)
       >>> print (et.date (1980))
       1980-11-04
       >>> print (et.date (2016))
       2016-11-08

    """

    def __init__ (self, name, month, day, * countries, ** kw) :
        self.__super.__init__ (name, countries, month = month, day = day, ** kw)
    # end def __init__

    def _date (self, year) :
        return CAL.Date (year, self.month, self.day)
    # end def _date

# end class Fixed

class Easter_Dependent (_Rule_) :
    """Day relative to easter date.

       >>> ED = Easter_Dependent
       >>> aw = ED ("Ash Wednesday", -46)
       >>> print (aw.date (2016))
       2016-02-10
       >>> print (aw.date (2017))
       2017-03-01

       The following test cases demonstrate the use of `delta_2` but these
       would actually be better specified by modifying `delta` by the static
       offset to ash wednesday:
       >>> RD = ED.RD
       >>> cm = ED ("Carnival", -46, delta_2 = dict (weekday = RD.MO (-2)))
       >>> print (cm.date (2016))
       2016-02-01
       >>> print (cm.date (2017))
       2017-02-20
       >>> cf = ED ("Carnival", -46, delta_2 = dict (weekday = RD.FR))
       >>> print (cf.date (2016))
       2016-02-12
       >>> print (cf.date (2017))
       2017-03-03

    """

    def __init__ (self, name, delta, * countries, ** kw) :
        self.__super.__init__ (name, countries, delta = delta, ** kw)
    # end def __init__

    def _date (self, year) :
        return CAL.Date (* easter_date (year))
    # end def _date

# end class Easter_Dependent

class Set (TFL.Meta.Object) :
    """Model a country specific set of rules for specific days."""

    _rules = []

    def __init__ (self, * rules) :
        self.years            = {}
        self.rules_by_country = {}
        self.dates            = {}
        if rules :
            self._rules = rules
    # end def __init__

    def __call__ (self, year, country) :
        years = self.years
        try :
            result = years [year, country]
        except KeyError :
            result = years [year, country] = self._calc (year, country)
        return result
    # end def __call__

    @TFL.Meta.Once_Property
    def countries (self) :
        return set (c for r in self._rules for c in r.countries)
    # end def countries

    def _rules_by_country (self, country) :
        map = self.rules_by_country
        try :
            result = map [country]
        except KeyError :
            result = map [country] = \
                [d for d in self._rules if d.matches (country)]
        return result
    # end def _rules_by_country

    def _calc (self, year, country) :
        dates  = self.dates
        result = {}
        for r in self._rules_by_country (country) :
            try :
                k, v = dates [year, r]
            except KeyError :
                date = r.date (year)
                if date is not None :
                    k, v = dates [year, r] = date.ordinal, r.name
            result [k] = v
        return result
    # end def _calc

# end class Set

if __name__ != "__main__" :
    CAL._Export_Module ()
### __END__ CAL.Day_Rule
