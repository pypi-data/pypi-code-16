# -*- coding: utf-8 -*-
# Copyright (C) 2010-2014 Mag. Christian Tanzer All rights reserved
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
#    GTW.OMP.SRM.Sailor
#
# Purpose
#    Model a sailor
#
# Revision Dates
#    15-Apr-2010 (CT) Creation
#     7-May-2010 (CT) `club` added
#     9-Feb-2011 (CT) `Sailor.left.ui_allow_new` set to `True`
#     7-Sep-2011 (CT) `completer` added to `nation`, `mna_number`, and `club`
#     7-Sep-2011 (CT) `club` changed from `Optional` to `Primary_Optional`
#     9-Sep-2011 (CT) `completer` re-added to `mna_number`,
#                     `completer` removed from `nation`
#    23-Sep-2011 (CT) `club` changed from `A_String` to `A_Id_Entity`
#    18-Nov-2011 (CT) Import `unicode_literals` from `__future__`
#    20-Jan-2012 (CT) Change `mna_number` from `A_String` to `A_Int`
#     7-May-2014 (CT) Add `club.completer`
#    26-Aug-2014 (CT) Add `ui_rank` declarations to move `mna_number` ahead
#                     of `nation`
#    ««revision-date»»···
#--

from   __future__            import unicode_literals

from   _GTW                     import GTW
from   _MOM.import_MOM          import *

from   _GTW._OMP._SRM.Attr_Type import *

import _GTW._OMP._PAP.Person

import _GTW._OMP._SRM.Club
import _GTW._OMP._SRM.Entity

from   _TFL.I18N                import _, _T, _Tn

_Ancestor_Essence = GTW.OMP.SRM.Link1

class Sailor (_Ancestor_Essence) :
    """A person that is member of a sailing club."""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        ### Primary attributes

        class left (_Ancestor.left) :

            role_type          = GTW.OMP.PAP.Person
            ui_allow_new       = True
            ui_rank            = -5

            completer          = Attr.E_Completer_Spec (Attr.Selector.primary)

        # end class left

        class nation (A_Nation) :
            """Nation for which the sailor sails."""

            kind               = Attr.Primary_Optional
            ui_rank            = -2

        # end class nation

        class mna_number (A_Int) :
            """Membership number in Member National Authorities (MNA)."""

            kind               = Attr.Primary_Optional
            completer          = Attr.Completer_Spec  (1, Attr.Selector.primary)
            min_value          = 0
            max_value          = 999999
            needs_raw_value    = True
            css_align          = "right"
            ui_rank            = -4

        # end class mna_number

        class club (A_Id_Entity) :
            """Club the sailor is starting for."""

            P_Type             = GTW.OMP.SRM.Club
            kind               = Attr.Primary_Optional
            completer          = Attr.E_Completer_Spec (Attr.Selector.primary)
            ui_rank            = -1

        # end class club

    # end class _Attributes

# end class Sailor

if __name__ != "__main__" :
    GTW.OMP.SRM._Export ("*")
### __END__ GTW.OMP.SRM.Sailor
