# -*- coding: utf-8 -*-
# Copyright (C) 2010-2016 Mag. Christian Tanzer All rights reserved
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
#    GTW.__test__.SCM_Summary
#
# Purpose
#    Test change summaries (MOM.SCM.Summary)
#
# Revision Dates
#     3-Sep-2010 (CT) Creation
#     8-Sep-2010 (CT) Creation continued..
#     9-Sep-2010 (CT) Creation continued...
#    14-Sep-2010 (CT) Creation continued....
#    19-Mar-2012 (CT) Adapt to reification of `SRM.Handicap`
#    12-Sep-2012 (CT) Adapt to recording of electric changes
#    12-Oct-2012 (CT) Adapt to repr change of `An_Entity`
#    15-Apr-2013 (CT) Adapt to change of `MOM.Attr.Kind.reset`
#    24-Apr-2013 (CT) Add test `no_net`; adapt to change of `MOM.SCM.Summary`
#     5-May-2015 (CT) Add tests for `as_json_cargo`
#     5-May-2015 (CT) Add test for `scope.add_after_commit_callback`
#     5-May-2016 (CT) Use `A_Date.now`
#    ««revision-date»»···
#--

from   __future__                    import print_function, unicode_literals

from   _GTW.__test__.model           import *
from   _GTW.__test__.Boat_in_Regatta import clean_change, show_change

from   _TFL.Regexp                   import Multi_Re_Replacer, Re_Replacer, re

import datetime

time_cleaner = Multi_Re_Replacer \
    ( Re_Replacer
        ( r"'c_time' : '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d+'"
        , r"'c_time' : <datetime>"
        )
    , Re_Replacer
        ( r"'c_time' : datetime.datetime\(\d+, \d+, \d+, \d+, \d+, \d+, \d+\)"
        , r"'c_time' : <datetime>"
        )
    , Re_Replacer
        ( r"'time' : '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d+'"
        , r"'time' : <datetime>"
        )
    , Re_Replacer
        ( r"'time' : datetime.datetime\(\d+, \d+, \d+, \d+, \d+, \d+, \d+\)"
        , r"'time' : <datetime>"
        )
    )

def log_commits (scope, change_summary) :
    print ("Commited %s changes" % len (change_summary))
# end def log_commits

