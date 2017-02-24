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
#    DNS.AAAA_Record
#
# Purpose
#    Model a DNS AAAA Record (IPv6)
#
# Revision Dates
#    06-Sep-2012 (RS) Creation
#    12-Sep-2012 (RS) Fix cut&paste error `A_Record` -> `AAAA_Record`
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

from   _MOM.import_MOM          import *
from   _GTW._OMP._DNS           import DNS
from   _GTW._OMP._NET.Attr_Type import A_IP6_Address
import _GTW._OMP._DNS.Record

_Ancestor_Essence = DNS.Record

class AAAA_Record (_Ancestor_Essence) :
    """A DNS AAAA record (IPv6)"""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class address (A_IP6_Address) :
            """IPv6 address for this name."""

            kind               = Attr.Primary

        # end class name

    # end class _Attributes

# end class AAAA_Record

if __name__ != "__main__" :
    DNS._Export ("*")
### __END__ DNS.AAAA_Record
