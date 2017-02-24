# -*- coding: utf-8 -*-
# Copyright (C) 2010-2013 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package TFL.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.pyk
#
# Purpose
#    Hide incompatibilities between Python2 and Python3
#
# Revision Dates
#    16-Jun-2010 (CT) Creation
#    ««revision-date»»···
#--

import sys

if sys.version_info < (3,) :
    from _TFL._pyk2 import pyk
else :
    from _TFL._pyk3 import pyk
### __END__ TFL.pyk