_basic = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> scope.add_after_commit_callback (log_commits)

    >>> date = (("start", A_Date.as_string (A_Date.now ())), )
    >>> PAP   = scope.PAP
    >>> SRM   = scope.SRM
    >>> EVT   = scope.EVT
    >>> SWP   = scope.SWP
    >>> RR    = EVT.Recurrence_Rule
    >>> RS    = EVT.Recurrence_Spec
    >>> bc    = SRM.Boat_Class (u"Optimist",          max_crew = 1)
    >>> _     = SRM.Boat_Class (u"420er",             max_crew = 2)
    >>> _     = SRM.Boat_Class (u"Laser",             max_crew = 1)
    >>> x     = SRM.Boat_Class (u"Seascape 18",       max_crew = 4)
    >>> ys    = SRM.Handicap ("Yardstick")
    >>> b     = SRM.Boat.instance_or_new ('Optimist', u"1107", u"AUT", raw = True)
    >>> c     = b.copy (b.left, nation = b.nation, sail_number = "1134")
    >>> p     = PAP.Person.instance_or_new (u"Tanzer", u"Laurens")
    >>> s     = SRM.Sailor.instance_or_new (p, nation = u"AUT", mna_number = u"29676", raw = True) ### 1
    >>> rev   = SRM.Regatta_Event (u"Himmelfahrt", (u"20080501", ), raw = True)
    >>> reg   = SRM.Regatta_C (rev, bc)
    >>> reh   = SRM.Regatta_H (rev, ys)
    >>> bir   = SRM.Boat_in_Regatta (b, reg, skipper = s)
    >>> r1    = SRM.Race_Result (bir, 1, points = 8)
    >>> r2    = SRM.Race_Result (bir, 2, points = 4)
    >>> p1    = SWP.Page ("event-1-text", text = "Text for the 1. event", date = date)
    >>> p2    = SWP.Page ("event-2-text", text = "Text for the 2. event", date = date)
    >>> e1    = EVT.Event (p1.epk, ("2010-08-18", ))
    >>> rs1   = RS (e1, date_exceptions = ["2010-08-15"])
    >>> rr1   = RR (rs1, start = "20100801", count = 7, unit = "Weekly", raw = True)
    >>>
    >>> _     = rev.date.set (start = "2010-05-13", finish = "2010-05-13")
    >>> _     = bc.set (loa = 2.43)
    >>> _     = p.set_raw (title = "Mr.", middle_name = "William")
    >>> _     = r1.set (discarded = True)
    >>> _     = rev.date.set (finish = "2010-05-14")

    >>> x
    SRM.Boat_Class ('seascape 18')
    >>> xtn = x.type_name
    >>> sort_by_cid = TFL.Sorted_By ("-cid")
    >>> int (scope.query_changes (Q.type_name == xtn).order_by (sort_by_cid).first().cid) ### before x.destroy ()
    31
    >>> x.destroy ()
    >>> int (scope.query_changes (Q.type_name == xtn).order_by (sort_by_cid).first().cid) ### after x.destroy ()
    35

    >>> rev.date.finish = datetime.date (2010, 5, 13)
    >>> rs1.dates.append (datetime.datetime (2010, 9, 8, 0, 0))
    >>> rs1.dates.append (datetime.datetime (2010, 10, 8, 0, 0))

    >>> ucc  = csm1 = scope.uncommitted_changes

    >>> for csp in ucc.changes :
    ...     show_change (csp)
    <Create SRM.Boat_Class ('Optimist', 'SRM.Boat_Class'), new-values = {'last_cid' : '<n>', 'max_crew' : '1'}>
    <Create SRM.Boat_Class ('420er', 'SRM.Boat_Class'), new-values = {'last_cid' : '<n>', 'max_crew' : '2'}>
    <Create SRM.Boat_Class ('Laser', 'SRM.Boat_Class'), new-values = {'last_cid' : '<n>', 'max_crew' : '1'}>
    <Create SRM.Boat_Class ('Seascape 18', 'SRM.Boat_Class'), new-values = {'last_cid' : '<n>'}>
    <Create SRM.Handicap ('Yardstick', 'SRM.Handicap'), new-values = {'last_cid' : '<n>'}>
    <Create SRM.Boat (('Optimist', 'SRM.Boat_Class'), '1107', 'AUT', '', 'SRM.Boat'), new-values = {'last_cid' : '<n>'}>
    <Copy SRM.Boat (('Optimist', 'SRM.Boat_Class'), '1134', 'AUT', '', 'SRM.Boat'), new-values = {'last_cid' : '<n>'}>
        <Create SRM.Boat (('Optimist', 'SRM.Boat_Class'), '1134', 'AUT', '', 'SRM.Boat'), new-values = {'last_cid' : '<n>'}>
    <Create PAP.Person ('Tanzer', 'Laurens', '', '', 'PAP.Person'), new-values = {'last_cid' : '<n>'}>
    <Create SRM.Sailor (('Tanzer', 'Laurens', '', '', 'PAP.Person'), 'AUT', '29676', '', 'SRM.Sailor'), new-values = {'last_cid' : '<n>'}>
    <Create SRM.Regatta_Event ('Himmelfahrt', (('finish', '2008-05-01'), ('start', '2008-05-01')), 'SRM.Regatta_Event'), new-values = {'last_cid' : '<n>', 'perma_name' : 'himmelfahrt'}>
    <Create SRM.Regatta_C (('Himmelfahrt', (('finish', '2008-05-01'), ('start', '2008-05-01')), 'SRM.Regatta_Event'), ('Optimist', 'SRM.Boat_Class'), 'SRM.Regatta_C'), new-values = {'is_cancelled' : 'no', 'last_cid' : '<n>', 'perma_name' : 'optimist'}>
    <Create SRM.Regatta_H (('Himmelfahrt', (('finish', '2008-05-01'), ('start', '2008-05-01')), 'SRM.Regatta_Event'), ('Yardstick', 'SRM.Handicap'), 'SRM.Regatta_H'), new-values = {'is_cancelled' : 'no', 'last_cid' : '<n>', 'perma_name' : 'yardstick'}>
    <Create SRM.Boat_in_Regatta ((('Optimist', 'SRM.Boat_Class'), '1107', 'AUT', '', 'SRM.Boat'), (('Himmelfahrt', (('finish', '2008-05-01'), ('start', '2008-05-01')), 'SRM.Regatta_Event'), ('Optimist', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), new-values = {'last_cid' : '<n>', 'registration_date' : '<today>', 'skipper' : 9}>
    <Create SRM.Race_Result (((('Optimist', 'SRM.Boat_Class'), '1107', 'AUT', '', 'SRM.Boat'), (('Himmelfahrt', (('finish', '2008-05-01'), ('start', '2008-05-01')), 'SRM.Regatta_Event'), ('Optimist', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), '1', 'SRM.Race_Result'), new-values = {'last_cid' : '<n>', 'points' : '8'}>
    <Create SRM.Race_Result (((('Optimist', 'SRM.Boat_Class'), '1107', 'AUT', '', 'SRM.Boat'), (('Himmelfahrt', (('finish', '2008-05-01'), ('start', '2008-05-01')), 'SRM.Regatta_Event'), ('Optimist', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), '2', 'SRM.Race_Result'), new-values = {'last_cid' : '<n>', 'points' : '4'}>
    <Create SWP.Page ('event-1-text', 'SWP.Page'), new-values = {'contents' : '<p>Text for the 1. event</p>\n', 'date' : (('start', '<today>'),), 'last_cid' : '<n>', 'text' : 'Text for the 1. event'}>
    <Create SWP.Page ('event-2-text', 'SWP.Page'), new-values = {'contents' : '<p>Text for the 2. event</p>\n', 'date' : (('start', '<today>'),), 'last_cid' : '<n>', 'text' : 'Text for the 2. event'}>
    <Create EVT.Event (('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), new-values = {'last_cid' : '<n>'}>
    <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-18', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
    <Create EVT.Recurrence_Spec ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), 'EVT.Recurrence_Spec'), new-values = {'date_exceptions' : '2010-08-15', 'last_cid' : '<n>'}>
    <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-18', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '<n>'}>
    <Create EVT.Recurrence_Rule (((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), 'EVT.Recurrence_Spec'), '', '', 'EVT.Recurrence_Rule'), new-values = {'count' : '7', 'last_cid' : '<n>', 'start' : '2010-08-01', 'unit' : 'Weekly'}>
    <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-01', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
    <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-08', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
    <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-22', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
    <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-29', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
    <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-09-05', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
    <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-09-12', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
    <Modify SRM.Regatta_Event ('Himmelfahrt', (('finish', '2010-05-13'), ('start', '2010-05-13')), 'SRM.Regatta_Event'), old-values = {'date' : (('finish', '2008-05-01'), ('start', '2008-05-01')), 'last_cid' : '<n>'}, new-values = {'date' : (('finish', '2010-05-13'), ('start', '2010-05-13')), 'last_cid' : '<n>'}>
    <Modify SRM.Boat_Class ('Optimist', 'SRM.Boat_Class'), old-values = {'last_cid' : '<n>', 'loa' : ''}, new-values = {'last_cid' : '<n>', 'loa' : '2.43'}>
    <Modify PAP.Person ('Tanzer', 'Laurens', 'William', 'Mr.', 'PAP.Person'), old-values = {'last_cid' : '<n>', 'middle_name' : '', 'title' : ''}, new-values = {'last_cid' : '<n>', 'middle_name' : 'William', 'title' : 'Mr.'}>
    <Modify SRM.Race_Result (((('Optimist', 'SRM.Boat_Class'), '1107', 'AUT', '', 'SRM.Boat'), (('Himmelfahrt', (('finish', '2010-05-13'), ('start', '2010-05-13')), 'SRM.Regatta_Event'), ('Optimist', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), '1', 'SRM.Race_Result'), old-values = {'discarded' : 'no', 'last_cid' : '<n>'}, new-values = {'discarded' : 'yes', 'last_cid' : '<n>'}>
    <Modify SRM.Regatta_Event ('Himmelfahrt', (('finish', '2010-05-14'), ('start', '2010-05-13')), 'SRM.Regatta_Event'), old-values = {'date' : (('finish', '2010-05-13'), ('start', '2010-05-13')), 'last_cid' : '<n>'}, new-values = {'date' : (('finish', '2010-05-14'), ('start', '2010-05-13')), 'last_cid' : '<n>'}>
    <Destroy SRM.Boat_Class ('Seascape 18', 'SRM.Boat_Class'), old-values = {'last_cid' : '<n>'}>
    <Modify/C SRM.Regatta_Event.date ('Himmelfahrt', (('finish', '2010-05-13'), ('start', '2010-05-13')), 'SRM.Regatta_Event'), old-values = {'finish' : '2010-05-14', 'last_cid' : '<n>'}, new-values = {'finish' : '2010-05-13', 'last_cid' : '<n>'}>
    <Modify EVT.Recurrence_Spec ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), 'EVT.Recurrence_Spec'), old-values = {'dates' : '', 'last_cid' : '<n>'}, new-values = {'dates' : '2010-09-08', 'last_cid' : '<n>'}>
    <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-01', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '<n>'}>
    <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-08', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '<n>'}>
    <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-22', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '<n>'}>
    <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-29', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '<n>'}>
    <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-09-05', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '<n>'}>
    <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-09-12', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '<n>'}>
    <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-01', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
    <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-08', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
    <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-22', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
    <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-29', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
    <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-09-05', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
    <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-09-08', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
    <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-09-12', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
    <Modify EVT.Recurrence_Spec ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), 'EVT.Recurrence_Spec'), old-values = {'dates' : '2010-09-08', 'last_cid' : '<n>'}, new-values = {'dates' : '2010-09-08,2010-10-08', 'last_cid' : '<n>'}>
    <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-01', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '<n>'}>
    <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-08', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '<n>'}>
    <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-22', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '<n>'}>
    <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-29', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '<n>'}>
    <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-09-05', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '<n>'}>
    <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-09-08', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '<n>'}>
    <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-09-12', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '<n>'}>
    <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-01', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
    <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-08', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
    <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-22', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
    <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-29', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
    <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-09-05', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
    <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-09-08', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
    <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-09-12', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
    <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-10-08', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>

    >>> for pid, csp in sorted (pyk.iteritems (ucc.by_pid)) : ### 1
    ...     show_change (csp)
    <Change Summary for pid 1: newborn, 1 change>
        <Create SRM.Boat_Class ('Optimist', 'SRM.Boat_Class'), new-values = {'last_cid' : '<n>', 'max_crew' : '1'}>
        <Modify SRM.Boat_Class ('Optimist', 'SRM.Boat_Class'), old-values = {'last_cid' : '<n>', 'loa' : ''}, new-values = {'last_cid' : '<n>', 'loa' : '2.43'}>
    <Change Summary for pid 2: newborn>
        <Create SRM.Boat_Class ('420er', 'SRM.Boat_Class'), new-values = {'last_cid' : '<n>', 'max_crew' : '2'}>
    <Change Summary for pid 3: newborn>
        <Create SRM.Boat_Class ('Laser', 'SRM.Boat_Class'), new-values = {'last_cid' : '<n>', 'max_crew' : '1'}>
    <Change Summary for pid 4: newborn, just died>
        <Create SRM.Boat_Class ('Seascape 18', 'SRM.Boat_Class'), new-values = {'last_cid' : '<n>'}>
        <Destroy SRM.Boat_Class ('Seascape 18', 'SRM.Boat_Class'), old-values = {'last_cid' : '<n>'}>
    <Change Summary for pid 5: newborn>
        <Create SRM.Handicap ('Yardstick', 'SRM.Handicap'), new-values = {'last_cid' : '<n>'}>
    <Change Summary for pid 6: newborn>
        <Create SRM.Boat (('Optimist', 'SRM.Boat_Class'), '1107', 'AUT', '', 'SRM.Boat'), new-values = {'last_cid' : '<n>'}>
    <Change Summary for pid 7: newborn, 1 change>
        <Create SRM.Boat (('Optimist', 'SRM.Boat_Class'), '1134', 'AUT', '', 'SRM.Boat'), new-values = {'last_cid' : '<n>'}>
        <Copy SRM.Boat (('Optimist', 'SRM.Boat_Class'), '1134', 'AUT', '', 'SRM.Boat'), new-values = {'last_cid' : '<n>'}>
          <Create SRM.Boat (('Optimist', 'SRM.Boat_Class'), '1134', 'AUT', '', 'SRM.Boat'), new-values = {'last_cid' : '<n>'}>
    <Change Summary for pid 8: newborn, 1 change>
        <Create PAP.Person ('Tanzer', 'Laurens', '', '', 'PAP.Person'), new-values = {'last_cid' : '<n>'}>
        <Modify PAP.Person ('Tanzer', 'Laurens', 'William', 'Mr.', 'PAP.Person'), old-values = {'last_cid' : '<n>', 'middle_name' : '', 'title' : ''}, new-values = {'last_cid' : '<n>', 'middle_name' : 'William', 'title' : 'Mr.'}>
    <Change Summary for pid 9: newborn>
        <Create SRM.Sailor (('Tanzer', 'Laurens', '', '', 'PAP.Person'), 'AUT', '29676', '', 'SRM.Sailor'), new-values = {'last_cid' : '<n>'}>
    <Change Summary for pid 10: newborn, 3 changes>
        <Create SRM.Regatta_Event ('Himmelfahrt', (('finish', '2008-05-01'), ('start', '2008-05-01')), 'SRM.Regatta_Event'), new-values = {'last_cid' : '<n>', 'perma_name' : 'himmelfahrt'}>
        <Modify SRM.Regatta_Event ('Himmelfahrt', (('finish', '2010-05-13'), ('start', '2010-05-13')), 'SRM.Regatta_Event'), old-values = {'date' : (('finish', '2008-05-01'), ('start', '2008-05-01')), 'last_cid' : '<n>'}, new-values = {'date' : (('finish', '2010-05-13'), ('start', '2010-05-13')), 'last_cid' : '<n>'}>
        <Modify SRM.Regatta_Event ('Himmelfahrt', (('finish', '2010-05-14'), ('start', '2010-05-13')), 'SRM.Regatta_Event'), old-values = {'date' : (('finish', '2010-05-13'), ('start', '2010-05-13')), 'last_cid' : '<n>'}, new-values = {'date' : (('finish', '2010-05-14'), ('start', '2010-05-13')), 'last_cid' : '<n>'}>
        <Modify/C SRM.Regatta_Event.date ('Himmelfahrt', (('finish', '2010-05-13'), ('start', '2010-05-13')), 'SRM.Regatta_Event'), old-values = {'finish' : '2010-05-14', 'last_cid' : '<n>'}, new-values = {'finish' : '2010-05-13', 'last_cid' : '<n>'}>
    <Change Summary for pid 11: newborn>
        <Create SRM.Regatta_C (('Himmelfahrt', (('finish', '2008-05-01'), ('start', '2008-05-01')), 'SRM.Regatta_Event'), ('Optimist', 'SRM.Boat_Class'), 'SRM.Regatta_C'), new-values = {'is_cancelled' : 'no', 'last_cid' : '<n>', 'perma_name' : 'optimist'}>
    <Change Summary for pid 12: newborn>
        <Create SRM.Regatta_H (('Himmelfahrt', (('finish', '2008-05-01'), ('start', '2008-05-01')), 'SRM.Regatta_Event'), ('Yardstick', 'SRM.Handicap'), 'SRM.Regatta_H'), new-values = {'is_cancelled' : 'no', 'last_cid' : '<n>', 'perma_name' : 'yardstick'}>
    <Change Summary for pid 13: newborn>
        <Create SRM.Boat_in_Regatta ((('Optimist', 'SRM.Boat_Class'), '1107', 'AUT', '', 'SRM.Boat'), (('Himmelfahrt', (('finish', '2008-05-01'), ('start', '2008-05-01')), 'SRM.Regatta_Event'), ('Optimist', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), new-values = {'last_cid' : '<n>', 'registration_date' : '<today>', 'skipper' : 9}>
    <Change Summary for pid 14: newborn, 1 change>
        <Create SRM.Race_Result (((('Optimist', 'SRM.Boat_Class'), '1107', 'AUT', '', 'SRM.Boat'), (('Himmelfahrt', (('finish', '2008-05-01'), ('start', '2008-05-01')), 'SRM.Regatta_Event'), ('Optimist', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), '1', 'SRM.Race_Result'), new-values = {'last_cid' : '<n>', 'points' : '8'}>
        <Modify SRM.Race_Result (((('Optimist', 'SRM.Boat_Class'), '1107', 'AUT', '', 'SRM.Boat'), (('Himmelfahrt', (('finish', '2010-05-13'), ('start', '2010-05-13')), 'SRM.Regatta_Event'), ('Optimist', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), '1', 'SRM.Race_Result'), old-values = {'discarded' : 'no', 'last_cid' : '<n>'}, new-values = {'discarded' : 'yes', 'last_cid' : '<n>'}>
    <Change Summary for pid 15: newborn>
        <Create SRM.Race_Result (((('Optimist', 'SRM.Boat_Class'), '1107', 'AUT', '', 'SRM.Boat'), (('Himmelfahrt', (('finish', '2008-05-01'), ('start', '2008-05-01')), 'SRM.Regatta_Event'), ('Optimist', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), '2', 'SRM.Race_Result'), new-values = {'last_cid' : '<n>', 'points' : '4'}>
    <Change Summary for pid 16: newborn>
        <Create SWP.Page ('event-1-text', 'SWP.Page'), new-values = {'contents' : '<p>Text for the 1. event</p>\n', 'date' : (('start', '<today>'),), 'last_cid' : '<n>', 'text' : 'Text for the 1. event'}>
    <Change Summary for pid 17: newborn>
        <Create SWP.Page ('event-2-text', 'SWP.Page'), new-values = {'contents' : '<p>Text for the 2. event</p>\n', 'date' : (('start', '<today>'),), 'last_cid' : '<n>', 'text' : 'Text for the 2. event'}>
    <Change Summary for pid 18: newborn>
        <Create EVT.Event (('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), new-values = {'last_cid' : '<n>'}>
    <Change Summary for pid 19: newborn, just died>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-18', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-18', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '<n>'}>
    <Change Summary for pid 20: newborn, 2 changes>
        <Create EVT.Recurrence_Spec ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), 'EVT.Recurrence_Spec'), new-values = {'date_exceptions' : '2010-08-15', 'last_cid' : '<n>'}>
        <Modify EVT.Recurrence_Spec ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), 'EVT.Recurrence_Spec'), old-values = {'dates' : '', 'last_cid' : '<n>'}, new-values = {'dates' : '2010-09-08', 'last_cid' : '<n>'}>
        <Modify EVT.Recurrence_Spec ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), 'EVT.Recurrence_Spec'), old-values = {'dates' : '2010-09-08', 'last_cid' : '<n>'}, new-values = {'dates' : '2010-09-08,2010-10-08', 'last_cid' : '<n>'}>
    <Change Summary for pid 21: newborn>
        <Create EVT.Recurrence_Rule (((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), 'EVT.Recurrence_Spec'), '', '', 'EVT.Recurrence_Rule'), new-values = {'count' : '7', 'last_cid' : '<n>', 'start' : '2010-08-01', 'unit' : 'Weekly'}>
    <Change Summary for pid 22: newborn, just died>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-01', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-01', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '<n>'}>
    <Change Summary for pid 23: newborn, just died>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-08', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-08', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '<n>'}>
    <Change Summary for pid 24: newborn, just died>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-22', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-22', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '<n>'}>
    <Change Summary for pid 25: newborn, just died>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-29', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-29', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '<n>'}>
    <Change Summary for pid 26: newborn, just died>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-09-05', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-09-05', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '<n>'}>
    <Change Summary for pid 27: newborn, just died>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-09-12', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-09-12', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '<n>'}>
    <Change Summary for pid 28: newborn, just died>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-01', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-01', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '<n>'}>
    <Change Summary for pid 29: newborn, just died>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-08', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-08', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '<n>'}>
    <Change Summary for pid 30: newborn, just died>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-22', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-22', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '<n>'}>
    <Change Summary for pid 31: newborn, just died>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-29', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-29', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '<n>'}>
    <Change Summary for pid 32: newborn, just died>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-09-05', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-09-05', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '<n>'}>
    <Change Summary for pid 33: newborn, just died>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-09-08', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-09-08', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '<n>'}>
    <Change Summary for pid 34: newborn, just died>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-09-12', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-09-12', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '<n>'}>
    <Change Summary for pid 35: newborn>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-01', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
    <Change Summary for pid 36: newborn>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-08', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
    <Change Summary for pid 37: newborn>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-22', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
    <Change Summary for pid 38: newborn>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-29', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
    <Change Summary for pid 39: newborn>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-09-05', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
    <Change Summary for pid 40: newborn>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-09-08', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
    <Change Summary for pid 41: newborn>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-09-12', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>
    <Change Summary for pid 42: newborn>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-10-08', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '<n>'}>

    >>> print (time_cleaner (formatted (ucc [0].as_json_cargo)))
    ( 'Create'
    , { '_new_attr' : {'max_crew' : '1'}
      , 'c_time' : <datetime>
      , 'c_user' : None
      , 'cid' : 1
      , 'epk' :
          ( 'Optimist'
          , 'SRM.Boat_Class'
          )
      , 'epk_pid' :
          ( 'Optimist'
          , 'SRM.Boat_Class'
          )
      , 'old_attr' : {}
      , 'pickle_cargo' :
          ( 'SRM.Boat_Class'
          , { 'beam' : (None,  )
            , 'electric' : (False,  )
            , 'last_cid' : (0,  )
            , 'loa' : (None,  )
            , 'max_crew' : (1,  )
            , 'name' :
                ( 'optimist'
                , 'Optimist'
                )
            , 'pid' : (1,  )
            , 'sail_area' : (None,  )
            , 'type_name' : ('SRM.Boat_Class',  )
            , 'x_locked' : (False,  )
            }
          , 1
          )
      , 'pid' : 1
      , 'time' : <datetime>
      , 'tool_version' :
          ( 'MOM-Test'
          , ( 0
            , 1
            , 2
            )
          )
      , 'type_name' : 'SRM.Boat_Class'
      , 'user' : None
      }
    , []
    )

    >>> ucc_json_cargo = ucc.as_json_cargo
    >>> ucc_restored   = MOM.SCM.Summary.from_json_cargo (ucc_json_cargo)
    >>> ucc is not ucc_restored
    True
    >>> not any (a is b for a, b in zip (ucc.changes, ucc_restored.changes))
    True
    >>> len (ucc) == len (ucc_restored)
    True
    >>> set (ucc.by_pid) == set (ucc_restored.by_pid)
    True
    >>> ucc.changed_attrs == ucc_restored.changed_attrs
    True

    >>> cjc = ucc_json_cargo [0]
    >>> with expect_except (TypeError) : # doctest:+ELLIPSIS
    ...     MOM.SCM.Change._Change_.from_json_cargo (("Foo", ) + cjc [1:])
    TypeError: Unknown Change class 'Foo' for restoring change from json-cargo ...

    >>> for pid, csp in sorted (pyk.iteritems (ucc.by_pid)) : ### 2
    ...   if csp :
    ...     print (csp.pid, clean_change (sorted (pyk.iteritems (csp.attribute_changes))))
    1 [('last_cid', (old = None, new = '31')), ('loa', (old = '', new = '2.43')), ('max_crew', (old = None, new = '1'))]
    2 [('last_cid', (old = None, new = '2')), ('max_crew', (old = None, new = '2'))]
    3 [('last_cid', (old = None, new = '3')), ('max_crew', (old = None, new = '1'))]
    5 [('last_cid', (old = None, new = '5'))]
    6 [('last_cid', (old = None, new = '6'))]
    7 [('last_cid', (old = None, new = '8'))]
    8 [('last_cid', (old = None, new = '32')), ('middle_name', (old = '', new = 'William')), ('title', (old = '', new = 'Mr.'))]
    9 [('last_cid', (old = None, new = '10'))]
    10 [('date', (old = (('finish', '2008-05-01'), ('start', '2008-05-01')), new = (('finish', '2010-05-13'), ('start', '2010-05-13')))), ('last_cid', (old = None, new = '36')), ('perma_name', (old = None, new = 'himmelfahrt'))]
    11 [('is_cancelled', (old = None, new = 'no')), ('last_cid', (old = None, new = '12')), ('perma_name', (old = None, new = 'optimist'))]
    12 [('is_cancelled', (old = None, new = 'no')), ('last_cid', (old = None, new = '13')), ('perma_name', (old = None, new = 'yardstick'))]
    13 [('last_cid', (old = None, new = '14')), ('registration_date', (old = None, new = '<today>')), ('skipper', (old = None, new = 9))]
    14 [('discarded', (old = 'no', new = 'yes')), ('last_cid', (old = None, new = '33')), ('points', (old = None, new = '8'))]
    15 [('last_cid', (old = None, new = '16')), ('points', (old = None, new = '4'))]
    16 [('contents', (old = None, new = '<p>Text for the 1. event</p>\n')), ('date', (old = None, new = (('start', '<today>'),))), ('last_cid', (old = None, new = '17')), ('text', (old = None, new = 'Text for the 1. event'))]
    17 [('contents', (old = None, new = '<p>Text for the 2. event</p>\n')), ('date', (old = None, new = (('start', '<today>'),))), ('last_cid', (old = None, new = '18')), ('text', (old = None, new = 'Text for the 2. event'))]
    18 [('last_cid', (old = None, new = '19'))]
    20 [('date_exceptions', (old = None, new = '2010-08-15')), ('dates', (old = '', new = '2010-09-08,2010-10-08')), ('last_cid', (old = None, new = '51'))]
    21 [('count', (old = None, new = '7')), ('last_cid', (old = None, new = '23')), ('start', (old = None, new = '2010-08-01')), ('unit', (old = None, new = 'Weekly'))]
    35 [('last_cid', (old = None, new = '59'))]
    36 [('last_cid', (old = None, new = '60'))]
    37 [('last_cid', (old = None, new = '61'))]
    38 [('last_cid', (old = None, new = '62'))]
    39 [('last_cid', (old = None, new = '63'))]
    40 [('last_cid', (old = None, new = '64'))]
    41 [('last_cid', (old = None, new = '65'))]
    42 [('last_cid', (old = None, new = '66'))]

    >>> for pid, ca in sorted (pyk.iteritems (ucc.changed_attrs)) :
    ...     print (pid, sorted (ca))
    1 ['last_cid', 'loa']
    2 ['last_cid']
    3 ['last_cid']
    5 ['last_cid']
    6 ['last_cid']
    7 ['last_cid']
    8 ['last_cid', 'middle_name', 'title']
    9 ['last_cid']
    10 ['date', 'last_cid']
    11 ['last_cid']
    12 ['last_cid']
    13 ['last_cid']
    14 ['discarded', 'last_cid']
    15 ['last_cid']
    16 ['last_cid']
    17 ['last_cid']
    18 ['last_cid']
    20 ['dates', 'last_cid']
    21 ['last_cid']
    35 ['last_cid']
    36 ['last_cid']
    37 ['last_cid']
    38 ['last_cid']
    39 ['last_cid']
    40 ['last_cid']
    41 ['last_cid']
    42 ['last_cid']

    >>> scope.commit ()
    Commited 65 changes

    >>> print (rs1.attr_as_code())
    (('event-1-text', ), ('2010-08-18', ), (), ''), dates = "'2010-09-08','2010-10-08'", date_exceptions = "'2010-08-15'"
    >>> rs1.set (date_exceptions = None)
    1
    >>> rs1.event.date.set (finish = datetime.date (2010, 8, 19), start = datetime.date (2010, 8, 13))
    1
    >>> rs1.dates.pop ()
    datetime.datetime(2010, 10, 8, 0, 0)

    >>> ucc = scope.uncommitted_changes
    >>> for pid, csp in sorted (pyk.iteritems (ucc.by_pid)) : ### 3
    ...     print (csp)
    <Change Summary for pid 18: 1 change>
        <Modify EVT.Event (('event-1-text', 'SWP.Page'), (('finish', '2010-08-19'), ('start', '2010-08-13')), '', '', 'EVT.Event'), old-values = {'date' : (('start', '2010-08-18'),), 'last_cid' : '19'}, new-values = {'date' : (('finish', '2010-08-19'), ('start', '2010-08-13')), 'last_cid' : '85'}>
    <Change Summary for pid 20: 2 changes>
        <Modify EVT.Recurrence_Spec ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), 'EVT.Recurrence_Spec'), old-values = {'date_exceptions' : '2010-08-15', 'last_cid' : '51'}, new-values = {'date_exceptions' : '', 'last_cid' : '67'}>
        <Modify EVT.Recurrence_Spec ((('event-1-text', 'SWP.Page'), (('finish', '2010-08-19'), ('start', '2010-08-13')), '', '', 'EVT.Event'), 'EVT.Recurrence_Spec'), old-values = {'dates' : '2010-09-08,2010-10-08', 'last_cid' : '67'}, new-values = {'dates' : '2010-09-08', 'last_cid' : '100'}>
    <Change Summary for pid 35: just died>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-01', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '59'}>
    <Change Summary for pid 36: just died>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-08', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '60'}>
    <Change Summary for pid 37: just died>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-22', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '61'}>
    <Change Summary for pid 38: just died>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-29', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '62'}>
    <Change Summary for pid 39: just died>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-09-05', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '63'}>
    <Change Summary for pid 40: just died>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-09-08', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '64'}>
    <Change Summary for pid 41: just died>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-09-12', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '65'}>
    <Change Summary for pid 42: just died>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-10-08', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '66'}>
    <Change Summary for pid 43: newborn, just died>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-01', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '76'}>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('finish', '2010-08-19'), ('start', '2010-08-13')), '', '', 'EVT.Event'), '2010-08-01', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '76'}>
    <Change Summary for pid 44: newborn, just died>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-08', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '77'}>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('finish', '2010-08-19'), ('start', '2010-08-13')), '', '', 'EVT.Event'), '2010-08-08', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '77'}>
    <Change Summary for pid 45: newborn, just died>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-15', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '78'}>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('finish', '2010-08-19'), ('start', '2010-08-13')), '', '', 'EVT.Event'), '2010-08-15', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '78'}>
    <Change Summary for pid 46: newborn, just died>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-22', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '79'}>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('finish', '2010-08-19'), ('start', '2010-08-13')), '', '', 'EVT.Event'), '2010-08-22', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '79'}>
    <Change Summary for pid 47: newborn, just died>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-08-29', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '80'}>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('finish', '2010-08-19'), ('start', '2010-08-13')), '', '', 'EVT.Event'), '2010-08-29', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '80'}>
    <Change Summary for pid 48: newborn, just died>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-09-05', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '81'}>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('finish', '2010-08-19'), ('start', '2010-08-13')), '', '', 'EVT.Event'), '2010-09-05', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '81'}>
    <Change Summary for pid 49: newborn, just died>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-09-08', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '82'}>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('finish', '2010-08-19'), ('start', '2010-08-13')), '', '', 'EVT.Event'), '2010-09-08', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '82'}>
    <Change Summary for pid 50: newborn, just died>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-09-12', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '83'}>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('finish', '2010-08-19'), ('start', '2010-08-13')), '', '', 'EVT.Event'), '2010-09-12', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '83'}>
    <Change Summary for pid 51: newborn, just died>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('start', '2010-08-18'),), '', '', 'EVT.Event'), '2010-10-08', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '84'}>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('finish', '2010-08-19'), ('start', '2010-08-13')), '', '', 'EVT.Event'), '2010-10-08', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '84'}>
    <Change Summary for pid 52: newborn, just died>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('finish', '2010-08-19'), ('start', '2010-08-13')), '', '', 'EVT.Event'), '2010-08-01', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '95'}>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('finish', '2010-08-19'), ('start', '2010-08-13')), '', '', 'EVT.Event'), '2010-08-01', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '95'}>
    <Change Summary for pid 53: newborn, just died>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('finish', '2010-08-19'), ('start', '2010-08-13')), '', '', 'EVT.Event'), '2010-08-08', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '96'}>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('finish', '2010-08-19'), ('start', '2010-08-13')), '', '', 'EVT.Event'), '2010-08-08', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '96'}>
    <Change Summary for pid 54: newborn, just died>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('finish', '2010-08-19'), ('start', '2010-08-13')), '', '', 'EVT.Event'), '2010-08-15', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '97'}>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('finish', '2010-08-19'), ('start', '2010-08-13')), '', '', 'EVT.Event'), '2010-08-15', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '97'}>
    <Change Summary for pid 55: newborn, just died>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('finish', '2010-08-19'), ('start', '2010-08-13')), '', '', 'EVT.Event'), '2010-09-08', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '98'}>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('finish', '2010-08-19'), ('start', '2010-08-13')), '', '', 'EVT.Event'), '2010-09-08', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '98'}>
    <Change Summary for pid 56: newborn, just died>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('finish', '2010-08-19'), ('start', '2010-08-13')), '', '', 'EVT.Event'), '2010-10-08', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '99'}>
        <Destroy EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('finish', '2010-08-19'), ('start', '2010-08-13')), '', '', 'EVT.Event'), '2010-10-08', '', 'EVT.Event_occurs'), old-values = {'last_cid' : '99'}>
    <Change Summary for pid 57: newborn>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('finish', '2010-08-19'), ('start', '2010-08-13')), '', '', 'EVT.Event'), '2010-08-01', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '106'}>
    <Change Summary for pid 58: newborn>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('finish', '2010-08-19'), ('start', '2010-08-13')), '', '', 'EVT.Event'), '2010-08-08', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '107'}>
    <Change Summary for pid 59: newborn>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('finish', '2010-08-19'), ('start', '2010-08-13')), '', '', 'EVT.Event'), '2010-08-15', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '108'}>
    <Change Summary for pid 60: newborn>
        <Create EVT.Event_occurs ((('event-1-text', 'SWP.Page'), (('finish', '2010-08-19'), ('start', '2010-08-13')), '', '', 'EVT.Event'), '2010-09-08', '', 'EVT.Event_occurs'), new-values = {'last_cid' : '109'}>

    >>> for pid, csp in sorted (pyk.iteritems (ucc.by_pid)) : ### 4
    ...   if csp :
    ...     print (csp.pid, clean_change (sorted (pyk.iteritems (csp.attribute_changes))))
    18 [('date', (old = (('start', '2010-08-18'),), new = (('finish', '2010-08-19'), ('start', '2010-08-13')))), ('last_cid', (old = '19', new = '85'))]
    20 [('date_exceptions', (old = '2010-08-15', new = '')), ('dates', (old = '2010-09-08,2010-10-08', new = '2010-09-08')), ('last_cid', (old = '51', new = '100'))]
    35 [('last_cid', (old = '59', new = None))]
    36 [('last_cid', (old = '60', new = None))]
    37 [('last_cid', (old = '61', new = None))]
    38 [('last_cid', (old = '62', new = None))]
    39 [('last_cid', (old = '63', new = None))]
    40 [('last_cid', (old = '64', new = None))]
    41 [('last_cid', (old = '65', new = None))]
    42 [('last_cid', (old = '66', new = None))]
    57 [('last_cid', (old = None, new = '106'))]
    58 [('last_cid', (old = None, new = '107'))]
    59 [('last_cid', (old = None, new = '108'))]
    60 [('last_cid', (old = None, new = '109'))]

    >>> for e, acs in ucc.entity_changes (scope) :
    ...     print (e.pid, clean_change (sorted (pyk.iteritems (acs))))
    18 [('date', (old = (('start', '2010-08-18'),), new = (('finish', '2010-08-19'), ('start', '2010-08-13')))), ('last_cid', (old = '19', new = '85'))]
    20 [('date_exceptions', (old = '2010-08-15', new = '')), ('dates', (old = '2010-09-08,2010-10-08', new = '2010-09-08')), ('last_cid', (old = '51', new = '100'))]
    57 [('last_cid', (old = None, new = '106'))]
    58 [('last_cid', (old = None, new = '107'))]
    59 [('last_cid', (old = None, new = '108'))]
    60 [('last_cid', (old = None, new = '109'))]

    >>> for e, acs in ucc.entity_changes (scope) :
    ...     e
    EVT.Event (('event-1-text', ), ('2010-08-13', '2010-08-19'), (), '')
    EVT.Recurrence_Spec ((('event-1-text', ), ('2010-08-13', '2010-08-19'), (), ''))
    EVT.Event_occurs ((('event-1-text', ), ('2010-08-13', '2010-08-19'), (), ''), '2010-08-01', ())
    EVT.Event_occurs ((('event-1-text', ), ('2010-08-13', '2010-08-19'), (), ''), '2010-08-08', ())
    EVT.Event_occurs ((('event-1-text', ), ('2010-08-13', '2010-08-19'), (), ''), '2010-08-15', ())
    EVT.Event_occurs ((('event-1-text', ), ('2010-08-13', '2010-08-19'), (), ''), '2010-09-08', ())

    >>> for pid, ca in sorted (pyk.iteritems (ucc.changed_attrs)) :
    ...     print (pid, sorted (ca))
    18 ['date', 'last_cid']
    20 ['date_exceptions', 'dates', 'last_cid']
    57 ['last_cid']
    58 ['last_cid']
    59 ['last_cid']
    60 ['last_cid']

    >>> scope.commit ()
    Commited 43 changes

    >>> SRM.Boat.query (sail_number = 1134).one ().destroy ()
    >>> b.destroy ()

    >>> ucc = scope.uncommitted_changes
    >>> for pid, csp in sorted (pyk.iteritems (ucc.by_pid)) : ### 5
    ...     show_change (csp)
    <Change Summary for pid 6: just died>
        <Destroy SRM.Boat (('Optimist', 'SRM.Boat_Class'), '1107', 'AUT', '', 'SRM.Boat'), old-values = {'last_cid' : '<n>'}>
          <Destroy SRM.Boat_in_Regatta ((('Optimist', 'SRM.Boat_Class'), '1107', 'AUT', '', 'SRM.Boat'), (('Himmelfahrt', (('finish', '2010-05-13'), ('start', '2010-05-13')), 'SRM.Regatta_Event'), ('Optimist', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), old-values = {'last_cid' : '<n>', 'registration_date' : '<today>', 'skipper' : 9}>
            <Destroy SRM.Race_Result (((('Optimist', 'SRM.Boat_Class'), '1107', 'AUT', '', 'SRM.Boat'), (('Himmelfahrt', (('finish', '2010-05-13'), ('start', '2010-05-13')), 'SRM.Regatta_Event'), ('Optimist', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), '1', 'SRM.Race_Result'), old-values = {'discarded' : 'yes', 'last_cid' : '<n>', 'points' : '8'}>
            <Destroy SRM.Race_Result (((('Optimist', 'SRM.Boat_Class'), '1107', 'AUT', '', 'SRM.Boat'), (('Himmelfahrt', (('finish', '2010-05-13'), ('start', '2010-05-13')), 'SRM.Regatta_Event'), ('Optimist', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), '2', 'SRM.Race_Result'), old-values = {'last_cid' : '<n>', 'points' : '4'}>
    <Change Summary for pid 7: just died>
        <Destroy SRM.Boat (('Optimist', 'SRM.Boat_Class'), '1134', 'AUT', '', 'SRM.Boat'), old-values = {'last_cid' : '<n>'}>
    <Change Summary for pid 13: just died>
        <Destroy SRM.Boat_in_Regatta ((('Optimist', 'SRM.Boat_Class'), '1107', 'AUT', '', 'SRM.Boat'), (('Himmelfahrt', (('finish', '2010-05-13'), ('start', '2010-05-13')), 'SRM.Regatta_Event'), ('Optimist', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), old-values = {'last_cid' : '<n>', 'registration_date' : '<today>', 'skipper' : 9}>
          <Destroy SRM.Race_Result (((('Optimist', 'SRM.Boat_Class'), '1107', 'AUT', '', 'SRM.Boat'), (('Himmelfahrt', (('finish', '2010-05-13'), ('start', '2010-05-13')), 'SRM.Regatta_Event'), ('Optimist', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), '1', 'SRM.Race_Result'), old-values = {'discarded' : 'yes', 'last_cid' : '<n>', 'points' : '8'}>
          <Destroy SRM.Race_Result (((('Optimist', 'SRM.Boat_Class'), '1107', 'AUT', '', 'SRM.Boat'), (('Himmelfahrt', (('finish', '2010-05-13'), ('start', '2010-05-13')), 'SRM.Regatta_Event'), ('Optimist', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), '2', 'SRM.Race_Result'), old-values = {'last_cid' : '<n>', 'points' : '4'}>
    <Change Summary for pid 14: just died>
        <Destroy SRM.Race_Result (((('Optimist', 'SRM.Boat_Class'), '1107', 'AUT', '', 'SRM.Boat'), (('Himmelfahrt', (('finish', '2010-05-13'), ('start', '2010-05-13')), 'SRM.Regatta_Event'), ('Optimist', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), '1', 'SRM.Race_Result'), old-values = {'discarded' : 'yes', 'last_cid' : '<n>', 'points' : '8'}>
    <Change Summary for pid 15: just died>
        <Destroy SRM.Race_Result (((('Optimist', 'SRM.Boat_Class'), '1107', 'AUT', '', 'SRM.Boat'), (('Himmelfahrt', (('finish', '2010-05-13'), ('start', '2010-05-13')), 'SRM.Regatta_Event'), ('Optimist', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), '2', 'SRM.Race_Result'), old-values = {'last_cid' : '<n>', 'points' : '4'}>

    >>> print (time_cleaner (formatted (ucc [0].as_json_cargo)))
    ( 'Destroy'
    , { '_new_attr' : {}
      , 'cid' : 110
      , 'epk' :
          ( ( 'Optimist'
            , 'SRM.Boat_Class'
            )
          , '1134'
          , 'AUT'
          , ''
          , 'SRM.Boat'
          )
      , 'epk_pid' :
          ( 1
          , '1134'
          , 'AUT'
          , ''
          , 'SRM.Boat'
          )
      , 'old_attr' : {'last_cid' : '8'}
      , 'pid' : 7
      , 'time' : <datetime>
      , 'tool_version' :
          ( 'MOM-Test'
          , ( 0
            , 1
            , 2
            )
          )
      , 'type_name' : 'SRM.Boat'
      , 'user' : None
      }
    , []
    )

    >>> for pid, csp in sorted (pyk.iteritems (ucc.by_pid)) : ### 6
    ...     print (csp.pid, clean_change (sorted (pyk.iteritems (csp.attribute_changes))))
    6 [('last_cid', (old = '6', new = None))]
    7 [('last_cid', (old = '8', new = None))]
    13 [('last_cid', (old = '14', new = None)), ('registration_date', (old = '<today>', new = None)), ('skipper', (old = 9, new = None))]
    14 [('discarded', (old = 'yes', new = None)), ('last_cid', (old = '33', new = None)), ('points', (old = '8', new = None))]
    15 [('last_cid', (old = '16', new = None)), ('points', (old = '4', new = None))]

    >>> for pid, ca in sorted (pyk.iteritems (ucc.changed_attrs)) :
    ...     print (pid, sorted (ca))

    >>> scope.commit ()
    Commited 2 changes

    >>> _ = p.lifetime.set (start = "1997-11-16")
    >>> _ = p.lifetime.set (finish = "2007-11-30")

    >>> ucc = scope.uncommitted_changes
    >>> for pid, csp in sorted (pyk.iteritems (ucc.by_pid)) : ### 7
    ...     print (csp)
    <Change Summary for pid 8: 2 changes>
        <Modify/C PAP.Person.lifetime ('Tanzer', 'Laurens', 'William', 'Mr.', 'PAP.Person'), old-values = {'last_cid' : '32', 'start' : ''}, new-values = {'last_cid' : '115', 'start' : '1997-11-16'}>
        <Modify/C PAP.Person.lifetime ('Tanzer', 'Laurens', 'William', 'Mr.', 'PAP.Person'), old-values = {'finish' : '', 'last_cid' : '115'}, new-values = {'finish' : '2007-11-30', 'last_cid' : '116'}>

    >>> print (time_cleaner (formatted (ucc [0].as_json_cargo)))
    ( 'Attr_Composite'
    , { '_new_attr' : {'start' : '1997-11-16'}
      , 'attr_name' : 'lifetime'
      , 'cid' : 115
      , 'epk' :
          ( 'Tanzer'
          , 'Laurens'
          , 'William'
          , 'Mr.'
          , 'PAP.Person'
          )
      , 'epk_pid' :
          ( 'Tanzer'
          , 'Laurens'
          , 'William'
          , 'Mr.'
          , 'PAP.Person'
          )
      , 'old_attr' :
          { 'last_cid' : '32'
          , 'start' : ''
          }
      , 'pid' : 8
      , 'time' : <datetime>
      , 'tool_version' :
          ( 'MOM-Test'
          , ( 0
            , 1
            , 2
            )
          )
      , 'type_name' : 'PAP.Person'
      , 'user' : None
      }
    , []
    )

    >>> for pid, csp in sorted (pyk.iteritems (ucc.by_pid)) : ### 8
    ...     print (csp.pid, clean_change (sorted (pyk.iteritems (csp.attribute_changes))))
    8 [('last_cid', (old = '32', new = '116')), ('lifetime', (old = (('finish', ''), ('start', '')), new = (('finish', '2007-11-30'), ('start', '1997-11-16'))))]

    >>> for pid, ca in sorted (pyk.iteritems (ucc.changed_attrs)) :
    ...     print (pid, sorted (ca))
    8 ['last_cid', 'lifetime']

    >>> len (csm1)
    65
    >>> conflicts, merges = csm1.change_conflicts ({}, scope)
    >>> sorted (conflicts), sorted (merges)
    ([], [])

"""

_no_net = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> PAP   = scope.PAP
    >>> p     = PAP.Person.instance_or_new (u"Tanzer", u"Laurens")

    >>> scope.commit ()

    >>> ucc = scope.uncommitted_changes
    >>> _   = p.set (title = "Mr.")

    >>> for pid, csp in sorted (pyk.iteritems (ucc.by_pid)) : ### 1
    ...     print (csp.pid, clean_change (sorted (pyk.iteritems (csp.attribute_changes))))
    1 [('last_cid', (old = '1', new = '2')), ('title', (old = '', new = 'Mr.'))]

    >>> _ = p.set (title = "")
    >>> for pid, csp in sorted (pyk.iteritems (ucc.by_pid)) : ### 2
    ...     print (csp.pid, clean_change (sorted (pyk.iteritems (csp.attribute_changes))))
    1 [('last_cid', (old = '1', new = '3'))]

    >>> scope.commit ()

    >>> ucc = scope.uncommitted_changes
    >>> _   = p.set (title = "Mr.")
    >>> for pid, csp in sorted (pyk.iteritems (ucc.by_pid)) : ### 3
    ...     print (csp.pid, clean_change (sorted (pyk.iteritems (csp.attribute_changes))))
    1 [('last_cid', (old = '3', new = '4')), ('title', (old = '', new = 'Mr.'))]

    >>> p.destroy ()
    >>> for pid, csp in sorted (pyk.iteritems (ucc.by_pid)) : ### 4
    ...     print (csp.pid, clean_change (sorted (pyk.iteritems (csp.attribute_changes))))
    1 [('last_cid', (old = '3', new = None)), ('title', (old = '', new = None))]

"""

_more = dict \
    ( conflicts = """

    >>> scope_1 = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> _ = scope_1.PAP.Person.instance_or_new (u"Tanzer", u"Laurens")
    >>> scope_1.commit ()

    >>> scope_2 = Scaffold.scope (%(p1)s, %(n1)s, create = False) # doctest:+ELLIPSIS
    Loading scope MOMT__...

    >>> p1  = scope_1.PAP.Person.instance (u"Tanzer", u"Laurens")
    >>> _   = p1.set (middle_name = u"William")
    >>> cs1 = scope_1.uncommitted_changes
    >>> len (cs1) ### 1
    1
    >>> for pid, csp in sorted (pyk.iteritems (cs1.by_pid)) :
    ...     print (csp)
    <Change Summary for pid 1: 1 change>
        <Modify PAP.Person ('Tanzer', 'Laurens', '', '', 'PAP.Person'), old-values = {'last_cid' : '1', 'middle_name' : ''}, new-values = {'last_cid' : '2', 'middle_name' : 'William'}>

    >>> p2 = scope_2.PAP.Person.instance (* p1.epk)
    >>> p2.middle_name
    ''
    >>> _ = p2.set (middle_name = u"W.")
    >>> cs2 = scope_2.uncommitted_changes
    >>> len (cs2) ### 1
    1
    >>> for pid, csp in sorted (pyk.iteritems (cs2.by_pid)) :
    ...     print (csp)
    <Change Summary for pid 1: 1 change>
        <Modify PAP.Person ('Tanzer', 'Laurens', '', '', 'PAP.Person'), old-values = {'last_cid' : '1', 'middle_name' : ''}, new-values = {'last_cid' : '3', 'middle_name' : 'W.'}>

    >>> scope_1.commit              ()
    >>> scope_1.ems.session.expunge ()
    >>> scope_2.commit              ()
    Traceback (most recent call last):
      ...
    Commit_Conflict

    >>> p2 = scope_2.PAP.Person.instance (* p1.epk)
    >>> p2.middle_name
    'W.'

    >>> p1 = scope_1.PAP.Person.instance (* p1.epk)
    >>> p1.middle_name
    'William'

    >>> scope_2.commit ()
    >>> scope_1.commit ()

    """
    )

Scaffold.Backend_Default_Path ["SQL"] = "'test.sqlite'"

__XXX__test__ = dict \
    ( Scaffold.create_test_dict (_more, ignore = ("HPS", "SQL"))
    , ** Scaffold.create_test_dict (_basic)
    )

__test__ = dict \
    ( ** Scaffold.create_test_dict
        ( dict
            ( basic  = _basic
            , no_net = _no_net
            )
        )
    )

### __END__ GTW.__test__.SCM_Summary
