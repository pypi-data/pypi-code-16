# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Martin Glueck All rights reserved
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
#    GTW.__test__.Rollback
#
# Purpose
#    Test scope rollback
#
# Revision Dates
#    20-Oct-2010 (MG) Creation
#     2-Jul-2012 (MG) Test fixed due to new handling of exceptions (no
#                     automatic rollback if a Name_Clash occurs)
#    30-Jul-2012 (CT) Replace obsolete comment by tests showing `count`,
#                     `query_s`, and length of `uncommitted_changes`
#    25-Aug-2013 (CT) Add `test_create_m`, fix style
#     3-Aug-2015 (CT) Adapt to `Person._init_raw_default = True`
#    ««revision-date»»···
#--

_test_attr = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> PAP = scope.PAP
    >>> per = PAP.Person ("ln", "fn")
    >>> per.lifetime.start = "2010-01-01"
    >>> scope.commit ()

    >>> per
    PAP.Person ('ln', 'fn', '', '')
    >>> per.lifetime
    MOM.Date_Interval_lifetime ('2010-01-01')

    >>> per.lifetime.finish = "2010-02-01"
    >>> per.lifetime
    MOM.Date_Interval_lifetime ('2010-01-01', '2010-02-01')

    >>> scope.rollback ()

    >>> per.lifetime
    MOM.Date_Interval_lifetime ('2010-01-01')

"""

_test_create = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> PAP = scope.PAP
    >>> per = PAP.Person ("ln", "fn")
    >>> scope.commit     () ### 1

    >>> p   = PAP.Person ("ln", "fn1")

    >>> PAP.Person.count ### 1
    2
    >>> prepr (PAP.Person.query (sort_key = "pid").all ()) ### 1
    [PAP.Person ('ln', 'fn', '', ''), PAP.Person ('ln', 'fn1', '', '')]
    >>> len (scope.uncommitted_changes) ### 1
    1

    >>> with expect_except (MOM.Error.Invariants) :
    ...     per = PAP.Person ("ln", "fn")
    Invariants: The attribute values for ('last_name', 'first_name', 'middle_name', 'title') must be unique for each object
      The new definition of Person PAP.Person ('Ln', 'Fn', '', '') would clash with 1 existing entities
      Already existing:
        PAP.Person ('Ln', 'Fn', '', '')

    >>> PAP.Person.count ### 2
    2
    >>> prepr (PAP.Person.query (sort_key = "pid").all ()) ### 2
    [PAP.Person ('ln', 'fn', '', ''), PAP.Person ('ln', 'fn1', '', '')]
    >>> len (scope.uncommitted_changes) ### 2
    1

    >>> scope.rollback () ### 2

    >>> PAP.Person.count ### 3
    1
    >>> prepr (PAP.Person.query (sort_key = "pid").all ()) ### 3
    [PAP.Person ('ln', 'fn', '', '')]
    >>> len (scope.uncommitted_changes) ### 3
    0

    >>> scope.rollback () ### 4

    >>> prepr (PAP.Person.query (first_name = "fn1").all ())
    []

    >>> PAP.Person.count ### 5
    1
    >>> prepr ((PAP.Person.query (sort_key = "pid").all ())) ### 5
    [PAP.Person ('ln', 'fn', '', '')]
    >>> len (scope.uncommitted_changes) ### 5
    0


"""

_test_create_m = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> PAP = scope.PAP
    >>> p1 = PAP.Person ("Tanzer", "Christian", raw = True)
    >>> e1 = PAP.Email  ("tanzer@swing.co.at")
    >>> _  = PAP.Person_has_Email (p1, e1)
    >>> scope.commit ()

    >>> scope.MOM.Id_Entity.query (sort_key = Q.pid).all () ### 1
    [PAP.Person ('tanzer', 'christian', '', ''), PAP.Email ('tanzer@swing.co.at'), PAP.Person_has_Email (('tanzer', 'christian', '', ''), ('tanzer@swing.co.at', ))]

    >>> scope.rollback () ### 2

    >>> scope.MOM.Id_Entity.query (sort_key = Q.pid).all () ### 3
    [PAP.Person ('tanzer', 'christian', '', ''), PAP.Email ('tanzer@swing.co.at'), PAP.Person_has_Email (('tanzer', 'christian', '', ''), ('tanzer@swing.co.at', ))]

    >>> p2 = PAP.Person ("Schlatterbeck", "Ralf", raw = True)
    >>> e2 = PAP.Email  ("rsc@runtux.com")
    >>> _  = PAP.Person_has_Email (p2, e2)

    >>> scope.MOM.Id_Entity.query (sort_key = Q.pid).all () ### 4
    [PAP.Person ('tanzer', 'christian', '', ''), PAP.Email ('tanzer@swing.co.at'), PAP.Person_has_Email (('tanzer', 'christian', '', ''), ('tanzer@swing.co.at', )), PAP.Person ('schlatterbeck', 'ralf', '', ''), PAP.Email ('rsc@runtux.com'), PAP.Person_has_Email (('schlatterbeck', 'ralf', '', ''), ('rsc@runtux.com', ))]

    >>> scope.rollback () ### 5

    >>> scope.MOM.Id_Entity.query (sort_key = Q.pid).all () ### 6
    [PAP.Person ('tanzer', 'christian', '', ''), PAP.Email ('tanzer@swing.co.at'), PAP.Person_has_Email (('tanzer', 'christian', '', ''), ('tanzer@swing.co.at', ))]

"""

from   _GTW.__test__.model                      import *

__test__ = Scaffold.create_test_dict \
    ( dict
        ( test_attr       = _test_attr
        , test_create     = _test_create
        , test_create_m   = _test_create_m
        )
    )

### __END__ GTW.__test__.Rename
