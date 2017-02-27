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
#    GTW.__test__.Attr_unique
#
# Purpose
#    Test unique-ness predicates
#
# Revision Dates
#     4-Aug-2013 (CT) Creation
#    29-Jul-2015 (CT) Adapt to name change of PAP.Phone attributes
#    25-Feb-2016 (CT) Add `test_unique_hps`
#    24-Feb-2017 (CT) Import `MOM.Inspect`, not `MOM.inspect`
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _GTW.__test__.model import *
from   _MOM.Inspect        import children_trans_iter

_test_unique_hps = """
    >>> apt, url = Scaffold.app_type_and_url (%(p1)s, %(n1)s)

    >>> for ET in apt._T_Extension :
    ...     ems_ps = ET._Predicates.uniqueness_ems
    ...     dbw_ps = ET._Predicates.uniqueness_dbw
    ...     if (ems_ps or dbw_ps) and ET.is_relevant :
    ...         print (ET.type_name)
    ...         print (" ".join ((" " * 3, "EMS", ", ".join (str (p) for p in ems_ps))).rstrip ())
    ...         print (" ".join ((" " * 3, "DBW", ", ".join (str (p) for p in dbw_ps))).rstrip ())
    Auth.Account
        EMS
        DBW Uniqueness predicate: unique_epk ('name',)
    Auth.Certificate
        EMS
        DBW Uniqueness predicate: unique_epk ('email', 'validity', 'desc')
    Auth.Group
        EMS
        DBW Uniqueness predicate: unique_epk ('name',)
    Auth.Account_in_Group
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'right')
    Auth.Account_Activation
        EMS
        DBW Uniqueness predicate: unique_epk ('left',)
    Auth.Account_Password_Change_Required
        EMS
        DBW Uniqueness predicate: unique_epk ('left',)
    Auth.Account_EMail_Verification
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'token')
    Auth.Account_Password_Reset
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'token')
    EVT.Calendar
        EMS
        DBW Uniqueness predicate: unique_epk ('name',)
    EVT.Event
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'date', 'time', 'calendar')
    EVT.Event_occurs
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'date', 'time')
    EVT.Recurrence_Spec
        EMS
        DBW Uniqueness predicate: unique_epk ('left',)
    EVT.Recurrence_Rule
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'is_exception', 'desc')
    PAP.Address
        EMS
        DBW Uniqueness predicate: unique_epk ('street', 'zip', 'city', 'country')
    PAP.Company
        EMS
        DBW Uniqueness predicate: unique_epk ('name', 'registered_in')
    PAP.Email
        EMS
        DBW Uniqueness predicate: unique_epk ('address',)
    PAP.Phone
        EMS
        DBW Uniqueness predicate: unique_epk ('cc', 'ndc', 'sn')
    PAP.Person
        EMS
        DBW Uniqueness predicate: unique_epk ('last_name', 'first_name', 'middle_name', 'title')
    PAP.Url
        EMS
        DBW Uniqueness predicate: unique_epk ('value',)
    PAP.Address_Position
        EMS
        DBW Uniqueness predicate: unique_epk ('left',)
    PAP.Subject_has_Property
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'right')
    PAP.Person_has_Account
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'right')
    SRM._Boat_Class_
        EMS
        DBW Uniqueness predicate: unique_epk ('name',)
    SRM.Boat_Class
        EMS
        DBW Uniqueness predicate: unique_epk ('name',)
    SRM.Handicap
        EMS
        DBW Uniqueness predicate: unique_epk ('name',)
    SRM.Boat
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'sail_number', 'nation', 'sail_number_x')
    SRM.Club
        EMS
        DBW Uniqueness predicate: unique_epk ('name',)
    SRM.Regatta_Event
        EMS
        DBW Uniqueness predicate: unique_epk ('name', 'date')
    SWP.Page
        EMS
        DBW Uniqueness predicate: unique_epk ('perma_name',)
    SWP.Page_Y
        EMS
        DBW Uniqueness predicate: unique_epk ('perma_name', 'year')
    SWP.Clip_O
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'date_x')
    SWP.Clip_X
        EMS
        DBW Uniqueness predicate: unique_epk ('perma_name',)
    SWP.Gallery
        EMS
        DBW Uniqueness predicate: unique_epk ('perma_name',)
    SWP.Picture
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'number')
    SWP.Referral
        EMS
        DBW Uniqueness predicate: unique_epk ('parent_url', 'perma_name')
    SRM.Page
        EMS
        DBW Uniqueness predicate: unique_epk ('perma_name', 'event')
    SRM.Regatta
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'boat_class')
    SRM.Regatta_C
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'boat_class')
    SRM.Regatta_H
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'boat_class')
    SRM.Sailor
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'nation', 'mna_number', 'club')
    SRM.Boat_in_Regatta
        EMS Uniqueness predicate: unique_regatta_skipper ('regatta', 'skipper')
        DBW Uniqueness predicate: unique_epk ('left', 'right')
    SRM.Race_Result
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'race')
    SRM.Team
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'name')
    SRM.Crew_Member
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'right')
    SRM.Team_has_Boat_in_Regatta
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'right')
    PAP.Subject_has_Address
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'right')
    PAP.Subject_has_Email
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'right')
    PAP.Subject_has_Phone
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'right', 'extension')
    PAP.Subject_has_Url
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'right')
    PAP.Company_has_Url
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'right')
    PAP.Person_has_Url
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'right')
    PAP.Company_has_Phone
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'right', 'extension')
    PAP.Person_has_Phone
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'right', 'extension')
    PAP.Company_has_Email
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'right')
    PAP.Person_has_Email
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'right')
    PAP.Company_has_Address
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'right')
    PAP.Person_has_Address
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'right')

"""

