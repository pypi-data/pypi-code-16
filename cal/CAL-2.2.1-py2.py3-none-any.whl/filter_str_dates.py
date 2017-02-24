# -*- coding: utf-8 -*-
# Copyright (C) 2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    CAL.filter_str_dates
#
# Purpose
#    Filter dates in string representation by given criteria
#
# Revision Dates
#    28-Mar-2016 (CT) Creation
#    ««revision-date»»···
#--

r"""
    This module provides functions for filtering a set of dates in string
    representation according to `month`, `quarter`, `year`, or `weekdays`.

    >>> dates = \
    ...   [ '20131202', '20131209', '20131216', '20131223', '20131230'
    ...   , '20140106', '20140113', '20140120', '20140127', '20140203'
    ...   , '20140210', '20140217', '20140224', '20140303', '20140310'
    ...   , '20140317', '20140324', '20140331', '20140407', '20140414'
    ...   , '20140421', '20140428', '20140505', '20140512', '20140519'
    ...   , '20140526', '20140602', '20140609', '20140616', '20140623'
    ...   , '20140630', '20140707', '20140714', '20140721', '20140728'
    ...   , '20140804', '20140811', '20140818', '20140825', '20140901'
    ...   , '20140908', '20140915', '20140922', '20140929', '20141006'
    ...   , '20141013', '20141020', '20141027', '20141103', '20141110'
    ...   , '20141117', '20141124', '20141201', '20141208', '20141215'
    ...   , '20141222', '20141229', '20150105', '20150112', '20150119'
    ...   , '20150126'
    ...   ]
    >>> dates_w = \
    ...   [ '20160329', '20160330', '20160331', '20160401', '20160402'
    ...   , '20160403', '20160404', '20160405', '20160406', '20160407'
    ...   , '20160408', '20160409', '20160410', '20160411', '20160412'
    ...   , '20160413', '20160414', '20160415', '20160416', '20160417'
    ...   , '20160418', '20160419', '20160420', '20160421', '20160422'
    ...   , '20160423', '20160424', '20160425', '20160426', '20160427'
    ...   , '20160428', '20160429', '20160430', '20160501'
    ...   ]


    >>> after =  Date (2013, 12, 1)
    >>> before = Date (2017,  2, 1)

    >>> dates_wc  = list (week_changes (after, before, dates_w))
    >>> dates_wc2 = list (week_changes (after, before, dates_wc))
    >>> print (" ".join (dates_wc))
    20160329 20160404 20160411 20160418 20160425 20160501
    >>> dates_wc2 == dates_wc
    True

    >>> dates_mc  = list (month_changes (after, before, dates))
    >>> dates_mc2 = list (month_changes (after, before, dates_mc))
    >>> print (" ".join (dates_mc))
    20131202 20131230 20140203 20140303 20140331 20140428 20140602 20140630 20140804 20140901 20140929 20141103 20141201 20141229 20150126
    >>> dates_mc2 == dates_mc
    True

    >>> dates_qc  = list (quarter_changes (after, before, dates))
    >>> dates_qc2 = list (quarter_changes (after, before, dates_qc))
    >>> print (" ".join (dates_qc))
    20131230 20140331 20140630 20140929 20141229
    >>> dates_qc2 == dates_qc
    True

    >>> dates_yc  = list (year_changes (after, before, dates))
    >>> dates_yc2 = list (year_changes (after, before, dates_yc))
    >>> print (" ".join (dates_yc))
    20131230 20141229
    >>> dates_yc2 == dates_yc
    True

    >>> print (":", " ".join (week_changes (after, before, dates_w, 1)), ":")
    : 20160329 20160405 20160412 20160419 20160426 20160501 :

    >>> print (":", " ".join (week_changes (after, before, dates_w, 2)), ":")
    : 20160330 20160406 20160413 20160420 20160427 20160501 :

    >>> print (":", " ".join (week_changes (after, before, dates_w, 3)), ":")
    : 20160331 20160407 20160414 20160421 20160428 :

    >>> print (":", " ".join (week_changes (after, before, dates_w, 4)), ":")
    : 20160401 20160408 20160415 20160422 20160429 :

    >>> print (":", " ".join (week_changes (after, before, dates_w, 5)), ":")
    : 20160402 20160409 20160416 20160423 20160430 :

    >>> print (":", " ".join (week_changes (after, before, dates_w, 6)), ":")
    : 20160403 20160410 20160417 20160424 20160501 :

    >>> print (":", " ".join (month_changes (after, before, dates_w)), ":")
    : 20160401 20160501 :

    >>> print (":", " ".join (month_changes (after, before, dates_w, 10)), ":")
    : 20160411 :

    >>> print (":", " ".join (quarter_changes (after, before, dates_w)), ":")
    : 20160401 :

    >>> print (":", " ".join (year_changes (after, before, dates_w)), ":")
    : :

"""

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _CAL                     import CAL
from   _TFL                     import TFL

