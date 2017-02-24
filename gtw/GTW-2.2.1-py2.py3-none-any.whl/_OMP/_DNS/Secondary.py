# -*- coding: utf-8 -*-
# Copyright (C) 2012-2013 Dr. Ralf Schlatterbeck All rights reserved
# Reichergasse 131, A-3411 Weidling, Austria. rsc@runtux.com
# #*** <License> ************************************************************#
# This package is part of the package GTW.OMP.DNS.
# 
# This package is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    DNS.Secondary
#
# Purpose
#    Model a secondary DNS server
#
# Revision Dates
#    27-Aug-2012 (RS) Creation
#     7-Aug-2013 (CT) Use `A_IP4_Address`, not `_A_Composite_IP_Address_`
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

from   _GTW                     import GTW
from   _MOM.import_MOM          import *

from   _GTW._OMP._DNS           import DNS

import _GTW._OMP._NET.Attr_Type
import _GTW._OMP._DNS.Entity
import _GTW._OMP._DNS.Zone

_Ancestor_Essence = DNS.Link1

class Secondary (_Ancestor_Essence) :
    """ Secondary DNS server.
        A secondary server is allowed Zone transfers and will be
        notified on updates.
    """

    is_partial = True

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class left (_Ancestor.left) :
            """The zone for which this server is a secondary"""

            role_type          = DNS.Zone
            role_name          = "zone"
            ui_allow_new       = False

        # end class name

        class address (GTW.OMP.NET.A_IP4_Address) :
            """IP Address of secondary server"""

            kind               = Attr.Primary

        # end class address

    # end class _Attributes

# end class Secondary

if __name__ != "__main__" :
    DNS._Export ("*")
### __END__ DNS.Secondary
