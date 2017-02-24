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
#    GTW.__test__.Boat_in_Regatta
#
# Purpose
#    Test creation and querying of Boat_in_Regatta
#
# Revision Dates
#     3-May-2010 (MG) Creation
#     3-May-2010 (CT) Creation continued
#    14-Dec-2011 (CT) Add tests for `attrs`
#    19-Jan-2012 (CT) Add tests for `object_referring_attributes`
#    19-Jan-2012 (CT) Add `_delayed` tests
#    19-Mar-2012 (CT) Adapt to `Boat_Class.name.ignore_case` now being `True`
#    19-Mar-2012 (CT) Adapt to reification of `SRM.Handicap`
#    27-Apr-2012 (CT) Add test for `skipper_not_multiplexed`
#     7-May-2012 (CT) Add test for `crew_number_valid`
#    12-Jun-2012 (CT) Add tests for `tn_pid`, `.attrs ("type_name")`
#    27-Jun-2012 (CT) Add tests for `query_changes` for `type_name`
#     1-Aug-2012 (CT) Add `_test_referential_integrity`
#     3-Aug-2012 (MG) Improve `_test_referential_integrity`
#     4-Aug-2012 (CT) Add `_test_undo`, add `raw = True` to entity creation
#    12-Oct-2012 (CT) Adapt to repr change of `An_Entity`
#    13-Nov-2012 (CT) Adapt to change of `SRM.Club.name.cooked`
#    10-Dec-2012 (CT) Add tests for `.FO` (nested attributes)
#    19-Mar-2013 (CT) Add tests for `AQ.Attrs`, `AQ.E_Type`, `AQx`
#    19-Mar-2013 (CT) Add test for `AQ.Atoms`
#    15-Apr-2013 (CT) Adapt to change of `MOM.Attr.Kind.reset`
#    26-Jul-2013 (CT) Add `_test_polymorph`
#    20-Aug-2013 (CT) Remove `show_ora`, `show_dep` from `test_code`
#                     Lazy loading of objects breaks this in SAS, SAW backends
#     9-Oct-2013 (CT) Add `_test_qr_grouped_by`
#    ««revision-date»»···
#--

from   __future__  import print_function, unicode_literals

