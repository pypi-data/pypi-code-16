# -*- coding: utf-8 -*-
# Copyright (C) 2013 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.OMP.PAP.
# 
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.OMP.PAP.Legal_Entity
#
# Purpose
#    Model a legal entity that isn't a natural person
#
# Revision Dates
#     4-Mar-2013 (CT) Creation
#    13-Jun-2014 (RS) `_Ancestor_Essence` is now `_PAP.Group`
#                     remove attributes inherited from ancestor
#    ««revision-date»»···
#--

from   __future__ import absolute_import, division, print_function, unicode_literals

from   _MOM.import_MOM             import *
from   _GTW._OMP._PAP.Attr_Type    import *

from   _GTW                        import GTW
from   _GTW._OMP._PAP              import PAP
from   _TFL.I18N                   import _

import _GTW._OMP._PAP.Group

_Ancestor_Essence = PAP.Group

class _PAP_Legal_Entity_ (_Ancestor_Essence) :
    """Model a legal entity that isn't a natural person."""

    _real_name  = "Legal_Entity"

    is_partial  = True

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

    # end class _Attributes

Legal_Entity = _PAP_Legal_Entity_ # end class

if __name__ != "__main__" :
    GTW.OMP.PAP._Export ("*")
### __END__ GTW.OMP.PAP.Legal_Entity
