# -*- coding: utf-8 -*-
# Copyright (C) 2011-2014 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This modify is part of the package GTW.OMP.SRM.
# 
# This modify is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.OMP.SRM.Club
#
# Purpose
#    Model a sailing club
#
# Revision Dates
#    23-Sep-2011 (CT) Creation
#    31-Jul-2012 (CT) Redefine `Club.name.cooked` to filter non-letters
#    13-Nov-2012 (CT) Fix typo in `name.cooked` (s/self/soc/)
#    ««revision-date»»···
#--

from   __future__  import unicode_literals

from   _GTW                     import GTW
from   _MOM.import_MOM          import *

import _GTW._OMP._SRM.Entity

from   _TFL.I18N                import _, _T, _Tn
from   _TFL.pyk                 import pyk
from   _TFL.Regexp              import Re_Replacer, re

_Ancestor_Essence = GTW.OMP.SRM.Object

class Club (_Ancestor_Essence) :
    """A sailing club."""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        ### Primary attributes

        class name (A_String) :
            """Short name of the sailing club."""

            kind               = Attr.Primary
            example            = "RORC"
            ignore_case        = True
            max_length         = 8
            completer          = Attr.Completer_Spec  (1, Attr.Selector.primary)

            _clean             = Re_Replacer (r"\W+", "", re.UNICODE)

            @TFL.Meta.Class_and_Instance_Method
            def cooked (soc, value) :
                if value is not None :
                    return soc._clean (pyk.text_type (value))
                return value
            # end def cooked

        # end class name

        ### Non-primary attributes

        class long_name (A_String) :
            """Long name of the sailing club."""

            kind               = Attr.Optional
            example            = "Royal Ocean Racing Club"
            max_length         = 64

        # end class long_name

    # end class _Attributes

# end class Club

if __name__ != "__main__" :
    GTW.OMP.SRM._Export ("*")
### __END__ GTW.OMP.SRM.Club
