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
#    GTW.__test__.Attr_type_name
#
# Purpose
#    Test cases for attribute `type_name`
#
# Revision Dates
#     4-Jun-2013 (CT) Creation
#    13-Jun-2014 (RS) Fix tests for `PAP.Group`
#    24-Feb-2017 (CT) Import `MOM.Inspect`, not `MOM.inspect`
#    ««revision-date»»···
#--

from   __future__ import absolute_import, division, print_function, unicode_literals

from   _GTW.__test__.model import *
from   _MOM.Inspect        import children_trans_iter

_test_hierarchy = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> MOM = scope.MOM

    >>> sk = TFL.Getter [0].Essence.type_name
    >>> for T, l in sorted (children_trans_iter (MOM.Id_Entity), key = sk) :
    ...   if T.show_in_ui :
    ...     ak = T.attr_prop ("type_name").__class__.__name__
    ...     tn = T.type_name
    ...     print ("%%-30s %%s %%s %%s" %% (T.Essence.type_name, ak, type (tn).__name__, tn))
    Auth.Account                   Internal__Type_Name Type_Name_Type Auth.Account
    Auth.Account_in_Group          Internal__Type_Name Type_Name_Type Auth.Account_in_Group
    Auth.Certificate               Internal__Type_Name Type_Name_Type Auth.Certificate
    Auth.Group                     Internal__Type_Name Type_Name_Type Auth.Group
    Auth.Id_Entity                 Internal__Type_Name Type_Name_Type Auth.Id_Entity
    Auth.Link                      Internal__Type_Name Type_Name_Type Auth.Link
    Auth.Link1                     Internal__Type_Name Type_Name_Type Auth.Link1
    Auth.Link2                     Internal__Type_Name Type_Name_Type Auth.Link2
    Auth.Object                    Internal__Type_Name Type_Name_Type Auth.Object
    Auth._Account_                 Internal__Type_Name Type_Name_Type Auth._Account_
    Auth._Link_n_                  Internal__Type_Name Type_Name_Type Auth._Link_n_
    EVT.Calendar                   Internal__Type_Name Type_Name_Type EVT.Calendar
    EVT.Event                      Internal__Type_Name Type_Name_Type EVT.Event
    EVT.Event_occurs               Internal__Type_Name Type_Name_Type EVT.Event_occurs
    EVT.Id_Entity                  Internal__Type_Name Type_Name_Type EVT.Id_Entity
    EVT.Link                       Internal__Type_Name Type_Name_Type EVT.Link
    EVT.Link1                      Internal__Type_Name Type_Name_Type EVT.Link1
    EVT.Object                     Internal__Type_Name Type_Name_Type EVT.Object
    EVT.Recurrence_Rule            Internal__Type_Name Type_Name_Type EVT.Recurrence_Rule
    EVT.Recurrence_Spec            Internal__Type_Name Type_Name_Type EVT.Recurrence_Spec
    EVT._Recurrence_Mixin_         Internal__Type_Name Type_Name_Type EVT._Recurrence_Mixin_
    MOM.Id_Entity                  Internal__Type_Name Type_Name_Type MOM.Id_Entity
    MOM.Link                       Internal__Type_Name Type_Name_Type MOM.Link
    MOM.Link1                      Internal__Type_Name Type_Name_Type MOM.Link1
    MOM.Link2                      Internal__Type_Name Type_Name_Type MOM.Link2
    MOM.Object                     Internal__Type_Name Type_Name_Type MOM.Object
    MOM._Link_n_                   Internal__Type_Name Type_Name_Type MOM._Link_n_
    PAP.Address                    Internal__Type_Name Type_Name_Type PAP.Address
    PAP.Address_Position           Internal__Type_Name Type_Name_Type PAP.Address_Position
    PAP.Company                    Internal__Type_Name Type_Name_Type PAP.Company
    PAP.Company_has_Address        Internal__Type_Name Type_Name_Type PAP.Company_has_Address
    PAP.Company_has_Email          Internal__Type_Name Type_Name_Type PAP.Company_has_Email
    PAP.Company_has_Phone          Internal__Type_Name Type_Name_Type PAP.Company_has_Phone
    PAP.Company_has_Url            Internal__Type_Name Type_Name_Type PAP.Company_has_Url
    PAP.Email                      Internal__Type_Name Type_Name_Type PAP.Email
    PAP.Group                      Internal__Type_Name Type_Name_Type PAP.Group
    PAP.Id_Entity                  Internal__Type_Name Type_Name_Type PAP.Id_Entity
    PAP.Legal_Entity               Internal__Type_Name Type_Name_Type PAP.Legal_Entity
    PAP.Link                       Internal__Type_Name Type_Name_Type PAP.Link
    PAP.Link1                      Internal__Type_Name Type_Name_Type PAP.Link1
    PAP.Link2                      Internal__Type_Name Type_Name_Type PAP.Link2
    PAP.Object                     Internal__Type_Name Type_Name_Type PAP.Object
    PAP.Person                     Internal__Type_Name Type_Name_Type PAP.Person
    PAP.Person_has_Account         Internal__Type_Name Type_Name_Type PAP.Person_has_Account
    PAP.Person_has_Address         Internal__Type_Name Type_Name_Type PAP.Person_has_Address
    PAP.Person_has_Email           Internal__Type_Name Type_Name_Type PAP.Person_has_Email
    PAP.Person_has_Phone           Internal__Type_Name Type_Name_Type PAP.Person_has_Phone
    PAP.Person_has_Url             Internal__Type_Name Type_Name_Type PAP.Person_has_Url
    PAP.Phone                      Internal__Type_Name Type_Name_Type PAP.Phone
    PAP.Property                   Internal__Type_Name Type_Name_Type PAP.Property
    PAP.Subject                    Internal__Type_Name Type_Name_Type PAP.Subject
    PAP.Subject_has_Address        Internal__Type_Name Type_Name_Type PAP.Subject_has_Address
    PAP.Subject_has_Email          Internal__Type_Name Type_Name_Type PAP.Subject_has_Email
    PAP.Subject_has_Phone          Internal__Type_Name Type_Name_Type PAP.Subject_has_Phone
    PAP.Subject_has_Property       Internal__Type_Name Type_Name_Type PAP.Subject_has_Property
    PAP.Subject_has_Url            Internal__Type_Name Type_Name_Type PAP.Subject_has_Url
    PAP.Url                        Internal__Type_Name Type_Name_Type PAP.Url
    PAP._Link_n_                   Internal__Type_Name Type_Name_Type PAP._Link_n_
    SRM.Boat                       Internal__Type_Name Type_Name_Type SRM.Boat
    SRM.Boat_Class                 Internal__Type_Name Type_Name_Type SRM.Boat_Class
    SRM.Boat_in_Regatta            Internal__Type_Name Type_Name_Type SRM.Boat_in_Regatta
    SRM.Club                       Internal__Type_Name Type_Name_Type SRM.Club
    SRM.Crew_Member                Internal__Type_Name Type_Name_Type SRM.Crew_Member
    SRM.Handicap                   Internal__Type_Name Type_Name_Type SRM.Handicap
    SRM.Id_Entity                  Internal__Type_Name Type_Name_Type SRM.Id_Entity
    SRM.Link                       Internal__Type_Name Type_Name_Type SRM.Link
    SRM.Link1                      Internal__Type_Name Type_Name_Type SRM.Link1
    SRM.Link2                      Internal__Type_Name Type_Name_Type SRM.Link2
    SRM.Object                     Internal__Type_Name Type_Name_Type SRM.Object
    SRM.Page                       Internal__Type_Name Type_Name_Type SRM.Page
    SRM.Race_Result                Internal__Type_Name Type_Name_Type SRM.Race_Result
    SRM.Regatta                    Internal__Type_Name Type_Name_Type SRM.Regatta
    SRM.Regatta_C                  Internal__Type_Name Type_Name_Type SRM.Regatta_C
    SRM.Regatta_Event              Internal__Type_Name Type_Name_Type SRM.Regatta_Event
    SRM.Regatta_H                  Internal__Type_Name Type_Name_Type SRM.Regatta_H
    SRM.Sailor                     Internal__Type_Name Type_Name_Type SRM.Sailor
    SRM.Team                       Internal__Type_Name Type_Name_Type SRM.Team
    SRM.Team_has_Boat_in_Regatta   Internal__Type_Name Type_Name_Type SRM.Team_has_Boat_in_Regatta
    SRM._Boat_Class_               Internal__Type_Name Type_Name_Type SRM._Boat_Class_
    SRM._Link_n_                   Internal__Type_Name Type_Name_Type SRM._Link_n_
    SWP.Clip_O                     Internal__Type_Name Type_Name_Type SWP.Clip_O
    SWP.Clip_X                     Internal__Type_Name Type_Name_Type SWP.Clip_X
    SWP.Gallery                    Internal__Type_Name Type_Name_Type SWP.Gallery
    SWP.Id_Entity                  Internal__Type_Name Type_Name_Type SWP.Id_Entity
    SWP.Link                       Internal__Type_Name Type_Name_Type SWP.Link
    SWP.Link1                      Internal__Type_Name Type_Name_Type SWP.Link1
    SWP.Object                     Internal__Type_Name Type_Name_Type SWP.Object
    SWP.Object_PN                  Internal__Type_Name Type_Name_Type SWP.Object_PN
    SWP.Page                       Internal__Type_Name Type_Name_Type SWP.Page
    SWP.Page_Y                     Internal__Type_Name Type_Name_Type SWP.Page_Y
    SWP.Picture                    Internal__Type_Name Type_Name_Type SWP.Picture
    SWP.Referral                   Internal__Type_Name Type_Name_Type SWP.Referral

