# -*- coding: utf-8 -*-
# Copyright (C) 2011-2016 Mag. Christian Tanzer All rights reserved
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
#    GTW.__test__.Attr_Filter
#
# Purpose
#    Test cases for MOM.Attr.Filter
#
# Revision Dates
#    11-Nov-2011 (CT) Creation
#    12-Nov-2011 (CT) Creation continued
#    18-Nov-2011 (CT) Creation continued..
#     2-Dec-2011 (CT) Creation continued...
#    13-Dec-2011 (CT) Creation continued.... (`.Atoms`)
#    19-Mar-2012 (CT) Adapt to reification of `SRM.Handicap`
#    14-May-2012 (CT) Add test showing `P_Type` of `scope.attribute_types`
#    31-Jul-2012 (CT) Add `Angle` to test output
#    11-Oct-2012 (CT) Change duplicate removal for `Sig_Key` test
#     6-Dec-2012 (CT) Remove `Entity_created_by_Person`
#    20-Jan-2013 (CT) Add `AIS`
#    26-Apr-2013 (CT) Remove `AIS`
#    29-Jul-2015 (CT) Adapt to name change of PAP.Phone attributes
#    ««revision-date»»···
#--

from   __future__  import print_function, unicode_literals

_test_code = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> PAP = scope.PAP

    >>> for aq in PAP.Person.E_Type.AQ.Attrs :
    ...     print (aq)
    <last_name.AQ [Attr.Type.Querier String_FL]>
    <first_name.AQ [Attr.Type.Querier String_FL]>
    <middle_name.AQ [Attr.Type.Querier String]>
    <title.AQ [Attr.Type.Querier String]>
    <lifetime.AQ [Attr.Type.Querier Composite]>
    <sex.AQ [Attr.Type.Querier Ckd]>
    <creation.AQ [Attr.Type.Querier Rev_Ref]>
    <last_change.AQ [Attr.Type.Querier Rev_Ref]>
    <last_cid.AQ [Attr.Type.Querier Ckd]>
    <pid.AQ [Attr.Type.Querier Ckd]>
    <type_name.AQ [Attr.Type.Querier String]>
    <events.AQ [Attr.Type.Querier Rev_Ref]>
    <accounts.AQ [Attr.Type.Querier Rev_Ref]>
    <sailors.AQ [Attr.Type.Querier Rev_Ref]>
    <urls.AQ [Attr.Type.Querier Rev_Ref]>
    <phones.AQ [Attr.Type.Querier Rev_Ref]>
    <emails.AQ [Attr.Type.Querier Rev_Ref]>
    <addresses.AQ [Attr.Type.Querier Rev_Ref]>

    >>> paq = MOM.Attr.Querier.E_Type (PAP.Person.E_Type, MOM.Attr.Selector.ui_attr)
    >>> for aq in paq.Attrs :
    ...     print (aq)
    <last_name.AQ [Attr.Type.Querier String_FL]>
    <first_name.AQ [Attr.Type.Querier String_FL]>
    <middle_name.AQ [Attr.Type.Querier String]>
    <title.AQ [Attr.Type.Querier String]>
    <lifetime.AQ [Attr.Type.Querier Composite]>
    <sex.AQ [Attr.Type.Querier Ckd]>
    <creation.AQ [Attr.Type.Querier Rev_Ref]>
    <last_change.AQ [Attr.Type.Querier Rev_Ref]>
    <last_cid.AQ [Attr.Type.Querier Ckd]>
    <pid.AQ [Attr.Type.Querier Ckd]>
    <type_name.AQ [Attr.Type.Querier String]>
    <events.AQ [Attr.Type.Querier Rev_Ref]>
    <accounts.AQ [Attr.Type.Querier Rev_Ref]>
    <sailors.AQ [Attr.Type.Querier Rev_Ref]>
    <urls.AQ [Attr.Type.Querier Rev_Ref]>
    <phones.AQ [Attr.Type.Querier Rev_Ref]>
    <emails.AQ [Attr.Type.Querier Rev_Ref]>
    <addresses.AQ [Attr.Type.Querier Rev_Ref]>

    >>> for aq in paq.Attrs_Transitive :
    ...     print (aq)
    <last_name.AQ [Attr.Type.Querier String_FL]>
    <first_name.AQ [Attr.Type.Querier String_FL]>
    <middle_name.AQ [Attr.Type.Querier String]>
    <title.AQ [Attr.Type.Querier String]>
    <lifetime.AQ [Attr.Type.Querier Composite]>
    <lifetime.start.AQ [Attr.Type.Querier Date]>
    <lifetime.start.day.AQ [Attr.Type.Querier Ckd]>
    <lifetime.start.month.AQ [Attr.Type.Querier Ckd]>
    <lifetime.start.year.AQ [Attr.Type.Querier Ckd]>
    <lifetime.finish.AQ [Attr.Type.Querier Date]>
    <lifetime.finish.day.AQ [Attr.Type.Querier Ckd]>
    <lifetime.finish.month.AQ [Attr.Type.Querier Ckd]>
    <lifetime.finish.year.AQ [Attr.Type.Querier Ckd]>
    <lifetime.alive.AQ [Attr.Type.Querier Boolean]>
    <sex.AQ [Attr.Type.Querier Ckd]>
    <creation.AQ [Attr.Type.Querier Rev_Ref]>
    <creation.c_time.AQ [Attr.Type.Querier Ckd]>
    <creation.c_user.AQ [Attr.Type.Querier Id_Entity]>
    <creation.kind.AQ [Attr.Type.Querier String]>
    <creation.time.AQ [Attr.Type.Querier Ckd]>
    <creation.user.AQ [Attr.Type.Querier Id_Entity]>
    <last_change.AQ [Attr.Type.Querier Rev_Ref]>
    <last_change.c_time.AQ [Attr.Type.Querier Ckd]>
    <last_change.c_user.AQ [Attr.Type.Querier Id_Entity]>
    <last_change.kind.AQ [Attr.Type.Querier String]>
    <last_change.time.AQ [Attr.Type.Querier Ckd]>
    <last_change.user.AQ [Attr.Type.Querier Id_Entity]>
    <last_cid.AQ [Attr.Type.Querier Ckd]>
    <pid.AQ [Attr.Type.Querier Ckd]>
    <type_name.AQ [Attr.Type.Querier String]>
    <events.AQ [Attr.Type.Querier Rev_Ref]>
    <events.date.AQ [Attr.Type.Querier Composite]>
    <events.date.start.AQ [Attr.Type.Querier Date]>
    <events.date.start.day.AQ [Attr.Type.Querier Ckd]>
    <events.date.start.month.AQ [Attr.Type.Querier Ckd]>
    <events.date.start.year.AQ [Attr.Type.Querier Ckd]>
    <events.date.finish.AQ [Attr.Type.Querier Date]>
    <events.date.finish.day.AQ [Attr.Type.Querier Ckd]>
    <events.date.finish.month.AQ [Attr.Type.Querier Ckd]>
    <events.date.finish.year.AQ [Attr.Type.Querier Ckd]>
    <events.date.alive.AQ [Attr.Type.Querier Boolean]>
    <events.time.AQ [Attr.Type.Querier Composite]>
    <events.time.start.AQ [Attr.Type.Querier Time]>
    <events.time.start.hour.AQ [Attr.Type.Querier Ckd]>
    <events.time.start.minute.AQ [Attr.Type.Querier Ckd]>
    <events.time.start.second.AQ [Attr.Type.Querier Ckd]>
    <events.time.finish.AQ [Attr.Type.Querier Time]>
    <events.time.finish.hour.AQ [Attr.Type.Querier Ckd]>
    <events.time.finish.minute.AQ [Attr.Type.Querier Ckd]>
    <events.time.finish.second.AQ [Attr.Type.Querier Ckd]>
    <events.calendar.AQ [Attr.Type.Querier Id_Entity]>
    <events.calendar.name.AQ [Attr.Type.Querier String]>
    <events.calendar.desc.AQ [Attr.Type.Querier String]>
    <events.detail.AQ [Attr.Type.Querier String]>
    <events.short_title.AQ [Attr.Type.Querier String]>
    <accounts.AQ [Attr.Type.Querier Rev_Ref]>
    <accounts.name.AQ [Attr.Type.Querier String]>
    <accounts.enabled.AQ [Attr.Type.Querier Boolean]>
    <accounts.superuser.AQ [Attr.Type.Querier Boolean]>
    <accounts.active.AQ [Attr.Type.Querier Boolean]>
    <accounts.suspended.AQ [Attr.Type.Querier Boolean]>
    <sailors.AQ [Attr.Type.Querier Rev_Ref]>
    <sailors.mna_number.AQ [Attr.Type.Querier Raw]>
    <sailors.nation.AQ [Attr.Type.Querier Ckd]>
    <sailors.club.AQ [Attr.Type.Querier Id_Entity]>
    <sailors.club.name.AQ [Attr.Type.Querier String]>
    <sailors.club.long_name.AQ [Attr.Type.Querier String]>
    <urls.AQ [Attr.Type.Querier Rev_Ref]>
    <urls.value.AQ [Attr.Type.Querier String]>
    <urls.desc.AQ [Attr.Type.Querier String]>
    <phones.AQ [Attr.Type.Querier Rev_Ref]>
    <phones.sn.AQ [Attr.Type.Querier String]>
    <phones.ndc.AQ [Attr.Type.Querier String]>
    <phones.cc.AQ [Attr.Type.Querier String]>
    <phones.desc.AQ [Attr.Type.Querier String]>
    <emails.AQ [Attr.Type.Querier Rev_Ref]>
    <emails.address.AQ [Attr.Type.Querier String]>
    <emails.desc.AQ [Attr.Type.Querier String]>
    <addresses.AQ [Attr.Type.Querier Rev_Ref]>
    <addresses.street.AQ [Attr.Type.Querier String]>
    <addresses.zip.AQ [Attr.Type.Querier String]>
    <addresses.city.AQ [Attr.Type.Querier String]>
    <addresses.country.AQ [Attr.Type.Querier String]>
    <addresses.desc.AQ [Attr.Type.Querier String]>
    <addresses.region.AQ [Attr.Type.Querier String]>

    >>> for aq in paq.Atoms :
    ...     print (aq)
    <last_name.AQ [Attr.Type.Querier String_FL]>
    <first_name.AQ [Attr.Type.Querier String_FL]>
    <middle_name.AQ [Attr.Type.Querier String]>
    <title.AQ [Attr.Type.Querier String]>
    <lifetime.start.AQ [Attr.Type.Querier Date]>
    <lifetime.finish.AQ [Attr.Type.Querier Date]>
    <lifetime.alive.AQ [Attr.Type.Querier Boolean]>
    <sex.AQ [Attr.Type.Querier Ckd]>
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
    <accounts.name.AQ [Attr.Type.Querier String]>
    <accounts.enabled.AQ [Attr.Type.Querier Boolean]>
    <accounts.superuser.AQ [Attr.Type.Querier Boolean]>
    <accounts.active.AQ [Attr.Type.Querier Boolean]>
    <accounts.suspended.AQ [Attr.Type.Querier Boolean]>
    <sailors.mna_number.AQ [Attr.Type.Querier Raw]>
    <sailors.nation.AQ [Attr.Type.Querier Ckd]>
    <sailors.club.name.AQ [Attr.Type.Querier String]>
    <sailors.club.long_name.AQ [Attr.Type.Querier String]>
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

    >>> for aq in PAP.Person_has_Phone.E_Type.AQ.Atoms :
    ...     print (aq)
    <left.last_name.AQ [Attr.Type.Querier String_FL]>
    <left.first_name.AQ [Attr.Type.Querier String_FL]>
    <left.middle_name.AQ [Attr.Type.Querier String]>
    <left.title.AQ [Attr.Type.Querier String]>
    <left.lifetime.start.AQ [Attr.Type.Querier Date]>
    <left.lifetime.finish.AQ [Attr.Type.Querier Date]>
    <left.lifetime.alive.AQ [Attr.Type.Querier Boolean]>
    <left.sex.AQ [Attr.Type.Querier Ckd]>
    <right.sn.AQ [Attr.Type.Querier String]>
    <right.ndc.AQ [Attr.Type.Querier String]>
    <right.cc.AQ [Attr.Type.Querier String]>
    <right.desc.AQ [Attr.Type.Querier String]>
    <extension.AQ [Attr.Type.Querier String]>
    <desc.AQ [Attr.Type.Querier String]>
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

    >>> for aq in PAP.Person_has_Phone.E_Type.AQ.left.Atoms :
    ...     print (aq)
    <left.last_name.AQ [Attr.Type.Querier String_FL]>
    <left.first_name.AQ [Attr.Type.Querier String_FL]>
    <left.middle_name.AQ [Attr.Type.Querier String]>
    <left.title.AQ [Attr.Type.Querier String]>
    <left.lifetime.start.AQ [Attr.Type.Querier Date]>
    <left.lifetime.finish.AQ [Attr.Type.Querier Date]>
    <left.lifetime.alive.AQ [Attr.Type.Querier Boolean]>
    <left.sex.AQ [Attr.Type.Querier Ckd]>

    >>> for aq in PAP.Person_has_Phone.E_Type.AQ.left.Unwrapped_Atoms :
    ...     print (aq)
    <last_name.AQ [Attr.Type.Querier String_FL]>
    <first_name.AQ [Attr.Type.Querier String_FL]>
    <middle_name.AQ [Attr.Type.Querier String]>
    <title.AQ [Attr.Type.Querier String]>
    <lifetime.start.AQ [Attr.Type.Querier Date]>
    <lifetime.finish.AQ [Attr.Type.Querier Date]>
    <sex.AQ [Attr.Type.Querier Ckd]>

    >>> ET_lifetime    = PAP.Person.E_Type.attributes ["lifetime"]
    >>> person_attrs   = MOM.Attr.Selector.ui_attr (PAP.Person.E_Type)
    >>> php_attrs      = MOM.Attr.Selector.ui_attr (PAP.Person_has_Phone.E_Type)
    >>> lifetime_attrs = MOM.Attr.Selector.ui_attr (ET_lifetime)

    >>> prepr (person_attrs.names)
    ('last_name', 'first_name', 'middle_name', 'title', 'lifetime', 'sex', 'creation', 'last_change', 'last_cid', 'pid', 'type_name', 'events', 'accounts', 'sailors', 'urls', 'phones', 'emails', 'addresses')
    >>> prepr (php_attrs.names)
    ('left', 'right', 'extension', 'desc', 'creation', 'last_change', 'last_cid', 'pid', 'type_name', 'events')
    >>> prepr (lifetime_attrs.names)
    ('start', 'finish', 'alive')

    >>> for attr in person_attrs :
    ...     print (attr.typ, attr.AQ)
    String <last_name.AQ [Attr.Type.Querier String_FL]>
    String <first_name.AQ [Attr.Type.Querier String_FL]>
    String <middle_name.AQ [Attr.Type.Querier String]>
    String <title.AQ [Attr.Type.Querier String]>
    Date_Interval <lifetime.AQ [Attr.Type.Querier Composite]>
    Sex <sex.AQ [Attr.Type.Querier Ckd]>
    Rev_Ref <creation.AQ [Attr.Type.Querier Rev_Ref]>
    Rev_Ref <last_change.AQ [Attr.Type.Querier Rev_Ref]>
    Int <last_cid.AQ [Attr.Type.Querier Ckd]>
    Surrogate <pid.AQ [Attr.Type.Querier Ckd]>
    String <type_name.AQ [Attr.Type.Querier String]>
    Link_Ref_List <events.AQ [Attr.Type.Querier Rev_Ref]>
    Role_Ref_Set <accounts.AQ [Attr.Type.Querier Rev_Ref]>
    Link_Ref_List <sailors.AQ [Attr.Type.Querier Rev_Ref]>
    Role_Ref_Set <urls.AQ [Attr.Type.Querier Rev_Ref]>
    Role_Ref_Set <phones.AQ [Attr.Type.Querier Rev_Ref]>
    Role_Ref_Set <emails.AQ [Attr.Type.Querier Rev_Ref]>
    Role_Ref_Set <addresses.AQ [Attr.Type.Querier Rev_Ref]>

    >>> for attr in person_attrs :
    ...     print (attr.typ, attr.AQ.AC)
    String <Attr.Auto_Complete_PN last_name.STARTSWITH [auto-complete]>
    String <Attr.Auto_Complete_PN first_name.STARTSWITH [auto-complete]>
    String <Attr.Auto_Complete_S middle_name.STARTSWITH [auto-complete]>
    String <Attr.Auto_Complete_S title.STARTSWITH [auto-complete]>
    Date_Interval <Attr.Composite_Auto_Complete lifetime.EQ [auto-complete]>
    Sex <Attr.Auto_Complete sex.EQ [auto-complete]>
    Rev_Ref <Attr.Id_Entity_Auto_Complete creation.EQ [auto-complete]>
    Rev_Ref <Attr.Id_Entity_Auto_Complete last_change.EQ [auto-complete]>
    Int <Attr.Auto_Complete last_cid.EQ [auto-complete]>
    Surrogate <Attr.Auto_Complete pid.EQ [auto-complete]>
    String <Attr.Auto_Complete_S type_name.STARTSWITH [auto-complete]>
    Link_Ref_List <Attr.Id_Entity_Auto_Complete events.EQ [auto-complete]>
    Role_Ref_Set <Attr.Id_Entity_Auto_Complete accounts.EQ [auto-complete]>
    Link_Ref_List <Attr.Id_Entity_Auto_Complete sailors.EQ [auto-complete]>
    Role_Ref_Set <Attr.Id_Entity_Auto_Complete urls.EQ [auto-complete]>
    Role_Ref_Set <Attr.Id_Entity_Auto_Complete phones.EQ [auto-complete]>
    Role_Ref_Set <Attr.Id_Entity_Auto_Complete emails.EQ [auto-complete]>
    Role_Ref_Set <Attr.Id_Entity_Auto_Complete addresses.EQ [auto-complete]>

    >>> for attr in person_attrs :
    ...     print (attr.typ, getattr (attr.AQ, "GE", "** GE undefined **"))
    String <Attr.Greater_Equal last_name.GE [>=]>
    String <Attr.Greater_Equal first_name.GE [>=]>
    String <Attr.Greater_Equal middle_name.GE [>=]>
    String <Attr.Greater_Equal title.GE [>=]>
    Date_Interval <Attr.Composite_Greater_Equal lifetime.GE [>=]>
    Sex <Attr.Greater_Equal sex.GE [>=]>
    Rev_Ref <Attr.Id_Entity_Greater_Equal creation.GE [>=]>
    Rev_Ref <Attr.Id_Entity_Greater_Equal last_change.GE [>=]>
    Int <Attr.Greater_Equal last_cid.GE [>=]>
    Surrogate <Attr.Greater_Equal pid.GE [>=]>
    String <Attr.Greater_Equal type_name.GE [>=]>
    Link_Ref_List <Attr.Id_Entity_Greater_Equal events.GE [>=]>
    Role_Ref_Set <Attr.Id_Entity_Greater_Equal accounts.GE [>=]>
    Link_Ref_List <Attr.Id_Entity_Greater_Equal sailors.GE [>=]>
    Role_Ref_Set <Attr.Id_Entity_Greater_Equal urls.GE [>=]>
    Role_Ref_Set <Attr.Id_Entity_Greater_Equal phones.GE [>=]>
    Role_Ref_Set <Attr.Id_Entity_Greater_Equal emails.GE [>=]>
    Role_Ref_Set <Attr.Id_Entity_Greater_Equal addresses.GE [>=]>

    >>> for attr in person_attrs :
    ...     print (attr.typ, getattr (attr.AQ, "CONTAINS", "** CONTAINS undefined **"))
    String <Attr.Contains last_name.CONTAINS [contains]>
    String <Attr.Contains first_name.CONTAINS [contains]>
    String <Attr.Contains middle_name.CONTAINS [contains]>
    String <Attr.Contains title.CONTAINS [contains]>
    Date_Interval ** CONTAINS undefined **
    Sex ** CONTAINS undefined **
    Rev_Ref ** CONTAINS undefined **
    Rev_Ref ** CONTAINS undefined **
    Int ** CONTAINS undefined **
    Surrogate ** CONTAINS undefined **
    String <Attr.Contains type_name.CONTAINS [contains]>
    Link_Ref_List ** CONTAINS undefined **
    Role_Ref_Set ** CONTAINS undefined **
    Link_Ref_List ** CONTAINS undefined **
    Role_Ref_Set ** CONTAINS undefined **
    Role_Ref_Set ** CONTAINS undefined **
    Role_Ref_Set ** CONTAINS undefined **
    Role_Ref_Set ** CONTAINS undefined **

    >>> for attr in lifetime_attrs :
    ...     print (attr.typ, attr.AQ)
    Date <start.AQ [Attr.Type.Querier Date]>
    Date <finish.AQ [Attr.Type.Querier Date]>
    Boolean <alive.AQ [Attr.Type.Querier Boolean]>

    >>> for attr in lifetime_attrs :
    ...     print (attr.typ, getattr (PAP.Person.E_Type.AQ.lifetime, attr.name))
    Date <lifetime.start.AQ [Attr.Type.Querier Date]>
    Date <lifetime.finish.AQ [Attr.Type.Querier Date]>
    Boolean <lifetime.alive.AQ [Attr.Type.Querier Boolean]>

    >>> for attr in lifetime_attrs :
    ...     print (attr, getattr (ET_lifetime.AQ, attr.name))
    Date `start` <lifetime.start.AQ [Attr.Type.Querier Date]>
    Date `finish` <lifetime.finish.AQ [Attr.Type.Querier Date]>
    Boolean `alive` <lifetime.alive.AQ [Attr.Type.Querier Boolean]>

    >>> for attr in person_attrs :
    ...     print (attr.typ, attr.AQ.__class__)
    String <Attr.Type.Querier String_FL ('CONTAINS', 'ENDSWITH', 'EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE', 'STARTSWITH')>
    String <Attr.Type.Querier String_FL ('CONTAINS', 'ENDSWITH', 'EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE', 'STARTSWITH')>
    String <Attr.Type.Querier String ('CONTAINS', 'ENDSWITH', 'EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE', 'STARTSWITH')>
    String <Attr.Type.Querier String ('CONTAINS', 'ENDSWITH', 'EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE', 'STARTSWITH')>
    Date_Interval <Attr.Type.Querier Composite ()>
    Sex <Attr.Type.Querier Ckd ('EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE')>
    Rev_Ref <Attr.Type.Querier Rev_Ref ('EQ', 'IN', 'NE')>
    Rev_Ref <Attr.Type.Querier Rev_Ref ('EQ', 'IN', 'NE')>
    Int <Attr.Type.Querier Ckd ('EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE')>
    Surrogate <Attr.Type.Querier Ckd ('EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE')>
    String <Attr.Type.Querier String ('CONTAINS', 'ENDSWITH', 'EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE', 'STARTSWITH')>
    Link_Ref_List <Attr.Type.Querier Rev_Ref ('EQ', 'IN', 'NE')>
    Role_Ref_Set <Attr.Type.Querier Rev_Ref ('EQ', 'IN', 'NE')>
    Link_Ref_List <Attr.Type.Querier Rev_Ref ('EQ', 'IN', 'NE')>
    Role_Ref_Set <Attr.Type.Querier Rev_Ref ('EQ', 'IN', 'NE')>
    Role_Ref_Set <Attr.Type.Querier Rev_Ref ('EQ', 'IN', 'NE')>
    Role_Ref_Set <Attr.Type.Querier Rev_Ref ('EQ', 'IN', 'NE')>
    Role_Ref_Set <Attr.Type.Querier Rev_Ref ('EQ', 'IN', 'NE')>

    >>> for attr in php_attrs :
    ...     print (attr.typ, attr.AQ.__class__)
    Person <Attr.Type.Querier Id_Entity ('EQ', 'IN', 'NE')>
    Phone <Attr.Type.Querier Id_Entity ('EQ', 'IN', 'NE')>
    Numeric_String <Attr.Type.Querier String ('CONTAINS', 'ENDSWITH', 'EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE', 'STARTSWITH')>
    String <Attr.Type.Querier String ('CONTAINS', 'ENDSWITH', 'EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE', 'STARTSWITH')>
    Rev_Ref <Attr.Type.Querier Rev_Ref ('EQ', 'IN', 'NE')>
    Rev_Ref <Attr.Type.Querier Rev_Ref ('EQ', 'IN', 'NE')>
    Int <Attr.Type.Querier Ckd ('EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE')>
    Surrogate <Attr.Type.Querier Ckd ('EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE')>
    String <Attr.Type.Querier String ('CONTAINS', 'ENDSWITH', 'EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE', 'STARTSWITH')>
    Link_Ref_List <Attr.Type.Querier Rev_Ref ('EQ', 'IN', 'NE')>

    >>> for attr in lifetime_attrs :
    ...     print (attr.typ, attr.AQ.__class__)
    Date <Attr.Type.Querier Date ('EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE')>
    Date <Attr.Type.Querier Date ('EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE')>
    Boolean <Attr.Type.Querier Boolean ('EQ',)>

    >>> PhP_ET_person = PAP.Person_has_Phone.E_Type.attributes ["left"]
    >>> print (PhP_ET_person.AQ)
    <left.AQ [Attr.Type.Querier Id_Entity]>
    >>> print (PhP_ET_person.AQ.lifetime)
    <left.lifetime.AQ [Attr.Type.Querier Composite]>
    >>> print (PhP_ET_person.AQ.lifetime.start)
    <left.lifetime.start.AQ [Attr.Type.Querier Date]>

    >>> print (PAP.Person_has_Phone.E_Type.AQ.person)
    <left.AQ [Attr.Type.Querier Id_Entity]>
    >>> print (PAP.Person_has_Phone.E_Type.AQ.person.lifetime)
    <left.lifetime.AQ [Attr.Type.Querier Composite]>
    >>> print (PAP.Person_has_Phone.E_Type.AQ.person.lifetime.start)
    <left.lifetime.start.AQ [Attr.Type.Querier Date]>

    >>> def show_Q (a, level = 0) :
    ...     print ("%%s%%-20s%%s" %% ("  " * level, a._attr_name, a.Sig_Key))
    ...     for c in a.Attrs :
    ...         show_Q (c, level + 1)
    >>> AQ = PAP.Person_has_Phone.AQ
    >>> for pka in PAP.Person_has_Phone.E_Type.primary :
    ...     show_Q (getattr (AQ, pka.name))
    left                2
      last_name           3
      first_name          3
      middle_name         3
      title               3
      lifetime            None
        start               0
          day                 0
          month               0
          year                0
        finish              0
          day                 0
          month               0
          year                0
        alive               1
      sex                 0
    right               2
      sn                  3
      ndc                 3
      cc                  3
      desc                3
    extension           3

    >>> for pka in scope.SRM.Boat_in_Regatta.E_Type.AQ.Attrs :
    ...     show_Q (pka)
    left                2
      left                2
        name                3
        beam                0
        loa                 0
        max_crew            0
        sail_area           0
      sail_number         4
      nation              0
      sail_number_x       3
      name                3
    right               2
      left                2
        name                3
        date                None
          start               0
            day                 0
            month               0
            year                0
          finish              0
            day                 0
            month               0
            year                0
          alive               1
        club                2
          name                3
          long_name           3
        desc                3
        is_cancelled        1
        perma_name          3
        year                0
      boat_class          2
        name                3
      discards            0
      is_cancelled        1
      kind                3
      races               0
      result              None
        date                0
        software            3
        status              3
      starters_rl         0
      perma_name          3
      races_counted       0
      year                0
    skipper             2
      left                2
        last_name           3
        first_name          3
        middle_name         3
        title               3
        lifetime            None
          start               0
            day                 0
            month               0
            year                0
          finish              0
            day                 0
            month               0
            year                0
          alive               1
        sex                 0
      mna_number          4
      nation              0
      club                2
        name                3
        long_name           3
    place               0
    points              0
    yardstick           0
    creation            2
      c_time              0
      c_user              2
      kind                3
      time                0
      user                2
    last_change         2
      c_time              0
      c_user              2
      kind                3
      time                0
      user                2
    last_cid            0
    pid                 0
    type_name           3
    rank                0
    registration_date   0
      day                 0
      month               0
      year                0
    events              2
      date                None
        start               0
          day                 0
          month               0
          year                0
        finish              0
          day                 0
          month               0
          year                0
        alive               1
      time                None
        start               0
          hour                0
          minute              0
          second              0
        finish              0
          hour                0
          minute              0
          second              0
      calendar            2
        name                3
        desc                3
      detail              3
      short_title         3
    race_results        2
      race                0
      points              0
      status              3
      discarded           1
    _crew               2
      mna_number          4
      nation              0
      club                2
        name                3
        long_name           3
    teams               2
      left                2
        left                2
          name                3
          date                None
            start               0
              day                 0
              month               0
              year                0
            finish              0
              day                 0
              month               0
              year                0
            alive               1
          club                2
            name                3
            long_name           3
          desc                3
          is_cancelled        1
          perma_name          3
          year                0
        boat_class          2
          name                3
          beam                0
          loa                 0
          max_crew            0
          sail_area           0
        discards            0
        is_cancelled        1
        kind                3
        races               0
        result              None
          date                0
          software            3
          status              3
        starters_rl         0
        is_team_race        1
        perma_name          3
        races_counted       0
        year                0
        max_crew            0
      name                3
      club                2
        name                3
        long_name           3
      desc                3
      leader              2
        last_name           3
        first_name          3
        middle_name         3
        title               3
        lifetime            None
          start               0
            day                 0
            month               0
            year                0
          finish              0
            day                 0
            month               0
            year                0
          alive               1
        sex                 0
      place               0
      registration_date   0
        day                 0
        month               0
        year                0

    >>> def show_QA (a) :
    ...     print (repr (a._attr))
    ...     for c in a.Atoms :
    ...         print ("   ", repr (c._attr), c._full_name)
    >>> def show_QUA (a) :
    ...     print (repr (a._attr), "unwrapped")
    ...     for c in a.Unwrapped_Atoms :
    ...         print ("   ", repr (c._attr), c._full_name)
    >>> for pka in scope.SRM.Boat_in_Regatta.E_Type.AQ.Attrs :
    ...     show_QA (pka)
    ...     show_QUA (pka)
    Boat `left`
        String `name` left.left.name
        Float `beam` left.left.beam
        Float `loa` left.left.loa
        Int `max_crew` left.left.max_crew
        Float `sail_area` left.left.sail_area
        Int `sail_number` left.sail_number
        Nation `nation` left.nation
        String `sail_number_x` left.sail_number_x
        String `name` left.name
    Boat `left` unwrapped
        String `name` left.name
        Int `sail_number` sail_number
        Nation `nation` nation
        String `sail_number_x` sail_number_x
        String `name` name
    Regatta `right`
        String `name` right.left.name
        Date `start` right.left.date.start
        Date `finish` right.left.date.finish
        Boolean `alive` right.left.date.alive
        String `name` right.left.club.name
        String `long_name` right.left.club.long_name
        String `desc` right.left.desc
        Boolean `is_cancelled` right.left.is_cancelled
        String `perma_name` right.left.perma_name
        Int `year` right.left.year
        String `name` right.boat_class.name
        Int `discards` right.discards
        Boolean `is_cancelled` right.is_cancelled
        String `kind` right.kind
        Int `races` right.races
        Date-Time `date` right.result.date
        String `software` right.result.software
        String `status` right.result.status
        Int `starters_rl` right.starters_rl
        String `perma_name` right.perma_name
        Int `races_counted` right.races_counted
        Int `year` right.year
    Regatta `right` unwrapped
        String `name` left.name
        Date `start` left.date.start
        Date `finish` left.date.finish
        String `name` boat_class.name
        Int `discards` discards
        Boolean `is_cancelled` is_cancelled
        String `kind` kind
        Int `races` races
        Date-Time `date` result.date
        String `software` result.software
        String `status` result.status
        Int `starters_rl` starters_rl
        String `perma_name` perma_name
        Int `races_counted` races_counted
        Int `year` year
    Entity `skipper`
        String `last_name` skipper.left.last_name
        String `first_name` skipper.left.first_name
        String `middle_name` skipper.left.middle_name
        String `title` skipper.left.title
        Date `start` skipper.left.lifetime.start
        Date `finish` skipper.left.lifetime.finish
        Boolean `alive` skipper.left.lifetime.alive
        Sex `sex` skipper.left.sex
        Int `mna_number` skipper.mna_number
        Nation `nation` skipper.nation
        String `name` skipper.club.name
        String `long_name` skipper.club.long_name
    Entity `skipper` unwrapped
        String `last_name` left.last_name
        String `first_name` left.first_name
        String `middle_name` left.middle_name
        String `title` left.title
        Int `mna_number` mna_number
        Nation `nation` nation
        String `name` club.name
    Int `place`
        Int `place` place
    Int `place` unwrapped
        Int `place` place
    Int `points`
        Int `points` points
    Int `points` unwrapped
        Int `points` points
    Int `yardstick`
        Int `yardstick` yardstick
    Int `yardstick` unwrapped
        Int `yardstick` yardstick
    Rev_Ref `creation`
        Date-Time `c_time` creation.c_time
        String `kind` creation.kind
        Date-Time `time` creation.time
    Rev_Ref `creation` unwrapped
        Date-Time `c_time` c_time
        String `kind` kind
        Date-Time `time` time
    Rev_Ref `last_change`
        Date-Time `c_time` last_change.c_time
        String `kind` last_change.kind
        Date-Time `time` last_change.time
    Rev_Ref `last_change` unwrapped
        Date-Time `c_time` c_time
        String `kind` kind
        Date-Time `time` time
    Int `last_cid`
        Int `last_cid` last_cid
    Int `last_cid` unwrapped
        Int `last_cid` last_cid
    Surrogate `pid`
        Surrogate `pid` pid
    Surrogate `pid` unwrapped
        Surrogate `pid` pid
    String `type_name`
        String `type_name` type_name
    String `type_name` unwrapped
        String `type_name` type_name
    Int `rank`
        Int `rank` rank
    Int `rank` unwrapped
        Int `rank` rank
    Date `registration_date`
        Date `registration_date` registration_date
    Date `registration_date` unwrapped
        Int `day` day
        Int `month` month
        Int `year` year
    Link_Ref_List `events`
        Date `start` events.date.start
        Date `finish` events.date.finish
        Boolean `alive` events.date.alive
        Time `start` events.time.start
        Time `finish` events.time.finish
        Name `name` events.calendar.name
        String `desc` events.calendar.desc
        String `detail` events.detail
        String `short_title` events.short_title
    Link_Ref_List `events` unwrapped
        Date `start` date.start
        Date `finish` date.finish
        Time `start` time.start
        Time `finish` time.finish
        Name `name` calendar.name
        String `detail` detail
        String `short_title` short_title
    Link_Ref_List `race_results`
        Int `race` race_results.race
        Int `points` race_results.points
        String `status` race_results.status
        Boolean `discarded` race_results.discarded
    Link_Ref_List `race_results` unwrapped
        Int `race` race
        Int `points` points
        String `status` status
        Boolean `discarded` discarded
    Role_Ref_Set `_crew`
        Int `mna_number` _crew.mna_number
        Nation `nation` _crew.nation
        String `name` _crew.club.name
        String `long_name` _crew.club.long_name
    Role_Ref_Set `_crew` unwrapped
        Int `mna_number` mna_number
        Nation `nation` nation
        String `name` club.name
    Role_Ref_Set `teams`
        String `name` teams.left.left.name
        Date `start` teams.left.left.date.start
        Date `finish` teams.left.left.date.finish
        Boolean `alive` teams.left.left.date.alive
        String `name` teams.left.left.club.name
        String `long_name` teams.left.left.club.long_name
        String `desc` teams.left.left.desc
        Boolean `is_cancelled` teams.left.left.is_cancelled
        String `perma_name` teams.left.left.perma_name
        Int `year` teams.left.left.year
        String `name` teams.left.boat_class.name
        Float `beam` teams.left.boat_class.beam
        Float `loa` teams.left.boat_class.loa
        Int `max_crew` teams.left.boat_class.max_crew
        Float `sail_area` teams.left.boat_class.sail_area
        Int `discards` teams.left.discards
        Boolean `is_cancelled` teams.left.is_cancelled
        String `kind` teams.left.kind
        Int `races` teams.left.races
        Date-Time `date` teams.left.result.date
        String `software` teams.left.result.software
        String `status` teams.left.result.status
        Int `starters_rl` teams.left.starters_rl
        Boolean `is_team_race` teams.left.is_team_race
        String `perma_name` teams.left.perma_name
        Int `races_counted` teams.left.races_counted
        Int `year` teams.left.year
        Int `max_crew` teams.left.max_crew
        String `name` teams.name
        String `name` teams.club.name
        String `long_name` teams.club.long_name
        String `desc` teams.desc
        String `last_name` teams.leader.last_name
        String `first_name` teams.leader.first_name
        String `middle_name` teams.leader.middle_name
        String `title` teams.leader.title
        Date `start` teams.leader.lifetime.start
        Date `finish` teams.leader.lifetime.finish
        Boolean `alive` teams.leader.lifetime.alive
        Sex `sex` teams.leader.sex
        Int `place` teams.place
        Date `registration_date` teams.registration_date
    Role_Ref_Set `teams` unwrapped
        String `name` left.left.name
        Date `start` left.left.date.start
        Date `finish` left.left.date.finish
        String `name` left.boat_class.name
        String `name` name
        String `name` club.name
        String `desc` desc
        String `last_name` leader.last_name
        String `first_name` leader.first_name
        String `middle_name` leader.middle_name
        String `title` leader.title
        Int `place` place
        Date `registration_date` registration_date

    >>> seen = set ()
    >>> for at in sorted (scope.attribute_types, key = TFL.Getter.typ) :
    ...     msg = "%%s %%s %%s" %% (at.typ, at.AQ.__class__, at.AQ.Sig_Key)
    ...     if msg not in seen :
    ...         print (msg)
    ...         seen.add (msg)
    Account <Attr.Type.Querier Id_Entity ('EQ', 'IN', 'NE')> 2
    Address <Attr.Type.Querier Id_Entity ('EQ', 'IN', 'NE')> 2
    Angle <Attr.Type.Querier Raw ('CONTAINS', 'ENDSWITH', 'EQ', 'EQS', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE', 'NES', 'STARTSWITH')> 4
    Boat <Attr.Type.Querier Id_Entity ('EQ', 'IN', 'NE')> 2
    Boat_Class <Attr.Type.Querier Id_Entity ('EQ', 'IN', 'NE')> 2
    Boat_in_Regatta <Attr.Type.Querier Id_Entity ('EQ', 'IN', 'NE')> 2
    Boolean <Attr.Type.Querier Boolean ('EQ',)> 1
    Company <Attr.Type.Querier Id_Entity ('EQ', 'IN', 'NE')> 2
    Date <Attr.Type.Querier Date ('EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE')> 0
    Date-Slug <Attr.Type.Querier String ('CONTAINS', 'ENDSWITH', 'EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE', 'STARTSWITH')> 3
    Date-Time <Attr.Type.Querier Ckd ('EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE')> 0
    Date_Interval <Attr.Type.Querier Composite ()> None
    Date_List <Attr.Type.Querier Ckd ('EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE')> 0
    Date_Time_Interval <Attr.Type.Querier Composite ()> None
    Directory <Attr.Type.Querier String ('CONTAINS', 'ENDSWITH', 'EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE', 'STARTSWITH')> 3
    Email <Attr.Type.Querier Id_Entity ('EQ', 'IN', 'NE')> 2
    Email <Attr.Type.Querier String ('CONTAINS', 'ENDSWITH', 'EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE', 'STARTSWITH')> 3
    Entity <Attr.Type.Querier Id_Entity ('EQ', 'IN', 'NE')> 2
    Event <Attr.Type.Querier Id_Entity ('EQ', 'IN', 'NE')> 2
    Float <Attr.Type.Querier Ckd ('EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE')> 0
    Format <Attr.Type.Querier Ckd ('EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE')> 0
    Gallery <Attr.Type.Querier Id_Entity ('EQ', 'IN', 'NE')> 2
    Group <Attr.Type.Querier Id_Entity ('EQ', 'IN', 'NE')> 2
    Id_Entity <Attr.Type.Querier Id_Entity ('EQ', 'IN', 'NE')> 2
    Int <Attr.Type.Querier Ckd ('EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE')> 0
    Int <Attr.Type.Querier Raw ('CONTAINS', 'ENDSWITH', 'EQ', 'EQS', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE', 'NES', 'STARTSWITH')> 4
    Int_List <Attr.Type.Querier Ckd ('EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE')> 0
    Name <Attr.Type.Querier String ('CONTAINS', 'ENDSWITH', 'EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE', 'STARTSWITH')> 3
    Nation <Attr.Type.Querier Ckd ('EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE')> 0
    Numeric_String <Attr.Type.Querier String ('CONTAINS', 'ENDSWITH', 'EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE', 'STARTSWITH')> 3
    Object_PN <Attr.Type.Querier Id_Entity ('EQ', 'IN', 'NE')> 2
    Person <Attr.Type.Querier Id_Entity ('EQ', 'IN', 'NE')> 2
    Phone <Attr.Type.Querier Id_Entity ('EQ', 'IN', 'NE')> 2
    Picture <Attr.Type.Querier Composite ()> None
    Position <Attr.Type.Querier Composite ()> None
    Recurrence_Spec <Attr.Type.Querier Id_Entity ('EQ', 'IN', 'NE')> 2
    Regatta <Attr.Type.Querier Id_Entity ('EQ', 'IN', 'NE')> 2
    Regatta_C <Attr.Type.Querier Id_Entity ('EQ', 'IN', 'NE')> 2
    Regatta_Event <Attr.Type.Querier Id_Entity ('EQ', 'IN', 'NE')> 2
    Regatta_Result <Attr.Type.Querier Composite ()> None
    Sailor <Attr.Type.Querier Id_Entity ('EQ', 'IN', 'NE')> 2
    Sex <Attr.Type.Querier Ckd ('EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE')> 0
    String <Attr.Type.Querier String ('CONTAINS', 'ENDSWITH', 'EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE', 'STARTSWITH')> 3
    String <Attr.Type.Querier String_FL ('CONTAINS', 'ENDSWITH', 'EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE', 'STARTSWITH')> 3
    Team <Attr.Type.Querier Id_Entity ('EQ', 'IN', 'NE')> 2
    Text <Attr.Type.Querier String ('CONTAINS', 'ENDSWITH', 'EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE', 'STARTSWITH')> 3
    Thumbnail <Attr.Type.Querier Composite ()> None
    Time <Attr.Type.Querier Time ('EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE')> 0
    Time_Interval <Attr.Type.Querier Composite ()> None
    Unit <Attr.Type.Querier Ckd ('EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE')> 0
    Url <Attr.Type.Querier Id_Entity ('EQ', 'IN', 'NE')> 2
    Url <Attr.Type.Querier String ('CONTAINS', 'ENDSWITH', 'EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE', 'STARTSWITH')> 3
    Weekday_RR_List <Attr.Type.Querier Ckd ('EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE')> 0
    X <Attr.Type.Querier Ckd ('EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE')> 0
    Y <Attr.Type.Querier Ckd ('EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE')> 0

    >>> for sig, Sig_Key in sorted (pyk.iteritems (at.AQ.Signatures), key = TFL.Getter [1]) :
    ...     print (Sig_Key, sig)
    0 ('EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE')
    1 ('EQ',)
    2 ('EQ', 'IN', 'NE')
    3 ('CONTAINS', 'ENDSWITH', 'EQ', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE', 'STARTSWITH')
    4 ('CONTAINS', 'ENDSWITH', 'EQ', 'EQS', 'GE', 'GT', 'IN', 'LE', 'LT', 'NE', 'NES', 'STARTSWITH')
    5 ('CONTAINS', 'EQ', 'GE', 'GT', 'IN', 'IS_ADJACENT', 'LE', 'LT', 'NE', 'OVERLAPS')

    >>> for k, v in sorted (pyk.iteritems (at.AQ.Base_Op_Table)) :
    ...     print ("%%-12s %%s" %% (k, v))
    CONTAINS     <Attr.Filter CONTAINS [contains]>
    ENDSWITH     <Attr.Filter ENDSWITH [ends-with]>
    EQ           <Attr.Filter EQ [==]>
    EQS          <Attr.Filter EQS [EQS]>
    GE           <Attr.Filter GE [>=]>
    GT           <Attr.Filter GT [>]>
    IN           <Attr.Filter IN [in]>
    LE           <Attr.Filter LE [<=]>
    LT           <Attr.Filter LT [<]>
    NE           <Attr.Filter NE [!=]>
    NES          <Attr.Filter NES [NES]>
    STARTSWITH   <Attr.Filter STARTSWITH [starts-with]>

    >>> seen = set ()
    >>> for at in sorted (scope.attribute_types, key = TFL.Getter.typ) :
    ...     k = at.typ
    ...     if k not in seen and not isinstance (at, MOM.Attr._A_Entity_):
    ...         pt = portable_repr (at.P_Type) if at.P_Type else ("-" * 10)
    ...         print ("%%-20s %%-20s %%s" %% (at.typ, at, pt))
    ...         seen.add (k)
    Angle                lat                  <class 'builtins.float'>
    Boolean              discarded            <class 'builtins.bool'>
    Date                 date                 <class 'datetime.date'>
    Date-Slug            perma_name           <class 'builtins.text-string'>
    Date-Time            date                 <class 'datetime.datetime'>
    Date_List            date_exceptions      <class '_MOM._Attr.Coll.List'>
    Directory            directory            <class 'builtins.byte-string'>
    Email                address              <class 'builtins.text-string'>
    Float                beam                 <class 'builtins.float'>
    Format               format               ----------
    Int                  count                <class 'builtins.int'>
    Int_List             easter_offset        <class '_MOM._Attr.Coll.List'>
    Name                 name                 <class 'builtins.text-string'>
    Nation               nation               <class 'builtins.text-string'>
    Numeric_String       cc                   <class 'builtins.text-string'>
    Sex                  sex                  <class 'builtins.text-string'>
    String               city                 <class 'builtins.text-string'>
    Text                 abstract             <class 'builtins.text-string'>
    Time                 finish               <class 'datetime.time'>
    Unit                 unit                 <class 'builtins.int'>
    Url                  link_to              <class 'builtins.text-string'>
    Weekday_RR_List      week_day             <class '_MOM._Attr.Coll.List'>
    X                    width                <class 'builtins.int'>
    Y                    height               <class 'builtins.int'>

"""

from _GTW.__test__.model import *

__test__ = Scaffold.create_test_dict (_test_code)

### __END__ GTW.__test__.Attr_Filter
