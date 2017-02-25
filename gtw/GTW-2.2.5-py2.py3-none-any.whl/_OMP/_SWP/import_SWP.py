# -*- coding: utf-8 -*-
# Copyright (C) 2010-2014 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package GTW.OMP.SWP.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.OMP.SWP.import_SWP
#
# Purpose
#    Import SWP object model
#
# Revision Dates
#    24-Feb-2010 (CT) Creation
#    23-Mar-2010 (CT) `Gallery` and `Picture` added
#     9-Apr-2010 (CT) `Clip` added
#    28-Jan-2014 (CT) Add `Referral`
#    ««revision-date»»···
#--

from   _MOM.import_MOM        import *
from   _GTW                   import GTW

import _GTW._OMP._SWP.Object_PN
import _GTW._OMP._SWP.Clip
import _GTW._OMP._SWP.Format
import _GTW._OMP._SWP.Gallery
import _GTW._OMP._SWP.Page
import _GTW._OMP._SWP.Picture
import _GTW._OMP._SWP.Referral

### __END__ GTW.OMP.SWP.import_SWP
