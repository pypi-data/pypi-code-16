# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Martin Glueck All rights reserved
# Langstrasse 4, A--2244 Spannberg, Austria. martin@mangari.org
# #*** <License> ************************************************************#
# This module is part of the package GTW.RST.TOP.elFinder.
# 
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.RST.TOP.elFinder.Error
#
# Purpose
#    Error handling for the jquery file browser `elfinder 2`
#    http://elfinder.org/
#
# Revision Dates
#    29-Jan-2013 (MG) Creation
#    ««revision-date»»···
#--

from   __future__ import absolute_import, division, print_function, unicode_literals

from    _GTW                       import GTW
from    _TFL._Meta.Once_Property   import Once_Property
import  _GTW._RST._TOP._elFinder

class Error (Exception) :
    """elFinder error message"""

    def __init__ (self, code, data = None) :
        self.code = code
        self.data = data
    # end def __init__

    @Once_Property
    def json_cargo (self) :
        if self.data :
            return [self.code, self.data]
        return self.code
    # end def json_cargo

# end class Error

if __name__ != "__main__" :
    GTW.RST.TOP.elFinder._Export ("*")
### __END__ GTW.RST.TOP.elFinder.Error
