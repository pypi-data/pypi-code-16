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
#    GTW.OMP.PAP.Person_in_Group
#
# Purpose
#    Model the membership of a person in a Group
#
# Revision Dates
#    13-Jun-2014 (RS) Creation
#     4-Sep-2014 (CT) Add `ui_allow_new = False` to `left` and `right`
#    12-Sep-2014 (CT) Add `left.rev_ref_attr_name = "member"`
#    ««revision-date»»···
#--

from   __future__             import unicode_literals

from   _MOM.import_MOM        import *
from   _GTW                   import GTW
from   _GTW._OMP._PAP         import PAP

import _GTW._OMP._PAP.Person
import _GTW._OMP._PAP.Group

_Ancestor_Essence = PAP.Link2

class Person_in_Group (_Ancestor_Essence) :
    """Link a %(left.role_name)s to a %(right.role_name)s"""

    is_partial  = True
    is_relevant = True

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class left (_Ancestor.left) :
            """%(left.role_type.ui_name)s linked to %(right.role_type.ui_name)s"""

            role_type           = PAP.Person
            rev_ref_attr_name   = "member"
            ui_allow_new        = False

        # end class left

        class right (_Ancestor.right) :
            """%(right.role_type.ui_name)s of %(left.role_type.ui_name.lower())s"""

            role_type           = PAP.Group
            auto_rev_ref_np     = True
            auto_derive_np      = True
            link_ref_attr_name  = "member"
            ui_allow_new        = False

        # end class right

    # end class _Attributes

# end class Person_in_Group

if __name__ != "__main__" :
    GTW.OMP.PAP._Export ("*")
### __END__ GTW.OMP.PAP.Person_in_Group