_test_code = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> PAP   = scope.PAP
    >>> SRM   = scope.SRM
    >>> BiR   = SRM.Boat_in_Regatta
    >>> today = BiR.registration_date.default
    >>> bc    = SRM.Boat_Class ("Optimist", max_crew = 1, raw = True)
    >>> ys    = SRM.Handicap ("Yardstick", raw = True)
    >>> b     = SRM.Boat.instance_or_new ('Optimist', "1107", "AUT", raw = True)
    >>> p     = PAP.Person.instance_or_new ("Tanzer", "Christian", raw = True)
    >>> s     = SRM.Sailor.instance_or_new (p.epk_raw, nation = "AUT", mna_number = "29676", raw = True) ### 1
    >>> rev   = SRM.Regatta_Event ("Himmelfahrt", ("20080501", ), raw = True)
    >>> reg   = SRM.Regatta_C (rev.epk_raw, bc.epk_raw, raw = True)
    >>> reh   = SRM.Regatta_H (rev.epk_raw, ys,  raw = True)
    >>> prepr (list (r.name for r in sorted (rev.regattas, key = TFL.Sorted_By ("+"))))
    ['Optimist', 'Yardstick']

    >>> reg.set_raw (result = dict (date = "26.5.2009 10:20", software = "calculated with REGATTA.yellow8.com", status = "final", raw = True))
    1
    >>> prepr ((pyk.text_type (reg.FO.result)))
    '2009-05-26 10:20, calculated with REGATTA.yellow8.com, final'
    >>> scope.commit ()

    >>> scope.MOM.Id_Entity.query ().order_by (TFL.Sorted_By ("pid")).attrs ("pid", "type_name").all ()
    [(1, 'SRM.Boat_Class'), (2, 'SRM.Handicap'), (3, 'SRM.Boat'), (4, 'PAP.Person'), (5, 'SRM.Sailor'), (6, 'SRM.Regatta_Event'), (7, 'SRM.Regatta_C'), (8, 'SRM.Regatta_H')]
    >>> scope.MOM.Id_Entity.query ().order_by (TFL.Sorted_By ("pid")).attrs ("type_name", "pid").all ()
    [('SRM.Boat_Class', 1), ('SRM.Handicap', 2), ('SRM.Boat', 3), ('PAP.Person', 4), ('SRM.Sailor', 5), ('SRM.Regatta_Event', 6), ('SRM.Regatta_C', 7), ('SRM.Regatta_H', 8)]

    >>> scope.MOM.Id_Entity.query ().order_by (TFL.Sorted_By ("type_name", "pid")).attrs ("pid", "type_name").all ()
    [(4, 'PAP.Person'), (3, 'SRM.Boat'), (1, 'SRM.Boat_Class'), (2, 'SRM.Handicap'), (7, 'SRM.Regatta_C'), (6, 'SRM.Regatta_Event'), (8, 'SRM.Regatta_H'), (5, 'SRM.Sailor')]

    >>> prepr (rev.epk_raw)
    ('Himmelfahrt', (('finish', '2008-05-01'), ('start', '2008-05-01')), 'SRM.Regatta_Event')
    >>> prepr (reg.epk_raw)
    (('Himmelfahrt', (('finish', '2008-05-01'), ('start', '2008-05-01')), 'SRM.Regatta_Event'), ('Optimist', 'SRM.Boat_Class'), 'SRM.Regatta_C')
    >>> SRM.Regatta_C.instance (* reg.epk)
    SRM.Regatta_C (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', ))
    >>> SRM.Regatta.instance (* reg.epk)
    SRM.Regatta_C (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', ))
    >>> SRM.Regatta_C.instance (* reg.epk_raw, raw = True)
    SRM.Regatta_C (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', ))

    >>> bir = BiR (b.epk_raw, reg.epk_raw, skipper = s.epk_raw, raw = True)
    >>> bir.registration_date == today
    True

    >>> prepr (bir.epk_raw)
    ((('Optimist', 'SRM.Boat_Class'), '1107', 'AUT', '', 'SRM.Boat'), (('Himmelfahrt', (('finish', '2008-05-01'), ('start', '2008-05-01')), 'SRM.Regatta_Event'), ('Optimist', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta')
    >>> BiR.instance (* bir.epk_raw, raw = True)
    SRM.Boat_in_Regatta ((('optimist', ), 1107, 'AUT', ''), (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', )))

    >>> print (bir.FO.pid)
    9
    >>> print (bir.FO.right.left.pid)
    6
    >>> print (bir.FO.left)
    Optimist, AUT 1107
    >>> print (bir.FO.left.left)
    Optimist
    >>> print (bir.FO.left.left.name)
    Optimist
    >>> print (bir.FO.right)
    Himmelfahrt 2008-05-01, Optimist
    >>> print (bir.FO.right.left)
    Himmelfahrt 2008-05-01
    >>> print (bir.FO.right.left.date)
    2008-05-01
    >>> print (bir.FO.right.left.date.start)
    2008-05-01
    >>> print (bir.FO.right.left.date.finish)
    2008-05-01

    >>> print (getattr (bir.FO, "pid"))
    9
    >>> print (getattr (bir.FO, "right.left.pid"))
    6
    >>> print (getattr (bir.FO, "left"))
    Optimist, AUT 1107
    >>> print (getattr (bir.FO, "left.left"))
    Optimist
    >>> print (getattr (bir.FO, "left.left.name"))
    Optimist
    >>> print (getattr (bir.FO, "right"))
    Himmelfahrt 2008-05-01, Optimist
    >>> print (getattr (bir.FO, "right.left"))
    Himmelfahrt 2008-05-01
    >>> print (getattr (bir.FO, "right.left.date"))
    2008-05-01
    >>> print (getattr (bir.FO, "right.left.date.finish"))
    2008-05-01

    >>> sorted (reg.boats)
    [SRM.Boat_in_Regatta ((('optimist', ), 1107, 'AUT', ''), (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', )))]

    >>> sort_key = TFL.Sorted_By ("-regatta.event.date.start", "skipper.person.last_name", "skipper.person.first_name")

    >>> print (sort_key)
    <Sorted_By: Descending-Getter function for `.regatta.event.date.start`, Getter function for `.skipper.person.last_name`, Getter function for `.skipper.person.first_name`>
    >>> print (BiR.E_Type.sort_key_pm (sort_key))
    <Sorted_By: Getter function for `.relevant_root.type_name`, <Sorted_By: Descending-Getter function for `.regatta.event.date.start`, Getter function for `.skipper.person.last_name`, Getter function for `.skipper.person.first_name`>>

    >>> list (BiR.query (sort_key = sort_key))
    [SRM.Boat_in_Regatta ((('optimist', ), 1107, 'AUT', ''), (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', )))]
    >>> list (BiR.query_s (sort_key = sort_key))
    [SRM.Boat_in_Regatta ((('optimist', ), 1107, 'AUT', ''), (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', )))]

    >>> df = SRM.Regatta.AQ.event.date.start.EQ ("2008")
    >>> df
    Q.left.date.start.between (datetime.date(2008, 1, 1), datetime.date(2008, 12, 31))

    >>> AQ  = BiR.AQ.Select (MOM.Attr.Selector.sig)
    >>> q   = SRM.Regatta.query_s ().filter (df)
    >>> fs  = tuple (x.QR for x in AQ.regatta.Unwrapped_Atoms)
    >>> fsn = tuple (x._name for x in fs)
    >>> fss = ('left.__raw_name', 'left.date')
    >>> fst = ('left', )

    >>> AQ
    <Attr.Type.Querier.E_Type for SRM.Boat_in_Regatta>
    >>> AQ._attr_selector
    <MOM.Attr.Selector.Kind sig_attr>
    >>> AQ.left._attr_selector
    <MOM.Attr.Selector.Kind sig_attr>
    >>> AQ.right.left.date._attr_selector
    <MOM.Attr.Selector.Kind sig_attr>

    >>> AQ.Attrs
    (<left.AQ [Attr.Type.Querier Id_Entity]>, <right.AQ [Attr.Type.Querier Id_Entity]>)
    >>> AQ.left.Attrs
    (<left.left.AQ [Attr.Type.Querier Id_Entity]>, <left.sail_number.AQ [Attr.Type.Querier Raw]>, <left.nation.AQ [Attr.Type.Querier Ckd]>, <left.sail_number_x.AQ [Attr.Type.Querier String]>)
    >>> AQ.right.left.date.Attrs
    (<right.left.date.start.AQ [Attr.Type.Querier Date]>, <right.left.date.finish.AQ [Attr.Type.Querier Date]>)

    >>> print (AQ.E_Type.type_name)
    SRM.Boat_in_Regatta
    >>> print (AQ.left.E_Type.type_name)
    SRM.Boat
    >>> print (AQ.right.left.date.E_Type.type_name)
    MOM.Date_Interval_C

    >>> for aq in BiR.AQ.Attrs_Transitive :
    ...     prepr ((aq, aq.E_Type.type_name if aq.E_Type and aq.E_Type.PNS else "-"*5))
    (<left.AQ [Attr.Type.Querier Id_Entity]>, 'SRM.Boat')
    (<left.left.AQ [Attr.Type.Querier Id_Entity]>, 'SRM.Boat_Class')
    (<left.left.name.AQ [Attr.Type.Querier String]>, '-----')
    (<left.left.beam.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<left.left.loa.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<left.left.max_crew.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<left.left.sail_area.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<left.sail_number.AQ [Attr.Type.Querier Raw]>, '-----')
    (<left.nation.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<left.sail_number_x.AQ [Attr.Type.Querier String]>, '-----')
    (<left.name.AQ [Attr.Type.Querier String]>, '-----')
    (<right.AQ [Attr.Type.Querier Id_Entity]>, 'SRM.Regatta')
    (<right.left.AQ [Attr.Type.Querier Id_Entity]>, 'SRM.Regatta_Event')
    (<right.left.name.AQ [Attr.Type.Querier String]>, '-----')
    (<right.left.date.AQ [Attr.Type.Querier Composite]>, 'MOM.Date_Interval_C')
    (<right.left.date.start.AQ [Attr.Type.Querier Date]>, '-----')
    (<right.left.date.start.day.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<right.left.date.start.month.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<right.left.date.start.year.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<right.left.date.finish.AQ [Attr.Type.Querier Date]>, '-----')
    (<right.left.date.finish.day.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<right.left.date.finish.month.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<right.left.date.finish.year.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<right.left.date.alive.AQ [Attr.Type.Querier Boolean]>, '-----')
    (<right.left.club.AQ [Attr.Type.Querier Id_Entity]>, 'SRM.Club')
    (<right.left.club.name.AQ [Attr.Type.Querier String]>, '-----')
    (<right.left.club.long_name.AQ [Attr.Type.Querier String]>, '-----')
    (<right.left.desc.AQ [Attr.Type.Querier String]>, '-----')
    (<right.left.is_cancelled.AQ [Attr.Type.Querier Boolean]>, '-----')
    (<right.left.perma_name.AQ [Attr.Type.Querier String]>, '-----')
    (<right.left.year.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<right.boat_class.AQ [Attr.Type.Querier Id_Entity]>, 'SRM._Boat_Class_')
    (<right.boat_class.name.AQ [Attr.Type.Querier String]>, '-----')
    (<right.discards.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<right.is_cancelled.AQ [Attr.Type.Querier Boolean]>, '-----')
    (<right.kind.AQ [Attr.Type.Querier String]>, '-----')
    (<right.races.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<right.result.AQ [Attr.Type.Querier Composite]>, 'SRM.Regatta_Result')
    (<right.result.date.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<right.result.software.AQ [Attr.Type.Querier String]>, '-----')
    (<right.result.status.AQ [Attr.Type.Querier String]>, '-----')
    (<right.starters_rl.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<right.perma_name.AQ [Attr.Type.Querier String]>, '-----')
    (<right.races_counted.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<right.year.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<skipper.AQ [Attr.Type.Querier Id_Entity]>, 'SRM.Sailor')
    (<skipper.left.AQ [Attr.Type.Querier Id_Entity]>, 'PAP.Person')
    (<skipper.left.last_name.AQ [Attr.Type.Querier String_FL]>, '-----')
    (<skipper.left.first_name.AQ [Attr.Type.Querier String_FL]>, '-----')
    (<skipper.left.middle_name.AQ [Attr.Type.Querier String]>, '-----')
    (<skipper.left.title.AQ [Attr.Type.Querier String]>, '-----')
    (<skipper.left.lifetime.AQ [Attr.Type.Querier Composite]>, 'MOM.Date_Interval_lifetime')
    (<skipper.left.lifetime.start.AQ [Attr.Type.Querier Date]>, '-----')
    (<skipper.left.lifetime.start.day.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<skipper.left.lifetime.start.month.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<skipper.left.lifetime.start.year.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<skipper.left.lifetime.finish.AQ [Attr.Type.Querier Date]>, '-----')
    (<skipper.left.lifetime.finish.day.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<skipper.left.lifetime.finish.month.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<skipper.left.lifetime.finish.year.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<skipper.left.lifetime.alive.AQ [Attr.Type.Querier Boolean]>, '-----')
    (<skipper.left.sex.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<skipper.mna_number.AQ [Attr.Type.Querier Raw]>, '-----')
    (<skipper.nation.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<skipper.club.AQ [Attr.Type.Querier Id_Entity]>, 'SRM.Club')
    (<skipper.club.name.AQ [Attr.Type.Querier String]>, '-----')
    (<skipper.club.long_name.AQ [Attr.Type.Querier String]>, '-----')
    (<place.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<points.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<yardstick.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<creation.AQ [Attr.Type.Querier Rev_Ref]>, 'MOM.MD_Change')
    (<creation.c_time.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<creation.c_user.AQ [Attr.Type.Querier Id_Entity]>, 'MOM.Id_Entity')
    (<creation.kind.AQ [Attr.Type.Querier String]>, '-----')
    (<creation.time.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<creation.user.AQ [Attr.Type.Querier Id_Entity]>, 'MOM.Id_Entity')
    (<last_change.AQ [Attr.Type.Querier Rev_Ref]>, 'MOM.MD_Change')
    (<last_change.c_time.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<last_change.c_user.AQ [Attr.Type.Querier Id_Entity]>, 'MOM.Id_Entity')
    (<last_change.kind.AQ [Attr.Type.Querier String]>, '-----')
    (<last_change.time.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<last_change.user.AQ [Attr.Type.Querier Id_Entity]>, 'MOM.Id_Entity')
    (<last_cid.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<pid.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<type_name.AQ [Attr.Type.Querier String]>, '-----')
    (<rank.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<registration_date.AQ [Attr.Type.Querier Date]>, '-----')
    (<registration_date.day.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<registration_date.month.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<registration_date.year.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<events.AQ [Attr.Type.Querier Rev_Ref]>, 'EVT.Event')
    (<events.date.AQ [Attr.Type.Querier Composite]>, 'MOM.Date_Interval')
    (<events.date.start.AQ [Attr.Type.Querier Date]>, '-----')
    (<events.date.start.day.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<events.date.start.month.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<events.date.start.year.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<events.date.finish.AQ [Attr.Type.Querier Date]>, '-----')
    (<events.date.finish.day.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<events.date.finish.month.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<events.date.finish.year.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<events.date.alive.AQ [Attr.Type.Querier Boolean]>, '-----')
    (<events.time.AQ [Attr.Type.Querier Composite]>, 'MOM.Time_Interval')
    (<events.time.start.AQ [Attr.Type.Querier Time]>, '-----')
    (<events.time.start.hour.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<events.time.start.minute.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<events.time.start.second.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<events.time.finish.AQ [Attr.Type.Querier Time]>, '-----')
    (<events.time.finish.hour.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<events.time.finish.minute.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<events.time.finish.second.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<events.calendar.AQ [Attr.Type.Querier Id_Entity]>, 'EVT.Calendar')
    (<events.calendar.name.AQ [Attr.Type.Querier String]>, '-----')
    (<events.calendar.desc.AQ [Attr.Type.Querier String]>, '-----')
    (<events.detail.AQ [Attr.Type.Querier String]>, '-----')
    (<events.short_title.AQ [Attr.Type.Querier String]>, '-----')
    (<race_results.AQ [Attr.Type.Querier Rev_Ref]>, 'SRM.Race_Result')
    (<race_results.race.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<race_results.points.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<race_results.status.AQ [Attr.Type.Querier String]>, '-----')
    (<race_results.discarded.AQ [Attr.Type.Querier Boolean]>, '-----')
    (<_crew.AQ [Attr.Type.Querier Rev_Ref]>, 'SRM.Sailor')
    (<_crew.mna_number.AQ [Attr.Type.Querier Raw]>, '-----')
    (<_crew.nation.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<_crew.club.AQ [Attr.Type.Querier Id_Entity]>, 'SRM.Club')
    (<_crew.club.name.AQ [Attr.Type.Querier String]>, '-----')
    (<_crew.club.long_name.AQ [Attr.Type.Querier String]>, '-----')
    (<teams.AQ [Attr.Type.Querier Rev_Ref]>, 'SRM.Team')
    (<teams.left.AQ [Attr.Type.Querier Id_Entity]>, 'SRM.Regatta_C')
    (<teams.left.left.AQ [Attr.Type.Querier Id_Entity]>, 'SRM.Regatta_Event')
    (<teams.left.left.name.AQ [Attr.Type.Querier String]>, '-----')
    (<teams.left.left.date.AQ [Attr.Type.Querier Composite]>, 'MOM.Date_Interval_C')
    (<teams.left.left.date.start.AQ [Attr.Type.Querier Date]>, '-----')
    (<teams.left.left.date.start.day.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<teams.left.left.date.start.month.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<teams.left.left.date.start.year.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<teams.left.left.date.finish.AQ [Attr.Type.Querier Date]>, '-----')
    (<teams.left.left.date.finish.day.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<teams.left.left.date.finish.month.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<teams.left.left.date.finish.year.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<teams.left.left.date.alive.AQ [Attr.Type.Querier Boolean]>, '-----')
    (<teams.left.left.club.AQ [Attr.Type.Querier Id_Entity]>, 'SRM.Club')
    (<teams.left.left.club.name.AQ [Attr.Type.Querier String]>, '-----')
    (<teams.left.left.club.long_name.AQ [Attr.Type.Querier String]>, '-----')
    (<teams.left.left.desc.AQ [Attr.Type.Querier String]>, '-----')
    (<teams.left.left.is_cancelled.AQ [Attr.Type.Querier Boolean]>, '-----')
    (<teams.left.left.perma_name.AQ [Attr.Type.Querier String]>, '-----')
    (<teams.left.left.year.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<teams.left.boat_class.AQ [Attr.Type.Querier Id_Entity]>, 'SRM.Boat_Class')
    (<teams.left.boat_class.name.AQ [Attr.Type.Querier String]>, '-----')
    (<teams.left.boat_class.beam.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<teams.left.boat_class.loa.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<teams.left.boat_class.max_crew.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<teams.left.boat_class.sail_area.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<teams.left.discards.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<teams.left.is_cancelled.AQ [Attr.Type.Querier Boolean]>, '-----')
    (<teams.left.kind.AQ [Attr.Type.Querier String]>, '-----')
    (<teams.left.races.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<teams.left.result.AQ [Attr.Type.Querier Composite]>, 'SRM.Regatta_Result')
    (<teams.left.result.date.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<teams.left.result.software.AQ [Attr.Type.Querier String]>, '-----')
    (<teams.left.result.status.AQ [Attr.Type.Querier String]>, '-----')
    (<teams.left.starters_rl.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<teams.left.is_team_race.AQ [Attr.Type.Querier Boolean]>, '-----')
    (<teams.left.perma_name.AQ [Attr.Type.Querier String]>, '-----')
    (<teams.left.races_counted.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<teams.left.year.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<teams.left.max_crew.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<teams.name.AQ [Attr.Type.Querier String]>, '-----')
    (<teams.club.AQ [Attr.Type.Querier Id_Entity]>, 'SRM.Club')
    (<teams.club.name.AQ [Attr.Type.Querier String]>, '-----')
    (<teams.club.long_name.AQ [Attr.Type.Querier String]>, '-----')
    (<teams.desc.AQ [Attr.Type.Querier String]>, '-----')
    (<teams.leader.AQ [Attr.Type.Querier Id_Entity]>, 'PAP.Person')
    (<teams.leader.last_name.AQ [Attr.Type.Querier String_FL]>, '-----')
    (<teams.leader.first_name.AQ [Attr.Type.Querier String_FL]>, '-----')
    (<teams.leader.middle_name.AQ [Attr.Type.Querier String]>, '-----')
    (<teams.leader.title.AQ [Attr.Type.Querier String]>, '-----')
    (<teams.leader.lifetime.AQ [Attr.Type.Querier Composite]>, 'MOM.Date_Interval_lifetime')
    (<teams.leader.lifetime.start.AQ [Attr.Type.Querier Date]>, '-----')
    (<teams.leader.lifetime.start.day.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<teams.leader.lifetime.start.month.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<teams.leader.lifetime.start.year.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<teams.leader.lifetime.finish.AQ [Attr.Type.Querier Date]>, '-----')
    (<teams.leader.lifetime.finish.day.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<teams.leader.lifetime.finish.month.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<teams.leader.lifetime.finish.year.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<teams.leader.lifetime.alive.AQ [Attr.Type.Querier Boolean]>, '-----')
    (<teams.leader.sex.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<teams.place.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<teams.registration_date.AQ [Attr.Type.Querier Date]>, '-----')
    (<teams.registration_date.day.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<teams.registration_date.month.AQ [Attr.Type.Querier Ckd]>, '-----')
    (<teams.registration_date.year.AQ [Attr.Type.Querier Ckd]>, '-----')

    >>> BiR.AQ
    <Attr.Type.Querier.E_Type for SRM.Boat_in_Regatta>

    >>> for aq in BiR.AQ.Atoms :
    ...     print (aq._id)
    left__left__name
    left__left__beam
    left__left__loa
    left__left__max_crew
    left__left__sail_area
    left__sail_number
    left__nation
    left__sail_number_x
    left__name
    right__left__name
    right__left__date__start
    right__left__date__finish
    right__left__date__alive
    right__left__club__name
    right__left__club__long_name
    right__left__desc
    right__left__is_cancelled
    right__left__perma_name
    right__left__year
    right__boat_class__name
    right__discards
    right__is_cancelled
    right__kind
    right__races
    right__result__date
    right__result__software
    right__result__status
    right__starters_rl
    right__perma_name
    right__races_counted
    right__year
    skipper__left__last_name
    skipper__left__first_name
    skipper__left__middle_name
    skipper__left__title
    skipper__left__lifetime__start
    skipper__left__lifetime__finish
    skipper__left__lifetime__alive
    skipper__left__sex
    skipper__mna_number
    skipper__nation
    skipper__club__name
    skipper__club__long_name
    place
    points
    yardstick
    creation__c_time
    creation__kind
    creation__time
    last_change__c_time
    last_change__kind
    last_change__time
    last_cid
    pid
    type_name
    rank
    registration_date
    events__date__start
    events__date__finish
    events__date__alive
    events__time__start
    events__time__finish
    events__calendar__name
    events__calendar__desc
    events__detail
    events__short_title
    race_results__race
    race_results__points
    race_results__status
    race_results__discarded
    _crew__mna_number
    _crew__nation
    _crew__club__name
    _crew__club__long_name
    teams__left__left__name
    teams__left__left__date__start
    teams__left__left__date__finish
    teams__left__left__date__alive
    teams__left__left__club__name
    teams__left__left__club__long_name
    teams__left__left__desc
    teams__left__left__is_cancelled
    teams__left__left__perma_name
    teams__left__left__year
    teams__left__boat_class__name
    teams__left__boat_class__beam
    teams__left__boat_class__loa
    teams__left__boat_class__max_crew
    teams__left__boat_class__sail_area
    teams__left__discards
    teams__left__is_cancelled
    teams__left__kind
    teams__left__races
    teams__left__result__date
    teams__left__result__software
    teams__left__result__status
    teams__left__starters_rl
    teams__left__is_team_race
    teams__left__perma_name
    teams__left__races_counted
    teams__left__year
    teams__left__max_crew
    teams__name
    teams__club__name
    teams__club__long_name
    teams__desc
    teams__leader__last_name
    teams__leader__first_name
    teams__leader__middle_name
    teams__leader__title
    teams__leader__lifetime__start
    teams__leader__lifetime__finish
    teams__leader__lifetime__alive
    teams__leader__sex
    teams__place
    teams__registration_date

    >>> fs
    (Q.left.__raw_name, Q.left.date.start, Q.left.date.finish, Q.boat_class.__raw_name)

    >>> list (q)
    [SRM.Regatta_C (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', )), SRM.Regatta_H (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('yardstick', ))]

    >>> prepr (list (q.attrs (* fs)))
    [('Himmelfahrt', datetime.date(2008, 5, 1), datetime.date(2008, 5, 1), 'Optimist'), ('Himmelfahrt', datetime.date(2008, 5, 1), datetime.date(2008, 5, 1), 'Yardstick')]

    >>> prepr (list (q.attrs (* fsn)))
    [('Himmelfahrt', datetime.date(2008, 5, 1), datetime.date(2008, 5, 1), 'Optimist'), ('Himmelfahrt', datetime.date(2008, 5, 1), datetime.date(2008, 5, 1), 'Yardstick')]

    >>> prepr (list (q.attrs (* fss)))
    [('Himmelfahrt', MOM.Date_Interval_C ('2008-05-01', '2008-05-01'))]

    >>> prepr (list (q.attrs (* fst)))
    [(SRM.Regatta_Event ('himmelfahrt', ('2008-05-01', '2008-05-01')),)]

    >>> prepr (list (q.attrs (* fst, allow_duplicates = True)))
    [(SRM.Regatta_Event ('himmelfahrt', ('2008-05-01', '2008-05-01')),), (SRM.Regatta_Event ('himmelfahrt', ('2008-05-01', '2008-05-01')),)]

    >>> AQ  = BiR.AQ.Select (MOM.Attr.Selector.ui_attr)
    >>> AQ
    <Attr.Type.Querier.E_Type for SRM.Boat_in_Regatta>
    >>> AQ._attr_selector
    <MOM.Attr.Selector.Pred <MOM.Attr.Selector.Kind q_able> if Q.show_in_ui>
    >>> AQ.left._attr_selector
    <MOM.Attr.Selector.Pred <MOM.Attr.Selector.Kind q_able> if Q.show_in_ui>
    >>> AQ.right.left.date._attr_selector
    <MOM.Attr.Selector.Pred <MOM.Attr.Selector.Kind q_able> if Q.show_in_ui>

    >>> tuple (x.QR for x in AQ.regatta.Atoms)
    (Q.right.left.__raw_name, Q.right.left.date.start, Q.right.left.date.finish, Q.right.left.date.alive, Q.right.left.club.__raw_name, Q.right.left.club.long_name, Q.right.left.desc, Q.right.left.is_cancelled, Q.right.left.perma_name, Q.right.left.year, Q.right.boat_class.__raw_name, Q.right.discards, Q.right.is_cancelled, Q.right.kind, Q.right.races, Q.right.result.date, Q.right.result.software, Q.right.result.status, Q.right.starters_rl, Q.right.perma_name, Q.right.races_counted, Q.right.year)

    >>> scope.query_changes (type_name = "SRM.Regatta").order_by (Q.cid).first ()
    >>> scope.query_changes (type_name = "SRM.Regatta_C").order_by (Q.cid).first ()
    <Create SRM.Regatta_C (('Himmelfahrt', (('finish', '2008-05-01'), ('start', '2008-05-01')), 'SRM.Regatta_Event'), ('Optimist', 'SRM.Boat_Class'), 'SRM.Regatta_C'), new-values = {'is_cancelled' : 'no', 'last_cid' : '7', 'perma_name' : 'optimist'}>
    >>> scope.query_changes (Q.type_name == "SRM.Regatta_H").order_by (Q.cid).first ()
    <Create SRM.Regatta_H (('Himmelfahrt', (('finish', '2008-05-01'), ('start', '2008-05-01')), 'SRM.Regatta_Event'), ('Yardstick', 'SRM.Handicap'), 'SRM.Regatta_H'), new-values = {'is_cancelled' : 'no', 'last_cid' : '8', 'perma_name' : 'yardstick'}>

    >>> scope.query_changes ((Q.type_name == "SRM.Regatta_C") | (Q.type_name == "SRM.Regatta_H")).order_by (Q.cid).first ()
    <Create SRM.Regatta_C (('Himmelfahrt', (('finish', '2008-05-01'), ('start', '2008-05-01')), 'SRM.Regatta_Event'), ('Optimist', 'SRM.Boat_Class'), 'SRM.Regatta_C'), new-values = {'is_cancelled' : 'no', 'last_cid' : '7', 'perma_name' : 'optimist'}>

    >>> scope.query_changes (Q.OR (Q.type_name == "SRM.Regatta_C", Q.type_name == "SRM.Regatta_H")).order_by (Q.cid).first ()
    <Create SRM.Regatta_C (('Himmelfahrt', (('finish', '2008-05-01'), ('start', '2008-05-01')), 'SRM.Regatta_Event'), ('Optimist', 'SRM.Boat_Class'), 'SRM.Regatta_C'), new-values = {'is_cancelled' : 'no', 'last_cid' : '7', 'perma_name' : 'optimist'}>

    >>> scope.query_changes (Q.type_name.IN (('SRM.Regatta', 'SRM.Regatta_H', 'SRM.Regatta_C'))).order_by (Q.cid).first ()
    <Create SRM.Regatta_C (('Himmelfahrt', (('finish', '2008-05-01'), ('start', '2008-05-01')), 'SRM.Regatta_Event'), ('Optimist', 'SRM.Boat_Class'), 'SRM.Regatta_C'), new-values = {'is_cancelled' : 'no', 'last_cid' : '7', 'perma_name' : 'optimist'}>

    >>> scope.commit ()

    >>> b8   = SRM.Boat.instance_or_new ('Optimist', "1108", "AUT", raw = True)

    >>> b8
    SRM.Boat (('optimist', ), 1108, 'AUT', '')

    >>> with expect_except (MOM.Error.Invariants) :
    ...     bir8 = BiR (b8, reg, skipper = s)
    Invariants: A sailor can't be skipper of more than one boat in a single
    regatta event.
      The new definition of Boat in Regatta SRM.Boat_in_Regatta ((('Optimist', 'SRM.Boat_Class'), '1108', 'AUT', '', 'SRM.Boat'), (('Himmelfahrt', (('finish', '2008-05-01'), ('start', '2008-05-01')), 'SRM.Regatta_Event'), ('Optimist', 'SRM.Boat_Class'), 'SRM.Regatta_C')) would clash with 1 existing entities
      Already existing:
        SRM.Boat_in_Regatta ((('Optimist', 'SRM.Boat_Class'), '1107', 'AUT', '', 'SRM.Boat'), (('Himmelfahrt', (('finish', '2008-05-01'), ('start', '2008-05-01')), 'SRM.Regatta_Event'), ('Optimist', 'SRM.Boat_Class'), 'SRM.Regatta_C'))

    >>> b8
    SRM.Boat (('optimist', ), 1108, 'AUT', '')

    >>> scope.commit ()

    >>> scope.rollback ()

    >>> p2  = PAP.Person.instance_or_new ("Tanzer", "Laurens")
    >>> s2  = SRM.Sailor.instance_or_new (p2, nation = "AUT", raw = True)
    >>> cr = SRM.Crew_Member (bir, s2)

    >>> with expect_except (MOM.Error.Invariants) :
    ...     scope.commit ()
    Invariants: Condition `crew_number_valid` : The number of crew members must be less than
    `boat.b_class.max_crew`. (number_of_crew < boat.b_class.max_crew)
        _crew = ('Tanzer Laurens, AUT',)
        boat = Optimist, AUT 1107
        boat.b_class.max_crew = 1
        number_of_crew = 1 << len (_crew)

    >>> print (bir.skipper)
    (('tanzer', 'christian', '', ''), 'AUT', 29676, '')
    >>> bir.skipper is s
    True
    >>> bir.skipper.destroy ()
    >>> with expect_except (MOM.Error.Destroyed_Entity) :
    ...     print (bir.skipper)
    Destroyed_Entity: <Destroyed entity SRM.Boat_in_Regatta ((('optimist', ), 1107, 'AUT', ''), (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', )))>: access to attribute 'skipper' not allowed


"""

_test_delayed  = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> PAP = scope.PAP
    >>> SRM = scope.SRM
    >>> BiR = SRM.Boat_in_Regatta
    >>> bc  = SRM.Boat_Class.E_Type ("Optimist", max_crew = 1, raw = True)
    >>> ys  = SRM.Handicap.E_Type ("Yardstick", raw = True)
    >>> b   = SRM.Boat.E_Type (bc, "1107", "AUT", raw = True)
    >>> p   = PAP.Person.E_Type ("Tanzer", "Christian", raw = True)
    >>> s   = SRM.Sailor.E_Type (p, nation = "AUT", mna_number = "29676", raw = True) ### 1
    >>> rev = SRM.Regatta_Event.E_Type ("Himmelfahrt", ("20080501", ), raw = True)
    >>> reg = SRM.Regatta_C.E_Type (rev, bc)
    >>> reh = SRM.Regatta_H.E_Type (rev, ys)
    >>> bir = BiR.E_Type (b, reg, skipper = s)

    >>> list (r.name for r in sorted (getattr (rev, "regattas", [])))
    []

    >>> reg.set_raw (result = dict (date = "26.5.2009 10:20", software = "calculated with REGATTA.yellow8.com", status = "final", raw = True))
    1
    >>> prepr ((pyk.text_type (reg.FO.result)))
    '2009-05-26 10:20, calculated with REGATTA.yellow8.com, final'

    >>> show_ora (bir)  ### before scope.add
    ---
    >>> show_dep (s)    ### before scope.add
    ---

    >>> for _ in (bc, ys, b, p, s, rev, reg, reh, bir) :
    ...     scope.add (_)

    >>> prepr ((list (r.name for r in sorted (rev.regattas, key = TFL.Sorted_By ("+")))))
    ['Optimist', 'Yardstick']

    >>> show_ora (bir)         ### before destroy
    (('tanzer', 'christian', '', ''), 'AUT', 29676, '') : Entity `skipper`
    >>> show_dep (bir.skipper) ### before destroy
    ((('optimist', ), 1107, 'AUT', ''), (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', ))) : 1
    >>> print (bir.skipper)
    (('tanzer', 'christian', '', ''), 'AUT', 29676, '')
    >>> bir.skipper is s
    True
    >>> bir.skipper.destroy ()
    >>> show_ora (bir)  ### after destroy
    ---
    >>> show_dep (s)    ### after destroy
    ---
    >>> with expect_except (MOM.Error.Destroyed_Entity) :
    ...     print (bir.skipper)
    Destroyed_Entity: <Destroyed entity SRM.Boat_in_Regatta ((('optimist', ), 1107, 'AUT', ''), (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', )))>: access to attribute 'skipper' not allowed

"""

_test_polymorph = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> PAP = scope.PAP
    >>> SRM = scope.SRM

    >>> bc    = SRM.Boat_Class ("Optimist", max_crew = 1, raw = True)
    >>> ys    = SRM.Handicap ("Yardstick", raw = True)
    >>> rev   = SRM.Regatta_Event ("Himmelfahrt", ("20080501", ), raw = True)
    >>> reg   = SRM.Regatta_C (rev.epk_raw, bc.epk_raw, raw = True)
    >>> reh   = SRM.Regatta_H (rev.epk_raw, ys,  raw = True)

    >>> df = SRM.Regatta.AQ.event.date.start.EQ ("2008")
    >>> df
    Q.left.date.start.between (datetime.date(2008, 1, 1), datetime.date(2008, 12, 31))
    >>> q   = SRM.Regatta.query_s ().filter (df)

    >>> list (q)
    [SRM.Regatta_C (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', )), SRM.Regatta_H (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('yardstick', ))]

    >>> sk = TFL.Sorted_By (Q.event.date, Q.event.name, Q.boat_class.name)
    >>> sk = Q.pid

    >>> SRM.Regatta.query   ().order_by (sk).all ()
    [SRM.Regatta_C (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', )), SRM.Regatta_H (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('yardstick', ))]

    >>> SRM.Regatta_C.query ().order_by (sk).all ()
    [SRM.Regatta_C (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', ))]

    >>> SRM.Regatta_H.query ().order_by (sk).all ()
    [SRM.Regatta_H (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('yardstick', ))]

"""

_test_qr_grouped_by = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> PAP   = scope.PAP
    >>> SRM   = scope.SRM
    >>> BiR   = SRM.Boat_in_Regatta
    >>> today = BiR.registration_date.default
    >>> bc    = SRM.Boat_Class ("Optimist", max_crew = 1, raw = True)
    >>> ol    = SRM.Boat.instance_or_new ('Optimist', "1107", "AUT", raw = True)
    >>> oc    = SRM.Boat.instance_or_new ('Optimist', "1134", "AUT", raw = True)
    >>> pl    = PAP.Person.instance_or_new ("Tanzer", "Laurens", raw = True)
    >>> pc    = PAP.Person.instance_or_new ("Tanzer", "Clarissa", raw = True)
    >>> sl    = SRM.Sailor.instance_or_new (pl, nation = "AUT", raw = True)
    >>> sc    = SRM.Sailor.instance_or_new (pc, nation = "AUT", raw = True)
    >>> rev   = SRM.Regatta_Event ("Himmelfahrt", ("20080501", ), raw = True)
    >>> reg   = SRM.Regatta_C (rev.epk_raw, bc, raw = True)

    >>> birl  = BiR (ol, reg, skipper = sl)
    >>> birc  = BiR (oc, reg, skipper = sc)

    >>> _     = SRM.Race_Result (birl, 1, points = 1)
    >>> _     = SRM.Race_Result (birl, 2, points = 2)
    >>> _     = SRM.Race_Result (birl, 3, points = 3)

    >>> _     = SRM.Race_Result (birc, 1, points = 2)
    >>> _     = SRM.Race_Result (birc, 2, points = 1)
    >>> _     = SRM.Race_Result (birc, 3, points = 6)

    >>> q     = SRM.Boat_in_Regatta.query ()
    >>> qa    = q.attrs (Q.pid, Q.boat, Q.SUM (Q.race_results.points), Q.SUM (1))
    >>> qag   = qa.group_by (Q.pid, Q.boat)
    >>> for x in sorted (qag, key = TFL.Getter [2]) :
    ...     print (x [1:])
    (SRM.Boat (('optimist', ), 1107, 'AUT', ''), 6, 3)
    (SRM.Boat (('optimist', ), 1134, 'AUT', ''), 9, 3)

    >>> q = SRM.Race_Result.query ()
    >>> for x in sorted (q.attrs (Q.left, Q.SUM (Q.points)).group_by (Q.left), key = TFL.Getter [1]) :
    ...     print (x [1:])
    (6,)
    (9,)

    >>> for x in sorted (q.attrs (Q.left, Q.SUM (Q.points), Q.SUM (1)).group_by (Q.left), key = TFL.Getter [1]) :
    ...     print (x [1:])
    (6, 3)
    (9, 3)

    >>> for x in sorted (q.attrs (Q.left, Q.SUM (Q.points), Q.SUM (Q.points) / Q.SUM (1)).group_by (Q.left), key = TFL.Getter [1]) :
    ...     print (x [1:])
    (6, 2.0)
    (9, 3.0)

    >>> for x in sorted (q.attrs (Q.left, Q.SUM (Q.points), Q.SUM (Q.points) // Q.SUM (1)).group_by (Q.left), key = TFL.Getter [1]) :
    ...     print (x [1:])
    (6, 2)
    (9, 3)

    >>> for x in sorted (q.attrs (Q.left, Q.MIN (Q.points), Q.MAX (Q.points), Q.AVG (Q.points), Q.COUNT (Q.points)).group_by (Q.left), key = TFL.Getter [1]) :
    ...     print (", ".join (tuple ("%%g" %% (y, ) for y in x [1:])))
    1, 3, 2, 3
    1, 6, 3, 3

"""

_test_referential_integrity = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> PAP = scope.PAP
    >>> SRM = scope.SRM
    >>> BiR = SRM.Boat_in_Regatta
    >>> bc  = SRM.Boat_Class ("Optimist", max_crew = 1, raw = True)
    >>> cl  = SRM.Club ("SC-AMS", raw = True)
    >>> b   = SRM.Boat ('Optimist', "1107", "AUT", raw = True)
    >>> p   = PAP.Person ("Tanzer", "Christian", raw = True)
    >>> s   = SRM.Sailor (p, nation = "AUT", mna_number = "29676", club = cl, raw = True) ### 1
    >>> rev = SRM.Regatta_Event ("Himmelfahrt", ("20080501", ), raw = True)
    >>> reg = SRM.Regatta_C (rev.epk_raw, bc.epk_raw, raw = True)
    >>> bir = BiR (b, reg, skipper = s)

    >>> scope.commit ()

    >>> bir                                           ### before s.destroy ()
    SRM.Boat_in_Regatta ((('optimist', ), 1107, 'AUT', ''), (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', )))
    >>> print (bir.pid)                               ### before s.destroy ()
    8
    >>> print (cl.pid)                                ### before s.destroy ()
    2
    >>> print (s.pid)                                 ### before s.destroy ()
    5
    >>> print (bir.skipper)                           ### before s.destroy () 1
    (('tanzer', 'christian', '', ''), 'AUT', 29676, ('scams', ))
    >>> bir.last_cid                                  ### before s.destroy ()
    8
    >>> scope.MOM.Id_Entity.query_s ().count ()       ### before s.destroy ()
    8
    >>> scope.MOM.Id_Entity.query_s ().all ()         ### before s.destroy ()
    [SRM.Regatta_Event ('himmelfahrt', ('2008-05-01', '2008-05-01')), SRM.Regatta_C (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', )), SRM.Boat_Class ('optimist'), SRM.Boat (('optimist', ), 1107, 'AUT', ''), SRM.Boat_in_Regatta ((('optimist', ), 1107, 'AUT', ''), (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', ))), SRM.Club ('scams'), PAP.Person ('tanzer', 'christian', '', ''), SRM.Sailor (('tanzer', 'christian', '', ''), 'AUT', 29676, ('scams', ))]

    >>> with expect_except (MOM.Error.Required_Empty) :
    ...     bir.skipper = None
    Required_Empty: Condition `skipper_not_empty` : The attribute skipper needs a non-empty value
        skipper = None
    >>> with expect_except (MOM.Error.Invariants) :
    ...     bir.set (skipper = None)
    Invariants: Condition `skipper_not_empty` : The attribute skipper needs a non-empty value
        skipper = None
    >>> print (bir.skipper)                           ### before s.destroy () 2
    (('tanzer', 'christian', '', ''), 'AUT', 29676, ('scams', ))

    >>> scope.max_cid                                 ### before s.destroy ()
    8

    >>> print (s.club)                                ### before s.destroy ()
    ('scams')

    >>> if hasattr (scope.ems.session, "expunge") : scope.ems.session.expunge ()
    >>> cl.destroy ()
    >>> print (s.club)                                ### after cl.destroy ()
    None

    >>> scope.max_cid                                 ### after cl.destroy ()
    10
    >>> bir.last_cid                                  ### after cl.destroy ()
    8
    >>> print (bir)                                   ### after cl.destroy ()
    ((('optimist', ), 1107, 'AUT', ''), (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', )))
    >>> print (s.pid)                                 ### after cl.destroy ()
    5
    >>> print (bir.skipper)                           ### after cl.destroy ()
    (('tanzer', 'christian', '', ''), 'AUT', 29676, '')

    >>> scope.pid_query (s.pid)
    SRM.Sailor (('tanzer', 'christian', '', ''), 'AUT', 29676, '')

    >>> s.destroy ()

    >>> scope.max_cid                                 ### after s.destroy ()
    12

    >>> bir.last_cid                                  ### after s.destroy ()
    8
    >>> with expect_except (MOM.Error.Destroyed_Entity) :
    ...     bir.left
    Destroyed_Entity: <Destroyed entity SRM.Boat_in_Regatta ((('optimist', ), 1107, 'AUT', ''), (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', )))>: access to attribute 'left' not allowed
    >>> scope.MOM.Id_Entity.query_s ().count ()       ### after s.destroy ()
    5
    >>> scope.MOM.Id_Entity.query_s ().all ()         ### after s.destroy ()
    [SRM.Regatta_Event ('himmelfahrt', ('2008-05-01', '2008-05-01')), SRM.Regatta_C (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', )), SRM.Boat_Class ('optimist'), SRM.Boat (('optimist', ), 1107, 'AUT', ''), PAP.Person ('tanzer', 'christian', '', '')]

    >>> bir                                           ### after s.destroy ()
    <Destroyed entity SRM.Boat_in_Regatta ((('optimist', ), 1107, 'AUT', ''), (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', )))>

    >>> with expect_except (MOM.Error.Destroyed_Entity) :
    ...     print (bir.skipper)                           ### after s.destroy ()
    Destroyed_Entity: <Destroyed entity SRM.Boat_in_Regatta ((('optimist', ), 1107, 'AUT', ''), (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', )))>: access to attribute 'skipper' not allowed

    >>> for c in scope.uncommitted_changes :
    ...     show_change (c)
    <Destroy SRM.Club ('SC-AMS', 'SRM.Club'), old-values = {'last_cid' : '<n>'}>
        <Modify SRM.Sailor (('Tanzer', 'Christian', '', '', 'PAP.Person'), 'AUT', '29676', '', 'SRM.Sailor'), old-values = {'club' : 2, 'last_cid' : '<n>'}, new-values = {'club' : '', 'last_cid' : '<n>'}>
    <Destroy SRM.Sailor (('Tanzer', 'Christian', '', '', 'PAP.Person'), 'AUT', '29676', '', 'SRM.Sailor'), old-values = {'last_cid' : '<n>'}>
        <Destroy SRM.Boat_in_Regatta ((('Optimist', 'SRM.Boat_Class'), '1107', 'AUT', '', 'SRM.Boat'), (('Himmelfahrt', (('finish', '2008-05-01'), ('start', '2008-05-01')), 'SRM.Regatta_Event'), ('Optimist', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), old-values = {'last_cid' : '<n>', 'registration_date' : '<today>', 'skipper' : 5}>

    >>> for c in scope.uncommitted_changes :
    ...     print (c.cid, c.pid, c.type_name, portable_repr (c.epk_pid))
    ...     for cc in c.children :
    ...         print ("   ", cc.cid, cc.pid, cc.type_name, portable_repr (cc.epk_pid))
    10 2 SRM.Club ('SC-AMS', 'SRM.Club')
        9 5 SRM.Sailor (4, 'AUT', '29676', '', 'SRM.Sailor')
    12 5 SRM.Sailor (4, 'AUT', '29676', '', 'SRM.Sailor')
        11 8 SRM.Boat_in_Regatta (3, 7, 'SRM.Boat_in_Regatta')

    >>> undo_changes (scope, list (reversed (scope.uncommitted_changes [-1:])))

    >>> for c in scope.uncommitted_changes :
    ...     show_change (c)
    <Destroy SRM.Club ('SC-AMS', 'SRM.Club'), old-values = {'last_cid' : '<n>'}>
        <Modify SRM.Sailor (('Tanzer', 'Christian', '', '', 'PAP.Person'), 'AUT', '29676', '', 'SRM.Sailor'), old-values = {'club' : 2, 'last_cid' : '<n>'}, new-values = {'club' : '', 'last_cid' : '<n>'}>
    <Destroy SRM.Sailor (('Tanzer', 'Christian', '', '', 'PAP.Person'), 'AUT', '29676', '', 'SRM.Sailor'), old-values = {'last_cid' : '<n>'}>
        <Destroy SRM.Boat_in_Regatta ((('Optimist', 'SRM.Boat_Class'), '1107', 'AUT', '', 'SRM.Boat'), (('Himmelfahrt', (('finish', '2008-05-01'), ('start', '2008-05-01')), 'SRM.Regatta_Event'), ('Optimist', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), old-values = {'last_cid' : '<n>', 'registration_date' : '<today>', 'skipper' : 5}>
    <Create SRM.Sailor (('Tanzer', 'Christian', '', '', 'PAP.Person'), 'AUT', '29676', '', 'SRM.Sailor'), new-values = {'last_cid' : '<n>'}>
    <Create SRM.Boat_in_Regatta ((('Optimist', 'SRM.Boat_Class'), '1107', 'AUT', '', 'SRM.Boat'), (('Himmelfahrt', (('finish', '2008-05-01'), ('start', '2008-05-01')), 'SRM.Regatta_Event'), ('Optimist', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), new-values = {'last_cid' : '<n>', 'registration_date' : '<today>', 'skipper' : 5}>

"""

_test_undo = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> PAP = scope.PAP
    >>> SRM = scope.SRM
    >>> BiR = SRM.Boat_in_Regatta
    >>> bc  = SRM.Boat_Class ("Optimist", max_crew = 1, raw = True)
    >>> cl  = SRM.Club ("SC-AMS", raw = True)
    >>> b   = SRM.Boat ('Optimist', "1107", "AUT", raw = True)
    >>> p   = PAP.Person ("Tanzer", "Christian", raw = True)
    >>> s   = SRM.Sailor (p, nation = "AUT", mna_number = "29676", club = cl, raw = True) ### 1
    >>> rev = SRM.Regatta_Event ("Himmelfahrt", ("20080501", ), raw = True)
    >>> reg = SRM.Regatta_C (rev, bc)
    >>> bir = BiR (b, reg, skipper = s)

    >>> scope.commit ()

    >>> for _e in scope.MOM.Id_Entity.query_s () : ### 1
    ...    print (_e.pid, _e.as_code ())
    6 SRM.Regatta_Event ('himmelfahrt', ('2008-05-01', '2008-05-01'), )
    7 SRM.Regatta_C (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', ), is_cancelled = 'no')
    1 SRM.Boat_Class ('optimist', max_crew = 1)
    3 SRM.Boat (('optimist', ), 1107, 'AUT', '', )
    8 SRM.Boat_in_Regatta ((('optimist', ), 1107, 'AUT', ''), (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', )), skipper = (("'tanzer'", "'christian'", "''", "''"), "'AUT'", '29676', ("'scams'",)))
    2 SRM.Club ('scams', )
    4 PAP.Person ('tanzer', 'christian', '', '', )
    5 SRM.Sailor (('tanzer', 'christian', '', ''), 'AUT', 29676, ('scams', ), )

    >>> print (sorted (scope.MOM.Id_Entity.query ().attr ("pid"))) ### 2
    [1, 2, 3, 4, 5, 6, 7, 8]

    >>> s                   ### before first destroy
    SRM.Sailor (('tanzer', 'christian', '', ''), 'AUT', 29676, ('scams', ))

    >>> cl                  ### before first destroy
    SRM.Club ('scams')
    >>> cl.last_cid, s.last_cid, scope.max_cid
    (2, 5, 8)
    >>> cl.destroy ()

    >>> s                   ### after first destroy
    SRM.Sailor (('tanzer', 'christian', '', ''), 'AUT', 29676, '')

    >>> cl                  ### after first destroy
    <Destroyed entity SRM.Club ('scams')>
    >>> s.last_cid, scope.max_cid
    (9, 10)
    >>> for c in scope.uncommitted_changes : ### after first destroy
    ...     show_change (c)
    <Destroy SRM.Club ('SC-AMS', 'SRM.Club'), old-values = {'last_cid' : '<n>'}>
        <Modify SRM.Sailor (('Tanzer', 'Christian', '', '', 'PAP.Person'), 'AUT', '29676', '', 'SRM.Sailor'), old-values = {'club' : 2, 'last_cid' : '<n>'}, new-values = {'club' : '', 'last_cid' : '<n>'}>

    >>> print (sorted (scope.MOM.Id_Entity.query ().attr ("pid"))) ### 3
    [1, 3, 4, 5, 6, 7, 8]

    >>> scope.rollback ()   ### first rollback
    >>> for c in scope.uncommitted_changes :
    ...     show_change (c)

    >>> print (sorted (scope.MOM.Id_Entity.query ().attr ("pid"))) ### 3.5
    [1, 2, 3, 4, 5, 6, 7, 8]

    >>> s                   ### after first rollback
    SRM.Sailor (('tanzer', 'christian', '', ''), 'AUT', 29676, ('scams', ))

    >>> cl                  ### after first rollback
    SRM.Club ('scams')

    >>> cl_revived = SRM.Club.instance ("SC-AMS")
    >>> cl_revived
    SRM.Club ('scams')
    >>> cl_revived.last_cid
    2
    >>> MOM.BREAK = True*0
    >>> cl_revived.destroy ()

    >>> s                   ### after second destroy
    SRM.Sailor (('tanzer', 'christian', '', ''), 'AUT', 29676, '')

    >>> for c in scope.query_changes () : ### after second destroy of club
    ...     print (clean_change (c))
    <Create SRM.Boat_Class ('Optimist', 'SRM.Boat_Class'), new-values = {'last_cid' : '<n>', 'max_crew' : '1'}>
    <Create SRM.Club ('SC-AMS', 'SRM.Club'), new-values = {'last_cid' : '<n>'}>
    <Create SRM.Boat (('Optimist', 'SRM.Boat_Class'), '1107', 'AUT', '', 'SRM.Boat'), new-values = {'last_cid' : '<n>'}>
    <Create PAP.Person ('Tanzer', 'Christian', '', '', 'PAP.Person'), new-values = {'last_cid' : '<n>'}>
    <Create SRM.Sailor (('Tanzer', 'Christian', '', '', 'PAP.Person'), 'AUT', '29676', ('SC-AMS', 'SRM.Club'), 'SRM.Sailor'), new-values = {'last_cid' : '<n>'}>
    <Create SRM.Regatta_Event ('Himmelfahrt', (('finish', '2008-05-01'), ('start', '2008-05-01')), 'SRM.Regatta_Event'), new-values = {'last_cid' : '<n>', 'perma_name' : 'himmelfahrt'}>
    <Create SRM.Regatta_C (('Himmelfahrt', (('finish', '2008-05-01'), ('start', '2008-05-01')), 'SRM.Regatta_Event'), ('Optimist', 'SRM.Boat_Class'), 'SRM.Regatta_C'), new-values = {'is_cancelled' : 'no', 'last_cid' : '<n>', 'perma_name' : 'optimist'}>
    <Create SRM.Boat_in_Regatta ((('Optimist', 'SRM.Boat_Class'), '1107', 'AUT', '', 'SRM.Boat'), (('Himmelfahrt', (('finish', '2008-05-01'), ('start', '2008-05-01')), 'SRM.Regatta_Event'), ('Optimist', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), new-values = {'last_cid' : '<n>', 'registration_date' : '<today>', 'skipper' : 5}>
    <Modify SRM.Sailor (('Tanzer', 'Christian', '', '', 'PAP.Person'), 'AUT', '29676', '', 'SRM.Sailor'), old-values = {'club' : 2, 'last_cid' : '<n>'}, new-values = {'club' : '', 'last_cid' : '<n>'}>
    <Destroy SRM.Club ('SC-AMS', 'SRM.Club'), old-values = {'last_cid' : '<n>'}>
        <Modify SRM.Sailor (('Tanzer', 'Christian', '', '', 'PAP.Person'), 'AUT', '29676', '', 'SRM.Sailor'), old-values = {'club' : 2, 'last_cid' : '<n>'}, new-values = {'club' : '', 'last_cid' : '<n>'}>

    >>> s.destroy ()

    >>> cl_revived  ### after second destroy
    <Destroyed entity SRM.Club ('scams')>
    >>> s  ### after second destroy
    <Destroyed entity SRM.Sailor (('tanzer', 'christian', '', ''), 'AUT', 29676, '')>

    >>> for c in scope.uncommitted_changes : ### after second destroy
    ...     show_change (c)
    <Destroy SRM.Club ('SC-AMS', 'SRM.Club'), old-values = {'last_cid' : '<n>'}>
        <Modify SRM.Sailor (('Tanzer', 'Christian', '', '', 'PAP.Person'), 'AUT', '29676', '', 'SRM.Sailor'), old-values = {'club' : 2, 'last_cid' : '<n>'}, new-values = {'club' : '', 'last_cid' : '<n>'}>
    <Destroy SRM.Sailor (('Tanzer', 'Christian', '', '', 'PAP.Person'), 'AUT', '29676', '', 'SRM.Sailor'), old-values = {'last_cid' : '<n>'}>
        <Destroy SRM.Boat_in_Regatta ((('Optimist', 'SRM.Boat_Class'), '1107', 'AUT', '', 'SRM.Boat'), (('Himmelfahrt', (('finish', '2008-05-01'), ('start', '2008-05-01')), 'SRM.Regatta_Event'), ('Optimist', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), old-values = {'last_cid' : '<n>', 'registration_date' : '<today>', 'skipper' : 5}>
    >>> print (sorted (scope.MOM.Id_Entity.query ().attr ("pid"))) ### 4
    [1, 3, 4, 6, 7]

    >>> scope.rollback ()   ### second rollback

    >>> cl  ### after second rollback
    SRM.Club ('scams')
    >>> s   ### after second rollback
    SRM.Sailor (('tanzer', 'christian', '', ''), 'AUT', 29676, ('scams', ))

    >>> for c in scope.uncommitted_changes : ### after second rollback
    ...     show_change (c)


    >>> for _e in scope.MOM.Id_Entity.query_s () : ### 5
    ...    print (_e.pid, _e.as_code ())
    6 SRM.Regatta_Event ('himmelfahrt', ('2008-05-01', '2008-05-01'), )
    7 SRM.Regatta_C (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', ), is_cancelled = 'no')
    1 SRM.Boat_Class ('optimist', max_crew = 1)
    3 SRM.Boat (('optimist', ), 1107, 'AUT', '', )
    8 SRM.Boat_in_Regatta ((('optimist', ), 1107, 'AUT', ''), (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', )), skipper = (("'tanzer'", "'christian'", "''", "''"), "'AUT'", '29676', ("'scams'",)))
    2 SRM.Club ('scams', )
    4 PAP.Person ('tanzer', 'christian', '', '', )
    5 SRM.Sailor (('tanzer', 'christian', '', ''), 'AUT', 29676, ('scams', ), )

    >>> print (sorted (scope.MOM.Id_Entity.query ().attr ("pid"))) ### 6
    [1, 2, 3, 4, 5, 6, 7, 8]


"""

from   _GTW.__test__.model import *
from   _TFL.predicate      import first
from   _TFL.Regexp         import Multi_Re_Replacer, Re_Replacer, re
from   datetime            import datetime

_clean_change = Multi_Re_Replacer \
    ( Re_Replacer
        ( r"'%s'" % (datetime.now ().strftime("%Y/%m/%d"), )
        , r"'<today>'"
        )
    , Re_Replacer
        ( r"'%s'" % (datetime.now ().strftime("%Y-%m-%d"), )
        , r"'<today>'"
        )
    , Re_Replacer
        ( r"'last_cid' : '\d+'"
        , r"'last_cid' : '<n>'"
        )
    )

def clean_change (c) :
    result = portable_repr (c)
    result = _clean_change (result)
    return result
# end def clean_change

def show_change (c) :
    print (clean_change (c))
# end def show_changes

def show_dep (x) :
    if x and x.dependencies :
        for k, v in sorted (pyk.iteritems (x.dependencies), key = TFL.Getter [0].ui_display) :
            print (k, ":", v)
    else :
        print ("---")

def show_ora (x) :
    if x and x.object_referring_attributes :
        for k, vs in sorted (pyk.iteritems (x.object_referring_attributes)) :
            print (k, ":", ", ".join (str (v) for v in vs))
    else :
        print ("---")

def undo_changes (scope, changes) :
    for c in changes :
        c.undo (scope)
# end def undo_change

__test__ = Scaffold.create_test_dict \
    ( dict
        ( normal        = _test_code
        , delayed       = _test_delayed
        , polymorph     = _test_polymorph
        , qr_grouped_by = _test_qr_grouped_by
        , ref_int       = _test_referential_integrity
        , undo          = _test_undo
        )
    )

### __END__ GTW.__test__.Boat_in_Regatta
