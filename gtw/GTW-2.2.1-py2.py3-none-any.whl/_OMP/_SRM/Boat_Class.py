# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Mag. Christian Tanzer All rights reserved
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
#    GTW.OMP.SRM.Boat_Class
#
# Purpose
#    Model a class of sailboats
#
# Revision Dates
#    15-Apr-2010 (CT) Creation
#     8-Sep-2011 (CT) `completer` added to `name`
#    18-Nov-2011 (CT) Import `unicode_literals` from `__future__`
#     2-Mar-2012 (CT) Set `name.ignore_case` to `True`
#    19-Mar-2012 (CT) Factor `_Boat_Class_`, add `Handicap`
#     7-Aug-2012 (CT) Add `example`
#    13-May-2015 (CT) Change `max_crew` to `Optional`, not `Required`
#    ««revision-date»»···
#--

from   __future__            import unicode_literals

from   _GTW                     import GTW
from   _MOM.import_MOM          import *

import _GTW._OMP._SRM.Entity

from   _TFL.I18N                import _, _T, _Tn

_Ancestor_Essence = GTW.OMP.SRM.Object

class _Boat_Class_ (_Ancestor_Essence) :

    is_partial  = True
    is_relevant = True

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        ### Primary attributes

        class name (A_String) :

            kind               = Attr.Primary
            example            = "Laser"
            ignore_case        = True
            max_length         = 48

            completer          = Attr.Completer_Spec  (1, Attr.Selector.primary)

        # end class name

    # end class _Attributes

# end class _Boat_Class_

_Ancestor_Essence = _Boat_Class_

class Boat_Class (_Ancestor_Essence) :
    """Model a class of sailboats"""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        ### Primary attributes

        class name (_Ancestor.name) :
            """Name of class of sailboats."""

            example            = "Laser"

        # end class name

        ### Non-primary attributes

        class beam (A_Float) :
            """Maximum beam of boat (in meters)."""

            kind               = Attr.Optional
            example            = 1.39
            max_value          = 5.0
            min_value          = 0.5

        # end class beam

        class loa (A_Float) :
            """Length over all (in meters)."""

            kind               = Attr.Optional
            example            = 4.2
            max_value          = 10.0
            min_value          = 2.0

        # end class loa

        class max_crew (A_Int) :
            """Maximum number of crew for this class of sailboats."""

            kind               = Attr.Optional
            default            = 4
            example            = 1
            max_value          = 4
            min_value          = 1

        # end class max_crew

        class sail_area (A_Float) :
            """Seal area upwind (in square meters)."""

            kind               = Attr.Optional
            example            = 7.06
            min_value          = 3.5

        # end class sail_area

    # end class _Attributes

# end class Boat_Class

_Ancestor_Essence = _Boat_Class_

class Handicap (_Ancestor_Essence) :
    """Model a handicap formula for sailboats."""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class name (_Ancestor.name) :
            """Name of handicap formula."""

            example            = "IRC"

        # end class name

    # end class _Attributes

# end class Handicap

if __name__ != "__main__" :
    GTW.OMP.SRM._Export ("*", "_Boat_Class_")
### __END__ GTW.OMP.SRM.Boat_Class
