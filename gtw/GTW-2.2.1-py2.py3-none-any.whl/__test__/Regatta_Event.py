# -*- coding: utf-8 -*-
# Copyright (C) 2010-2014 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package GTW.__test__.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.__test__.Regatta_Event
#
# Purpose
#    Test Regatta_Event creation and querying
#
# Revision Dates
#    30-Apr-2010 (CT) Creation
#    14-Nov-2011 (CT) Add tests for `query` and `query_s` with `sort_key`
#    12-Oct-2012 (CT) Adapt to repr change of `An_Entity`
#    29-Jul-2013 (CT) Add tests for `set` of `name`
#    ««revision-date»»···
#--

from   __future__               import print_function

_test_code = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> SRM = scope.SRM
    >>> RE  = SRM.Regatta_Event
    >>> rev = RE (u"Himmelfahrt", ("20080501", ), raw = True)
    >>> rev.pid
    1
    >>> prepr (rev.epk_raw)
    ('Himmelfahrt', (('finish', '2008-05-01'), ('start', '2008-05-01')), 'SRM.Regatta_Event')

    >>> RE.instance (* rev.epk_raw, raw = True)
    SRM.Regatta_Event ('himmelfahrt', ('2008-05-01', '2008-05-01'))
    >>> RE.instance (* rev.epk)
    SRM.Regatta_Event ('himmelfahrt', ('2008-05-01', '2008-05-01'))

    >>> sort_key = TFL.Sorted_By ("-date.start", "name")

    >>> print (sort_key)
    <Sorted_By: Descending-Getter function for `.date.start`, Getter function for `.name`>
    >>> print (RE.E_Type.sort_key_pm (sort_key))
    <Sorted_By: Getter function for `.relevant_root.type_name`, <Sorted_By: Descending-Getter function for `.date.start`, Getter function for `.name`>>

    >>> list (RE.query (sort_key = sort_key))
    [SRM.Regatta_Event ('himmelfahrt', ('2008-05-01', '2008-05-01'))]
    >>> list (RE.query_s (sort_key = sort_key))
    [SRM.Regatta_Event ('himmelfahrt', ('2008-05-01', '2008-05-01'))]

    >>> scope.commit ()

    >>> rev.set (name = "himmelfahrt")
    0

    >>> rev.set_raw (name = "Himmelfahrt")
    0

    >>> rev.set (name = "Himmelfahrt")
    0

    >>> RE.query ().all ()
    [SRM.Regatta_Event ('himmelfahrt', ('2008-05-01', '2008-05-01'))]

    >>> for x in RE.query () :
    ...     print (x.ui_display)
    Himmelfahrt 2008-05-01

    >>> rev.set_raw (name = "Himmelfahrtskommando")
    1

    >>> RE.query ().all ()
    [SRM.Regatta_Event ('himmelfahrtskommando', ('2008-05-01', '2008-05-01'))]

    >>> rev.set (name = "Himmelfahrt")
    1

"""

from _GTW.__test__.model import *

__test__ = Scaffold.create_test_dict (_test_code)

### __END__ GTW.__test__.Regatta_Event
