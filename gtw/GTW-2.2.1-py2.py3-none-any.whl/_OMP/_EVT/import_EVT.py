# -*- coding: utf-8 -*-
# Copyright (C) 2010-2011 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package GTW.OMP.EVT.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.OMP.EVT.import_EVT
#
# Purpose
#    Import EVT object model
#
# Revision Dates
#    10-Mar-2010 (CT) Creation
#     8-Nov-2011 (CT) `Calendar` added
#    ««revision-date»»···
#--

from   _MOM.import_MOM        import *
from   _GTW                   import GTW

import _GTW._OMP._EVT
import _GTW._OMP._EVT.Entity

import _GTW._OMP._EVT.Calendar
import _GTW._OMP._EVT.Event
import _GTW._OMP._EVT.Recurrence_Spec

### __END__ GTW.OMP.EVT.import_EVT
