# -*- coding: utf-8 -*-
# Copyright (C) 2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.OMP.PAP.E164.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.OMP.PAP.E164.Error
#
# Purpose
#    Exception classes for E164
#
# Revision Dates
#    31-Jul-2015 (CT) Creation
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

import _GTW._OMP._PAP._E164

from   _TFL.I18N                import _, _T, _Tn

import _TFL._Meta.Object

class _E164_Value_Error_ \
        (TFL.Meta.BaM (ValueError, metaclass = TFL.Meta.Object.__class__)) :

    _real_name = "ValueError"

    def __init__ (self, country, number, tail = "") :
        self.__super.__init__ \
            ( "".join
                ( ( _T ("Not a proper phone number for %s: %s")
                  % (country, number)
                  , tail
                  )
                )
            )
    # end def __init__

ValueError = _E164_Value_Error_ # end class

class SN_Too_Short (ValueError) :
    """Raised if subscriber number doesn't have enough digits"""

    def __init__ (self, country, number, length, min_length) :
        return self.__super.__init__ \
            ( country, number
            , _T( "; subscriber number must have at least %s digits"
                  "; got %s digits instead"
                )
            % (min_length, length)
            )
    # end def __init__

# end class SN_Too_Short

class SN_Too_Long (ValueError) :
    """Raised if subscriber number has too many digits"""

    def __init__ (self, country, number, length, max_length) :
        return self.__super.__init__ \
            ( country, number
            , _T( "; subscriber number must have at most %s digits"
                  "; got %s digits instead"
                )
            % (max_length, length)
            )
    # end def __init__

# end class SN_Too_Long

if __name__ != "__main__" :
    GTW.OMP.PAP.E164._Export ("*")
### __END__ GTW.OMP.PAP.E164.Error
