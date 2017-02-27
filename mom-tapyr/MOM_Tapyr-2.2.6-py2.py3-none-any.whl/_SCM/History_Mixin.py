# -*- coding: utf-8 -*-
# Copyright (C) 2004-2014 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package _MOM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    MOM.SCM.History_Mixin
#
# Purpose
#    History mixin for MOM Scope change management
#
# Revision Dates
#     7-Oct-2009 (CT) Creation (factored from TOM.SCM.History_Mixin)
#    17-Dec-2009 (CT) `add_change` added
#    17-May-2010 (CT) Changed `change_count` from class variable into
#                     instance variable
#    ««revision-date»»···
#--

from   _MOM                  import MOM
from   _TFL                  import TFL
from   _TFL.pyk              import pyk

import _MOM._SCM

import _TFL._Meta.Object

@pyk.adapt__bool__
class History_Mixin (TFL.Meta.Object) :

    change_count = 0

    def __init__ (self) :
        self.history      = []
    # end def __init__

    def add_change (self, change) :
        self.history.append (change)
    # end def add_change

    def __bool__ (self) :
        return bool (self.change_count or self.history)
    # end def __bool__

# end class History_Mixin

if __name__ != "__main__" :
    MOM.SCM._Export ("*")
### __END__ MOM.SCM.History_Mixin
