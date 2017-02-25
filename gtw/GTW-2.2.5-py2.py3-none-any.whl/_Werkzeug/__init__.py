# -*- coding: utf-8 -*-
# Copyright (C) 2007-2010 Martin Glück. All rights reserved
# Langstrasse 4, A--2244 Spannberg, Austria. martin@mangari.org
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.Werkzeug.__init__
#
# Purpose
#    Some wrappers/extensions to the werkzeug WSGI utilities
#    (werkzeug.pocoo.org)
#
# Revision Dates
#    20-Mar-2010 (MG) Creation
#    ««revision-date»»···
#--

from   _TFL.Package_Namespace import Package_Namespace
from   _GTW                   import GTW

Werkzeug = Package_Namespace ()
GTW._Export                 ("Werkzeug")

del Package_Namespace

### __END__ GTW.Werkzeug.__init__
