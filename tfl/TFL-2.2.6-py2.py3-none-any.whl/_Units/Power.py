# -*- coding: utf-8 -*-
# Copyright (C) 2006-2013 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Units.Power
#
# Purpose
#    Units of power
#
# Revision Dates
#    15-Feb-2006 (CT) Creation
#    ««revision-date»»···
#--

from   _TFL import TFL
import _TFL._Meta.Object
import _TFL._Units.Kind

class Power (TFL.Units.Kind) :
    """Units of power

       >>> Power (1.0)
       1
       >>> Power (1, "kW")
       1000
       >>> Power (1, "hp")
       735.49875
       >>> Power (1, "cal/s")
       4.1868
    """

    Unit              = TFL.Units.Unit

    base_unit         = Unit ("watt", 1.0, "W")
    _units            = \
        ( ### see http://en.wikipedia.org/wiki/Conversion_of_units
          Unit ("calorie_per_second",         4.1868,     "cal/s")
        , Unit ("horsepower",               735.49875,    "hp")
        , Unit ("kilowatt",                1000.0,        "kW")
        )

# end class Power

if __name__ != "__main__" :
    TFL.Units._Export ("*")
### __END__ TFL.Units.Power
