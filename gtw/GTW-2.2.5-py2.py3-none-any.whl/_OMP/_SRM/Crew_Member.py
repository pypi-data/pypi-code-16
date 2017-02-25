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
#    GTW.OMP.SRM.Crew_Member
#
# Purpose
#    Crew member of a `Boat_in_Regatta`
#
# Revision Dates
#    19-Apr-2010 (CT) Creation
#    13-Oct-2010 (CT) Derive from `Link2` instead of `Link1`
#     1-Dec-2010 (CT) `key` added
#     9-Feb-2011 (CT) `right.ui_allow_new` set to `True`
#    18-Nov-2011 (CT) Import `unicode_literals` from `__future__`
#     8-Aug-2012 (CT) Add `example`
#    12-May-2013 (CT) Replace `auto_cache` by `rev_ref_attr_name`
#    26-Aug-2014 (CT) Add `key.ui_rank`
#    ««revision-date»»···
#--

from   __future__            import unicode_literals

from   _GTW                     import GTW
from   _MOM.import_MOM          import *

import _GTW._OMP._PAP.Person

import _GTW._OMP._SRM.Boat_in_Regatta
import _GTW._OMP._SRM.Entity

from   _TFL.I18N                import _, _T, _Tn

_Ancestor_Essence = GTW.OMP.SRM.Link2

class Crew_Member (_Ancestor_Essence) :
    """Crew member of a `Boat_in_Regatta`."""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        ### Primary attributes

        class left (_Ancestor.left) :
            """`Boat_in_Regatta` the crew member sails on."""

            role_type          = GTW.OMP.SRM.Boat_in_Regatta

        # end class left

        class right (_Ancestor.right) :
            """Person which sails as crew member on `boat_in_regatta`"""

            role_type          = GTW.OMP.SRM.Sailor
            rev_ref_attr_name  = "_crew"
            rev_ref_singular   = True
            ui_allow_new       = True

        # end class right

        ### Non-primary attributes

        class key (A_Int) :
            """The crew members of a boat will be sorted by `key`, if
               defined, by order of creation otherwise.
            """

            kind               = Attr.Optional
            Kind_Mixins        = (Attr.Sticky_Mixin, )
            default            = 0
            example            = 7
            ui_rank            = 10

        # end class key

        class role (A_String) :
            """Role of crew member."""

            kind               = Attr.Optional
            example            = _ ("trimmer")
            max_length         = 32

            completer          = Attr.Completer_Spec  (1)

        # end class role

    # end class _Attributes

# end class Crew_Member

if __name__ != "__main__" :
    GTW.OMP.SRM._Export ("*")
### __END__ GTW.OMP.SRM.Crew_Member
