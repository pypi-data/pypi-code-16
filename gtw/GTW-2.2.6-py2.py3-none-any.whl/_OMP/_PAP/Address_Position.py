# -*- coding: utf-8 -*-
# Copyright (C) 2012-2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.OMP.PAP.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.OMP.PAP.Address_Position
#
# Purpose
#    Model the geographical position of an Address
#
# Revision Dates
#    11-Oct-2012 (CT) Creation
#    10-May-2013 (CT) Replace `auto_cache` by `link_ref_attr_name`
#    25-Feb-2016 (CT) Change kind `Required`, not `Primary`, for `position`
#    ««revision-date»»···
#--

from   __future__ import absolute_import, division, print_function, unicode_literals

from   _MOM.import_MOM        import *
from   _MOM._Attr.Position    import *

from   _GTW                   import GTW
from   _GTW._OMP._PAP         import PAP
import _GTW._OMP._PAP.Entity
import _GTW._OMP._PAP.Address

_Ancestor_Essence = PAP.Link1

class Address_Position (_Ancestor_Essence) :
    """Geographical position of an Address."""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        ### Primary attributes

        class left (_Ancestor.left) :
            """Postal address of the `position`"""

            role_type          = PAP.Address
            max_links          = 1
            link_ref_attr_name = "gps"
            link_ref_singular  = True

        # end class left

        class position (A_Position) :
            """Geographical position"""

            kind               = Attr.Required

        # end class position

    # end class _Attributes

# end class Address_Position

if __name__ != "__main__" :
    GTW.OMP.PAP._Export ("*")
### __END__ GTW.OMP.PAP.Address_Position
