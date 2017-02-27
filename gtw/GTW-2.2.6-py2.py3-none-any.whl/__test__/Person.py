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
#    GTW.__test__.Person
#
# Purpose
#    Test PAP.Person creation and querying
#
# Revision Dates
#    27-Apr-2010 (CT) Creation
#     5-Jul-2011 (CT) `MOM.Attr.Selector` tests added
#     6-Jul-2011 (CT) Tests for `f_completer` added
#    17-Jul-2011 (CT) s/f_completer/completer/, completion tests added
#    19-Jul-2011 (CT) Test for `Q.RAW` added
#    21-Jul-2011 (CT) Test for `Q.RAW` improved
#    22-Jul-2011 (CT) Completer tests adapted to changes in `MOM.Attr.Completer`
#    15-Sep-2011 (CT) Move instantiation of `attr.completer` to `MOM.Attr.Spec`
#    12-Jun-2012 (CT) Add test for `.attrs ("pid", "type_name")`
#    12-Sep-2012 (CT) Add `_test_partial_roles`
#    13-Sep-2012 (CT) Add `_test_roles`
#     6-Dec-2012 (CT) Add `Person_has_Account`
#     6-Dec-2012 (CT) Remove `Entity_created_by_Person`
#    19-Oct-2016 (CT) Add test `attr_prop`
#    19-Oct-2016 (CT) Add test `FO`
#    ««revision-date»»···
#--

from   __future__  import print_function

_test_attr_prop = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> PAP = scope.PAP

    >>> PAP.Person.attr_prop ("lifetime")
    Date_Interval `lifetime`

    >>> PAP.Person.attr_prop ("lifetime.start")
    Date `start`

    >>> PAP.Person.attr_prop ("lifetime.start.year")
    Int `year`

