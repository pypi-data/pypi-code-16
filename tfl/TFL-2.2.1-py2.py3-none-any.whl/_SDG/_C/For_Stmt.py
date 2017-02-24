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
#    TFL.SDG.C.For_Stmt
#
# Purpose
#    Model for statements in the code of a C file
#
# Revision Dates
#    10-Aug-2004 (CT) Creation
#    23-Jul-2007 (CED) Activated absolute_import
#    06-Aug-2007 (CED) Future import removed again
#    26-Feb-2012 (MG) `__future__` imports added
#    ««revision-date»»···
#--



from   __future__  import absolute_import, division, print_function, unicode_literals
from   _TFL              import TFL
import _TFL._SDG._C.Block
import _TFL._SDG._C.Conditional

class For (TFL.SDG.C.Conditional, TFL.SDG.C.Block) :
    """For statement"""

    Ancestor             = TFL.SDG.C.Block

    init_arg_defaults    = dict \
        ( init           = ""
        , increase       = ""
        )

    front_args           = ("init", "condition", "increase")

    _autoconvert         = dict \
        ( init           = lambda s, k, v
              : s._convert (v, TFL.SDG.C.Expression)
        , increase       = lambda s, k, v
              : s._convert (v, TFL.SDG.C.Expression)
        )

    c_format             = "\n".join \
        ( ( """for (%(::*init:)s; %(::*condition:)s; %(::*increase:)s)"""
          , Ancestor._c_format
          )
        )
# end class For

if __name__ != "__main__" :
    TFL.SDG.C._Export ("*")
### __END__ TFL.SDG.C.For_Stmt