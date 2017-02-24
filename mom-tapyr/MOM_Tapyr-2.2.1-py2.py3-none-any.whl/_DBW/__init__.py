# -*- coding: utf-8 -*-
# Copyright (C) 2009-2013 Martin Glück. All rights reserved
# Langstrasse 4, A--2244 Spannberg, Austria. martin@mangari.org
# ****************************************************************************
# This package is part of the package _MOM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    MOM.DBW.__init__
#
# Purpose
#    Package for database wrappers
#
# Revision Dates
#    20-Sep-2009 (MG) Creation
#    ««revision-date»»···
#--

from   _MOM                   import MOM
from   _TFL.Package_Namespace import Package_Namespace

DBW = Package_Namespace ()
MOM._Export ("DBW")

del Package_Namespace

__doc__ = """
.. moduleauthor:: Christian Tanzer <tanzer@swing.co.at>

`MOM.DBW` contains packages with database wrappers for various backends.

"""

### __END__ MOM.DBW.__init__
