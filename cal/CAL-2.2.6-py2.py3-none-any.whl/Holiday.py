# -*- coding: utf-8 -*-
# Copyright (C) 2003-2016 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    CAL.Holiday
#
# Purpose
#    Provide information about fixed and moving Austrian holidays
#
# Revision Dates
#    20-Apr-2003 (CT) Creation
#     6-Feb-2004 (CT) Use (y, m, d) tuples instead of strings as dictionary
#                     keys
#     9-Feb-2004 (CT) Dependency on `Y.map` removed
#     5-Jun-2004 (CT) `easter_date` implementation using Spencer Jones'
#                     algorithm added
#    10-Oct-2004 (MG) Use new `CAL.Date_Time` module instead of `Date_Time`
#    15-Oct-2004 (CT) Use `CAL.Date` instead of `CAL.Date_Time`
#    15-Oct-2004 (CT) `_main` and `_command_spec` added
#    17-Oct-2004 (CT) Use `Date_Delta` instead of `Delta`
#    31-Oct-2004 (CT) `_main` changed to display date, too
#     5-Nov-2004 (CT) Use `//` for int division
#    16-Jun-2010 (CT) Use unicode for holiday names
#    16-Jun-2013 (CT) Use `TFL.CAO`, not `TFL.Command_Line`
#    29-Jan-2016 (CT) Modernize, DRY
#     1-Feb-2016 (CT) Add country dependent holidays; remove obsolete code
#     2-Feb-2016 (CT) Factor `CAL.Day_Rule`
#     2-Feb-2016 (CT) Add I18N, german and swiss holidays
#    11-Feb-2016 (CT) Factor `TFL.I18N.test_language`
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _CAL                    import CAL
from   _TFL                    import TFL
from   _TFL.pyk                import pyk

from   _TFL.I18N                import _, _T, _Tn

import _CAL.Date
import _CAL.Day_Rule
import _CAL.Delta

import _TFL.CAO
import _TFL._Meta.Object
import _TFL._Meta.Once_Property

