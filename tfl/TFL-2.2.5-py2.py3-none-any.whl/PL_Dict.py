# -*- coding: utf-8 -*-
# Copyright (C) 1999-2005 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.PL_Dict
#
# Purpose
#    Provide a dictionary similar to those in Perl. Referencing undefined
#    keys doesn't trigger an exception but returns an undefined value.
#
# Revision Dates
#     6-Apr-1999 (CT) Creation
#     8-Apr-1999 (CT) Constructor semantics changed (`** kw' instead of
#                     argument `data = None')
#    24-Mar-2005 (CT) Moved into package `TFL`
#    23-Jul-2007 (CED) Activated absolute_import
#    06-Aug-2007 (CED) Future import removed again
#    ««revision-date»»···
#--



from   _TFL      import TFL

from   UserDict  import UserDict
from   copy      import deepcopy

class PL_Dict (UserDict) :
    """Perl like dictionary: references to undefined keys return an undefined
       value instead of raising an exception.
    """

    def __init__ (self, undefined = None, ** kw) :
        """Construct a new `PL_Dict' with elements specified as keyword
           arguments `kw' and undefined value `undefined'.
        """
        UserDict.__init__ (self)
        self.data.update  (kw)
        self.body         = self.data ### alias name for `self.data'
        self.undefined    = undefined
    # end def __init__

    def __getitem__ (self, key) :
        try :
            return self.data [key]
        except KeyError :
            return deepcopy (self.undefined)
    # end def __getitem__

    def __delitem__ (self, key) :
        try :
            del self.data [key]
        except KeyError :
            pass
    # end def __delitem__

# end class PL_Dict

if __name__ != "__main__" :
    TFL._Export ("*")
### __END__ TFL.PL_Dict
