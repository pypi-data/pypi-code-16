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
#    GTW.__test__.Attr
#
# Purpose
#    Test attribute framework
#
# Revision Dates
#    11-Jun-2013 (CT) Creation
#    26-Jun-2013 (CT) Add `test_pickled_types`, factor `_attr_map`
#    13-Jun-2014 (RS) Fix tests for `PAP.Group`
#    29-Jul-2015 (CT) Adapt to name change of PAP.Phone attributes
#    24-Feb-2017 (CT) Import `MOM.Inspect`, not `MOM.inspect`
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

### enforce import order
import _GTW._OMP._Auth.import_Auth
import _GTW._OMP._PAP.import_PAP
import _GTW._OMP._EVT.import_EVT
import _GTW._OMP._SWP.import_SWP
import _GTW._OMP._SRM.import_SRM

from   _GTW.__test__.model import *
from   _MOM.Inspect        import children_trans_iter
from   _TFL.pyk            import pyk

def _attr_map (Top) :
    result = TFL.defaultdict (list)
    for T, l in children_trans_iter (Top) :
        ET = T.E_Type
        for name, kind in sorted (pyk.iteritems (ET.attributes)) :
            if kind.show_in_ui and (ET.children_np or not ET.is_partial) :
                if not ET.type_name.startswith ("Auth") :
                    k  = (name, kind.DET_Root)
                    result [k].append ((kind, ET))
    return result
# end def _attr_map

