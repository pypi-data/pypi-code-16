# -*- coding: utf-8 -*-
# Copyright (C) 2013 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package MOM.DBW.SAW.SQ.
# 
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    MOM.DBW.SAW.SQ.__init__
#
# Purpose
#    Database wrapper for SQLite accessed by sqlalchemy wrapped by SAW
#
# Revision Dates
#    21-Jun-2013 (CT) Creation
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from _MOM._DBW._SAW import SAW
from   _TFL.Package_Namespace import Derived_Package_Namespace

SQ = Derived_Package_Namespace (parent = SAW)
SAW._Export ("SQ")

del Derived_Package_Namespace

### __END__ .MOM.DBW.SAW.SQ__init__
