# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Martin Glück. All rights reserved
# Langstrasse 4, A--2244 Spannberg, Austria. martin@mangari.org
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.OMP.Auth.__init__
#
# Purpose
#    Package defining a partial object model for Authentication
#
# Revision Dates
#    13-Jan-2010 (MG) Creation
#     9-Oct-2012 (CT) Add `_desc_`
#    15-Jun-2013 (CT) Use `MOM.Derived_PNS`
#    ««revision-date»»···
#--

from   _GTW._OMP              import OMP
from   _MOM                   import MOM
import _MOM.Derived_PNS

_desc_ = __doc__ = """
Partial object model for authentication: accounts, groups, and their relations.
"""

Auth = MOM.Derived_PNS (parent = MOM, pns_alias = "Auth")
OMP._Export ("Auth")

### __END__ GTW.OMP.Auth.__init__
