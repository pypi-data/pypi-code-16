# -*- coding: utf-8 -*-
# Copyright (C) 2009-2017 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.__init__
#
# Purpose
#    Package implementing Glück and Tanzer's Web framework
#
# Revision Dates
#    28-Dec-2009 (CT) Creation
#    12-Oct-2016 (CT) Add `__version__`
#    22-Feb-2017 (CT) Remove `__version__`
#    ««revision-date»»···
#--

from _TFL.Package_Namespace import Package_Namespace

__doc__     = """
`GTW` provides a `Werkzeug-based <http://werkzeug.pocoo.org/>`_ framework for
defining RESTful web applications built on top of :mod:`MOM<_MOM>`.
"""

GTW = Package_Namespace ()

del Package_Namespace

### __END__ GTW.__init__
