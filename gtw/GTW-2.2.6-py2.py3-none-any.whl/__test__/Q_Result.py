# -*- coding: utf-8 -*-
# Copyright (C) 2010-2016 Martin Glueck All rights reserved
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
#    GTW.__test__.Q_Result
#
# Purpose
#    Tests for low level Q_Result functions.
#
# Revision Dates
#     1-Sep-2010 (MG) Creation
#     2-Sep-2010 (CT) Changed to test `HPS` backend, too
#     2-Sep-2010 (CT) Test for `set` of `Q.lifetime.finish` added
#     2-Sep-2010 (MG) More tests added
#    19-Jul-2011 (MG) New tests for `RAW` queries added
#    22-Jul-2011 (MG) Tests for `LOWER` added
#    26-Jul-2011 (CT) Tests (q1, q2, q3) for `attrs` combined with `count`
#                     and `all` added
#    16-Sep-2011 (MG) `attrs_query` test added
#    12-Oct-2012 (CT) Adapt to repr change of `An_Entity`
#     3-Aug-2015 (CT) Remove type-cast to `scope.MOM.Date_Interval`
#     3-Aug-2015 (CT) Adapt to `Person._init_raw_default = True`
#    ««revision-date»»···
#--

from __future__ import print_function, unicode_literals

