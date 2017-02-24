# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.__test__.
# 
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.__test__.Team
#
# Purpose
#    Test creation and querying of SRM.Team
#
# Revision Dates
#    24-Jan-2012 (CT) Creation
#    19-Mar-2012 (CT) Adapt to `Boat_Class.name.ignore_case` now being `True`
#    12-Oct-2012 (CT) Adapt to repr change of `An_Entity`
#    ««revision-date»»···
#--

from   __future__  import unicode_literals

_test_code = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> SRM  = scope.SRM
    >>> bc   = SRM.Boat_Class ("Optimist", max_crew = 1)
    >>> rev0 = SRM.Regatta_Event (u"Teamrace", (u"20100918", ), raw = True)
    >>> reg0 = SRM.Regatta_C (rev0, boat_class = bc, raw = True)
    >>> rev1 = SRM.Regatta_Event (u"Teamrace", (u"20111015", ), raw = True)
    >>> reg1 = SRM.Regatta_C (rev1, boat_class = bc, raw = True)
    >>> t1  = SRM.Team (reg0, "Wien/1")
    >>> t2  = SRM.Team (reg0, "Wien/2")
    >>> t3  = SRM.Team (reg0, "Tirol/1")
    >>> t4  = SRM.Team (reg0, "Vorarlberg/1")
    >>> t5  = SRM.Team (reg1, "Wien/3")
    >>> t6  = SRM.Team (reg1, "Wien/4")
    >>> t7  = SRM.Team (reg1, "Tirol/2")
    >>> t8  = SRM.Team (reg1, "Vorarlberg/2")

    >>> scope.commit ()

    >>> t1.regatta.event.date.start
    datetime.date(2010, 9, 18)

    >>> prepr (SRM.Team.query ().order_by (TFL.Sorted_By ("name")).all ())
    [SRM.Team ((('teamrace', ('2010-09-18', '2010-09-18')), ('optimist', )), 'tirol/1'), SRM.Team ((('teamrace', ('2011-10-15', '2011-10-15')), ('optimist', )), 'tirol/2'), SRM.Team ((('teamrace', ('2010-09-18', '2010-09-18')), ('optimist', )), 'vorarlberg/1'), SRM.Team ((('teamrace', ('2011-10-15', '2011-10-15')), ('optimist', )), 'vorarlberg/2'), SRM.Team ((('teamrace', ('2010-09-18', '2010-09-18')), ('optimist', )), 'wien/1'), SRM.Team ((('teamrace', ('2010-09-18', '2010-09-18')), ('optimist', )), 'wien/2'), SRM.Team ((('teamrace', ('2011-10-15', '2011-10-15')), ('optimist', )), 'wien/3'), SRM.Team ((('teamrace', ('2011-10-15', '2011-10-15')), ('optimist', )), 'wien/4')]

    >>> scope.rollback ()

    >>> prepr (SRM.Team.query (Q.regatta.event.date.start == t1.regatta.event.date.start).order_by (TFL.Sorted_By ("name")).all ())
    [SRM.Team ((('teamrace', ('2010-09-18', '2010-09-18')), ('optimist', )), 'tirol/1'), SRM.Team ((('teamrace', ('2010-09-18', '2010-09-18')), ('optimist', )), 'vorarlberg/1'), SRM.Team ((('teamrace', ('2010-09-18', '2010-09-18')), ('optimist', )), 'wien/1'), SRM.Team ((('teamrace', ('2010-09-18', '2010-09-18')), ('optimist', )), 'wien/2')]

    >>> scope.rollback ()

    >>> prepr (SRM.Team.query ().order_by ("-left.left.date.start", "name").all ())
    [SRM.Team ((('teamrace', ('2011-10-15', '2011-10-15')), ('optimist', )), 'tirol/2'), SRM.Team ((('teamrace', ('2011-10-15', '2011-10-15')), ('optimist', )), 'vorarlberg/2'), SRM.Team ((('teamrace', ('2011-10-15', '2011-10-15')), ('optimist', )), 'wien/3'), SRM.Team ((('teamrace', ('2011-10-15', '2011-10-15')), ('optimist', )), 'wien/4'), SRM.Team ((('teamrace', ('2010-09-18', '2010-09-18')), ('optimist', )), 'tirol/1'), SRM.Team ((('teamrace', ('2010-09-18', '2010-09-18')), ('optimist', )), 'vorarlberg/1'), SRM.Team ((('teamrace', ('2010-09-18', '2010-09-18')), ('optimist', )), 'wien/1'), SRM.Team ((('teamrace', ('2010-09-18', '2010-09-18')), ('optimist', )), 'wien/2')]

    >>> scope.rollback ()

    >>> prepr (SRM.Team.query ().order_by ("regatta.event.date.-start", "name").all ())
    [SRM.Team ((('teamrace', ('2011-10-15', '2011-10-15')), ('optimist', )), 'tirol/2'), SRM.Team ((('teamrace', ('2011-10-15', '2011-10-15')), ('optimist', )), 'vorarlberg/2'), SRM.Team ((('teamrace', ('2011-10-15', '2011-10-15')), ('optimist', )), 'wien/3'), SRM.Team ((('teamrace', ('2011-10-15', '2011-10-15')), ('optimist', )), 'wien/4'), SRM.Team ((('teamrace', ('2010-09-18', '2010-09-18')), ('optimist', )), 'tirol/1'), SRM.Team ((('teamrace', ('2010-09-18', '2010-09-18')), ('optimist', )), 'vorarlberg/1'), SRM.Team ((('teamrace', ('2010-09-18', '2010-09-18')), ('optimist', )), 'wien/1'), SRM.Team ((('teamrace', ('2010-09-18', '2010-09-18')), ('optimist', )), 'wien/2')]


"""

from _GTW.__test__.model import *

__test__ = Scaffold.create_test_dict \
    ( dict
        ( normal  = _test_code
        )
    )

### __END__ GTW.__test__.Team
