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
#    GTW.__test__.Query_Sorted_By
#
# Purpose
#    Test sorting of queries
#
# Revision Dates
#    30-Apr-2010 (MG) Creation
#     7-May-2010 (MG) `sail_number` is now a numeric string
#    10-Aug-2010 (MG) Additional test added
#    10-Aug-2010 (MG) Test changed to allow different backends
#    16-Aug-2010 (MG) Test fixed
#    20-Dec-2010 (CT) Python 2.7 compatibility
#    19-Mar-2012 (CT) Adapt to `Boat_Class.name.ignore_case` now being `True`
#    12-Oct-2012 (CT) Adapt to repr change of `An_Entity`
#    30-Jul-2013 (CT) Rename to `Query_Sorted_By`, enable `HPS`
#    ««revision-date»»···
#--

from   __future__  import print_function, unicode_literals

_composite = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> EVT = scope.EVT
    >>> SWP = scope.SWP
    >>> p1 = SWP.Page ("event-1-text", text = "Text for the 1. event")
    >>> p2 = SWP.Page ("event-2-text", text = "Text for the 2. event")
    >>> e1 = EVT.Event (p1.epk_raw, ("1.2.2010", ), raw = True)
    >>> e2 = EVT.Event (p2.epk_raw, ("1.1.2010", ), raw = True)
    >>> q = EVT.Event.query ().order_by (TFL.Sorted_By (Q.date.start))
    >>> for e in q.all () : print (e)
    (('event-2-text', ), ('2010-01-01', ), (), '')
    (('event-1-text', ), ('2010-02-01', ), (), '')

    >>> for e in EVT.Event.query (sort_key = EVT.Event.sorted_by) :
    ...     print (e)
    (('event-2-text', ), ('2010-01-01', ), (), '')
    (('event-1-text', ), ('2010-02-01', ), (), '')

    >>> for e in EVT.Event.query (sort_key = TFL.Sorted_By ("-date.start")) :
    ...     print (e)
    (('event-1-text', ), ('2010-02-01', ), (), '')
    (('event-2-text', ), ('2010-01-01', ), (), '')

"""

_link1_role = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> EVT = scope.EVT
    >>> SWP = scope.SWP
    >>> p1 = SWP.Page ("event-1-text", text = "Text for the 1. event")
    >>> p2 = SWP.Page ("event-2-text", text = "Text for the 2. event")
    >>> e1 = EVT.Event (p1.epk_raw, ("1.2.2010", ), raw = True)
    >>> e2 = EVT.Event (p2.epk_raw, ("1.1.2010", ), raw = True)
    >>> q = EVT.Event_occurs.query_s ()
    >>> for e in q.all () : print (e) ### default sort order
    ((('event-2-text', ), ('2010-01-01', ), (), ''), '2010-01-01', ())
    ((('event-1-text', ), ('2010-02-01', ), (), ''), '2010-02-01', ())
    >>> q = EVT.Event_occurs.query ().order_by (TFL.Sorted_By ("-event.date.start"))
    >>> for e in q.all () : print (e) ### sorted by descending date
    ((('event-1-text', ), ('2010-02-01', ), (), ''), '2010-02-01', ())
    ((('event-2-text', ), ('2010-01-01', ), (), ''), '2010-01-01', ())


"""

