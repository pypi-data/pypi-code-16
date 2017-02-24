# -*- coding: utf-8 -*-
# Copyright (C) 2004-2007 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    JD
#
# Purpose
#    Compute `julian day number` for a given date
#
# Revision Dates
#     5-Jun-2004 (CT) Creation
#    11-Aug-2007 (CT) U_Test ballast removed
#    ««revision-date»»···
#--

"""A julian day number is a continuous count of days from the beginning of
the year -4712. By (astronomical) tradition, the Julian Day begins at
Greenwhich mean noon, that is, at 12h Universal Time.

see Jean Meeus, Astronomical Algorithms, 1991, 1998
"""

def JD (d, m, y) :
    """Returns Julian Day number for year `y`, month `m`, and day `d`."""
    if m <= 2 :
        y -= 1
        m += 12
    if (y, m, d) >= (1582, 10, 15) :
        a = int (y / 100)
        b = 2 - a + int (a / 4)
    else :
        b = 0
    jd = int (365.25  * (y + 4716)) + int (30.6001 * (m + 1)) + d + b - 1524.5
    return jd
# end def JD

if __name__ != "__main__" :
    from _CAL import CAL
    CAL._Export ("JD")
### __END__ JD