_test_DET = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> MOM   = scope.MOM
    >>> nl    = pyk.unichr (10)
    >>> a_map = _attr_map (MOM.Id_Entity)

    >>> for (name, DT), xs in sorted (pyk.iteritems (a_map)) :
    ...     if len (xs) > 1 :
    ...         print ("%%s [%%s]" %% (name, DT))
    ...         for kind, ET in sorted (xs, key = lambda x : x [1].i_rank) :
    ...             flag = "*" if not ET.is_partial else ""
    ...             print ("    %%-30s%%-2s %%s" %% (ET.type_name, flag, kind.e_type.type_name))
    addresses [PAP.Subject]
        PAP.Subject                      PAP.Subject
        PAP.Group                        PAP.Subject
        PAP.Legal_Entity                 PAP.Subject
    boat_class [SRM.Regatta]
        SRM.Regatta                      SRM.Regatta
        SRM.Regatta_C                 *  SRM.Regatta_C
        SRM.Regatta_H                 *  SRM.Regatta_H
    clips [SWP.Object_PN]
        SWP.Object_PN                    SWP.Object_PN
        SWP.Page                      *  SWP.Object_PN
        SWP.Page_Y                    *  SWP.Object_PN
        SWP.Clip_X                    *  SWP.Object_PN
        SWP.Gallery                   *  SWP.Object_PN
        SWP.Referral                  *  SWP.Object_PN
        SRM.Page                      *  SWP.Object_PN
    contents [SWP.Page_Mixin]
        SWP.Page                      *  SWP.Page_Mixin
        SWP.Page_Y                    *  SWP.Page_Mixin
        SWP.Clip_X                    *  SWP.Page_Mixin
        SRM.Page                      *  SWP.Page_Mixin
    creation [MOM.Id_Entity]
        MOM.Id_Entity                    MOM.Id_Entity
        MOM.Link                         MOM.Id_Entity
        MOM.Link1                        MOM.Id_Entity
        MOM._Link_n_                     MOM.Id_Entity
        MOM.Link2                        MOM.Id_Entity
        MOM.Object                       MOM.Id_Entity
        PAP.Id_Entity                    MOM.Id_Entity
        PAP.Object                       MOM.Id_Entity
        PAP.Property                     MOM.Id_Entity
        PAP.Address                   *  MOM.Id_Entity
        PAP.Subject                      MOM.Id_Entity
        PAP.Group                        MOM.Id_Entity
        PAP.Legal_Entity                 MOM.Id_Entity
        PAP.Company                   *  MOM.Id_Entity
        PAP.Email                     *  MOM.Id_Entity
        PAP.Phone                     *  MOM.Id_Entity
        PAP.Person                    *  MOM.Id_Entity
        PAP.Url                       *  MOM.Id_Entity
        PAP.Link                         MOM.Id_Entity
        PAP.Link1                        MOM.Id_Entity
        PAP.Address_Position          *  MOM.Id_Entity
        PAP._Link_n_                     MOM.Id_Entity
        PAP.Link2                        MOM.Id_Entity
        PAP.Subject_has_Property         MOM.Id_Entity
        PAP.Person_has_Account        *  MOM.Id_Entity
        EVT.Id_Entity                    MOM.Id_Entity
        EVT.Object                       MOM.Id_Entity
        EVT.Calendar                  *  MOM.Id_Entity
        EVT.Link                         MOM.Id_Entity
        EVT.Link1                        MOM.Id_Entity
        EVT.Event                     *  MOM.Id_Entity
        EVT.Event_occurs              *  MOM.Id_Entity
        EVT._Recurrence_Mixin_           MOM.Id_Entity
        EVT.Recurrence_Spec           *  MOM.Id_Entity
        EVT.Recurrence_Rule           *  MOM.Id_Entity
        SWP.Id_Entity                    MOM.Id_Entity
        SWP.Object                       MOM.Id_Entity
        SWP.Object_PN                    MOM.Id_Entity
        SWP.Page                      *  MOM.Id_Entity
        SWP.Page_Y                    *  MOM.Id_Entity
        SWP.Link                         MOM.Id_Entity
        SWP.Link1                        MOM.Id_Entity
        SWP.Clip_O                    *  MOM.Id_Entity
        SWP.Clip_X                    *  MOM.Id_Entity
        SWP.Gallery                   *  MOM.Id_Entity
        SWP.Picture                   *  MOM.Id_Entity
        SWP.Referral                  *  MOM.Id_Entity
        SRM.Id_Entity                    MOM.Id_Entity
        SRM.Object                       MOM.Id_Entity
        SRM._Boat_Class_                 MOM.Id_Entity
        SRM.Boat_Class                *  MOM.Id_Entity
        SRM.Handicap                  *  MOM.Id_Entity
        SRM.Link                         MOM.Id_Entity
        SRM.Link1                        MOM.Id_Entity
        SRM.Boat                      *  MOM.Id_Entity
        SRM.Club                      *  MOM.Id_Entity
        SRM.Regatta_Event             *  MOM.Id_Entity
        SRM.Page                      *  MOM.Id_Entity
        SRM.Regatta                      MOM.Id_Entity
        SRM.Regatta_C                 *  MOM.Id_Entity
        SRM.Regatta_H                 *  MOM.Id_Entity
        SRM.Sailor                    *  MOM.Id_Entity
        SRM._Link_n_                     MOM.Id_Entity
        SRM.Link2                        MOM.Id_Entity
        SRM.Boat_in_Regatta           *  MOM.Id_Entity
        SRM.Race_Result               *  MOM.Id_Entity
        SRM.Team                      *  MOM.Id_Entity
        SRM.Crew_Member               *  MOM.Id_Entity
        SRM.Team_has_Boat_in_Regatta  *  MOM.Id_Entity
        PAP.Subject_has_Address          MOM.Id_Entity
        PAP.Subject_has_Email            MOM.Id_Entity
        PAP.Subject_has_Phone            MOM.Id_Entity
        PAP.Subject_has_Url              MOM.Id_Entity
        PAP.Company_has_Url           *  MOM.Id_Entity
        PAP.Person_has_Url            *  MOM.Id_Entity
        PAP.Company_has_Phone         *  MOM.Id_Entity
        PAP.Person_has_Phone          *  MOM.Id_Entity
        PAP.Company_has_Email         *  MOM.Id_Entity
        PAP.Person_has_Email          *  MOM.Id_Entity
        PAP.Company_has_Address       *  MOM.Id_Entity
        PAP.Person_has_Address        *  MOM.Id_Entity
    date [SWP.Object_PN]
        SWP.Object_PN                    SWP.Object_PN
        SWP.Page                      *  SWP.Object_PN
        SWP.Page_Y                    *  SWP.Object_PN
        SWP.Clip_X                    *  SWP.Object_PN
        SWP.Gallery                   *  SWP.Object_PN
        SWP.Referral                  *  SWP.Object_PN
        SRM.Page                      *  SWP.Object_PN
    desc [PAP.Property]
        PAP.Property                     PAP.Property
        PAP.Address                   *  PAP.Address
        PAP.Email                     *  PAP.Email
        PAP.Phone                     *  PAP.Phone
        PAP.Url                       *  PAP.Url
    desc [PAP.Subject_has_Property]
        PAP.Subject_has_Property         PAP.Subject_has_Property
        PAP.Subject_has_Address          PAP.Subject_has_Property
        PAP.Subject_has_Email            PAP.Subject_has_Property
        PAP.Subject_has_Phone            PAP.Subject_has_Property
        PAP.Subject_has_Url              PAP.Subject_has_Property
        PAP.Company_has_Url           *  PAP.Subject_has_Property
        PAP.Person_has_Url            *  PAP.Subject_has_Property
        PAP.Company_has_Phone         *  PAP.Subject_has_Property
        PAP.Person_has_Phone          *  PAP.Subject_has_Property
        PAP.Company_has_Email         *  PAP.Subject_has_Property
        PAP.Person_has_Email          *  PAP.Subject_has_Property
        PAP.Company_has_Address       *  PAP.Subject_has_Property
        PAP.Person_has_Address        *  PAP.Subject_has_Property
    discards [SRM.Regatta]
        SRM.Regatta                      SRM.Regatta
        SRM.Regatta_C                 *  SRM.Regatta
        SRM.Regatta_H                 *  SRM.Regatta
    emails [PAP.Subject]
        PAP.Subject                      PAP.Subject
        PAP.Group                        PAP.Subject
        PAP.Legal_Entity                 PAP.Subject
    events [MOM.Id_Entity]
        MOM.Id_Entity                    MOM.Id_Entity
        MOM.Link                         MOM.Id_Entity
        MOM.Link1                        MOM.Id_Entity
        MOM._Link_n_                     MOM.Id_Entity
        MOM.Link2                        MOM.Id_Entity
        MOM.Object                       MOM.Id_Entity
        PAP.Id_Entity                    MOM.Id_Entity
        PAP.Object                       MOM.Id_Entity
        PAP.Property                     MOM.Id_Entity
        PAP.Address                   *  MOM.Id_Entity
        PAP.Subject                      MOM.Id_Entity
        PAP.Group                        MOM.Id_Entity
        PAP.Legal_Entity                 MOM.Id_Entity
        PAP.Company                   *  MOM.Id_Entity
        PAP.Email                     *  MOM.Id_Entity
        PAP.Phone                     *  MOM.Id_Entity
        PAP.Person                    *  MOM.Id_Entity
        PAP.Url                       *  MOM.Id_Entity
        PAP.Link                         MOM.Id_Entity
        PAP.Link1                        MOM.Id_Entity
        PAP.Address_Position          *  MOM.Id_Entity
        PAP._Link_n_                     MOM.Id_Entity
        PAP.Link2                        MOM.Id_Entity
        PAP.Subject_has_Property         MOM.Id_Entity
        PAP.Person_has_Account        *  MOM.Id_Entity
        EVT.Id_Entity                    MOM.Id_Entity
        EVT.Object                       MOM.Id_Entity
        EVT.Calendar                  *  MOM.Id_Entity
        EVT.Link                         MOM.Id_Entity
        EVT.Link1                        MOM.Id_Entity
        EVT.Event                     *  MOM.Id_Entity
        EVT.Event_occurs              *  MOM.Id_Entity
        EVT._Recurrence_Mixin_           MOM.Id_Entity
        EVT.Recurrence_Spec           *  MOM.Id_Entity
        EVT.Recurrence_Rule           *  MOM.Id_Entity
        SWP.Id_Entity                    MOM.Id_Entity
        SWP.Object                       MOM.Id_Entity
        SWP.Object_PN                    MOM.Id_Entity
        SWP.Page                      *  MOM.Id_Entity
        SWP.Page_Y                    *  MOM.Id_Entity
        SWP.Link                         MOM.Id_Entity
        SWP.Link1                        MOM.Id_Entity
        SWP.Clip_O                    *  MOM.Id_Entity
        SWP.Clip_X                    *  MOM.Id_Entity
        SWP.Gallery                   *  MOM.Id_Entity
        SWP.Picture                   *  MOM.Id_Entity
        SWP.Referral                  *  MOM.Id_Entity
        SRM.Id_Entity                    MOM.Id_Entity
        SRM.Object                       MOM.Id_Entity
        SRM._Boat_Class_                 MOM.Id_Entity
        SRM.Boat_Class                *  MOM.Id_Entity
        SRM.Handicap                  *  MOM.Id_Entity
        SRM.Link                         MOM.Id_Entity
        SRM.Link1                        MOM.Id_Entity
        SRM.Boat                      *  MOM.Id_Entity
        SRM.Club                      *  MOM.Id_Entity
        SRM.Regatta_Event             *  MOM.Id_Entity
        SRM.Page                      *  MOM.Id_Entity
        SRM.Regatta                      MOM.Id_Entity
        SRM.Regatta_C                 *  MOM.Id_Entity
        SRM.Regatta_H                 *  MOM.Id_Entity
        SRM.Sailor                    *  MOM.Id_Entity
        SRM._Link_n_                     MOM.Id_Entity
        SRM.Link2                        MOM.Id_Entity
        SRM.Boat_in_Regatta           *  MOM.Id_Entity
        SRM.Race_Result               *  MOM.Id_Entity
        SRM.Team                      *  MOM.Id_Entity
        SRM.Crew_Member               *  MOM.Id_Entity
        SRM.Team_has_Boat_in_Regatta  *  MOM.Id_Entity
        PAP.Subject_has_Address          MOM.Id_Entity
        PAP.Subject_has_Email            MOM.Id_Entity
        PAP.Subject_has_Phone            MOM.Id_Entity
        PAP.Subject_has_Url              MOM.Id_Entity
        PAP.Company_has_Url           *  MOM.Id_Entity
        PAP.Person_has_Url            *  MOM.Id_Entity
        PAP.Company_has_Phone         *  MOM.Id_Entity
        PAP.Person_has_Phone          *  MOM.Id_Entity
        PAP.Company_has_Email         *  MOM.Id_Entity
        PAP.Person_has_Email          *  MOM.Id_Entity
        PAP.Company_has_Address       *  MOM.Id_Entity
        PAP.Person_has_Address        *  MOM.Id_Entity
    extension [PAP.Subject_has_Phone]
        PAP.Subject_has_Phone            PAP.Subject_has_Phone
        PAP.Company_has_Phone         *  PAP.Subject_has_Phone
        PAP.Person_has_Phone          *  PAP.Subject_has_Phone
    format [SWP.Page_Mixin]
        SWP.Page                      *  SWP.Page_Mixin
        SWP.Page_Y                    *  SWP.Page_Mixin
        SWP.Clip_X                    *  SWP.Page_Mixin
        SRM.Page                      *  SWP.Page_Mixin
    head_line [SWP.Page_Mixin]
        SWP.Page                      *  SWP.Page_Mixin
        SWP.Page_Y                    *  SWP.Page_Mixin
        SWP.Clip_X                    *  SWP.Page_Mixin
        SRM.Page                      *  SWP.Page_Mixin
    hidden [SWP.Object_PN]
        SWP.Object_PN                    SWP.Object_PN
        SWP.Page                      *  SWP.Object_PN
        SWP.Page_Y                    *  SWP.Object_PN
        SWP.Clip_X                    *  SWP.Object_PN
        SWP.Gallery                   *  SWP.Object_PN
        SWP.Referral                  *  SWP.Object_PN
        SRM.Page                      *  SWP.Object_PN
    is_cancelled [SRM.Regatta]
        SRM.Regatta                      SRM.Regatta
        SRM.Regatta_C                 *  SRM.Regatta
        SRM.Regatta_H                 *  SRM.Regatta
    kind [SRM.Regatta]
        SRM.Regatta                      SRM.Regatta
        SRM.Regatta_C                 *  SRM.Regatta
        SRM.Regatta_H                 *  SRM.Regatta
    last_change [MOM.Id_Entity]
        MOM.Id_Entity                    MOM.Id_Entity
        MOM.Link                         MOM.Id_Entity
        MOM.Link1                        MOM.Id_Entity
        MOM._Link_n_                     MOM.Id_Entity
        MOM.Link2                        MOM.Id_Entity
        MOM.Object                       MOM.Id_Entity
        PAP.Id_Entity                    MOM.Id_Entity
        PAP.Object                       MOM.Id_Entity
        PAP.Property                     MOM.Id_Entity
        PAP.Address                   *  MOM.Id_Entity
        PAP.Subject                      MOM.Id_Entity
        PAP.Group                        MOM.Id_Entity
        PAP.Legal_Entity                 MOM.Id_Entity
        PAP.Company                   *  MOM.Id_Entity
        PAP.Email                     *  MOM.Id_Entity
        PAP.Phone                     *  MOM.Id_Entity
        PAP.Person                    *  MOM.Id_Entity
        PAP.Url                       *  MOM.Id_Entity
        PAP.Link                         MOM.Id_Entity
        PAP.Link1                        MOM.Id_Entity
        PAP.Address_Position          *  MOM.Id_Entity
        PAP._Link_n_                     MOM.Id_Entity
        PAP.Link2                        MOM.Id_Entity
        PAP.Subject_has_Property         MOM.Id_Entity
        PAP.Person_has_Account        *  MOM.Id_Entity
        EVT.Id_Entity                    MOM.Id_Entity
        EVT.Object                       MOM.Id_Entity
        EVT.Calendar                  *  MOM.Id_Entity
        EVT.Link                         MOM.Id_Entity
        EVT.Link1                        MOM.Id_Entity
        EVT.Event                     *  MOM.Id_Entity
        EVT.Event_occurs              *  MOM.Id_Entity
        EVT._Recurrence_Mixin_           MOM.Id_Entity
        EVT.Recurrence_Spec           *  MOM.Id_Entity
        EVT.Recurrence_Rule           *  MOM.Id_Entity
        SWP.Id_Entity                    MOM.Id_Entity
        SWP.Object                       MOM.Id_Entity
        SWP.Object_PN                    MOM.Id_Entity
        SWP.Page                      *  MOM.Id_Entity
        SWP.Page_Y                    *  MOM.Id_Entity
        SWP.Link                         MOM.Id_Entity
        SWP.Link1                        MOM.Id_Entity
        SWP.Clip_O                    *  MOM.Id_Entity
        SWP.Clip_X                    *  MOM.Id_Entity
        SWP.Gallery                   *  MOM.Id_Entity
        SWP.Picture                   *  MOM.Id_Entity
        SWP.Referral                  *  MOM.Id_Entity
        SRM.Id_Entity                    MOM.Id_Entity
        SRM.Object                       MOM.Id_Entity
        SRM._Boat_Class_                 MOM.Id_Entity
        SRM.Boat_Class                *  MOM.Id_Entity
        SRM.Handicap                  *  MOM.Id_Entity
        SRM.Link                         MOM.Id_Entity
        SRM.Link1                        MOM.Id_Entity
        SRM.Boat                      *  MOM.Id_Entity
        SRM.Club                      *  MOM.Id_Entity
        SRM.Regatta_Event             *  MOM.Id_Entity
        SRM.Page                      *  MOM.Id_Entity
        SRM.Regatta                      MOM.Id_Entity
        SRM.Regatta_C                 *  MOM.Id_Entity
        SRM.Regatta_H                 *  MOM.Id_Entity
        SRM.Sailor                    *  MOM.Id_Entity
        SRM._Link_n_                     MOM.Id_Entity
        SRM.Link2                        MOM.Id_Entity
        SRM.Boat_in_Regatta           *  MOM.Id_Entity
        SRM.Race_Result               *  MOM.Id_Entity
        SRM.Team                      *  MOM.Id_Entity
        SRM.Crew_Member               *  MOM.Id_Entity
        SRM.Team_has_Boat_in_Regatta  *  MOM.Id_Entity
        PAP.Subject_has_Address          MOM.Id_Entity
        PAP.Subject_has_Email            MOM.Id_Entity
        PAP.Subject_has_Phone            MOM.Id_Entity
        PAP.Subject_has_Url              MOM.Id_Entity
        PAP.Company_has_Url           *  MOM.Id_Entity
        PAP.Person_has_Url            *  MOM.Id_Entity
        PAP.Company_has_Phone         *  MOM.Id_Entity
        PAP.Person_has_Phone          *  MOM.Id_Entity
        PAP.Company_has_Email         *  MOM.Id_Entity
        PAP.Person_has_Email          *  MOM.Id_Entity
        PAP.Company_has_Address       *  MOM.Id_Entity
        PAP.Person_has_Address        *  MOM.Id_Entity
    last_cid [MOM.Id_Entity]
        MOM.Id_Entity                    MOM.Id_Entity
        MOM.Link                         MOM.Id_Entity
        MOM.Link1                        MOM.Id_Entity
        MOM._Link_n_                     MOM.Id_Entity
        MOM.Link2                        MOM.Id_Entity
        MOM.Object                       MOM.Id_Entity
        PAP.Id_Entity                    MOM.Id_Entity
        PAP.Object                       MOM.Id_Entity
        PAP.Property                     MOM.Id_Entity
        PAP.Address                   *  MOM.Id_Entity
        PAP.Subject                      MOM.Id_Entity
        PAP.Group                        MOM.Id_Entity
        PAP.Legal_Entity                 MOM.Id_Entity
        PAP.Company                   *  MOM.Id_Entity
        PAP.Email                     *  MOM.Id_Entity
        PAP.Phone                     *  MOM.Id_Entity
        PAP.Person                    *  MOM.Id_Entity
        PAP.Url                       *  MOM.Id_Entity
        PAP.Link                         MOM.Id_Entity
        PAP.Link1                        MOM.Id_Entity
        PAP.Address_Position          *  MOM.Id_Entity
        PAP._Link_n_                     MOM.Id_Entity
        PAP.Link2                        MOM.Id_Entity
        PAP.Subject_has_Property         MOM.Id_Entity
        PAP.Person_has_Account        *  MOM.Id_Entity
        EVT.Id_Entity                    MOM.Id_Entity
        EVT.Object                       MOM.Id_Entity
        EVT.Calendar                  *  MOM.Id_Entity
        EVT.Link                         MOM.Id_Entity
        EVT.Link1                        MOM.Id_Entity
        EVT.Event                     *  MOM.Id_Entity
        EVT.Event_occurs              *  MOM.Id_Entity
        EVT._Recurrence_Mixin_           MOM.Id_Entity
        EVT.Recurrence_Spec           *  MOM.Id_Entity
        EVT.Recurrence_Rule           *  MOM.Id_Entity
        SWP.Id_Entity                    MOM.Id_Entity
        SWP.Object                       MOM.Id_Entity
        SWP.Object_PN                    MOM.Id_Entity
        SWP.Page                      *  MOM.Id_Entity
        SWP.Page_Y                    *  MOM.Id_Entity
        SWP.Link                         MOM.Id_Entity
        SWP.Link1                        MOM.Id_Entity
        SWP.Clip_O                    *  MOM.Id_Entity
        SWP.Clip_X                    *  MOM.Id_Entity
        SWP.Gallery                   *  MOM.Id_Entity
        SWP.Picture                   *  MOM.Id_Entity
        SWP.Referral                  *  MOM.Id_Entity
        SRM.Id_Entity                    MOM.Id_Entity
        SRM.Object                       MOM.Id_Entity
        SRM._Boat_Class_                 MOM.Id_Entity
        SRM.Boat_Class                *  MOM.Id_Entity
        SRM.Handicap                  *  MOM.Id_Entity
        SRM.Link                         MOM.Id_Entity
        SRM.Link1                        MOM.Id_Entity
        SRM.Boat                      *  MOM.Id_Entity
        SRM.Club                      *  MOM.Id_Entity
        SRM.Regatta_Event             *  MOM.Id_Entity
        SRM.Page                      *  MOM.Id_Entity
        SRM.Regatta                      MOM.Id_Entity
        SRM.Regatta_C                 *  MOM.Id_Entity
        SRM.Regatta_H                 *  MOM.Id_Entity
        SRM.Sailor                    *  MOM.Id_Entity
        SRM._Link_n_                     MOM.Id_Entity
        SRM.Link2                        MOM.Id_Entity
        SRM.Boat_in_Regatta           *  MOM.Id_Entity
        SRM.Race_Result               *  MOM.Id_Entity
        SRM.Team                      *  MOM.Id_Entity
        SRM.Crew_Member               *  MOM.Id_Entity
        SRM.Team_has_Boat_in_Regatta  *  MOM.Id_Entity
        PAP.Subject_has_Address          MOM.Id_Entity
        PAP.Subject_has_Email            MOM.Id_Entity
        PAP.Subject_has_Phone            MOM.Id_Entity
        PAP.Subject_has_Url              MOM.Id_Entity
        PAP.Company_has_Url           *  MOM.Id_Entity
        PAP.Person_has_Url            *  MOM.Id_Entity
        PAP.Company_has_Phone         *  MOM.Id_Entity
        PAP.Person_has_Phone          *  MOM.Id_Entity
        PAP.Company_has_Email         *  MOM.Id_Entity
        PAP.Person_has_Email          *  MOM.Id_Entity
        PAP.Company_has_Address       *  MOM.Id_Entity
        PAP.Person_has_Address        *  MOM.Id_Entity
    left [MOM.Link]
        MOM.Link                         MOM.Link
        MOM.Link1                        MOM.Link1
        MOM._Link_n_                     MOM.Link
        MOM.Link2                        MOM.Link
        PAP.Link                         MOM.Link
        PAP.Link1                        MOM.Link
        PAP.Address_Position          *  PAP.Address_Position
        PAP._Link_n_                     MOM.Link
        PAP.Link2                        MOM.Link
        PAP.Subject_has_Property         PAP.Subject_has_Property
        PAP.Person_has_Account        *  PAP.Person_has_Account
        EVT.Link                         MOM.Link
        EVT.Link1                        MOM.Link
        EVT.Event                     *  EVT.Event
        EVT.Event_occurs              *  EVT.Event_occurs
        EVT._Recurrence_Mixin_           MOM.Link
        EVT.Recurrence_Spec           *  EVT.Recurrence_Spec
        EVT.Recurrence_Rule           *  EVT.Recurrence_Rule
        SWP.Link                         MOM.Link
        SWP.Link1                        MOM.Link
        SWP.Clip_O                    *  SWP.Clip_O
        SWP.Picture                   *  SWP.Picture
        SRM.Link                         MOM.Link
        SRM.Link1                        MOM.Link
        SRM.Boat                      *  SRM.Boat
        SRM.Regatta                      SRM.Regatta
        SRM.Regatta_C                 *  SRM.Regatta
        SRM.Regatta_H                 *  SRM.Regatta
        SRM.Sailor                    *  SRM.Sailor
        SRM._Link_n_                     MOM.Link
        SRM.Link2                        MOM.Link
        SRM.Boat_in_Regatta           *  SRM.Boat_in_Regatta
        SRM.Race_Result               *  SRM.Race_Result
        SRM.Team                      *  SRM.Team
        SRM.Crew_Member               *  SRM.Crew_Member
        SRM.Team_has_Boat_in_Regatta  *  SRM.Team_has_Boat_in_Regatta
        PAP.Subject_has_Address          PAP.Subject_has_Address
        PAP.Subject_has_Email            PAP.Subject_has_Email
        PAP.Subject_has_Phone            PAP.Subject_has_Phone
        PAP.Subject_has_Url              PAP.Subject_has_Url
        PAP.Company_has_Url           *  PAP.Company_has_Url
        PAP.Person_has_Url            *  PAP.Person_has_Url
        PAP.Company_has_Phone         *  PAP.Company_has_Phone
        PAP.Person_has_Phone          *  PAP.Person_has_Phone
        PAP.Company_has_Email         *  PAP.Company_has_Email
        PAP.Person_has_Email          *  PAP.Person_has_Email
        PAP.Company_has_Address       *  PAP.Company_has_Address
        PAP.Person_has_Address        *  PAP.Person_has_Address
    lifetime [PAP.Subject]
        PAP.Subject                      PAP.Subject
        PAP.Group                        PAP.Subject
        PAP.Legal_Entity                 PAP.Subject
        PAP.Company                   *  PAP.Subject
        PAP.Person                    *  PAP.Subject
    name [PAP.Group]
        PAP.Group                        PAP.Group
        PAP.Legal_Entity                 PAP.Legal_Entity
        PAP.Company                   *  PAP.Company
    name [SRM._Boat_Class_]
        SRM._Boat_Class_                 SRM._Boat_Class_
        SRM.Boat_Class                *  SRM.Boat_Class
        SRM.Handicap                  *  SRM.Handicap
    perma_name [SRM.Regatta]
        SRM.Regatta                      SRM.Regatta
        SRM.Regatta_C                 *  SRM.Regatta
        SRM.Regatta_H                 *  SRM.Regatta
    perma_name [SWP.Object_PN]
        SWP.Object_PN                    SWP.Object_PN
        SWP.Page                      *  SWP.Object_PN
        SWP.Page_Y                    *  SWP.Object_PN
        SWP.Clip_X                    *  SWP.Object_PN
        SWP.Gallery                   *  SWP.Object_PN
        SWP.Referral                  *  SWP.Object_PN
        SRM.Page                      *  SWP.Object_PN
    phones [PAP.Subject]
        PAP.Subject                      PAP.Subject
        PAP.Group                        PAP.Subject
        PAP.Legal_Entity                 PAP.Subject
    pid [MOM.Id_Entity]
        MOM.Id_Entity                    MOM.Id_Entity
        MOM.Link                         MOM.Id_Entity
        MOM.Link1                        MOM.Id_Entity
        MOM._Link_n_                     MOM.Id_Entity
        MOM.Link2                        MOM.Id_Entity
        MOM.Object                       MOM.Id_Entity
        PAP.Id_Entity                    MOM.Id_Entity
        PAP.Object                       MOM.Id_Entity
        PAP.Property                     MOM.Id_Entity
        PAP.Address                   *  MOM.Id_Entity
        PAP.Subject                      MOM.Id_Entity
        PAP.Group                        MOM.Id_Entity
        PAP.Legal_Entity                 MOM.Id_Entity
        PAP.Company                   *  MOM.Id_Entity
        PAP.Email                     *  MOM.Id_Entity
        PAP.Phone                     *  MOM.Id_Entity
        PAP.Person                    *  MOM.Id_Entity
        PAP.Url                       *  MOM.Id_Entity
        PAP.Link                         MOM.Id_Entity
        PAP.Link1                        MOM.Id_Entity
        PAP.Address_Position          *  MOM.Id_Entity
        PAP._Link_n_                     MOM.Id_Entity
        PAP.Link2                        MOM.Id_Entity
        PAP.Subject_has_Property         MOM.Id_Entity
        PAP.Person_has_Account        *  MOM.Id_Entity
        EVT.Id_Entity                    MOM.Id_Entity
        EVT.Object                       MOM.Id_Entity
        EVT.Calendar                  *  MOM.Id_Entity
        EVT.Link                         MOM.Id_Entity
        EVT.Link1                        MOM.Id_Entity
        EVT.Event                     *  MOM.Id_Entity
        EVT.Event_occurs              *  MOM.Id_Entity
        EVT._Recurrence_Mixin_           MOM.Id_Entity
        EVT.Recurrence_Spec           *  MOM.Id_Entity
        EVT.Recurrence_Rule           *  MOM.Id_Entity
        SWP.Id_Entity                    MOM.Id_Entity
        SWP.Object                       MOM.Id_Entity
        SWP.Object_PN                    MOM.Id_Entity
        SWP.Page                      *  MOM.Id_Entity
        SWP.Page_Y                    *  MOM.Id_Entity
        SWP.Link                         MOM.Id_Entity
        SWP.Link1                        MOM.Id_Entity
        SWP.Clip_O                    *  MOM.Id_Entity
        SWP.Clip_X                    *  MOM.Id_Entity
        SWP.Gallery                   *  MOM.Id_Entity
        SWP.Picture                   *  MOM.Id_Entity
        SWP.Referral                  *  MOM.Id_Entity
        SRM.Id_Entity                    MOM.Id_Entity
        SRM.Object                       MOM.Id_Entity
        SRM._Boat_Class_                 MOM.Id_Entity
        SRM.Boat_Class                *  MOM.Id_Entity
        SRM.Handicap                  *  MOM.Id_Entity
        SRM.Link                         MOM.Id_Entity
        SRM.Link1                        MOM.Id_Entity
        SRM.Boat                      *  MOM.Id_Entity
        SRM.Club                      *  MOM.Id_Entity
        SRM.Regatta_Event             *  MOM.Id_Entity
        SRM.Page                      *  MOM.Id_Entity
        SRM.Regatta                      MOM.Id_Entity
        SRM.Regatta_C                 *  MOM.Id_Entity
        SRM.Regatta_H                 *  MOM.Id_Entity
        SRM.Sailor                    *  MOM.Id_Entity
        SRM._Link_n_                     MOM.Id_Entity
        SRM.Link2                        MOM.Id_Entity
        SRM.Boat_in_Regatta           *  MOM.Id_Entity
        SRM.Race_Result               *  MOM.Id_Entity
        SRM.Team                      *  MOM.Id_Entity
        SRM.Crew_Member               *  MOM.Id_Entity
        SRM.Team_has_Boat_in_Regatta  *  MOM.Id_Entity
        PAP.Subject_has_Address          MOM.Id_Entity
        PAP.Subject_has_Email            MOM.Id_Entity
        PAP.Subject_has_Phone            MOM.Id_Entity
        PAP.Subject_has_Url              MOM.Id_Entity
        PAP.Company_has_Url           *  MOM.Id_Entity
        PAP.Person_has_Url            *  MOM.Id_Entity
        PAP.Company_has_Phone         *  MOM.Id_Entity
        PAP.Person_has_Phone          *  MOM.Id_Entity
        PAP.Company_has_Email         *  MOM.Id_Entity
        PAP.Person_has_Email          *  MOM.Id_Entity
        PAP.Company_has_Address       *  MOM.Id_Entity
        PAP.Person_has_Address        *  MOM.Id_Entity
    prio [SWP.Object_PN]
        SWP.Object_PN                    SWP.Object_PN
        SWP.Page                      *  SWP.Object_PN
        SWP.Page_Y                    *  SWP.Object_PN
        SWP.Clip_X                    *  SWP.Object_PN
        SWP.Gallery                   *  SWP.Object_PN
        SWP.Referral                  *  SWP.Object_PN
        SRM.Page                      *  SWP.Object_PN
    races [SRM.Regatta]
        SRM.Regatta                      SRM.Regatta
        SRM.Regatta_C                 *  SRM.Regatta
        SRM.Regatta_H                 *  SRM.Regatta
    races_counted [SRM.Regatta]
        SRM.Regatta                      SRM.Regatta
        SRM.Regatta_C                 *  SRM.Regatta
        SRM.Regatta_H                 *  SRM.Regatta
    result [SRM.Regatta]
        SRM.Regatta                      SRM.Regatta
        SRM.Regatta_C                 *  SRM.Regatta
        SRM.Regatta_H                 *  SRM.Regatta
    right [MOM._Link_n_]
        MOM._Link_n_                     MOM._Link_n_
        MOM.Link2                        MOM._Link_n_
        PAP._Link_n_                     MOM._Link_n_
        PAP.Link2                        MOM._Link_n_
        PAP.Subject_has_Property         PAP.Subject_has_Property
        PAP.Person_has_Account        *  PAP.Person_has_Account
        SRM._Link_n_                     MOM._Link_n_
        SRM.Link2                        MOM._Link_n_
        SRM.Boat_in_Regatta           *  SRM.Boat_in_Regatta
        SRM.Crew_Member               *  SRM.Crew_Member
        SRM.Team_has_Boat_in_Regatta  *  SRM.Team_has_Boat_in_Regatta
        PAP.Subject_has_Address          PAP.Subject_has_Address
        PAP.Subject_has_Email            PAP.Subject_has_Email
        PAP.Subject_has_Phone            PAP.Subject_has_Phone
        PAP.Subject_has_Url              PAP.Subject_has_Url
        PAP.Company_has_Url           *  PAP.Company_has_Url
        PAP.Person_has_Url            *  PAP.Person_has_Url
        PAP.Company_has_Phone         *  PAP.Company_has_Phone
        PAP.Person_has_Phone          *  PAP.Person_has_Phone
        PAP.Company_has_Email         *  PAP.Company_has_Email
        PAP.Person_has_Email          *  PAP.Person_has_Email
        PAP.Company_has_Address       *  PAP.Company_has_Address
        PAP.Person_has_Address        *  PAP.Person_has_Address
    short_name [PAP.Group]
        PAP.Group                        PAP.Group
        PAP.Legal_Entity                 PAP.Legal_Entity
        PAP.Company                   *  PAP.Company
    short_title [SWP.Object_PN]
        SWP.Object_PN                    SWP.Object_PN
        SWP.Page                      *  SWP.Object_PN
        SWP.Page_Y                    *  SWP.Object_PN
        SWP.Clip_X                    *  SWP.Object_PN
        SWP.Gallery                   *  SWP.Object_PN
        SWP.Referral                  *  SWP.Object_PN
    starters_rl [SRM.Regatta]
        SRM.Regatta                      SRM.Regatta
        SRM.Regatta_C                 *  SRM.Regatta
        SRM.Regatta_H                 *  SRM.Regatta
    text [SWP.Page_Mixin]
        SWP.Page                      *  SWP.Page_Mixin
        SWP.Page_Y                    *  SWP.Page_Mixin
        SWP.Clip_X                    *  SWP.Clip_X
        SRM.Page                      *  SWP.Page_Mixin
    title [SWP.Object_PN]
        SWP.Object_PN                    SWP.Object_PN
        SWP.Page                      *  SWP.Object_PN
        SWP.Page_Y                    *  SWP.Object_PN
        SWP.Clip_X                    *  SWP.Clip_X
        SWP.Gallery                   *  SWP.Object_PN
        SWP.Referral                  *  SWP.Object_PN
    type_name [MOM.Id_Entity]
        MOM.Id_Entity                    MOM.Id_Entity
        MOM.Link                         MOM.Id_Entity
        MOM.Link1                        MOM.Id_Entity
        MOM._Link_n_                     MOM.Id_Entity
        MOM.Link2                        MOM.Id_Entity
        MOM.Object                       MOM.Id_Entity
        PAP.Id_Entity                    MOM.Id_Entity
        PAP.Object                       MOM.Id_Entity
        PAP.Property                     MOM.Id_Entity
        PAP.Address                   *  MOM.Id_Entity
        PAP.Subject                      MOM.Id_Entity
        PAP.Group                        MOM.Id_Entity
        PAP.Legal_Entity                 MOM.Id_Entity
        PAP.Company                   *  MOM.Id_Entity
        PAP.Email                     *  MOM.Id_Entity
        PAP.Phone                     *  MOM.Id_Entity
        PAP.Person                    *  MOM.Id_Entity
        PAP.Url                       *  MOM.Id_Entity
        PAP.Link                         MOM.Id_Entity
        PAP.Link1                        MOM.Id_Entity
        PAP.Address_Position          *  MOM.Id_Entity
        PAP._Link_n_                     MOM.Id_Entity
        PAP.Link2                        MOM.Id_Entity
        PAP.Subject_has_Property         MOM.Id_Entity
        PAP.Person_has_Account        *  MOM.Id_Entity
        EVT.Id_Entity                    MOM.Id_Entity
        EVT.Object                       MOM.Id_Entity
        EVT.Calendar                  *  MOM.Id_Entity
        EVT.Link                         MOM.Id_Entity
        EVT.Link1                        MOM.Id_Entity
        EVT.Event                     *  MOM.Id_Entity
        EVT.Event_occurs              *  MOM.Id_Entity
        EVT._Recurrence_Mixin_           MOM.Id_Entity
        EVT.Recurrence_Spec           *  MOM.Id_Entity
        EVT.Recurrence_Rule           *  MOM.Id_Entity
        SWP.Id_Entity                    MOM.Id_Entity
        SWP.Object                       MOM.Id_Entity
        SWP.Object_PN                    MOM.Id_Entity
        SWP.Page                      *  MOM.Id_Entity
        SWP.Page_Y                    *  MOM.Id_Entity
        SWP.Link                         MOM.Id_Entity
        SWP.Link1                        MOM.Id_Entity
        SWP.Clip_O                    *  MOM.Id_Entity
        SWP.Clip_X                    *  MOM.Id_Entity
        SWP.Gallery                   *  MOM.Id_Entity
        SWP.Picture                   *  MOM.Id_Entity
        SWP.Referral                  *  MOM.Id_Entity
        SRM.Id_Entity                    MOM.Id_Entity
        SRM.Object                       MOM.Id_Entity
        SRM._Boat_Class_                 MOM.Id_Entity
        SRM.Boat_Class                *  MOM.Id_Entity
        SRM.Handicap                  *  MOM.Id_Entity
        SRM.Link                         MOM.Id_Entity
        SRM.Link1                        MOM.Id_Entity
        SRM.Boat                      *  MOM.Id_Entity
        SRM.Club                      *  MOM.Id_Entity
        SRM.Regatta_Event             *  MOM.Id_Entity
        SRM.Page                      *  MOM.Id_Entity
        SRM.Regatta                      MOM.Id_Entity
        SRM.Regatta_C                 *  MOM.Id_Entity
        SRM.Regatta_H                 *  MOM.Id_Entity
        SRM.Sailor                    *  MOM.Id_Entity
        SRM._Link_n_                     MOM.Id_Entity
        SRM.Link2                        MOM.Id_Entity
        SRM.Boat_in_Regatta           *  MOM.Id_Entity
        SRM.Race_Result               *  MOM.Id_Entity
        SRM.Team                      *  MOM.Id_Entity
        SRM.Crew_Member               *  MOM.Id_Entity
        SRM.Team_has_Boat_in_Regatta  *  MOM.Id_Entity
        PAP.Subject_has_Address          MOM.Id_Entity
        PAP.Subject_has_Email            MOM.Id_Entity
        PAP.Subject_has_Phone            MOM.Id_Entity
        PAP.Subject_has_Url              MOM.Id_Entity
        PAP.Company_has_Url           *  MOM.Id_Entity
        PAP.Person_has_Url            *  MOM.Id_Entity
        PAP.Company_has_Phone         *  MOM.Id_Entity
        PAP.Person_has_Phone          *  MOM.Id_Entity
        PAP.Company_has_Email         *  MOM.Id_Entity
        PAP.Person_has_Email          *  MOM.Id_Entity
        PAP.Company_has_Address       *  MOM.Id_Entity
        PAP.Person_has_Address        *  MOM.Id_Entity
    urls [PAP.Subject]
        PAP.Subject                      PAP.Subject
        PAP.Group                        PAP.Subject
        PAP.Legal_Entity                 PAP.Subject
    year [SRM.Regatta]
        SRM.Regatta                      SRM.Regatta
        SRM.Regatta_C                 *  SRM.Regatta
        SRM.Regatta_H                 *  SRM.Regatta


    >>> name, DT = ("left", "MOM.Link")
    >>> xs       = a_map [name, DT]
    >>> for kind, ET in sorted (xs, key = lambda x : x [1].i_rank) : ### left
    ...     print ("%%-30s %%-30s %%s" %% (ET.type_name, kind.attr.DET, kind.attr.DET_Base))
    MOM.Link                       MOM.Link                       None
    MOM.Link1                      MOM.Link1                      MOM.Link
    MOM._Link_n_                   MOM.Link                       None
    MOM.Link2                      MOM.Link                       None
    PAP.Link                       MOM.Link                       None
    PAP.Link1                      MOM.Link                       None
    PAP.Address_Position           PAP.Address_Position           MOM.Link1
    PAP._Link_n_                   MOM.Link                       None
    PAP.Link2                      MOM.Link                       None
    PAP.Subject_has_Property       PAP.Subject_has_Property       MOM.Link
    PAP.Person_has_Account         PAP.Person_has_Account         MOM.Link
    EVT.Link                       MOM.Link                       None
    EVT.Link1                      MOM.Link                       None
    EVT.Event                      EVT.Event                      MOM.Link1
    EVT.Event_occurs               EVT.Event_occurs               MOM.Link1
    EVT._Recurrence_Mixin_         MOM.Link                       None
    EVT.Recurrence_Spec            EVT.Recurrence_Spec            MOM.Link1
    EVT.Recurrence_Rule            EVT.Recurrence_Rule            MOM.Link1
    SWP.Link                       MOM.Link                       None
    SWP.Link1                      MOM.Link                       None
    SWP.Clip_O                     SWP.Clip_O                     MOM.Link1
    SWP.Picture                    SWP.Picture                    MOM.Link1
    SRM.Link                       MOM.Link                       None
    SRM.Link1                      MOM.Link                       None
    SRM.Boat                       SRM.Boat                       MOM.Link1
    SRM.Regatta                    SRM.Regatta                    MOM.Link1
    SRM.Regatta_C                  SRM.Regatta                    MOM.Link1
    SRM.Regatta_H                  SRM.Regatta                    MOM.Link1
    SRM.Sailor                     SRM.Sailor                     MOM.Link1
    SRM._Link_n_                   MOM.Link                       None
    SRM.Link2                      MOM.Link                       None
    SRM.Boat_in_Regatta            SRM.Boat_in_Regatta            MOM.Link
    SRM.Race_Result                SRM.Race_Result                MOM.Link1
    SRM.Team                       SRM.Team                       MOM.Link1
    SRM.Crew_Member                SRM.Crew_Member                MOM.Link
    SRM.Team_has_Boat_in_Regatta   SRM.Team_has_Boat_in_Regatta   MOM.Link
    PAP.Subject_has_Address        PAP.Subject_has_Property       MOM.Link
    PAP.Subject_has_Email          PAP.Subject_has_Property       MOM.Link
    PAP.Subject_has_Phone          PAP.Subject_has_Property       MOM.Link
    PAP.Subject_has_Url            PAP.Subject_has_Property       MOM.Link
    PAP.Company_has_Url            PAP.Company_has_Url            PAP.Subject_has_Property
    PAP.Person_has_Url             PAP.Person_has_Url             PAP.Subject_has_Property
    PAP.Company_has_Phone          PAP.Company_has_Phone          PAP.Subject_has_Property
    PAP.Person_has_Phone           PAP.Person_has_Phone           PAP.Subject_has_Property
    PAP.Company_has_Email          PAP.Company_has_Email          PAP.Subject_has_Property
    PAP.Person_has_Email           PAP.Person_has_Email           PAP.Subject_has_Property
    PAP.Company_has_Address        PAP.Company_has_Address        PAP.Subject_has_Property
    PAP.Person_has_Address         PAP.Person_has_Address         PAP.Subject_has_Property

    >>> name, DT = ("left", "MOM.Link")
    >>> xs       = a_map [name, DT]
    >>> for ak, ET in sorted (xs, key = lambda x : x [1].i_rank) : ### left, no Link1
    ...   if len (ET.Roles) > 1 :
    ...     db = ak.det_base.type_name if ak.det_base else None
    ...     print ("%%-30s %%-30s %%s" %% (ET.type_name, ak.e_type.type_name, db))
    MOM._Link_n_                   MOM.Link                       None
    MOM.Link2                      MOM.Link                       None
    PAP._Link_n_                   MOM.Link                       None
    PAP.Link2                      MOM.Link                       None
    PAP.Subject_has_Property       PAP.Subject_has_Property       MOM.Link
    PAP.Person_has_Account         PAP.Person_has_Account         MOM.Link
    SRM._Link_n_                   MOM.Link                       None
    SRM.Link2                      MOM.Link                       None
    SRM.Boat_in_Regatta            SRM.Boat_in_Regatta            MOM.Link
    SRM.Crew_Member                SRM.Crew_Member                MOM.Link
    SRM.Team_has_Boat_in_Regatta   SRM.Team_has_Boat_in_Regatta   MOM.Link
    PAP.Subject_has_Address        PAP.Subject_has_Address        MOM.Link
    PAP.Subject_has_Email          PAP.Subject_has_Email          MOM.Link
    PAP.Subject_has_Phone          PAP.Subject_has_Phone          MOM.Link
    PAP.Subject_has_Url            PAP.Subject_has_Url            MOM.Link
    PAP.Company_has_Url            PAP.Company_has_Url            PAP.Subject_has_Property
    PAP.Person_has_Url             PAP.Person_has_Url             PAP.Subject_has_Property
    PAP.Company_has_Phone          PAP.Company_has_Phone          PAP.Subject_has_Property
    PAP.Person_has_Phone           PAP.Person_has_Phone           PAP.Subject_has_Property
    PAP.Company_has_Email          PAP.Company_has_Email          PAP.Subject_has_Property
    PAP.Person_has_Email           PAP.Person_has_Email           PAP.Subject_has_Property
    PAP.Company_has_Address        PAP.Company_has_Address        PAP.Subject_has_Property
    PAP.Person_has_Address         PAP.Person_has_Address         PAP.Subject_has_Property

    >>> name, DT = ("right", "MOM._Link_n_")
    >>> xs       = a_map [name, DT]
    >>> for ak, ET in sorted (xs, key = lambda x : x [1].i_rank) : ### right
    ...     db = ak.det_base.type_name if ak.det_base else None
    ...     print ("%%-30s %%-30s %%s" %% (ET.type_name, ak.e_type.type_name, db))
    MOM._Link_n_                   MOM._Link_n_                   None
    MOM.Link2                      MOM._Link_n_                   None
    PAP._Link_n_                   MOM._Link_n_                   None
    PAP.Link2                      MOM._Link_n_                   None
    PAP.Subject_has_Property       PAP.Subject_has_Property       MOM._Link_n_
    PAP.Person_has_Account         PAP.Person_has_Account         MOM._Link_n_
    SRM._Link_n_                   MOM._Link_n_                   None
    SRM.Link2                      MOM._Link_n_                   None
    SRM.Boat_in_Regatta            SRM.Boat_in_Regatta            MOM._Link_n_
    SRM.Crew_Member                SRM.Crew_Member                MOM._Link_n_
    SRM.Team_has_Boat_in_Regatta   SRM.Team_has_Boat_in_Regatta   MOM._Link_n_
    PAP.Subject_has_Address        PAP.Subject_has_Address        PAP.Subject_has_Property
    PAP.Subject_has_Email          PAP.Subject_has_Email          PAP.Subject_has_Property
    PAP.Subject_has_Phone          PAP.Subject_has_Phone          PAP.Subject_has_Property
    PAP.Subject_has_Url            PAP.Subject_has_Url            PAP.Subject_has_Property
    PAP.Company_has_Url            PAP.Company_has_Url            PAP.Subject_has_Property
    PAP.Person_has_Url             PAP.Person_has_Url             PAP.Subject_has_Property
    PAP.Company_has_Phone          PAP.Company_has_Phone          PAP.Subject_has_Property
    PAP.Person_has_Phone           PAP.Person_has_Phone           PAP.Subject_has_Property
    PAP.Company_has_Email          PAP.Company_has_Email          PAP.Subject_has_Property
    PAP.Person_has_Email           PAP.Person_has_Email           PAP.Subject_has_Property
    PAP.Company_has_Address        PAP.Company_has_Address        PAP.Subject_has_Property
    PAP.Person_has_Address         PAP.Person_has_Address         PAP.Subject_has_Property

    >>> name, DT = ("left", "MOM.Link")
    >>> xs       = a_map [name, DT]
    >>> for ak, ET in sorted (xs, key = lambda x : x [1].i_rank) : ### left
    ...     flag = "*" if not ET.is_partial else ""
    ...     rt = ak.E_Type.type_name if ak.E_Type else None
    ...     print ("%%-30s%%-2s %%s" %% (ET.type_name, flag, rt))
    MOM.Link                         None
    MOM.Link1                        None
    MOM._Link_n_                     None
    MOM.Link2                        None
    PAP.Link                         None
    PAP.Link1                        None
    PAP.Address_Position          *  PAP.Address
    PAP._Link_n_                     None
    PAP.Link2                        None
    PAP.Subject_has_Property         PAP.Subject
    PAP.Person_has_Account        *  PAP.Person
    EVT.Link                         None
    EVT.Link1                        None
    EVT.Event                     *  MOM.Id_Entity
    EVT.Event_occurs              *  EVT.Event
    EVT._Recurrence_Mixin_           None
    EVT.Recurrence_Spec           *  EVT.Event
    EVT.Recurrence_Rule           *  EVT.Recurrence_Spec
    SWP.Link                         None
    SWP.Link1                        None
    SWP.Clip_O                    *  SWP.Object_PN
    SWP.Picture                   *  SWP.Gallery
    SRM.Link                         None
    SRM.Link1                        None
    SRM.Boat                      *  SRM.Boat_Class
    SRM.Regatta                      SRM.Regatta_Event
    SRM.Regatta_C                 *  SRM.Regatta_Event
    SRM.Regatta_H                 *  SRM.Regatta_Event
    SRM.Sailor                    *  PAP.Person
    SRM._Link_n_                     None
    SRM.Link2                        None
    SRM.Boat_in_Regatta           *  SRM.Boat
    SRM.Race_Result               *  SRM.Boat_in_Regatta
    SRM.Team                      *  SRM.Regatta_C
    SRM.Crew_Member               *  SRM.Boat_in_Regatta
    SRM.Team_has_Boat_in_Regatta  *  SRM.Team
    PAP.Subject_has_Address          PAP.Subject
    PAP.Subject_has_Email            PAP.Subject
    PAP.Subject_has_Phone            PAP.Subject
    PAP.Subject_has_Url              PAP.Subject
    PAP.Company_has_Url           *  PAP.Company
    PAP.Person_has_Url            *  PAP.Person
    PAP.Company_has_Phone         *  PAP.Company
    PAP.Person_has_Phone          *  PAP.Person
    PAP.Company_has_Email         *  PAP.Company
    PAP.Person_has_Email          *  PAP.Person
    PAP.Company_has_Address       *  PAP.Company
    PAP.Person_has_Address        *  PAP.Person

    >>> name, DT = ("right", "MOM._Link_n_")
    >>> xs       = a_map [name, DT]
    >>> for ak, ET in sorted (xs, key = lambda x : x [1].i_rank) : ### right
    ...     flag = "*" if not ET.is_partial else ""
    ...     rt = ak.E_Type.type_name if ak.E_Type else None
    ...     print ("%%-30s%%-2s %%s" %% (ET.type_name, flag, rt))
    MOM._Link_n_                     None
    MOM.Link2                        None
    PAP._Link_n_                     None
    PAP.Link2                        None
    PAP.Subject_has_Property         PAP.Property
    PAP.Person_has_Account        *  Auth.Account
    SRM._Link_n_                     None
    SRM.Link2                        None
    SRM.Boat_in_Regatta           *  SRM.Regatta
    SRM.Crew_Member               *  SRM.Sailor
    SRM.Team_has_Boat_in_Regatta  *  SRM.Boat_in_Regatta
    PAP.Subject_has_Address          PAP.Address
    PAP.Subject_has_Email            PAP.Email
    PAP.Subject_has_Phone            PAP.Phone
    PAP.Subject_has_Url              PAP.Url
    PAP.Company_has_Url           *  PAP.Url
    PAP.Person_has_Url            *  PAP.Url
    PAP.Company_has_Phone         *  PAP.Phone
    PAP.Person_has_Phone          *  PAP.Phone
    PAP.Company_has_Email         *  PAP.Email
    PAP.Person_has_Email          *  PAP.Email
    PAP.Company_has_Address       *  PAP.Address
    PAP.Person_has_Address        *  PAP.Address

    >>> name, DT = ("left", "MOM.Link")
    >>> xs       = a_map [name, DT]
    >>> for i, (kind, ET) in enumerate (sorted (xs, key = lambda x : x [1].i_rank)) : ### left
    ...   if not i :
    ...     print ("%%-30s %%-30s %%-30s %%s" %% ("E_Type", "det", "det_base", "attr.E_Type"))
    ...     print ("=" * 110)
    ...   if len (ET.Roles) > 1 :
    ...     det = kind.attr.det.type_name
    ...     deb = kind.attr.det_base
    ...     db  = deb.type_name if deb else "<Undef/value>"
    ...     at  = kind.E_Type.type_name if kind.E_Type else "<Undef/value>"
    ...     print ("%%-30s %%-30s %%-30s %%s" %% (ET.type_name, det, db, at))
    E_Type                         det                            det_base                       attr.E_Type
    ==============================================================================================================
    MOM._Link_n_                   MOM.Link                       <Undef/value>                  <Undef/value>
    MOM.Link2                      MOM.Link                       <Undef/value>                  <Undef/value>
    PAP._Link_n_                   MOM.Link                       <Undef/value>                  <Undef/value>
    PAP.Link2                      MOM.Link                       <Undef/value>                  <Undef/value>
    PAP.Subject_has_Property       PAP.Subject_has_Property       MOM.Link                       PAP.Subject
    PAP.Person_has_Account         PAP.Person_has_Account         MOM.Link                       PAP.Person
    SRM._Link_n_                   MOM.Link                       <Undef/value>                  <Undef/value>
    SRM.Link2                      MOM.Link                       <Undef/value>                  <Undef/value>
    SRM.Boat_in_Regatta            SRM.Boat_in_Regatta            MOM.Link                       SRM.Boat
    SRM.Crew_Member                SRM.Crew_Member                MOM.Link                       SRM.Boat_in_Regatta
    SRM.Team_has_Boat_in_Regatta   SRM.Team_has_Boat_in_Regatta   MOM.Link                       SRM.Team
    PAP.Subject_has_Address        PAP.Subject_has_Property       MOM.Link                       PAP.Subject
    PAP.Subject_has_Email          PAP.Subject_has_Property       MOM.Link                       PAP.Subject
    PAP.Subject_has_Phone          PAP.Subject_has_Property       MOM.Link                       PAP.Subject
    PAP.Subject_has_Url            PAP.Subject_has_Property       MOM.Link                       PAP.Subject
    PAP.Company_has_Url            PAP.Company_has_Url            PAP.Subject_has_Property       PAP.Company
    PAP.Person_has_Url             PAP.Person_has_Url             PAP.Subject_has_Property       PAP.Person
    PAP.Company_has_Phone          PAP.Company_has_Phone          PAP.Subject_has_Property       PAP.Company
    PAP.Person_has_Phone           PAP.Person_has_Phone           PAP.Subject_has_Property       PAP.Person
    PAP.Company_has_Email          PAP.Company_has_Email          PAP.Subject_has_Property       PAP.Company
    PAP.Person_has_Email           PAP.Person_has_Email           PAP.Subject_has_Property       PAP.Person
    PAP.Company_has_Address        PAP.Company_has_Address        PAP.Subject_has_Property       PAP.Company
    PAP.Person_has_Address         PAP.Person_has_Address         PAP.Subject_has_Property       PAP.Person

    >>> name, DT = ("right", "MOM._Link_n_")
    >>> xs       = a_map [name, DT]
    >>> for i, (kind, ET) in enumerate (sorted (xs, key = lambda x : x [1].i_rank)) : ### right
    ...     if not i :
    ...         print ("%%-30s %%-30s %%-30s %%s" %% ("E_Type", "det", "det_base", "attr.E_Type"))
    ...         print ("=" * 110)
    ...     det = kind.attr.det.type_name
    ...     deb = kind.attr.det_base
    ...     db  = deb.type_name if deb else "<Undef/value>"
    ...     at  = kind.E_Type.type_name if kind.E_Type else "<Undef/value>"
    ...     print ("%%-30s %%-30s %%-30s %%s" %% (ET.type_name, det, db, at))
    E_Type                         det                            det_base                       attr.E_Type
    ==============================================================================================================
    MOM._Link_n_                   MOM._Link_n_                   <Undef/value>                  <Undef/value>
    MOM.Link2                      MOM._Link_n_                   <Undef/value>                  <Undef/value>
    PAP._Link_n_                   MOM._Link_n_                   <Undef/value>                  <Undef/value>
    PAP.Link2                      MOM._Link_n_                   <Undef/value>                  <Undef/value>
    PAP.Subject_has_Property       PAP.Subject_has_Property       MOM._Link_n_                   PAP.Property
    PAP.Person_has_Account         PAP.Person_has_Account         MOM._Link_n_                   Auth.Account
    SRM._Link_n_                   MOM._Link_n_                   <Undef/value>                  <Undef/value>
    SRM.Link2                      MOM._Link_n_                   <Undef/value>                  <Undef/value>
    SRM.Boat_in_Regatta            SRM.Boat_in_Regatta            MOM._Link_n_                   SRM.Regatta
    SRM.Crew_Member                SRM.Crew_Member                MOM._Link_n_                   SRM.Sailor
    SRM.Team_has_Boat_in_Regatta   SRM.Team_has_Boat_in_Regatta   MOM._Link_n_                   SRM.Boat_in_Regatta
    PAP.Subject_has_Address        PAP.Subject_has_Address        PAP.Subject_has_Property       PAP.Address
    PAP.Subject_has_Email          PAP.Subject_has_Email          PAP.Subject_has_Property       PAP.Email
    PAP.Subject_has_Phone          PAP.Subject_has_Phone          PAP.Subject_has_Property       PAP.Phone
    PAP.Subject_has_Url            PAP.Subject_has_Url            PAP.Subject_has_Property       PAP.Url
    PAP.Company_has_Url            PAP.Subject_has_Url            PAP.Subject_has_Property       PAP.Url
    PAP.Person_has_Url             PAP.Subject_has_Url            PAP.Subject_has_Property       PAP.Url
    PAP.Company_has_Phone          PAP.Subject_has_Phone          PAP.Subject_has_Property       PAP.Phone
    PAP.Person_has_Phone           PAP.Subject_has_Phone          PAP.Subject_has_Property       PAP.Phone
    PAP.Company_has_Email          PAP.Subject_has_Email          PAP.Subject_has_Property       PAP.Email
    PAP.Person_has_Email           PAP.Subject_has_Email          PAP.Subject_has_Property       PAP.Email
    PAP.Company_has_Address        PAP.Subject_has_Address        PAP.Subject_has_Property       PAP.Address
    PAP.Person_has_Address         PAP.Subject_has_Address        PAP.Subject_has_Property       PAP.Address

    >>> name, DT = ("left", "MOM.Link")
    >>> xs       = a_map [name, DT]
    >>> for i, (kind, ET) in enumerate (sorted (xs, key = lambda x : x [1].i_rank)) : ### left
    ...   if not i :
    ...     print ("%%-30s %%-30s %%s" %% ("E_Type", "det", "det_kind"))
    ...     print ("=" * 80)
    ...   if len (ET.Roles) > 1 :
    ...     det = kind.attr.det.type_name
    ...     dek = kind.attr.det_kind
    ...     print ("%%-30s %%-30s %%s" %% (ET.type_name, det, dek))
    E_Type                         det                            det_kind
    ================================================================================
    MOM._Link_n_                   MOM.Link                       Left `left`
    MOM.Link2                      MOM.Link                       Left `left`
    PAP._Link_n_                   MOM.Link                       Left `left`
    PAP.Link2                      MOM.Link                       Left `left`
    PAP.Subject_has_Property       PAP.Subject_has_Property       Subject `left`
    PAP.Person_has_Account         PAP.Person_has_Account         Person `left`
    SRM._Link_n_                   MOM.Link                       Left `left`
    SRM.Link2                      MOM.Link                       Left `left`
    SRM.Boat_in_Regatta            SRM.Boat_in_Regatta            Boat `left`
    SRM.Crew_Member                SRM.Crew_Member                Boat_in_Regatta `left`
    SRM.Team_has_Boat_in_Regatta   SRM.Team_has_Boat_in_Regatta   Team `left`
    PAP.Subject_has_Address        PAP.Subject_has_Property       Subject `left`
    PAP.Subject_has_Email          PAP.Subject_has_Property       Subject `left`
    PAP.Subject_has_Phone          PAP.Subject_has_Property       Subject `left`
    PAP.Subject_has_Url            PAP.Subject_has_Property       Subject `left`
    PAP.Company_has_Url            PAP.Company_has_Url            Company `left`
    PAP.Person_has_Url             PAP.Person_has_Url             Person `left`
    PAP.Company_has_Phone          PAP.Company_has_Phone          Company `left`
    PAP.Person_has_Phone           PAP.Person_has_Phone           Person `left`
    PAP.Company_has_Email          PAP.Company_has_Email          Company `left`
    PAP.Person_has_Email           PAP.Person_has_Email           Person `left`
    PAP.Company_has_Address        PAP.Company_has_Address        Company `left`
    PAP.Person_has_Address         PAP.Person_has_Address         Person `left`

    >>> name, DT = ("right", "MOM._Link_n_")
    >>> xs       = a_map [name, DT]
    >>> for i, (kind, ET) in enumerate (sorted (xs, key = lambda x : x [1].i_rank)) : ### right
    ...     if not i :
    ...         print ("%%-30s %%-30s %%s" %% ("E_Type", "det", "det_kind"))
    ...         print ("=" * 80)
    ...     det = kind.attr.det.type_name
    ...     dek = kind.attr.det_kind
    ...     print ("%%-30s %%-30s %%s" %% (ET.type_name, det, dek))
    E_Type                         det                            det_kind
    ================================================================================
    MOM._Link_n_                   MOM._Link_n_                   Right `right`
    MOM.Link2                      MOM._Link_n_                   Right `right`
    PAP._Link_n_                   MOM._Link_n_                   Right `right`
    PAP.Link2                      MOM._Link_n_                   Right `right`
    PAP.Subject_has_Property       PAP.Subject_has_Property       Property `right`
    PAP.Person_has_Account         PAP.Person_has_Account         Account `right`
    SRM._Link_n_                   MOM._Link_n_                   Right `right`
    SRM.Link2                      MOM._Link_n_                   Right `right`
    SRM.Boat_in_Regatta            SRM.Boat_in_Regatta            Regatta `right`
    SRM.Crew_Member                SRM.Crew_Member                Sailor `right`
    SRM.Team_has_Boat_in_Regatta   SRM.Team_has_Boat_in_Regatta   Boat_in_Regatta `right`
    PAP.Subject_has_Address        PAP.Subject_has_Address        Address `right`
    PAP.Subject_has_Email          PAP.Subject_has_Email          Email `right`
    PAP.Subject_has_Phone          PAP.Subject_has_Phone          Phone `right`
    PAP.Subject_has_Url            PAP.Subject_has_Url            Url `right`
    PAP.Company_has_Url            PAP.Subject_has_Url            Url `right`
    PAP.Person_has_Url             PAP.Subject_has_Url            Url `right`
    PAP.Company_has_Phone          PAP.Subject_has_Phone          Phone `right`
    PAP.Person_has_Phone           PAP.Subject_has_Phone          Phone `right`
    PAP.Company_has_Email          PAP.Subject_has_Email          Email `right`
    PAP.Person_has_Email           PAP.Subject_has_Email          Email `right`
    PAP.Company_has_Address        PAP.Subject_has_Address        Address `right`
    PAP.Person_has_Address         PAP.Subject_has_Address        Address `right`