_q_result = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> PAP = scope.PAP
    >>> _   = PAP.Person  ("LN 1", "FN 1", lifetime = ("2010-01-01", ))
    >>> _   = PAP.Person  ("LN 2", "FN 2", title = "Dr.")
    >>> p   = PAP.Person  ("LN 3", "FN 3", lifetime = ("2010-03-01", ))
    >>> _   = PAP.Person  ("LN 4", "FN 4", title = "DI")
    >>> _   = PAP.Person  ("LN 5", "FN 5", title = "DI")
    >>> a   = PAP.Address ("S", "C", "Z", "C")
    >>> pha = PAP.Person_has_Address (p, a)

    >>> scope.commit ()

    >>> q   = PAP.Person.query ()
    >>> print (q.count ())
    5
    >>> len (q.all ())
    5
    >>> print (q.attr ("first_name").count ())
    5
    >>> prepr (sorted (q.attr ("first_name")))
    ['fn 1', 'fn 2', 'fn 3', 'fn 4', 'fn 5']
    >>> print (q.attrs (Q.first_name).count ())
    5
    >>> prepr (sorted (q.attrs (Q.first_name)))
    [('fn 1',), ('fn 2',), ('fn 3',), ('fn 4',), ('fn 5',)]

    >>> prepr (sorted (q.attr (Q.lifetime.start).distinct (), key = lambda v : (v.__class__.__name__, v)))
    [None, datetime.date(2010, 1, 1), datetime.date(2010, 3, 1)]
    >>> prepr (sorted (q.attrs (Q.first_name, Q.lifetime.start, "last_name")))
    [('fn 1', datetime.date(2010, 1, 1), 'ln 1'), ('fn 2', None, 'ln 2'), ('fn 3', datetime.date(2010, 3, 1), 'ln 3'), ('fn 4', None, 'ln 4'), ('fn 5', None, 'ln 5')]

    ### ??? >>> scope.commit ()
    >>> if hasattr (scope.ems.session, "expunge") : scope.ems.session.expunge ()

    >>> p = PAP.Person.query (pid = 1).one ()
    >>> p.lifetime # 1
    MOM.Date_Interval_lifetime ('2010-01-01')

    >>> p.lifetime.finish = datetime.date (2010, 12, 31)

    >>> p.lifetime # 2
    MOM.Date_Interval_lifetime ('2010-01-01', '2010-12-31')
    >>> first (PAP.Person.query (pid = 1).attrs (Q.lifetime.start, Q.lifetime.finish))
    (datetime.date(2010, 1, 1), datetime.date(2010, 12, 31))
    >>> first (PAP.Person.query (pid = 1).attr (Q.lifetime))
    MOM.Date_Interval_lifetime ('2010-01-01', '2010-12-31')

    >>> prepr (sorted (PAP.Person.query (pid = 1).attrs ("first_name", Q.lifetime)))
    [('fn 1', MOM.Date_Interval_lifetime ('2010-01-01', '2010-12-31'))]

    >>> prepr (sorted (PAP.Person.query (pid = 1).attrs (Q.RAW.first_name, Q.lifetime)))
    [('Fn 1', MOM.Date_Interval_lifetime ('2010-01-01', '2010-12-31'))]

    >>> scope.rollback ()

    >>> prepr (sorted (PAP.Person_has_Address.query ().attr ("left")))
    [PAP.Person ('ln 3', 'fn 3', '', '')]
    >>> prepr (sorted (PAP.Person_has_Address.query ().attr ("person")))
    [PAP.Person ('ln 3', 'fn 3', '', '')]
    >>> prepr (sorted (PAP.Person_has_Address.query ().attrs ("right")))
    [(PAP.Address ('s', 'c', 'z', 'c'),)]
    >>> prepr (sorted (PAP.Person_has_Address.query ().attrs ("address")))
    [(PAP.Address ('s', 'c', 'z', 'c'),)]
    >>> prepr (sorted (PAP.Person_has_Address.query ().attrs ("left", "address")))
    [(PAP.Person ('ln 3', 'fn 3', '', ''), PAP.Address ('s', 'c', 'z', 'c'))]
    >>> prepr (sorted (PAP.Person_has_Address.query ().attrs ("person", "address")))
    [(PAP.Person ('ln 3', 'fn 3', '', ''), PAP.Address ('s', 'c', 'z', 'c'))]

    >>> prepr (PAP.Person.query_1 (Q.last_name.STARTSWITH ("ln")))
    (2, None)
    >>> prepr (PAP.Person.query_1 (Q.last_name.STARTSWITH ("ln 1")))
    (1, PAP.Person ('ln 1', 'fn 1', '', ''))
    >>> prepr (PAP.Person.query_1 (Q.last_name.STARTSWITH ("ln 42")))
    (0, None)

    >>> q0  = PAP.Person.query (Q.RAW.title.STARTSWITH ("D"))
    >>> q1  = q0.distinct ()
    >>> q1.count ()
    3

    >>> q9  = q0.attrs (Q.RAW.title, allow_duplicates = True)
    >>> prepr (sorted (q9.all ()))
    [('DI',), ('DI',), ('Dr.',)]
    >>> q9.count ()
    3

    >>> q10 = q0.attrs (Q.RAW.title)
    >>> prepr (sorted (q10.all ()))
    [('DI',), ('Dr.',)]
    >>> q10.count ()
    2

    >>> q2  = q1.attrs (Q.RAW.title).order_by (Q.RAW.title)
    >>> q3  = q1.attrs (Q.RAW.title).order_by (Q.RAW.title)
    >>> prepr (sorted (q2.all ()))
    [('DI',), ('Dr.',)]
    >>> q2.count ()
    2
    >>> q3.count ()
    2
    >>> prepr (q2.all ())
    [('DI',), ('Dr.',)]
    >>> prepr (q3.all ())
    [('DI',), ('Dr.',)]

    >>> q4  = q2.distinct ()
    >>> q5  = q3.distinct ()
    >>> prepr (q4.all ())
    [('DI',), ('Dr.',)]
    >>> q4.count ()
    2
    >>> q5.count ()
    2
    >>> prepr (q4.all ())
    [('DI',), ('Dr.',)]
    >>> prepr (q5.all ())
    [('DI',), ('Dr.',)]

    >>> prepr (q2.first ())
    ('DI',)
    >>> prepr (q3.limit (1).all ())
    [('DI',)]

    >>> prepr (sorted (q0.all (), key = PAP.Person.sort_key))
    [PAP.Person ('ln 2', 'fn 2', '', 'dr.'), PAP.Person ('ln 4', 'fn 4', '', 'di'), PAP.Person ('ln 5', 'fn 5', '', 'di')]
    >>> prepr (sorted ((t, int (c)) for (t, c) in q0.attrs (Q.title, Q.SUM (1), allow_duplicates = True).group_by (Q.title)))
    [('di', 2), ('dr.', 1)]

    >>> qy = PAP.Person.AQ.lifetime.start.AC ("2010")
    >>> qy
    Q.lifetime.start.between (datetime.date(2010, 1, 1), datetime.date(2010, 12, 31))
    >>> qm = PAP.Person.AQ.lifetime.start.AC ("2010/01")
    >>> qm
    Q.lifetime.start.between (datetime.date(2010, 1, 1), datetime.date(2010, 1, 31))

    >>> prepr (PAP.Person.query_s (qy).attrs (Q.last_name, Q.lifetime.start).all ())
    [('ln 1', datetime.date(2010, 1, 1)), ('ln 3', datetime.date(2010, 3, 1))]
    >>> prepr (PAP.Person.query_s (qm).attrs (Q.last_name, Q.lifetime.start).all ())
    [('ln 1', datetime.date(2010, 1, 1))]

    >>> _   = PAP.Person  ("LN 1", "FN 2", title = "DI")
    >>> _   = PAP.Person  ("LN 4", "FN 1", title = "DI")
    >>> _   = PAP.Person  ("LN 4", "FN 2", title = "DI")
    >>> _   = PAP.Person  ("LN 5", "FN 2", title = "DI")

    >>> q = PAP.Person.query_s ()
    >>> qfn = PAP.Person.AQ.first_name
    >>> qln = PAP.Person.AQ.last_name

    >>> print (q.count ())
    9
    >>> prepr (sorted (q.attrs ("first_name", "last_name")))
    [('fn 1', 'ln 1'), ('fn 1', 'ln 4'), ('fn 2', 'ln 1'), ('fn 2', 'ln 2'), ('fn 2', 'ln 4'), ('fn 2', 'ln 5'), ('fn 3', 'ln 3'), ('fn 4', 'ln 4'), ('fn 5', 'ln 5')]

    >>> qin = qfn.IN (["FN 1", "FN 5", "LN 3"])
    >>> prepr (qin.args)
    (['fn 1', 'fn 5', 'ln 3'],)

    >>> prepr (sorted (q.filter (qfn.IN (["FN 1", "FN 5", "LN 3"])).attrs ("first_name", "last_name")))
    [('fn 1', 'ln 1'), ('fn 1', 'ln 4'), ('fn 5', 'ln 5')]

    >>> prepr (sorted (q.filter (qfn.IN (["FN 1", "FN 2"])).attrs ("first_name", "last_name")))
    [('fn 1', 'ln 1'), ('fn 1', 'ln 4'), ('fn 2', 'ln 1'), ('fn 2', 'ln 2'), ('fn 2', 'ln 4'), ('fn 2', 'ln 5')]

    >>> prepr (sorted (q.filter (qln.IN (["LN 4", "LN 5"])).attrs ("first_name", "last_name")))
    [('fn 1', 'ln 4'), ('fn 2', 'ln 4'), ('fn 2', 'ln 5'), ('fn 4', 'ln 4'), ('fn 5', 'ln 5')]

