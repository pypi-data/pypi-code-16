# -*- coding: utf-8 -*-
# Copyright (C) 2010-2013 Mag. Christian Tanzer All rights reserved
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
#    GTW.OMP.SRM.Race_Result
#
# Purpose
#    Race result of a `Boat_in_Regatta`
#
# Revision Dates
#     6-Sep-2010 (CT) Creation
#     7-Oct-2011 (CT) `race.min_value` set to `1`
#    18-Nov-2011 (CT) Import `unicode_literals` from `__future__`
#    15-May-2013 (CT) Replace `auto_cache` by `rev_ref_attr_name`
#    25-Jun-2013 (CT) Add `max_value`, `example` to integer attributes
#    30-Oct-2013 (CT) Remove unnecessary `Race_Result.left.rev_ref_attr_name`
#    ««revision-date»»···
#--

from   __future__            import unicode_literals

from   _GTW                     import GTW
from   _MOM.import_MOM          import *

import _GTW._OMP._SRM.Boat_in_Regatta
import _GTW._OMP._SRM.Entity

from   _TFL.I18N                import _, _T, _Tn

_Ancestor_Essence = GTW.OMP.SRM.Link1

class Race_Result (_Ancestor_Essence) :
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

        class discarded (A_Boolean) :
            """The result of this race is discarded."""

            kind               = Attr.Optional
            Kind_Mixins        = (Attr.Sticky_Mixin, )
            default            = False
            rank               = 3

        # end class discarded

        class points (A_Int) :
            """Points of boat in this race."""

            kind               = Attr.Necessary
            example            = "42"
            min_value          = 1
            rank               = 1

        # end class points

        class status (A_String) :
            """Status of boat in this race (DNS, DNF, BFD, ...)"""

            kind               = Attr.Optional
            max_length         = 8
            rank               = 2

        # end class status

    # end class _Attributes

    @property
    def ui_display_format (self) :
        result = "%(points)s"
        if self.discarded :
            result = "[" + result + "]"
        if self.status :
            result += " %(status)s"
        return result
    # end def ui_display_format

# end class Race_Result

if __name__ != "__main__" :
    GTW.OMP.SRM._Export ("*")
### __END__ GTW.OMP.SRM.Race_Result
