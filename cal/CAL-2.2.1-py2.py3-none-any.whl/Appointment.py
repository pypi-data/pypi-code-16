# -*- coding: utf-8 -*-
# Copyright (C) 2003-2014 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    Appointment
#
# Purpose
#    Model an appointment in a calendar
#
# Revision Dates
#    13-Apr-2003 (CT) Creation
#    19-Apr-2003 (CT) `time_pat` changed to allow for 1-digit hours, too
#    19-Apr-2003 (CT) `prio_pat` factored
#    11-Aug-2007 (CT) Imports corrected
#    17-Dec-2007 (CT) `time_pat` changed to allow for end-time without
#                     start-time, too (plus change of `_duration`)
#    ««revision-date»»···
#--

from   _CAL                       import CAL
from   _TFL                       import TFL

from   _TFL.Regexp                import *
from   _TFL._Meta.totally_ordered import totally_ordered

import _TFL._Meta.Object

time_pat        = Regexp \
    ( r"(?P<time> "
      r"(?:  (?P<hh_head> \d{1,2}) (?: : (?P<mm_head> \d{2}))? )?"
      r"(?: -(?P<hh_tail> \d{1,2}) (?: : (?P<mm_tail> \d{2}))? )?"
      r")"
    , re.VERBOSE
    )
prio_pat        = Regexp (r"(?P<prio> [A-Za-z0-9 ])", re.VERBOSE)
entry_sep       = Regexp ("^>", re.MULTILINE)
entry_pat       = Regexp \
    ( r"[ ]+"
    + time_pat.pattern + r"?"
    + r"[ ]+"
    + prio_pat.pattern
    + r"[ ]<[ ]"
    + r"\s*"
    + r"(?P<activity> .*)"
    + "$"
    , re.VERBOSE | re.MULTILINE | re.DOTALL
    )

@totally_ordered
class Appointment (TFL.Meta.Object) :
    """Model one appointment in a calendar"""

    format = "> %-11s %1.1s < %s"

    def __init__ (self, pat_match, text = None) :
        self.time         = pat_match.time or ""
        self.prio         = pat_match.prio or ""
        self.activity     = pat_match.activity.strip ()
        self.duration     = self._duration (pat_match)
        self.text         = text or str (self)
    # end def __init__

    def _duration (self, pat_match) :
        p = pat_match
        if p.hh_head is not None and p.hh_tail is not None :
            d_h = int (p.hh_tail)      - int (p.hh_head)
            d_m = int (p.mm_tail or 0) - int (p.mm_head or 0)
            return d_h + (d_m / 60.)
    # end def _duration

    def __eq__ (self, rhs) :
        return self.text == getattr (rhs, "text", rhs)
    # end def __eq__

    def __hash__ (self) :
        return hash (self.text)
    # end def __hash__

    def __lt__ (self, rhs) :
        return self.text < getattr (rhs, "text", rhs)
    # end def __lt__

    def __str__ (self) :
        return self.format % (self.time, self.prio, self.activity)
    # end def __str__

# end class Appointment

def appointments (buffer) :
    result = []
    for a in entry_sep.split (buffer) :
        if entry_pat.match (a) :
            result.append (Appointment (entry_pat, a))
    return result
# end def appointments

if __name__ != "__main__" :
    CAL._Export ("*")
### __END__ Appointment
