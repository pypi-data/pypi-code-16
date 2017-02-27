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
#    Calendar
#
# Purpose
#    Model a calendar used by a single person/group/project
#
# Revision Dates
#    10-Nov-2004 (CT) Creation
#    14-Nov-2004 (CT) `_new_week` added
#    15-Nov-2004 (CT) More doctests added
#    10-Dec-2004 (CT) Small fixes
#    11-Aug-2007 (CT) Imports corrected
#     7-Nov-2007 (CT) Use `Getter` instead of `lambda`
#    29-Jan-2016 (CT) Remove `populate` from call to `CAL.Year`
#     1-Feb-2016 (CT) Add `country`
#    19-Apr-2016 (CT) Use `CAL.Year.Day`, not `CAL.Day`
#    20-Jun-2016 (CT) Add cache for `Calendar` instances
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _CAL              import CAL
from   _TFL              import TFL

import _CAL.Date
import _CAL.Year

import _TFL._Meta.Object
import _TFL.Accessor

from   _TFL.pyk          import pyk
from   _TFL.predicate    import *
from   _TFL              import sos

class _Cal_Dict_ (dict) :

    def __init__ (self, cal, creator) :
        dict.__init__ (self)
        self.cal     = cal
        self.creator = creator
    # end def __init__

    def __getitem__ (self, key) :
        try :
            return dict.__getitem__ (self, key)
        except KeyError :
            try :
                result = self [key] = self.creator (key)
            except KeyboardInterrupt :
                raise
            except Exception as exc :
                print ("_Cal_Dict_", self.creator, exc)
                raise KeyError (key)
            else :
                return result
    # end def __getitem__

# end class _Cal_Dict_

class Calendar (TFL.Meta.Object) :
    """Model a calendar used by a single person/group/project

       >>> from _CAL.Date  import *
       >>> d = Date (2004, 11, 15)
       >>> C = Calendar ()
       >>> len (C.week)
       0
       >>> y = C.year [2004]
       >>> y
       Year (2004)
       >>> y is C.year [2004]
       True
       >>> C.week [d.wk_ordinal] is y.weeks [d.week - 1]
       True
       >>> C.week [d.wk_ordinal]
       Wk 47/2004 <2004/11/15 to 2004/11/21>
       >>> len (C.week)
       53
    """

    day             = property (TFL.Getter._days)
    week            = property (TFL.Getter._weeks)
    year            = property (TFL.Getter._years)

    default_country = "AT"

    _Table          = {}
    _undefined      = object ()

    def __new__ (cls, name = None, country = _undefined) :
        if country is cls._undefined :
            country = cls.default_country
        key   = (name, country)
        Table = cls._Table
        try :
            self    = Table [key]
        except KeyError :
            self    = Table [key] = cls.__c_super.__new__ (cls, name, country)
            self._init_ (name, country)
        return self
    # end def __new__

    def _init_ (self, name, country) :
        self.name    = name
        self.country = country
        self._days   = _Cal_Dict_ (self, self._new_day)
        self._weeks  = _Cal_Dict_ (self, self._new_week)
        self._years  = _Cal_Dict_ (self, self._new_year)
    # end def _init_

    def _new_day (self, date) :
        return CAL.Year.Day (date, self)
    # end def _new_day

    def _new_week (self, wko) :
        d = self.day  [wko * 7]
        y = self.year [d.year]
        if wko not in self._weeks :
            if d.month == 1 :
                y = self.year [d.year - 1]
            elif d.month == 12 :
                y = self.year [d.year + 1]
        if wko in self._weeks :
            return self._weeks [wko]
        else :
            print \
                ( "%s._new_week is stymied: %s"
                % (self.__class__.__name__, wko)
                )
    # end def _new_week

    def _new_year (self, year) :
        return CAL.Year (year, cal = self)
    # end def _new_year

# end class Calendar

if __name__ != "__main__" :
    CAL._Export ("*")
### __END__ Calendar
