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
#    GTW.OMP.SRM.Team
#
# Purpose
#    Model a team of sailors participating in a regatta
#
# Revision Dates
#    31-Aug-2010 (CT) Creation
#     8-Sep-2011 (CT) `completer` added to `name` and `club`
#    22-Sep-2011 (CT) s/A_Entity/A_Id_Entity/
#    22-Sep-2011 (CT) s/Class/P_Type/ for _A_Id_Entity_ attributes
#    23-Sep-2011 (CT) `club` changed from `A_String` to `A_Id_Entity`
#    15-May-2013 (CT) Replace `auto_cache` by `rev_ref_attr_name`
#    30-Oct-2013 (CT) Remove unnecessary `Team.left.rev_ref_attr_name`
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division
from   __future__  import print_function, unicode_literals

from   _GTW                     import GTW
from   _MOM.import_MOM          import *

import _GTW._OMP._PAP.Person

import _GTW._OMP._SRM.Club
import _GTW._OMP._SRM.Entity

from   _TFL.I18N                import _, _T, _Tn

_Ancestor_Essence = GTW.OMP.SRM.Link1

class Team (_Ancestor_Essence) :
    """A team of sailors participating in a regatta."""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        ### Primary attributes

        class left (_Ancestor.left) :
            """Regatta in which this team sails."""

            role_type          = GTW.OMP.SRM.Regatta_C
            role_name          = "regatta"

        # end class left

        class name (A_String) :
            """Name of the sailing team."""

            kind               = Attr.Primary
            ignore_case        = True
            max_length         = 64
            completer          = Attr.Completer_Spec  (1)

        # end class name

        ### Non-primary attributes

        class club (A_Id_Entity) :
            """Club the team is starting for."""

            P_Type             = GTW.OMP.SRM.Club
            kind               = Attr.Optional

        # end class club

        class desc (A_String) :
            """Short description of the team."""

            kind               = Attr.Optional
            max_length         = 160

        # end class desc

        class leader (A_Id_Entity) :
            """Leader of team."""

            P_Type             = GTW.OMP.PAP.Person
            kind               = Attr.Optional

        # end class leader

        class place (A_Int) :
            """Place of team in this regatta."""

            kind               = Attr.Optional
            min_value          = 1

        # end class place

        class registration_date (A_Date) :
            """Date of registration."""

            kind               = Attr.Internal
            computed_default   = A_Date.now

        # end class registration_date

    # end class _Attributes

# end class Team

if __name__ != "__main__" :
    GTW.OMP.SRM._Export ("*")
### __END__ GTW.OMP.SRM.Team