class Holidays (CAL.Day_Rule.Set) :

    F = CAL.Day_Rule.Fixed
    E = CAL.Day_Rule.Easter_Dependent

    ### https://en.wikipedia.org/wiki/List_of_holidays_by_country
    _rules = \
        ( F (_ ("New Year's Day"),                      1,  1)
        , F (_ ("Epiphany"),                            1,  6, "AT")
        , F (_ ("Martin Luther King Day")
             , 1, 1, "US", delta = dict (weekday = F.RD.MO (3))
            )
        , F (_ ("Inauguration Day")
            , 1, 20, "US", y_filter = lambda y : (y % 4 == 1)
            )
        , F (_ ("Washington's Birthday")
            , 2, 1, "US", delta = dict (weekday = F.RD.MO (3))
            )
        , F (_ ("Saint Patrick's Day"),                 3, 17, "IE")
        , F (_ ("Labor Day"),                           5,  1, "AT", "DE")
        , F (_ ("May Day Bank Holiday")
            , 5,  1, "UK", delta = dict (weekday = F.RD.MO (1))
            )
        , F (_ ("May Day")
            , 5,  1, "IE"
            , delta = dict (weekday = F.RD.MO (1))
            , y_filter = lambda y : y >= 1994
            )
        , F (_ ("Spring Bank Holiday")
            , 5,  31, "UK", delta = dict (weekday = F.RD.MO (-1))
            )
        , F (_ ("Memorial Day")
            , 5,  31, "US", delta = dict (weekday = F.RD.MO (-1))
            )
        , F (_ ("June Holiday")
            , 6,  1, "IE", delta = dict (weekday = F.RD.MO (1))
            )
        , F (_ ("Independence Day"),                    7,  4, "US")
        , F (_ ("Swiss National Day"),                  8,  1, "CH")
        , F (_ ("August Holiday")
            , 8,  1, "IE", delta = dict (weekday = F.RD.MO (1))
            )
        , F (_ ("Assumption Day"),                      8, 15, "AT")
        , F (_ ("Late Summer Bank Holiday")
            , 8,  31, "UK", delta = dict (weekday = F.RD.MO (-1))
            )
        , F (_ ("Labor Day")
            , 9,  1, "US", delta = dict (weekday = F.RD.MO (1))
            )
        , F (_ ("Federal Day of Thanksgiving, Repentance and Prayer")
            , 9, 1, "CH", delta = dict (weekday = F.RD.SU (3))
            )
        , F (_ ("German Unity Day"),                   10,  3, "DE"
            , y_filter = lambda y : y >= 1990
            )
        , F (_ ("Columbus Day")
            , 10,  1, "US", delta = dict (weekday = F.RD.MO (2))
            )
        , F (_ ("Austrian National Day"),              10, 26, "AT")
        , F (_ ("October Holiday")
            , 10,  31, "IE", delta = dict (weekday = F.RD.MO (-1))
            )
        , F (_ ("All Saints' Day"),                    11,  1, "AT")
        , F (_ ("Veterans Day"),                       11, 11, "US")
        , F (_ ("Thanksgiving")
            , 11,  1, "US", delta = dict (weekday = F.RD.TH (4))
            )
        , F (_ ("Feast of the Immaculate Conception"), 12,  8, "AT")
        , F (_ ("Christmas Day"),                      12, 25, "AT", "CH", "DE", "IE", "UK", "US")
        , F (_ ("St. Stephen's Day"),                  12, 26, "AT", "CH", "DE", "IE")
        , F (_ ("Boxing Day"),                         12, 26, "UK")
        # easter dependent movable holidays
        , E (_ ("Good Friday"),     -2, "CH", "DE", "UK")
        , E (_ ("Easter Sunday"),    0, "AT", "CH", "DE", "UK")
        , E (_ ("Easter Monday"),    1, "AT", "CH", "DE", "IE", "UK")
        , E (_ ("Ascension Day"),   39, "AT", "CH", "DE")
        , E (_ ("Whit Sunday"),     49, "AT", "CH", "DE")
        , E (_ ("Whit Monday"),     50, "AT", "CH", "DE")
        , E (_ ("Corpus Christi"),  60, "AT")
        )

# end class Holidays

holidays = Holidays ()

