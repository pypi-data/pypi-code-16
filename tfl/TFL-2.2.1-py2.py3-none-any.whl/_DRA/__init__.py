# -*- coding: utf-8 -*-
# Copyright (C) 2006-2016 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.DRA.__init__
#
# Purpose
#    Package for data reduction and analysis
#
# Revision Dates
#    15-Nov-2006 (CT) Creation
#     9-Oct-2016 (CT) Move to Package_Namespace `TFL`
#    ««revision-date»»···
#--

from   _TFL                   import TFL
from   _TFL.Package_Namespace import Package_Namespace

DRA = Package_Namespace ()

TFL._Export ("DRA")

del Package_Namespace

### __END__ TFL.DRA.__init__
