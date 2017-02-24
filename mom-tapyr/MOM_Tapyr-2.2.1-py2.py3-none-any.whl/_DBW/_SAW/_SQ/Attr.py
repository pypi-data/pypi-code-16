# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package MOM.DBW.SAW.SQ.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    MOM.DBW.SAW.SQ.Attr
#
# Purpose
#    SQLite specific attribute handling for SAW
#
# Revision Dates
#     4-Aug-2013 (CT) Creation
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _MOM                import MOM
from   _TFL                import TFL
from   _TFL.pyk            import pyk

from   _MOM._DBW._SAW      import SAW, SA

import _MOM._DBW._SAW.Attr
import _MOM._DBW._SAW._SQ

### http://www.sqlite.org/lang_datefunc.html
_strftime_map = dict \
    ( day      = "d"
    , doy      = "j" ### day of year: 001-366
    , hour     = "H"
    , jdn      = "J" ### Julian day number
    , minute   = "M"
    , month    = "m"
    , second   = "S"
    , week     = "W" ### week of year: 00-53
    , year     = "Y"
    )

### Functions to extract fields from date column ##############################
@MOM.Attr._A_DT_._saw_extract_field.add_type (SAW.SQ.Manager.__class__)
def _saw_extract_date_field_sq (self, DBW, col, field) :
    fmt_c  = _strftime_map    [field]
    clause = SA.func.strftime ("%%%s" % (fmt_c, ), col)
    return SA.expression.cast (clause, SA.types.Integer)
# end def _saw_extract_date_field_sq

if __name__ != "__main__" :
    MOM.DBW.SAW.SQ._Export_Module ()
### __END__ MOM.DBW.SAW.SQ.Attr
