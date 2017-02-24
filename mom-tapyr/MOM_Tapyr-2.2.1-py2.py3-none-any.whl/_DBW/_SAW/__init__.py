# -*- coding: utf-8 -*-
# Copyright (C) 2013 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package MOM.DBW.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    MOM.DBW.SAW.__init__
#
# Purpose
#    Base database wrapper for databases accessed via sqlalchemy
#
# Revision Dates
#    28-May-2013 (CT) Creation
#    ««revision-date»»···
#--

from   _MOM._DBW              import DBW
from   _TFL.Package_Namespace import Package_Namespace

SAW = Package_Namespace ()
DBW._Export ("SAW")

del Package_Namespace

__doc__ = """
.. moduleauthor:: Christian Tanzer <tanzer@swing.co.at>

`MOM.DBW.SAW` provides a database wrapper for databases accessed via
SQLAlchemy.

"""

### __END__ MOM.DBW.SAW.__init__
