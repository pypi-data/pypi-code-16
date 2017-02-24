# -*- coding: utf-8 -*-
# Copyright (C) 2010-2014 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package MOM.__test__.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    MOM.__test__.Sailor
#
# Purpose
#    Test SRM.Sailor creation and querying
#
# Revision Dates
#    27-Apr-2010 (CT) Creation
#     9-Sep-2011 (CT) Queries for `p` and `p.pid` added
#     9-Sep-2011 (CT) Tests for `Q.left.pid` added
#    ««revision-date»»···
#--

_test_code = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> PAP = scope.PAP
    >>> SRM = scope.SRM
    >>> p = PAP.Person.instance_or_new ("Tanzer", "Christian")
    >>> p
    PAP.Person ('tanzer', 'christian', '', '')
    >>> s = SRM.Sailor.instance_or_new (p, nation = "AUT", raw = True) ### 1
    >>> s
    SRM.Sailor (('tanzer', 'christian', '', ''), 'AUT', None, '')

    >>> _ = s.set (mna_number = 29676)
    >>> s
    SRM.Sailor (('tanzer', 'christian', '', ''), 'AUT', 29676, '')
    >>> SRM.Sailor.instance (p.epk_raw, nation = "AUT", mna_number = "29676", raw = True)
    SRM.Sailor (('tanzer', 'christian', '', ''), 'AUT', 29676, '')
    >>> SRM.Sailor.instance_or_new (p.epk_raw, nation = "AUT", mna_number = "29676", raw = True)
    SRM.Sailor (('tanzer', 'christian', '', ''), 'AUT', 29676, '')
    >>> SRM.Sailor.instance_or_new (p.epk_raw, s.nation, s.mna_number)
    SRM.Sailor (('tanzer', 'christian', '', ''), 'AUT', 29676, '')

    >>> prepr (SRM.Sailor.query (left = p).all ())
    [SRM.Sailor (('tanzer', 'christian', '', ''), 'AUT', 29676, '')]
    >>> prepr (SRM.Sailor.query (left = p.pid).all ())
    [SRM.Sailor (('tanzer', 'christian', '', ''), 'AUT', 29676, '')]
    >>> prepr (SRM.Sailor.query (Q.left == p).all ())
    [SRM.Sailor (('tanzer', 'christian', '', ''), 'AUT', 29676, '')]
    >>> prepr (SRM.Sailor.query (Q.left == p.pid).all ())
    [SRM.Sailor (('tanzer', 'christian', '', ''), 'AUT', 29676, '')]
    >>> prepr (SRM.Sailor.query (Q.left.pid == p.pid).all ())
    [SRM.Sailor (('tanzer', 'christian', '', ''), 'AUT', 29676, '')]
    >>> prepr (SRM.Sailor.query (Q.left.pid == p).all ())
    [SRM.Sailor (('tanzer', 'christian', '', ''), 'AUT', 29676, '')]

"""

from _GTW.__test__.model import *

__test__ = Scaffold.create_test_dict (_test_code)

### __END__ MOM.__test__.Sailor
