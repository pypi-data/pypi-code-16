# -*- coding: utf-8 -*-
# Copyright (C) 2017 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package TFL.Units.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    TFL.Units.Temperature
#
# Purpose
#    Temperature units
#
# Revision Dates
#    17-Feb-2017 (CT) Creation
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _TFL import TFL
from   _TFL.formatted_repr import formatted_repr

import _TFL._Meta.Object
import _TFL._Units.Kind
import _TFL._Units.Unit

class Temperature (TFL.Units.Kind) :
    """Units of temperature.

    >>> def show (v) :
    ...     print (formatted_repr (v))

    >>> show (Temperature (0, "C").as_F)
    32
    >>> show (Temperature (0, "°C").as_F)
    32
    >>> show (Temperature (0, "°").as_F)
    32
    >>> show (Temperature (0, "C").as_K)
    273.15

    >>> show (Temperature (0, "F").as_C)
    -17.7777777778
    >>> show (Temperature (0, "°F").as_C)
    -17.7777777778

    >>> show (Temperature (0, "F").as_K)
    255.372222222

    >>> show (Temperature (0, "K").as_C)
    -273.15
    >>> show (Temperature (0, "K").as_F)
    -459.67

    >>> show (Temperature (15, "C").as_F)
    59
    >>> show (Temperature (15, "C").as_K)
    288.15

    >>> show (Temperature (37, "C").as_F)
    98.6
    >>> show (Temperature (37, "C").as_K)
    310.15

    >>> show (Temperature (100).as_K)
    373.15
    >>> show (Temperature (100).as_F)
    212

    >>> show (Temperature (500).as_K)
    773.15
    >>> show (Temperature (500).as_F)
    932

    >>> show (Temperature (5500).as_K)
    5773.15
    >>> show (Temperature (5500).as_F)
    9932

    >>> show (Temperature.Celsius (0))
    0

    >>> show (Temperature.Fahrenheit (0))
    -17.7777777778

    >>> show (Temperature.Kelvin (0))
    -273.15

    """

    Unit              = TFL.Units.Unit

    base_unit         = Unit ("Celsius", 1.0, "C", aliases = ("°C", "°"))

    _units            = \
        ( Unit ("Fahrenheit", 5/9, "F", offset =  -32, aliases = ("°F", ))
        , Unit ("Kelvin",     1.0, "K", offset = -273.15)
        )

# end class Temperature

if __name__ != "__main__" :
    TFL.Units._Export ("*")
### __END__ TFL.Units.Temperature
