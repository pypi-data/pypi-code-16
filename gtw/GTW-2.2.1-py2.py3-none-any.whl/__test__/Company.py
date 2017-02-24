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
#    GTW.__test__.Company
#
# Purpose
#    Test PAP.Company and descendents
#
# Revision Dates
#    26-Feb-2013 (CT) Creation
#     4-Mar-2013 (CT) Add tests for `PAP.Association`
#     6-Mar-2013 (CT) Adapt to new attribute `Company.registered_in`
#     6-Mar-2013 (CT) Add test for `polymorphic_epk` using `children_trans_iter`
#    19-Mar-2013 (CT) Add test for `AQ` for recursive attribute `affiliate`
#    19-Mar-2013 (CT) Add test for `AQ.Atoms`, `AQ.Unwrapped_Atoms`
#    11-May-2013 (CT) Add `test_entity_attr`
#    15-May-2013 (CT) Add test for `link_ref_attr`
#    24-Jul-2013 (CT) Add `test_saw`
#    13-Jun-2014 (RS) Fix tests for `PAP.Group`
#    29-Jul-2015 (CT) Adapt to name change of PAP.Phone attributes
#    24-Feb-2017 (CT) Import `MOM.Inspect`, not `MOM.inspect`
#    ««revision-date»»···
#--

from   __future__ import absolute_import, division, print_function, unicode_literals

