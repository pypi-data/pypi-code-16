# -*- coding: utf-8 -*-
# Copyright (C) 2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package MOM.Attr.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    MOM.Attr.Range_DT
#
# Purpose
#    Attributes types for date-time specific ranges
#
# Revision Dates
#    20-Jul-2016 (CT) Creation
#    21-Sep-2016 (CT) Use `A_Time_X`, not `A_Time`, for `A_Date_Range.C_Type`
#    11-Oct-2016 (CT) Adapt to move of `Range_DT` from `TFL` to `CAL`
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _CAL                  import CAL
from   _MOM.import_MOM       import *
from   _MOM._Attr.Range      import *

from   _TFL.I18N             import _, _T, _Tn
from   _TFL.pyk              import pyk

import _CAL.Range_DT

class A_Date_Range (_A_Range_) :
    """Date range."""

    C_Type         = A_Date
    P_Type         = CAL.Date_Range
    example        = "[2016-07-05, 2016-07-20]"
    typ            = _ ("Date_Range")

    class _Attributes (_A_Range_._Attributes) :

        _Ancestor = _A_Range_._Attributes

        class btype (_Ancestor.btype) :

            default            = "[]"

        # end class btype

        class lower (_Ancestor.lower, A_Date) :

            ui_name            = _ ("start")

        # end class lower

        class upper (_Ancestor.upper, A_Date) :

            ui_name            = _ ("finish")

        # end class upper

    # end class _Attributes

# end class A_Date_Range

class A_Time_Range (_A_Range_) :
    """Time range."""

    C_Type         = A_Time_X
    P_Type         = CAL.Time_Range
    example        = "[08:30, 10:00)"
    typ            = _ ("Time_Range")

    class _Attributes (_A_Range_._Attributes) :

        _Ancestor = _A_Range_._Attributes

        class btype (_Ancestor.btype) :

            default            = "[)"

        # end class btype

        class lower (_Ancestor.lower, A_Time_X) :

            ui_name            = _ ("start")

        # end class lower

        class upper (_Ancestor.upper, A_Time_X) :

            ui_name            = _ ("finish")

        # end class upper

    # end class _Attributes

# end class A_Time_Range

__sphinx__members = __all__ = __attr_types = attr_types_of_module ()

if __name__ != "__main__" :
    MOM.Attr._Export (* __attr_types)
### __END__ MOM.Attr.Range_DT