from   _CAL.Date                import Date
from   _TFL.Math_Func           import sign
from   _TFL.multimap            import mm_list
from   _TFL.Q_Exp               import Q
from   _TFL.predicate           import pairwise
from   _TFL.pyk                 import pyk

import _TFL.CAO

in_range = Date.str_dates_in_range

def by_range (after, before, str_dates) :
    """Yield all elements of `str_dates` in range `(before, after)`"""
    return (sd for (d, sd) in in_range (after, before, str_dates))
# end def by_range

def month_changes (after, before, str_dates, offset = 0, limit = 8) :
    """Yield all elements of `str_dates` closest to month changes."""
    return unit_changes (after, before, str_dates, "month", offset, limit)
# end def month_changes

def quarter_changes (after, before, str_dates, offset = 0, limit = 15) :
    """Yield all elements of `str_dates` closest to quarter changes."""
    return unit_changes (after, before, str_dates, "quarter", offset, limit)
# end def quarter_changes

def unit_changes (after, before, str_dates, unit, offset = 0, limit = 5) :
    """Yield all elements of `str_dates` closest to `unit` changes."""
    map = mm_list ()
    for d, sd in in_range (after, before, str_dates) :
        p1, p2  = d.periods [unit]
        if offset :
            p1 += offset
            p2 += offset
        p       = p1 if (d - p1 < (p2 - p1) // 2) else (p2 + 1)
        delta   = (d - p).days
        a_delta = abs (delta)
        if a_delta <= limit :
            map [p].append ((a_delta, - sign (delta), sd))
    result = list (min (v) [-1] for v in pyk.itervalues (map))
    return sorted (result)
# end def unit_changes

def week_changes (after, before, str_dates, offset = 0, limit = 3) :
    """Yield all elements of `str_dates` closest to week changes."""
    return unit_changes (after, before, str_dates, "week", offset, limit)
# end def week_changes

def weekdays (after, before, week_days, str_dates) :
    """Yield all elements of `str_dates` which match `week_days`"""
    wdays = set (week_days)
    for d, sd in in_range (after, before, str_dates) :
        if d.weekday in wdays :
            yield sd
# end def weekdays

def year_changes (after, before, str_dates, offset = 0, limit = 39) :
    """Yield all elements of `str_dates` closest to year changes."""
    return unit_changes (after, before, str_dates, "year", offset, limit)
# end def year_changes

def _main (cmd) :
    after = before = None
    if cmd.after :
        after  = cmd.after
    if cmd.before :
        before = cmd.before
    if cmd.newlines :
        sep = "\n"
    else :
        sep = cmd.separator
    args  = (after, before, cmd.argv)
    dates = set (by_range (* args))
    if cmd.month_change :
        result = month_changes (* args)
    elif cmd.quarter_change :
        result = quarter_changes (* args)
    elif cmd.week_days :
        result = weekdays (after, before, cmd.week_days, cmd.argv)
    elif cmd.year_change :
        result = year_changes (* args)
    else :
        result = sorted (dates)
    if cmd.invert :
        result = sorted (dates - set (result))
    return sep.join (result)
# end def _main

_Command = TFL.CAO.Cmd \
    ( handler     = _main
    , args        =
        ("date:S", )
    , opts        =
        ( TFL.CAO.Opt.Date
            ( name        = "after"
            , description = "Keep all dates after the one specified"
            )
        , TFL.CAO.Opt.Date
            ( name        = "before"
            , description = "Keep all dates before the one specified"
            )
        , "-invert:B?Keep dates that don't match the specified filter"
        , "-month_change:B?Keep dates closest to change of month"
        , "-newlines:B?print new lines between dates"
        , "-quarter_change:B?Keep dates closest to change of quarter"
        , "-separator:S= ?Separator between dates"
        , "-week_days:I,?Keep all dates with weekdays specified"
        , "-year_change:B?Keep dates closest to change of year"
        )
    )

if __name__ != "__main__" :
    CAL._Export_Module ()
if __name__ == "__main__" :
    print (_Command ())
### __END__ CAL.filter_str_dates
