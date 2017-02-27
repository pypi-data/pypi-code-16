# -*- coding: utf-8 -*-
# Copyright (C) 2009-2014 Mag. Christian Tanzer. All rights reserved
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
#    MOM.Pred.Err_and_Warn_List
#
# Purpose
#    Encapsules lists of error and warning objects
#
# Revision Dates
#     1-Oct-2009 (CT) Creation
#    ««revision-date»»···
#--

from   _MOM                  import MOM
from   _TFL                  import TFL
from   _TFL.pyk              import pyk

import _MOM._Pred

import _TFL._Meta.Object

@pyk.adapt__bool__
class Err_and_Warn_List (TFL.Meta.Object) :

    def __init__ (self, errors, warnings) :
        self.errors   = errors
        self.warnings = warnings
    # end def __init__

    def extend (self, other) :
        self.errors.extend   (other.errors)
        self.warnings.extend (other.warnings)
    # end def extend

    def __len__ (self) :
        return len (self.errors)
    # end def __len__

    def __bool__ (self) :
        return bool (self.errors)
    # end def __bool__

    def __iter__ (self) :
        return iter (self.errors)
    # end def __iter__

# end class Err_and_Warn_List

if __name__ != "__main__" :
    MOM.Pred._Export ("*")
### __END__ MOM.Pred.Err_and_Warn_List