_test_code = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> PAP = scope.PAP

    >>> p1 = PAP.Person ("Doe", "Jane", lifetime = ("20010101", ), raw = True)
    >>> bm = PAP.Biz_Man (p1)
    >>> cp = PAP.Company_P ("Doe, Inc.", bm, raw = True)
    >>> ta = PAP.Association ("Towel Carriers Association", short_name = "TCA", raw = True)

    >>> print (p1.ui_repr)
    PAP.Person ('Doe', 'Jane', '', '')

    >>> print (bm.ui_repr)
    PAP.Biz_Man (('Doe', 'Jane', '', '', 'PAP.Person'),)

    >>> print (cp.ui_repr)
    PAP.Company_P ('Doe, Inc.', (('Doe', 'Jane', '', '', 'PAP.Person'), 'PAP.Biz_Man'), '')

    >>> print (ta.ui_repr)
    PAP.Association ('Towel Carriers Association',)

    >>> scope.commit ()

    >>> PAP.Person.sorted_by_epk
    <Sorted_By: Getter function for `.last_name`, Getter function for `.first_name`, Getter function for `.middle_name`, Getter function for `.title`>

    >>> PAP.Biz_Man.sorted_by_epk
    <Sorted_By: Getter function for `.left.last_name`, Getter function for `.left.first_name`, Getter function for `.left.middle_name`, Getter function for `.left.title`>

    >>> PAP.Company_P.sorted_by_epk
    <Sorted_By: Getter function for `.name`, Getter function for `.owner.left.last_name`, Getter function for `.owner.left.first_name`, Getter function for `.owner.left.middle_name`, Getter function for `.owner.left.title`, Getter function for `.registered_in`>

    >>> PAP.Person.query (sort_key = TFL.Sorted_By ("pid")).count ()
    1
    >>> PAP.Biz_Man.query (sort_key = TFL.Sorted_By ("pid")).count ()
    1
    >>> PAP.Company_P.query (sort_key = TFL.Sorted_By ("pid")).count ()
    1

    >>> PAP.Person.query ().count ()
    1

    >>> PAP.Person.query (sort_key = PAP.Person.sorted_by_epk).count ()
    1
    >>> PAP.Biz_Man.query (sort_key = PAP.Biz_Man.sorted_by_epk).count ()
    1
    >>> PAP.Company_P.query (sort_key = PAP.Company_P.sorted_by_epk).count ()
    1

    >>> cq = PAP.Company_P ("Jane's, Inc.", bm)

    >>> PAP.Company_P.query (sort_key = TFL.Sorted_By ("pid")).count ()
    2

    >>> PAP.Company_P.query (sort_key = PAP.Company_P.sorted_by_epk).count ()
    2

    >>> print (PAP.Association.E_Type.attr_prop ("name").description)
    Name of association.

    >>> print (PAP.Company.E_Type.attr_prop ("name").description)
    Name of company.

    >>> for s in PAP.Subject.query ().order_by (TFL.Sorted_By ("type_name", "pid")) :
    ...     print (s.ui_repr)
    PAP.Association ('Towel Carriers Association',)
    PAP.Company_P ('Doe, Inc.', (('Doe', 'Jane', '', '', 'PAP.Person'), 'PAP.Biz_Man'), '')
    PAP.Company_P ("Jane's, Inc.", (('Doe', 'Jane', '', '', 'PAP.Person'), 'PAP.Biz_Man'), '')
    PAP.Person ('Doe', 'Jane', '', '')

    >>> for s in PAP.Subject.query_s () :
    ...     print (s.ui_repr)
    PAP.Person ('Doe', 'Jane', '', '')
    PAP.Company_P ('Doe, Inc.', (('Doe', 'Jane', '', '', 'PAP.Person'), 'PAP.Biz_Man'), '')
    PAP.Company_P ("Jane's, Inc.", (('Doe', 'Jane', '', '', 'PAP.Person'), 'PAP.Biz_Man'), '')
    PAP.Association ('Towel Carriers Association',)

    >>> sk = lambda x : (not bool (x.children), x.i_rank)
    >>> for i, (T, l) in enumerate (children_trans_iter (PAP.Subject, sort_key = sk)) :
    ...     if not i :
    ...         print ("%%-50s %%5s %%5s %%5s" %% ("type_name", "relev", "p_epk", "p_epks"))
    ...         print ("=" * 70)
    ...     et = T.E_Type
    ...     fs = (et.is_relevant, et.polymorphic_epk, et.polymorphic_epks)
    ...     if any (fs) :
    ...         hd  = "%%s%%s" %% ("  " * l, et.type_name)
    ...         hdl = len (hd)
    ...         sep = (" " if hdl %% 2 else "") + ". " * ((50 - hdl) // 2)
    ...         r, p, s = ((x or "") for x in fs)
    ...         print ("%%s %%s %%5s %%5s %%5s" %% (hd, sep, r, p, s))
    type_name                                          relev p_epk p_epks
    ======================================================================
    PAP.Subject  . . . . . . . . . . . . . . . . . . .         True  True
      PAP.Group  . . . . . . . . . . . . . . . . . . .         True  True
        PAP.Legal_Entity . . . . . . . . . . . . . . .         True  True
          PAP.Company  . . . . . . . . . . . . . . . .   True  True  True
            PAP.Company_P  . . . . . . . . . . . . . .   True
          PAP.Association  . . . . . . . . . . . . . .   True
      PAP.Person . . . . . . . . . . . . . . . . . . .   True

    >>> AQ = PAP.Company_P.E_Type.AQ

    >>> for aq in AQ.Attrs_Transitive :
    ...     print (aq, aq.E_Type.type_name if aq.E_Type and aq.E_Type.PNS else "-"*5)
    <name.AQ [Attr.Type.Querier String]> -----
    <owner.AQ [Attr.Type.Querier Id_Entity]> PAP.Biz_Man
    <owner.left.AQ [Attr.Type.Querier Id_Entity]> PAP.Person
    <owner.left.last_name.AQ [Attr.Type.Querier String_FL]> -----
    <owner.left.first_name.AQ [Attr.Type.Querier String_FL]> -----
    <owner.left.middle_name.AQ [Attr.Type.Querier String]> -----
    <owner.left.title.AQ [Attr.Type.Querier String]> -----
    <owner.left.lifetime.AQ [Attr.Type.Querier Composite]> MOM.Date_Interval_lifetime
    <owner.left.lifetime.start.AQ [Attr.Type.Querier Date]> -----
    <owner.left.lifetime.start.day.AQ [Attr.Type.Querier Ckd]> -----
    <owner.left.lifetime.start.month.AQ [Attr.Type.Querier Ckd]> -----
    <owner.left.lifetime.start.year.AQ [Attr.Type.Querier Ckd]> -----
    <owner.left.lifetime.finish.AQ [Attr.Type.Querier Date]> -----
    <owner.left.lifetime.finish.day.AQ [Attr.Type.Querier Ckd]> -----
    <owner.left.lifetime.finish.month.AQ [Attr.Type.Querier Ckd]> -----
    <owner.left.lifetime.finish.year.AQ [Attr.Type.Querier Ckd]> -----
    <owner.left.lifetime.alive.AQ [Attr.Type.Querier Boolean]> -----
    <owner.left.sex.AQ [Attr.Type.Querier Ckd]> -----
    <registered_in.AQ [Attr.Type.Querier String]> -----
    <lifetime.AQ [Attr.Type.Querier Composite]> MOM.Date_Interval_lifetime
    <lifetime.start.AQ [Attr.Type.Querier Date]> -----
    <lifetime.start.day.AQ [Attr.Type.Querier Ckd]> -----
    <lifetime.start.month.AQ [Attr.Type.Querier Ckd]> -----
    <lifetime.start.year.AQ [Attr.Type.Querier Ckd]> -----
    <lifetime.finish.AQ [Attr.Type.Querier Date]> -----
    <lifetime.finish.day.AQ [Attr.Type.Querier Ckd]> -----
    <lifetime.finish.month.AQ [Attr.Type.Querier Ckd]> -----
    <lifetime.finish.year.AQ [Attr.Type.Querier Ckd]> -----
    <lifetime.alive.AQ [Attr.Type.Querier Boolean]> -----
    <short_name.AQ [Attr.Type.Querier String]> -----
    <affiliate.AQ [Attr.Type.Querier Id_Entity]> PAP.Company_P
    <affiliate.name.AQ [Attr.Type.Querier String]> -----
    <affiliate.owner.AQ [Attr.Type.Querier Id_Entity]> PAP.Biz_Man
    <affiliate.owner.left.AQ [Attr.Type.Querier Id_Entity]> PAP.Person
    <affiliate.owner.left.last_name.AQ [Attr.Type.Querier String_FL]> -----
    <affiliate.owner.left.first_name.AQ [Attr.Type.Querier String_FL]> -----
    <affiliate.owner.left.middle_name.AQ [Attr.Type.Querier String]> -----
    <affiliate.owner.left.title.AQ [Attr.Type.Querier String]> -----
    <affiliate.owner.left.lifetime.AQ [Attr.Type.Querier Composite]> MOM.Date_Interval_lifetime
    <affiliate.owner.left.lifetime.start.AQ [Attr.Type.Querier Date]> -----
    <affiliate.owner.left.lifetime.start.day.AQ [Attr.Type.Querier Ckd]> -----
    <affiliate.owner.left.lifetime.start.month.AQ [Attr.Type.Querier Ckd]> -----
    <affiliate.owner.left.lifetime.start.year.AQ [Attr.Type.Querier Ckd]> -----
    <affiliate.owner.left.lifetime.finish.AQ [Attr.Type.Querier Date]> -----
    <affiliate.owner.left.lifetime.finish.day.AQ [Attr.Type.Querier Ckd]> -----
    <affiliate.owner.left.lifetime.finish.month.AQ [Attr.Type.Querier Ckd]> -----
    <affiliate.owner.left.lifetime.finish.year.AQ [Attr.Type.Querier Ckd]> -----
    <affiliate.owner.left.lifetime.alive.AQ [Attr.Type.Querier Boolean]> -----
    <affiliate.owner.left.sex.AQ [Attr.Type.Querier Ckd]> -----
    <affiliate.registered_in.AQ [Attr.Type.Querier String]> -----
    <affiliate.lifetime.AQ [Attr.Type.Querier Composite]> MOM.Date_Interval_lifetime
    <affiliate.lifetime.start.AQ [Attr.Type.Querier Date]> -----
    <affiliate.lifetime.start.day.AQ [Attr.Type.Querier Ckd]> -----
    <affiliate.lifetime.start.month.AQ [Attr.Type.Querier Ckd]> -----
    <affiliate.lifetime.start.year.AQ [Attr.Type.Querier Ckd]> -----
    <affiliate.lifetime.finish.AQ [Attr.Type.Querier Date]> -----
    <affiliate.lifetime.finish.day.AQ [Attr.Type.Querier Ckd]> -----
    <affiliate.lifetime.finish.month.AQ [Attr.Type.Querier Ckd]> -----
    <affiliate.lifetime.finish.year.AQ [Attr.Type.Querier Ckd]> -----
    <affiliate.lifetime.alive.AQ [Attr.Type.Querier Boolean]> -----
    <affiliate.short_name.AQ [Attr.Type.Querier String]> -----
    <affiliate.affiliate.AQ [Attr.Type.Querier Id_Entity]> PAP.Company_P
    <creation.AQ [Attr.Type.Querier Rev_Ref]> MOM.MD_Change
    <creation.c_time.AQ [Attr.Type.Querier Ckd]> -----
    <creation.c_user.AQ [Attr.Type.Querier Id_Entity]> MOM.Id_Entity
    <creation.kind.AQ [Attr.Type.Querier String]> -----
    <creation.time.AQ [Attr.Type.Querier Ckd]> -----
    <creation.user.AQ [Attr.Type.Querier Id_Entity]> MOM.Id_Entity
    <last_change.AQ [Attr.Type.Querier Rev_Ref]> MOM.MD_Change
    <last_change.c_time.AQ [Attr.Type.Querier Ckd]> -----
    <last_change.c_user.AQ [Attr.Type.Querier Id_Entity]> MOM.Id_Entity
    <last_change.kind.AQ [Attr.Type.Querier String]> -----
    <last_change.time.AQ [Attr.Type.Querier Ckd]> -----
    <last_change.user.AQ [Attr.Type.Querier Id_Entity]> MOM.Id_Entity
    <last_cid.AQ [Attr.Type.Querier Ckd]> -----
    <pid.AQ [Attr.Type.Querier Ckd]> -----
    <type_name.AQ [Attr.Type.Querier String]> -----
    <events.AQ [Attr.Type.Querier Rev_Ref]> EVT.Event
    <events.date.AQ [Attr.Type.Querier Composite]> MOM.Date_Interval
    <events.date.start.AQ [Attr.Type.Querier Date]> -----
    <events.date.start.day.AQ [Attr.Type.Querier Ckd]> -----
    <events.date.start.month.AQ [Attr.Type.Querier Ckd]> -----
    <events.date.start.year.AQ [Attr.Type.Querier Ckd]> -----
    <events.date.finish.AQ [Attr.Type.Querier Date]> -----
    <events.date.finish.day.AQ [Attr.Type.Querier Ckd]> -----
    <events.date.finish.month.AQ [Attr.Type.Querier Ckd]> -----
    <events.date.finish.year.AQ [Attr.Type.Querier Ckd]> -----
    <events.date.alive.AQ [Attr.Type.Querier Boolean]> -----
    <events.time.AQ [Attr.Type.Querier Composite]> MOM.Time_Interval
    <events.time.start.AQ [Attr.Type.Querier Time]> -----
    <events.time.start.hour.AQ [Attr.Type.Querier Ckd]> -----
    <events.time.start.minute.AQ [Attr.Type.Querier Ckd]> -----
    <events.time.start.second.AQ [Attr.Type.Querier Ckd]> -----
    <events.time.finish.AQ [Attr.Type.Querier Time]> -----
    <events.time.finish.hour.AQ [Attr.Type.Querier Ckd]> -----
    <events.time.finish.minute.AQ [Attr.Type.Querier Ckd]> -----
    <events.time.finish.second.AQ [Attr.Type.Querier Ckd]> -----
    <events.calendar.AQ [Attr.Type.Querier Id_Entity]> EVT.Calendar
    <events.calendar.name.AQ [Attr.Type.Querier String]> -----
    <events.calendar.desc.AQ [Attr.Type.Querier String]> -----
    <events.detail.AQ [Attr.Type.Querier String]> -----
    <events.short_title.AQ [Attr.Type.Querier String]> -----
    <urls.AQ [Attr.Type.Querier Rev_Ref]> PAP.Url
    <urls.value.AQ [Attr.Type.Querier String]> -----
    <urls.desc.AQ [Attr.Type.Querier String]> -----
    <phones.AQ [Attr.Type.Querier Rev_Ref]> PAP.Phone
    <phones.sn.AQ [Attr.Type.Querier String]> -----
    <phones.ndc.AQ [Attr.Type.Querier String]> -----
    <phones.cc.AQ [Attr.Type.Querier String]> -----
    <phones.desc.AQ [Attr.Type.Querier String]> -----
    <emails.AQ [Attr.Type.Querier Rev_Ref]> PAP.Email
    <emails.address.AQ [Attr.Type.Querier String]> -----
    <emails.desc.AQ [Attr.Type.Querier String]> -----
    <addresses.AQ [Attr.Type.Querier Rev_Ref]> PAP.Address
    <addresses.street.AQ [Attr.Type.Querier String]> -----
    <addresses.zip.AQ [Attr.Type.Querier String]> -----
    <addresses.city.AQ [Attr.Type.Querier String]> -----
    <addresses.country.AQ [Attr.Type.Querier String]> -----
    <addresses.desc.AQ [Attr.Type.Querier String]> -----
    <addresses.region.AQ [Attr.Type.Querier String]> -----

    >>> AQ
    <Attr.Type.Querier.E_Type for PAP.Company_P>

    >>> for aq in AQ.Atoms :
    ...     print (aq)
    <name.AQ [Attr.Type.Querier String]>
    <owner.left.last_name.AQ [Attr.Type.Querier String_FL]>
    <owner.left.first_name.AQ [Attr.Type.Querier String_FL]>
    <owner.left.middle_name.AQ [Attr.Type.Querier String]>
    <owner.left.title.AQ [Attr.Type.Querier String]>
    <owner.left.lifetime.start.AQ [Attr.Type.Querier Date]>
    <owner.left.lifetime.finish.AQ [Attr.Type.Querier Date]>
    <owner.left.lifetime.alive.AQ [Attr.Type.Querier Boolean]>
    <owner.left.sex.AQ [Attr.Type.Querier Ckd]>
    <registered_in.AQ [Attr.Type.Querier String]>
    <lifetime.start.AQ [Attr.Type.Querier Date]>
    <lifetime.finish.AQ [Attr.Type.Querier Date]>
    <lifetime.alive.AQ [Attr.Type.Querier Boolean]>
    <short_name.AQ [Attr.Type.Querier String]>
    <affiliate.name.AQ [Attr.Type.Querier String]>
    <affiliate.owner.left.last_name.AQ [Attr.Type.Querier String_FL]>
    <affiliate.owner.left.first_name.AQ [Attr.Type.Querier String_FL]>
    <affiliate.owner.left.middle_name.AQ [Attr.Type.Querier String]>
    <affiliate.owner.left.title.AQ [Attr.Type.Querier String]>
    <affiliate.owner.left.lifetime.start.AQ [Attr.Type.Querier Date]>
    <affiliate.owner.left.lifetime.finish.AQ [Attr.Type.Querier Date]>
    <affiliate.owner.left.lifetime.alive.AQ [Attr.Type.Querier Boolean]>
    <affiliate.owner.left.sex.AQ [Attr.Type.Querier Ckd]>
    <affiliate.registered_in.AQ [Attr.Type.Querier String]>
    <affiliate.lifetime.start.AQ [Attr.Type.Querier Date]>
    <affiliate.lifetime.finish.AQ [Attr.Type.Querier Date]>
    <affiliate.lifetime.alive.AQ [Attr.Type.Querier Boolean]>
    <affiliate.short_name.AQ [Attr.Type.Querier String]>
    <creation.c_time.AQ [Attr.Type.Querier Ckd]>
    <creation.kind.AQ [Attr.Type.Querier String]>
    <creation.time.AQ [Attr.Type.Querier Ckd]>
    <last_change.c_time.AQ [Attr.Type.Querier Ckd]>
    <last_change.kind.AQ [Attr.Type.Querier String]>
    <last_change.time.AQ [Attr.Type.Querier Ckd]>
    <last_cid.AQ [Attr.Type.Querier Ckd]>
    <pid.AQ [Attr.Type.Querier Ckd]>
    <type_name.AQ [Attr.Type.Querier String]>
    <events.date.start.AQ [Attr.Type.Querier Date]>
    <events.date.finish.AQ [Attr.Type.Querier Date]>
    <events.date.alive.AQ [Attr.Type.Querier Boolean]>
    <events.time.start.AQ [Attr.Type.Querier Time]>
    <events.time.finish.AQ [Attr.Type.Querier Time]>
    <events.calendar.name.AQ [Attr.Type.Querier String]>
    <events.calendar.desc.AQ [Attr.Type.Querier String]>
    <events.detail.AQ [Attr.Type.Querier String]>
    <events.short_title.AQ [Attr.Type.Querier String]>
    <urls.value.AQ [Attr.Type.Querier String]>
    <urls.desc.AQ [Attr.Type.Querier String]>
    <phones.sn.AQ [Attr.Type.Querier String]>
    <phones.ndc.AQ [Attr.Type.Querier String]>
    <phones.cc.AQ [Attr.Type.Querier String]>
    <phones.desc.AQ [Attr.Type.Querier String]>
    <emails.address.AQ [Attr.Type.Querier String]>
    <emails.desc.AQ [Attr.Type.Querier String]>
    <addresses.street.AQ [Attr.Type.Querier String]>
    <addresses.zip.AQ [Attr.Type.Querier String]>
    <addresses.city.AQ [Attr.Type.Querier String]>
    <addresses.country.AQ [Attr.Type.Querier String]>
    <addresses.desc.AQ [Attr.Type.Querier String]>
    <addresses.region.AQ [Attr.Type.Querier String]>

    >>> for aq in AQ.Unwrapped_Atoms :
    ...     print (aq)
    <name.AQ [Attr.Type.Querier String]>
    <owner.left.last_name.AQ [Attr.Type.Querier String_FL]>
    <owner.left.first_name.AQ [Attr.Type.Querier String_FL]>
    <owner.left.middle_name.AQ [Attr.Type.Querier String]>
    <owner.left.title.AQ [Attr.Type.Querier String]>
    <registered_in.AQ [Attr.Type.Querier String]>
    <lifetime.start.AQ [Attr.Type.Querier Date]>
    <lifetime.finish.AQ [Attr.Type.Querier Date]>
    <short_name.AQ [Attr.Type.Querier String]>
    <affiliate.name.AQ [Attr.Type.Querier String]>
    <affiliate.owner.left.last_name.AQ [Attr.Type.Querier String_FL]>
    <affiliate.owner.left.first_name.AQ [Attr.Type.Querier String_FL]>
    <affiliate.owner.left.middle_name.AQ [Attr.Type.Querier String]>
    <affiliate.owner.left.title.AQ [Attr.Type.Querier String]>
    <affiliate.registered_in.AQ [Attr.Type.Querier String]>
    <creation.cid.AQ [Attr.Type.Querier Ckd]>
    <creation.c_time.AQ [Attr.Type.Querier Ckd]>
    <creation.parent.AQ [Attr.Type.Querier Ckd]>
    <creation.parent_cid.AQ [Attr.Type.Querier Ckd]>
    <creation.kind.AQ [Attr.Type.Querier String]>
    <creation.time.AQ [Attr.Type.Querier Ckd]>
    <creation.type_name.AQ [Attr.Type.Querier String]>
    <last_change.cid.AQ [Attr.Type.Querier Ckd]>
    <last_change.c_time.AQ [Attr.Type.Querier Ckd]>
    <last_change.parent.AQ [Attr.Type.Querier Ckd]>
    <last_change.parent_cid.AQ [Attr.Type.Querier Ckd]>
    <last_change.kind.AQ [Attr.Type.Querier String]>
    <last_change.time.AQ [Attr.Type.Querier Ckd]>
    <last_change.type_name.AQ [Attr.Type.Querier String]>
    <last_cid.AQ [Attr.Type.Querier Ckd]>
    <pid.AQ [Attr.Type.Querier Ckd]>
    <type_name.AQ [Attr.Type.Querier String]>
    <events.date.start.AQ [Attr.Type.Querier Date]>
    <events.date.finish.AQ [Attr.Type.Querier Date]>
    <events.date.alive.AQ [Attr.Type.Querier Boolean]>
    <events.time.start.AQ [Attr.Type.Querier Time]>
    <events.time.finish.AQ [Attr.Type.Querier Time]>
    <events.calendar.name.AQ [Attr.Type.Querier String]>
    <events.calendar.desc.AQ [Attr.Type.Querier String]>
    <events.detail.AQ [Attr.Type.Querier String]>
    <events.short_title.AQ [Attr.Type.Querier String]>
    <events.last_cid.AQ [Attr.Type.Querier Ckd]>
    <events.pid.AQ [Attr.Type.Querier Ckd]>
    <events.type_name.AQ [Attr.Type.Querier String]>
    <urls.value.AQ [Attr.Type.Querier String]>
    <urls.desc.AQ [Attr.Type.Querier String]>
    <urls.last_cid.AQ [Attr.Type.Querier Ckd]>
    <urls.pid.AQ [Attr.Type.Querier Ckd]>
    <urls.type_name.AQ [Attr.Type.Querier String]>
    <phones.sn.AQ [Attr.Type.Querier String]>
    <phones.ndc.AQ [Attr.Type.Querier String]>
    <phones.cc.AQ [Attr.Type.Querier String]>
    <phones.desc.AQ [Attr.Type.Querier String]>
    <phones.last_cid.AQ [Attr.Type.Querier Ckd]>
    <phones.pid.AQ [Attr.Type.Querier Ckd]>
    <phones.type_name.AQ [Attr.Type.Querier String]>
    <emails.address.AQ [Attr.Type.Querier String]>
    <emails.desc.AQ [Attr.Type.Querier String]>
    <emails.last_cid.AQ [Attr.Type.Querier Ckd]>
    <emails.pid.AQ [Attr.Type.Querier Ckd]>
    <emails.type_name.AQ [Attr.Type.Querier String]>
    <addresses.street.AQ [Attr.Type.Querier String]>
    <addresses.zip.AQ [Attr.Type.Querier String]>
    <addresses.city.AQ [Attr.Type.Querier String]>
    <addresses.country.AQ [Attr.Type.Querier String]>
    <addresses.desc.AQ [Attr.Type.Querier String]>
    <addresses.region.AQ [Attr.Type.Querier String]>
    <addresses.last_cid.AQ [Attr.Type.Querier Ckd]>
    <addresses.pid.AQ [Attr.Type.Querier Ckd]>
    <addresses.type_name.AQ [Attr.Type.Querier String]>

    >>> print (formatted (AQ.As_Json_Cargo))
    { 'filters' :
        [ { 'name' : 'name'
          , 'sig_key' : 3
          , 'ui_name' : 'Name'
          }
        , { 'Class' : 'Entity'
          , 'attrs' :
              [ { 'Class' : 'Entity'
                , 'attrs' :
                    [ { 'name' : 'last_name'
                      , 'sig_key' : 3
                      , 'ui_name' : 'Last name'
                      }
                    , { 'name' : 'first_name'
                      , 'sig_key' : 3
                      , 'ui_name' : 'First name'
                      }
                    , { 'name' : 'middle_name'
                      , 'sig_key' : 3
                      , 'ui_name' : 'Middle name'
                      }
                    , { 'name' : 'title'
                      , 'sig_key' : 3
                      , 'ui_name' : 'Academic title'
                      }
                    , { 'attrs' :
                          [ { 'attrs' :
                                [ { 'name' : 'day'
                                  , 'sig_key' : 0
                                  , 'ui_name' : 'Day'
                                  }
                                , { 'name' : 'month'
                                  , 'sig_key' : 0
                                  , 'ui_name' : 'Month'
                                  }
                                , { 'name' : 'year'
                                  , 'sig_key' : 0
                                  , 'ui_name' : 'Year'
                                  }
                                ]
                            , 'name' : 'start'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Start'
                            }
                          , { 'attrs' :
                                [ { 'name' : 'day'
                                  , 'sig_key' : 0
                                  , 'ui_name' : 'Day'
                                  }
                                , { 'name' : 'month'
                                  , 'sig_key' : 0
                                  , 'ui_name' : 'Month'
                                  }
                                , { 'name' : 'year'
                                  , 'sig_key' : 0
                                  , 'ui_name' : 'Year'
                                  }
                                ]
                            , 'name' : 'finish'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Finish'
                            }
                          , { 'name' : 'alive'
                            , 'sig_key' : 1
                            , 'ui_name' : 'Alive'
                            }
                          ]
                      , 'name' : 'lifetime'
                      , 'ui_name' : 'Lifetime'
                      }
                    , { 'name' : 'sex'
                      , 'sig_key' : 0
                      , 'ui_name' : 'Sex'
                      }
                    ]
                , 'name' : 'left'
                , 'sig_key' : 2
                , 'ui_name' : 'Man'
                }
              ]
          , 'name' : 'owner'
          , 'sig_key' : 2
          , 'ui_name' : 'Owner'
          }
        , { 'name' : 'registered_in'
          , 'sig_key' : 3
          , 'ui_name' : 'Registered in'
          }
        , { 'attrs' :
              [ { 'attrs' :
                    [ { 'name' : 'day'
                      , 'sig_key' : 0
                      , 'ui_name' : 'Day'
                      }
                    , { 'name' : 'month'
                      , 'sig_key' : 0
                      , 'ui_name' : 'Month'
                      }
                    , { 'name' : 'year'
                      , 'sig_key' : 0
                      , 'ui_name' : 'Year'
                      }
                    ]
                , 'name' : 'start'
                , 'sig_key' : 0
                , 'ui_name' : 'Start'
                }
              , { 'attrs' :
                    [ { 'name' : 'day'
                      , 'sig_key' : 0
                      , 'ui_name' : 'Day'
                      }
                    , { 'name' : 'month'
                      , 'sig_key' : 0
                      , 'ui_name' : 'Month'
                      }
                    , { 'name' : 'year'
                      , 'sig_key' : 0
                      , 'ui_name' : 'Year'
                      }
                    ]
                , 'name' : 'finish'
                , 'sig_key' : 0
                , 'ui_name' : 'Finish'
                }
              , { 'name' : 'alive'
                , 'sig_key' : 1
                , 'ui_name' : 'Alive'
                }
              ]
          , 'name' : 'lifetime'
          , 'ui_name' : 'Lifetime'
          }
        , { 'name' : 'short_name'
          , 'sig_key' : 3
          , 'ui_name' : 'Short name'
          }
        , { 'Class' : 'Entity'
          , 'attrs' :
              [ { 'name' : 'name'
                , 'sig_key' : 3
                , 'ui_name' : 'Name'
                }
              , { 'Class' : 'Entity'
                , 'attrs' :
                    [ { 'Class' : 'Entity'
                      , 'attrs' :
                          [ { 'name' : 'last_name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Last name'
                            }
                          , { 'name' : 'first_name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'First name'
                            }
                          , { 'name' : 'middle_name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Middle name'
                            }
                          , { 'name' : 'title'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Academic title'
                            }
                          , { 'attrs' :
                                [ { 'attrs' :
                                      [ { 'name' : 'day'
                                        , 'sig_key' : 0
                                        , 'ui_name' : 'Day'
                                        }
                                      , { 'name' : 'month'
                                        , 'sig_key' : 0
                                        , 'ui_name' : 'Month'
                                        }
                                      , { 'name' : 'year'
                                        , 'sig_key' : 0
                                        , 'ui_name' : 'Year'
                                        }
                                      ]
                                  , 'name' : 'start'
                                  , 'sig_key' : 0
                                  , 'ui_name' : 'Start'
                                  }
                                , { 'attrs' :
                                      [ { 'name' : 'day'
                                        , 'sig_key' : 0
                                        , 'ui_name' : 'Day'
                                        }
                                      , { 'name' : 'month'
                                        , 'sig_key' : 0
                                        , 'ui_name' : 'Month'
                                        }
                                      , { 'name' : 'year'
                                        , 'sig_key' : 0
                                        , 'ui_name' : 'Year'
                                        }
                                      ]
                                  , 'name' : 'finish'
                                  , 'sig_key' : 0
                                  , 'ui_name' : 'Finish'
                                  }
                                , { 'name' : 'alive'
                                  , 'sig_key' : 1
                                  , 'ui_name' : 'Alive'
                                  }
                                ]
                            , 'name' : 'lifetime'
                            , 'ui_name' : 'Lifetime'
                            }
                          , { 'name' : 'sex'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Sex'
                            }
                          ]
                      , 'name' : 'left'
                      , 'sig_key' : 2
                      , 'ui_name' : 'Man'
                      }
                    ]
                , 'name' : 'owner'
                , 'sig_key' : 2
                , 'ui_name' : 'Owner'
                }
              , { 'name' : 'registered_in'
                , 'sig_key' : 3
                , 'ui_name' : 'Registered in'
                }
              , { 'attrs' :
                    [ { 'attrs' :
                          [ { 'name' : 'day'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Day'
                            }
                          , { 'name' : 'month'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Month'
                            }
                          , { 'name' : 'year'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Year'
                            }
                          ]
                      , 'name' : 'start'
                      , 'sig_key' : 0
                      , 'ui_name' : 'Start'
                      }
                    , { 'attrs' :
                          [ { 'name' : 'day'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Day'
                            }
                          , { 'name' : 'month'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Month'
                            }
                          , { 'name' : 'year'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Year'
                            }
                          ]
                      , 'name' : 'finish'
                      , 'sig_key' : 0
                      , 'ui_name' : 'Finish'
                      }
                    , { 'name' : 'alive'
                      , 'sig_key' : 1
                      , 'ui_name' : 'Alive'
                      }
                    ]
                , 'name' : 'lifetime'
                , 'ui_name' : 'Lifetime'
                }
              , { 'name' : 'short_name'
                , 'sig_key' : 3
                , 'ui_name' : 'Short name'
                }
              , { 'Class' : 'Entity'
                , 'name' : 'affiliate'
                , 'sig_key' : 2
                , 'ui_name' : 'Affiliate'
                }
              ]
          , 'name' : 'affiliate'
          , 'sig_key' : 2
          , 'ui_name' : 'Affiliate'
          }
        , { 'Class' : 'Entity'
          , 'attrs' :
              [ { 'name' : 'c_time'
                , 'sig_key' : 0
                , 'ui_name' : 'C time'
                }
              , { 'Class' : 'Entity'
                , 'children_np' :
                    [ { 'Class' : 'Entity'
                      , 'attrs' :
                          [ { 'name' : 'name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Name'
                            }
                          ]
                      , 'name' : 'c_user'
                      , 'sig_key' : 2
                      , 'type_name' : 'Auth.Account'
                      , 'ui_name' : 'C user'
                      , 'ui_type_name' : 'Account'
                      }
                    , { 'Class' : 'Entity'
                      , 'attrs' :
                          [ { 'name' : 'last_name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Last name'
                            }
                          , { 'name' : 'first_name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'First name'
                            }
                          , { 'name' : 'middle_name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Middle name'
                            }
                          , { 'name' : 'title'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Academic title'
                            }
                          ]
                      , 'name' : 'c_user'
                      , 'sig_key' : 2
                      , 'type_name' : 'PAP.Person'
                      , 'ui_name' : 'C user'
                      , 'ui_type_name' : 'Person'
                      }
                    ]
                , 'name' : 'c_user'
                , 'sig_key' : 2
                , 'ui_name' : 'C user'
                }
              , { 'name' : 'kind'
                , 'sig_key' : 3
                , 'ui_name' : 'Kind'
                }
              , { 'name' : 'time'
                , 'sig_key' : 0
                , 'ui_name' : 'Time'
                }
              , { 'Class' : 'Entity'
                , 'children_np' :
                    [ { 'Class' : 'Entity'
                      , 'attrs' :
                          [ { 'name' : 'name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Name'
                            }
                          ]
                      , 'name' : 'user'
                      , 'sig_key' : 2
                      , 'type_name' : 'Auth.Account'
                      , 'ui_name' : 'User'
                      , 'ui_type_name' : 'Account'
                      }
                    , { 'Class' : 'Entity'
                      , 'attrs' :
                          [ { 'name' : 'last_name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Last name'
                            }
                          , { 'name' : 'first_name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'First name'
                            }
                          , { 'name' : 'middle_name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Middle name'
                            }
                          , { 'name' : 'title'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Academic title'
                            }
                          ]
                      , 'name' : 'user'
                      , 'sig_key' : 2
                      , 'type_name' : 'PAP.Person'
                      , 'ui_name' : 'User'
                      , 'ui_type_name' : 'Person'
                      }
                    ]
                , 'name' : 'user'
                , 'sig_key' : 2
                , 'ui_name' : 'User'
                }
              ]
          , 'name' : 'creation'
          , 'sig_key' : 2
          , 'ui_name' : 'Creation'
          }
        , { 'Class' : 'Entity'
          , 'attrs' :
              [ { 'name' : 'c_time'
                , 'sig_key' : 0
                , 'ui_name' : 'C time'
                }
              , { 'Class' : 'Entity'
                , 'children_np' :
                    [ { 'Class' : 'Entity'
                      , 'attrs' :
                          [ { 'name' : 'name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Name'
                            }
                          ]
                      , 'name' : 'c_user'
                      , 'sig_key' : 2
                      , 'type_name' : 'Auth.Account'
                      , 'ui_name' : 'C user'
                      , 'ui_type_name' : 'Account'
                      }
                    , { 'Class' : 'Entity'
                      , 'attrs' :
                          [ { 'name' : 'last_name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Last name'
                            }
                          , { 'name' : 'first_name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'First name'
                            }
                          , { 'name' : 'middle_name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Middle name'
                            }
                          , { 'name' : 'title'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Academic title'
                            }
                          ]
                      , 'name' : 'c_user'
                      , 'sig_key' : 2
                      , 'type_name' : 'PAP.Person'
                      , 'ui_name' : 'C user'
                      , 'ui_type_name' : 'Person'
                      }
                    ]
                , 'name' : 'c_user'
                , 'sig_key' : 2
                , 'ui_name' : 'C user'
                }
              , { 'name' : 'kind'
                , 'sig_key' : 3
                , 'ui_name' : 'Kind'
                }
              , { 'name' : 'time'
                , 'sig_key' : 0
                , 'ui_name' : 'Time'
                }
              , { 'Class' : 'Entity'
                , 'children_np' :
                    [ { 'Class' : 'Entity'
                      , 'attrs' :
                          [ { 'name' : 'name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Name'
                            }
                          ]
                      , 'name' : 'user'
                      , 'sig_key' : 2
                      , 'type_name' : 'Auth.Account'
                      , 'ui_name' : 'User'
                      , 'ui_type_name' : 'Account'
                      }
                    , { 'Class' : 'Entity'
                      , 'attrs' :
                          [ { 'name' : 'last_name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Last name'
                            }
                          , { 'name' : 'first_name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'First name'
                            }
                          , { 'name' : 'middle_name'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Middle name'
                            }
                          , { 'name' : 'title'
                            , 'sig_key' : 3
                            , 'ui_name' : 'Academic title'
                            }
                          ]
                      , 'name' : 'user'
                      , 'sig_key' : 2
                      , 'type_name' : 'PAP.Person'
                      , 'ui_name' : 'User'
                      , 'ui_type_name' : 'Person'
                      }
                    ]
                , 'name' : 'user'
                , 'sig_key' : 2
                , 'ui_name' : 'User'
                }
              ]
          , 'name' : 'last_change'
          , 'sig_key' : 2
          , 'ui_name' : 'Last change'
          }
        , { 'name' : 'last_cid'
          , 'sig_key' : 0
          , 'ui_name' : 'Last cid'
          }
        , { 'name' : 'pid'
          , 'sig_key' : 0
          , 'ui_name' : 'Pid'
          }
        , { 'name' : 'type_name'
          , 'sig_key' : 3
          , 'ui_name' : 'Type name'
          }
        , { 'Class' : 'Entity'
          , 'attrs' :
              [ { 'attrs' :
                    [ { 'attrs' :
                          [ { 'name' : 'day'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Day'
                            }
                          , { 'name' : 'month'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Month'
                            }
                          , { 'name' : 'year'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Year'
                            }
                          ]
                      , 'name' : 'start'
                      , 'sig_key' : 0
                      , 'ui_name' : 'Start'
                      }
                    , { 'attrs' :
                          [ { 'name' : 'day'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Day'
                            }
                          , { 'name' : 'month'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Month'
                            }
                          , { 'name' : 'year'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Year'
                            }
                          ]
                      , 'name' : 'finish'
                      , 'sig_key' : 0
                      , 'ui_name' : 'Finish'
                      }
                    , { 'name' : 'alive'
                      , 'sig_key' : 1
                      , 'ui_name' : 'Alive'
                      }
                    ]
                , 'name' : 'date'
                , 'ui_name' : 'Date'
                }
              , { 'attrs' :
                    [ { 'attrs' :
                          [ { 'name' : 'hour'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Hour'
                            }
                          , { 'name' : 'minute'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Minute'
                            }
                          , { 'name' : 'second'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Second'
                            }
                          ]
                      , 'name' : 'start'
                      , 'sig_key' : 0
                      , 'ui_name' : 'Start'
                      }
                    , { 'attrs' :
                          [ { 'name' : 'hour'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Hour'
                            }
                          , { 'name' : 'minute'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Minute'
                            }
                          , { 'name' : 'second'
                            , 'sig_key' : 0
                            , 'ui_name' : 'Second'
                            }
                          ]
                      , 'name' : 'finish'
                      , 'sig_key' : 0
                      , 'ui_name' : 'Finish'
                      }
                    ]
                , 'name' : 'time'
                , 'ui_name' : 'Time'
                }
              , { 'Class' : 'Entity'
                , 'attrs' :
                    [ { 'name' : 'name'
                      , 'sig_key' : 3
                      , 'ui_name' : 'Name'
                      }
                    , { 'name' : 'desc'
                      , 'sig_key' : 3
                      , 'ui_name' : 'Description'
                      }
                    ]
                , 'name' : 'calendar'
                , 'sig_key' : 2
                , 'ui_name' : 'Calendar'
                }
              , { 'name' : 'detail'
                , 'sig_key' : 3
                , 'ui_name' : 'Detail'
                }
              , { 'name' : 'short_title'
                , 'sig_key' : 3
                , 'ui_name' : 'Short title'
                }
              ]
          , 'name' : 'events'
          , 'sig_key' : 2
          , 'ui_name' : 'Events'
          }
        , { 'Class' : 'Entity'
          , 'attrs' :
              [ { 'name' : 'value'
                , 'sig_key' : 3
                , 'ui_name' : 'Value'
                }
              , { 'name' : 'desc'
                , 'sig_key' : 3
                , 'ui_name' : 'Description'
                }
              ]
          , 'name' : 'urls'
          , 'sig_key' : 2
          , 'ui_name' : 'Urls'
          }
        , { 'Class' : 'Entity'
          , 'attrs' :
              [ { 'name' : 'sn'
                , 'sig_key' : 3
                , 'ui_name' : 'Subscriber number'
                }
              , { 'name' : 'ndc'
                , 'sig_key' : 3
                , 'ui_name' : 'Network destination code'
                }
              , { 'name' : 'cc'
                , 'sig_key' : 3
                , 'ui_name' : 'Country code'
                }
              , { 'name' : 'desc'
                , 'sig_key' : 3
                , 'ui_name' : 'Description'
                }
              ]
          , 'name' : 'phones'
          , 'sig_key' : 2
          , 'ui_name' : 'Phones'
          }
        , { 'Class' : 'Entity'
          , 'attrs' :
              [ { 'name' : 'address'
                , 'sig_key' : 3
                , 'ui_name' : 'Email address'
                }
              , { 'name' : 'desc'
                , 'sig_key' : 3
                , 'ui_name' : 'Description'
                }
              ]
          , 'name' : 'emails'
          , 'sig_key' : 2
          , 'ui_name' : 'Emails'
          }
        , { 'Class' : 'Entity'
          , 'attrs' :
              [ { 'name' : 'street'
                , 'sig_key' : 3
                , 'ui_name' : 'Street'
                }
              , { 'name' : 'zip'
                , 'sig_key' : 3
                , 'ui_name' : 'Zip code'
                }
              , { 'name' : 'city'
                , 'sig_key' : 3
                , 'ui_name' : 'City'
                }
              , { 'name' : 'country'
                , 'sig_key' : 3
                , 'ui_name' : 'Country'
                }
              , { 'name' : 'desc'
                , 'sig_key' : 3
                , 'ui_name' : 'Description'
                }
              , { 'name' : 'region'
                , 'sig_key' : 3
                , 'ui_name' : 'Region'
                }
              ]
          , 'name' : 'addresses'
          , 'sig_key' : 2
          , 'ui_name' : 'Addresses'
          }
        ]
    , 'name_sep' : '__'
    , 'op_map' :
        { 'CONTAINS' :
            { 'desc' : 'Select entities where the attribute contains the specified value'
            , 'sym' : 'contains'
            }
        , 'ENDSWITH' :
            { 'desc' : 'Select entities where the attribute value ends with the specified value'
            , 'sym' : 'ends-with'
            }
        , 'EQ' :
            { 'desc' : 'Select entities where the attribute is equal to the specified value'
            , 'sym' : '=='
            }
        , 'EQS' :
            { 'desc' : 'Select entities where the attribute is equal to the specified string value'
            , 'sym' : 'EQS'
            }
        , 'GE' :
            { 'desc' : 'Select entities where the attribute is greater than, or equal to, the specified value'
            , 'sym' : '>='
            }
        , 'GT' :
            { 'desc' : 'Select entities where the attribute is greater than the specified value'
            , 'sym' : '>'
            }
        , 'IN' :
            { 'desc' : 'Select entities where the attribute is a member of the specified list of values'
            , 'sym' : 'in'
            }
        , 'LE' :
            { 'desc' : 'Select entities where the attribute is less than, or equal to, the specified value'
            , 'sym' : '<='
            }
        , 'LT' :
            { 'desc' : 'Select entities where the attribute is less than the specified value'
            , 'sym' : '<'
            }
        , 'NE' :
            { 'desc' : 'Select entities where the attribute is not equal to the specified value'
            , 'sym' : '!='
            }
        , 'NES' :
            { 'desc' : 'Select entities where the attribute is not equal to the specified string value'
            , 'sym' : 'NES'
            }
        , 'STARTSWITH' :
            { 'desc' : 'Select entities where the attribute value starts with the specified value'
            , 'sym' : 'starts-with'
            }
        }
    , 'op_sep' : '___'
    , 'sig_map' :
        { 0 :
            ( 'EQ'
            , 'GE'
            , 'GT'
            , 'IN'
            , 'LE'
            , 'LT'
            , 'NE'
            )
        , 1 : ('EQ', )
        , 2 :
            ( 'EQ'
            , 'IN'
            , 'NE'
            )
        , 3 :
            ( 'CONTAINS'
            , 'ENDSWITH'
            , 'EQ'
            , 'GE'
            , 'GT'
            , 'IN'
            , 'LE'
            , 'LT'
            , 'NE'
            , 'STARTSWITH'
            )
        }
    , 'ui_sep' : '/'
    }

    >>> print (formatted (AQ.As_Template_Elem))
    [ Record
        ( attr = String `name`
        , full_name = 'name'
        , id = 'name'
        , name = 'name'
        , sig_key = 3
        , ui_name = 'Name'
        )
    , Record
        ( Class = 'Entity'
        , attr = Entity `owner`
        , attrs =
          [ Record
              ( Class = 'Entity'
              , attr = Person `left`
              , attrs =
                [ Record
                    ( attr = String `last_name`
                    , full_name = 'owner.left.last_name'
                    , id = 'owner__left__last_name'
                    , name = 'last_name'
                    , sig_key = 3
                    , ui_name = 'Owner/Man/Last name'
                    )
                , Record
                    ( attr = String `first_name`
                    , full_name = 'owner.left.first_name'
                    , id = 'owner__left__first_name'
                    , name = 'first_name'
                    , sig_key = 3
                    , ui_name = 'Owner/Man/First name'
                    )
                , Record
                    ( attr = String `middle_name`
                    , full_name = 'owner.left.middle_name'
                    , id = 'owner__left__middle_name'
                    , name = 'middle_name'
                    , sig_key = 3
                    , ui_name = 'Owner/Man/Middle name'
                    )
                , Record
                    ( attr = String `title`
                    , full_name = 'owner.left.title'
                    , id = 'owner__left__title'
                    , name = 'title'
                    , sig_key = 3
                    , ui_name = 'Owner/Man/Academic title'
                    )
                , Record
                    ( attr = Date_Interval `lifetime`
                    , attrs =
                      [ Record
                          ( attr = Date `start`
                          , attrs =
                            [ Record
                                ( attr = Int `day`
                                , full_name = 'owner.left.lifetime.start.day'
                                , id = 'owner__left__lifetime__start__day'
                                , name = 'day'
                                , sig_key = 0
                                , ui_name = 'Owner/Man/Lifetime/Start/Day'
                                )
                            , Record
                                ( attr = Int `month`
                                , full_name = 'owner.left.lifetime.start.month'
                                , id = 'owner__left__lifetime__start__month'
                                , name = 'month'
                                , sig_key = 0
                                , ui_name = 'Owner/Man/Lifetime/Start/Month'
                                )
                            , Record
                                ( attr = Int `year`
                                , full_name = 'owner.left.lifetime.start.year'
                                , id = 'owner__left__lifetime__start__year'
                                , name = 'year'
                                , sig_key = 0
                                , ui_name = 'Owner/Man/Lifetime/Start/Year'
                                )
                            ]
                          , full_name = 'owner.left.lifetime.start'
                          , id = 'owner__left__lifetime__start'
                          , name = 'start'
                          , sig_key = 0
                          , ui_name = 'Owner/Man/Lifetime/Start'
                          )
                      , Record
                          ( attr = Date `finish`
                          , attrs =
                            [ Record
                                ( attr = Int `day`
                                , full_name = 'owner.left.lifetime.finish.day'
                                , id = 'owner__left__lifetime__finish__day'
                                , name = 'day'
                                , sig_key = 0
                                , ui_name = 'Owner/Man/Lifetime/Finish/Day'
                                )
                            , Record
                                ( attr = Int `month`
                                , full_name = 'owner.left.lifetime.finish.month'
                                , id = 'owner__left__lifetime__finish__month'
                                , name = 'month'
                                , sig_key = 0
                                , ui_name = 'Owner/Man/Lifetime/Finish/Month'
                                )
                            , Record
                                ( attr = Int `year`
                                , full_name = 'owner.left.lifetime.finish.year'
                                , id = 'owner__left__lifetime__finish__year'
                                , name = 'year'
                                , sig_key = 0
                                , ui_name = 'Owner/Man/Lifetime/Finish/Year'
                                )
                            ]
                          , full_name = 'owner.left.lifetime.finish'
                          , id = 'owner__left__lifetime__finish'
                          , name = 'finish'
                          , sig_key = 0
                          , ui_name = 'Owner/Man/Lifetime/Finish'
                          )
                      , Record
                          ( attr = Boolean `alive`
                          , choices =
                            [ 'no'
                            , 'yes'
                            ]
                          , full_name = 'owner.left.lifetime.alive'
                          , id = 'owner__left__lifetime__alive'
                          , name = 'alive'
                          , sig_key = 1
                          , ui_name = 'Owner/Man/Lifetime/Alive'
                          )
                      ]
                    , full_name = 'owner.left.lifetime'
                    , id = 'owner__left__lifetime'
                    , name = 'lifetime'
                    , ui_name = 'Owner/Man/Lifetime'
                    )
                , Record
                    ( attr = Sex `sex`
                    , choices =
                      [ ( 'F'
                        , 'Female'
                        )
                      , ( 'M'
                        , 'Male'
                        )
                      ]
                    , full_name = 'owner.left.sex'
                    , id = 'owner__left__sex'
                    , name = 'sex'
                    , sig_key = 0
                    , ui_name = 'Owner/Man/Sex'
                    )
                ]
              , full_name = 'owner.left'
              , id = 'owner__left'
              , name = 'left'
              , sig_key = 2
              , type_name = 'PAP.Person'
              , ui_name = 'Owner/Man'
              , ui_type_name = 'Person'
              )
          ]
        , full_name = 'owner'
        , id = 'owner'
        , name = 'owner'
        , sig_key = 2
        , type_name = 'PAP.Biz_Man'
        , ui_name = 'Owner'
        , ui_type_name = 'Biz_Man'
        )
    , Record
        ( attr = String `registered_in`
        , full_name = 'registered_in'
        , id = 'registered_in'
        , name = 'registered_in'
        , sig_key = 3
        , ui_name = 'Registered in'
        )
    , Record
        ( attr = Date_Interval `lifetime`
        , attrs =
          [ Record
              ( attr = Date `start`
              , attrs =
                [ Record
                    ( attr = Int `day`
                    , full_name = 'lifetime.start.day'
                    , id = 'lifetime__start__day'
                    , name = 'day'
                    , sig_key = 0
                    , ui_name = 'Lifetime/Start/Day'
                    )
                , Record
                    ( attr = Int `month`
                    , full_name = 'lifetime.start.month'
                    , id = 'lifetime__start__month'
                    , name = 'month'
                    , sig_key = 0
                    , ui_name = 'Lifetime/Start/Month'
                    )
                , Record
                    ( attr = Int `year`
                    , full_name = 'lifetime.start.year'
                    , id = 'lifetime__start__year'
                    , name = 'year'
                    , sig_key = 0
                    , ui_name = 'Lifetime/Start/Year'
                    )
                ]
              , full_name = 'lifetime.start'
              , id = 'lifetime__start'
              , name = 'start'
              , sig_key = 0
              , ui_name = 'Lifetime/Start'
              )
          , Record
              ( attr = Date `finish`
              , attrs =
                [ Record
                    ( attr = Int `day`
                    , full_name = 'lifetime.finish.day'
                    , id = 'lifetime__finish__day'
                    , name = 'day'
                    , sig_key = 0
                    , ui_name = 'Lifetime/Finish/Day'
                    )
                , Record
                    ( attr = Int `month`
                    , full_name = 'lifetime.finish.month'
                    , id = 'lifetime__finish__month'
                    , name = 'month'
                    , sig_key = 0
                    , ui_name = 'Lifetime/Finish/Month'
                    )
                , Record
                    ( attr = Int `year`
                    , full_name = 'lifetime.finish.year'
                    , id = 'lifetime__finish__year'
                    , name = 'year'
                    , sig_key = 0
                    , ui_name = 'Lifetime/Finish/Year'
                    )
                ]
              , full_name = 'lifetime.finish'
              , id = 'lifetime__finish'
              , name = 'finish'
              , sig_key = 0
              , ui_name = 'Lifetime/Finish'
              )
          , Record
              ( attr = Boolean `alive`
              , choices =
                [ 'no'
                , 'yes'
                ]
              , full_name = 'lifetime.alive'
              , id = 'lifetime__alive'
              , name = 'alive'
              , sig_key = 1
              , ui_name = 'Lifetime/Alive'
              )
          ]
        , full_name = 'lifetime'
        , id = 'lifetime'
        , name = 'lifetime'
        , ui_name = 'Lifetime'
        )
    , Record
        ( attr = String `short_name`
        , full_name = 'short_name'
        , id = 'short_name'
        , name = 'short_name'
        , sig_key = 3
        , ui_name = 'Short name'
        )
    , Record
        ( Class = 'Entity'
        , attr = Entity `affiliate`
        , attrs =
          [ Record
              ( attr = String `name`
              , full_name = 'affiliate.name'
              , id = 'affiliate__name'
              , name = 'name'
              , sig_key = 3
              , ui_name = 'Affiliate/Name'
              )
          , Record
              ( Class = 'Entity'
              , attr = Entity `owner`
              , attrs =
                [ Record
                    ( Class = 'Entity'
                    , attr = Person `left`
                    , attrs =
                      [ Record
                          ( attr = String `last_name`
                          , full_name = 'affiliate.owner.left.last_name'
                          , id = 'affiliate__owner__left__last_name'
                          , name = 'last_name'
                          , sig_key = 3
                          , ui_name = 'Affiliate/Owner/Man/Last name'
                          )
                      , Record
                          ( attr = String `first_name`
                          , full_name = 'affiliate.owner.left.first_name'
                          , id = 'affiliate__owner__left__first_name'
                          , name = 'first_name'
                          , sig_key = 3
                          , ui_name = 'Affiliate/Owner/Man/First name'
                          )
                      , Record
                          ( attr = String `middle_name`
                          , full_name = 'affiliate.owner.left.middle_name'
                          , id = 'affiliate__owner__left__middle_name'
                          , name = 'middle_name'
                          , sig_key = 3
                          , ui_name = 'Affiliate/Owner/Man/Middle name'
                          )
                      , Record
                          ( attr = String `title`
                          , full_name = 'affiliate.owner.left.title'
                          , id = 'affiliate__owner__left__title'
                          , name = 'title'
                          , sig_key = 3
                          , ui_name = 'Affiliate/Owner/Man/Academic title'
                          )
                      , Record
                          ( attr = Date_Interval `lifetime`
                          , attrs =
                            [ Record
                                ( attr = Date `start`
                                , attrs =
                                  [ Record
                                      ( attr = Int `day`
                                      , full_name = 'affiliate.owner.left.lifetime.start.day'
                                      , id = 'affiliate__owner__left__lifetime__start__day'
                                      , name = 'day'
                                      , sig_key = 0
                                      , ui_name = 'Affiliate/Owner/Man/Lifetime/Start/Day'
                                      )
                                  , Record
                                      ( attr = Int `month`
                                      , full_name = 'affiliate.owner.left.lifetime.start.month'
                                      , id = 'affiliate__owner__left__lifetime__start__month'
                                      , name = 'month'
                                      , sig_key = 0
                                      , ui_name = 'Affiliate/Owner/Man/Lifetime/Start/Month'
                                      )
                                  , Record
                                      ( attr = Int `year`
                                      , full_name = 'affiliate.owner.left.lifetime.start.year'
                                      , id = 'affiliate__owner__left__lifetime__start__year'
                                      , name = 'year'
                                      , sig_key = 0
                                      , ui_name = 'Affiliate/Owner/Man/Lifetime/Start/Year'
                                      )
                                  ]
                                , full_name = 'affiliate.owner.left.lifetime.start'
                                , id = 'affiliate__owner__left__lifetime__start'
                                , name = 'start'
                                , sig_key = 0
                                , ui_name = 'Affiliate/Owner/Man/Lifetime/Start'
                                )
                            , Record
                                ( attr = Date `finish`
                                , attrs =
                                  [ Record
                                      ( attr = Int `day`
                                      , full_name = 'affiliate.owner.left.lifetime.finish.day'
                                      , id = 'affiliate__owner__left__lifetime__finish__day'
                                      , name = 'day'
                                      , sig_key = 0
                                      , ui_name = 'Affiliate/Owner/Man/Lifetime/Finish/Day'
                                      )
                                  , Record
                                      ( attr = Int `month`
                                      , full_name = 'affiliate.owner.left.lifetime.finish.month'
                                      , id = 'affiliate__owner__left__lifetime__finish__month'
                                      , name = 'month'
                                      , sig_key = 0
                                      , ui_name = 'Affiliate/Owner/Man/Lifetime/Finish/Month'
                                      )
                                  , Record
                                      ( attr = Int `year`
                                      , full_name = 'affiliate.owner.left.lifetime.finish.year'
                                      , id = 'affiliate__owner__left__lifetime__finish__year'
                                      , name = 'year'
                                      , sig_key = 0
                                      , ui_name = 'Affiliate/Owner/Man/Lifetime/Finish/Year'
                                      )
                                  ]
                                , full_name = 'affiliate.owner.left.lifetime.finish'
                                , id = 'affiliate__owner__left__lifetime__finish'
                                , name = 'finish'
                                , sig_key = 0
                                , ui_name = 'Affiliate/Owner/Man/Lifetime/Finish'
                                )
                            , Record
                                ( attr = Boolean `alive`
                                , choices =
                                  [ 'no'
                                  , 'yes'
                                  ]
                                , full_name = 'affiliate.owner.left.lifetime.alive'
                                , id = 'affiliate__owner__left__lifetime__alive'
                                , name = 'alive'
                                , sig_key = 1
                                , ui_name = 'Affiliate/Owner/Man/Lifetime/Alive'
                                )
                            ]
                          , full_name = 'affiliate.owner.left.lifetime'
                          , id = 'affiliate__owner__left__lifetime'
                          , name = 'lifetime'
                          , ui_name = 'Affiliate/Owner/Man/Lifetime'
                          )
                      , Record
                          ( attr = Sex `sex`
                          , choices =
                            [ ( 'F'
                              , 'Female'
                              )
                            , ( 'M'
                              , 'Male'
                              )
                            ]
                          , full_name = 'affiliate.owner.left.sex'
                          , id = 'affiliate__owner__left__sex'
                          , name = 'sex'
                          , sig_key = 0
                          , ui_name = 'Affiliate/Owner/Man/Sex'
                          )
                      ]
                    , full_name = 'affiliate.owner.left'
                    , id = 'affiliate__owner__left'
                    , name = 'left'
                    , sig_key = 2
                    , type_name = 'PAP.Person'
                    , ui_name = 'Affiliate/Owner/Man'
                    , ui_type_name = 'Person'
                    )
                ]
              , full_name = 'affiliate.owner'
              , id = 'affiliate__owner'
              , name = 'owner'
              , sig_key = 2
              , type_name = 'PAP.Biz_Man'
              , ui_name = 'Affiliate/Owner'
              , ui_type_name = 'Biz_Man'
              )
          , Record
              ( attr = String `registered_in`
              , full_name = 'affiliate.registered_in'
              , id = 'affiliate__registered_in'
              , name = 'registered_in'
              , sig_key = 3
              , ui_name = 'Affiliate/Registered in'
              )
          , Record
              ( attr = Date_Interval `lifetime`
              , attrs =
                [ Record
                    ( attr = Date `start`
                    , attrs =
                      [ Record
                          ( attr = Int `day`
                          , full_name = 'affiliate.lifetime.start.day'
                          , id = 'affiliate__lifetime__start__day'
                          , name = 'day'
                          , sig_key = 0
                          , ui_name = 'Affiliate/Lifetime/Start/Day'
                          )
                      , Record
                          ( attr = Int `month`
                          , full_name = 'affiliate.lifetime.start.month'
                          , id = 'affiliate__lifetime__start__month'
                          , name = 'month'
                          , sig_key = 0
                          , ui_name = 'Affiliate/Lifetime/Start/Month'
                          )
                      , Record
                          ( attr = Int `year`
                          , full_name = 'affiliate.lifetime.start.year'
                          , id = 'affiliate__lifetime__start__year'
                          , name = 'year'
                          , sig_key = 0
                          , ui_name = 'Affiliate/Lifetime/Start/Year'
                          )
                      ]
                    , full_name = 'affiliate.lifetime.start'
                    , id = 'affiliate__lifetime__start'
                    , name = 'start'
                    , sig_key = 0
                    , ui_name = 'Affiliate/Lifetime/Start'
                    )
                , Record
                    ( attr = Date `finish`
                    , attrs =
                      [ Record
                          ( attr = Int `day`
                          , full_name = 'affiliate.lifetime.finish.day'
                          , id = 'affiliate__lifetime__finish__day'
                          , name = 'day'
                          , sig_key = 0
                          , ui_name = 'Affiliate/Lifetime/Finish/Day'
                          )
                      , Record
                          ( attr = Int `month`
                          , full_name = 'affiliate.lifetime.finish.month'
                          , id = 'affiliate__lifetime__finish__month'
                          , name = 'month'
                          , sig_key = 0
                          , ui_name = 'Affiliate/Lifetime/Finish/Month'
                          )
                      , Record
                          ( attr = Int `year`
                          , full_name = 'affiliate.lifetime.finish.year'
                          , id = 'affiliate__lifetime__finish__year'
                          , name = 'year'
                          , sig_key = 0
                          , ui_name = 'Affiliate/Lifetime/Finish/Year'
                          )
                      ]
                    , full_name = 'affiliate.lifetime.finish'
                    , id = 'affiliate__lifetime__finish'
                    , name = 'finish'
                    , sig_key = 0
                    , ui_name = 'Affiliate/Lifetime/Finish'
                    )
                , Record
                    ( attr = Boolean `alive`
                    , choices =
                      [ 'no'
                      , 'yes'
                      ]
                    , full_name = 'affiliate.lifetime.alive'
                    , id = 'affiliate__lifetime__alive'
                    , name = 'alive'
                    , sig_key = 1
                    , ui_name = 'Affiliate/Lifetime/Alive'
                    )
                ]
              , full_name = 'affiliate.lifetime'
              , id = 'affiliate__lifetime'
              , name = 'lifetime'
              , ui_name = 'Affiliate/Lifetime'
              )
          , Record
              ( attr = String `short_name`
              , full_name = 'affiliate.short_name'
              , id = 'affiliate__short_name'
              , name = 'short_name'
              , sig_key = 3
              , ui_name = 'Affiliate/Short name'
              )
          , Record
              ( Class = 'Entity'
              , attr = Entity `affiliate`
              , full_name = 'affiliate.affiliate'
              , id = 'affiliate__affiliate'
              , name = 'affiliate'
              , sig_key = 2
              , type_name = 'PAP.Company_P'
              , ui_name = 'Affiliate/Affiliate'
              , ui_type_name = 'Company_P'
              )
          ]
        , full_name = 'affiliate'
        , id = 'affiliate'
        , name = 'affiliate'
        , sig_key = 2
        , type_name = 'PAP.Company_P'
        , ui_name = 'Affiliate'
        , ui_type_name = 'Company_P'
        )
    , Record
        ( Class = 'Entity'
        , attr = Rev_Ref `creation`
        , attrs =
          [ Record
              ( attr = Date-Time `c_time`
              , full_name = 'creation.c_time'
              , id = 'creation__c_time'
              , name = 'c_time'
              , sig_key = 0
              , ui_name = 'Creation/C time'
              )
          , Record
              ( Class = 'Entity'
              , attr = Entity `c_user`
              , children_np =
                [ Record
                    ( Class = 'Entity'
                    , attr = Entity `c_user`
                    , attrs =
                      [ Record
                          ( attr = Email `name`
                          , full_name = 'creation.c_user[Auth.Account].name'
                          , id = 'creation__c_user[Auth.Account]__name'
                          , name = 'name'
                          , sig_key = 3
                          , ui_name = 'Creation/C user[Account]/Name'
                          )
                      ]
                    , full_name = 'creation.c_user[Auth.Account]'
                    , id = 'creation__c_user[Auth.Account]'
                    , name = 'c_user'
                    , sig_key = 2
                    , type_name = 'Auth.Account'
                    , ui_name = 'Creation/C user[Account]'
                    , ui_type_name = 'Account'
                    )
                , Record
                    ( Class = 'Entity'
                    , attr = Entity `c_user`
                    , attrs =
                      [ Record
                          ( attr = String `last_name`
                          , full_name = 'creation.c_user[PAP.Person].last_name'
                          , id = 'creation__c_user[PAP.Person]__last_name'
                          , name = 'last_name'
                          , sig_key = 3
                          , ui_name = 'Creation/C user[Person]/Last name'
                          )
                      , Record
                          ( attr = String `first_name`
                          , full_name = 'creation.c_user[PAP.Person].first_name'
                          , id = 'creation__c_user[PAP.Person]__first_name'
                          , name = 'first_name'
                          , sig_key = 3
                          , ui_name = 'Creation/C user[Person]/First name'
                          )
                      , Record
                          ( attr = String `middle_name`
                          , full_name = 'creation.c_user[PAP.Person].middle_name'
                          , id = 'creation__c_user[PAP.Person]__middle_name'
                          , name = 'middle_name'
                          , sig_key = 3
                          , ui_name = 'Creation/C user[Person]/Middle name'
                          )
                      , Record
                          ( attr = String `title`
                          , full_name = 'creation.c_user[PAP.Person].title'
                          , id = 'creation__c_user[PAP.Person]__title'
                          , name = 'title'
                          , sig_key = 3
                          , ui_name = 'Creation/C user[Person]/Academic title'
                          )
                      ]
                    , full_name = 'creation.c_user[PAP.Person]'
                    , id = 'creation__c_user[PAP.Person]'
                    , name = 'c_user'
                    , sig_key = 2
                    , type_name = 'PAP.Person'
                    , ui_name = 'Creation/C user[Person]'
                    , ui_type_name = 'Person'
                    )
                ]
              , full_name = 'creation.c_user'
              , id = 'creation__c_user'
              , name = 'c_user'
              , sig_key = 2
              , type_name = 'MOM.Id_Entity'
              , ui_name = 'Creation/C user'
              , ui_type_name = 'Id_Entity'
              )
          , Record
              ( attr = String `kind`
              , full_name = 'creation.kind'
              , id = 'creation__kind'
              , name = 'kind'
              , sig_key = 3
              , ui_name = 'Creation/Kind'
              )
          , Record
              ( attr = Date-Time `time`
              , full_name = 'creation.time'
              , id = 'creation__time'
              , name = 'time'
              , sig_key = 0
              , ui_name = 'Creation/Time'
              )
          , Record
              ( Class = 'Entity'
              , attr = Entity `user`
              , children_np =
                [ Record
                    ( Class = 'Entity'
                    , attr = Entity `user`
                    , attrs =
                      [ Record
                          ( attr = Email `name`
                          , full_name = 'creation.user[Auth.Account].name'
                          , id = 'creation__user[Auth.Account]__name'
                          , name = 'name'
                          , sig_key = 3
                          , ui_name = 'Creation/User[Account]/Name'
                          )
                      ]
                    , full_name = 'creation.user[Auth.Account]'
                    , id = 'creation__user[Auth.Account]'
                    , name = 'user'
                    , sig_key = 2
                    , type_name = 'Auth.Account'
                    , ui_name = 'Creation/User[Account]'
                    , ui_type_name = 'Account'
                    )
                , Record
                    ( Class = 'Entity'
                    , attr = Entity `user`
                    , attrs =
                      [ Record
                          ( attr = String `last_name`
                          , full_name = 'creation.user[PAP.Person].last_name'
                          , id = 'creation__user[PAP.Person]__last_name'
                          , name = 'last_name'
                          , sig_key = 3
                          , ui_name = 'Creation/User[Person]/Last name'
                          )
                      , Record
                          ( attr = String `first_name`
                          , full_name = 'creation.user[PAP.Person].first_name'
                          , id = 'creation__user[PAP.Person]__first_name'
                          , name = 'first_name'
                          , sig_key = 3
                          , ui_name = 'Creation/User[Person]/First name'
                          )
                      , Record
                          ( attr = String `middle_name`
                          , full_name = 'creation.user[PAP.Person].middle_name'
                          , id = 'creation__user[PAP.Person]__middle_name'
                          , name = 'middle_name'
                          , sig_key = 3
                          , ui_name = 'Creation/User[Person]/Middle name'
                          )
                      , Record
                          ( attr = String `title`
                          , full_name = 'creation.user[PAP.Person].title'
                          , id = 'creation__user[PAP.Person]__title'
                          , name = 'title'
                          , sig_key = 3
                          , ui_name = 'Creation/User[Person]/Academic title'
                          )
                      ]
                    , full_name = 'creation.user[PAP.Person]'
                    , id = 'creation__user[PAP.Person]'
                    , name = 'user'
                    , sig_key = 2
                    , type_name = 'PAP.Person'
                    , ui_name = 'Creation/User[Person]'
                    , ui_type_name = 'Person'
                    )
                ]
              , full_name = 'creation.user'
              , id = 'creation__user'
              , name = 'user'
              , sig_key = 2
              , type_name = 'MOM.Id_Entity'
              , ui_name = 'Creation/User'
              , ui_type_name = 'Id_Entity'
              )
          ]
        , full_name = 'creation'
        , id = 'creation'
        , name = 'creation'
        , sig_key = 2
        , type_name = 'MOM.MD_Change'
        , ui_name = 'Creation'
        , ui_type_name = 'MD_Change'
        )
    , Record
        ( Class = 'Entity'
        , attr = Rev_Ref `last_change`
        , attrs =
          [ Record
              ( attr = Date-Time `c_time`
              , full_name = 'last_change.c_time'
              , id = 'last_change__c_time'
              , name = 'c_time'
              , sig_key = 0
              , ui_name = 'Last change/C time'
              )
          , Record
              ( Class = 'Entity'
              , attr = Entity `c_user`
              , children_np =
                [ Record
                    ( Class = 'Entity'
                    , attr = Entity `c_user`
                    , attrs =
                      [ Record
                          ( attr = Email `name`
                          , full_name = 'last_change.c_user[Auth.Account].name'
                          , id = 'last_change__c_user[Auth.Account]__name'
                          , name = 'name'
                          , sig_key = 3
                          , ui_name = 'Last change/C user[Account]/Name'
                          )
                      ]
                    , full_name = 'last_change.c_user[Auth.Account]'
                    , id = 'last_change__c_user[Auth.Account]'
                    , name = 'c_user'
                    , sig_key = 2
                    , type_name = 'Auth.Account'
                    , ui_name = 'Last change/C user[Account]'
                    , ui_type_name = 'Account'
                    )
                , Record
                    ( Class = 'Entity'
                    , attr = Entity `c_user`
                    , attrs =
                      [ Record
                          ( attr = String `last_name`
                          , full_name = 'last_change.c_user[PAP.Person].last_name'
                          , id = 'last_change__c_user[PAP.Person]__last_name'
                          , name = 'last_name'
                          , sig_key = 3
                          , ui_name = 'Last change/C user[Person]/Last name'
                          )
                      , Record
                          ( attr = String `first_name`
                          , full_name = 'last_change.c_user[PAP.Person].first_name'
                          , id = 'last_change__c_user[PAP.Person]__first_name'
                          , name = 'first_name'
                          , sig_key = 3
                          , ui_name = 'Last change/C user[Person]/First name'
                          )
                      , Record
                          ( attr = String `middle_name`
                          , full_name = 'last_change.c_user[PAP.Person].middle_name'
                          , id = 'last_change__c_user[PAP.Person]__middle_name'
                          , name = 'middle_name'
                          , sig_key = 3
                          , ui_name = 'Last change/C user[Person]/Middle name'
                          )
                      , Record
                          ( attr = String `title`
                          , full_name = 'last_change.c_user[PAP.Person].title'
                          , id = 'last_change__c_user[PAP.Person]__title'
                          , name = 'title'
                          , sig_key = 3
                          , ui_name = 'Last change/C user[Person]/Academic title'
                          )
                      ]
                    , full_name = 'last_change.c_user[PAP.Person]'
                    , id = 'last_change__c_user[PAP.Person]'
                    , name = 'c_user'
                    , sig_key = 2
                    , type_name = 'PAP.Person'
                    , ui_name = 'Last change/C user[Person]'
                    , ui_type_name = 'Person'
                    )
                ]
              , full_name = 'last_change.c_user'
              , id = 'last_change__c_user'
              , name = 'c_user'
              , sig_key = 2
              , type_name = 'MOM.Id_Entity'
              , ui_name = 'Last change/C user'
              , ui_type_name = 'Id_Entity'
              )
          , Record
              ( attr = String `kind`
              , full_name = 'last_change.kind'
              , id = 'last_change__kind'
              , name = 'kind'
              , sig_key = 3
              , ui_name = 'Last change/Kind'
              )
          , Record
              ( attr = Date-Time `time`
              , full_name = 'last_change.time'
              , id = 'last_change__time'
              , name = 'time'
              , sig_key = 0
              , ui_name = 'Last change/Time'
              )
          , Record
              ( Class = 'Entity'
              , attr = Entity `user`
              , children_np =
                [ Record
                    ( Class = 'Entity'
                    , attr = Entity `user`
                    , attrs =
                      [ Record
                          ( attr = Email `name`
                          , full_name = 'last_change.user[Auth.Account].name'
                          , id = 'last_change__user[Auth.Account]__name'
                          , name = 'name'
                          , sig_key = 3
                          , ui_name = 'Last change/User[Account]/Name'
                          )
                      ]
                    , full_name = 'last_change.user[Auth.Account]'
                    , id = 'last_change__user[Auth.Account]'
                    , name = 'user'
                    , sig_key = 2
                    , type_name = 'Auth.Account'
                    , ui_name = 'Last change/User[Account]'
                    , ui_type_name = 'Account'
                    )
                , Record
                    ( Class = 'Entity'
                    , attr = Entity `user`
                    , attrs =
                      [ Record
                          ( attr = String `last_name`
                          , full_name = 'last_change.user[PAP.Person].last_name'
                          , id = 'last_change__user[PAP.Person]__last_name'
                          , name = 'last_name'
                          , sig_key = 3
                          , ui_name = 'Last change/User[Person]/Last name'
                          )
                      , Record
                          ( attr = String `first_name`
                          , full_name = 'last_change.user[PAP.Person].first_name'
                          , id = 'last_change__user[PAP.Person]__first_name'
                          , name = 'first_name'
                          , sig_key = 3
                          , ui_name = 'Last change/User[Person]/First name'
                          )
                      , Record
                          ( attr = String `middle_name`
                          , full_name = 'last_change.user[PAP.Person].middle_name'
                          , id = 'last_change__user[PAP.Person]__middle_name'
                          , name = 'middle_name'
                          , sig_key = 3
                          , ui_name = 'Last change/User[Person]/Middle name'
                          )
                      , Record
                          ( attr = String `title`
                          , full_name = 'last_change.user[PAP.Person].title'
                          , id = 'last_change__user[PAP.Person]__title'
                          , name = 'title'
                          , sig_key = 3
                          , ui_name = 'Last change/User[Person]/Academic title'
                          )
                      ]
                    , full_name = 'last_change.user[PAP.Person]'
                    , id = 'last_change__user[PAP.Person]'
                    , name = 'user'
                    , sig_key = 2
                    , type_name = 'PAP.Person'
                    , ui_name = 'Last change/User[Person]'
                    , ui_type_name = 'Person'
                    )
                ]
              , full_name = 'last_change.user'
              , id = 'last_change__user'
              , name = 'user'
              , sig_key = 2
              , type_name = 'MOM.Id_Entity'
              , ui_name = 'Last change/User'
              , ui_type_name = 'Id_Entity'
              )
          ]
        , full_name = 'last_change'
        , id = 'last_change'
        , name = 'last_change'
        , sig_key = 2
        , type_name = 'MOM.MD_Change'
        , ui_name = 'Last change'
        , ui_type_name = 'MD_Change'
        )
    , Record
        ( attr = Int `last_cid`
        , full_name = 'last_cid'
        , id = 'last_cid'
        , name = 'last_cid'
        , sig_key = 0
        , ui_name = 'Last cid'
        )
    , Record
        ( attr = Surrogate `pid`
        , full_name = 'pid'
        , id = 'pid'
        , name = 'pid'
        , sig_key = 0
        , ui_name = 'Pid'
        )
    , Record
        ( attr = String `type_name`
        , full_name = 'type_name'
        , id = 'type_name'
        , name = 'type_name'
        , sig_key = 3
        , ui_name = 'Type name'
        )
    , Record
        ( Class = 'Entity'
        , attr = Link_Ref_List `events`
        , attrs =
          [ Record
              ( attr = Date_Interval `date`
              , attrs =
                [ Record
                    ( attr = Date `start`
                    , attrs =
                      [ Record
                          ( attr = Int `day`
                          , full_name = 'events.date.start.day'
                          , id = 'events__date__start__day'
                          , name = 'day'
                          , sig_key = 0
                          , ui_name = 'Events/Date/Start/Day'
                          )
                      , Record
                          ( attr = Int `month`
                          , full_name = 'events.date.start.month'
                          , id = 'events__date__start__month'
                          , name = 'month'
                          , sig_key = 0
                          , ui_name = 'Events/Date/Start/Month'
                          )
                      , Record
                          ( attr = Int `year`
                          , full_name = 'events.date.start.year'
                          , id = 'events__date__start__year'
                          , name = 'year'
                          , sig_key = 0
                          , ui_name = 'Events/Date/Start/Year'
                          )
                      ]
                    , full_name = 'events.date.start'
                    , id = 'events__date__start'
                    , name = 'start'
                    , sig_key = 0
                    , ui_name = 'Events/Date/Start'
                    )
                , Record
                    ( attr = Date `finish`
                    , attrs =
                      [ Record
                          ( attr = Int `day`
                          , full_name = 'events.date.finish.day'
                          , id = 'events__date__finish__day'
                          , name = 'day'
                          , sig_key = 0
                          , ui_name = 'Events/Date/Finish/Day'
                          )
                      , Record
                          ( attr = Int `month`
                          , full_name = 'events.date.finish.month'
                          , id = 'events__date__finish__month'
                          , name = 'month'
                          , sig_key = 0
                          , ui_name = 'Events/Date/Finish/Month'
                          )
                      , Record
                          ( attr = Int `year`
                          , full_name = 'events.date.finish.year'
                          , id = 'events__date__finish__year'
                          , name = 'year'
                          , sig_key = 0
                          , ui_name = 'Events/Date/Finish/Year'
                          )
                      ]
                    , full_name = 'events.date.finish'
                    , id = 'events__date__finish'
                    , name = 'finish'
                    , sig_key = 0
                    , ui_name = 'Events/Date/Finish'
                    )
                , Record
                    ( attr = Boolean `alive`
                    , choices =
                      [ 'no'
                      , 'yes'
                      ]
                    , full_name = 'events.date.alive'
                    , id = 'events__date__alive'
                    , name = 'alive'
                    , sig_key = 1
                    , ui_name = 'Events/Date/Alive'
                    )
                ]
              , full_name = 'events.date'
              , id = 'events__date'
              , name = 'date'
              , ui_name = 'Events/Date'
              )
          , Record
              ( attr = Time_Interval `time`
              , attrs =
                [ Record
                    ( attr = Time `start`
                    , attrs =
                      [ Record
                          ( attr = Int `hour`
                          , full_name = 'events.time.start.hour'
                          , id = 'events__time__start__hour'
                          , name = 'hour'
                          , sig_key = 0
                          , ui_name = 'Events/Time/Start/Hour'
                          )
                      , Record
                          ( attr = Int `minute`
                          , full_name = 'events.time.start.minute'
                          , id = 'events__time__start__minute'
                          , name = 'minute'
                          , sig_key = 0
                          , ui_name = 'Events/Time/Start/Minute'
                          )
                      , Record
                          ( attr = Int `second`
                          , full_name = 'events.time.start.second'
                          , id = 'events__time__start__second'
                          , name = 'second'
                          , sig_key = 0
                          , ui_name = 'Events/Time/Start/Second'
                          )
                      ]
                    , full_name = 'events.time.start'
                    , id = 'events__time__start'
                    , name = 'start'
                    , sig_key = 0
                    , ui_name = 'Events/Time/Start'
                    )
                , Record
                    ( attr = Time `finish`
                    , attrs =
                      [ Record
                          ( attr = Int `hour`
                          , full_name = 'events.time.finish.hour'
                          , id = 'events__time__finish__hour'
                          , name = 'hour'
                          , sig_key = 0
                          , ui_name = 'Events/Time/Finish/Hour'
                          )
                      , Record
                          ( attr = Int `minute`
                          , full_name = 'events.time.finish.minute'
                          , id = 'events__time__finish__minute'
                          , name = 'minute'
                          , sig_key = 0
                          , ui_name = 'Events/Time/Finish/Minute'
                          )
                      , Record
                          ( attr = Int `second`
                          , full_name = 'events.time.finish.second'
                          , id = 'events__time__finish__second'
                          , name = 'second'
                          , sig_key = 0
                          , ui_name = 'Events/Time/Finish/Second'
                          )
                      ]
                    , full_name = 'events.time.finish'
                    , id = 'events__time__finish'
                    , name = 'finish'
                    , sig_key = 0
                    , ui_name = 'Events/Time/Finish'
                    )
                ]
              , full_name = 'events.time'
              , id = 'events__time'
              , name = 'time'
              , ui_name = 'Events/Time'
              )
          , Record
              ( Class = 'Entity'
              , attr = Entity `calendar`
              , attrs =
                [ Record
                    ( attr = Name `name`
                    , full_name = 'events.calendar.name'
                    , id = 'events__calendar__name'
                    , name = 'name'
                    , sig_key = 3
                    , ui_name = 'Events/Calendar/Name'
                    )
                , Record
                    ( attr = String `desc`
                    , full_name = 'events.calendar.desc'
                    , id = 'events__calendar__desc'
                    , name = 'desc'
                    , sig_key = 3
                    , ui_name = 'Events/Calendar/Description'
                    )
                ]
              , full_name = 'events.calendar'
              , id = 'events__calendar'
              , name = 'calendar'
              , sig_key = 2
              , type_name = 'EVT.Calendar'
              , ui_name = 'Events/Calendar'
              , ui_type_name = 'Calendar'
              )
          , Record
              ( attr = String `detail`
              , full_name = 'events.detail'
              , id = 'events__detail'
              , name = 'detail'
              , sig_key = 3
              , ui_name = 'Events/Detail'
              )
          , Record
              ( attr = String `short_title`
              , full_name = 'events.short_title'
              , id = 'events__short_title'
              , name = 'short_title'
              , sig_key = 3
              , ui_name = 'Events/Short title'
              )
          ]
        , full_name = 'events'
        , id = 'events'
        , name = 'events'
        , sig_key = 2
        , type_name = 'EVT.Event'
        , ui_name = 'Events'
        , ui_type_name = 'Event'
        )
    , Record
        ( Class = 'Entity'
        , attr = Role_Ref_Set `urls`
        , attrs =
          [ Record
              ( attr = Url `value`
              , full_name = 'urls.value'
              , id = 'urls__value'
              , name = 'value'
              , sig_key = 3
              , ui_name = 'Urls/Value'
              )
          , Record
              ( attr = String `desc`
              , full_name = 'urls.desc'
              , id = 'urls__desc'
              , name = 'desc'
              , sig_key = 3
              , ui_name = 'Urls/Description'
              )
          ]
        , full_name = 'urls'
        , id = 'urls'
        , name = 'urls'
        , sig_key = 2
        , type_name = 'PAP.Url'
        , ui_name = 'Urls'
        , ui_type_name = 'Url'
        )
    , Record
        ( Class = 'Entity'
        , attr = Role_Ref_Set `phones`
        , attrs =
          [ Record
              ( attr = Numeric_String `sn`
              , full_name = 'phones.sn'
              , id = 'phones__sn'
              , name = 'sn'
              , sig_key = 3
              , ui_name = 'Phones/Subscriber number'
              )
          , Record
              ( attr = Numeric_String `ndc`
              , full_name = 'phones.ndc'
              , id = 'phones__ndc'
              , name = 'ndc'
              , sig_key = 3
              , ui_name = 'Phones/Network destination code'
              )
          , Record
              ( attr = Numeric_String `cc`
              , full_name = 'phones.cc'
              , id = 'phones__cc'
              , name = 'cc'
              , sig_key = 3
              , ui_name = 'Phones/Country code'
              )
          , Record
              ( attr = String `desc`
              , full_name = 'phones.desc'
              , id = 'phones__desc'
              , name = 'desc'
              , sig_key = 3
              , ui_name = 'Phones/Description'
              )
          ]
        , full_name = 'phones'
        , id = 'phones'
        , name = 'phones'
        , sig_key = 2
        , type_name = 'PAP.Phone'
        , ui_name = 'Phones'
        , ui_type_name = 'Phone'
        )
    , Record
        ( Class = 'Entity'
        , attr = Role_Ref_Set `emails`
        , attrs =
          [ Record
              ( attr = Email `address`
              , full_name = 'emails.address'
              , id = 'emails__address'
              , name = 'address'
              , sig_key = 3
              , ui_name = 'Emails/Email address'
              )
          , Record
              ( attr = String `desc`
              , full_name = 'emails.desc'
              , id = 'emails__desc'
              , name = 'desc'
              , sig_key = 3
              , ui_name = 'Emails/Description'
              )
          ]
        , full_name = 'emails'
        , id = 'emails'
        , name = 'emails'
        , sig_key = 2
        , type_name = 'PAP.Email'
        , ui_name = 'Emails'
        , ui_type_name = 'Email'
        )
    , Record
        ( Class = 'Entity'
        , attr = Role_Ref_Set `addresses`
        , attrs =
          [ Record
              ( attr = String `street`
              , full_name = 'addresses.street'
              , id = 'addresses__street'
              , name = 'street'
              , sig_key = 3
              , ui_name = 'Addresses/Street'
              )
          , Record
              ( attr = String `zip`
              , full_name = 'addresses.zip'
              , id = 'addresses__zip'
              , name = 'zip'
              , sig_key = 3
              , ui_name = 'Addresses/Zip code'
              )
          , Record
              ( attr = String `city`
              , full_name = 'addresses.city'
              , id = 'addresses__city'
              , name = 'city'
              , sig_key = 3
              , ui_name = 'Addresses/City'
              )
          , Record
              ( attr = String `country`
              , full_name = 'addresses.country'
              , id = 'addresses__country'
              , name = 'country'
              , sig_key = 3
              , ui_name = 'Addresses/Country'
              )
          , Record
              ( attr = String `desc`
              , full_name = 'addresses.desc'
              , id = 'addresses__desc'
              , name = 'desc'
              , sig_key = 3
              , ui_name = 'Addresses/Description'
              )
          , Record
              ( attr = String `region`
              , full_name = 'addresses.region'
              , id = 'addresses__region'
              , name = 'region'
              , sig_key = 3
              , ui_name = 'Addresses/Region'
              )
          ]
        , full_name = 'addresses'
        , id = 'addresses'
        , name = 'addresses'
        , sig_key = 2
        , type_name = 'PAP.Address'
        , ui_name = 'Addresses'
        , ui_type_name = 'Address'
        )
    ]

    >>> QR  = GTW.RST.TOP.MOM.Query_Restriction
    >>> print (formatted (QR.Filter_Atoms (QR.Filter (PAP.Company_P, "affiliate"))))
    ( Record
      ( AQ = <name.AQ [Attr.Type.Querier String]>
      , attr = String `name`
      , edit = None
      , full_name = 'name'
      , id = 'name___AC'
      , name = 'name___AC'
      , op = Record
          ( desc = 'Select entities where the attribute value starts with the specified value'
          , label = 'auto-complete'
          )
      , sig_key = 3
      , ui_name = 'Name'
      , value = None
      )
    , Record
      ( AQ = <owner.left.last_name.AQ [Attr.Type.Querier String_FL]>
      , attr = String `last_name`
      , edit = None
      , full_name = 'owner.left.last_name'
      , id = 'owner__left__last_name___AC'
      , name = 'owner__left__last_name___AC'
      , op = Record
          ( desc = 'Select entities where the attribute value starts with the specified value'
          , label = 'auto-complete'
          )
      , sig_key = 3
      , ui_name = 'Owner/Man/Last name'
      , value = None
      )
    , Record
      ( AQ = <owner.left.first_name.AQ [Attr.Type.Querier String_FL]>
      , attr = String `first_name`
      , edit = None
      , full_name = 'owner.left.first_name'
      , id = 'owner__left__first_name___AC'
      , name = 'owner__left__first_name___AC'
      , op = Record
          ( desc = 'Select entities where the attribute value starts with the specified value'
          , label = 'auto-complete'
          )
      , sig_key = 3
      , ui_name = 'Owner/Man/First name'
      , value = None
      )
    , Record
      ( AQ = <owner.left.middle_name.AQ [Attr.Type.Querier String]>
      , attr = String `middle_name`
      , edit = None
      , full_name = 'owner.left.middle_name'
      , id = 'owner__left__middle_name___AC'
      , name = 'owner__left__middle_name___AC'
      , op = Record
          ( desc = 'Select entities where the attribute value starts with the specified value'
          , label = 'auto-complete'
          )
      , sig_key = 3
      , ui_name = 'Owner/Man/Middle name'
      , value = None
      )
    , Record
      ( AQ = <owner.left.title.AQ [Attr.Type.Querier String]>
      , attr = String `title`
      , edit = None
      , full_name = 'owner.left.title'
      , id = 'owner__left__title___AC'
      , name = 'owner__left__title___AC'
      , op = Record
          ( desc = 'Select entities where the attribute value starts with the specified value'
          , label = 'auto-complete'
          )
      , sig_key = 3
      , ui_name = 'Owner/Man/Academic title'
      , value = None
      )
    , Record
      ( AQ = <registered_in.AQ [Attr.Type.Querier String]>
      , attr = String `registered_in`
      , edit = None
      , full_name = 'registered_in'
      , id = 'registered_in___AC'
      , name = 'registered_in___AC'
      , op = Record
          ( desc = 'Select entities where the attribute value starts with the specified value'
          , label = 'auto-complete'
          )
      , sig_key = 3
      , ui_name = 'Registered in'
      , value = None
      )
    )

    >>> print (formatted (PAP.Company_has_Phone.AQ.As_Json_Cargo ["filters"]))
    [ { 'Class' : 'Entity'
      , 'children_np' :
          [ { 'Class' : 'Entity'
            , 'attrs' :
                [ { 'name' : 'name'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Name'
                  }
                , { 'name' : 'registered_in'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Registered in'
                  }
                , { 'attrs' :
                      [ { 'name' : 'start'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Start'
                        }
                      , { 'name' : 'finish'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Finish'
                        }
                      ]
                  , 'name' : 'lifetime'
                  , 'ui_name' : 'Lifetime'
                  }
                , { 'name' : 'short_name'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Short name'
                  }
                ]
            , 'name' : 'left'
            , 'sig_key' : 2
            , 'type_name' : 'PAP.Company'
            , 'ui_name' : 'Company'
            , 'ui_type_name' : 'Company'
            }
          , { 'Class' : 'Entity'
            , 'attrs' :
                [ { 'name' : 'name'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Name'
                  }
                , { 'Class' : 'Entity'
                  , 'attrs' :
                      [ { 'Class' : 'Entity'
                        , 'attrs' :
                            [ { 'name' : 'last_name'
                              , 'sig_key' : 3
                              , 'ui_name' : 'Last name'
                              }
                            , { 'name' : 'first_name'
                              , 'sig_key' : 3
                              , 'ui_name' : 'First name'
                              }
                            , { 'name' : 'middle_name'
                              , 'sig_key' : 3
                              , 'ui_name' : 'Middle name'
                              }
                            , { 'name' : 'title'
                              , 'sig_key' : 3
                              , 'ui_name' : 'Academic title'
                              }
                            ]
                        , 'name' : 'left'
                        , 'sig_key' : 2
                        , 'ui_name' : 'Man'
                        }
                      ]
                  , 'name' : 'owner'
                  , 'sig_key' : 2
                  , 'ui_name' : 'Owner'
                  }
                , { 'name' : 'registered_in'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Registered in'
                  }
                ]
            , 'name' : 'left'
            , 'sig_key' : 2
            , 'type_name' : 'PAP.Company_P'
            , 'ui_name' : 'Company'
            , 'ui_type_name' : 'Company_P'
            }
          ]
      , 'name' : 'left'
      , 'sig_key' : 2
      , 'ui_name' : 'Company'
      }
    , { 'Class' : 'Entity'
      , 'attrs' :
          [ { 'name' : 'sn'
            , 'sig_key' : 3
            , 'ui_name' : 'Subscriber number'
            }
          , { 'name' : 'ndc'
            , 'sig_key' : 3
            , 'ui_name' : 'Network destination code'
            }
          , { 'name' : 'cc'
            , 'sig_key' : 3
            , 'ui_name' : 'Country code'
            }
          , { 'name' : 'desc'
            , 'sig_key' : 3
            , 'ui_name' : 'Description'
            }
          ]
      , 'name' : 'right'
      , 'sig_key' : 2
      , 'ui_name' : 'Phone'
      }
    , { 'name' : 'extension'
      , 'sig_key' : 3
      , 'ui_name' : 'Extension'
      }
    , { 'name' : 'desc'
      , 'sig_key' : 3
      , 'ui_name' : 'Description'
      }
    , { 'Class' : 'Entity'
      , 'attrs' :
          [ { 'name' : 'c_time'
            , 'sig_key' : 0
            , 'ui_name' : 'C time'
            }
          , { 'Class' : 'Entity'
            , 'children_np' :
                [ { 'Class' : 'Entity'
                  , 'attrs' :
                      [ { 'name' : 'name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Name'
                        }
                      ]
                  , 'name' : 'c_user'
                  , 'sig_key' : 2
                  , 'type_name' : 'Auth.Account'
                  , 'ui_name' : 'C user'
                  , 'ui_type_name' : 'Account'
                  }
                , { 'Class' : 'Entity'
                  , 'attrs' :
                      [ { 'name' : 'last_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Last name'
                        }
                      , { 'name' : 'first_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'First name'
                        }
                      , { 'name' : 'middle_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Middle name'
                        }
                      , { 'name' : 'title'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Academic title'
                        }
                      ]
                  , 'name' : 'c_user'
                  , 'sig_key' : 2
                  , 'type_name' : 'PAP.Person'
                  , 'ui_name' : 'C user'
                  , 'ui_type_name' : 'Person'
                  }
                ]
            , 'name' : 'c_user'
            , 'sig_key' : 2
            , 'ui_name' : 'C user'
            }
          , { 'name' : 'kind'
            , 'sig_key' : 3
            , 'ui_name' : 'Kind'
            }
          , { 'name' : 'time'
            , 'sig_key' : 0
            , 'ui_name' : 'Time'
            }
          , { 'Class' : 'Entity'
            , 'children_np' :
                [ { 'Class' : 'Entity'
                  , 'attrs' :
                      [ { 'name' : 'name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Name'
                        }
                      ]
                  , 'name' : 'user'
                  , 'sig_key' : 2
                  , 'type_name' : 'Auth.Account'
                  , 'ui_name' : 'User'
                  , 'ui_type_name' : 'Account'
                  }
                , { 'Class' : 'Entity'
                  , 'attrs' :
                      [ { 'name' : 'last_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Last name'
                        }
                      , { 'name' : 'first_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'First name'
                        }
                      , { 'name' : 'middle_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Middle name'
                        }
                      , { 'name' : 'title'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Academic title'
                        }
                      ]
                  , 'name' : 'user'
                  , 'sig_key' : 2
                  , 'type_name' : 'PAP.Person'
                  , 'ui_name' : 'User'
                  , 'ui_type_name' : 'Person'
                  }
                ]
            , 'name' : 'user'
            , 'sig_key' : 2
            , 'ui_name' : 'User'
            }
          ]
      , 'name' : 'creation'
      , 'sig_key' : 2
      , 'ui_name' : 'Creation'
      }
    , { 'Class' : 'Entity'
      , 'attrs' :
          [ { 'name' : 'c_time'
            , 'sig_key' : 0
            , 'ui_name' : 'C time'
            }
          , { 'Class' : 'Entity'
            , 'children_np' :
                [ { 'Class' : 'Entity'
                  , 'attrs' :
                      [ { 'name' : 'name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Name'
                        }
                      ]
                  , 'name' : 'c_user'
                  , 'sig_key' : 2
                  , 'type_name' : 'Auth.Account'
                  , 'ui_name' : 'C user'
                  , 'ui_type_name' : 'Account'
                  }
                , { 'Class' : 'Entity'
                  , 'attrs' :
                      [ { 'name' : 'last_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Last name'
                        }
                      , { 'name' : 'first_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'First name'
                        }
                      , { 'name' : 'middle_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Middle name'
                        }
                      , { 'name' : 'title'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Academic title'
                        }
                      ]
                  , 'name' : 'c_user'
                  , 'sig_key' : 2
                  , 'type_name' : 'PAP.Person'
                  , 'ui_name' : 'C user'
                  , 'ui_type_name' : 'Person'
                  }
                ]
            , 'name' : 'c_user'
            , 'sig_key' : 2
            , 'ui_name' : 'C user'
            }
          , { 'name' : 'kind'
            , 'sig_key' : 3
            , 'ui_name' : 'Kind'
            }
          , { 'name' : 'time'
            , 'sig_key' : 0
            , 'ui_name' : 'Time'
            }
          , { 'Class' : 'Entity'
            , 'children_np' :
                [ { 'Class' : 'Entity'
                  , 'attrs' :
                      [ { 'name' : 'name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Name'
                        }
                      ]
                  , 'name' : 'user'
                  , 'sig_key' : 2
                  , 'type_name' : 'Auth.Account'
                  , 'ui_name' : 'User'
                  , 'ui_type_name' : 'Account'
                  }
                , { 'Class' : 'Entity'
                  , 'attrs' :
                      [ { 'name' : 'last_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Last name'
                        }
                      , { 'name' : 'first_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'First name'
                        }
                      , { 'name' : 'middle_name'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Middle name'
                        }
                      , { 'name' : 'title'
                        , 'sig_key' : 3
                        , 'ui_name' : 'Academic title'
                        }
                      ]
                  , 'name' : 'user'
                  , 'sig_key' : 2
                  , 'type_name' : 'PAP.Person'
                  , 'ui_name' : 'User'
                  , 'ui_type_name' : 'Person'
                  }
                ]
            , 'name' : 'user'
            , 'sig_key' : 2
            , 'ui_name' : 'User'
            }
          ]
      , 'name' : 'last_change'
      , 'sig_key' : 2
      , 'ui_name' : 'Last change'
      }
    , { 'name' : 'last_cid'
      , 'sig_key' : 0
      , 'ui_name' : 'Last cid'
      }
    , { 'name' : 'pid'
      , 'sig_key' : 0
      , 'ui_name' : 'Pid'
      }
    , { 'name' : 'type_name'
      , 'sig_key' : 3
      , 'ui_name' : 'Type name'
      }
    , { 'Class' : 'Entity'
      , 'attrs' :
          [ { 'attrs' :
                [ { 'attrs' :
                      [ { 'name' : 'day'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Day'
                        }
                      , { 'name' : 'month'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Month'
                        }
                      , { 'name' : 'year'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Year'
                        }
                      ]
                  , 'name' : 'start'
                  , 'sig_key' : 0
                  , 'ui_name' : 'Start'
                  }
                , { 'attrs' :
                      [ { 'name' : 'day'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Day'
                        }
                      , { 'name' : 'month'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Month'
                        }
                      , { 'name' : 'year'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Year'
                        }
                      ]
                  , 'name' : 'finish'
                  , 'sig_key' : 0
                  , 'ui_name' : 'Finish'
                  }
                , { 'name' : 'alive'
                  , 'sig_key' : 1
                  , 'ui_name' : 'Alive'
                  }
                ]
            , 'name' : 'date'
            , 'ui_name' : 'Date'
            }
          , { 'attrs' :
                [ { 'attrs' :
                      [ { 'name' : 'hour'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Hour'
                        }
                      , { 'name' : 'minute'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Minute'
                        }
                      , { 'name' : 'second'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Second'
                        }
                      ]
                  , 'name' : 'start'
                  , 'sig_key' : 0
                  , 'ui_name' : 'Start'
                  }
                , { 'attrs' :
                      [ { 'name' : 'hour'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Hour'
                        }
                      , { 'name' : 'minute'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Minute'
                        }
                      , { 'name' : 'second'
                        , 'sig_key' : 0
                        , 'ui_name' : 'Second'
                        }
                      ]
                  , 'name' : 'finish'
                  , 'sig_key' : 0
                  , 'ui_name' : 'Finish'
                  }
                ]
            , 'name' : 'time'
            , 'ui_name' : 'Time'
            }
          , { 'Class' : 'Entity'
            , 'attrs' :
                [ { 'name' : 'name'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Name'
                  }
                , { 'name' : 'desc'
                  , 'sig_key' : 3
                  , 'ui_name' : 'Description'
                  }
                ]
            , 'name' : 'calendar'
            , 'sig_key' : 2
            , 'ui_name' : 'Calendar'
            }
          , { 'name' : 'detail'
            , 'sig_key' : 3
            , 'ui_name' : 'Detail'
            }
          , { 'name' : 'short_title'
            , 'sig_key' : 3
            , 'ui_name' : 'Short title'
            }
          ]
      , 'name' : 'events'
      , 'sig_key' : 2
      , 'ui_name' : 'Events'
      }
    ]

"""

_test_entity_attr = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> MOM = scope.MOM
    >>> PAP = scope.PAP
    >>> sk = lambda x : (not bool (x.children), x.i_rank)

    >>> show_T_attrs (PAP.Subject, "%%s%%-15s %%-10s %%-25.25s %%s", None, sk)
    PAP.Subject
        address_links   query      PAP.Subject_has_Address   PAP.Subject_has_Address
        addresses       query      PAP.Address               PAP.Subject_has_Address
        created_by      computed   MOM.Id_Entity
        email_links     query      PAP.Subject_has_Email     PAP.Subject_has_Email
        emails          query      PAP.Email                 PAP.Subject_has_Email
        events          query      EVT.Event                 EVT.Event
        last_changed_by computed   MOM.Id_Entity
        phone_links     query      PAP.Subject_has_Phone     PAP.Subject_has_Phone
        phones          query      PAP.Phone                 PAP.Subject_has_Phone
        property_links  query      PAP.Subject_has_Property  PAP.Subject_has_Property
        url_links       query      PAP.Subject_has_Url       PAP.Subject_has_Url
        urls            query      PAP.Url                   PAP.Subject_has_Url
    .PAP.Group
        address_links   query      PAP.Subject_has_Address   PAP.Subject_has_Address
        addresses       query      PAP.Address               PAP.Subject_has_Address
        created_by      computed   MOM.Id_Entity
        email_links     query      PAP.Subject_has_Email     PAP.Subject_has_Email
        emails          query      PAP.Email                 PAP.Subject_has_Email
        events          query      EVT.Event                 EVT.Event
        last_changed_by computed   MOM.Id_Entity
        phone_links     query      PAP.Subject_has_Phone     PAP.Subject_has_Phone
        phones          query      PAP.Phone                 PAP.Subject_has_Phone
        property_links  query      PAP.Subject_has_Property  PAP.Subject_has_Property
        url_links       query      PAP.Subject_has_Url       PAP.Subject_has_Url
        urls            query      PAP.Url                   PAP.Subject_has_Url
    ..PAP.Legal_Entity
        address_links   query      PAP.Subject_has_Address   PAP.Subject_has_Address
        addresses       query      PAP.Address               PAP.Subject_has_Address
        created_by      computed   MOM.Id_Entity
        email_links     query      PAP.Subject_has_Email     PAP.Subject_has_Email
        emails          query      PAP.Email                 PAP.Subject_has_Email
        events          query      EVT.Event                 EVT.Event
        last_changed_by computed   MOM.Id_Entity
        phone_links     query      PAP.Subject_has_Phone     PAP.Subject_has_Phone
        phones          query      PAP.Phone                 PAP.Subject_has_Phone
        property_links  query      PAP.Subject_has_Property  PAP.Subject_has_Property
        url_links       query      PAP.Subject_has_Url       PAP.Subject_has_Url
        urls            query      PAP.Url                   PAP.Subject_has_Url
    ...PAP.Company
        address_links   query      PAP.Company_has_Address   PAP.Company_has_Address
        addresses       query      PAP.Address               PAP.Company_has_Address
        created_by      computed   MOM.Id_Entity
        email_links     query      PAP.Company_has_Email     PAP.Company_has_Email
        emails          query      PAP.Email                 PAP.Company_has_Email
        events          query      EVT.Event                 EVT.Event
        last_changed_by computed   MOM.Id_Entity
        phone_links     query      PAP.Company_has_Phone     PAP.Company_has_Phone
        phones          query      PAP.Phone                 PAP.Company_has_Phone
        property_links  query      PAP.Subject_has_Property  PAP.Subject_has_Property
        url_links       query      PAP.Company_has_Url       PAP.Company_has_Url
        urls            query      PAP.Url                   PAP.Company_has_Url
    ....PAP.Company_P
        address_links   query      PAP.Company_has_Address   PAP.Company_has_Address
        addresses       query      PAP.Address               PAP.Company_has_Address
        affiliate       optional   PAP.Company_P
        created_by      computed   MOM.Id_Entity
        email_links     query      PAP.Company_has_Email     PAP.Company_has_Email
        emails          query      PAP.Email                 PAP.Company_has_Email
        events          query      EVT.Event                 EVT.Event
        last_changed_by computed   MOM.Id_Entity
        owner           primary    PAP.Biz_Man
        phone_links     query      PAP.Company_has_Phone     PAP.Company_has_Phone
        phones          query      PAP.Phone                 PAP.Company_has_Phone
        property_links  query      PAP.Subject_has_Property  PAP.Subject_has_Property
        url_links       query      PAP.Company_has_Url       PAP.Company_has_Url
        urls            query      PAP.Url                   PAP.Company_has_Url
    ...PAP.Association
        address_links   query      PAP.Association_has_Addre PAP.Association_has_Address
        addresses       query      PAP.Address               PAP.Association_has_Address
        created_by      computed   MOM.Id_Entity
        email_links     query      PAP.Association_has_Email PAP.Association_has_Email
        emails          query      PAP.Email                 PAP.Association_has_Email
        events          query      EVT.Event                 EVT.Event
        last_changed_by computed   MOM.Id_Entity
        phone_links     query      PAP.Association_has_Phone PAP.Association_has_Phone
        phones          query      PAP.Phone                 PAP.Association_has_Phone
        property_links  query      PAP.Subject_has_Property  PAP.Subject_has_Property
        url_links       query      PAP.Association_has_Url   PAP.Association_has_Url
        urls            query      PAP.Url                   PAP.Association_has_Url
    .PAP.Person
        account_links   query      PAP.Person_has_Account    PAP.Person_has_Account
        accounts        query      Auth.Account              PAP.Person_has_Account
        address_links   query      PAP.Person_has_Address    PAP.Person_has_Address
        addresses       query      PAP.Address               PAP.Person_has_Address
        biz_man         query      PAP.Biz_Man               PAP.Biz_Man
        created_by      computed   MOM.Id_Entity
        email_links     query      PAP.Person_has_Email      PAP.Person_has_Email
        emails          query      PAP.Email                 PAP.Person_has_Email
        events          query      EVT.Event                 EVT.Event
        last_changed_by computed   MOM.Id_Entity
        phone_links     query      PAP.Person_has_Phone      PAP.Person_has_Phone
        phones          query      PAP.Phone                 PAP.Person_has_Phone
        property_links  query      PAP.Subject_has_Property  PAP.Subject_has_Property
        sailors         query      SRM.Sailor                SRM.Sailor
        url_links       query      PAP.Person_has_Url        PAP.Person_has_Url
        urls            query      PAP.Url                   PAP.Person_has_Url

    >>> seen = set ()
    >>> show_T_attrs (MOM.Id_Entity, "%%s%%-35s %%-10s %%-25.25s %%s", set (), sk)
    MOM.Id_Entity
        created_by                          computed   MOM.Id_Entity
        events                              query      EVT.Event                 EVT.Event
        last_changed_by                     computed   MOM.Id_Entity
    .MOM.Link
    ..MOM.Link1
    ...Auth.Link1
    ....Auth._Account_Action_
        left                                primary    Auth.Account              Auth._Account_Action_
    .....Auth._Account_Token_Action_
    ...EVT.Link1
    ....EVT._Recurrence_Mixin_
    .....EVT.Recurrence_Spec
        left                                primary    EVT.Event                 EVT.Recurrence_Spec
        rules                               query      EVT.Recurrence_Rule       EVT.Recurrence_Rule
    .....EVT.Recurrence_Rule
        left                                primary    EVT.Recurrence_Spec       EVT.Recurrence_Rule
    ....EVT.Event
        calendar                            primary    EVT.Calendar
        left                                primary    MOM.Id_Entity             EVT.Event
        occurs                              query      EVT.Event_occurs          EVT.Event_occurs
        recurrence                          query      EVT.Recurrence_Spec       EVT.Recurrence_Spec
    ....EVT.Event_occurs
        essence                             query      MOM.Id_Entity
    ...PAP.Link1
    ....PAP.Address_Position
        left                                primary    PAP.Address               PAP.Address_Position
    ....PAP.Biz_Man
        left                                primary    PAP.Person                PAP.Biz_Man
        owns                                query      PAP.Company_P             PAP.Company_P
    ...SRM.Link1
    ....SRM.Regatta
        boat_class                          primary    SRM._Boat_Class_
        boats                               query      SRM.Boat_in_Regatta       SRM.Boat_in_Regatta
        left                                primary    SRM.Regatta_Event         SRM.Regatta
    .....SRM.Regatta_C
        boat_class                          primary    SRM.Boat_Class
        teams                               query      SRM.Team                  SRM.Team
    .....SRM.Regatta_H
        boat_class                          primary    SRM.Handicap
    ....SRM.Boat
        left                                primary    SRM.Boat_Class            SRM.Boat
        regatta_links                       query      SRM.Boat_in_Regatta       SRM.Boat_in_Regatta
    ....SRM.Sailor
        boat_in_regatta_links               query      SRM.Crew_Member           SRM.Crew_Member
        club                                primary    SRM.Club
    ....SRM.Race_Result
        left                                primary    SRM.Boat_in_Regatta       SRM.Race_Result
    ....SRM.Team
        boat_links                          query      SRM.Team_has_Boat_in_Rega SRM.Team_has_Boat_in_Regatta
        leader                              optional   PAP.Person
        left                                primary    SRM.Regatta_C             SRM.Team
    ...SWP.Link1
    ....SWP.Clip_O
        left                                primary    SWP.Object_PN             SWP.Clip_O
    ....SWP.Picture
        left                                primary    SWP.Gallery               SWP.Picture
    ..MOM._Link_n_
    ...MOM.Link2
    ....Auth.Link2
    .....Auth.Account_in_Group
        right                               primary    Auth.Group                Auth.Account_in_Group
    ....PAP.Link2
    .....PAP.Subject_has_Property
        left                                primary    PAP.Subject               PAP.Subject_has_Property
        right                               primary    PAP.Property              PAP.Subject_has_Property
    ......PAP.Subject_has_Address
        right                               primary    PAP.Address               PAP.Subject_has_Address
    .......PAP.Company_has_Address
        left                                primary    PAP.Company               PAP.Company_has_Address
    .......PAP.Association_has_Address
        left                                primary    PAP.Association           PAP.Association_has_Address
    ......PAP.Subject_has_Email
        right                               primary    PAP.Email                 PAP.Subject_has_Email
    ......PAP.Subject_has_Phone
        right                               primary    PAP.Phone                 PAP.Subject_has_Phone
    ......PAP.Subject_has_Url
        right                               primary    PAP.Url                   PAP.Subject_has_Url
    .....PAP.Person_has_Account
        right                               primary    Auth.Account              PAP.Person_has_Account
    ....SRM.Link2
    .....SRM.Boat_in_Regatta
        _crew                               query      SRM.Sailor                SRM.Crew_Member
        crew                                computed   SRM.Sailor
        left                                primary    SRM.Boat                  SRM.Boat_in_Regatta
        race_results                        query      SRM.Race_Result           SRM.Race_Result
        right                               primary    SRM.Regatta               SRM.Boat_in_Regatta
        sailor_links                        query      SRM.Crew_Member           SRM.Crew_Member
        skipper                             required   SRM.Sailor
        team_links                          query      SRM.Team_has_Boat_in_Rega SRM.Team_has_Boat_in_Regatta
    .....SRM.Crew_Member
        right                               primary    SRM.Sailor                SRM.Crew_Member
    .....SRM.Team_has_Boat_in_Regatta
        left                                primary    SRM.Team                  SRM.Team_has_Boat_in_Regatta
        right                               primary    SRM.Boat_in_Regatta       SRM.Team_has_Boat_in_Regatta
    ...Auth._Link_n_
    ...PAP._Link_n_
    ...SRM._Link_n_
    ..Auth.Link
    ..EVT.Link
    ..PAP.Link
    ..SRM.Link
    ..SWP.Link
    .MOM.Object
    ..Auth.Object
    ...Auth._Account_
    ....Auth.Account
        _account_action_s                   query      Auth._Account_Action_     Auth._Account_Action_
        _account_token_action_s             query      Auth._Account_Token_Actio Auth._Account_Token_Action_
        account_email_verifications         query      Auth.Account_EMail_Verifi Auth.Account_EMail_Verification
        account_password_resets             query      Auth.Account_Password_Res Auth.Account_Password_Reset
        activation                          query      Auth.Account_Activation   Auth.Account_Activation
        activations                         query      Auth.Account_Activation   Auth.Account_Activation
        group_links                         query      Auth.Account_in_Group     Auth.Account_in_Group
        groups                              query      Auth.Group                Auth.Account_in_Group
        password_change_required            query      Auth.Account_Password_Cha Auth.Account_Password_Change_Required
        password_change_requireds           query      Auth.Account_Password_Cha Auth.Account_Password_Change_Required
        person                              query      PAP.Person                PAP.Person_has_Account
        person_link                         query      PAP.Person_has_Account    PAP.Person_has_Account
        person_links                        query      PAP.Person_has_Account    PAP.Person_has_Account
    ...Auth.Group
        account_links                       query      Auth.Account_in_Group     Auth.Account_in_Group
        accounts                            query      Auth.Account              Auth.Account_in_Group
    ..EVT.Object
    ..PAP.Object
    ...PAP.Property
        subject_links                       query      PAP.Subject_has_Property  PAP.Subject_has_Property
    ....PAP.Address
        association_links                   query      PAP.Association_has_Addre PAP.Association_has_Address
        associations                        query      PAP.Association           PAP.Association_has_Address
        companies                           query      PAP.Company               PAP.Company_has_Address
        company_links                       query      PAP.Company_has_Address   PAP.Company_has_Address
        gps                                 query      PAP.Address_Position      PAP.Address_Position
        person_links                        query      PAP.Person_has_Address    PAP.Person_has_Address
        persons                             query      PAP.Person                PAP.Person_has_Address
        subject_links                       query      PAP.Subject_has_Address   PAP.Subject_has_Address
    ....PAP.Email
        association_links                   query      PAP.Association_has_Email PAP.Association_has_Email
        company_links                       query      PAP.Company_has_Email     PAP.Company_has_Email
        person_links                        query      PAP.Person_has_Email      PAP.Person_has_Email
        subject_links                       query      PAP.Subject_has_Email     PAP.Subject_has_Email
    ....PAP.Phone
        association_links                   query      PAP.Association_has_Phone PAP.Association_has_Phone
        company_links                       query      PAP.Company_has_Phone     PAP.Company_has_Phone
        person_links                        query      PAP.Person_has_Phone      PAP.Person_has_Phone
        subject_links                       query      PAP.Subject_has_Phone     PAP.Subject_has_Phone
    ....PAP.Url
        association_links                   query      PAP.Association_has_Url   PAP.Association_has_Url
        company_links                       query      PAP.Company_has_Url       PAP.Company_has_Url
        person_links                        query      PAP.Person_has_Url        PAP.Person_has_Url
        subject_links                       query      PAP.Subject_has_Url       PAP.Subject_has_Url
    ...PAP.Subject
        address_links                       query      PAP.Subject_has_Address   PAP.Subject_has_Address
        addresses                           query      PAP.Address               PAP.Subject_has_Address
        email_links                         query      PAP.Subject_has_Email     PAP.Subject_has_Email
        emails                              query      PAP.Email                 PAP.Subject_has_Email
        phone_links                         query      PAP.Subject_has_Phone     PAP.Subject_has_Phone
        phones                              query      PAP.Phone                 PAP.Subject_has_Phone
        property_links                      query      PAP.Subject_has_Property  PAP.Subject_has_Property
        url_links                           query      PAP.Subject_has_Url       PAP.Subject_has_Url
        urls                                query      PAP.Url                   PAP.Subject_has_Url
    ....PAP.Group
    .....PAP.Legal_Entity
    ......PAP.Company
        address_links                       query      PAP.Company_has_Address   PAP.Company_has_Address
        email_links                         query      PAP.Company_has_Email     PAP.Company_has_Email
        phone_links                         query      PAP.Company_has_Phone     PAP.Company_has_Phone
        url_links                           query      PAP.Company_has_Url       PAP.Company_has_Url
    .......PAP.Company_P
        affiliate                           optional   PAP.Company_P
        owner                               primary    PAP.Biz_Man
    ......PAP.Association
        address_links                       query      PAP.Association_has_Addre PAP.Association_has_Address
        email_links                         query      PAP.Association_has_Email PAP.Association_has_Email
        phone_links                         query      PAP.Association_has_Phone PAP.Association_has_Phone
        url_links                           query      PAP.Association_has_Url   PAP.Association_has_Url
    ....PAP.Person
        account_links                       query      PAP.Person_has_Account    PAP.Person_has_Account
        address_links                       query      PAP.Person_has_Address    PAP.Person_has_Address
        biz_man                             query      PAP.Biz_Man               PAP.Biz_Man
        email_links                         query      PAP.Person_has_Email      PAP.Person_has_Email
        phone_links                         query      PAP.Person_has_Phone      PAP.Person_has_Phone
        sailors                             query      SRM.Sailor                SRM.Sailor
        url_links                           query      PAP.Person_has_Url        PAP.Person_has_Url
    ..SRM.Object
    ...SRM._Boat_Class_
    ....SRM.Boat_Class
        boats                               query      SRM.Boat                  SRM.Boat
    ...SRM.Regatta_Event
        regattas                            query      SRM.Regatta               SRM.Regatta
    ...SRM.Page
        clips                               query      SWP.Clip_O                SWP.Clip_O
        event                               primary    SRM.Regatta_Event
    ..SWP.Object
    ...SWP.Object_PN
    ....SWP.Page
    ....SWP.Gallery
        pictures                            query      SWP.Picture               SWP.Picture
    .Auth.Id_Entity
    .EVT.Id_Entity
    .PAP.Id_Entity
    .SRM.Id_Entity
    .SWP.Id_Entity

    >>> for T, l in sorted (children_trans_iter (MOM.Id_Entity), key = TFL.Getter [0].type_name):
    ...     if T.link_ref_attr and not T.is_partial :
    ...         print (T.type_name)
    ...         for a in T.link_ref_attr :
    ...             if a.Ref_Type.show_in_ui :
    ...                  print (" " * 3, a.name)
    Auth.Account
        group_links
        events
        person_links
    Auth.Account_Activation
        events
    Auth.Account_EMail_Verification
        events
    Auth.Account_Password_Change_Required
        events
    Auth.Account_Password_Reset
        events
    Auth.Account_in_Group
        events
    Auth.Certificate
        events
    Auth.Group
        account_links
        events
    EVT.Calendar
        events
    EVT.Event
        events
        occurs
    EVT.Event_occurs
        events
    EVT.Recurrence_Rule
        events
    EVT.Recurrence_Spec
        events
        rules
    PAP.Address
        events
        subject_links
        company_links
        person_links
        association_links
    PAP.Address_Position
        events
    PAP.Association
        events
        property_links
        url_links
        phone_links
        email_links
        address_links
    PAP.Association_has_Address
        events
    PAP.Association_has_Email
        events
    PAP.Association_has_Phone
        events
    PAP.Association_has_Url
        events
    PAP.Biz_Man
        events
    PAP.Company
        events
        property_links
        url_links
        phone_links
        email_links
        address_links
    PAP.Company_P
        events
        property_links
        url_links
        phone_links
        email_links
        address_links
    PAP.Company_has_Address
        events
    PAP.Company_has_Email
        events
    PAP.Company_has_Phone
        events
    PAP.Company_has_Url
        events
    PAP.Email
        events
        subject_links
        company_links
        person_links
        association_links
    PAP.Person
        events
        property_links
        account_links
        sailors
        url_links
        phone_links
        email_links
        address_links
    PAP.Person_has_Account
        events
    PAP.Person_has_Address
        events
    PAP.Person_has_Email
        events
    PAP.Person_has_Phone
        events
    PAP.Person_has_Url
        events
    PAP.Phone
        events
        subject_links
        company_links
        person_links
        association_links
    PAP.Url
        events
        subject_links
        company_links
        person_links
        association_links
    SRM.Boat
        events
        regatta_links
    SRM.Boat_Class
        events
        boats
    SRM.Boat_in_Regatta
        events
        race_results
        sailor_links
        team_links
    SRM.Club
        events
    SRM.Crew_Member
        events
    SRM.Handicap
        events
    SRM.Page
        events
        clips
    SRM.Race_Result
        events
    SRM.Regatta_C
        events
        boats
        teams
    SRM.Regatta_Event
        events
        regattas
    SRM.Regatta_H
        events
        boats
    SRM.Sailor
        events
        boat_in_regatta_links
    SRM.Team
        events
        boat_links
    SRM.Team_has_Boat_in_Regatta
        events
    SWP.Clip_O
        events
    SWP.Clip_X
        events
        clips
    SWP.Gallery
        events
        clips
        pictures
    SWP.Page
        events
        clips
    SWP.Page_Y
        events
        clips
    SWP.Picture
        events
    SWP.Referral
        events
        clips

    >>> for T, l in sorted (children_trans_iter (MOM.Id_Entity), key = TFL.Getter [0].type_name):
    ...     if T.rev_ref_attr and not T.is_partial :
    ...         print (T.type_name)
    ...         for a in T.rev_ref_attr :
    ...             if a.Ref_Type.show_in_ui :
    ...                  print (" " * 3, a.name)
    Auth.Account
        creation
        last_change
        group_links
        groups
        events
        person
        person_links
        person_link
    Auth.Account_Activation
        creation
        last_change
        events
    Auth.Account_EMail_Verification
        creation
        last_change
        events
    Auth.Account_Password_Change_Required
        creation
        last_change
        events
    Auth.Account_Password_Reset
        creation
        last_change
        events
    Auth.Account_in_Group
        creation
        last_change
        events
    Auth.Certificate
        creation
        last_change
        events
    Auth.Group
        creation
        last_change
        accounts
        account_links
        events
    EVT.Calendar
        creation
        last_change
        events
    EVT.Event
        creation
        last_change
        events
        occurs
        recurrence
    EVT.Event_occurs
        creation
        last_change
        events
    EVT.Recurrence_Rule
        creation
        last_change
        events
    EVT.Recurrence_Spec
        creation
        last_change
        events
        rules
    PAP.Address
        creation
        last_change
        events
        gps
        subject_links
        companies
        company_links
        persons
        person_links
        associations
        association_links
    PAP.Address_Position
        creation
        last_change
        events
    PAP.Association
        creation
        last_change
        events
        property_links
        url_links
        urls
        phone_links
        phones
        email_links
        emails
        address_links
        addresses
    PAP.Association_has_Address
        creation
        last_change
        events
    PAP.Association_has_Email
        creation
        last_change
        events
    PAP.Association_has_Phone
        creation
        last_change
        events
    PAP.Association_has_Url
        creation
        last_change
        events
    PAP.Biz_Man
        creation
        last_change
        events
        owns
    PAP.Company
        creation
        last_change
        events
        property_links
        url_links
        urls
        phone_links
        phones
        email_links
        emails
        address_links
        addresses
    PAP.Company_P
        creation
        last_change
        events
        property_links
        url_links
        urls
        phone_links
        phones
        email_links
        emails
        address_links
        addresses
    PAP.Company_has_Address
        creation
        last_change
        events
    PAP.Company_has_Email
        creation
        last_change
        events
    PAP.Company_has_Phone
        creation
        last_change
        events
    PAP.Company_has_Url
        creation
        last_change
        events
    PAP.Email
        creation
        last_change
        events
        subject_links
        companies
        company_links
        persons
        person_links
        associations
        association_links
    PAP.Person
        creation
        last_change
        events
        property_links
        account_links
        accounts
        sailors
        biz_man
        url_links
        urls
        phone_links
        phones
        email_links
        emails
        address_links
        addresses
    PAP.Person_has_Account
        creation
        last_change
        events
    PAP.Person_has_Address
        creation
        last_change
        events
    PAP.Person_has_Email
        creation
        last_change
        events
    PAP.Person_has_Phone
        creation
        last_change
        events
    PAP.Person_has_Url
        creation
        last_change
        events
    PAP.Phone
        creation
        last_change
        events
        subject_links
        companies
        company_links
        persons
        person_links
        associations
        association_links
    PAP.Url
        creation
        last_change
        events
        subject_links
        companies
        company_links
        persons
        person_links
        associations
        association_links
    SRM.Boat
        creation
        last_change
        events
        regatta_links
    SRM.Boat_Class
        creation
        last_change
        events
        boats
    SRM.Boat_in_Regatta
        creation
        last_change
        events
        race_results
        sailor_links
        _crew
        teams
        team_links
    SRM.Club
        creation
        last_change
        events
    SRM.Crew_Member
        creation
        last_change
        events
    SRM.Handicap
        creation
        last_change
        events
    SRM.Page
        creation
        last_change
        events
        clips
    SRM.Race_Result
        creation
        last_change
        events
    SRM.Regatta_C
        creation
        last_change
        events
        boats
        teams
    SRM.Regatta_Event
        creation
        last_change
        events
        regattas
    SRM.Regatta_H
        creation
        last_change
        events
        boats
    SRM.Sailor
        creation
        last_change
        events
        boat_in_regatta_links
    SRM.Team
        creation
        last_change
        events
        boat_links
        boats
    SRM.Team_has_Boat_in_Regatta
        creation
        last_change
        events
    SWP.Clip_O
        creation
        last_change
        events
    SWP.Clip_X
        creation
        last_change
        events
        clips
    SWP.Gallery
        creation
        last_change
        events
        clips
        pictures
    SWP.Page
        creation
        last_change
        events
        clips
    SWP.Page_Y
        creation
        last_change
        events
        clips
    SWP.Picture
        creation
        last_change
        events
    SWP.Referral
        creation
        last_change
        events
        clips

    >>> for T, l in sorted (children_trans_iter (MOM.Id_Entity), key = TFL.Getter [0].type_name):
    ...     print ("%%-40s %%s" %% (T.type_name, T.show_in_ui))
    Auth.Account                             True
    Auth.Account_Activation                  False
    Auth.Account_EMail_Verification          False
    Auth.Account_Password_Change_Required    False
    Auth.Account_Password_Reset              False
    Auth.Account_in_Group                    True
    Auth.Certificate                         True
    Auth.Group                               True
    Auth.Id_Entity                           True
    Auth.Link                                True
    Auth.Link1                               True
    Auth.Link2                               True
    Auth.Object                              True
    Auth._Account_                           True
    Auth._Account_Action_                    False
    Auth._Account_Token_Action_              False
    Auth._Link_n_                            True
    EVT.Calendar                             True
    EVT.Event                                True
    EVT.Event_occurs                         True
    EVT.Id_Entity                            True
    EVT.Link                                 True
    EVT.Link1                                True
    EVT.Object                               True
    EVT.Recurrence_Rule                      True
    EVT.Recurrence_Spec                      True
    EVT._Recurrence_Mixin_                   True
    MOM.Id_Entity                            True
    MOM.Link                                 True
    MOM.Link1                                True
    MOM.Link2                                True
    MOM.Link3                                False
    MOM.Object                               True
    MOM._Link_n_                             True
    PAP.Address                              True
    PAP.Address_Position                     True
    PAP.Association                          True
    PAP.Association_has_Address              True
    PAP.Association_has_Email                True
    PAP.Association_has_Phone                True
    PAP.Association_has_Url                  True
    PAP.Biz_Man                              True
    PAP.Company                              True
    PAP.Company_P                            True
    PAP.Company_has_Address                  True
    PAP.Company_has_Email                    True
    PAP.Company_has_Phone                    True
    PAP.Company_has_Url                      True
    PAP.Email                                True
    PAP.Group                                True
    PAP.Id_Entity                            True
    PAP.Legal_Entity                         True
    PAP.Link                                 True
    PAP.Link1                                True
    PAP.Link2                                True
    PAP.Object                               True
    PAP.Person                               True
    PAP.Person_has_Account                   True
    PAP.Person_has_Address                   True
    PAP.Person_has_Email                     True
    PAP.Person_has_Phone                     True
    PAP.Person_has_Url                       True
    PAP.Phone                                True
    PAP.Property                             True
    PAP.Subject                              True
    PAP.Subject_has_Address                  True
    PAP.Subject_has_Email                    True
    PAP.Subject_has_Phone                    True
    PAP.Subject_has_Property                 True
    PAP.Subject_has_Url                      True
    PAP.Url                                  True
    PAP._Link_n_                             True
    SRM.Boat                                 True
    SRM.Boat_Class                           True
    SRM.Boat_in_Regatta                      True
    SRM.Club                                 True
    SRM.Crew_Member                          True
    SRM.Handicap                             True
    SRM.Id_Entity                            True
    SRM.Link                                 True
    SRM.Link1                                True
    SRM.Link2                                True
    SRM.Object                               True
    SRM.Page                                 True
    SRM.Race_Result                          True
    SRM.Regatta                              True
    SRM.Regatta_C                            True
    SRM.Regatta_Event                        True
    SRM.Regatta_H                            True
    SRM.Sailor                               True
    SRM.Team                                 True
    SRM.Team_has_Boat_in_Regatta             True
    SRM._Boat_Class_                         True
    SRM._Link_n_                             True
    SWP.Clip_O                               True
    SWP.Clip_X                               True
    SWP.Gallery                              True
    SWP.Id_Entity                            True
    SWP.Link                                 True
    SWP.Link1                                True
    SWP.Object                               True
    SWP.Object_PN                            True
    SWP.Page                                 True
    SWP.Page_Y                               True
    SWP.Picture                              True
    SWP.Referral                             True

"""

_test_saw = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> PAP = scope.PAP

    >>> print (PAP.Biz_Man.query ())
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_biz_man."left" AS pap_biz_man_left,
           pap_biz_man.pid AS pap_biz_man_pid
         FROM mom_id_entity
           JOIN pap_biz_man ON mom_id_entity.pid = pap_biz_man.pid


    >>> print (PAP.Subject._SAW.sa_joins_strict)
    mom_id_entity

    >>> print (PAP.Subject._SAW.sa_joins)
    mom_id_entity
      LEFT OUTER JOIN pap_company ON mom_id_entity.pid = pap_company.pid
      LEFT OUTER JOIN pap_company_p ON pap_company.pid = pap_company_p.pid
      LEFT OUTER JOIN pap_person ON mom_id_entity.pid = pap_person.pid
      LEFT OUTER JOIN pap_association ON mom_id_entity.pid = pap_association.pid

    >>> print (PAP.Subject.query ())
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_association.__raw_name AS pap_association___raw_name,
           pap_association.__raw_short_name AS pap_association___raw_short_name,
           pap_association.lifetime__finish AS pap_association_lifetime__finish,
           pap_association.lifetime__start AS pap_association_lifetime__start,
           pap_association.name AS pap_association_name,
           pap_association.pid AS pap_association_pid,
           pap_association.short_name AS pap_association_short_name,
           pap_company.__raw_name AS pap_company___raw_name,
           pap_company.__raw_registered_in AS pap_company___raw_registered_in,
           pap_company.__raw_short_name AS pap_company___raw_short_name,
           pap_company.lifetime__finish AS pap_company_lifetime__finish,
           pap_company.lifetime__start AS pap_company_lifetime__start,
           pap_company.name AS pap_company_name,
           pap_company.pid AS pap_company_pid,
           pap_company.registered_in AS pap_company_registered_in,
           pap_company.short_name AS pap_company_short_name,
           pap_company_p.affiliate AS pap_company_p_affiliate,
           pap_company_p.owner AS pap_company_p_owner,
           pap_company_p.pid AS pap_company_p_pid,
           pap_person.__raw_first_name AS pap_person___raw_first_name,
           pap_person.__raw_last_name AS pap_person___raw_last_name,
           pap_person.__raw_middle_name AS pap_person___raw_middle_name,
           pap_person.__raw_title AS pap_person___raw_title,
           pap_person.first_name AS pap_person_first_name,
           pap_person.last_name AS pap_person_last_name,
           pap_person.lifetime__finish AS pap_person_lifetime__finish,
           pap_person.lifetime__start AS pap_person_lifetime__start,
           pap_person.middle_name AS pap_person_middle_name,
           pap_person.pid AS pap_person_pid,
           pap_person.sex AS pap_person_sex,
           pap_person.title AS pap_person_title
         FROM mom_id_entity
           LEFT OUTER JOIN pap_company ON mom_id_entity.pid = pap_company.pid
           LEFT OUTER JOIN pap_company_p ON pap_company.pid = pap_company_p.pid
           LEFT OUTER JOIN pap_person ON mom_id_entity.pid = pap_person.pid
           LEFT OUTER JOIN pap_association ON mom_id_entity.pid = pap_association.pid
         WHERE mom_id_entity.pid = pap_company.pid
            OR mom_id_entity.pid = pap_company_p.pid
            OR mom_id_entity.pid = pap_person.pid
            OR mom_id_entity.pid = pap_association.pid

    >>> p1 = PAP.Person ("Doe", "Jane", lifetime = ("20010101", ), raw = True)
    >>> bm = PAP.Biz_Man (p1)
    >>> cp = PAP.Company_P ("Doe, Inc.", bm, raw = True)
    >>> ta = PAP.Association ("Towel Carriers Association", short_name = "TCA", raw = True)
    >>> cq = PAP.Company_P ("Jane's, Inc.", bm)


"""

from   _GTW.__test__.model      import *
from   _MOM.import_MOM          import Q
from   _MOM.Inspect             import children_trans_iter
from   _TFL.pyk                 import pyk

import _GTW._OMP._PAP.Association
import _GTW._RST._TOP._MOM.Query_Restriction

_Ancestor_Essence = GTW.OMP.PAP.Link1

class Biz_Man (_Ancestor_Essence) :
    """Russian in business"""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class left (_Ancestor.left) :
            """Network device the interface is connected to."""

            role_type           = GTW.OMP.PAP.Person
            role_name           = "man"
            max_links           = 1
            link_ref_singular   = True

        # end class left

    # end class _Attributes

# end class Biz_Man

_Ancestor_Essence = GTW.OMP.PAP.Company

class Company_P (_Ancestor_Essence) :
    """Company owned and operated by a single person"""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class owner (A_Id_Entity) :
            """Owner of the company"""

            kind               = Attr.Primary
            P_Type             = Biz_Man
            rev_ref_attr_name  = "owns"

        # end class owner

        class affiliate  (A_Id_Entity) :
            """Affiliate of the company"""

            kind               = Attr.Optional
            P_Type             = "GTW.OMP.PAP.Company_P"

        # end class affiliate

    # end class _Attributes

# end class Company_P

def T_attrs (T, seen = None) :
    if seen is None :
        seen = set ()
    Ref_Attr_Types = \
        ( MOM.Attr._A_Id_Entity_
        , MOM.Attr._A_Id_Entity_Collection_
        )
    def _gen () :
        for n, a in sorted (pyk.iteritems (T.attributes)) :
            attr = a.attr
            PT   = attr.P_Type
            if PT and isinstance (attr, Ref_Attr_Types) :
                key = (attr.name, PT.type_name)
                if key not in seen :
                    seen.add (key)
                    yield n, a, PT
    return sorted (_gen ())
# end def T_attrs

def show_T_attrs (Root, format, seen, sk, lead = ".") :
    for (T, l) in children_trans_iter (Root, sort_key = sk) :
        attrs = T_attrs (T, seen)
        if attrs or T.children :
            print ("%s%s" % (lead * l, T.type_name))
            for n, a, PT in attrs :
                RT = getattr (getattr (a, "Ref_Type", None), "type_name", "")
                if not RT :
                    RT = getattr (a, "assoc", "")
                    if not isinstance (RT, pyk.string_types) :
                        RT = getattr (RT, "type_name", "")
                if RT.startswith ("GTW.OMP.") :
                    RT = RT [len ("GTW.OMP."):]
                line = format % (" " * 4, a.name, a.kind, PT.type_name, RT)
                print (line.rstrip ())
# end def show_T_attrs

__test__ = Scaffold.create_test_dict \
    ( dict
        ( test_main        = _test_code
        , test_entity_attr = _test_entity_attr
        )
    )

__test__.update \
    ( Scaffold.create_test_dict \
        ( dict
            ( test_saw     = _test_saw
            )
        , ignore           = ("HPS", "MYS")
        )
    )

### __END__ GTW.__test__.Company
