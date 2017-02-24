# -*- coding: utf-8 -*-
# Copyright (C) 2012-2016 Mag. Christian Tanzer All rights reserved
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
#    GTW.__test__.Page_uv
#
# Purpose
#    Test Page subtypes.
#
# Revision Dates
#    30-Jan-2012 (CT) Creation
#    19-Mar-2012 (CT) Adapt to factoring of `PAP.Subject`
#    19-Mar-2012 (CT) Adapt to reification of `SRM.Handicap`
#     2-Aug-2012 (MG) New test for `auto_up_depends` attributes added
#    12-Sep-2012 (RS) Add `Id_Entity`
#     6-Dec-2012 (CT) Add `Person_has_Account`
#     6-Dec-2012 (CT) Remove `Entity_created_by_Person`
#    14-Dec-2012 (CT) Test relevant_roots for relevant `E_Types`
#    20-Jan-2013 (CT) Add `Auth.Certificate`
#     4-Mar-2013 (CT) Add `PAP.Legal_Entity`
#     6-Mar-2013 (CT) Adapt to new attribute `Company.registered_in`
#    13-Jun-2014 (RS) Fix tests for `PAP.Group`
#    29-Jul-2015 (CT) Adapt to name change of PAP.Phone attributes
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

_test_code = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> SWP = scope.SWP

    >>> SWP.Page_U ("foo", text = "U", format = SWP.Format.ReST)
    SWP.Page_U ('foo')
    >>> scope.commit ()

    >>> SWP.Page_U.query_s (perma_name = "foo").all ()
    [SWP.Page_U ('foo')]
    >>> SWP.Page_V.query_s (perma_name = "foo").all ()
    []
    >>> SWP.Page.query_s (perma_name = "foo").all ()
    [SWP.Page_U ('foo')]

    >>> scope.commit ()
    >>> with expect_except (MOM.Error.Invariants) :
    ...     SWP.Page_V ("foo", text = "V")
    Invariants: The attribute values for 'perma_name' must be unique for each object
      The new definition of Page V SWP.Page_V ('foo',) would clash with 1 existing entities
      Already existing:
        SWP.Page_U ('foo',)
    >>> SWP.Page_U.query_s (perma_name = "foo").all ()
    [SWP.Page_U ('foo')]
    >>> SWP.Page_V.query_s (perma_name = "foo").all ()
    []
    >>> SWP.Page.query_s (perma_name = "foo").all ()
    [SWP.Page_U ('foo')]

    >>> SWP.Page_V ("bar", text = "V", format = "Markdown", raw = True)
    SWP.Page_V ('bar')
    >>> scope.commit ()

    >>> SWP.Page_U.query_s ().all ()
    [SWP.Page_U ('foo')]
    >>> SWP.Page_V.query_s ().all ()
    [SWP.Page_V ('bar')]
    >>> SWP.Page.query_s ().all ()
    [SWP.Page_V ('bar'), SWP.Page_U ('foo')]

    >>> akw = dict (format = "Markdown")
    >>> SWP.Page.query_s (* SWP.Page.raw_query_attrs (akw, akw)).all ()
    [SWP.Page_V ('bar')]

    >>> akw = dict (format = "ReST")
    >>> SWP.Page.query_s (* SWP.Page.raw_query_attrs (akw, akw)).all ()
    [SWP.Page_U ('foo')]

    >>> fmt = "%%(type_name)-45s  %%(polymorphic_epk)-5s  %%(epk_sig)s"
    >>> rets = list (et for et in scope.app_type._T_Extension if et.PNS != MOM and et.is_relevant)
    >>> rets = sorted (rets, key = TFL.Sorted_By ("epk_sig", "type_name"))
    >>> for et in rets :
    ...     print (fmt %% TFL.Caller.Object_Scope (et))
    PAP.Email                                      False  ('address',)
    PAP.Phone                                      False  ('cc', 'ndc', 'sn')
    Auth.Certificate                               False  ('email', 'validity', 'desc')
    PAP.Person                                     False  ('last_name', 'first_name', 'middle_name', 'title')
    Auth.Account_Activation                        False  ('left',)
    Auth.Account_Password_Change_Required          False  ('left',)
    EVT.Recurrence_Spec                            False  ('left',)
    PAP.Address_Position                           False  ('left',)
    SRM.Regatta                                    False  ('left', 'boat_class')
    SRM.Regatta_C                                  False  ('left', 'boat_class')
    SRM.Regatta_H                                  False  ('left', 'boat_class')
    EVT.Event_occurs                               False  ('left', 'date', 'time')
    EVT.Event                                      False  ('left', 'date', 'time', 'calendar')
    SWP.Clip_O                                     False  ('left', 'date_x')
    EVT.Recurrence_Rule                            False  ('left', 'is_exception', 'desc')
    SRM.Team                                       False  ('left', 'name')
    SRM.Sailor                                     False  ('left', 'nation', 'mna_number', 'club')
    SWP.Picture                                    False  ('left', 'number')
    SRM.Race_Result                                False  ('left', 'race')
    Auth.Account_in_Group                          False  ('left', 'right')
    PAP.Company_has_Address                        False  ('left', 'right')
    PAP.Company_has_Email                          False  ('left', 'right')
    PAP.Company_has_Url                            False  ('left', 'right')
    PAP.Person_has_Account                         False  ('left', 'right')
    PAP.Person_has_Address                         False  ('left', 'right')
    PAP.Person_has_Email                           False  ('left', 'right')
    PAP.Person_has_Url                             False  ('left', 'right')
    PAP.Subject_has_Address                        False  ('left', 'right')
    PAP.Subject_has_Email                          False  ('left', 'right')
    PAP.Subject_has_Property                       True   ('left', 'right')
    PAP.Subject_has_Url                            False  ('left', 'right')
    SRM.Boat_in_Regatta                            False  ('left', 'right')
    SRM.Crew_Member                                False  ('left', 'right')
    SRM.Team_has_Boat_in_Regatta                   False  ('left', 'right')
    PAP.Company_has_Phone                          False  ('left', 'right', 'extension')
    PAP.Person_has_Phone                           False  ('left', 'right', 'extension')
    PAP.Subject_has_Phone                          False  ('left', 'right', 'extension')
    SRM.Boat                                       False  ('left', 'sail_number', 'nation', 'sail_number_x')
    Auth.Account_EMail_Verification                False  ('left', 'token')
    Auth.Account_Password_Reset                    False  ('left', 'token')
    Auth.Account                                   False  ('name',)
    Auth.Group                                     False  ('name',)
    EVT.Calendar                                   False  ('name',)
    SRM.Boat_Class                                 False  ('name',)
    SRM.Club                                       False  ('name',)
    SRM.Handicap                                   False  ('name',)
    SRM._Boat_Class_                               False  ('name',)
    SRM.Regatta_Event                              False  ('name', 'date')
    PAP.Company                                    False  ('name', 'registered_in')
    SWP.Referral                                   False  ('parent_url', 'perma_name')
    SWP.Clip_X                                     False  ('perma_name',)
    SWP.Gallery                                    False  ('perma_name',)
    SWP.Page                                       True   ('perma_name',)
    SWP.Page_U                                     False  ('perma_name',)
    SWP.Page_V                                     False  ('perma_name',)
    SRM.Page                                       False  ('perma_name', 'event')
    SWP.Page_Y                                     False  ('perma_name', 'year')
    PAP.Address                                    False  ('street', 'zip', 'city', 'country')
    PAP.Url                                        False  ('value',)

    >>> fmt = "%%(type_name)-45s  %%(is_relevant)-5s  %%(polymorphic_epk)-5s  %%(polymorphic_epks)s"
    >>> for i, et in enumerate (scope.app_type._T_Extension) :
    ...   if not i :
    ...     print (fmt %% (dict (type_name = "type_name", is_relevant = "relev", polymorphic_epk = "p_epk", polymorphic_epks = "p_epks")))
    ...     print ("=" * 70)
    ...   if et.PNS != MOM :
    ...     print (fmt %% TFL.Caller.Object_Scope (et))
    type_name                                      relev  p_epk  p_epks
    ======================================================================
    Auth.Entity                                    False  True   True
    Auth.Id_Entity                                 False  True   True
    Auth.Object                                    False  True   True
    Auth._Account_                                 False  False  False
    Auth.Account                                   True   False  False
    Auth.Certificate                               True   False  False
    Auth.Group                                     True   False  False
    Auth.Link                                      False  True   True
    Auth._Link_n_                                  False  False  False
    Auth.Link2                                     False  False  False
    Auth.Account_in_Group                          True   False  False
    Auth.Link1                                     False  True   True
    Auth._Account_Action_                          False  True   True
    Auth.Account_Activation                        True   False  False
    Auth.Account_Password_Change_Required          True   False  False
    Auth._Account_Token_Action_                    False  False  False
    Auth.Account_EMail_Verification                True   False  False
    Auth.Account_Password_Reset                    True   False  False
    EVT.Entity                                     False  True   True
    EVT.Id_Entity                                  False  True   True
    EVT.Object                                     False  True   True
    EVT.Calendar                                   True   False  False
    EVT.Link                                       False  True   True
    EVT.Link1                                      False  True   True
    EVT.Event                                      True   False  True
    EVT.Event_occurs                               True   False  True
    EVT._Recurrence_Mixin_                         False  True   True
    EVT.Recurrence_Spec                            True   False  True
    EVT.Recurrence_Rule                            True   False  True
    PAP.Entity                                     False  True   True
    PAP.Id_Entity                                  False  True   True
    PAP.Object                                     False  True   True
    PAP.Property                                   False  True   True
    PAP.Address                                    True   False  False
    PAP.Subject                                    False  True   True
    PAP.Group                                      False  True   True
    PAP.Legal_Entity                               False  True   True
    PAP.Company                                    True   False  False
    PAP.Email                                      True   False  False
    PAP.Phone                                      True   False  False
    PAP.Person                                     True   False  False
    PAP.Url                                        True   False  False
    PAP.Link                                       False  True   True
    PAP.Link1                                      False  False  False
    PAP.Address_Position                           True   False  False
    PAP._Link_n_                                   False  True   True
    PAP.Link2                                      False  True   True
    PAP.Subject_has_Property                       True   True   True
    PAP.Person_has_Account                         True   False  False
    SRM.Regatta_Result                             False  False  False
    SRM.Entity                                     False  True   True
    SRM.Id_Entity                                  False  True   True
    SRM.Object                                     False  True   True
    SRM._Boat_Class_                               True   False  False
    SRM.Boat_Class                                 True   False  False
    SRM.Handicap                                   True   False  False
    SRM.Link                                       False  True   True
    SRM.Link1                                      False  True   True
    SRM.Boat                                       True   False  False
    SRM.Club                                       True   False  False
    SRM.Regatta_Event                              True   False  False
    SWP.Entity                                     False  True   True
    SWP.Id_Entity                                  False  True   True
    SWP.Object                                     False  True   True
    SWP.Object_PN                                  False  True   True
    SWP.Page_Mixin                                 False  True   True
    SWP.Page                                       True   True   True
    SWP.Page_Y                                     True   False  False
    SWP.Link                                       False  True   True
    SWP.Link1                                      False  True   True
    SWP.Clip_O                                     True   False  True
    SWP.Clip_X                                     True   False  False
    SWP.Gallery                                    True   False  False
    SWP.Picture                                    True   False  False
    SWP.Referral                                   True   False  False
    SRM.Page                                       True   False  False
    SRM.Regatta                                    True   False  False
    SRM.Regatta_C                                  True   False  False
    SRM.Regatta_H                                  True   False  False
    SRM.Sailor                                     True   False  False
    SRM._Link_n_                                   False  False  False
    SRM.Link2                                      False  False  False
    SRM.Boat_in_Regatta                            True   False  False
    SRM.Race_Result                                True   False  False
    SRM.Team                                       True   False  False
    SRM.Crew_Member                                True   False  False
    SRM.Team_has_Boat_in_Regatta                   True   False  False
    SWP.Page_U                                     True   False  False
    SWP.Page_V                                     True   False  False
    PAP.Subject_has_Address                        True   False  True
    PAP.Subject_has_Email                          True   False  True
    PAP.Subject_has_Phone                          True   False  True
    PAP.Subject_has_Url                            True   False  True
    PAP.Company_has_Url                            True   False  False
    PAP.Person_has_Url                             True   False  False
    PAP.Company_has_Phone                          True   False  False
    PAP.Person_has_Phone                           True   False  False
    PAP.Company_has_Email                          True   False  False
    PAP.Person_has_Email                           True   False  False
    PAP.Company_has_Address                        True   False  False
    PAP.Person_has_Address                         True   False  False

    >>> fmt = "%%-45s  %%s"
    >>> for et in scope.app_type._T_Extension :
    ...     rr = ("%%s %%s" %% (et.relevant_root.type_name, len (et.relevant_roots or {}))) if et.relevant_root else sorted (getattr (et, "relevant_roots", {}))
    ...     if rr :
    ...         print (fmt %% (et.type_name, rr))
    MOM.Id_Entity                                  ['Auth.Account', 'Auth.Account_Activation', 'Auth.Account_EMail_Verification', 'Auth.Account_Password_Change_Required', 'Auth.Account_Password_Reset', 'Auth.Account_in_Group', 'Auth.Certificate', 'Auth.Group', 'EVT.Calendar', 'EVT.Event', 'EVT.Event_occurs', 'EVT.Recurrence_Rule', 'EVT.Recurrence_Spec', 'PAP.Address', 'PAP.Address_Position', 'PAP.Company', 'PAP.Email', 'PAP.Person', 'PAP.Person_has_Account', 'PAP.Phone', 'PAP.Subject_has_Property', 'PAP.Url', 'SRM.Boat', 'SRM.Boat_in_Regatta', 'SRM.Club', 'SRM.Crew_Member', 'SRM.Race_Result', 'SRM.Regatta', 'SRM.Regatta_Event', 'SRM.Sailor', 'SRM.Team', 'SRM.Team_has_Boat_in_Regatta', 'SRM._Boat_Class_', 'SWP.Clip_O', 'SWP.Gallery', 'SWP.Page', 'SWP.Picture', 'SWP.Referral']
    MOM.Link                                       ['Auth.Account_Activation', 'Auth.Account_EMail_Verification', 'Auth.Account_Password_Change_Required', 'Auth.Account_Password_Reset', 'Auth.Account_in_Group', 'EVT.Event', 'EVT.Event_occurs', 'EVT.Recurrence_Rule', 'EVT.Recurrence_Spec', 'PAP.Address_Position', 'PAP.Person_has_Account', 'PAP.Subject_has_Property', 'SRM.Boat', 'SRM.Boat_in_Regatta', 'SRM.Crew_Member', 'SRM.Race_Result', 'SRM.Regatta', 'SRM.Sailor', 'SRM.Team', 'SRM.Team_has_Boat_in_Regatta', 'SWP.Clip_O', 'SWP.Picture']
    MOM.Link1                                      ['Auth.Account_Activation', 'Auth.Account_EMail_Verification', 'Auth.Account_Password_Change_Required', 'Auth.Account_Password_Reset', 'EVT.Event', 'EVT.Event_occurs', 'EVT.Recurrence_Rule', 'EVT.Recurrence_Spec', 'PAP.Address_Position', 'SRM.Boat', 'SRM.Race_Result', 'SRM.Regatta', 'SRM.Sailor', 'SRM.Team', 'SWP.Clip_O', 'SWP.Picture']
    MOM._Link_n_                                   ['Auth.Account_in_Group', 'PAP.Person_has_Account', 'PAP.Subject_has_Property', 'SRM.Boat_in_Regatta', 'SRM.Crew_Member', 'SRM.Team_has_Boat_in_Regatta']
    MOM.Link2                                      ['Auth.Account_in_Group', 'PAP.Person_has_Account', 'PAP.Subject_has_Property', 'SRM.Boat_in_Regatta', 'SRM.Crew_Member', 'SRM.Team_has_Boat_in_Regatta']
    MOM.Object                                     ['Auth.Account', 'Auth.Certificate', 'Auth.Group', 'EVT.Calendar', 'PAP.Address', 'PAP.Company', 'PAP.Email', 'PAP.Person', 'PAP.Phone', 'PAP.Url', 'SRM.Club', 'SRM.Regatta_Event', 'SRM._Boat_Class_', 'SWP.Gallery', 'SWP.Page', 'SWP.Referral']
    Auth.Id_Entity                                 ['Auth.Account', 'Auth.Account_Activation', 'Auth.Account_EMail_Verification', 'Auth.Account_Password_Change_Required', 'Auth.Account_Password_Reset', 'Auth.Account_in_Group', 'Auth.Certificate', 'Auth.Group']
    Auth.Object                                    ['Auth.Account', 'Auth.Certificate', 'Auth.Group']
    Auth._Account_                                 ['Auth.Account']
    Auth.Account                                   Auth.Account 0
    Auth.Certificate                               Auth.Certificate 0
    Auth.Group                                     Auth.Group 0
    Auth.Link                                      ['Auth.Account_Activation', 'Auth.Account_EMail_Verification', 'Auth.Account_Password_Change_Required', 'Auth.Account_Password_Reset', 'Auth.Account_in_Group']
    Auth._Link_n_                                  ['Auth.Account_in_Group']
    Auth.Link2                                     ['Auth.Account_in_Group']
    Auth.Account_in_Group                          Auth.Account_in_Group 0
    Auth.Link1                                     ['Auth.Account_Activation', 'Auth.Account_EMail_Verification', 'Auth.Account_Password_Change_Required', 'Auth.Account_Password_Reset']
    Auth._Account_Action_                          ['Auth.Account_Activation', 'Auth.Account_EMail_Verification', 'Auth.Account_Password_Change_Required', 'Auth.Account_Password_Reset']
    Auth.Account_Activation                        Auth.Account_Activation 0
    Auth.Account_Password_Change_Required          Auth.Account_Password_Change_Required 0
    Auth._Account_Token_Action_                    ['Auth.Account_EMail_Verification', 'Auth.Account_Password_Reset']
    Auth.Account_EMail_Verification                Auth.Account_EMail_Verification 0
    Auth.Account_Password_Reset                    Auth.Account_Password_Reset 0
    EVT.Id_Entity                                  ['EVT.Calendar', 'EVT.Event', 'EVT.Event_occurs', 'EVT.Recurrence_Rule', 'EVT.Recurrence_Spec']
    EVT.Object                                     ['EVT.Calendar']
    EVT.Calendar                                   EVT.Calendar 0
    EVT.Link                                       ['EVT.Event', 'EVT.Event_occurs', 'EVT.Recurrence_Rule', 'EVT.Recurrence_Spec']
    EVT.Link1                                      ['EVT.Event', 'EVT.Event_occurs', 'EVT.Recurrence_Rule', 'EVT.Recurrence_Spec']
    EVT.Event                                      EVT.Event 0
    EVT.Event_occurs                               EVT.Event_occurs 0
    EVT._Recurrence_Mixin_                         ['EVT.Recurrence_Rule', 'EVT.Recurrence_Spec']
    EVT.Recurrence_Spec                            EVT.Recurrence_Spec 0
    EVT.Recurrence_Rule                            EVT.Recurrence_Rule 0
    PAP.Id_Entity                                  ['PAP.Address', 'PAP.Address_Position', 'PAP.Company', 'PAP.Email', 'PAP.Person', 'PAP.Person_has_Account', 'PAP.Phone', 'PAP.Subject_has_Property', 'PAP.Url']
    PAP.Object                                     ['PAP.Address', 'PAP.Company', 'PAP.Email', 'PAP.Person', 'PAP.Phone', 'PAP.Url']
    PAP.Property                                   ['PAP.Address', 'PAP.Email', 'PAP.Phone', 'PAP.Url']
    PAP.Address                                    PAP.Address 0
    PAP.Subject                                    ['PAP.Company', 'PAP.Person']
    PAP.Group                                      ['PAP.Company']
    PAP.Legal_Entity                               ['PAP.Company']
    PAP.Company                                    PAP.Company 0
    PAP.Email                                      PAP.Email 0
    PAP.Phone                                      PAP.Phone 0
    PAP.Person                                     PAP.Person 0
    PAP.Url                                        PAP.Url 0
    PAP.Link                                       ['PAP.Address_Position', 'PAP.Person_has_Account', 'PAP.Subject_has_Property']
    PAP.Link1                                      ['PAP.Address_Position']
    PAP.Address_Position                           PAP.Address_Position 0
    PAP._Link_n_                                   ['PAP.Person_has_Account', 'PAP.Subject_has_Property']
    PAP.Link2                                      ['PAP.Person_has_Account', 'PAP.Subject_has_Property']
    PAP.Subject_has_Property                       PAP.Subject_has_Property 0
    PAP.Person_has_Account                         PAP.Person_has_Account 0
    SRM.Id_Entity                                  ['SRM.Boat', 'SRM.Boat_in_Regatta', 'SRM.Club', 'SRM.Crew_Member', 'SRM.Race_Result', 'SRM.Regatta', 'SRM.Regatta_Event', 'SRM.Sailor', 'SRM.Team', 'SRM.Team_has_Boat_in_Regatta', 'SRM._Boat_Class_']
    SRM.Object                                     ['SRM.Club', 'SRM.Regatta_Event', 'SRM._Boat_Class_']
    SRM._Boat_Class_                               SRM._Boat_Class_ 0
    SRM.Boat_Class                                 SRM._Boat_Class_ 0
    SRM.Handicap                                   SRM._Boat_Class_ 0
    SRM.Link                                       ['SRM.Boat', 'SRM.Boat_in_Regatta', 'SRM.Crew_Member', 'SRM.Race_Result', 'SRM.Regatta', 'SRM.Sailor', 'SRM.Team', 'SRM.Team_has_Boat_in_Regatta']
    SRM.Link1                                      ['SRM.Boat', 'SRM.Race_Result', 'SRM.Regatta', 'SRM.Sailor', 'SRM.Team']
    SRM.Boat                                       SRM.Boat 0
    SRM.Club                                       SRM.Club 0
    SRM.Regatta_Event                              SRM.Regatta_Event 0
    SWP.Id_Entity                                  ['SWP.Clip_O', 'SWP.Gallery', 'SWP.Page', 'SWP.Picture', 'SWP.Referral']
    SWP.Object                                     ['SWP.Gallery', 'SWP.Page', 'SWP.Referral']
    SWP.Object_PN                                  ['SWP.Gallery', 'SWP.Page', 'SWP.Referral']
    SWP.Page                                       SWP.Page 0
    SWP.Page_Y                                     SWP.Page 0
    SWP.Link                                       ['SWP.Clip_O', 'SWP.Picture']
    SWP.Link1                                      ['SWP.Clip_O', 'SWP.Picture']
    SWP.Clip_O                                     SWP.Clip_O 0
    SWP.Clip_X                                     SWP.Page 0
    SWP.Gallery                                    SWP.Gallery 0
    SWP.Picture                                    SWP.Picture 0
    SWP.Referral                                   SWP.Referral 0
    SRM.Page                                       SWP.Page 0
    SRM.Regatta                                    SRM.Regatta 0
    SRM.Regatta_C                                  SRM.Regatta 0
    SRM.Regatta_H                                  SRM.Regatta 0
    SRM.Sailor                                     SRM.Sailor 0
    SRM._Link_n_                                   ['SRM.Boat_in_Regatta', 'SRM.Crew_Member', 'SRM.Team_has_Boat_in_Regatta']
    SRM.Link2                                      ['SRM.Boat_in_Regatta', 'SRM.Crew_Member', 'SRM.Team_has_Boat_in_Regatta']
    SRM.Boat_in_Regatta                            SRM.Boat_in_Regatta 0
    SRM.Race_Result                                SRM.Race_Result 0
    SRM.Team                                       SRM.Team 0
    SRM.Crew_Member                                SRM.Crew_Member 0
    SRM.Team_has_Boat_in_Regatta                   SRM.Team_has_Boat_in_Regatta 0
    SWP.Page_U                                     SWP.Page 0
    SWP.Page_V                                     SWP.Page 0
    PAP.Subject_has_Address                        PAP.Subject_has_Property 0
    PAP.Subject_has_Email                          PAP.Subject_has_Property 0
    PAP.Subject_has_Phone                          PAP.Subject_has_Property 0
    PAP.Subject_has_Url                            PAP.Subject_has_Property 0
    PAP.Company_has_Url                            PAP.Subject_has_Property 0
    PAP.Person_has_Url                             PAP.Subject_has_Property 0
    PAP.Company_has_Phone                          PAP.Subject_has_Property 0
    PAP.Person_has_Phone                           PAP.Subject_has_Property 0
    PAP.Company_has_Email                          PAP.Subject_has_Property 0
    PAP.Person_has_Email                           PAP.Subject_has_Property 0
    PAP.Company_has_Address                        PAP.Subject_has_Property 0
    PAP.Person_has_Address                         PAP.Subject_has_Property 0

    >>> print (sorted (rr.type_name for rr in scope.relevant_roots))
    ['Auth.Account', 'Auth.Account_Activation', 'Auth.Account_EMail_Verification', 'Auth.Account_Password_Change_Required', 'Auth.Account_Password_Reset', 'Auth.Account_in_Group', 'Auth.Certificate', 'Auth.Group', 'EVT.Calendar', 'EVT.Event', 'EVT.Event_occurs', 'EVT.Recurrence_Rule', 'EVT.Recurrence_Spec', 'PAP.Address', 'PAP.Address_Position', 'PAP.Company', 'PAP.Email', 'PAP.Person', 'PAP.Person_has_Account', 'PAP.Phone', 'PAP.Subject_has_Property', 'PAP.Url', 'SRM.Boat', 'SRM.Boat_in_Regatta', 'SRM.Club', 'SRM.Crew_Member', 'SRM.Race_Result', 'SRM.Regatta', 'SRM.Regatta_Event', 'SRM.Sailor', 'SRM.Team', 'SRM.Team_has_Boat_in_Regatta', 'SRM._Boat_Class_', 'SWP.Clip_O', 'SWP.Gallery', 'SWP.Page', 'SWP.Picture', 'SWP.Referral']

    >>> fmt = "%%-45s  %%-20s  %%s"
    >>> for et in rets :
    ...     print (fmt %% (et.type_name, et.epk_sig_root.type_name if et.epk_sig_root is not et else "=", et.epk_sig))
    PAP.Email                                      =                     ('address',)
    PAP.Phone                                      =                     ('cc', 'ndc', 'sn')
    Auth.Certificate                               =                     ('email', 'validity', 'desc')
    PAP.Person                                     =                     ('last_name', 'first_name', 'middle_name', 'title')
    Auth.Account_Activation                        =                     ('left',)
    Auth.Account_Password_Change_Required          =                     ('left',)
    EVT.Recurrence_Spec                            =                     ('left',)
    PAP.Address_Position                           =                     ('left',)
    SRM.Regatta                                    =                     ('left', 'boat_class')
    SRM.Regatta_C                                  SRM.Regatta           ('left', 'boat_class')
    SRM.Regatta_H                                  SRM.Regatta           ('left', 'boat_class')
    EVT.Event_occurs                               =                     ('left', 'date', 'time')
    EVT.Event                                      =                     ('left', 'date', 'time', 'calendar')
    SWP.Clip_O                                     =                     ('left', 'date_x')
    EVT.Recurrence_Rule                            =                     ('left', 'is_exception', 'desc')
    SRM.Team                                       =                     ('left', 'name')
    SRM.Sailor                                     =                     ('left', 'nation', 'mna_number', 'club')
    SWP.Picture                                    =                     ('left', 'number')
    SRM.Race_Result                                =                     ('left', 'race')
    Auth.Account_in_Group                          =                     ('left', 'right')
    PAP.Company_has_Address                        PAP.Subject_has_Property  ('left', 'right')
    PAP.Company_has_Email                          PAP.Subject_has_Property  ('left', 'right')
    PAP.Company_has_Url                            PAP.Subject_has_Property  ('left', 'right')
    PAP.Person_has_Account                         =                     ('left', 'right')
    PAP.Person_has_Address                         PAP.Subject_has_Property  ('left', 'right')
    PAP.Person_has_Email                           PAP.Subject_has_Property  ('left', 'right')
    PAP.Person_has_Url                             PAP.Subject_has_Property  ('left', 'right')
    PAP.Subject_has_Address                        PAP.Subject_has_Property  ('left', 'right')
    PAP.Subject_has_Email                          PAP.Subject_has_Property  ('left', 'right')
    PAP.Subject_has_Property                       =                     ('left', 'right')
    PAP.Subject_has_Url                            PAP.Subject_has_Property  ('left', 'right')
    SRM.Boat_in_Regatta                            =                     ('left', 'right')
    SRM.Crew_Member                                =                     ('left', 'right')
    SRM.Team_has_Boat_in_Regatta                   =                     ('left', 'right')
    PAP.Company_has_Phone                          PAP.Subject_has_Phone  ('left', 'right', 'extension')
    PAP.Person_has_Phone                           PAP.Subject_has_Phone  ('left', 'right', 'extension')
    PAP.Subject_has_Phone                          =                     ('left', 'right', 'extension')
    SRM.Boat                                       =                     ('left', 'sail_number', 'nation', 'sail_number_x')
    Auth.Account_EMail_Verification                =                     ('left', 'token')
    Auth.Account_Password_Reset                    =                     ('left', 'token')
    Auth.Account                                   =                     ('name',)
    Auth.Group                                     =                     ('name',)
    EVT.Calendar                                   =                     ('name',)
    SRM.Boat_Class                                 SRM._Boat_Class_      ('name',)
    SRM.Club                                       =                     ('name',)
    SRM.Handicap                                   SRM._Boat_Class_      ('name',)
    SRM._Boat_Class_                               =                     ('name',)
    SRM.Regatta_Event                              =                     ('name', 'date')
    PAP.Company                                    =                     ('name', 'registered_in')
    SWP.Referral                                   =                     ('parent_url', 'perma_name')
    SWP.Clip_X                                     SWP.Page              ('perma_name',)
    SWP.Gallery                                    =                     ('perma_name',)
    SWP.Page                                       =                     ('perma_name',)
    SWP.Page_U                                     SWP.Page              ('perma_name',)
    SWP.Page_V                                     SWP.Page              ('perma_name',)
    SRM.Page                                       =                     ('perma_name', 'event')
    SWP.Page_Y                                     =                     ('perma_name', 'year')
    PAP.Address                                    =                     ('street', 'zip', 'city', 'country')
    PAP.Url                                        =                     ('value',)

"""

_auto_update = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> SWP = scope.SWP

    >>> p = SWP.Page (perma_name = "p1", text = "First text")
    >>> prepr ((p.text, p.contents))
    ('First text', '<p>First text</p>\n')

    >>> p.set (text = "New Text")
    2
    >>> prepr ((p.text, p.contents))
    ('New Text', '<p>New Text</p>\n')

    >>> scope.commit ()

    >>> if hasattr (scope.ems.session, "expunge") : scope.ems.session.expunge ()
    >>> p = SWP.Page.query ().first ()
    >>> prepr ((p.text, p.contents))
    ('New Text', '<p>New Text</p>\n')

"""

from _GTW.__test__.model import *
from   _TFL.predicate    import any_true

_Ancestor_Essence = GTW.OMP.SWP.Page

class Page_U (_Ancestor_Essence) :
    """Page of type U"""

    ui_name = "Page U"

# end class Page_U

class Page_V (_Ancestor_Essence) :
    """Page of type V"""

    ui_name = "Page V"

# end class Page_V

__test__ = Scaffold.create_test_dict \
    ( dict
        ( normal      = _test_code
        , auto_update = _auto_update
        )
    )

### __END__ GTW.__test__.Page_uv
