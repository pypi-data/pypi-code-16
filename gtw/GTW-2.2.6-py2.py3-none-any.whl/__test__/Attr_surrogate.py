# -*- coding: utf-8 -*-
# Copyright (C) 2013-2017 Mag. Christian Tanzer All rights reserved
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
#    GTW.__test__.Attr_surrogate
#
# Purpose
#    Test surrogate attributes
#
# Revision Dates
#     5-Jun-2013 (CT) Creation
#     1-Aug-2013 (CT) Add `test_no_reuse`
#    24-Feb-2017 (CT) Import `MOM.Inspect`, not `MOM.inspect`
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _GTW.__test__.model import *
from   _MOM.Inspect        import children_trans_iter

import _GTW._OMP._Auth.import_Auth

_test_map = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> ET_Cert = scope.Auth.Certificate.E_Type
    >>> for a in ET_Cert.q_able :
    ...     print (repr (a))
    Email `email`
    Date_Time_Interval `validity`
    String `desc`
    Date-Time `revocation_date`
    Rev_Ref `creation`
    Boolean `electric`
    Rev_Ref `last_change`
    Int `last_cid`
    Surrogate `pid`
    String `type_name`
    Surrogate `cert_id`
    None `pem`
    Boolean `alive`
    Link_Ref_List `events`

    >>> sorted ((k, t.type_name) for k, t in pyk.iteritems (scope.app_type.surrogate_t_map))
    [(1, 'MOM.Id_Entity'), (2, 'MOM.MD_Change'), (3, 'Auth.Certificate')]

    >>> sorted ((str (k), a) for k, a in pyk.iteritems (scope.app_type.surrogate_map))
    [('Auth.Certificate.cert_id', Surrogate `cert_id`), ('MOM.Id_Entity.pid', Surrogate `pid`), ('MOM.MD_Change.cid', Surrogate `cid`)]

"""

_test_no_reuse = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> SRM = scope.SRM
    >>> bc = SRM.Boat_Class ("Optimist", max_crew = 2)
    >>> b1 = SRM.Boat       (bc, 1, "AUT")

    >>> int (bc.pid), int (b1.pid)
    (1, 2)

    >>> scope.ems.pm.reserve (None, 100)
    100

    >>> b2 = SRM.Boat (bc, 2, "AUT")
    >>> int (b2.pid)
    101

    >>> scope.commit () ### 1

    >>> scope.max_cid, scope.max_pid ### after commit 1
    (3, 101)

    >>> b3 = SRM.Boat (bc, 3, "AUT") ### 1
    >>> int (b3.pid)
    102

    >>> b1.last_cid ### 1 before change
    2
    >>> _ = b1.set (sail_number = 42) ### 1
    >>> b1.last_cid ### 1 after change
    5

    >>> scope.max_cid, scope.max_pid >= b2.pid ### before rollback 2
    (5, True)

    >>> scope.rollback () ### 2

    >>> scope.max_cid >= b2.last_cid, scope.max_pid >= b2.pid ### after rollback 2
    (True, True)

    >>> b3 = SRM.Boat (bc, 3, "AUT") ### 2
    >>> b3.pid > b2.pid ### 2
    True

    >>> b1.last_cid >= b3.last_cid ### 2 before change
    False
    >>> _ = b1.set (sail_number = 42) ## 2
    >>> b1.last_cid >= b3.last_cid ### 2 after change
    True

    >>> scope.max_cid >= b3.last_cid , scope.max_pid >= b3.pid ### after changes after rollback 2
    (True, True)

"""

__test__ = Scaffold.create_test_dict \
    ( dict
        ( test_map      = _test_map
        , test_no_reuse = _test_no_reuse
        )
    )

### __END__ GTW.__test__.Attr_surrogate
