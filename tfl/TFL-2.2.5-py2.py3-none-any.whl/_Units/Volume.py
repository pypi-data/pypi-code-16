# -*- coding: utf-8 -*-
# Copyright (C) 2004-2014 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Units.Volume
#
# Purpose
#    Volume units
#
# Revision Dates
#     8-Aug-2004 (CT) Creation
#    26-Nov-2014 (CT) Correct spelling of `deca` (not `deka`!)
#    ««revision-date»»···
#--

from   _TFL import TFL
import _TFL._Meta.Object
import _TFL._Units.Kind
import _TFL._Units.Length

class Volume (TFL.Units.Kind) :
    """Units of volume

       >>> Volume (1.0)
       1
       >>> Volume (1.0, "cbkm")
       1000000000
       >>> Volume (1.0, "cbin")
       1.6387064e-05
       >>> Volume (1.0, "cbft")
       0.028316846592
       >>> Volume (1.0, "cbyd")
       0.764554857984
       >>> Volume (1.0, "cbmi")
       4168181825.44
    """

    Length            = TFL.Units.Length
    Unit              = TFL.Units.Unit

    base_unit         = Unit ("cubic_meter", 1.0, "cbm")
    _units            = \
        (
        # SI prefixes
          Unit ("cubic_nanometer",  Length.nanometer    ** 3, "cbnm")
        , Unit ("cubic_micrometer", Length.micrometer   ** 3, "cbum")
        , Unit ("cubic_millimeter", Length.millimeter   ** 3, "cbmm")
        , Unit ("cubic_centimeter", Length.centimeter   ** 3, "cbcm")
        , Unit ("cubic_decimeter",  Length.decimeter    ** 3, "cbdm")
        , Unit ("cubic_decameter",  Length.decameter    ** 3, "cbdam")
        , Unit ("cubic_hectometer", Length.hectometer   ** 3, "cbhm")
        , Unit ("cubic_kilometer",  Length.kilometer    ** 3, "cbkm")
        # US customary units
        , Unit ("cubic_inch",       Length.inch         ** 3, "cbin")
        , Unit ("cubic_foot",       Length.foot         ** 3, "cbft")
        , Unit ("cubic_yard",       Length.yard         ** 3, "cbyd")
        , Unit ("cubic_mile",       Length.statute_mile ** 3, "cbmi")
        )

# end class Volume

if __name__ != "__main__" :
    TFL.Units._Export ("*")
### __END__ TFL.Units.Volume
