# -*- coding: utf-8 -*-
# Copyright (C) 2006-2014 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Units.Speed
#
# Purpose
#    Units of speed
#
# Revision Dates
#    15-Feb-2006 (CT) Creation
#    ««revision-date»»···
#--

from   _TFL import TFL
import _TFL._Meta.Object
import _TFL._Units.Kind
import _TFL._Units.Length
import _TFL._Units.Prefix
import _TFL._Units.Time
import _TFL._Units.Unit

class Speed (TFL.Units.Kind) :
    """Units of speed.

       >>> Speed (1)
       1
       >>> Speed (1, "kmh")
       0.277777777778
       >>> Speed (1, "c")
       299792458
    """

    Length        = TFL.Units.Length
    Time          = TFL.Units.Time
    Unit          = TFL.Units.Unit

    base_unit     = Unit ("meter_per_second", 1.0, "m/s")
    _units        = \
        ( ### see http://en.wikipedia.org/wiki/Conversion_of_units
        # Usual units
          Unit ("kilometer_per_hour", Length.kilometer     / Time.hour,   "kmh")
        # US customary units
        , Unit ("furlong_per_fortnight", Length.furlong    / Time.fortnight)
        , Unit ("mile_per_hour",      Length.statute_mile  / Time.hour,   "mph")
        , Unit ("knots",              Length.nautical_mile / Time.hour,    "kn")
        # physics units
        , Unit ("speed_of_light",     Length.light_second  / Time.second,   "c")
        )

# end class Speed

if __name__ != "__main__" :
    TFL.Units._Export ("*")
### __END__ TFL.Units.Speed
