# -*- coding: utf-8 -*-
# Copyright (C) 2010-2013 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package GTW.OMP.Auth.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.OMP.Auth.Account_in_Group
#
# Purpose
#    Model association Account_in_Group
#
# Revision Dates
#    16-Jan-2010 (CT) Creation
#    18-Jan-2010 (CT) `auto_cache` added
#    15-May-2013 (CT) Rename `auto_cache` to `auto_rev_ref`
#    ««revision-date»»···
#--

from   _MOM.import_MOM        import *
from   _GTW                   import GTW

from   _GTW._OMP._Auth        import Auth
import _GTW._OMP._Auth.Entity
import _GTW._OMP._Auth.Account
import _GTW._OMP._Auth.Group

from   _TFL.I18N              import _, _T, _Tn

_Ancestor_Essence = Auth.Link2

class Account_in_Group (_Ancestor_Essence) :
    """Model association Account_in_Group"""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class left (_Ancestor.left) :

            role_type     = Auth.Account
            auto_rev_ref  = True

        # end class left

        class right (_Ancestor.right) :

            role_type     = Auth.Group
            auto_rev_ref  = True

        # end class right

    # end class _Attributes

# end class Account_in_Group

if __name__ != "__main__" :
    GTW.OMP.Auth._Export ("*")
### __END__ GTW.OMP.Auth.Account_in_Group
