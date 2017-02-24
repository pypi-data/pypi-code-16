# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Mag. Christian Tanzer All rights reserved
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
#    migration
#
# Purpose
#    Test scope migrations
#
# Revision Dates
#    19-May-2010 (CT) Creation
#     1-Jul-2010 (CT) `race_results` as example of composite-collection added
#    13-Jul-2010 (CT) Changed to use `DB_Man` for migration
#                     (instead of `Scope.copy`)
#     2-Aug-2010 (MG) `Account_Anonymous` added to test an border case for
#                     the migration
#    16-Aug-2010 (MG) Test for a change with children added
#    17-Aug-2010 (CT) Use `unicode` instead of `str`
#     6-Sep-2010 (CT) Adapted to change of `Race_Result` from Composite-List
#                     to `Link1`
#    14-Jun-2011 (MG) `MYST` added to `Backend_Parameters`
#    19-Mar-2012 (CT) Adapt to `Boat_Class.name.ignore_case` now being `True`
#    19-Mar-2012 (CT) Adapt to reification of `SRM.Handicap`
#     1-Aug-2012 (MG) Add test type name change queries
#    24-Jan-2013 (CT) Change `nation` from `Austria` to `AUT`
#    ««revision-date»»···
#--

from   __future__        import print_function

from _GTW.__test__.model import *

class _Migration_Scaffold_ (Scaffold.__class__) :

    Backend_Parameters    = dict \
        ( Scaffold.Backend_Parameters
        , HPS             = "'hps:///test.hps'"
        , SQL             = "'sqlite:///test.sql'"
        , sq              = "'sqlite:///test.sql'"
        )

# end class _Migration_Scaffold_

Scaffold = _Migration_Scaffold_ ()

