# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Dr. Ralf Schlatterbeck All rights reserved
# Reichergasse 131, A-3411 Weidling, Austria. rsc@runtux.com
# ****************************************************************************
# This module is part of the package GTW.OMP.DNS.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.OMP.DNS.UI_Spec
#
# Purpose
#    UI specification for E_Types defined by GTW.OMP.DNS
#
# Revision Dates
#     6-Sep-2012 (RS) Creation
#    16-Dec-2015 (CT) Change to `UI_Spec`
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

import _GTW._OMP._DNS

import _TFL.Sorted_By

class UI_Spec (object) :
    """UI specification for E_Types defined by GTW.OMP.DNS"""

    AAAA_Record          = dict \
        (
        )

    A_Record             = dict \
        (
        )

    CNAME_Record         = dict \
        (
        )

    MX_Record            = dict \
        (
        )

    NS_Record            = dict \
        (
        )

    Secondary_IP4        = dict \
        (
        )

    Secondary_IP6        = dict \
        (
        )

    SRV_Record           = dict \
        (
        )

    TXT_Record           = dict \
        (
        )

    Zone                 = dict \
        (
        )

# end class UI_Spec

if __name__ != "__main__" :
    GTW.OMP.DNS._Export ("UI_Spec")
### __END__ GTW.OMP.DNS.UI_Spec
