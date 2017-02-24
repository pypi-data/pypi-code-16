# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package MOM.Attr.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    MOM.Attr.Time_Interval
#
# Purpose
#    Composite attribute type for time interval (start, finish)
#
# Revision Dates
#     8-Mar-2010 (CT) Creation
#    22-Sep-2011 (CT) s/C_Type/P_Type/ for _A_Composite_ attributes
#    18-Nov-2011 (CT) Import `unicode_literals` from `__future__`
#     5-Jun-2013 (CT) Use `is_attr_type`, not home-grown code
#    11-Dec-2015 (CT) Use `attr_types_of_module`, not home-grown code
#    ««revision-date»»···
#--

from   __future__            import unicode_literals

from   _MOM.import_MOM       import *
from   _MOM.import_MOM       import _A_Composite_

from   _TFL.I18N             import _, _T, _Tn
from   _TFL.pyk              import pyk

_Ancestor_Essence = MOM.An_Entity

@pyk.adapt__bool__
class Time_Interval (_Ancestor_Essence) :
    """Model a time interval (start, finish)"""

    ui_display_sep = " - "

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class start (A_Time) :
            """Start time of interval"""

            kind               = Attr.Necessary
            rank               = 1

        # end class start

        class finish (A_Time) :
            """Finish time of interval"""

            kind               = Attr.Optional
            rank               = 2

        # end class finish

    # end class _Attributes

    class _Predicates (_Ancestor_Essence._Predicates) :

        _Ancestor = _Ancestor_Essence._Predicates

        class finish_after_start (Pred.Condition) :
            """The finish time must be later than the start time"""

            kind               = Pred.Object
            assertion          = "start < finish"
            attributes         = ("start", "finish")

        # end class finish_after_start

    # end class _Predicates

    def __bool__ (self) :
        return self.start is not None
    # end def __bool__

# end class Time_Interval

class A_Time_Interval (_A_Composite_) :
    """Models an attribute holding a time interval (start, finish)"""

    P_Type         = Time_Interval
    typ            = "Time_Interval"

# end class A_Time_Interval

__attr_types      = Attr.attr_types_of_module ()
__sphinx__members = ("Time_Interval", ) + __attr_types

if __name__ != "__main__" :
    MOM.Attr._Export (* __attr_types)
### __END__ MOM.Attr.Time_Interval