_test_code = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> apt_s, url_s = scope.app_type, scope.db_url
    >>> PAP  = scope.PAP
    >>> SRM  = scope.SRM
    >>> Auth = scope.Auth

    >>> x = SRM.Boat_Class (u"29er",              max_crew = 2)
    >>> x = SRM.Boat_Class (u"420er",             max_crew = 2)
    >>> x = SRM.Boat_Class (u"470er",             max_crew = 2)
    >>> x = SRM.Boat_Class (u"49er",              max_crew = 2)
    >>> x = SRM.Boat_Class (u"Aquila Kiel",       max_crew = 3)
    >>> sw= x.copy         (u"Aquila Schwert",    max_crew = 3)
    >>> x = SRM.Boat_Class (u"Fam",               max_crew = 3)
    >>> x = SRM.Boat_Class (u"Finn-Dinghy",       max_crew = 1)
    >>> x = SRM.Boat_Class (u"Korsar",            max_crew = 2)
    >>> x = SRM.Boat_Class (u"Laser",             max_crew = 1)
    >>> x = SRM.Boat_Class (u"Laser 4.7",         max_crew = 1)
    >>> x = SRM.Boat_Class (u"Laser Master",      max_crew = 1)
    >>> x = SRM.Boat_Class (u"Laser Radial",      max_crew = 1)
    >>> x = SRM.Boat_Class (u"O-Jolle",           max_crew = 1)
    >>> x = SRM.Boat_Class (u"Optimist",          max_crew = 1)
    >>> x = SRM.Boat_Class (u"Pirat Regatta",     max_crew = 2)
    >>> x = SRM.Boat_Class (u"Pirat Klassik",     max_crew = 2)
    >>> x = SRM.Boat_Class (u"Pirat Schulboot",   max_crew = 2)
    >>> x = SRM.Boat_Class (u"Pirat",             max_crew = 2)
    >>> x = SRM.Boat_Class (u"Robby Jolle",       max_crew = 2)
    >>> x = SRM.Boat_Class (u"Seascape 18",       max_crew = 4)
    >>> x = SRM.Boat_Class (u"Zoom8",             max_crew = 1)

    >>> sw.last_cid
    7
    >>> for c in scope.uncommitted_changes :
    ...     print (c)
    <Create SRM.Boat_Class ('29er', 'SRM.Boat_Class'), new-values = {'last_cid' : '1', 'max_crew' : '2'}>
    <Create SRM.Boat_Class ('420er', 'SRM.Boat_Class'), new-values = {'last_cid' : '2', 'max_crew' : '2'}>
    <Create SRM.Boat_Class ('470er', 'SRM.Boat_Class'), new-values = {'last_cid' : '3', 'max_crew' : '2'}>
    <Create SRM.Boat_Class ('49er', 'SRM.Boat_Class'), new-values = {'last_cid' : '4', 'max_crew' : '2'}>
    <Create SRM.Boat_Class ('Aquila Kiel', 'SRM.Boat_Class'), new-values = {'last_cid' : '5', 'max_crew' : '3'}>
    <Copy SRM.Boat_Class ('Aquila Schwert', 'SRM.Boat_Class'), new-values = {'last_cid' : '7'}>
        <Create SRM.Boat_Class ('Aquila Schwert', 'SRM.Boat_Class'), new-values = {'last_cid' : '6', 'max_crew' : '3'}>
    <Create SRM.Boat_Class ('Fam', 'SRM.Boat_Class'), new-values = {'last_cid' : '8', 'max_crew' : '3'}>
    <Create SRM.Boat_Class ('Finn-Dinghy', 'SRM.Boat_Class'), new-values = {'last_cid' : '9', 'max_crew' : '1'}>
    <Create SRM.Boat_Class ('Korsar', 'SRM.Boat_Class'), new-values = {'last_cid' : '10', 'max_crew' : '2'}>
    <Create SRM.Boat_Class ('Laser', 'SRM.Boat_Class'), new-values = {'last_cid' : '11', 'max_crew' : '1'}>
    <Create SRM.Boat_Class ('Laser 4.7', 'SRM.Boat_Class'), new-values = {'last_cid' : '12', 'max_crew' : '1'}>
    <Create SRM.Boat_Class ('Laser Master', 'SRM.Boat_Class'), new-values = {'last_cid' : '13', 'max_crew' : '1'}>
    <Create SRM.Boat_Class ('Laser Radial', 'SRM.Boat_Class'), new-values = {'last_cid' : '14', 'max_crew' : '1'}>
    <Create SRM.Boat_Class ('O-Jolle', 'SRM.Boat_Class'), new-values = {'last_cid' : '15', 'max_crew' : '1'}>
    <Create SRM.Boat_Class ('Optimist', 'SRM.Boat_Class'), new-values = {'last_cid' : '16', 'max_crew' : '1'}>
    <Create SRM.Boat_Class ('Pirat Regatta', 'SRM.Boat_Class'), new-values = {'last_cid' : '17', 'max_crew' : '2'}>
    <Create SRM.Boat_Class ('Pirat Klassik', 'SRM.Boat_Class'), new-values = {'last_cid' : '18', 'max_crew' : '2'}>
    <Create SRM.Boat_Class ('Pirat Schulboot', 'SRM.Boat_Class'), new-values = {'last_cid' : '19', 'max_crew' : '2'}>
    <Create SRM.Boat_Class ('Pirat', 'SRM.Boat_Class'), new-values = {'last_cid' : '20', 'max_crew' : '2'}>
    <Create SRM.Boat_Class ('Robby Jolle', 'SRM.Boat_Class'), new-values = {'last_cid' : '21', 'max_crew' : '2'}>
    <Create SRM.Boat_Class ('Seascape 18', 'SRM.Boat_Class'), new-values = {'last_cid' : '22'}>
    <Create SRM.Boat_Class ('Zoom8', 'SRM.Boat_Class'), new-values = {'last_cid' : '23', 'max_crew' : '1'}>

    >>> scope.commit ()

    >>> x = SRM.Boat (('Optimist',),     1, u"AUT")
    >>> x = SRM.Boat (('Optimist',),     2, u"AUT")
    >>> x = SRM.Boat (('Laser',),        3, u"AUT")
    >>> x = SRM.Boat (('Seascape 18',), 14, u"AUT")

    >>> scope.commit ()

    >>> bc  = SRM.Boat_Class.instance (u"Optimist")
    >>> ys  = SRM.Handicap ("Yardstick")
    >>> b   = SRM.Boat.instance_or_new ('Optimist', u"1107", u"AUT", raw = True)
    >>> p   = PAP.Person.instance_or_new (u"Tanzer", u"Christian")
    >>> s   = SRM.Sailor.instance_or_new (p.epk_raw, nation = u"AUT", mna_number = u"29676", raw = True) ### 1
    >>> rev = SRM.Regatta_Event (u"Himmelfahrt", dict (start = u"20080501", raw = True), raw = True)
    >>> reg = SRM.Regatta_C (rev, bc)
    >>> reh = SRM.Regatta_H (rev, ys)
    >>> bir = SRM.Boat_in_Regatta (b, reg, skipper = s)

    >>> rr1 = SRM.Race_Result (bir, 1, points = 8)
    >>> rr2 = SRM.Race_Result (bir, 2, points = 4)

    >>> scope.commit ()
    >>> sw.last_cid
    7
    >>> scope.MOM.Id_Entity.count
    36
    >>> int (scope.query_changes (parent = None).count ())
    36
    >>> int (scope.query_changes ().count ())
    37
    >>> int (scope.ems.max_cid)
    37

    >>> bc.set (loa = 2.43)
    1
    >>> SRM.Boat_Class.instance (u"Laser").set (sail_area = 7.06, loa = 4.064, beam = 1.422)
    3
    >>> SRM.Boat_Class.instance (u"Seascape 18").set (loa = 5.45, beam = 2.45, sail_area = 23)
    3
    >>> scope.commit ()

    >>> MOM.B = True
    >>> print (sw.last_cid) ### X
    7
    >>> scope.MOM.Id_Entity.count
    36
    >>> print (sw.last_cid) ### Y
    7
    >>> MOM.B = False
    >>> int (scope.query_changes ().count ())
    40
    >>> int (scope.ems.max_cid)
    40
    >>> len (scope.SRM.Regatta_Event.query ().first ().regattas)
    2
    >>> b = SRM.Boat_Class.query (Q.RAW.name == u"Aquila Schwert").one ()
    >>> print (b.last_cid, sw.last_cid, b is sw)
    7 7 True
    >>> c = scope.query_changes (cid = b.last_cid).one ()
    >>> print (c) ### change in source scope
    <Copy SRM.Boat_Class ('Aquila Schwert', 'SRM.Boat_Class'), new-values = {'last_cid' : '7'}>
        <Create SRM.Boat_Class ('Aquila Schwert', 'SRM.Boat_Class'), new-values = {'last_cid' : '6', 'max_crew' : '3'}>
    >>> len (c.children)
    1
    >>> int (c.cid), int (c.children [0].cid)
    (7, 6)

    >>> [s for s in scope if not s.last_cid] ### before expunge
    []
    >>> sum ((not s.last_cid) for s in scope), sum (bool (s.last_cid) for s in scope) ### before expunge
    (0, 36)
    >>> if hasattr (scope.ems.session, "expunge") : scope.ems.session.expunge ()
    >>> [s for s in scope if not s.last_cid] ### after expunge
    []
    >>> sum ((not s.last_cid) for s in scope), sum (bool (s.last_cid) for s in scope)  ### after expunge
    (0, 36)
    >>> scope.query_changes (type_name = "SRM.Boat_Class").count ()
    26
    >>> b = scope.SRM.Boat_Class.query (Q.RAW.name == u"Aquila Schwert").one ()
    >>> print (b.last_cid) ### before migration
    7

    Save contents of scope to database and destroy scope:

    >>> scope.ems.compact ()
    >>> scope.destroy ()

    Now, we migrate all objects and the change history to a new backend. All
    entities, changes, cids, and pids should be identical afterwards:

    >>> db_url = "hps:////tmp/gtw_test_migration.gtw"
    >>> apt_t, url_t = Scaffold.app_type_and_url (db_url)
    >>> apt_t.delete_database (url_t) # 1
    >>> db_man_s = Scaffold.DB_Man.connect (apt_s, url_s)
    >>> db_man_t = Scaffold.DB_Man.create  (apt_t, url_t, db_man_s)
    >>> db_man_s.destroy ()
    >>> db_man_t.destroy ()

    >>> scope_s = Scaffold.scope (url_s, create = False) # doctest:+ELLIPSIS
    Loading scope MOMT__...
    >>> scope_t = Scaffold.scope (url_t, create = False) # doctest:+ELLIPSIS
    Loading scope MOMT__...

    >>> tuple (s.MOM.Id_Entity.count for s in (scope_s, scope_t))
    (36, 36)
    >>> all (s.as_pickle_cargo () == t.as_pickle_cargo () for (s, t) in zip (scope_s, scope_t))
    True
    >>> int (scope_t.ems.max_cid)
    40
    >>> len (scope_t.SRM.Regatta_Event.query ().first ().regattas)
    2
    >>> [s for (s, t) in zip (scope_s, scope_t) if s.last_cid != t.last_cid or not s.last_cid]
    []
    >>> [s.query_changes (type_name = "SRM.Boat_Class").count () for s in (scope_t, scope_s)]
    [26, 26]
    >>> bs = scope_s.SRM.Boat_Class.query (Q.RAW.name == u"Aquila Schwert").one ()
    >>> bt = scope_t.SRM.Boat_Class.query (Q.RAW.name == u"Aquila Schwert").one ()
    >>> print (bs.last_cid, bt.last_cid) ### migrated to HPS
    7 7

    Now we delete the original database and then migrate back into the
    original app-type/backend. Again, all entities, changes, cids,
    and pids should still be identical:

    >>> scope_s.destroy ()
    >>> scope_t.destroy ()
    >>> apt_s.delete_database (url_s) # 2
    >>> db_man_t = Scaffold.DB_Man.connect (apt_t, url_t)
    >>> db_man_u = Scaffold.DB_Man.create  (apt_s, url_s, db_man_t)
    >>> db_man_t.destroy ()
    >>> db_man_u.destroy ()

    >>> scope_t = Scaffold.scope (url_t, create = False) # doctest:+ELLIPSIS
    Loading scope MOMT__...
    >>> scope_u = Scaffold.scope (url_s, create = False) # doctest:+ELLIPSIS
    Loading scope MOMT__...

    >>> tuple (s.MOM.Id_Entity.count for s in (scope_t, scope_u))
    (36, 36)
    >>> all (s.as_pickle_cargo () == t.as_pickle_cargo () for (s, t) in zip (scope_t, scope_u))
    True
    >>> int (scope_u.ems.max_cid)
    40
    >>> len (scope_u.SRM.Regatta_Event.query ().first ().regattas)
    2
    >>> [s for (s, t) in zip (scope_t, scope_u) if s.last_cid != t.last_cid or not s.last_cid]
    []

    >>> b = scope_u.SRM.Boat_Class.query (Q.RAW.name == u"Aquila Schwert").one ()
    >>> print (b.last_cid) ### after migration
    7
    >>> c = scope_u.query_changes (cid = b.last_cid).one () ### mig scope
    >>> print (c)
    <Copy SRM.Boat_Class ('Aquila Schwert', 'SRM.Boat_Class'), new-values = {'last_cid' : '7'}>
        <Create SRM.Boat_Class ('Aquila Schwert', 'SRM.Boat_Class'), new-values = {'last_cid' : '6', 'max_crew' : '3'}>
    >>> len (c.children)
    1
    >>> int (c.cid), int (c.children [0].cid)
    (7, 6)
    >>> scope_u.query_changes (type_name = "SRM.Boat_Class").count ()
    26

    Lets clean up::

    >>> scope_t.destroy ()
    >>> scope_u.destroy ()

    >>> apt_t.delete_database (url_t) # 3
    >>> apt_s.delete_database (url_s) # 4

"""

__test__ = Scaffold.create_test_dict \
    ( dict
        ( test_code = _test_code
        )
    , ignore = ("HPS", )
    )

### __END__ migration
