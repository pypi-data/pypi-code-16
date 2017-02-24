# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Mag. Christian Tanzer All rights reserved
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
#    GTW.__test__.Certificate
#
# Purpose
#    Test GTW.OMP.Auth.Certificate
#
# Revision Dates
#    16-Jan-2013 (CT) Creation
#    25-Feb-2013 (CT) Add tests
#    26-Apr-2013 (CT) Remove `cert_id`
#    ««revision-date»»···
#--

from   __future__ import absolute_import, division, print_function, unicode_literals

from   _GTW.__test__.model      import *

import datetime

_test_create = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope ...
    >>> Auth  = scope.Auth

    >>> a1 = Auth.Account (name = "foo@bar", raw = True)
    >>> a2 = Auth.Account (name = "foo@baz", raw = True)

    >>> Auth.Certificate.query_s ().all ()
    []

    >>> c1 = Auth.Certificate (email = "foo@bar", validity = ("20130116", ), raw = True)
    >>> c2 = Auth.Certificate (email = "foo@baz", validity = ("20130131", ), raw = True)

    >>> scope.commit ()

    >>> all_cs = Auth.Certificate.query_s ().all ()
    >>> prepr (all_cs)
    [Auth.Certificate ('foo@bar', ('2013-01-16', ), ''), Auth.Certificate ('foo@baz', ('2013-01-31', ), '')]

    >>> for c in all_cs :
    ...     print (c.as_code (), c.validity.start)
    Auth.Certificate ('foo@bar', ('2013-01-16', ), '', ) 2013-01-16 00:00:00
    Auth.Certificate ('foo@baz', ('2013-01-31', ), '', ) 2013-01-31 00:00:00

    >>> c3 = Auth.Certificate (email = "foo@baz", validity = ("20150131", ), raw = True)

    >>> scope.commit ()

    >>> all_cs = Auth.Certificate.query_s ().all ()
    >>> prepr (all_cs)
    [Auth.Certificate ('foo@bar', ('2013-01-16', ), ''), Auth.Certificate ('foo@baz', ('2013-01-31', ), ''), Auth.Certificate ('foo@baz', ('2015-01-31', ), '')]

    >>> prepr ((c1, c1.alive))
    (Auth.Certificate ('foo@bar', ('2013-01-16', ), ''), False)

    >>> c1.pem = b"fake value to fool `alive`"

    >>> prepr ((c1, c1.alive))
    (Auth.Certificate ('foo@bar', ('2013-01-16', ), ''), True)

    >>> rdf = MOM.Attr.A_Date_Time.now () + datetime.timedelta (days = +1)
    >>> rdp = MOM.Attr.A_Date_Time.now () + datetime.timedelta (days = -1)
    >>> with expect_except (MOM.Error.Invariants) :
    ...     _ = c1.set (revocation_date = rdf) # doctest:+ELLIPSIS
    Invariants: Condition `valid_revocation_date` : The revocation date cannot be in the future. (revocation_date <= today)
        revocation_date = ...
        today = ...

    >>> _ = c1.set (revocation_date = rdp)
    >>> prepr ((c1, c1.alive))
    (Auth.Certificate ('foo@bar', ('2013-01-16', ), ''), False)

    >>> scope.commit ()
    >>> prepr ((c1, c1.alive))
    (Auth.Certificate ('foo@bar', ('2013-01-16', ), ''), False)

    >>> c4 = Auth.Certificate (email = "foo@foo", validity = (), raw = True)

    >>> prepr ((c4, c4.alive))
    (Auth.Certificate ('foo@foo', (), ''), None)

    >>> c4.validity.start = "20130225"
    >>> prepr ((c4, c4.alive))
    (Auth.Certificate ('foo@foo', ('2013-02-25', ), ''), False)

    >>> c4.pem = b"fake value to fool `alive`"
    >>> prepr ((c4, c4.alive))
    (Auth.Certificate ('foo@foo', ('2013-02-25', ), ''), True)

    >>> c5 = Auth.Certificate (email = "bar@foo", validity = ("20130225", ), raw = True)

    >>> prepr ((c5, c5.alive))
    (Auth.Certificate ('bar@foo', ('2013-02-25', ), ''), False)

    >>> for c in Auth.Certificate.query ().order_by (Q.cert_id) :
    ...     (int (c.pid), int (c.cert_id or 0) or None)
    (3, 1)
    (4, 2)
    (5, 3)
    (6, 4)
    (7, 5)

"""

class _Certificate_Scaffold_ (Scaffold.__class__) :

    Backend_Parameters    = dict \
        ( Scaffold.Backend_Parameters
        , HPS             = "'hps:///test.hps'"
        , SQL             = "'sqlite:///test.sql'"
        , sq              = "'sqlite:///test.sql'"
        )

# end class _Certificate_Scaffold_

Scaffold = _Certificate_Scaffold_ ()

__test__ = Scaffold.create_test_dict \
    ( dict
        ( test_create  = _test_create
        )
    )

### __END__ GTW.__test__.Certificate
