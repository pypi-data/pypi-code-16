# -*- coding: utf-8 -*-
# Copyright (C) 2004-2005 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    Formatter_Scope
#
# Purpose
#    Provide a descendent of TFL.Caller.Object_Scope that returns
#    `""` instead of `None`
#
# Revision Dates
#    12-Dec-2004 (CT) Creation
#    ««revision-date»»···
#--

from   _TFL                    import TFL
from   _CAL                    import CAL
import _TFL.Caller

class Formatter_Scope (TFL.Caller.Object_Scope) :

    def __getitem__ (self, index) :
        result = self.__super.__getitem__ (index)
        if result is None :
            result = ""
        return result
    # end def __getitem__

# end class Formatter_Scope

if __name__ != "__main__" :
    CAL._Export ("*")
### __END__ Formatter_Scope


