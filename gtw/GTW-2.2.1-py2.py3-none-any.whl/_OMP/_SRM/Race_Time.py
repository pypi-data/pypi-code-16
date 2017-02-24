# -*- coding: utf-8 -*-
# Copyright (C) 2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package GTW.OMP.SRM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.OMP.SRM.Race_Time
#
# Purpose
#    Race time (elapsed) of a `Boat_in_Regatta`
#
# Revision Dates
#    25-Oct-2015 (CT) Creation
#    28-Oct-2015 (CT) Add `max_ui_length` to attribute `time`
#    ««revision-date»»···
#--

from   __future__            import unicode_literals

from   _GTW                     import GTW
from   _MOM.import_MOM          import *

import _GTW._OMP._SRM.Boat_in_Regatta

from   _TFL.I18N                import _, _T, _Tn

_Ancestor_Essence = GTW.OMP.SRM.Link1

class Race_Time (_Ancestor_Essence) :
    """Race result of a `Boat_in_Regatta`."""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        ### Primary attributes

        class left (_Ancestor.left) :
            """`Boat_in_Regatta` the crew member sails on."""

            role_type          = GTW.OMP.SRM.Boat_in_Regatta

        # end class left

        class race (A_Int) :
            """Number of race."""

            kind               = Attr.Primary
            example            = "5"
            max_value          = 32
            min_value          = 1

        # end class race

        ### Non-primary attributes

        class time (A_Duration) :
            """Elapsed time sailed by boat in this race."""

            kind               = Attr.Required
            example            = "42:23"
            max_ui_length      = 12
            min_value          = 1
            needs_raw_value    = True
            rank               = 1

        # end class time

        class time_corrected (A_Duration) :
            """Corrected time for boat in this race, """

            kind               = Attr.Cached

        # end class time_corrected

    # end class _Attributes

# end class Race_Time

if __name__ != "__main__" :
    GTW.OMP.SRM._Export ("*")
### __END__ GTW.OMP.SRM.Race_Time
