# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Dr. Ralf Schlatterbeck All rights reserved
# Reichergasse 131, A-3411 Weidling, Austria. rsc@runtux.com
# ****************************************************************************
# This package is part of the package GTW.OMP.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.OMP.DNS.__init__
#
# Purpose
#    Package defining a partial object model for Domain-Name Service
#    (DNS)
#
# Revision Dates
#    27-Aug-2012 (RS) Creation
#    15-Jun-2013 (CT) Use `MOM.Derived_PNS`
#    ««revision-date»»···
#--

from   _GTW._OMP              import OMP
from   _MOM                   import MOM
import _MOM.Derived_PNS

_desc_ = __doc__ = """
Partial object model for domain name service.
"""

DNS = MOM.Derived_PNS (parent = MOM, pns_alias = "DNS")
OMP._Export ("DNS")

### __END__ GTW.OMP.DNS.__init__