"""

_test_code = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> PAP = scope.PAP

    >>> print (PAP.Person.count)
    0
    >>> p = PAP.Person.instance_or_new ("Tanzer", "Christian") ### 1
    >>> p
    PAP.Person ('tanzer', 'christian', '', '')
    >>> print (PAP.Person.count)
    1
    >>> PAP.Person.instance ("Tanzer", "Christian")
    PAP.Person ('tanzer', 'christian', '', '')
    >>> PAP.Person.query_s ().all ()
    [PAP.Person ('tanzer', 'christian', '', '')]

    >>> PAP.Person.instance_or_new ("Tanzer", "Christian") ### 2
    PAP.Person ('tanzer', 'christian', '', '')
    >>> print (PAP.Person.count)
    1

    >>> p.edit_attr
    (String `last_name`, String `first_name`, String `middle_name`, String `title`, Date_Interval `lifetime`, Sex `sex`)
    >>> for a in p.edit_attr :
    ...     pn = a.P_Type.__name__
    ...     pn = portable_repr.Type_Name_Map.get (pn, pn)
    ...     prepr ((a.name, pn, a.get_value (p), a.get_raw (p)))
    ('last_name', 'text-string', 'tanzer', 'Tanzer')
    ('first_name', 'text-string', 'christian', 'Christian')
    ('middle_name', 'text-string', '', '')
    ('title', 'text-string', '', '')
    ('lifetime', 'Date_Interval_lifetime', MOM.Date_Interval_lifetime (), '')
    ('sex', 'text-string', None, '')

    >>> _ = PAP.Person ("Tanzer", "Egon")
    >>> _ = PAP.Person ("Tanzer", "Walter")
    >>> _ = PAP.Person ("Tanzer", "Martin")
    >>> _ = PAP.Person ("Tanzer", "Michael")

    >>> print (PAP.Person.count)
    5
    >>> print (PAP.Person.query ().count ())
    5
    >>> print (PAP.Person.query (Q.first_name.CONTAINS ("i")).count ())
    3
    >>> print (PAP.Person.query (Q.RAW.first_name.STARTSWITH ("M")).count ())
    2

    >>> S = MOM.Attr.Selector
    >>> S.primary (PAP.Person).names
    ('last_name', 'first_name', 'middle_name', 'title')
    >>> S.Combo (S.primary, exclude = S.P_optional) (PAP.Person).names
    ('last_name', 'first_name')
    >>> S.Combo (S.primary, exclude = S.P_required) (PAP.Person).names
    ('middle_name', 'title')
    >>> S.necessary (PAP.Person).names
    ('sex',)
    >>> S.optional (PAP.Person).names
    ('lifetime',)
    >>> S.required (PAP.Person).names
    ()
    >>> S.user (PAP.Person).names
    ('lifetime', 'sex')
    >>> pu = S.List (S.primary, S.user)
    >>> pu (PAP.Person).names
    ('last_name', 'first_name', 'middle_name', 'title', 'lifetime', 'sex')
    >>> S.Combo (pu, exclude = S.P_optional) (PAP.Person).names
    ('last_name', 'first_name')
    >>> S.Combo (pu, exclude = S.P_required) (PAP.Person).names
    ('middle_name', 'title', 'lifetime', 'sex')

    >>> S.Primary_Followers ("last_name") (PAP.Person).names
    ('first_name', 'middle_name', 'title')
    >>> S.Primary_Followers ("first_name") (PAP.Person).names
    ('middle_name', 'title')
    >>> S.Primary_Followers ("middle_name") (PAP.Person).names
    ('title',)
    >>> S.Primary_Followers ("title") (PAP.Person).names
    ()

    >>> lnc = PAP.Person.last_name.completer
    >>> print (lnc.name, lnc.names, lnc.treshold)
    last_name ('last_name', 'first_name', 'middle_name', 'title') 1
    >>> fnc = PAP.Person.first_name.completer
    >>> print (fnc.name, fnc.names, fnc.treshold)
    first_name ('first_name', 'last_name', 'middle_name', 'title') 1
    >>> tnc = PAP.Person.title.completer
    >>> print (tnc.name, tnc.names, tnc.treshold)
    title ('title',) 0

    >>> show_ac (lnc, scope, dict (last_name = "Ta"))
    Tanzer, Christian, '', ''
    Tanzer, Egon, '', ''
    Tanzer, Martin, '', ''
    Tanzer, Michael, '', ''
    Tanzer, Walter, '', ''
    >>> show_ac (lnc, scope, dict (last_name = "Ta", first_name = "M"))
    Tanzer, Martin, '', ''
    Tanzer, Michael, '', ''
    >>> show_ac (lnc, scope, dict (last_name = "Ta", first_name = "Ma"))
    Tanzer, Martin, '', ''
    >>> show_ac (lnc, scope, dict (last_name = "Ta", title = "Mag."))
    <BLANKLINE>

    >>> show_ac (lnc, scope, dict (last_name = "Ta"), complete_entity = True)
    Tanzer, Christian, '', '', 1, 1
    Tanzer, Egon, '', '', 2, 2
    Tanzer, Martin, '', '', 4, 4
    Tanzer, Michael, '', '', 5, 5
    Tanzer, Walter, '', '', 3, 3
    >>> show_ac (lnc, scope, dict (last_name = "Ta", first_name = "Ma"), complete_entity = True)
    Tanzer, Martin, '', '', 4, 4

    >>> lnc (scope, dict (last_name = "Ta")).count ()
    5
    >>> lnc (scope, dict (last_name = "Ta", first_name = "M")).count ()
    2
    >>> lnc (scope, dict (last_name = "Ta", first_name = "Ma")).count ()
    1
    >>> lnc (scope, dict (last_name = "Ta", first_name = "Mo")).count ()
    0
    >>> lnc (scope, dict ()).count ()
    0

    >>> PAP.Person.query_s (Q.last_name == "Tanzer").all ()
    []
    >>> PAP.Person.query_s (Q.RAW.last_name == "Tanzer").all ()
    [PAP.Person ('tanzer', 'christian', '', ''), PAP.Person ('tanzer', 'egon', '', ''), PAP.Person ('tanzer', 'martin', '', ''), PAP.Person ('tanzer', 'michael', '', ''), PAP.Person ('tanzer', 'walter', '', '')]
    >>> PAP.Person.query_s (Q.RAW.last_name.STARTSWITH ("Ta")).all ()
    [PAP.Person ('tanzer', 'christian', '', ''), PAP.Person ('tanzer', 'egon', '', ''), PAP.Person ('tanzer', 'martin', '', ''), PAP.Person ('tanzer', 'michael', '', ''), PAP.Person ('tanzer', 'walter', '', '')]

    >>> PAP.Person.query ().order_by (TFL.Sorted_By ("-first_name")).count ()
    5

    >>> PAP.Person.query_s (last_name = "tanzer").attrs ("pid", "type_name").all ()
    [(1, 'PAP.Person'), (2, 'PAP.Person'), (4, 'PAP.Person'), (5, 'PAP.Person'), (3, 'PAP.Person')]


"""

