# -*- coding: utf-8 -*-
# Copyright (C) 2012 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This package is part of the package MOM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    MOM.Graph.__init__
#
# Purpose
#    Package providing graphical display of MOM object models
#
# Revision Dates
#    16-Aug-2012 (CT) Creation
#    ««revision-date»»···
#--

from   _TFL.Package_Namespace import Package_Namespace
from   _MOM                   import MOM

Graph = Package_Namespace ()
MOM._Export ("Graph")

del Package_Namespace

### __END__ MOM.Graph.__init__