"""

_test_pickled_types = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> MOM   = scope.MOM
    >>> nl    = pyk.unichr (10)
    >>> a_map = _attr_map (MOM.Id_Entity)

    >>> p_types = set ()
    >>> for (name, DT), xs in sorted (pyk.iteritems (a_map)) :
    ...     kind, ET = xs [0]
    ...     if kind.save_to_db and not kind.is_composite :
    ...         pt = kind.Pickled_Type
    ...         if pt :
    ...             at = kind.attr
    ...             pn = pt.__name__
    ...             pn = portable_repr.Type_Name_Map.get (pn, pn)
    ...             p_types.add (pn)
    ...             print ("%%-20s %%-15s %%-15s %%6s %%5d %%5d" %% (kind.name, at.typ, pn, pt.max_length, pt.max_ui_length, pt.length))
    abstract             Text            text-string          0   120     0
    address              Email           text-string         80    81    80
    beam                 Float           float             None    22    22
    boat_class           Entity          _Boat_Class_      None    20    20
    calendar             Entity          Calendar          None    20    20
    cc                   Numeric_String  text-string          3     4     3
    city                 String          text-string         30    31    30
    club                 Entity          Club              None    20    20
    club                 Entity          Club              None    20    20
    club                 Entity          Club              None    20    20
    contents             Text            text-string          0   120     0
    contents             Text            text-string          0   120     0
    count                Int             int               None     1     1
    country              String          text-string         20    21    20
    date                 Date            date              None    12    12
    date_exceptions      Date_List       byte-string          0    20     0
    dates                Date_List       byte-string          0    20     0
    desc                 String          text-string         80    81    80
    desc                 String          text-string         20    21    20
    desc                 String          text-string         20    21    20
    desc                 String          text-string         20    21    20
    desc                 String          text-string         30    31    30
    desc                 String          text-string        160   161   160
    desc                 String          text-string        160   161   160
    detail               String          text-string        160   161   160
    directory            Directory       byte-string          0   120     0
    discarded            Boolean         bool              None     5     5
    discards             Int             int               None     3     3
    download_name        String          text-string         64    65    64
    easter_offset        Int_List        byte-string          0    20     0
    event                Entity          Regatta_Event     None    20    20
    extension            Numeric_String  text-string          5     6     5
    finish               Date            date              None    12    12
    first_name           String          text-string         32    33    32
    format               Format          text-string          8     9     8
    head_line            String          text-string        256   257   256
    hidden               Boolean         bool              None     5     5
    is_cancelled         Boolean         bool              None     5     5
    is_cancelled         Boolean         bool              None     5     5
    is_exception         Boolean         bool              None     5     5
    is_team_race         Boolean         bool              None     5     5
    key                  Int             int               None    20    20
    kind                 String          text-string         32    33    32
    last_cid             Int             int               None    20    20
    last_name            String          text-string         48    49    48
    leader               Entity          Person            None    20    20
    link_to              Url             text-string        160   161   160
    loa                  Float           float             None    22    22
    long_name            String          text-string         64    65    64
    max_crew             Int             int               None     2     2
    middle_name          String          text-string         32    33    32
    mna_number           Int             int               None     7     7
    month                Int_List        byte-string          0    20     0
    month_day            Int_List        byte-string          0    20     0
    name                 Name            text-string         32    33    32
    name                 String          text-string         64    65    64
    name                 String          text-string         48    49    48
    name                 String          text-string          8     9     8
    name                 String          text-string         64    65    64
    name                 String          text-string         64    65    64
    name                 String          text-string         48    49    48
    name                 String          text-string        100   101   100
    nation               Nation          text-string          3    20     3
    nation               Nation          text-string          3    20     3
    ndc                  Numeric_String  text-string          5     6     5
    number               Int             int               None    20    20
    parent_url           Url             text-string        160   161   160
    period               Int             int               None     1     1
    perma_name           String          text-string         64    65    64
    perma_name           String          text-string         64    65    64
    perma_name           Date-Slug       text-string         80    81    80
    pid                  Surrogate       int               None    20    20
    place                Int             int               None     1     1
    place                Int             int               None     1     1
    points               Int             int               None     1     1
    points               Int             int               None     1     1
    prio                 Int             int               None    20    20
    prio                 Int             int               None    20    20
    race                 Int             int               None     3     3
    races                Int             int               None     3     3
    rank                 Int             int               None    20    20
    region               String          text-string         20    21    20
    registered_in        String          text-string         64    65    64
    registration_date    Date            date              None    12    12
    registration_date    Date            date              None    12    12
    restrict_pos         Int_List        byte-string          0    20     0
    role                 String          text-string         32    33    32
    sail_area            Float           float             None    22    22
    sail_number          Int             int               None     7     7
    sail_number_x        String          text-string          8     9     8
    sex                  Sex             text-string          1     2     1
    short_name           String          text-string         12    13    12
    short_title          String          text-string         30    31    30
    short_title          String          text-string         30    31    30
    skipper              Entity          Sailor            None    20    20
    sn                   Numeric_String  text-string         14    15    14
    start                Date            date              None    12    12
    starters_rl          Int             int               None    20    20
    status               String          text-string          8     9     8
    street               String          text-string         60    61    60
    target_url           Url             text-string        160   161   160
    text                 Text            text-string          0   120     0
    title                String          text-string         20    21    20
    title                String          text-string        120   121   120
    type_name            String          text-string          0   120     0
    unit                 Unit            int               None    20    20
    value                Url             text-string        160   161   160
    week                 Int_List        byte-string          0    20     0
    week_day             Weekday_RR_List byte-string          0    20     0
    yardstick            Int             int               None     3     3
    year                 Int             int               None     5     5
    year_day             Int_List        byte-string          0    20     0
    zip                  String          text-string          6     7     6

    >>> for p in sorted (p_types) :
    ...     print (p)
    Calendar
    Club
    Person
    Regatta_Event
    Sailor
    _Boat_Class_
    bool
    byte-string
    date
    float
    int
    text-string

    >>> for (name, DT), xs in sorted (pyk.iteritems (a_map)) :
    ...     kind, ET = xs [0]
    ...     if kind.save_to_db and not kind.is_composite :
    ...         pt = kind.Pickled_Type_Raw
    ...         if pt :
    ...             pn = pt.__name__
    ...             pn = portable_repr.Type_Name_Map.get (pn, pn)
    ...             print ("%%-20s %%-15s %%-15s %%6s %%5d %%5d" %% (kind.name, kind.typ, pn, pt.max_length, pt.max_ui_length, pt.length))
    address              Email           text-string         80    81    80
    city                 String          text-string         30    31    30
    country              String          text-string         20    21    20
    first_name           String          text-string         32    33    32
    last_name            String          text-string         48    49    48
    middle_name          String          text-string         32    33    32
    mna_number           Int             text-string       None     7     7
    name                 String          text-string         64    65    64
    name                 String          text-string          8     9     8
    name                 String          text-string         64    65    64
    name                 String          text-string         64    65    64
    name                 String          text-string         48    49    48
    region               String          text-string         20    21    20
    registered_in        String          text-string         64    65    64
    sail_number          Int             text-string       None     7     7
    sail_number_x        String          text-string          8     9     8
    short_name           String          text-string         12    13    12
    street               String          text-string         60    61    60
    title                String          text-string         20    21    20
    zip                  String          text-string          6     7     6

"""