"""

_test_set = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> PAP = scope.PAP
    >>> p = PAP.Person ("Tanzer", "Christian")
    >>> for x in scope.MOM.Id_Entity.query ().order_by (Q.pid) :
    ...    print (x.type_name, x.ui_display)
    PAP.Person Tanzer Christian

    >>> p.type_name = "not PAP.Person"
    Traceback (most recent call last):
      ...
    AttributeError: Attribute `PAP.Person.type_name` cannot be changed

    >>> print (p.type_name, p.ui_display)
    PAP.Person Tanzer Christian

    >>> with expect_except (MOM.Error.Attribute_Set) :
    ...     p.set (type_name = "not PAP.Person")
    Attribute_Set: Can't set internal attribute Person.type_name to 'not PAP.Person'

    >>> print (p.type_name, p.ui_display)
    PAP.Person Tanzer Christian

    >>> with expect_except (MOM.Error.Attribute_Set) :
    ...     p.set_raw (type_name = "not PAP.Person")
    Attribute_Set: Can't set internal attribute Person.type_name to 'not PAP.Person'

    >>> print (p.type_name, p.ui_display)
    PAP.Person Tanzer Christian

    >>> p.__class__.type_name = "not PAP.Person"
    Traceback (most recent call last):
      ...
    AttributeError: can't set attribute

    >>> PAP.Person.type_name
    'PAP.Person'

    >>> PAP.Person.E_Type.type_name = "not PAP.Person"
    Traceback (most recent call last):
      ...
    AttributeError: can't set attribute

    >>> PAP.Person.type_name
    'PAP.Person'

"""

__test__ = Scaffold.create_test_dict \
    ( dict
        ( test_hierarchy = _test_hierarchy
        , test_set       = _test_set
        )
    )

### __END__ GTW.__test__.Attr_type_name
