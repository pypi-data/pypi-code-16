# -*- coding: utf-8 -*-
# Copyright (C) 2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.RST.TOP.MOM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.RST.TOP.MOM.Random_Picture
#
# Purpose
#    Page displaying a random picture
#
# Revision Dates
#    14-Dec-2015 (CT) Creation
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

import _GTW._RST._TOP._MOM.Mixin
import _GTW._RST._TOP.Page

from   _MOM.import_MOM          import MOM, Q

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL.Decorator           import getattr_safe
from   _TFL.I18N                import _, _T, _Tn
from   _TFL.pyk                 import pyk

import random

_Ancestor = GTW.RST.TOP.Page

class Random_Picture (GTW.RST.MOM.Mixin, _Ancestor) :
    """Page displaying a random picture."""

    pid                = "Random_Picture"

    @property
    @getattr_safe
    def ETM (self) :
        return self.top.scope.SWP.Random_Picture
    # end def ETM

    @Once_Property
    @getattr_safe
    def count (self) :
        return self.ETM.count
    # end def count

    @property
    @getattr_safe
    def picture (self) :
        return self.ETM.query \
            (number = random.randrange (0, self.count)).first ()
    # end def picture

# end class Random_Picture

if __name__ != "__main__" :
    GTW.RST.TOP.MOM._Export ("*")
### __END__ GTW.RST.TOP.MOM.Random_Picture
