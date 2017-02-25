# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 Mag. Christian Tanzer All rights reserved
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
#    GTW.OMP.PAP.Person_has_Account
#
# Purpose
#    Link Person to one or more accounts
#
# Revision Dates
#     6-Dec-2012 (CT) Creation
#    15-May-2013 (CT) Rename `auto_cache` to `auto_rev_ref`
#    16-Apr-2014 (CT) Add query attribute `my_person`
#    12-Sep-2014 (CT) Remove `my_person`
#                     [use type restriction in queries, instead]
#    ««revision-date»»···
#--

from   __future__ import absolute_import, division, print_function, unicode_literals

from   _MOM.import_MOM             import *
from   _GTW                        import GTW
from   _GTW._OMP._PAP              import PAP
from   _TFL.I18N                   import _

import _GTW._OMP._Auth.Account
import _GTW._OMP._PAP.Person

_Ancestor_Essence = PAP.Link2

class Person_has_Account (_Ancestor_Essence) :
    """Link a Person to one or more Accounts."""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        ### Primary attributes

        class left (_Ancestor.left) :
            """Person using the account."""

            role_type          = PAP.Person
            auto_rev_ref       = True

        # end class left

        class right (_Ancestor.right) :
            """Account used by a person."""

            role_type          = GTW.OMP.Auth.Account
            auto_rev_ref       = True
            max_links          = 1

        # end class right

        ### Non-primary attributes

    # end class _Attributes

# end class Person_has_Account

if __name__ != "__main__" :
    GTW.OMP.PAP._Export ("*")
### __END__ GTW.OMP.PAP.Person_has_Account
