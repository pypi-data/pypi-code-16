# -*- coding: utf-8 -*-
# Copyright (C) 2010 Martin Glueck All rights reserved
# Langstrasse 4, A--2244 Spannberg, Austria. martin@mangari.org
# ****************************************************************************
# This module is part of the package GTW.__test__.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    Composite_as_Primary_Optional
#
# Purpose
#    Use composites as primary optional attributes
#
# Revision Dates
#    21-Apr-2010 (MG) Creation
#    27-Apr-2010 (CT) Test for `sqlite` added, `Scaffold` used
#    ««revision-date»»···
#--

_test_code = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> EVT = scope.EVT
    >>> SWP = scope.SWP
    >>> event_page = SWP.Page (u"2010-01-01-00:00", text = U"An event")
    >>> event = EVT.Event (event_page)
    >>> event.date
    MOM.Date_Interval ()
    >>> event.destroy ()
    >>> event_raw = EVT.Event (event_page.epk_raw, raw = True)
    >>> event_raw.date
    MOM.Date_Interval ()
"""

from _GTW.__test__.model import *

__test__ = Scaffold.create_test_dict (_test_code)

### __END__ GTW.__test__.Composite_as_Primary_Optional