def _show (year, country, lang = "de") :
    """
    >>> _show (2016, "AT")
      1 2016/01/01 Neujahr
      6 2016/01/06 Hl. Drei Könige
     87 2016/03/27 Ostersonntag
     88 2016/03/28 Ostermontag
    122 2016/05/01 Tag der Arbeit
    126 2016/05/05 Christi Himmelfahrt
    136 2016/05/15 Pfingstsonntag
    137 2016/05/16 Pfingstmontag
    147 2016/05/26 Fronleichnam
    228 2016/08/15 Mariä Himmelfahrt
    300 2016/10/26 Nationalfeiertag
    306 2016/11/01 Allerheiligen
    343 2016/12/08 Mariä Empfängnis
    360 2016/12/25 1. Weihnachtstag
    361 2016/12/26 2. Weihnachtstag

    >>> _show (2016, "DE")
      1 2016/01/01 Neujahr
     85 2016/03/25 Karfreitag
     87 2016/03/27 Ostersonntag
     88 2016/03/28 Ostermontag
    122 2016/05/01 Tag der Arbeit
    126 2016/05/05 Christi Himmelfahrt
    136 2016/05/15 Pfingstsonntag
    137 2016/05/16 Pfingstmontag
    277 2016/10/03 Tag der Deutschen Einheit
    360 2016/12/25 1. Weihnachtstag
    361 2016/12/26 2. Weihnachtstag

    >>> _show (2016, "CH", lang = "en")
      1 2016/01/01 New Year's Day
     85 2016/03/25 Good Friday
     87 2016/03/27 Easter Sunday
     88 2016/03/28 Easter Monday
    126 2016/05/05 Ascension Day
    136 2016/05/15 Whit Sunday
    137 2016/05/16 Whit Monday
    214 2016/08/01 Swiss National Day
    262 2016/09/18 Federal Day of Thanksgiving, Repentance and Prayer
    360 2016/12/25 Christmas Day
    361 2016/12/26 St. Stephen's Day

    >>> _show (2016, "IE")
      1 2016/01/01 Neujahr
     77 2016/03/17 Saint Patrick's Day
     88 2016/03/28 Ostermontag
    123 2016/05/02 Mai-Feiertag
    158 2016/06/06 Juni-Feiertag
    214 2016/08/01 August-Feiertag
    305 2016/10/31 Oktober-Feiertag
    360 2016/12/25 1. Weihnachtstag
    361 2016/12/26 2. Weihnachtstag

    >>> _show (2016, "UK")
      1 2016/01/01 Neujahr
     85 2016/03/25 Karfreitag
     87 2016/03/27 Ostersonntag
     88 2016/03/28 Ostermontag
    123 2016/05/02 Bankfeiertag
    151 2016/05/30 Bankfeiertag
    242 2016/08/29 Bankfeiertag
    360 2016/12/25 1. Weihnachtstag
    361 2016/12/26 2. Weihnachtstag

    >>> _show (2017, "UK", lang = "en")
      1 2017/01/01 New Year's Day
    104 2017/04/14 Good Friday
    106 2017/04/16 Easter Sunday
    107 2017/04/17 Easter Monday
    121 2017/05/01 May Day Bank Holiday
    149 2017/05/29 Spring Bank Holiday
    240 2017/08/28 Late Summer Bank Holiday
    359 2017/12/25 Christmas Day
    360 2017/12/26 Boxing Day

    >>> _show (2016, "US", lang = "en")
      1 2016/01/01 New Year's Day
     18 2016/01/18 Martin Luther King Day
     46 2016/02/15 Washington's Birthday
    151 2016/05/30 Memorial Day
    186 2016/07/04 Independence Day
    249 2016/09/05 Labor Day
    284 2016/10/10 Columbus Day
    316 2016/11/11 Veterans Day
    329 2016/11/24 Thanksgiving
    360 2016/12/25 Christmas Day

    >>> _show (2017, "US", lang = "en")
      1 2017/01/01 New Year's Day
     16 2017/01/16 Martin Luther King Day
     20 2017/01/20 Inauguration Day
     51 2017/02/20 Washington's Birthday
    149 2017/05/29 Memorial Day
    185 2017/07/04 Independence Day
    247 2017/09/04 Labor Day
    282 2017/10/09 Columbus Day
    315 2017/11/11 Veterans Day
    327 2017/11/23 Thanksgiving
    359 2017/12/25 Christmas Day

    >>> _show (2016, "ANY")
      1 2016/01/01 Neujahr

    """
    import _CAL.Year
    with TFL.I18N.test_language (lang) :
        Y = CAL.Year (year)
        O = Y.head.ordinal - 1
        for ordinal, name in sorted (pyk.iteritems (holidays (year, country))) :
            print ("%3d %s %s" % (ordinal - O, Y.cal.day [ordinal], _T (name)))
# end def _show

def _main (cmd) :
    _show (cmd.year, cmd.country, cmd.language)
# end def _main

today    = CAL.Date ()
year     = today.year
_Command = TFL.CAO.Cmd \
    ( handler       = _main
    , args          =
        ( "year:I=%d?Year for which to show holidays" % (year, )
        ,
        )
    , opts          =
        ( "-country:S=AT?Country for which to show holidays"
        , "-language:S=de?Language to use for holiday names"
        )
    , max_args      = 1
    )

if __name__ != "__main__" :
    CAL._Export ("*")
else :
    _Command ()
### __END__ CAL.Holiday