_test_FO = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> PAP = scope.PAP

    >>> p = PAP.Person.instance_or_new ("Tanzer", "Christian", lifetime = ("1959-09-26",))
    >>> print (p.ui_display)
    Tanzer Christian

    >>> print (getattr (p.FO, "lifetime"))
    1959-09-26

    >>> print (getattr (p.FO, "lifetime.start"))
    1959-09-26

    >>> print (getattr (p.FO, "lifetime.start.year"))
    1959

"""

_test_partial_roles = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> PAP = scope.PAP

    >>> for ET in scope.T_Extension :
    ...     for pr in ET.Partial_Roles :
    ...         pret = scope.entity_type (pr.E_Type)
    ...         print (ET.type_name, portable_repr (pr), pret.type_name, sorted (pret.children_np))
    EVT.Event <class '_GTW._OMP._EVT.Event.left'> MOM.Id_Entity ['Auth.Account', 'Auth.Account_Activation', 'Auth.Account_EMail_Verification', 'Auth.Account_Password_Change_Required', 'Auth.Account_Password_Reset', 'Auth.Account_in_Group', 'Auth.Certificate', 'Auth.Group', 'EVT.Calendar', 'EVT.Event', 'EVT.Event_occurs', 'EVT.Recurrence_Rule', 'EVT.Recurrence_Spec', 'PAP.Address', 'PAP.Address_Position', 'PAP.Company', 'PAP.Company_has_Address', 'PAP.Company_has_Email', 'PAP.Company_has_Phone', 'PAP.Company_has_Url', 'PAP.Email', 'PAP.Person', 'PAP.Person_has_Account', 'PAP.Person_has_Address', 'PAP.Person_has_Email', 'PAP.Person_has_Phone', 'PAP.Person_has_Url', 'PAP.Phone', 'PAP.Url', 'SRM.Boat', 'SRM.Boat_Class', 'SRM.Boat_in_Regatta', 'SRM.Club', 'SRM.Crew_Member', 'SRM.Handicap', 'SRM.Page', 'SRM.Race_Result', 'SRM.Regatta_C', 'SRM.Regatta_Event', 'SRM.Regatta_H', 'SRM.Sailor', 'SRM.Team', 'SRM.Team_has_Boat_in_Regatta', 'SWP.Clip_O', 'SWP.Gallery', 'SWP.Page', 'SWP.Picture', 'SWP.Referral']
    PAP.Subject_has_Property <class '_GTW._OMP._PAP.Subject_has_Property.left'> PAP.Subject ['PAP.Company', 'PAP.Person']
    PAP.Subject_has_Property <class '_GTW._OMP._PAP.Subject_has_Property.right'> PAP.Property ['PAP.Address', 'PAP.Email', 'PAP.Phone', 'PAP.Url']
    SWP.Clip_O <class '_GTW._OMP._SWP.Clip.left'> SWP.Object_PN ['SWP.Gallery', 'SWP.Page', 'SWP.Referral']
    SRM.Boat_in_Regatta <class '_GTW._OMP._SRM.Boat_in_Regatta.right'> SRM.Regatta ['SRM.Regatta_C', 'SRM.Regatta_H']
    PAP.Subject_has_Address <class '_GTW._OMP._PAP.Subject_has_Property.left'> PAP.Subject ['PAP.Company', 'PAP.Person']
    PAP.Subject_has_Email <class '_GTW._OMP._PAP.Subject_has_Property.left'> PAP.Subject ['PAP.Company', 'PAP.Person']
    PAP.Subject_has_Phone <class '_GTW._OMP._PAP.Subject_has_Property.left'> PAP.Subject ['PAP.Company', 'PAP.Person']
    PAP.Subject_has_Url <class '_GTW._OMP._PAP.Subject_has_Property.left'> PAP.Subject ['PAP.Company', 'PAP.Person']

"""

