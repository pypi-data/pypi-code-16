# -*- coding: utf-8 -*-
# Copyright (C) 2014 Dr. Ralf Schlatterbeck All rights reserved
# Reichergasse 131, A--3411 Weidling, Austria. rsc@runtux.com
# ****************************************************************************
# This module is part of the package GTW.OMP.PAP.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.OMP.PAP.Adhoc_Group
#
# Purpose
#    Model an adhoc group of persons
#
# Revision Dates
#    13-Jun-2014 (RS) Creation
#    ««revision-date»»···
#--

from   __future__            import unicode_literals

from   _MOM.import_MOM             import *

from   _GTW._OMP._PAP.Attr_Type    import *

from   _GTW                        import GTW
from   _GTW._OMP._PAP              import PAP

import _GTW._OMP._PAP.Group

_Ancestor_Essence = PAP.Group

class _PAP_Adhoc_Group_ (_Ancestor_Essence) :
    """Adhoc group of persons."""

    _real_name = "Adhoc_Group"

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

    # end class _Attributes

Adhoc_Group = _PAP_Adhoc_Group_ # end class

if __name__ != "__main__" :
    GTW.OMP.PAP._Export ("*")
### __END__ GTW.OMP.PAP.Adhoc_Group
