# -*- coding: utf-8 -*-
# Copyright (C) 2010-2014 Martin Glueck All rights reserved
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
#    GTW.__test__.PID_Manager
#
# Purpose
#    Testing of the pid manager
#
# Revision Dates
#    12-May-2010 (MG) Creation
#    19-Mar-2012 (CT) Adapt to `Boat_Class.name.ignore_case` now being `True`
#    ««revision-date»»···
#--

from _GTW.__test__.model import *

_test_code = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> SRM = scope.SRM
    >>> bc = SRM.Boat_Class ("Optimist", max_crew = 2)
    >>> b1 = SRM.Boat       (bc, 1, "AUT")
    >>> int (bc.pid), int (b1.pid)
    (1, 2)
    >>> scope.ems.pm.reserve (None, 100)
    100
    >>> b2 = SRM.Boat       (bc, 2, "AUT")
    >>> int (b2.pid)
    101
    >>> with expect_except (MOM.Error.Invariants) :
    ...     b3 = SRM.Boat       (bc, 2, "AUT") # doctest:+ELLIPSIS
    Invariants: The attribute values for ('left', 'sail_number', 'nation', 'sail_number_x') must be unique for each object
      The new definition of Boat SRM.Boat (('Optimist', 'SRM.Boat_Class'), '2', 'AUT', '') would clash with 1 existing entities
      Already existing:
        SRM.Boat (('Optimist', 'SRM.Boat_Class'), '2', 'AUT', '')
    >>> b3 = SRM.Boat       (bc, 3, "AUT")
    >>> b3.pid > b2.pid
    True

"""

__test__ = Scaffold.create_test_dict (_test_code)

### __END__ GTW.__test__.PID_Manager
