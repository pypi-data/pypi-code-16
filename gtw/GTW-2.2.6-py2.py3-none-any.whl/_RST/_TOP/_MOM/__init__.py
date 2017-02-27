# -*- coding: utf-8 -*-
# Copyright (C) 2012 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This package is part of the package GTW.RST.TOP.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.RST.TOP.MOM.__init__
#
# Purpose
#    Framework for MOM-specific Tree-of-Pages, mostly RESTful
#
# Revision Dates
#    15-Jul-2012 (CT) Creation
#    ««revision-date»»···
#--

from   _TFL.Package_Namespace import Package_Namespace
from   _GTW._RST._TOP         import TOP

MOM = Package_Namespace ()
TOP._Export ("MOM")

del Package_Namespace

### __END__ GTW.RST.TOP.MOM.__init__
