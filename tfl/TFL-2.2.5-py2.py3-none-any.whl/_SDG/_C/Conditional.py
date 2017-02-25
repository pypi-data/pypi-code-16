# -*- coding: utf-8 -*-
# Copyright (C) 2004 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    Conditional
#
# Purpose
#    Root class for conditional constructs
#
# Revision Dates
#     9-Aug-2004 (CT) Creation
#    20-Oct-2004 (CT) `scope` set to `HC`
#    21-Oct-2004 (CT) `scope` argument passed to `_convert`
#    23-Jul-2007 (CED) Activated absolute_import
#    06-Aug-2007 (CED) Future import removed again
#    26-Feb-2012 (MG) `__future__` imports added
#    ««revision-date»»···
#--



from   __future__  import absolute_import, division, print_function, unicode_literals
from   _TFL              import TFL
import _TFL._SDG._C.Expression
import _TFL._SDG._C.Node

class Conditional (TFL.SDG.C.Node) :
    """Root class for conditional constructs"""

    scope               = TFL.SDG.C.HC

    init_arg_defaults    = dict \
        ( condition      = ""
        )

    front_args           = ("condition", )

    _autoconvert         = dict \
        ( condition      = lambda s, k, v
              : s._convert (v, TFL.SDG.C.Expression, scope = TFL.SDG.C.HC)
        )

# end class Conditional

if __name__ != "__main__" :
    TFL.SDG.C._Export ("*")
### __END__ Conditional