_test_roles = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> PAP = scope.PAP

    >>> for ET in scope.T_Extension :
    ...     for r in ET.Roles :
    ...         if r.E_Type :
    ...             ret = scope.entity_type (r.E_Type)
    ...             print (ET.type_name, r, ret.type_name)
    Auth.Account_in_Group Account `left` Auth.Account
    Auth.Account_in_Group Group `right` Auth.Group
    Auth._Account_Action_ Account `left` Auth.Account
    Auth.Account_Activation Account `left` Auth.Account
    Auth.Account_Password_Change_Required Account `left` Auth.Account
    Auth._Account_Token_Action_ Account `left` Auth.Account
    Auth.Account_EMail_Verification Account `left` Auth.Account
    Auth.Account_Password_Reset Account `left` Auth.Account
    EVT.Event Id_Entity `left` MOM.Id_Entity
    EVT.Event_occurs Event `left` EVT.Event
    EVT.Recurrence_Spec Event `left` EVT.Event
    EVT.Recurrence_Rule Recurrence_Spec `left` EVT.Recurrence_Spec
    PAP.Address_Position Address `left` PAP.Address
    PAP.Subject_has_Property Subject `left` PAP.Subject
    PAP.Subject_has_Property Property `right` PAP.Property
    PAP.Person_has_Account Person `left` PAP.Person
    PAP.Person_has_Account Account `right` Auth.Account
    SRM.Boat Boat_Class `left` SRM.Boat_Class
    SWP.Clip_O Object_PN `left` SWP.Object_PN
    SWP.Picture Gallery `left` SWP.Gallery
    SRM.Regatta Regatta_Event `left` SRM.Regatta_Event
    SRM.Regatta_C Regatta_Event `left` SRM.Regatta_Event
    SRM.Regatta_H Regatta_Event `left` SRM.Regatta_Event
    SRM.Sailor Person `left` PAP.Person
    SRM.Boat_in_Regatta Boat `left` SRM.Boat
    SRM.Boat_in_Regatta Regatta `right` SRM.Regatta
    SRM.Race_Result Boat_in_Regatta `left` SRM.Boat_in_Regatta
    SRM.Team Regatta_C `left` SRM.Regatta_C
    SRM.Crew_Member Boat_in_Regatta `left` SRM.Boat_in_Regatta
    SRM.Crew_Member Sailor `right` SRM.Sailor
    SRM.Team_has_Boat_in_Regatta Team `left` SRM.Team
    SRM.Team_has_Boat_in_Regatta Boat_in_Regatta `right` SRM.Boat_in_Regatta
    PAP.Subject_has_Address Subject `left` PAP.Subject
    PAP.Subject_has_Address Address `right` PAP.Address
    PAP.Subject_has_Email Subject `left` PAP.Subject
    PAP.Subject_has_Email Email `right` PAP.Email
    PAP.Subject_has_Phone Subject `left` PAP.Subject
    PAP.Subject_has_Phone Phone `right` PAP.Phone
    PAP.Subject_has_Url Subject `left` PAP.Subject
    PAP.Subject_has_Url Url `right` PAP.Url
    PAP.Company_has_Url Company `left` PAP.Company
    PAP.Company_has_Url Url `right` PAP.Url
    PAP.Person_has_Url Person `left` PAP.Person
    PAP.Person_has_Url Url `right` PAP.Url
    PAP.Company_has_Phone Company `left` PAP.Company
    PAP.Company_has_Phone Phone `right` PAP.Phone
    PAP.Person_has_Phone Person `left` PAP.Person
    PAP.Person_has_Phone Phone `right` PAP.Phone
    PAP.Company_has_Email Company `left` PAP.Company
    PAP.Company_has_Email Email `right` PAP.Email
    PAP.Person_has_Email Person `left` PAP.Person
    PAP.Person_has_Email Email `right` PAP.Email
    PAP.Company_has_Address Company `left` PAP.Company
    PAP.Company_has_Address Address `right` PAP.Address
    PAP.Person_has_Address Person `left` PAP.Person
    PAP.Person_has_Address Address `right` PAP.Address

"""

from   _GTW.__test__.model      import *
from   _MOM.import_MOM          import Q

from   itertools                import chain as ichain

def show_ac (completer, scope, val_dict, complete_entity = False) :
    def _gen (xs) :
        for x in sorted (xs) :
            yield ", ".join (str (f) or "''" for f in x)
    q     = completer (scope, val_dict)
    deps  = completer.names
    if complete_entity :
        deps += ("pid", "last_cid")
    attrs = tuple (getattr (Q.RAW, a) for a in deps)
    print ("\n".join (_gen (q.attrs (* attrs))))

__test__ = Scaffold.create_test_dict \
    ( dict
        ( attr_prop     = _test_attr_prop
        , FO            = _test_FO
        , main          = _test_code
        , partial_roles = _test_partial_roles
        , roles         = _test_roles
        )
    )

### __END__ GTW.__test__.Person