_test_unique_sql = """
    >>> apt, url = Scaffold.app_type_and_url (%(p1)s, %(n1)s)

    >>> for ET in apt._T_Extension :
    ...     ems_ps = ET._Predicates.uniqueness_ems
    ...     dbw_ps = ET._Predicates.uniqueness_dbw
    ...     if (ems_ps or dbw_ps) and ET.is_relevant :
    ...         print (ET.type_name)
    ...         print (" ".join ((" " * 3, "EMS", ", ".join (str (p) for p in ems_ps))).rstrip ())
    ...         print (" ".join ((" " * 3, "DBW", ", ".join (str (p) for p in dbw_ps))).rstrip ())
    Auth.Account
        EMS
        DBW Uniqueness predicate: unique_epk ('name',)
    Auth.Certificate
        EMS
        DBW Uniqueness predicate: unique_epk ('email', 'validity', 'desc')
    Auth.Group
        EMS
        DBW Uniqueness predicate: unique_epk ('name',)
    Auth.Account_in_Group
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'right')
    Auth.Account_Activation
        EMS
        DBW Uniqueness predicate: unique_epk ('left',)
    Auth.Account_Password_Change_Required
        EMS
        DBW Uniqueness predicate: unique_epk ('left',)
    Auth.Account_EMail_Verification
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'token')
    Auth.Account_Password_Reset
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'token')
    EVT.Calendar
        EMS
        DBW Uniqueness predicate: unique_epk ('name',)
    EVT.Event
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'date', 'time', 'calendar')
    EVT.Event_occurs
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'date', 'time')
    EVT.Recurrence_Spec
        EMS
        DBW Uniqueness predicate: unique_epk ('left',)
    EVT.Recurrence_Rule
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'is_exception', 'desc')
    PAP.Address
        EMS
        DBW Uniqueness predicate: unique_epk ('street', 'zip', 'city', 'country')
    PAP.Company
        EMS
        DBW Uniqueness predicate: unique_epk ('name', 'registered_in')
    PAP.Email
        EMS
        DBW Uniqueness predicate: unique_epk ('address',)
    PAP.Phone
        EMS
        DBW Uniqueness predicate: unique_epk ('cc', 'ndc', 'sn')
    PAP.Person
        EMS
        DBW Uniqueness predicate: unique_epk ('last_name', 'first_name', 'middle_name', 'title')
    PAP.Url
        EMS
        DBW Uniqueness predicate: unique_epk ('value',)
    PAP.Address_Position
        EMS
        DBW Uniqueness predicate: unique_epk ('left',)
    PAP.Subject_has_Property
        EMS Uniqueness predicate: unique_epk ('left', 'right')
        DBW
    PAP.Person_has_Account
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'right')
    SRM._Boat_Class_
        EMS
        DBW Uniqueness predicate: unique_epk ('name',)
    SRM.Boat_Class
        EMS Uniqueness predicate: unique_epk ('name',)
        DBW
    SRM.Handicap
        EMS Uniqueness predicate: unique_epk ('name',)
        DBW
    SRM.Boat
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'sail_number', 'nation', 'sail_number_x')
    SRM.Club
        EMS
        DBW Uniqueness predicate: unique_epk ('name',)
    SRM.Regatta_Event
        EMS
        DBW Uniqueness predicate: unique_epk ('name', 'date')
    SWP.Page
        EMS Uniqueness predicate: unique_epk ('perma_name',)
        DBW
    SWP.Page_Y
        EMS Uniqueness predicate: unique_epk ('perma_name', 'year')
        DBW
    SWP.Clip_O
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'date_x')
    SWP.Clip_X
        EMS Uniqueness predicate: unique_epk ('perma_name',)
        DBW
    SWP.Gallery
        EMS
        DBW Uniqueness predicate: unique_epk ('perma_name',)
    SWP.Picture
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'number')
    SWP.Referral
        EMS
        DBW Uniqueness predicate: unique_epk ('parent_url', 'perma_name')
    SRM.Page
        EMS Uniqueness predicate: unique_epk ('perma_name', 'event')
        DBW
    SRM.Regatta
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'boat_class')
    SRM.Regatta_C
        EMS Uniqueness predicate: unique_epk ('left', 'boat_class')
        DBW
    SRM.Regatta_H
        EMS Uniqueness predicate: unique_epk ('left', 'boat_class')
        DBW
    SRM.Sailor
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'nation', 'mna_number', 'club')
    SRM.Boat_in_Regatta
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'right'), Uniqueness predicate: unique_regatta_skipper ('regatta', 'skipper')
    SRM.Race_Result
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'race')
    SRM.Team
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'name')
    SRM.Crew_Member
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'right')
    SRM.Team_has_Boat_in_Regatta
        EMS
        DBW Uniqueness predicate: unique_epk ('left', 'right')
    PAP.Subject_has_Address
        EMS Uniqueness predicate: unique_epk ('left', 'right')
        DBW
    PAP.Subject_has_Email
        EMS Uniqueness predicate: unique_epk ('left', 'right')
        DBW
    PAP.Subject_has_Phone
        EMS Uniqueness predicate: unique_epk ('left', 'right', 'extension')
        DBW
    PAP.Subject_has_Url
        EMS Uniqueness predicate: unique_epk ('left', 'right')
        DBW
    PAP.Company_has_Url
        EMS Uniqueness predicate: unique_epk ('left', 'right')
        DBW
    PAP.Person_has_Url
        EMS Uniqueness predicate: unique_epk ('left', 'right')
        DBW
    PAP.Company_has_Phone
        EMS Uniqueness predicate: unique_epk ('left', 'right', 'extension')
        DBW
    PAP.Person_has_Phone
        EMS Uniqueness predicate: unique_epk ('left', 'right', 'extension')
        DBW
    PAP.Company_has_Email
        EMS Uniqueness predicate: unique_epk ('left', 'right')
        DBW
    PAP.Person_has_Email
        EMS Uniqueness predicate: unique_epk ('left', 'right')
        DBW
    PAP.Company_has_Address
        EMS Uniqueness predicate: unique_epk ('left', 'right')
        DBW
    PAP.Person_has_Address
        EMS Uniqueness predicate: unique_epk ('left', 'right')
        DBW

"""

__test__ = Scaffold.create_test_dict \
    ( dict
        ( test_unique_sql      = _test_unique_sql
        )
    , ignore = ("HPS", )
    )

__test__.update \
    ( Scaffold.create_test_dict \
        ( dict
            ( test_unique_hps = _test_unique_hps
            )
        , ignore           = ("pg", "POS", "my", "MYS", "sq", "SQL")
        )
    )

### __END__ GTW.__test__.Attr_unique
