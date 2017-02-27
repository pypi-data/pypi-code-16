# -*- coding: utf-8 -*-
# Copyright (C) 2014 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.OMP.SWP.
# 
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.OMP.SWP.Referral
#
# Purpose
#    A resource referring to another resource
#
# Revision Dates
#    28-Jan-2014 (CT) Creation
#    29-Jan-2014 (CT) Change `download` to `download_name`
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _MOM.import_MOM          import *

from   _GTW                     import GTW

import _GTW._OMP._SWP.Object_PN

from   _TFL.I18N                import _, _T, _Tn

_Ancestor_Essence = GTW.OMP.SWP.Object_PN

class Referral (_Ancestor_Essence) :
    """A resource referring to another resource."""

    ui_display_sep        = "/"

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        ### Primary attributes

        class parent_url (A_Url_L) :
            """URL of parent resource."""

            kind               = Attr.Primary
            rank               = -10

        # end class parent_url

        ### Non-primary attributes

        class download_name (A_String) :
            """Mark `target_url` as downloadable URL with specified filename."""

            kind               = Attr.Optional

        # end class download_name

        class target_url (A_Url) :
            """URL of target resource."""

            kind               = Attr.Required

        # end class target_url

    # end class _Attributes

# end class Referral

if __name__ != "__main__" :
    GTW.OMP.SWP._Export ("*")
### __END__ GTW.OMP.SWP.Referral