"""

_attrs_query = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> PAP = scope.PAP

    >>> _   = PAP.Person  ("LN 1", "FN 1", lifetime = ("2010-01-01", ))
    >>> _   = PAP.Person  ("LN 2", "FN 2", lifetime = ("2010-01-10", ), title = "Dr.")
    >>> p   = PAP.Person  ("LN 3", "FN 3", lifetime = ("2010-01-03", ))
    >>> _   = PAP.Person  ("LN 4", "FN 4", lifetime = ("2010-01-16", ), title = "DI")
    >>> _   = PAP.Person  ("LN 5", "FN 5", lifetime = ("2010-02-01", ), title = "DI")

    >>> scope.commit ()

    >>> q   = PAP.Person.query ()
    >>> prepr (q.attr  ("last_name").order_by (Q.last_name).all ())
    ['ln 1', 'ln 2', 'ln 3', 'ln 4', 'ln 5']
    >>> q.attr  ("lifetime.start").order_by (Q.lifetime.start).all ()
    [datetime.date(2010, 1, 1), datetime.date(2010, 1, 3), datetime.date(2010, 1, 10), datetime.date(2010, 1, 16), datetime.date(2010, 2, 1)]

    >>> q1  = q.attrs ("last_name", "first_name")
    >>> prepr (q1.order_by (Q.last_name).all ())
    [('ln 1', 'fn 1'), ('ln 2', 'fn 2'), ('ln 3', 'fn 3'), ('ln 4', 'fn 4'), ('ln 5', 'fn 5')]

    >>> q2  = q.attrs (Q.last_name, Q.lifetime.start)
    >>> prepr (q2.order_by (Q.lifetime.start).all ())
    [('ln 1', datetime.date(2010, 1, 1)), ('ln 3', datetime.date(2010, 1, 3)), ('ln 2', datetime.date(2010, 1, 10)), ('ln 4', datetime.date(2010, 1, 16)), ('ln 5', datetime.date(2010, 2, 1))]

"""

