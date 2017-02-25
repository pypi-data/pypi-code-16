# -*- coding: utf-8 -*-
# Copyright (C) 2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This package is part of the package GTW.OMP.PAP.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.OMP.PAP.E164.__init__
#
# Purpose
#    Package providing country specific information about E.164, aka,
#    the international public telecommunication numbering plan
#
# Revision Dates
#    23-Jul-2015 (CT) Creation
#    ««revision-date»»···
#--

from   _GTW._OMP._PAP         import PAP
from   _TFL.Package_Namespace import Package_Namespace

E164 = Package_Namespace ()
PAP._Export ("E164")

### __END__ GTW.OMP.PAP.E164.__init__
