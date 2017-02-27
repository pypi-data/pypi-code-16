# -*- coding: utf-8 -*-
# Copyright (C) 2009-2010 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This package is part of the package _MOM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    MOM.Meta.__init__
#
# Purpose
#    Initialize package `MOM.Meta`
#
# Revision Dates
#    17-Sep-2009 (CT) Creation (factored from TOM.Meta)
#    ««revision-date»»···
#--

from   _TFL.Package_Namespace import Derived_Package_Namespace
from   _TFL                   import TFL
from   _MOM                   import MOM

import _TFL._Meta

Meta = Derived_Package_Namespace (parent = TFL.Meta)
MOM._Export ("Meta")

del Derived_Package_Namespace

__doc__ = """
.. moduleauthor:: Christian Tanzer <tanzer@swing.co.at>

`MOM.Meta` provides meta classes for the definition and
implementation of essential object models (see :mod:`MOM<_MOM>`).

"""

### __END__ MOM.Meta.__init__
