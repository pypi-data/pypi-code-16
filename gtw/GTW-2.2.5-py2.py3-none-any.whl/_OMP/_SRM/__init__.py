# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This package is part of the package GTW.OMP.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.OMP.SRM.__init__
#
# Purpose
#    Package defining a partial object model for sailing regattas
#
# Revision Dates
#    15-Apr-2010 (CT) Creation
#     9-Oct-2012 (CT) Add `_desc_`
#    15-Jun-2013 (CT) Use `MOM.Derived_PNS`
#    ««revision-date»»···
#--

from   _GTW._OMP              import OMP
from   _MOM                   import MOM
import _MOM.Derived_PNS

_desc_ = __doc__ = """
Partial object model for the management of sailboat regattas.
"""

SRM = MOM.Derived_PNS (parent = MOM, pns_alias = "SRM")
OMP._Export ("SRM")

### __END__ GTW.OMP.SRM.__init__
