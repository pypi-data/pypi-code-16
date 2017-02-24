# -*- coding: utf-8 -*-
# Copyright (C) 2009 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package _MOM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    MOM.Product_Version
#
# Purpose
#    Model product version of form `major.minor.patchlevel'
#
# Revision Dates
#    18-Dec-2009 (CT) Creation
#    ««revision-date»»···
#--

from _MOM import MOM

from _TFL.Product_Version import *

if __name__ == "__main__" :
    MOM._Export ("Product_Version")
### __END__ MOM.Product_Version
