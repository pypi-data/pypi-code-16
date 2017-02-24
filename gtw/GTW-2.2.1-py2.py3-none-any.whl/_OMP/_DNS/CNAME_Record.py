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
#    DNS.CNAME_Record
#
# Purpose
#    Model a DNS CNAME Record
#
# Revision Dates
#    06-Sep-2012 (RS) Creation
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

from   _MOM.import_MOM          import *
from   _GTW._OMP._DNS           import DNS
from   _GTW._OMP._DNS.Attr_Type import *
import _GTW._OMP._DNS.Record

_Ancestor_Essence = DNS.Record

class CNAME_Record (_Ancestor_Essence) :
    """A DNS CNAME record"""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class target (A_DNS_Name) :
            """Target of CNAME alias."""

            kind               = Attr.Required

        # end class target

    # end class _Attributes

# end class CNAME_Record

if __name__ != "__main__" :
    DNS._Export ("*")
### __END__ DNS.CNAME_Record
