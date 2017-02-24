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
#    GTW.OMP.Auth.Group
#
# Purpose
#    Model a group of accounts
#
# Revision Dates
#    16-Jan-2010 (CT) Creation
#    28-Feb-2010 (CT) `desc` added
#    18-Nov-2011 (CT) Import `unicode_literals` from `__future__`
#    17-Jun-2013 (CT) Derive `Group` from `MOM.Object`, not `MOM.Named_Object`
#    ««revision-date»»···
#--

from   __future__            import unicode_literals

from   _MOM.import_MOM        import *
from   _GTW                   import GTW

from   _GTW._OMP._Auth        import Auth
import _GTW._OMP._Auth.Entity

_Ancestor_Essence = Auth.Object

class _Auth_Group_ (_Ancestor_Essence) :
    """Model a group of accounts."""

    _real_name = "Group"

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class name (A_String) :
            """Name of %(type_base_name.lower ())s."""

            kind               = Attr.Primary
            max_length         = 32
            completer          = Attr.Completer_Spec  (2, Attr.Selector.primary)

        # end class name

        class desc (A_String) :
            """Description of group"""

            kind               = Attr.Optional
            max_length         = 20

        # end class desc

    # end class _Attributes

Group = _Auth_Group_ # end class

if __name__ != "__main__" :
    GTW.OMP.Auth._Export ("*")
### __END__ GTW.OMP.Auth.Group
