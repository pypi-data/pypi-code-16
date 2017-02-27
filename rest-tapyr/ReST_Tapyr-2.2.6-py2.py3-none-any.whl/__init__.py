# -*- coding: utf-8 -*-
# Copyright (C) 2010-2017 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This file is part of the package _ReST.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    ReST.__init__
#
# Purpose
#    Package augmenting reStructuredText
#
# Revision Dates
#    15-Feb-2010 (CT) Creation
#    29-Aug-2014 (CT) Filter warnings from `PIL`
#    12-Oct-2016 (CT) Add `__version__`
#    22-Feb-2017 (CT) Remove `__version__`
#    ««revision-date»»···
#--

from _TFL.Package_Namespace import Package_Namespace

ReST = Package_Namespace ()

del Package_Namespace

### Filter PIL warnings to avoid crap like this::
# /usr/lib/python2.7/site-packages/PIL/Image.py:44:
#     DeprecationWarning: classic int division
#   MAX_IMAGE_PIXELS = int(1024 * 1024 * 1024 / 4 / 3)

import warnings
warnings.filterwarnings ("ignore", module = "^PIL.*")
del warnings

### __END__ ReST.__init__
