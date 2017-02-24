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
#    GTW.OMP.PAP.Id_Entity_permits_Group
#
# Purpose
#    Model permissions for an Id_Entity
#
# Revision Dates
#     3-Jul-2014 (RS) Creation
#    ««revision-date»»···
#--

from   __future__            import unicode_literals

from   _MOM.import_MOM             import *
from   _GTW                        import GTW
from   _GTW._OMP._PAP              import PAP

import _MOM.Entity
import _GTW._OMP._PAP.Group

from   _TFL.I18N                   import _

_Ancestor_Essence = PAP.Link2

class Id_Entity_permits_Group (_Ancestor_Essence) :
    """Permission of a %(right.role_name)s on %(left.role_name)s."""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class left (_Ancestor.left) :
            """ID_Entity for which the permission exists"""

            role_type           = MOM.Id_Entity
            ui_allow_new        = False

        # end class left

        class right (_Ancestor.right) :
            """Permitted Group"""

            role_type           = PAP.Group
            ui_allow_new        = False

        # end class right

    # end class _Attributes

# end class Id_Entity_permits_Group

if __name__ != "__main__" :
    GTW.OMP.PAP._Export ("*")
### __END__ GTW.OMP.PAP.Id_Entity_permits_Group