_link2_link1 = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> PAP = scope.PAP
    >>> SRM = scope.SRM
    >>> bc  = SRM.Boat_Class ("Optimist", max_crew = 1)
    >>> b   = SRM.Boat.instance_or_new ('Optimist', u"1107", "AUT", raw = True)
    >>> p   = PAP.Person.instance_or_new ("Tanzer", "Christian")
    >>> s   = SRM.Sailor.instance_or_new (p.epk_raw, nation = "AUT", mna_number = "29676", raw = True) ### 1
    >>> rev = SRM.Regatta_Event (u"Himmelfahrt", ("20080501", ), raw = True)
    >>> reg = SRM.Regatta_C     (rev.epk_raw, boat_class = bc.epk_raw, raw = True)
    >>> bir = SRM.Boat_in_Regatta (b.epk_raw, reg.epk_raw, skipper = s.epk_raw, raw = True)

    >>> rev = SRM.Regatta_Event (u"Himmelfahrt", ("20090521", ), raw = True)
    >>> reg = SRM.Regatta_C     (rev.epk_raw, boat_class = bc.epk_raw, raw = True)
    >>> bir = SRM.Boat_in_Regatta (b.epk_raw, reg.epk_raw, skipper = s.epk_raw, raw = True)

    >>> rev = SRM.Regatta_Event (u"Himmelfahrt", ("20100513", ), raw = True)
    >>> reg = SRM.Regatta_C     (rev.epk_raw, boat_class = bc.epk_raw, raw = True)
    >>> bir = SRM.Boat_in_Regatta (b.epk_raw, reg.epk_raw, skipper = s.epk_raw, raw = True)

    >>> q = scope.SRM.Boat_in_Regatta.query ()
    >>> for r in q.order_by (Q.right.left.date.start) : print (r)
    ((('optimist', ), 1107, 'AUT', ''), (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', )))
    ((('optimist', ), 1107, 'AUT', ''), (('himmelfahrt', ('2009-05-21', '2009-05-21')), ('optimist', )))
    ((('optimist', ), 1107, 'AUT', ''), (('himmelfahrt', ('2010-05-13', '2010-05-13')), ('optimist', )))
    >>> q = scope.SRM.Boat_in_Regatta.query ()
    >>> for r in q.order_by (TFL.Sorted_By ("-right.left.date.start")) : print (r)
    ((('optimist', ), 1107, 'AUT', ''), (('himmelfahrt', ('2010-05-13', '2010-05-13')), ('optimist', )))
    ((('optimist', ), 1107, 'AUT', ''), (('himmelfahrt', ('2009-05-21', '2009-05-21')), ('optimist', )))
    ((('optimist', ), 1107, 'AUT', ''), (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', )))

    Unfortunately, we cannot use `.attrs (* qa)` because
    * `HPS` doesn't currently support expressions for `attrs`
    * PostgreSQL returns floating point numbers for the expression `qd`
    >>> qd = Q.right.left.date.finish.day - Q.right.left.date.start.month
    >>> qa = (Q.right.left, qd, Q.right.left.date.start.year)
    >>> for x in q.order_by (qd) :
    ...     print (tuple (q (x) for q in qa))
    (SRM.Regatta_Event ('himmelfahrt', ('2008-05-01', '2008-05-01')), -4, 2008)
    (SRM.Regatta_Event ('himmelfahrt', ('2010-05-13', '2010-05-13')), 8, 2010)
    (SRM.Regatta_Event ('himmelfahrt', ('2009-05-21', '2009-05-21')), 16, 2009)

"""

_query_attr = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> PAP  = scope.PAP
    >>> SRM  = scope.SRM
    >>> bc   = SRM.Boat_Class ("Optimist", max_crew = 1)
    >>> b    = SRM.Boat.instance_or_new ('Optimist', u"1107", "AUT", raw = True)
    >>> p    = PAP.Person.instance_or_new ("Tanzer", "Christian")
    >>> s    = SRM.Sailor.instance_or_new (p.epk_raw, nation = "AUT", mna_number = "29676", raw = True) ### 1
    >>> rev = SRM.Regatta_Event (u"Himmelfahrt", ("20080501", ), raw = True)
    >>> reg = SRM.Regatta_C     (rev.epk_raw, boat_class = bc.epk_raw, raw = True)
    >>> bir = SRM.Boat_in_Regatta (b.epk_raw, reg.epk_raw, skipper = s.epk_raw, raw = True)

    >>> rev = SRM.Regatta_Event (u"Himmelfahrt", ("20090521", ), raw = True)
    >>> reg = SRM.Regatta_C     (rev.epk_raw, boat_class = bc.epk_raw, raw = True)
    >>> bir = SRM.Boat_in_Regatta (b.epk_raw, reg.epk_raw, skipper = s.epk_raw, raw = True)

    >>> rev = SRM.Regatta_Event (u"Himmelfahrt", ("20100513", ), raw = True)
    >>> reg = SRM.Regatta_C     (rev.epk_raw, boat_class = bc.epk_raw, raw = True)
    >>> bir = SRM.Boat_in_Regatta (b.epk_raw, reg.epk_raw, skipper = s.epk_raw, raw = True)

    >>> q = SRM.Regatta_C.query ()
    >>> for r in q.order_by (Q.event.date.start) : prepr (r.year, r)
    2008 SRM.Regatta_C (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', ))
    2009 SRM.Regatta_C (('himmelfahrt', ('2009-05-21', '2009-05-21')), ('optimist', ))
    2010 SRM.Regatta_C (('himmelfahrt', ('2010-05-13', '2010-05-13')), ('optimist', ))
    >>> for r in q.order_by (TFL.Sorted_By ("-event.date.start")) : prepr (r.year, r)
    2010 SRM.Regatta_C (('himmelfahrt', ('2010-05-13', '2010-05-13')), ('optimist', ))
    2009 SRM.Regatta_C (('himmelfahrt', ('2009-05-21', '2009-05-21')), ('optimist', ))
    2008 SRM.Regatta_C (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', ))

"""

if 0 :
    import warnings
    from sqlalchemy import exc as sa_exc
    warnings.filterwarnings \
        (action = "error", category = sa_exc.SAWarning)

from _GTW.__test__.model import *
from _MOM.import_MOM     import Q

__test__ = Scaffold.create_test_dict \
    ( dict
        ( composite       = _composite
        , link1_role      = _link1_role
        , link2_link1     = _link2_link1
        , query_attr      = _query_attr
        )
    )

### __END__ GTW.__test__.Query_Sorted_By
