# -*- coding: utf-8 -*-
# Copyright (C) 2012 Dr. Ralf Schlatterbeck All rights reserved
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
#    DNS.Secondary_IP4
#
# Purpose
#    Model a secondary DNS server with IPv4 Address
#
# Revision Dates
#    27-Aug-2012 (RS) Creation
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

from   _MOM.import_MOM          import *
from   _GTW._OMP._DNS           import DNS
from   _GTW._OMP._NET.Attr_Type import A_IP4_Address
import _GTW._OMP._DNS.Secondary

_Ancestor_Essence = DNS.Secondary

class Secondary_IP4 (_Ancestor_Essence) :
    """ Secondary DNS server (with IPv4 Address).
        A secondary server is allowed Zone transfers and will be
        notified on updates.
    """

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class address (A_IP4_Address) :
            """IPv4 Address of secondary server"""

            kind               = Attr.Primary

        # end class address

    # end class _Attributes

# end class Secondary_IP4

if __name__ != "__main__" :
    DNS._Export ("*")
### __END__ DNS.Secondary_IP4
