# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Mag. Christian Tanzer All rights reserved
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
#    GTW.OMP.Auth.UI_Spec
#
# Purpose
#    UI specification for E_Types defined by GTW.OMP.Auth
#
# Revision Dates
#    26-Feb-2010 (CT) Creation
#    30-Apr-2010 (MG) Adapted to new form's
#     2-May-2010 (MG) Simplified
#     6-May-2010 (MG) Switch to render mode rendering
#    18-Nov-2011 (CT) Import `unicode_literals` from `__future__`
#    24-Jan-2012 (CT) Remove `Form_args`, `*_completer`,
#                     i.e., stuff related to non-AFS forms
#    22-May-2012 (CT) Fix typo (`Account_P = dict`, not `Account = dict`)
#    26-Jul-2012 (CT) Import `_GTW._RST.Permission`, not `_GTW._NAV.Permission`
#    16-Jan-2013 (CT) Add `Certificate`
#    16-Dec-2015 (CT) Change to `UI_Spec`
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

from   _GTW._RST.Permission     import Is_Superuser

import _GTW._OMP._PAP

import _TFL.Sorted_By

class UI_Spec (object) :
    """UI specification for E_Types defined by GTW.OMP.Auth"""

    Account          = dict \
        ( permission = Is_Superuser ()
        )

    Certificate      = dict \
        ( permission = Is_Superuser ()
        )

    Group            = dict \
        ( permission = Is_Superuser ()
        )

    Account_in_Group = dict \
        ( permission = Is_Superuser ()
        )

# end class UI_Spec

if __name__ != "__main__" :
    GTW.OMP.Auth._Export ("UI_Spec")
### __END__ GTW.OMP.Auth.UI_Spec
