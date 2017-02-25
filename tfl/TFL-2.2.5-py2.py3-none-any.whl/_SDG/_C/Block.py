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
#    TFL.SDG.C.Block
#
# Purpose
#    Model C blocks
#
# Revision Dates
#    30-Jul-2004 (CT) Creation
#    24-Aug-2004 (CT) `trailer` added
#    23-Jul-2007 (CED) Activated absolute_import
#    06-Aug-2007 (CED) Future import removed again
#    26-Feb-2012 (MG) `__future__` imports added
#    ««revision-date»»···
#--



from   __future__  import absolute_import, division, print_function, unicode_literals
from   _TFL              import TFL
import _TFL._SDG._C._Scope_

class Block (TFL.SDG.C._Scope_) :
    """C block of statements"""

    cgi                  = TFL.SDG.C.Node.Body
    star_level           = 3
    trailer              = ";"

    h_format             = ""
    _c_format = c_format = "".join \
        ( ( """ >{
                >>%(::*decl_children:)s
                >>%(::*head_children:)s
                >>%(::*body_children:)s
                >>%(::*tail_children:)s
                >}%(trailer)s
            """
          )
        )

# end class Block

if __name__ != "__main__" :
    TFL.SDG.C._Export ("*")
### __END__ TFL.SDG.C.Block