_test_types = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> MOM = scope.MOM
    >>> for T, l in children_trans_iter (MOM.Id_Entity) :
    ...     ET = T.E_Type
    ...     print ("%%s%%s" %% ("  " * l, ET.type_name))
    MOM.Id_Entity
      MOM.Link
        MOM.Link1
          Auth.Link1
            Auth._Account_Action_
              Auth.Account_Activation
              Auth.Account_Password_Change_Required
              Auth._Account_Token_Action_
                Auth.Account_EMail_Verification
                Auth.Account_Password_Reset
          PAP.Link1
            PAP.Address_Position
          EVT.Link1
            EVT.Event
            EVT.Event_occurs
            EVT._Recurrence_Mixin_
              EVT.Recurrence_Spec
              EVT.Recurrence_Rule
          SWP.Link1
            SWP.Clip_O
            SWP.Picture
          SRM.Link1
            SRM.Boat
            SRM.Regatta
              SRM.Regatta_C
              SRM.Regatta_H
            SRM.Sailor
            SRM.Race_Result
            SRM.Team
        MOM._Link_n_
          MOM.Link2
            Auth.Link2
              Auth.Account_in_Group
            PAP.Link2
              PAP.Subject_has_Property
                PAP.Subject_has_Address
                  PAP.Company_has_Address
                  PAP.Person_has_Address
                PAP.Subject_has_Email
                  PAP.Company_has_Email
                  PAP.Person_has_Email
                PAP.Subject_has_Phone
                  PAP.Company_has_Phone
                  PAP.Person_has_Phone
                PAP.Subject_has_Url
                  PAP.Company_has_Url
                  PAP.Person_has_Url
              PAP.Person_has_Account
            SRM.Link2
              SRM.Boat_in_Regatta
              SRM.Crew_Member
              SRM.Team_has_Boat_in_Regatta
          MOM.Link3
          Auth._Link_n_
          PAP._Link_n_
          SRM._Link_n_
        Auth.Link
        PAP.Link
        EVT.Link
        SWP.Link
        SRM.Link
      MOM.Object
        Auth.Object
          Auth._Account_
            Auth.Account
          Auth.Certificate
          Auth.Group
        PAP.Object
          PAP.Property
            PAP.Address
            PAP.Email
            PAP.Phone
            PAP.Url
          PAP.Subject
            PAP.Group
              PAP.Legal_Entity
                PAP.Company
            PAP.Person
        EVT.Object
          EVT.Calendar
        SWP.Object
          SWP.Object_PN
            SWP.Page
              SWP.Page_Y
              SWP.Clip_X
              SRM.Page
            SWP.Gallery
            SWP.Referral
        SRM.Object
          SRM._Boat_Class_
            SRM.Boat_Class
            SRM.Handicap
          SRM.Club
          SRM.Regatta_Event
      Auth.Id_Entity
      PAP.Id_Entity
      EVT.Id_Entity
      SWP.Id_Entity
      SRM.Id_Entity


"""

__test__ = Scaffold.create_test_dict \
    ( dict
        ( test_DET           = _test_DET
        , test_pickled_types = _test_pickled_types
        , test_types         = _test_types
        )
    )

### __END__ GTW.__test__.Attr
