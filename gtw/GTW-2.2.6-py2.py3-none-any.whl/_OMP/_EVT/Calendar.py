# -*- coding: utf-8 -*-
# Copyright (C) 2011 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.OMP.EVT.
# 
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.OMP.EVT.Calendar
#
# Purpose
#    Model a calendar
#
# Revision Dates
#     8-Nov-2011 (CT) Creation
#    ««revision-date»»···
#--

from   __future__  import unicode_literals

from   _MOM.import_MOM            import *
from   _MOM._Attr.Type            import *
from   _GTW                       import GTW

import _GTW._OMP._EVT.Entity

from   _TFL.I18N                  import _, _T, _Tn

_Ancestor_Essence = GTW.OMP.EVT.Object

class Calendar (_Ancestor_Essence) :
    """Model a calendar of events."""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class name (A_Name) :
            """Name of the calendar"""

            kind               = Attr.Primary
            completer          = Attr.Completer_Spec (0, Attr.Selector.primary)

        # end class name

        class desc (A_String) :
            """Short description of calendar"""

            kind           = Attr.Optional
            max_length     = 80
            ui_name        = "Description"

        # end class desc

    # end class _Attributes

# end class Calendar

if __name__ != "__main__" :
    GTW.OMP.EVT._Export ("*")
### __END__ GTW.OMP.EVT.Calendar