_raw_query = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> p1   = scope.PAP.Person  ("LN 1", "FN 1", lifetime = ("2010-01-01", ))
    >>> p  = scope.PAP.Person  ("LN 2", "FN 2")
    >>> p   = scope.PAP.Person  ("LN 3", "FN 3", lifetime = ("2010-01-03", ))
    >>> p   = scope.PAP.Person  ("Lname 4", "Fn 3")
    >>> a   = scope.PAP.Address ("S", "C", "Z", "C")
    >>> pha = scope.PAP.Person_has_Address (p, a)

    >>> p1.last_cid
    1
    >>> scope.commit ()
    >>> prepr (scope.PAP.Person.query (Q.RAW.last_cid == "1").all ())
    [PAP.Person ('ln 1', 'fn 1', '', '')]
    >>> prepr (scope.PAP.Person.query (Q.RAW.pid == "1").all ())
    [PAP.Person ('ln 1', 'fn 1', '', '')]
    >>> prepr (scope.PAP.Person.query (Q.RAW.last_name == "LN 1").all ())
    [PAP.Person ('ln 1', 'fn 1', '', '')]
    >>> prepr (scope.PAP.Person.query (Q.RAW.lifetime.start == "2010-01-01").all ())
    [PAP.Person ('ln 1', 'fn 1', '', '')]

    >>> prepr (scope.PAP.Person.query (Q.RAW.last_name.STARTSWITH ("LN")).order_by (Q.last_name).all ())
    [PAP.Person ('ln 1', 'fn 1', '', ''), PAP.Person ('ln 2', 'fn 2', '', ''), PAP.Person ('ln 3', 'fn 3', '', '')]
    >>> prepr (scope.PAP.Person.query (Q.RAW.last_name.STARTSWITH ("Ln")).order_by (Q.last_name).all ())
    [PAP.Person ('lname 4', 'fn 3', '', '')]


"""

_destroy_test = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> p = scope.PAP.Person ("ln", "fn")
    >>> for c in scope.uncommitted_changes :
    ...     prepr (c)
    <Create PAP.Person ('Ln', 'Fn', '', '', 'PAP.Person'), new-values = {'last_cid' : '1'}>
    >>> p.destroy ()
    >>> for c in scope.uncommitted_changes :
    ...     prepr (c)
    <Create PAP.Person ('Ln', 'Fn', '', '', 'PAP.Person'), new-values = {'last_cid' : '1'}>
    <Destroy PAP.Person ('Ln', 'Fn', '', '', 'PAP.Person'), old-values = {'last_cid' : '1'}>
    """

_copy_test = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> p1 = scope.PAP.Person ("ln", "fn")
    >>> p2 = p1.copy ("ln 2", "gn 2")
    >>> prepr ((p1.last_cid, p2.last_cid))
    (1, 3)
    >>> scope.commit ()
    >>> prepr ((p1.last_cid, p2.last_cid))
    (1, 3)
    """

from   _GTW.__test__.model import *
from   _TFL.predicate      import first

import datetime

__test__ = Scaffold.create_test_dict \
    ( dict
        ( q_result    = _q_result
        , raw_query   = _raw_query
        , attrs_query = _attrs_query
        , destroy     = _destroy_test
        , copy        = _copy_test
        )
    )

### __END__ GTW.__test__.Q_Result
