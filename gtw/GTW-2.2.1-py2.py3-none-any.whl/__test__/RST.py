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
#    GTW.__test__.RST
#
# Purpose
#    Test RESTful api
#
# Revision Dates
#    27-Jun-2012 (CT) Creation
#    31-Jul-2012 (CT) Add `settimeout` to `run_server`, fix `except` clause
#     2-Aug-2012 (CT) Change sequence of tests in `test_post` (Postgresql
#                     wastes pids for a Name_Clash)
#     2-Aug-2012 (CT) Add `change_query_filters` for entities to `test_cqf`
#     7-Aug-2012 (CT) Add `test_doc`
#     8-Aug-2012 (CT) Add `test_example_*`, continue `test_doc`
#    18-Sep-2012 (CT) Factor _GTW/__test__/Test_Command.py
#     4-Oct-2012 (CT) Adapt to `?brief`
#     5-Oct-2012 (CT) Test `.get ("/v1/SRM-Regatta.csv?verbose")`
#     5-Oct-2012 (CT) Test multiple `AQ` arguments for a single `get`
#     5-Oct-2012 (CT) Test `fields` query argument
#    12-Oct-2012 (CT) Adapt to repr change of `An_Entity`
#    21-Nov-2012 (CT) Test invalid `AQ` argument
#    27-Nov-2012 (CT) Test `location` header of `POST`
#     6-Dec-2012 (CT) Remove `Entity_created_by_Person`
#    11-Dec-2012 (CT) Adapt to change in `HTTP_Status` response
#    12-Dec-2012 (CT) Use `+ELLIPSIS` instead of `Re_Replacer`
#     6-Jan-2013 (CT) Add `test_client`
#     9-Jan-2013 (CT) Factor `GTW_RST_Test_Command`, `rst_harness`
#     3-Mar-2013 (CT) Add `link: ...rel=doc` to `headers`
#     4-Mar-2013 (CT) Add `PAP.Legal_Entity`
#     6-Mar-2013 (CT) Adapt to new attribute `Company.registered_in`
#     2-May-2013 (CT) Add `offset=[0,-1]/limit=1` tests to `test_query`
#     3-May-2013 (CT) Add `test_rat`, import `GTW.OMP.Auth`
#     8-May-2013 (CT) Remove `.pid`, `.url` from `attribute_names`, unless CSV
#    17-May-2013 (CT) Add tests for `rels`
#    13-Jun-2013 (CT) Remove `PNS_Aliases`
#    29-Jul-2013 (CT) Add `test_put`
#     4-Oct-2013 (CT) Add test for query argument `fields`
#    31-Mar-2014 (CT) Apply `date_cleaner` to `R.get("/Doc/SRM-Boat_in_Regatta")`
#    13-Jun-2014 (RS) Fix tests for `PAP.Group`
#    29-Jul-2015 (CT) Adapt to name change of PAP.Phone attributes
#    21-Oct-2015 (CT) Use `json_cleaner`, improve Python-3 compatibility
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

from   _GTW.__test__.rst_harness  import *
from   _GTW.__test__              import rst_harness

import _GTW._OMP._Auth.import_Auth
import _GTW._OMP._PAP.import_PAP
import _GTW._OMP._SRM.import_SRM

import _GTW._RST._MOM.Client

import datetime
import json

def run_server (db_url = "hps://", db_name = None, scaffold_name = "Scaffold") :
    return rst_harness.run_server \
        ("_GTW.__test__.RST", db_url, db_name, scaffold_name)
# end def run_server

class _GTW_Test_Command_ (GTW_RST_Test_Command) :

    _rn_prefix            = "_GTW_Test"

    SALT                  = b"c9cac445-3fd8-451d-9eff-dd56c7a91485"

    def fixtures (self, scope) :
        PAP   = scope.PAP
        SRM   = scope.SRM
        BiR   = SRM.Boat_in_Regatta
        ct    = PAP.Person ("Tanzer", "Christian", raw = True)
        lt    = PAP.Person ("Tanzer", "Laurens", "William", raw = True)
        cat   = PAP.Person ("Tanzer", "Clarissa", "Anna", raw = True)
        ct_s  = SRM.Sailor (ct,  nation = "AUT", mna_number = "29676", raw = True)
        lt_s  = SRM.Sailor (lt,  nation = "AUT", raw = True)
        cat_s = SRM.Sailor (cat, nation = "AUT", raw = True)
        opti  = SRM.Boat_Class ("Optimist", max_crew = "1")
        b     = SRM.Boat ("Optimist", "1107", "AUT", raw = True)
        ys    = SRM.Handicap ("Yardstick", raw = True)
        rev   = SRM.Regatta_Event ("Himmelfahrt", ("20080501", ), raw = True)
        reg   = SRM.Regatta_C (rev, opti)
        reh   = SRM.Regatta_H (rev, ys)
        rev_g = SRM.Regatta_Event \
            ("Guggenberger", ("20080620", "20080621"), raw = True)
        reg_c = SRM.Regatta_C (rev_g, opti)
        bir   = SRM.Boat_in_Regatta (b, reg,   skipper = lt_s)
        bir_g = SRM.Boat_in_Regatta (b, reg_c, skipper = lt_s)
        scope.commit ()
    # end def fixtures

_Command_  = _GTW_Test_Command_ # end class

class _GTW_Test_Command_RAT_ (_GTW_Test_Command_) :

    v1_auth_required        = True

    def fixtures (self, scope) :
        self.__super.fixtures (scope)
        Auth = scope.Auth
        Auth.Account.create_new_account_x \
            ("test@test.test", "test", enabled = True, suspended = False)
        scope.commit ()
    # end def fixtures

_Command_RAT_ = _GTW_Test_Command_RAT_ # end class

Scaffold      = _Command_     ()
Scaffold_RAT  = _Command_RAT_ ()

### «text» ### The doctest follows::

_test_client = r"""
    >>> server = run_server (%(p1)s, %(n1)s)

    >>> CC = GTW.RST.MOM.Client.Requester ("http://localhost:9999", verify = False)
    >>> CR = GTW.RST.MOM.Client.Requester ("http://localhost:9999", raw = True)

    >>> r = CC.get ("")
    >>> prepr (r._url)
    'http://localhost:9999/'
    >>> prepr ([e._url for e in r])
    ['http://localhost:9999/v1', 'http://localhost:9999/Doc', 'http://localhost:9999/RAISE']

    >>> r1 = list (x for x in  r [0] if x._url.endswith ("MOM-Id_Entity")) [0]

    >>> print (r1._url)
    http://localhost:9999/v1/MOM-Id_Entity

    >>> prepr ([e._url for e in r1._entries [:3]])
    ['/v1/MOM-Id_Entity/1', '/v1/MOM-Id_Entity/2', '/v1/MOM-Id_Entity/3']

    >>> r2 = r1 [0]
    >>> prepr (sorted (pyk.iteritems (r2._attrs)))
    [('first_name', 'christian'), ('last_name', 'tanzer'), ('middle_name', ''), ('title', '')]

    >>> r2c = CC.get (r2._url)
    >>> prepr (r2c._result.url)
    'http://localhost:9999/v1/MOM-Id_Entity/1'
    >>> r2r = CR.get (r2._url)
    >>> prepr (r2r._result.url)
    'http://localhost:9999/v1/MOM-Id_Entity/1?raw=True'
    >>> prepr (sorted (pyk.iteritems (r2r._attrs)))
    [('first_name', 'Christian'), ('last_name', 'Tanzer'), ('middle_name', ''), ('title', '')]

    >>> r2r._changed_p
    False
    >>> r2r.title = "Mag."
    >>> r2r._changed_p
    True

    >>> prepr (sorted (pyk.iteritems (r2r._attrs)))
    [('first_name', 'Christian'), ('last_name', 'Tanzer'), ('middle_name', ''), ('title', 'Mag.')]
    >>> prepr (sorted (pyk.iteritems (r2r._attrs_orig)))
    [('first_name', 'Christian'), ('last_name', 'Tanzer'), ('middle_name', ''), ('title', '')]

    >>> r2r_p = r2r.PUT ()
    >>> prepr (r2r_p._result.url)
    'http://localhost:9999/v1/MOM-Id_Entity/1?raw=True'

"""

_test_cqf = r"""
    >>> server = Scaffold (["wsgi"] + server_args + ["-db_url", %(p1)s, "-db_name", %(n1)s or ("test." + %(bn1)s)]) # doctest:+ELLIPSIS
    ...
    >>> root   = Scaffold.root
    >>> v1     = root.resource_from_href ("v1")
    >>> pids   = root.resource_from_href ("v1/pid")

    >>> prepr (v1)
    <Scope v1: /v1>
    >>> prepr (pids)
    <E_Type MOM-Id_Entity: /v1/MOM-Id_Entity>

    >>> for e in v1.entries :
    ...     print ("%%s\n    %%s" %% (e.name, e.change_query_filters))
    Auth-Account
        (Q.type_name == 'Auth.Account',)
    Auth-Account_in_Group
        (Q.type_name == 'Auth.Account_in_Group',)
    Auth-Certificate
        (Q.type_name == 'Auth.Certificate',)
    Auth-Group
        (Q.type_name == 'Auth.Group',)
    Auth-Id_Entity
        (Q.type_name.in_ (['Auth.Account', 'Auth.Account_Activation', 'Auth.Account_EMail_Verification', 'Auth.Account_Password_Change_Required', 'Auth.Account_Password_Reset', 'Auth.Account_in_Group', 'Auth.Certificate', 'Auth.Group'],),)
    Auth-Link
        (Q.type_name.in_ (['Auth.Account_Activation', 'Auth.Account_EMail_Verification', 'Auth.Account_Password_Change_Required', 'Auth.Account_Password_Reset', 'Auth.Account_in_Group'],),)
    Auth-Link1
        (Q.type_name.in_ (['Auth.Account_Activation', 'Auth.Account_EMail_Verification', 'Auth.Account_Password_Change_Required', 'Auth.Account_Password_Reset'],),)
    Auth-Link2
        (Q.type_name.in_ (['Auth.Account_in_Group'],),)
    Auth-Object
        (Q.type_name.in_ (['Auth.Account', 'Auth.Certificate', 'Auth.Group'],),)
    Auth-_Account_
        (Q.type_name.in_ (['Auth.Account'],),)
    Auth-_Link_n_
        (Q.type_name.in_ (['Auth.Account_in_Group'],),)
    MOM-Id_Entity
        ()
    MOM-Link
        (Q.type_name.in_ (['Auth.Account_Activation', 'Auth.Account_EMail_Verification', 'Auth.Account_Password_Change_Required', 'Auth.Account_Password_Reset', 'Auth.Account_in_Group', 'PAP.Address_Position', 'PAP.Company_has_Address', 'PAP.Company_has_Email', 'PAP.Company_has_Phone', 'PAP.Company_has_Url', 'PAP.Person_has_Account', 'PAP.Person_has_Address', 'PAP.Person_has_Email', 'PAP.Person_has_Phone', 'PAP.Person_has_Url', 'SRM.Boat', 'SRM.Boat_in_Regatta', 'SRM.Crew_Member', 'SRM.Race_Result', 'SRM.Regatta_C', 'SRM.Regatta_H', 'SRM.Sailor', 'SRM.Team', 'SRM.Team_has_Boat_in_Regatta', 'SWP.Clip_O', 'SWP.Picture'],),)
    MOM-Link1
        (Q.type_name.in_ (['Auth.Account_Activation', 'Auth.Account_EMail_Verification', 'Auth.Account_Password_Change_Required', 'Auth.Account_Password_Reset', 'PAP.Address_Position', 'SRM.Boat', 'SRM.Race_Result', 'SRM.Regatta_C', 'SRM.Regatta_H', 'SRM.Sailor', 'SRM.Team', 'SWP.Clip_O', 'SWP.Picture'],),)
    MOM-Link2
        (Q.type_name.in_ (['Auth.Account_in_Group', 'PAP.Company_has_Address', 'PAP.Company_has_Email', 'PAP.Company_has_Phone', 'PAP.Company_has_Url', 'PAP.Person_has_Account', 'PAP.Person_has_Address', 'PAP.Person_has_Email', 'PAP.Person_has_Phone', 'PAP.Person_has_Url', 'SRM.Boat_in_Regatta', 'SRM.Crew_Member', 'SRM.Team_has_Boat_in_Regatta'],),)
    MOM-Object
        (Q.type_name.in_ (['Auth.Account', 'Auth.Certificate', 'Auth.Group', 'PAP.Address', 'PAP.Company', 'PAP.Email', 'PAP.Person', 'PAP.Phone', 'PAP.Url', 'SRM.Boat_Class', 'SRM.Club', 'SRM.Handicap', 'SRM.Page', 'SRM.Regatta_Event', 'SWP.Gallery', 'SWP.Page', 'SWP.Referral'],),)
    MOM-_Link_n_
        (Q.type_name.in_ (['Auth.Account_in_Group', 'PAP.Company_has_Address', 'PAP.Company_has_Email', 'PAP.Company_has_Phone', 'PAP.Company_has_Url', 'PAP.Person_has_Account', 'PAP.Person_has_Address', 'PAP.Person_has_Email', 'PAP.Person_has_Phone', 'PAP.Person_has_Url', 'SRM.Boat_in_Regatta', 'SRM.Crew_Member', 'SRM.Team_has_Boat_in_Regatta'],),)
    PAP-Address
        (Q.type_name == 'PAP.Address',)
    PAP-Address_Position
        (Q.type_name == 'PAP.Address_Position',)
    PAP-Company
        (Q.type_name == 'PAP.Company',)
    PAP-Company_has_Address
        (Q.type_name == 'PAP.Company_has_Address',)
    PAP-Company_has_Email
        (Q.type_name == 'PAP.Company_has_Email',)
    PAP-Company_has_Phone
        (Q.type_name == 'PAP.Company_has_Phone',)
    PAP-Company_has_Url
        (Q.type_name == 'PAP.Company_has_Url',)
    PAP-Email
        (Q.type_name == 'PAP.Email',)
    PAP-Group
        (Q.type_name.in_ (['PAP.Company'],),)
    PAP-Id_Entity
        (Q.type_name.in_ (['PAP.Address', 'PAP.Address_Position', 'PAP.Company', 'PAP.Company_has_Address', 'PAP.Company_has_Email', 'PAP.Company_has_Phone', 'PAP.Company_has_Url', 'PAP.Email', 'PAP.Person', 'PAP.Person_has_Account', 'PAP.Person_has_Address', 'PAP.Person_has_Email', 'PAP.Person_has_Phone', 'PAP.Person_has_Url', 'PAP.Phone', 'PAP.Url'],),)
    PAP-Legal_Entity
        (Q.type_name.in_ (['PAP.Company'],),)
    PAP-Link
        (Q.type_name.in_ (['PAP.Address_Position', 'PAP.Company_has_Address', 'PAP.Company_has_Email', 'PAP.Company_has_Phone', 'PAP.Company_has_Url', 'PAP.Person_has_Account', 'PAP.Person_has_Address', 'PAP.Person_has_Email', 'PAP.Person_has_Phone', 'PAP.Person_has_Url'],),)
    PAP-Link1
        (Q.type_name.in_ (['PAP.Address_Position'],),)
    PAP-Link2
        (Q.type_name.in_ (['PAP.Company_has_Address', 'PAP.Company_has_Email', 'PAP.Company_has_Phone', 'PAP.Company_has_Url', 'PAP.Person_has_Account', 'PAP.Person_has_Address', 'PAP.Person_has_Email', 'PAP.Person_has_Phone', 'PAP.Person_has_Url'],),)
    PAP-Object
        (Q.type_name.in_ (['PAP.Address', 'PAP.Company', 'PAP.Email', 'PAP.Person', 'PAP.Phone', 'PAP.Url'],),)
    PAP-Person
        (Q.type_name == 'PAP.Person',)
    PAP-Person_has_Account
        (Q.type_name == 'PAP.Person_has_Account',)
    PAP-Person_has_Address
        (Q.type_name == 'PAP.Person_has_Address',)
    PAP-Person_has_Email
        (Q.type_name == 'PAP.Person_has_Email',)
    PAP-Person_has_Phone
        (Q.type_name == 'PAP.Person_has_Phone',)
    PAP-Person_has_Url
        (Q.type_name == 'PAP.Person_has_Url',)
    PAP-Phone
        (Q.type_name == 'PAP.Phone',)
    PAP-Property
        (Q.type_name.in_ (['PAP.Address', 'PAP.Email', 'PAP.Phone', 'PAP.Url'],),)
    PAP-Subject
        (Q.type_name.in_ (['PAP.Company', 'PAP.Person'],),)
    PAP-Subject_has_Address
        (Q.type_name.in_ (['PAP.Company_has_Address', 'PAP.Person_has_Address'],),)
    PAP-Subject_has_Email
        (Q.type_name.in_ (['PAP.Company_has_Email', 'PAP.Person_has_Email'],),)
    PAP-Subject_has_Phone
        (Q.type_name.in_ (['PAP.Company_has_Phone', 'PAP.Person_has_Phone'],),)
    PAP-Subject_has_Property
        (Q.type_name.in_ (['PAP.Company_has_Address', 'PAP.Company_has_Email', 'PAP.Company_has_Phone', 'PAP.Company_has_Url', 'PAP.Person_has_Address', 'PAP.Person_has_Email', 'PAP.Person_has_Phone', 'PAP.Person_has_Url'],),)
    PAP-Subject_has_Url
        (Q.type_name.in_ (['PAP.Company_has_Url', 'PAP.Person_has_Url'],),)
    PAP-Url
        (Q.type_name == 'PAP.Url',)
    PAP-_Link_n_
        (Q.type_name.in_ (['PAP.Company_has_Address', 'PAP.Company_has_Email', 'PAP.Company_has_Phone', 'PAP.Company_has_Url', 'PAP.Person_has_Account', 'PAP.Person_has_Address', 'PAP.Person_has_Email', 'PAP.Person_has_Phone', 'PAP.Person_has_Url'],),)
    SRM-Boat
        (Q.type_name == 'SRM.Boat',)
    SRM-Boat_Class
        (Q.type_name == 'SRM.Boat_Class',)
    SRM-Boat_in_Regatta
        (Q.type_name == 'SRM.Boat_in_Regatta',)
    SRM-Club
        (Q.type_name == 'SRM.Club',)
    SRM-Crew_Member
        (Q.type_name == 'SRM.Crew_Member',)
    SRM-Handicap
        (Q.type_name == 'SRM.Handicap',)
    SRM-Id_Entity
        (Q.type_name.in_ (['SRM.Boat', 'SRM.Boat_Class', 'SRM.Boat_in_Regatta', 'SRM.Club', 'SRM.Crew_Member', 'SRM.Handicap', 'SRM.Page', 'SRM.Race_Result', 'SRM.Regatta_C', 'SRM.Regatta_Event', 'SRM.Regatta_H', 'SRM.Sailor', 'SRM.Team', 'SRM.Team_has_Boat_in_Regatta'],),)
    SRM-Link
        (Q.type_name.in_ (['SRM.Boat', 'SRM.Boat_in_Regatta', 'SRM.Crew_Member', 'SRM.Race_Result', 'SRM.Regatta_C', 'SRM.Regatta_H', 'SRM.Sailor', 'SRM.Team', 'SRM.Team_has_Boat_in_Regatta'],),)
    SRM-Link1
        (Q.type_name.in_ (['SRM.Boat', 'SRM.Race_Result', 'SRM.Regatta_C', 'SRM.Regatta_H', 'SRM.Sailor', 'SRM.Team'],),)
    SRM-Link2
        (Q.type_name.in_ (['SRM.Boat_in_Regatta', 'SRM.Crew_Member', 'SRM.Team_has_Boat_in_Regatta'],),)
    SRM-Object
        (Q.type_name.in_ (['SRM.Boat_Class', 'SRM.Club', 'SRM.Handicap', 'SRM.Page', 'SRM.Regatta_Event'],),)
    SRM-Page
        (Q.type_name == 'SRM.Page',)
    SRM-Race_Result
        (Q.type_name == 'SRM.Race_Result',)
    SRM-Regatta
        (Q.type_name.in_ (['SRM.Regatta_C', 'SRM.Regatta_H'],),)
    SRM-Regatta_C
        (Q.type_name == 'SRM.Regatta_C',)
    SRM-Regatta_Event
        (Q.type_name == 'SRM.Regatta_Event',)
    SRM-Regatta_H
        (Q.type_name == 'SRM.Regatta_H',)
    SRM-Sailor
        (Q.type_name == 'SRM.Sailor',)
    SRM-Team
        (Q.type_name == 'SRM.Team',)
    SRM-Team_has_Boat_in_Regatta
        (Q.type_name == 'SRM.Team_has_Boat_in_Regatta',)
    SRM-_Boat_Class_
        (Q.type_name.in_ (['SRM.Boat_Class', 'SRM.Handicap'],),)
    SRM-_Link_n_
        (Q.type_name.in_ (['SRM.Boat_in_Regatta', 'SRM.Crew_Member', 'SRM.Team_has_Boat_in_Regatta'],),)
    SWP-Clip_O
        (Q.type_name == 'SWP.Clip_O',)
    SWP-Clip_X
        (Q.type_name == 'SWP.Clip_X',)
    SWP-Gallery
        (Q.type_name == 'SWP.Gallery',)
    SWP-Id_Entity
        (Q.type_name.in_ (['SWP.Clip_O', 'SWP.Gallery', 'SWP.Page', 'SWP.Picture', 'SWP.Referral'],),)
    SWP-Link
        (Q.type_name.in_ (['SWP.Clip_O', 'SWP.Picture'],),)
    SWP-Link1
        (Q.type_name.in_ (['SWP.Clip_O', 'SWP.Picture'],),)
    SWP-Object
        (Q.type_name.in_ (['SWP.Gallery', 'SWP.Page', 'SWP.Referral'],),)
    SWP-Object_PN
        (Q.type_name.in_ (['SWP.Gallery', 'SWP.Page', 'SWP.Referral'],),)
    SWP-Page
        (Q.type_name.in_ (['SRM.Page', 'SWP.Clip_X', 'SWP.Page', 'SWP.Page_Y'],),)
    SWP-Page_Y
        (Q.type_name == 'SWP.Page_Y',)
    SWP-Picture
        (Q.type_name == 'SWP.Picture',)
    SWP-Referral
        (Q.type_name == 'SWP.Referral',)

    >>> for e in v1.entries :
    ...     print ("%%s    %%s" %% (e.name, e.attributes))
    Auth-Account    (Email `name`, Boolean `enabled`, Boolean `superuser`)
    Auth-Account_in_Group    (Account `left`, Group `right`)
    Auth-Certificate    (Email `email`, Date_Time_Interval `validity`, String `desc`, Date-Time `revocation_date`)
    Auth-Group    (String `name`, String `desc`)
    Auth-Id_Entity    ()
    Auth-Link    (Left `left`,)
    Auth-Link1    (Left `left`,)
    Auth-Link2    (Left `left`, Right `right`)
    Auth-Object    ()
    Auth-_Account_    (Email `name`, Boolean `enabled`, Boolean `superuser`)
    Auth-_Link_n_    (Left `left`, Right `right`)
    MOM-Id_Entity    ()
    MOM-Link    (Left `left`,)
    MOM-Link1    (Left `left`,)
    MOM-Link2    (Left `left`, Right `right`)
    MOM-Object    ()
    MOM-_Link_n_    (Left `left`, Right `right`)
    PAP-Address    (String `street`, String `zip`, String `city`, String `country`, String `desc`, String `region`)
    PAP-Address_Position    (Address `left`, Position `position`)
    PAP-Company    (String `name`, String `registered_in`, Date_Interval `lifetime`, String `short_name`)
    PAP-Company_has_Address    (Company `left`, Address `right`, String `desc`)
    PAP-Company_has_Email    (Company `left`, Email `right`, String `desc`)
    PAP-Company_has_Phone    (Company `left`, Phone `right`, Numeric_String `extension`, String `desc`)
    PAP-Company_has_Url    (Company `left`, Url `right`, String `desc`)
    PAP-Email    (Email `address`, String `desc`)
    PAP-Group    (String `name`, Date_Interval `lifetime`, String `short_name`)
    PAP-Id_Entity    ()
    PAP-Legal_Entity    (String `name`, Date_Interval `lifetime`, String `short_name`)
    PAP-Link    (Left `left`,)
    PAP-Link1    (Left `left`,)
    PAP-Link2    (Left `left`, Right `right`)
    PAP-Object    ()
    PAP-Person    (String `last_name`, String `first_name`, String `middle_name`, String `title`, Date_Interval `lifetime`, Sex `sex`)
    PAP-Person_has_Account    (Person `left`, Account `right`)
    PAP-Person_has_Address    (Person `left`, Address `right`, String `desc`)
    PAP-Person_has_Email    (Person `left`, Email `right`, String `desc`)
    PAP-Person_has_Phone    (Person `left`, Phone `right`, Numeric_String `extension`, String `desc`)
    PAP-Person_has_Url    (Person `left`, Url `right`, String `desc`)
    PAP-Phone    (Numeric_String `cc`, Numeric_String `ndc`, Numeric_String `sn`, String `desc`)
    PAP-Property    (String `desc`,)
    PAP-Subject    (Date_Interval `lifetime`,)
    PAP-Subject_has_Address    (Subject `left`, Address `right`, String `desc`)
    PAP-Subject_has_Email    (Subject `left`, Email `right`, String `desc`)
    PAP-Subject_has_Phone    (Subject `left`, Phone `right`, Numeric_String `extension`, String `desc`)
    PAP-Subject_has_Property    (Subject `left`, Property `right`, String `desc`)
    PAP-Subject_has_Url    (Subject `left`, Url `right`, String `desc`)
    PAP-Url    (Url `value`, String `desc`)
    PAP-_Link_n_    (Left `left`, Right `right`)
    SRM-Boat    (Boat_Class `left`, Int `sail_number`, Nation `nation`, String `sail_number_x`, String `name`)
    SRM-Boat_Class    (String `name`, Float `beam`, Float `loa`, Int `max_crew`, Float `sail_area`)
    SRM-Boat_in_Regatta    (Boat `left`, Regatta `right`, Entity `skipper`, Int `place`, Int `points`, Int `yardstick`)
    SRM-Club    (String `name`, String `long_name`)
    SRM-Crew_Member    (Boat_in_Regatta `left`, Sailor `right`, Int `key`, String `role`)
    SRM-Handicap    (String `name`,)
    SRM-Id_Entity    ()
    SRM-Link    (Left `left`,)
    SRM-Link1    (Left `left`,)
    SRM-Link2    (Left `left`, Right `right`)
    SRM-Object    ()
    SRM-Page    (Date-Slug `perma_name`, Entity `event`, Text `text`, Date_Interval `date`, Format `format`, String `head_line`, String `desc`, Boolean `hidden`, Int `prio`)
    SRM-Race_Result    (Boat_in_Regatta `left`, Int `race`, Int `points`, String `status`, Boolean `discarded`)
    SRM-Regatta    (Regatta_Event `left`, Entity `boat_class`, Int `discards`, Boolean `is_cancelled`, String `kind`, Int `races`, Regatta_Result `result`, Int `starters_rl`)
    SRM-Regatta_C    (Regatta_Event `left`, Entity `boat_class`, Int `discards`, Boolean `is_cancelled`, String `kind`, Int `races`, Regatta_Result `result`, Int `starters_rl`, Boolean `is_team_race`)
    SRM-Regatta_Event    (String `name`, Date_Interval `date`, Entity `club`, String `desc`, Boolean `is_cancelled`)
    SRM-Regatta_H    (Regatta_Event `left`, Entity `boat_class`, Int `discards`, Boolean `is_cancelled`, String `kind`, Int `races`, Regatta_Result `result`, Int `starters_rl`)
    SRM-Sailor    (Person `left`, Nation `nation`, Int `mna_number`, Entity `club`)
    SRM-Team    (Regatta_C `left`, String `name`, Entity `club`, String `desc`, Entity `leader`, Int `place`)
    SRM-Team_has_Boat_in_Regatta    (Team `left`, Boat_in_Regatta `right`)
    SRM-_Boat_Class_    (String `name`,)
    SRM-_Link_n_    (Left `left`, Right `right`)
    SWP-Clip_O    (Object_PN `left`, Date_Interval `date_x`, Text `abstract`, Int `prio`)
    SWP-Clip_X    (Date-Slug `perma_name`, Text `text`, Date_Interval `date`, String `short_title`, String `title`, Format `format`, String `head_line`, Url `link_to`, Boolean `hidden`, Int `prio`)
    SWP-Gallery    (Date-Slug `perma_name`, Date_Interval `date`, String `short_title`, String `title`, Directory `directory`, Boolean `hidden`, Int `prio`)
    SWP-Id_Entity    ()
    SWP-Link    (Left `left`,)
    SWP-Link1    (Left `left`,)
    SWP-Object    ()
    SWP-Object_PN    (Date-Slug `perma_name`, Date_Interval `date`, String `short_title`, String `title`, Boolean `hidden`, Int `prio`)
    SWP-Page    (Date-Slug `perma_name`, Text `text`, Date_Interval `date`, String `short_title`, String `title`, Format `format`, String `head_line`, Boolean `hidden`, Int `prio`)
    SWP-Page_Y    (Date-Slug `perma_name`, Int `year`, Text `text`, Date_Interval `date`, String `short_title`, String `title`, Format `format`, String `head_line`, Boolean `hidden`, Int `prio`)
    SWP-Picture    (Gallery `left`, Int `number`, String `name`, Picture `photo`, Thumbnail `thumb`)
    SWP-Referral    (Url `parent_url`, Date-Slug `perma_name`, Url `target_url`, Date_Interval `date`, String `short_title`, String `title`, String `download_name`, Boolean `hidden`, Int `prio`)

    >>> print (root.href_pat_frag.replace (r"\_", "_"))
    v1(?:/(?:SWP\-Referral|SWP\-Picture|SWP\-Page_Y|SWP\-Page|SWP\-Object_PN|SWP\-Object|SWP\-Link1|SWP\-Link|SWP\-Id_Entity|SWP\-Gallery|SWP\-Clip_X|SWP\-Clip_O|SRM\-_Link_n_|SRM\-_Boat_Class_|SRM\-Team_has_Boat_in_Regatta|SRM\-Team|SRM\-Sailor|SRM\-Regatta_H|SRM\-Regatta_Event|SRM\-Regatta_C|SRM\-Regatta|SRM\-Race_Result|SRM\-Page|SRM\-Object|SRM\-Link2|SRM\-Link1|SRM\-Link|SRM\-Id_Entity|SRM\-Handicap|SRM\-Crew_Member|SRM\-Club|SRM\-Boat_in_Regatta|SRM\-Boat_Class|SRM\-Boat|PAP\-_Link_n_|PAP\-Url|PAP\-Subject_has_Url|PAP\-Subject_has_Property|PAP\-Subject_has_Phone|PAP\-Subject_has_Email|PAP\-Subject_has_Address|PAP\-Subject|PAP\-Property|PAP\-Phone|PAP\-Person_has_Url|PAP\-Person_has_Phone|PAP\-Person_has_Email|PAP\-Person_has_Address|PAP\-Person_has_Account|PAP\-Person|PAP\-Object|PAP\-Link2|PAP\-Link1|PAP\-Link|PAP\-Legal_Entity|PAP\-Id_Entity|PAP\-Group|PAP\-Email|PAP\-Company_has_Url|PAP\-Company_has_Phone|PAP\-Company_has_Email|PAP\-Company_has_Address|PAP\-Company|PAP\-Address_Position|PAP\-Address|MOM\-_Link_n_|MOM\-Object|MOM\-Link2|MOM\-Link1|MOM\-Link|MOM\-Id_Entity|Auth\-_Link_n_|Auth\-_Account_|Auth\-Object|Auth\-Link2|Auth\-Link1|Auth\-Link|Auth\-Id_Entity|Auth\-Group|Auth\-Certificate|Auth\-Account_in_Group|Auth\-Account))?|Doc

    >>> for o in sorted (pids.objects, key = Q.pid) :
    ...     e = pids._new_entry (o.pid)
    ...     print ("%%s %%s\n    %%s" %% (e.E_Type.type_name, portable_repr (o.ui_display), e.change_query_filters))
    PAP.Person 'Tanzer Christian'
        (Q.pid == 1,)
    PAP.Person 'Tanzer Laurens William'
        (Q.pid == 2,)
    PAP.Person 'Tanzer Clarissa Anna'
        (Q.pid == 3,)
    SRM.Sailor 'Tanzer Christian, AUT, 29676'
        (Q.pid.in_ ((4, 1),),)
    SRM.Sailor 'Tanzer Laurens William, AUT'
        (Q.pid.in_ ((5, 2),),)
    SRM.Sailor 'Tanzer Clarissa Anna, AUT'
        (Q.pid.in_ ((6, 3),),)
    SRM.Boat_Class 'Optimist'
        (Q.pid == 7,)
    SRM.Boat 'Optimist, AUT 1107'
        (Q.pid.in_ ((8, 7),),)
    SRM.Handicap 'Yardstick'
        (Q.pid == 9,)
    SRM.Regatta_Event 'Himmelfahrt 2008-05-01'
        (Q.pid == 10,)
    SRM.Regatta_C 'Himmelfahrt 2008-05-01, Optimist'
        (Q.pid.in_ ((11, 10, 7),),)
    SRM.Regatta_H 'Himmelfahrt 2008-05-01, Yardstick'
        (Q.pid.in_ ((12, 10, 9),),)
    SRM.Regatta_Event 'Guggenberger 2008-06-20 - 2008-06-21'
        (Q.pid == 13,)
    SRM.Regatta_C 'Guggenberger 2008-06-20 - 2008-06-21, Optimist'
        (Q.pid.in_ ((14, 13, 7),),)
    SRM.Boat_in_Regatta 'Optimist, AUT 1107, Himmelfahrt 2008-05-01, Optimist'
        (Q.pid.in_ ((15, 8, 11, 5),),)
    SRM.Boat_in_Regatta 'Optimist, AUT 1107, Guggenberger 2008-06-20 - 2008-06-21, Optimist'
        (Q.pid.in_ ((16, 8, 14, 5),),)

"""

_test_delete = r"""
    >>> server = run_server (%(p1)s, %(n1)s)

    >>> _ = show (R.get ("/v1/pid?brief")) ### 1
    { 'json' :
        { 'entries' :
            [ 1
            , 2
            , 3
            , 4
            , 5
            , 6
            , 7
            , 8
            , 9
            , 10
            , 11
            , 12
            , 13
            , 14
            , 15
            , 16
            ]
        , 'url_template' : '/v1/MOM-Id_Entity/{entry}'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/pid?brief'
    }

    >>> _ = show (R.get ("/v1/pid/1"))  ### 2
    { 'json' :
        { 'attributes' :
            { 'first_name' : 'christian'
            , 'last_name' : 'tanzer'
            , 'middle_name' : ''
            , 'title' : ''
            }
        , 'cid' : 1
        , 'pid' : 1
        , 'type_name' : 'PAP.Person'
        , 'url' : '/v1/MOM-Id_Entity/1'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/pid/1'
    }

    >>> _ = show (R.delete ("/v1/pid/1")) ### 3
    { 'json' :
        { 'attributes_raw' :
            { 'first_name' : 'Christian'
            , 'last_name' : 'Tanzer'
            , 'middle_name' : ''
            , 'title' : ''
            }
        , 'cid' : 1
        , 'error' : "You need to send the object's `cid` with the request"
        , 'pid' : 1
        , 'type_name' : 'PAP.Person'
        , 'url' : '/v1/MOM-Id_Entity/1'
        }
    , 'status' : 400
    , 'url' : 'http://localhost:9999/v1/pid/1'
    }

    >>> _ = show (R.delete ("/v1/pid/1", params = dict (cid = 2))) ### 4
    { 'json' :
        { 'attributes_raw' :
            { 'first_name' : 'Christian'
            , 'last_name' : 'Tanzer'
            , 'middle_name' : ''
            , 'title' : ''
            }
        , 'cid' : 1
        , 'error' : 'Cid mismatch: requested cid = 2, current cid = 1'
        , 'pid' : 1
        , 'type_name' : 'PAP.Person'
        , 'url' : '/v1/MOM-Id_Entity/1'
        }
    , 'status' : 409
    , 'url' : 'http://localhost:9999/v1/pid/1?cid=2'
    }

    >>> _ = show (R.get ("/v1/pid?count")) ### 5
    { 'json' : {'count' : 16}
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/pid?count'
    }

    >>> _ = show (R.delete ("/v1/pid/1", params = dict (cid = 1))) ### 6
    { 'json' :
        { 'attributes_raw' :
            { 'first_name' : 'Christian'
            , 'last_name' : 'Tanzer'
            , 'middle_name' : ''
            , 'title' : ''
            }
        , 'cid' : 1
        , 'pid' : 1
        , 'status' : 'Object with pid 1 successfully deleted'
        , 'type_name' : 'PAP.Person'
        , 'url' : '/v1/MOM-Id_Entity/1'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/pid/1?cid=1'
    }

    >>> _ = show (R.get ("/v1/pid?count")) ### 7
    { 'json' : {'count' : 14}
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/pid?count'
    }

    >>> _ = show (R.delete ("/v1/pid/1", params = dict (cid = 1))) ### 8 #doctest: +ELLIPSIS
    { 'json' :
        { 'description' : 'Gone'
        , 'info' : 'It was deleted by user `anonymous` on ...'
        , 'message' : "Id_Entity `1` doesn't exist anymore!"
        }
    , 'status' : 410
    , 'url' : 'http://localhost:9999/v1/pid/1?cid=1'
    }

    >>> _ = show (R.get ("/v1/pid/1")) ### 9 #doctest: +ELLIPSIS
    { 'json' :
        { 'description' : 'Gone'
        , 'info' : 'It was deleted by user `anonymous` on ...'
        , 'message' : "Id_Entity `1` doesn't exist anymore!"
        }
    , 'status' : 410
    , 'url' : 'http://localhost:9999/v1/pid/1'
    }

    >>> _ = show (R.get ("/v1/pid?brief")) ### 10
    { 'json' :
        { 'entries' :
            [ 2
            , 3
            , 5
            , 6
            , 7
            , 8
            , 9
            , 10
            , 11
            , 12
            , 13
            , 14
            , 15
            , 16
            ]
        , 'url_template' : '/v1/MOM-Id_Entity/{entry}'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/pid?brief'
    }

"""

_test_doc = r"""
    >>> server = run_server (%(p1)s, %(n1)s)

    >>> _ = show (R.get ("/Doc?brief"))
    { 'json' :
        { 'entries' :
            [ 'Auth-Account'
            , 'Auth-Account_in_Group'
            , 'Auth-Certificate'
            , 'Auth-Group'
            , 'Auth-Id_Entity'
            , 'Auth-Link'
            , 'Auth-Link1'
            , 'Auth-Link2'
            , 'Auth-Object'
            , 'Auth-_Account_'
            , 'Auth-_Link_n_'
            , 'MOM-Id_Entity'
            , 'MOM-Link'
            , 'MOM-Link1'
            , 'MOM-Link2'
            , 'MOM-Object'
            , 'MOM-_Link_n_'
            , 'PAP-Address'
            , 'PAP-Address_Position'
            , 'PAP-Company'
            , 'PAP-Company_has_Address'
            , 'PAP-Company_has_Email'
            , 'PAP-Company_has_Phone'
            , 'PAP-Company_has_Url'
            , 'PAP-Email'
            , 'PAP-Group'
            , 'PAP-Id_Entity'
            , 'PAP-Legal_Entity'
            , 'PAP-Link'
            , 'PAP-Link1'
            , 'PAP-Link2'
            , 'PAP-Object'
            , 'PAP-Person'
            , 'PAP-Person_has_Account'
            , 'PAP-Person_has_Address'
            , 'PAP-Person_has_Email'
            , 'PAP-Person_has_Phone'
            , 'PAP-Person_has_Url'
            , 'PAP-Phone'
            , 'PAP-Property'
            , 'PAP-Subject'
            , 'PAP-Subject_has_Address'
            , 'PAP-Subject_has_Email'
            , 'PAP-Subject_has_Phone'
            , 'PAP-Subject_has_Property'
            , 'PAP-Subject_has_Url'
            , 'PAP-Url'
            , 'PAP-_Link_n_'
            , 'SRM-Boat'
            , 'SRM-Boat_Class'
            , 'SRM-Boat_in_Regatta'
            , 'SRM-Club'
            , 'SRM-Crew_Member'
            , 'SRM-Handicap'
            , 'SRM-Id_Entity'
            , 'SRM-Link'
            , 'SRM-Link1'
            , 'SRM-Link2'
            , 'SRM-Object'
            , 'SRM-Page'
            , 'SRM-Race_Result'
            , 'SRM-Regatta'
            , 'SRM-Regatta_C'
            , 'SRM-Regatta_Event'
            , 'SRM-Regatta_H'
            , 'SRM-Sailor'
            , 'SRM-Team'
            , 'SRM-Team_has_Boat_in_Regatta'
            , 'SRM-_Boat_Class_'
            , 'SRM-_Link_n_'
            , 'SWP-Clip_O'
            , 'SWP-Clip_X'
            , 'SWP-Gallery'
            , 'SWP-Id_Entity'
            , 'SWP-Link'
            , 'SWP-Link1'
            , 'SWP-Object'
            , 'SWP-Object_PN'
            , 'SWP-Page'
            , 'SWP-Page_Y'
            , 'SWP-Picture'
            , 'SWP-Referral'
            ]
        , 'url_template' : '/Doc/{entry}'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/Doc?brief'
    }

    >>> _ = show (R.get ("/Doc/SRM-Boat_in_Regatta"), cleaner = json_cleaner)
    { 'json' :
        { 'attributes' :
            { 'editable' :
                [ { 'default_value' : ''
                  , 'description' : 'Boat racing in a regatta.'
                  , 'is_changeable' : True
                  , 'is_required' : True
                  , 'is_settable' : True
                  , 'kind' : 'primary'
                  , 'name' : 'left'
                  , 'p_type' : 'Boat'
                  , 'role_name' : 'boat'
                  , 'type' : 'Boat'
                  , 'type_name' : 'SRM.Boat'
                  , 'ui_name' : 'Boat'
                  , 'url' : '/Doc/SRM-Boat'
                  }
                , { 'default_value' : ''
                  , 'description' : 'Regatta a boat races in.'
                  , 'is_changeable' : True
                  , 'is_required' : True
                  , 'is_settable' : True
                  , 'kind' : 'primary'
                  , 'name' : 'right'
                  , 'p_type' : 'Regatta'
                  , 'role_name' : 'regatta'
                  , 'type' : 'Regatta'
                  , 'type_name' : 'SRM.Regatta'
                  , 'ui_name' : 'Regatta'
                  , 'url' : '/Doc/SRM-Regatta'
                  }
                , { 'default_value' : ''
                  , 'description' : 'Skipper of boat.'
                  , 'is_changeable' : True
                  , 'is_required' : True
                  , 'is_settable' : True
                  , 'kind' : 'required'
                  , 'name' : 'skipper'
                  , 'p_type' : 'Sailor'
                  , 'type' : 'Sailor'
                  , 'type_name' : 'SRM.Sailor'
                  , 'ui_name' : 'Skipper'
                  , 'url' : '/Doc/SRM-Sailor'
                  }
                , { 'default_value' : ''
                  , 'description' : 'Place of boat in this regatta.'
                  , 'example' : 2
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'optional'
                  , 'min_value' : 1
                  , 'name' : 'place'
                  , 'p_type' : 'int'
                  , 'type' : 'Int'
                  , 'ui_name' : 'Place'
                  }
                , { 'default_value' : ''
                  , 'description' : 'Total points of boat in this regatta.'
                  , 'example' : 25
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'optional'
                  , 'min_value' : 1
                  , 'name' : 'points'
                  , 'p_type' : 'int'
                  , 'type' : 'Int'
                  , 'ui_name' : 'Points'
                  }
                , { 'default_value' : '100'
                  , 'description' : 'Yardstick number of boat.'
                  , 'example' : 107
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'optional'
                  , 'min_value' : 50
                  , 'name' : 'yardstick'
                  , 'p_type' : 'int'
                  , 'type' : 'Int'
                  , 'ui_name' : 'Yardstick'
                  }
                ]
            , 'queryable' :
                [ { 'default_value' : ''
                  , 'description' : 'Creation change of the object'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'query'
                  , 'name' : 'creation'
                  , 'p_type' : 'MD_Change'
                  , 'type' : 'Rev_Ref'
                  , 'type_name' : 'MOM.MD_Change'
                  , 'ui_name' : 'Creation'
                  , 'url' : None
                  }
                , { 'default_value' : ''
                  , 'description' : 'Last change of the object'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'query'
                  , 'name' : 'last_change'
                  , 'p_type' : 'MD_Change'
                  , 'type' : 'Rev_Ref'
                  , 'type_name' : 'MOM.MD_Change'
                  , 'ui_name' : 'Last change'
                  , 'url' : None
                  }
                , { 'default_value' : '0'
                  , 'description' : 'Change id of last change for this entity.'
                  , 'example' : '42'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'internal'
                  , 'name' : 'last_cid'
                  , 'p_type' : 'int'
                  , 'type' : 'Int'
                  , 'ui_name' : 'Last cid'
                  }
                , { 'default_value' : ''
                  , 'description' : 'Permanent id of the instance.'
                  , 'example' : '42'
                  , 'explanation' : 'The `pid` is unique over all entities in a given scope. Once\ncreated, the `pid` of an instance never changes and is not ever\nreused for a different instance.\n\nThe `pid` remains unchanged during database migrations.'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'internal'
                  , 'name' : 'pid'
                  , 'p_type' : 'int'
                  , 'type' : 'Surrogate'
                  , 'ui_name' : 'Pid'
                  }
                , { 'default_value' : ''
                  , 'description' : 'Name of type of this entity.'
                  , 'example' : 'foo'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'internal'
                  , 'name' : 'type_name'
                  , 'p_type' : 'str'
                  , 'type' : 'String'
                  , 'ui_name' : 'Type name'
                  }
                , { 'default_value' : '0'
                  , 'description' : 'Rank of registration of boat in regatta.'
                  , 'example' : 13
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'internal'
                  , 'name' : 'rank'
                  , 'p_type' : 'int'
                  , 'type' : 'Int'
                  , 'ui_name' : 'Rank'
                  }
                , { 'date' : <date instance>
                  , 'description' : 'Date of registration.'
                  , 'example' : '2010-10-10'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'internal'
                  , 'name' : 'registration_date'
                  , 'p_type' : 'date'
                  , 'syntax' : 'yyyy-mm-dd'
                  , 'type' : 'Date'
                  , 'ui_name' : 'Registration date'
                  }
                , { 'default_value' : ''
                  , 'description' : '`Race_Result` links'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'query'
                  , 'name' : 'race_results'
                  , 'p_type' : 'Race_Result'
                  , 'role_name' : 'left'
                  , 'type' : 'Link_Ref_List'
                  , 'type_name' : 'SRM.Race_Result'
                  , 'ui_name' : 'Race results'
                  , 'url' : '/Doc/SRM-Race_Result'
                  }
                , { 'default_value' : ''
                  , 'description' : '`Sailor` linked to `Boat_in_Regatta`'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'query'
                  , 'name' : '_crew'
                  , 'p_type' : 'Sailor'
                  , 'role_name' : 'left'
                  , 'type' : 'Role_Ref_Set'
                  , 'type_name' : 'SRM.Sailor'
                  , 'ui_name' : ' crew'
                  , 'url' : '/Doc/SRM-Sailor'
                  }
                , { 'default_value' : ''
                  , 'description' : '`Team` linked to `Boat_in_Regatta`'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'query'
                  , 'name' : 'teams'
                  , 'p_type' : 'Team'
                  , 'role_name' : 'right'
                  , 'type' : 'Role_Ref_Set'
                  , 'type_name' : 'SRM.Team'
                  , 'ui_name' : 'Teams'
                  , 'url' : '/Doc/SRM-Team'
                  }
                ]
            }
        , 'cross_references' :
            [ { 'attributes' : ['left']
              , 'lra' : 'sailor_links'
              , 'type_name' : 'SRM.Crew_Member'
              , 'url' : '/Doc/SRM-Crew_Member'
              }
            , { 'attributes' : ['left']
              , 'lra' : 'race_results'
              , 'type_name' : 'SRM.Race_Result'
              , 'url' : '/Doc/SRM-Race_Result'
              }
            , { 'attributes' : ['right']
              , 'lra' : 'team_links'
              , 'type_name' : 'SRM.Team_has_Boat_in_Regatta'
              , 'url' : '/Doc/SRM-Team_has_Boat_in_Regatta'
              }
            ]
        , 'description' : 'Boat racing in a regatta.'
        , 'is_partial' : False
        , 'parents' :
            [ { 'type_name' : 'SRM.Link2'
              , 'url' : '/Doc/SRM-Link2'
              }
            ]
        , 'type_name' : 'SRM.Boat_in_Regatta'
        , 'ui_name' : 'SRM.Boat_in_Regatta'
        , 'url' : '/Doc/SRM-Boat_in_Regatta'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/Doc/SRM-Boat_in_Regatta'
    }

    >>> _ = show (R.get ("/Doc/SRM-Regatta"), cleaner = json_cleaner)
    { 'json' :
        { 'attributes' :
            { 'editable' :
                [ { 'default_value' : ''
                  , 'description' : 'Regatta event to which this regatta belongs.'
                  , 'is_changeable' : False
                  , 'is_required' : True
                  , 'is_settable' : True
                  , 'kind' : 'primary'
                  , 'name' : 'left'
                  , 'p_type' : 'Regatta_Event'
                  , 'role_name' : 'event'
                  , 'type' : 'Regatta_Event'
                  , 'type_name' : 'SRM.Regatta_Event'
                  , 'ui_name' : 'Event'
                  , 'url' : '/Doc/SRM-Regatta_Event'
                  }
                , { 'default_value' : ''
                  , 'description' : 'Class of boats sailing in this regatta.'
                  , 'is_changeable' : True
                  , 'is_required' : True
                  , 'is_settable' : True
                  , 'kind' : 'primary'
                  , 'name' : 'boat_class'
                  , 'p_type' : '_Boat_Class_'
                  , 'type' : '_Boat_Class_'
                  , 'type_name' : 'SRM._Boat_Class_'
                  , 'ui_name' : 'Boat class'
                  , 'url' : '/Doc/SRM-_Boat_Class_'
                  }
                , { 'default_value' : '0'
                  , 'description' : 'Number of discardable races in regatta'
                  , 'example' : '1'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'optional'
                  , 'max_value' : 32
                  , 'name' : 'discards'
                  , 'p_type' : 'int'
                  , 'type' : 'Int'
                  , 'ui_name' : 'Discards'
                  }
                , { 'Choices' :
                      [ 'no'
                      , 'yes'
                      ]
                  , 'default_value' : ''
                  , 'description' : 'Indicates that the regatta is cancelled'
                  , 'example' : 'no'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'optional'
                  , 'name' : 'is_cancelled'
                  , 'p_type' : 'bool'
                  , 'syntax' : 'The following string values are accepted as valid Boolean values: no, yes'
                  , 'type' : 'Boolean'
                  , 'ui_name' : 'Is cancelled'
                  }
                , { 'default_value' : ''
                  , 'description' : 'Kind of regatta.'
                  , 'example' : 'One race, one beer'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'optional'
                  , 'max_length' : 32
                  , 'name' : 'kind'
                  , 'p_type' : 'str'
                  , 'type' : 'String'
                  , 'ui_name' : 'Kind'
                  }
                , { 'default_value' : '0'
                  , 'description' : 'Number of races sailed in regatta'
                  , 'example' : '7'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'optional'
                  , 'max_value' : 32
                  , 'name' : 'races'
                  , 'p_type' : 'int'
                  , 'type' : 'Int'
                  , 'ui_name' : 'Races'
                  }
                , { 'attributes' :
                      [ { 'default_value' : ''
                        , 'description' : 'Date of regatta result.'
                        , 'example' : '1979-08-18'
                        , 'is_changeable' : True
                        , 'is_required' : False
                        , 'is_settable' : True
                        , 'kind' : 'necessary'
                        , 'name' : 'date'
                        , 'p_type' : 'datetime'
                        , 'syntax' : 'yyyy-mm-dd hh:mm:ss, the time `hh:mm:ss` is optional'
                        , 'type' : 'Date-Time'
                        , 'ui_name' : 'Date'
                        }
                      , { 'default_value' : ''
                        , 'description' : 'Name of software used for managing the regatta.'
                        , 'example' : 'Blowing Bits Inc.'
                        , 'is_changeable' : True
                        , 'is_required' : False
                        , 'is_settable' : True
                        , 'kind' : 'optional'
                        , 'max_length' : 64
                        , 'name' : 'software'
                        , 'p_type' : 'str'
                        , 'type' : 'String'
                        , 'ui_name' : 'Software'
                        }
                      , { 'default_value' : ''
                        , 'description' : 'Status of result (e.g., `preliminary` or `final`).'
                        , 'example' : 'Final'
                        , 'is_changeable' : True
                        , 'is_required' : False
                        , 'is_settable' : True
                        , 'kind' : 'optional'
                        , 'max_length' : 64
                        , 'name' : 'status'
                        , 'p_type' : 'str'
                        , 'type' : 'String'
                        , 'ui_name' : 'Status'
                        }
                      ]
                  , 'default_value' : ''
                  , 'description' : 'Information about result.'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'optional'
                  , 'name' : 'result'
                  , 'p_type' : 'Regatta_Result'
                  , 'type' : 'Regatta_Result'
                  , 'type_name' : 'SRM.Regatta_Result'
                  , 'ui_name' : 'Result'
                  }
                , { 'default_value' : ''
                  , 'description' : 'Number of boats participating in the regatta as relevant for\nfor low-point based formula for ranking list points.'
                  , 'example' : '42'
                  , 'explanation' : 'This is the number of boats that actually participated in the\n`regatta`. If the regatta field was split into groups, it is\nthe maximum number of starters of any group.'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'optional'
                  , 'name' : 'starters_rl'
                  , 'p_type' : 'int'
                  , 'type' : 'Int'
                  , 'ui_name' : 'Starters rl'
                  }
                ]
            , 'queryable' :
                [ { 'default_value' : ''
                  , 'description' : 'Creation change of the object'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'query'
                  , 'name' : 'creation'
                  , 'p_type' : 'MD_Change'
                  , 'type' : 'Rev_Ref'
                  , 'type_name' : 'MOM.MD_Change'
                  , 'ui_name' : 'Creation'
                  , 'url' : None
                  }
                , { 'default_value' : ''
                  , 'description' : 'Last change of the object'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'query'
                  , 'name' : 'last_change'
                  , 'p_type' : 'MD_Change'
                  , 'type' : 'Rev_Ref'
                  , 'type_name' : 'MOM.MD_Change'
                  , 'ui_name' : 'Last change'
                  , 'url' : None
                  }
                , { 'default_value' : '0'
                  , 'description' : 'Change id of last change for this entity.'
                  , 'example' : '42'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'internal'
                  , 'name' : 'last_cid'
                  , 'p_type' : 'int'
                  , 'type' : 'Int'
                  , 'ui_name' : 'Last cid'
                  }
                , { 'default_value' : ''
                  , 'description' : 'Permanent id of the instance.'
                  , 'example' : '42'
                  , 'explanation' : 'The `pid` is unique over all entities in a given scope. Once\ncreated, the `pid` of an instance never changes and is not ever\nreused for a different instance.\n\nThe `pid` remains unchanged during database migrations.'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'internal'
                  , 'name' : 'pid'
                  , 'p_type' : 'int'
                  , 'type' : 'Surrogate'
                  , 'ui_name' : 'Pid'
                  }
                , { 'default_value' : ''
                  , 'description' : 'Name of type of this entity.'
                  , 'example' : 'foo'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'internal'
                  , 'name' : 'type_name'
                  , 'p_type' : 'str'
                  , 'type' : 'String'
                  , 'ui_name' : 'Type name'
                  }
                , { 'default_value' : ''
                  , 'description' : 'A string.'
                  , 'example' : 'foo'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'internal'
                  , 'max_length' : 64
                  , 'name' : 'perma_name'
                  , 'p_type' : 'str'
                  , 'type' : 'String'
                  , 'ui_name' : 'Perma name'
                  }
                , { 'default_value' : ''
                  , 'description' : 'Number of races counted for result of regatta.'
                  , 'example' : '42'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'query'
                  , 'name' : 'races_counted'
                  , 'p_type' : 'int'
                  , 'type' : 'Int'
                  , 'ui_name' : 'Races counted'
                  }
                , { 'default_value' : ''
                  , 'description' : 'A integer value.'
                  , 'example' : '42'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'query'
                  , 'name' : 'year'
                  , 'p_type' : 'int'
                  , 'type' : 'Int'
                  , 'ui_name' : 'Year'
                  }
                ]
            }
        , 'children' :
            [ { 'type_name' : 'SRM.Regatta_C'
              , 'url' : '/Doc/SRM-Regatta_C'
              }
            , { 'type_name' : 'SRM.Regatta_H'
              , 'url' : '/Doc/SRM-Regatta_H'
              }
            ]
        , 'cross_references' :
            [ { 'attributes' : ['right']
              , 'lra' : 'boats'
              , 'type_name' : 'SRM.Boat_in_Regatta'
              , 'url' : '/Doc/SRM-Boat_in_Regatta'
              }
            ]
        , 'description' : 'Sailing regatta for one class or handicap.'
        , 'is_partial' : True
        , 'parents' :
            [ { 'type_name' : 'SRM.Link1'
              , 'url' : '/Doc/SRM-Link1'
              }
            ]
        , 'type_name' : 'SRM.Regatta'
        , 'ui_name' : 'SRM.Regatta'
        , 'url' : '/Doc/SRM-Regatta'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/Doc/SRM-Regatta'
    }

    >>> _ = show (R.get ("/Doc/SRM-Regatta_C"), cleaner = json_cleaner)
    { 'json' :
        { 'attributes' :
            { 'editable' :
                [ { 'default_value' : ''
                  , 'description' : 'Regatta event to which this regatta belongs.'
                  , 'is_changeable' : False
                  , 'is_required' : True
                  , 'is_settable' : True
                  , 'kind' : 'primary'
                  , 'name' : 'left'
                  , 'p_type' : 'Regatta_Event'
                  , 'role_name' : 'event'
                  , 'type' : 'Regatta_Event'
                  , 'type_name' : 'SRM.Regatta_Event'
                  , 'ui_name' : 'Event'
                  , 'url' : '/Doc/SRM-Regatta_Event'
                  }
                , { 'default_value' : ''
                  , 'description' : 'Class of boats sailing in this regatta.'
                  , 'is_changeable' : True
                  , 'is_required' : True
                  , 'is_settable' : True
                  , 'kind' : 'primary'
                  , 'name' : 'boat_class'
                  , 'p_type' : 'Boat_Class'
                  , 'type' : 'Boat_Class'
                  , 'type_name' : 'SRM.Boat_Class'
                  , 'ui_name' : 'Boat class'
                  , 'url' : '/Doc/SRM-Boat_Class'
                  }
                , { 'default_value' : '0'
                  , 'description' : 'Number of discardable races in regatta'
                  , 'example' : '1'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'optional'
                  , 'max_value' : 32
                  , 'name' : 'discards'
                  , 'p_type' : 'int'
                  , 'type' : 'Int'
                  , 'ui_name' : 'Discards'
                  }
                , { 'Choices' :
                      [ 'no'
                      , 'yes'
                      ]
                  , 'default_value' : ''
                  , 'description' : 'Indicates that the regatta is cancelled'
                  , 'example' : 'no'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'optional'
                  , 'name' : 'is_cancelled'
                  , 'p_type' : 'bool'
                  , 'syntax' : 'The following string values are accepted as valid Boolean values: no, yes'
                  , 'type' : 'Boolean'
                  , 'ui_name' : 'Is cancelled'
                  }
                , { 'default_value' : ''
                  , 'description' : 'Kind of regatta.'
                  , 'example' : 'One race, one beer'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'optional'
                  , 'max_length' : 32
                  , 'name' : 'kind'
                  , 'p_type' : 'str'
                  , 'type' : 'String'
                  , 'ui_name' : 'Kind'
                  }
                , { 'default_value' : '0'
                  , 'description' : 'Number of races sailed in regatta'
                  , 'example' : '7'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'optional'
                  , 'max_value' : 32
                  , 'name' : 'races'
                  , 'p_type' : 'int'
                  , 'type' : 'Int'
                  , 'ui_name' : 'Races'
                  }
                , { 'attributes' :
                      [ { 'default_value' : ''
                        , 'description' : 'Date of regatta result.'
                        , 'example' : '1979-08-18'
                        , 'is_changeable' : True
                        , 'is_required' : False
                        , 'is_settable' : True
                        , 'kind' : 'necessary'
                        , 'name' : 'date'
                        , 'p_type' : 'datetime'
                        , 'syntax' : 'yyyy-mm-dd hh:mm:ss, the time `hh:mm:ss` is optional'
                        , 'type' : 'Date-Time'
                        , 'ui_name' : 'Date'
                        }
                      , { 'default_value' : ''
                        , 'description' : 'Name of software used for managing the regatta.'
                        , 'example' : 'Blowing Bits Inc.'
                        , 'is_changeable' : True
                        , 'is_required' : False
                        , 'is_settable' : True
                        , 'kind' : 'optional'
                        , 'max_length' : 64
                        , 'name' : 'software'
                        , 'p_type' : 'str'
                        , 'type' : 'String'
                        , 'ui_name' : 'Software'
                        }
                      , { 'default_value' : ''
                        , 'description' : 'Status of result (e.g., `preliminary` or `final`).'
                        , 'example' : 'Final'
                        , 'is_changeable' : True
                        , 'is_required' : False
                        , 'is_settable' : True
                        , 'kind' : 'optional'
                        , 'max_length' : 64
                        , 'name' : 'status'
                        , 'p_type' : 'str'
                        , 'type' : 'String'
                        , 'ui_name' : 'Status'
                        }
                      ]
                  , 'default_value' : ''
                  , 'description' : 'Information about result.'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'optional'
                  , 'name' : 'result'
                  , 'p_type' : 'Regatta_Result'
                  , 'type' : 'Regatta_Result'
                  , 'type_name' : 'SRM.Regatta_Result'
                  , 'ui_name' : 'Result'
                  }
                , { 'default_value' : ''
                  , 'description' : 'Number of boats participating in the regatta as relevant for\nfor low-point based formula for ranking list points.'
                  , 'example' : '42'
                  , 'explanation' : 'This is the number of boats that actually participated in the\n`regatta`. If the regatta field was split into groups, it is\nthe maximum number of starters of any group.'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'optional'
                  , 'name' : 'starters_rl'
                  , 'p_type' : 'int'
                  , 'type' : 'Int'
                  , 'ui_name' : 'Starters rl'
                  }
                , { 'Choices' :
                      [ 'no'
                      , 'yes'
                      ]
                  , 'default_value' : 'no'
                  , 'description' : 'Boolean attribute.'
                  , 'example' : 'no'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'optional'
                  , 'name' : 'is_team_race'
                  , 'p_type' : 'bool'
                  , 'syntax' : 'The following string values are accepted as valid Boolean values: no, yes'
                  , 'type' : 'Boolean'
                  , 'ui_name' : 'Is team race'
                  }
                ]
            , 'queryable' :
                [ { 'default_value' : ''
                  , 'description' : 'Creation change of the object'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'query'
                  , 'name' : 'creation'
                  , 'p_type' : 'MD_Change'
                  , 'type' : 'Rev_Ref'
                  , 'type_name' : 'MOM.MD_Change'
                  , 'ui_name' : 'Creation'
                  , 'url' : None
                  }
                , { 'default_value' : ''
                  , 'description' : 'Last change of the object'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'query'
                  , 'name' : 'last_change'
                  , 'p_type' : 'MD_Change'
                  , 'type' : 'Rev_Ref'
                  , 'type_name' : 'MOM.MD_Change'
                  , 'ui_name' : 'Last change'
                  , 'url' : None
                  }
                , { 'default_value' : '0'
                  , 'description' : 'Change id of last change for this entity.'
                  , 'example' : '42'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'internal'
                  , 'name' : 'last_cid'
                  , 'p_type' : 'int'
                  , 'type' : 'Int'
                  , 'ui_name' : 'Last cid'
                  }
                , { 'default_value' : ''
                  , 'description' : 'Permanent id of the instance.'
                  , 'example' : '42'
                  , 'explanation' : 'The `pid` is unique over all entities in a given scope. Once\ncreated, the `pid` of an instance never changes and is not ever\nreused for a different instance.\n\nThe `pid` remains unchanged during database migrations.'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'internal'
                  , 'name' : 'pid'
                  , 'p_type' : 'int'
                  , 'type' : 'Surrogate'
                  , 'ui_name' : 'Pid'
                  }
                , { 'default_value' : ''
                  , 'description' : 'Name of type of this entity.'
                  , 'example' : 'foo'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'internal'
                  , 'name' : 'type_name'
                  , 'p_type' : 'str'
                  , 'type' : 'String'
                  , 'ui_name' : 'Type name'
                  }
                , { 'default_value' : ''
                  , 'description' : 'A string.'
                  , 'example' : 'foo'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'internal'
                  , 'max_length' : 64
                  , 'name' : 'perma_name'
                  , 'p_type' : 'str'
                  , 'type' : 'String'
                  , 'ui_name' : 'Perma name'
                  }
                , { 'default_value' : ''
                  , 'description' : 'Number of races counted for result of regatta.'
                  , 'example' : '42'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'query'
                  , 'name' : 'races_counted'
                  , 'p_type' : 'int'
                  , 'type' : 'Int'
                  , 'ui_name' : 'Races counted'
                  }
                , { 'default_value' : ''
                  , 'description' : 'A integer value.'
                  , 'example' : '42'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'query'
                  , 'name' : 'year'
                  , 'p_type' : 'int'
                  , 'type' : 'Int'
                  , 'ui_name' : 'Year'
                  }
                , { 'default_value' : ''
                  , 'description' : 'A integer value.'
                  , 'example' : '42'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'query'
                  , 'name' : 'max_crew'
                  , 'p_type' : 'int'
                  , 'type' : 'Int'
                  , 'ui_name' : 'Max crew'
                  }
                , { 'default_value' : ''
                  , 'description' : '`Team` links'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'query'
                  , 'name' : 'teams'
                  , 'p_type' : 'Team'
                  , 'role_name' : 'left'
                  , 'type' : 'Link_Ref_List'
                  , 'type_name' : 'SRM.Team'
                  , 'ui_name' : 'Teams'
                  , 'url' : '/Doc/SRM-Team'
                  }
                ]
            }
        , 'cross_references' :
            [ { 'attributes' : ['right']
              , 'lra' : 'boats'
              , 'type_name' : 'SRM.Boat_in_Regatta'
              , 'url' : '/Doc/SRM-Boat_in_Regatta'
              }
            , { 'attributes' : ['left']
              , 'lra' : 'teams'
              , 'type_name' : 'SRM.Team'
              , 'url' : '/Doc/SRM-Team'
              }
            ]
        , 'description' : 'Regatta for a single class of sail boats.'
        , 'is_partial' : False
        , 'parents' :
            [ { 'type_name' : 'SRM.Regatta'
              , 'url' : '/Doc/SRM-Regatta'
              }
            ]
        , 'relevant_root' :
            { 'type_name' : 'SRM.Regatta'
            , 'url' : '/Doc/SRM-Regatta'
            }
        , 'type_name' : 'SRM.Regatta_C'
        , 'ui_name' : 'SRM.Regatta_C'
        , 'url' : '/Doc/SRM-Regatta_C'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/Doc/SRM-Regatta_C'
    }

    >>> _ = show (R.get ("/Doc/SRM-Regatta_H"), cleaner = json_cleaner)
    { 'json' :
        { 'attributes' :
            { 'editable' :
                [ { 'default_value' : ''
                  , 'description' : 'Regatta event to which this regatta belongs.'
                  , 'is_changeable' : False
                  , 'is_required' : True
                  , 'is_settable' : True
                  , 'kind' : 'primary'
                  , 'name' : 'left'
                  , 'p_type' : 'Regatta_Event'
                  , 'role_name' : 'event'
                  , 'type' : 'Regatta_Event'
                  , 'type_name' : 'SRM.Regatta_Event'
                  , 'ui_name' : 'Event'
                  , 'url' : '/Doc/SRM-Regatta_Event'
                  }
                , { 'default_value' : ''
                  , 'description' : 'Name of handicap system used for this regatta.'
                  , 'is_changeable' : True
                  , 'is_required' : True
                  , 'is_settable' : True
                  , 'kind' : 'primary'
                  , 'name' : 'boat_class'
                  , 'p_type' : 'Handicap'
                  , 'type' : 'Handicap'
                  , 'type_name' : 'SRM.Handicap'
                  , 'ui_name' : 'Handicap'
                  , 'url' : '/Doc/SRM-Handicap'
                  }
                , { 'default_value' : '0'
                  , 'description' : 'Number of discardable races in regatta'
                  , 'example' : '1'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'optional'
                  , 'max_value' : 32
                  , 'name' : 'discards'
                  , 'p_type' : 'int'
                  , 'type' : 'Int'
                  , 'ui_name' : 'Discards'
                  }
                , { 'Choices' :
                      [ 'no'
                      , 'yes'
                      ]
                  , 'default_value' : ''
                  , 'description' : 'Indicates that the regatta is cancelled'
                  , 'example' : 'no'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'optional'
                  , 'name' : 'is_cancelled'
                  , 'p_type' : 'bool'
                  , 'syntax' : 'The following string values are accepted as valid Boolean values: no, yes'
                  , 'type' : 'Boolean'
                  , 'ui_name' : 'Is cancelled'
                  }
                , { 'default_value' : ''
                  , 'description' : 'Kind of regatta.'
                  , 'example' : 'One race, one beer'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'optional'
                  , 'max_length' : 32
                  , 'name' : 'kind'
                  , 'p_type' : 'str'
                  , 'type' : 'String'
                  , 'ui_name' : 'Kind'
                  }
                , { 'default_value' : '0'
                  , 'description' : 'Number of races sailed in regatta'
                  , 'example' : '7'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'optional'
                  , 'max_value' : 32
                  , 'name' : 'races'
                  , 'p_type' : 'int'
                  , 'type' : 'Int'
                  , 'ui_name' : 'Races'
                  }
                , { 'attributes' :
                      [ { 'default_value' : ''
                        , 'description' : 'Date of regatta result.'
                        , 'example' : '1979-08-18'
                        , 'is_changeable' : True
                        , 'is_required' : False
                        , 'is_settable' : True
                        , 'kind' : 'necessary'
                        , 'name' : 'date'
                        , 'p_type' : 'datetime'
                        , 'syntax' : 'yyyy-mm-dd hh:mm:ss, the time `hh:mm:ss` is optional'
                        , 'type' : 'Date-Time'
                        , 'ui_name' : 'Date'
                        }
                      , { 'default_value' : ''
                        , 'description' : 'Name of software used for managing the regatta.'
                        , 'example' : 'Blowing Bits Inc.'
                        , 'is_changeable' : True
                        , 'is_required' : False
                        , 'is_settable' : True
                        , 'kind' : 'optional'
                        , 'max_length' : 64
                        , 'name' : 'software'
                        , 'p_type' : 'str'
                        , 'type' : 'String'
                        , 'ui_name' : 'Software'
                        }
                      , { 'default_value' : ''
                        , 'description' : 'Status of result (e.g., `preliminary` or `final`).'
                        , 'example' : 'Final'
                        , 'is_changeable' : True
                        , 'is_required' : False
                        , 'is_settable' : True
                        , 'kind' : 'optional'
                        , 'max_length' : 64
                        , 'name' : 'status'
                        , 'p_type' : 'str'
                        , 'type' : 'String'
                        , 'ui_name' : 'Status'
                        }
                      ]
                  , 'default_value' : ''
                  , 'description' : 'Information about result.'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'optional'
                  , 'name' : 'result'
                  , 'p_type' : 'Regatta_Result'
                  , 'type' : 'Regatta_Result'
                  , 'type_name' : 'SRM.Regatta_Result'
                  , 'ui_name' : 'Result'
                  }
                , { 'default_value' : ''
                  , 'description' : 'Number of boats participating in the regatta as relevant for\nfor low-point based formula for ranking list points.'
                  , 'example' : '42'
                  , 'explanation' : 'This is the number of boats that actually participated in the\n`regatta`. If the regatta field was split into groups, it is\nthe maximum number of starters of any group.'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'optional'
                  , 'name' : 'starters_rl'
                  , 'p_type' : 'int'
                  , 'type' : 'Int'
                  , 'ui_name' : 'Starters rl'
                  }
                ]
            , 'queryable' :
                [ { 'default_value' : ''
                  , 'description' : 'Creation change of the object'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'query'
                  , 'name' : 'creation'
                  , 'p_type' : 'MD_Change'
                  , 'type' : 'Rev_Ref'
                  , 'type_name' : 'MOM.MD_Change'
                  , 'ui_name' : 'Creation'
                  , 'url' : None
                  }
                , { 'default_value' : ''
                  , 'description' : 'Last change of the object'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'query'
                  , 'name' : 'last_change'
                  , 'p_type' : 'MD_Change'
                  , 'type' : 'Rev_Ref'
                  , 'type_name' : 'MOM.MD_Change'
                  , 'ui_name' : 'Last change'
                  , 'url' : None
                  }
                , { 'default_value' : '0'
                  , 'description' : 'Change id of last change for this entity.'
                  , 'example' : '42'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'internal'
                  , 'name' : 'last_cid'
                  , 'p_type' : 'int'
                  , 'type' : 'Int'
                  , 'ui_name' : 'Last cid'
                  }
                , { 'default_value' : ''
                  , 'description' : 'Permanent id of the instance.'
                  , 'example' : '42'
                  , 'explanation' : 'The `pid` is unique over all entities in a given scope. Once\ncreated, the `pid` of an instance never changes and is not ever\nreused for a different instance.\n\nThe `pid` remains unchanged during database migrations.'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'internal'
                  , 'name' : 'pid'
                  , 'p_type' : 'int'
                  , 'type' : 'Surrogate'
                  , 'ui_name' : 'Pid'
                  }
                , { 'default_value' : ''
                  , 'description' : 'Name of type of this entity.'
                  , 'example' : 'foo'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'internal'
                  , 'name' : 'type_name'
                  , 'p_type' : 'str'
                  , 'type' : 'String'
                  , 'ui_name' : 'Type name'
                  }
                , { 'default_value' : ''
                  , 'description' : 'A string.'
                  , 'example' : 'foo'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'internal'
                  , 'max_length' : 64
                  , 'name' : 'perma_name'
                  , 'p_type' : 'str'
                  , 'type' : 'String'
                  , 'ui_name' : 'Perma name'
                  }
                , { 'default_value' : ''
                  , 'description' : 'Number of races counted for result of regatta.'
                  , 'example' : '42'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'query'
                  , 'name' : 'races_counted'
                  , 'p_type' : 'int'
                  , 'type' : 'Int'
                  , 'ui_name' : 'Races counted'
                  }
                , { 'default_value' : ''
                  , 'description' : 'A integer value.'
                  , 'example' : '42'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'query'
                  , 'name' : 'year'
                  , 'p_type' : 'int'
                  , 'type' : 'Int'
                  , 'ui_name' : 'Year'
                  }
                ]
            }
        , 'cross_references' :
            [ { 'attributes' : ['right']
              , 'lra' : 'boats'
              , 'type_name' : 'SRM.Boat_in_Regatta'
              , 'url' : '/Doc/SRM-Boat_in_Regatta'
              }
            ]
        , 'description' : 'Regatta for boats in a handicap system.'
        , 'is_partial' : False
        , 'parents' :
            [ { 'type_name' : 'SRM.Regatta'
              , 'url' : '/Doc/SRM-Regatta'
              }
            ]
        , 'relevant_root' :
            { 'type_name' : 'SRM.Regatta'
            , 'url' : '/Doc/SRM-Regatta'
            }
        , 'type_name' : 'SRM.Regatta_H'
        , 'ui_name' : 'SRM.Regatta_H'
        , 'url' : '/Doc/SRM-Regatta_H'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/Doc/SRM-Regatta_H'
    }

    >>> _ = show (R.get ("/Doc/SRM-Crew_Member"), cleaner = json_cleaner)
    { 'json' :
        { 'attributes' :
            { 'editable' :
                [ { 'default_value' : ''
                  , 'description' : '`Boat_in_Regatta` the crew member sails on.'
                  , 'is_changeable' : True
                  , 'is_required' : True
                  , 'is_settable' : True
                  , 'kind' : 'primary'
                  , 'name' : 'left'
                  , 'p_type' : 'Boat_in_Regatta'
                  , 'role_name' : 'boat_in_regatta'
                  , 'type' : 'Boat_in_Regatta'
                  , 'type_name' : 'SRM.Boat_in_Regatta'
                  , 'ui_name' : 'Boat in regatta'
                  , 'url' : '/Doc/SRM-Boat_in_Regatta'
                  }
                , { 'default_value' : ''
                  , 'description' : 'Person which sails as crew member on `boat_in_regatta`'
                  , 'is_changeable' : True
                  , 'is_required' : True
                  , 'is_settable' : True
                  , 'kind' : 'primary'
                  , 'name' : 'right'
                  , 'p_type' : 'Sailor'
                  , 'role_name' : 'sailor'
                  , 'type' : 'Sailor'
                  , 'type_name' : 'SRM.Sailor'
                  , 'ui_name' : 'Sailor'
                  , 'url' : '/Doc/SRM-Sailor'
                  }
                , { 'default_value' : '0'
                  , 'description' : 'The crew members of a boat will be sorted by `key`, if\ndefined, by order of creation otherwise.'
                  , 'example' : 7
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'optional'
                  , 'name' : 'key'
                  , 'p_type' : 'int'
                  , 'type' : 'Int'
                  , 'ui_name' : 'Key'
                  }
                , { 'default_value' : ''
                  , 'description' : 'Role of crew member.'
                  , 'example' : 'trimmer'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'optional'
                  , 'max_length' : 32
                  , 'name' : 'role'
                  , 'p_type' : 'str'
                  , 'type' : 'String'
                  , 'ui_name' : 'Role'
                  }
                ]
            , 'queryable' :
                [ { 'default_value' : ''
                  , 'description' : 'Creation change of the object'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'query'
                  , 'name' : 'creation'
                  , 'p_type' : 'MD_Change'
                  , 'type' : 'Rev_Ref'
                  , 'type_name' : 'MOM.MD_Change'
                  , 'ui_name' : 'Creation'
                  , 'url' : None
                  }
                , { 'default_value' : ''
                  , 'description' : 'Last change of the object'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'query'
                  , 'name' : 'last_change'
                  , 'p_type' : 'MD_Change'
                  , 'type' : 'Rev_Ref'
                  , 'type_name' : 'MOM.MD_Change'
                  , 'ui_name' : 'Last change'
                  , 'url' : None
                  }
                , { 'default_value' : '0'
                  , 'description' : 'Change id of last change for this entity.'
                  , 'example' : '42'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'internal'
                  , 'name' : 'last_cid'
                  , 'p_type' : 'int'
                  , 'type' : 'Int'
                  , 'ui_name' : 'Last cid'
                  }
                , { 'default_value' : ''
                  , 'description' : 'Permanent id of the instance.'
                  , 'example' : '42'
                  , 'explanation' : 'The `pid` is unique over all entities in a given scope. Once\ncreated, the `pid` of an instance never changes and is not ever\nreused for a different instance.\n\nThe `pid` remains unchanged during database migrations.'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'internal'
                  , 'name' : 'pid'
                  , 'p_type' : 'int'
                  , 'type' : 'Surrogate'
                  , 'ui_name' : 'Pid'
                  }
                , { 'default_value' : ''
                  , 'description' : 'Name of type of this entity.'
                  , 'example' : 'foo'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'internal'
                  , 'name' : 'type_name'
                  , 'p_type' : 'str'
                  , 'type' : 'String'
                  , 'ui_name' : 'Type name'
                  }
                ]
            }
        , 'description' : 'Crew member of a `Boat_in_Regatta`.'
        , 'is_partial' : False
        , 'parents' :
            [ { 'type_name' : 'SRM.Link2'
              , 'url' : '/Doc/SRM-Link2'
              }
            ]
        , 'type_name' : 'SRM.Crew_Member'
        , 'ui_name' : 'SRM.Crew_Member'
        , 'url' : '/Doc/SRM-Crew_Member'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/Doc/SRM-Crew_Member'
    }

"""

_test_example_1 = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> print ("Count before loop:", scope.MOM.Id_Entity.count)
    Count before loop: 16

    >>> for tn in sorted (scope.MOM.Id_Entity.children_np) :
    ...     ETM = scope [tn]
    ...     exa = ETM.example ()
    ...     print (tn, ":", portable_repr (exa.epk_raw) if exa is not None else "------")
    Auth.Account : ('foo@bar.baz', 'Auth.Account')
    Auth.Account_Activation : (('foo@bar.baz', 'Auth.Account'), 'Auth.Account_Activation')
    Auth.Account_EMail_Verification : ------
    Auth.Account_Password_Change_Required : (('foo@bar.baz', 'Auth.Account'), 'Auth.Account_Password_Change_Required')
    Auth.Account_Password_Reset : ------
    Auth.Account_in_Group : (('foo@bar.baz', 'Auth.Account'), ('foo', 'Auth.Group'), 'Auth.Account_in_Group')
    Auth.Certificate : ('foo@bar.baz', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'foo', 'Auth.Certificate')
    Auth.Group : ('foo', 'Auth.Group')
    PAP.Address : ('Mystery Lane 42', '9876', 'Middletown', 'Land Of The Brave', 'PAP.Address')
    PAP.Address_Position : (('Mystery Lane 42', '9876', 'Middletown', 'Land Of The Brave', 'PAP.Address'), 'PAP.Address_Position')
    PAP.Company : ('John Doe, Inc.', 'NY', 'PAP.Company')
    PAP.Company_has_Address : (('John Doe, Inc.', 'NY', 'PAP.Company'), ('Mystery Lane 42', '9876', 'Middletown', 'Land Of The Brave', 'PAP.Address'), 'PAP.Company_has_Address')
    PAP.Company_has_Email : (('John Doe, Inc.', 'NY', 'PAP.Company'), ('john.doe@example.com', 'PAP.Email'), 'PAP.Company_has_Email')
    PAP.Company_has_Phone : (('John Doe, Inc.', 'NY', 'PAP.Company'), ('+43', '1', '234567', 'PAP.Phone'), '99', 'PAP.Company_has_Phone')
    PAP.Company_has_Url : (('John Doe, Inc.', 'NY', 'PAP.Company'), ('http://xkcd.com/327/', 'PAP.Url'), 'PAP.Company_has_Url')
    PAP.Email : ('john.doe@example.com', 'PAP.Email')
    PAP.Person : ('Doe', 'John', 'F.', 'Dr.', 'PAP.Person')
    PAP.Person_has_Account : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), ('foo@bar.baz', 'Auth.Account'), 'PAP.Person_has_Account')
    PAP.Person_has_Address : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), ('Mystery Lane 42', '9876', 'Middletown', 'Land Of The Brave', 'PAP.Address'), 'PAP.Person_has_Address')
    PAP.Person_has_Email : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), ('john.doe@example.com', 'PAP.Email'), 'PAP.Person_has_Email')
    PAP.Person_has_Phone : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), ('+43', '1', '234567', 'PAP.Phone'), '99', 'PAP.Person_has_Phone')
    PAP.Person_has_Url : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), ('http://xkcd.com/327/', 'PAP.Url'), 'PAP.Person_has_Url')
    PAP.Phone : ('+43', '1', '234567', 'PAP.Phone')
    PAP.Url : ('http://xkcd.com/327/', 'PAP.Url')
    SRM.Boat : (('Laser', 'SRM.Boat_Class'), '2827', 'AUT', 'X', 'SRM.Boat')
    SRM.Boat_Class : ('Laser', 'SRM.Boat_Class')
    SRM.Boat_in_Regatta : ((('Laser', 'SRM.Boat_Class'), '2827', 'AUT', 'X', 'SRM.Boat'), (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta')
    SRM.Club : ('RORC', 'SRM.Club')
    SRM.Crew_Member : (((('Laser', 'SRM.Boat_Class'), '2827', 'AUT', 'X', 'SRM.Boat'), (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), 'AUT', '499999', ('RORC', 'SRM.Club'), 'SRM.Sailor'), 'SRM.Crew_Member')
    SRM.Handicap : ('IRC', 'SRM.Handicap')
    SRM.Page : ('20101010_000042_137', ('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), 'SRM.Page')
    SRM.Race_Result : (((('Laser', 'SRM.Boat_Class'), '2827', 'AUT', 'X', 'SRM.Boat'), (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), '5', 'SRM.Race_Result')
    SRM.Regatta_C : (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C')
    SRM.Regatta_Event : ('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event')
    SRM.Regatta_H : (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('IRC', 'SRM.Handicap'), 'SRM.Regatta_H')
    SRM.Sailor : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), 'AUT', '499999', ('RORC', 'SRM.Club'), 'SRM.Sailor')
    SRM.Team : ((('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'foo', 'SRM.Team')
    SRM.Team_has_Boat_in_Regatta : (((('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'foo', 'SRM.Team'), ((('Laser', 'SRM.Boat_Class'), '2827', 'AUT', 'X', 'SRM.Boat'), (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), 'SRM.Team_has_Boat_in_Regatta')
    SWP.Clip_O : (('20101010_000042_137', 'SWP.Page'), (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SWP.Clip_O')
    SWP.Gallery : ('20101010_000042_137', 'SWP.Gallery')
    SWP.Page : ('20101010_000042_137', 'SWP.Page')
    SWP.Picture : (('20101010_000042_137', 'SWP.Gallery'), '42', 'SWP.Picture')
    SWP.Referral : ('/bar', '20101010_000042_137', 'SWP.Referral')

    >>> print ("Count after loop:", scope.MOM.Id_Entity.count)
    Count after loop: 16

"""

_test_example_2 = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> for tn in sorted (scope.MOM.Id_Entity.children_np) : ### nummero 2
    ...     ETM = scope [tn]
    ...     exa = ETM.example ()
    ...     print (tn, ":", portable_repr (exa.epk_raw) if exa is not None else "------")
    Auth.Account : ('foo@bar.baz', 'Auth.Account')
    Auth.Account_Activation : (('foo@bar.baz', 'Auth.Account'), 'Auth.Account_Activation')
    Auth.Account_EMail_Verification : ------
    Auth.Account_Password_Change_Required : (('foo@bar.baz', 'Auth.Account'), 'Auth.Account_Password_Change_Required')
    Auth.Account_Password_Reset : ------
    Auth.Account_in_Group : (('foo@bar.baz', 'Auth.Account'), ('foo', 'Auth.Group'), 'Auth.Account_in_Group')
    Auth.Certificate : ('foo@bar.baz', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'foo', 'Auth.Certificate')
    Auth.Group : ('foo', 'Auth.Group')
    PAP.Address : ('Mystery Lane 42', '9876', 'Middletown', 'Land Of The Brave', 'PAP.Address')
    PAP.Address_Position : (('Mystery Lane 42', '9876', 'Middletown', 'Land Of The Brave', 'PAP.Address'), 'PAP.Address_Position')
    PAP.Company : ('John Doe, Inc.', 'NY', 'PAP.Company')
    PAP.Company_has_Address : (('John Doe, Inc.', 'NY', 'PAP.Company'), ('Mystery Lane 42', '9876', 'Middletown', 'Land Of The Brave', 'PAP.Address'), 'PAP.Company_has_Address')
    PAP.Company_has_Email : (('John Doe, Inc.', 'NY', 'PAP.Company'), ('john.doe@example.com', 'PAP.Email'), 'PAP.Company_has_Email')
    PAP.Company_has_Phone : (('John Doe, Inc.', 'NY', 'PAP.Company'), ('+43', '1', '234567', 'PAP.Phone'), '99', 'PAP.Company_has_Phone')
    PAP.Company_has_Url : (('John Doe, Inc.', 'NY', 'PAP.Company'), ('http://xkcd.com/327/', 'PAP.Url'), 'PAP.Company_has_Url')
    PAP.Email : ('john.doe@example.com', 'PAP.Email')
    PAP.Person : ('Doe', 'John', 'F.', 'Dr.', 'PAP.Person')
    PAP.Person_has_Account : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), ('foo@bar.baz', 'Auth.Account'), 'PAP.Person_has_Account')
    PAP.Person_has_Address : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), ('Mystery Lane 42', '9876', 'Middletown', 'Land Of The Brave', 'PAP.Address'), 'PAP.Person_has_Address')
    PAP.Person_has_Email : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), ('john.doe@example.com', 'PAP.Email'), 'PAP.Person_has_Email')
    PAP.Person_has_Phone : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), ('+43', '1', '234567', 'PAP.Phone'), '99', 'PAP.Person_has_Phone')
    PAP.Person_has_Url : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), ('http://xkcd.com/327/', 'PAP.Url'), 'PAP.Person_has_Url')
    PAP.Phone : ('+43', '1', '234567', 'PAP.Phone')
    PAP.Url : ('http://xkcd.com/327/', 'PAP.Url')
    SRM.Boat : (('Laser', 'SRM.Boat_Class'), '2827', 'AUT', 'X', 'SRM.Boat')
    SRM.Boat_Class : ('Laser', 'SRM.Boat_Class')
    SRM.Boat_in_Regatta : ((('Laser', 'SRM.Boat_Class'), '2827', 'AUT', 'X', 'SRM.Boat'), (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta')
    SRM.Club : ('RORC', 'SRM.Club')
    SRM.Crew_Member : (((('Laser', 'SRM.Boat_Class'), '2827', 'AUT', 'X', 'SRM.Boat'), (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), 'AUT', '499999', ('RORC', 'SRM.Club'), 'SRM.Sailor'), 'SRM.Crew_Member')
    SRM.Handicap : ('IRC', 'SRM.Handicap')
    SRM.Page : ('20101010_000042_137', ('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), 'SRM.Page')
    SRM.Race_Result : (((('Laser', 'SRM.Boat_Class'), '2827', 'AUT', 'X', 'SRM.Boat'), (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), '5', 'SRM.Race_Result')
    SRM.Regatta_C : (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C')
    SRM.Regatta_Event : ('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event')
    SRM.Regatta_H : (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('IRC', 'SRM.Handicap'), 'SRM.Regatta_H')
    SRM.Sailor : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), 'AUT', '499999', ('RORC', 'SRM.Club'), 'SRM.Sailor')
    SRM.Team : ((('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'foo', 'SRM.Team')
    SRM.Team_has_Boat_in_Regatta : (((('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'foo', 'SRM.Team'), ((('Laser', 'SRM.Boat_Class'), '2827', 'AUT', 'X', 'SRM.Boat'), (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), 'SRM.Team_has_Boat_in_Regatta')
    SWP.Clip_O : (('20101010_000042_137', 'SWP.Page'), (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SWP.Clip_O')
    SWP.Gallery : ('20101010_000042_137', 'SWP.Gallery')
    SWP.Page : ('20101010_000042_137', 'SWP.Page')
    SWP.Picture : (('20101010_000042_137', 'SWP.Gallery'), '42', 'SWP.Picture')
    SWP.Referral : ('/bar', '20101010_000042_137', 'SWP.Referral')


"""

_test_example_3 = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> for tn in sorted (scope.MOM.Id_Entity.children_np, reverse = True) :
    ...     ETM = scope [tn]
    ...     exa = ETM.example ()
    ...     print (tn, ":", portable_repr (exa.epk_raw) if exa is not None else "------")
    SWP.Referral : ('/bar', '20101010_000042_137', 'SWP.Referral')
    SWP.Picture : (('20101010_000042_137', 'SWP.Gallery'), '42', 'SWP.Picture')
    SWP.Page : ('20101010_000042_137', 'SWP.Page')
    SWP.Gallery : ('20101010_000042_137', 'SWP.Gallery')
    SWP.Clip_O : (('20101010_000042_137', 'SWP.Page'), (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SWP.Clip_O')
    SRM.Team_has_Boat_in_Regatta : (((('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'foo', 'SRM.Team'), ((('Laser', 'SRM.Boat_Class'), '2827', 'AUT', 'X', 'SRM.Boat'), (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), 'SRM.Team_has_Boat_in_Regatta')
    SRM.Team : ((('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'foo', 'SRM.Team')
    SRM.Sailor : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), 'AUT', '499999', ('RORC', 'SRM.Club'), 'SRM.Sailor')
    SRM.Regatta_H : (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('IRC', 'SRM.Handicap'), 'SRM.Regatta_H')
    SRM.Regatta_Event : ('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event')
    SRM.Regatta_C : (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C')
    SRM.Race_Result : (((('Laser', 'SRM.Boat_Class'), '2827', 'AUT', 'X', 'SRM.Boat'), (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), '5', 'SRM.Race_Result')
    SRM.Page : ('20101010_000042_137', ('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), 'SRM.Page')
    SRM.Handicap : ('IRC', 'SRM.Handicap')
    SRM.Crew_Member : (((('Laser', 'SRM.Boat_Class'), '2827', 'AUT', 'X', 'SRM.Boat'), (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), 'AUT', '499999', ('RORC', 'SRM.Club'), 'SRM.Sailor'), 'SRM.Crew_Member')
    SRM.Club : ('RORC', 'SRM.Club')
    SRM.Boat_in_Regatta : ((('Laser', 'SRM.Boat_Class'), '2827', 'AUT', 'X', 'SRM.Boat'), (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta')
    SRM.Boat_Class : ('Laser', 'SRM.Boat_Class')
    SRM.Boat : (('Laser', 'SRM.Boat_Class'), '2827', 'AUT', 'X', 'SRM.Boat')
    PAP.Url : ('http://xkcd.com/327/', 'PAP.Url')
    PAP.Phone : ('+43', '1', '234567', 'PAP.Phone')
    PAP.Person_has_Url : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), ('http://xkcd.com/327/', 'PAP.Url'), 'PAP.Person_has_Url')
    PAP.Person_has_Phone : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), ('+43', '1', '234567', 'PAP.Phone'), '99', 'PAP.Person_has_Phone')
    PAP.Person_has_Email : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), ('john.doe@example.com', 'PAP.Email'), 'PAP.Person_has_Email')
    PAP.Person_has_Address : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), ('Mystery Lane 42', '9876', 'Middletown', 'Land Of The Brave', 'PAP.Address'), 'PAP.Person_has_Address')
    PAP.Person_has_Account : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), ('foo@bar.baz', 'Auth.Account'), 'PAP.Person_has_Account')
    PAP.Person : ('Doe', 'John', 'F.', 'Dr.', 'PAP.Person')
    PAP.Email : ('john.doe@example.com', 'PAP.Email')
    PAP.Company_has_Url : (('John Doe, Inc.', 'NY', 'PAP.Company'), ('http://xkcd.com/327/', 'PAP.Url'), 'PAP.Company_has_Url')
    PAP.Company_has_Phone : (('John Doe, Inc.', 'NY', 'PAP.Company'), ('+43', '1', '234567', 'PAP.Phone'), '99', 'PAP.Company_has_Phone')
    PAP.Company_has_Email : (('John Doe, Inc.', 'NY', 'PAP.Company'), ('john.doe@example.com', 'PAP.Email'), 'PAP.Company_has_Email')
    PAP.Company_has_Address : (('John Doe, Inc.', 'NY', 'PAP.Company'), ('Mystery Lane 42', '9876', 'Middletown', 'Land Of The Brave', 'PAP.Address'), 'PAP.Company_has_Address')
    PAP.Company : ('John Doe, Inc.', 'NY', 'PAP.Company')
    PAP.Address_Position : (('Mystery Lane 42', '9876', 'Middletown', 'Land Of The Brave', 'PAP.Address'), 'PAP.Address_Position')
    PAP.Address : ('Mystery Lane 42', '9876', 'Middletown', 'Land Of The Brave', 'PAP.Address')
    Auth.Group : ('foo', 'Auth.Group')
    Auth.Certificate : ('foo@bar.baz', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'foo', 'Auth.Certificate')
    Auth.Account_in_Group : (('foo@bar.baz', 'Auth.Account'), ('foo', 'Auth.Group'), 'Auth.Account_in_Group')
    Auth.Account_Password_Reset : ------
    Auth.Account_Password_Change_Required : (('foo@bar.baz', 'Auth.Account'), 'Auth.Account_Password_Change_Required')
    Auth.Account_EMail_Verification : ------
    Auth.Account_Activation : (('foo@bar.baz', 'Auth.Account'), 'Auth.Account_Activation')
    Auth.Account : ('foo@bar.baz', 'Auth.Account')

"""

_test_example_4 = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> print ("Count before loop:", scope.MOM.Id_Entity.count)
    Count before loop: 16

    >>> for tn in sorted (scope.MOM.Id_Entity.children_np) : ### nummero 1
    ...     ETM = scope [tn]
    ...     exa = ETM.example ()
    ...     print (tn, ":", portable_repr (exa.epk_raw) if exa is not None else "------")
    Auth.Account : ('foo@bar.baz', 'Auth.Account')
    Auth.Account_Activation : (('foo@bar.baz', 'Auth.Account'), 'Auth.Account_Activation')
    Auth.Account_EMail_Verification : ------
    Auth.Account_Password_Change_Required : (('foo@bar.baz', 'Auth.Account'), 'Auth.Account_Password_Change_Required')
    Auth.Account_Password_Reset : ------
    Auth.Account_in_Group : (('foo@bar.baz', 'Auth.Account'), ('foo', 'Auth.Group'), 'Auth.Account_in_Group')
    Auth.Certificate : ('foo@bar.baz', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'foo', 'Auth.Certificate')
    Auth.Group : ('foo', 'Auth.Group')
    PAP.Address : ('Mystery Lane 42', '9876', 'Middletown', 'Land Of The Brave', 'PAP.Address')
    PAP.Address_Position : (('Mystery Lane 42', '9876', 'Middletown', 'Land Of The Brave', 'PAP.Address'), 'PAP.Address_Position')
    PAP.Company : ('John Doe, Inc.', 'NY', 'PAP.Company')
    PAP.Company_has_Address : (('John Doe, Inc.', 'NY', 'PAP.Company'), ('Mystery Lane 42', '9876', 'Middletown', 'Land Of The Brave', 'PAP.Address'), 'PAP.Company_has_Address')
    PAP.Company_has_Email : (('John Doe, Inc.', 'NY', 'PAP.Company'), ('john.doe@example.com', 'PAP.Email'), 'PAP.Company_has_Email')
    PAP.Company_has_Phone : (('John Doe, Inc.', 'NY', 'PAP.Company'), ('+43', '1', '234567', 'PAP.Phone'), '99', 'PAP.Company_has_Phone')
    PAP.Company_has_Url : (('John Doe, Inc.', 'NY', 'PAP.Company'), ('http://xkcd.com/327/', 'PAP.Url'), 'PAP.Company_has_Url')
    PAP.Email : ('john.doe@example.com', 'PAP.Email')
    PAP.Person : ('Doe', 'John', 'F.', 'Dr.', 'PAP.Person')
    PAP.Person_has_Account : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), ('foo@bar.baz', 'Auth.Account'), 'PAP.Person_has_Account')
    PAP.Person_has_Address : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), ('Mystery Lane 42', '9876', 'Middletown', 'Land Of The Brave', 'PAP.Address'), 'PAP.Person_has_Address')
    PAP.Person_has_Email : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), ('john.doe@example.com', 'PAP.Email'), 'PAP.Person_has_Email')
    PAP.Person_has_Phone : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), ('+43', '1', '234567', 'PAP.Phone'), '99', 'PAP.Person_has_Phone')
    PAP.Person_has_Url : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), ('http://xkcd.com/327/', 'PAP.Url'), 'PAP.Person_has_Url')
    PAP.Phone : ('+43', '1', '234567', 'PAP.Phone')
    PAP.Url : ('http://xkcd.com/327/', 'PAP.Url')
    SRM.Boat : (('Laser', 'SRM.Boat_Class'), '2827', 'AUT', 'X', 'SRM.Boat')
    SRM.Boat_Class : ('Laser', 'SRM.Boat_Class')
    SRM.Boat_in_Regatta : ((('Laser', 'SRM.Boat_Class'), '2827', 'AUT', 'X', 'SRM.Boat'), (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta')
    SRM.Club : ('RORC', 'SRM.Club')
    SRM.Crew_Member : (((('Laser', 'SRM.Boat_Class'), '2827', 'AUT', 'X', 'SRM.Boat'), (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), 'AUT', '499999', ('RORC', 'SRM.Club'), 'SRM.Sailor'), 'SRM.Crew_Member')
    SRM.Handicap : ('IRC', 'SRM.Handicap')
    SRM.Page : ('20101010_000042_137', ('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), 'SRM.Page')
    SRM.Race_Result : (((('Laser', 'SRM.Boat_Class'), '2827', 'AUT', 'X', 'SRM.Boat'), (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), '5', 'SRM.Race_Result')
    SRM.Regatta_C : (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C')
    SRM.Regatta_Event : ('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event')
    SRM.Regatta_H : (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('IRC', 'SRM.Handicap'), 'SRM.Regatta_H')
    SRM.Sailor : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), 'AUT', '499999', ('RORC', 'SRM.Club'), 'SRM.Sailor')
    SRM.Team : ((('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'foo', 'SRM.Team')
    SRM.Team_has_Boat_in_Regatta : (((('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'foo', 'SRM.Team'), ((('Laser', 'SRM.Boat_Class'), '2827', 'AUT', 'X', 'SRM.Boat'), (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), 'SRM.Team_has_Boat_in_Regatta')
    SWP.Clip_O : (('20101010_000042_137', 'SWP.Page'), (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SWP.Clip_O')
    SWP.Gallery : ('20101010_000042_137', 'SWP.Gallery')
    SWP.Page : ('20101010_000042_137', 'SWP.Page')
    SWP.Picture : (('20101010_000042_137', 'SWP.Gallery'), '42', 'SWP.Picture')
    SWP.Referral : ('/bar', '20101010_000042_137', 'SWP.Referral')

    >>> scope.destroy ()

    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> for tn in sorted (scope.MOM.Id_Entity.children_np) : ### nummero 2
    ...     ETM = scope [tn]
    ...     exa = ETM.example ()
    ...     print (tn, ":", portable_repr (exa.epk_raw) if exa is not None else "------")
    Auth.Account : ('foo@bar.baz', 'Auth.Account')
    Auth.Account_Activation : (('foo@bar.baz', 'Auth.Account'), 'Auth.Account_Activation')
    Auth.Account_EMail_Verification : ------
    Auth.Account_Password_Change_Required : (('foo@bar.baz', 'Auth.Account'), 'Auth.Account_Password_Change_Required')
    Auth.Account_Password_Reset : ------
    Auth.Account_in_Group : (('foo@bar.baz', 'Auth.Account'), ('foo', 'Auth.Group'), 'Auth.Account_in_Group')
    Auth.Certificate : ('foo@bar.baz', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'foo', 'Auth.Certificate')
    Auth.Group : ('foo', 'Auth.Group')
    PAP.Address : ('Mystery Lane 42', '9876', 'Middletown', 'Land Of The Brave', 'PAP.Address')
    PAP.Address_Position : (('Mystery Lane 42', '9876', 'Middletown', 'Land Of The Brave', 'PAP.Address'), 'PAP.Address_Position')
    PAP.Company : ('John Doe, Inc.', 'NY', 'PAP.Company')
    PAP.Company_has_Address : (('John Doe, Inc.', 'NY', 'PAP.Company'), ('Mystery Lane 42', '9876', 'Middletown', 'Land Of The Brave', 'PAP.Address'), 'PAP.Company_has_Address')
    PAP.Company_has_Email : (('John Doe, Inc.', 'NY', 'PAP.Company'), ('john.doe@example.com', 'PAP.Email'), 'PAP.Company_has_Email')
    PAP.Company_has_Phone : (('John Doe, Inc.', 'NY', 'PAP.Company'), ('+43', '1', '234567', 'PAP.Phone'), '99', 'PAP.Company_has_Phone')
    PAP.Company_has_Url : (('John Doe, Inc.', 'NY', 'PAP.Company'), ('http://xkcd.com/327/', 'PAP.Url'), 'PAP.Company_has_Url')
    PAP.Email : ('john.doe@example.com', 'PAP.Email')
    PAP.Person : ('Doe', 'John', 'F.', 'Dr.', 'PAP.Person')
    PAP.Person_has_Account : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), ('foo@bar.baz', 'Auth.Account'), 'PAP.Person_has_Account')
    PAP.Person_has_Address : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), ('Mystery Lane 42', '9876', 'Middletown', 'Land Of The Brave', 'PAP.Address'), 'PAP.Person_has_Address')
    PAP.Person_has_Email : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), ('john.doe@example.com', 'PAP.Email'), 'PAP.Person_has_Email')
    PAP.Person_has_Phone : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), ('+43', '1', '234567', 'PAP.Phone'), '99', 'PAP.Person_has_Phone')
    PAP.Person_has_Url : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), ('http://xkcd.com/327/', 'PAP.Url'), 'PAP.Person_has_Url')
    PAP.Phone : ('+43', '1', '234567', 'PAP.Phone')
    PAP.Url : ('http://xkcd.com/327/', 'PAP.Url')
    SRM.Boat : (('Laser', 'SRM.Boat_Class'), '2827', 'AUT', 'X', 'SRM.Boat')
    SRM.Boat_Class : ('Laser', 'SRM.Boat_Class')
    SRM.Boat_in_Regatta : ((('Laser', 'SRM.Boat_Class'), '2827', 'AUT', 'X', 'SRM.Boat'), (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta')
    SRM.Club : ('RORC', 'SRM.Club')
    SRM.Crew_Member : (((('Laser', 'SRM.Boat_Class'), '2827', 'AUT', 'X', 'SRM.Boat'), (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), 'AUT', '499999', ('RORC', 'SRM.Club'), 'SRM.Sailor'), 'SRM.Crew_Member')
    SRM.Handicap : ('IRC', 'SRM.Handicap')
    SRM.Page : ('20101010_000042_137', ('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), 'SRM.Page')
    SRM.Race_Result : (((('Laser', 'SRM.Boat_Class'), '2827', 'AUT', 'X', 'SRM.Boat'), (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), '5', 'SRM.Race_Result')
    SRM.Regatta_C : (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C')
    SRM.Regatta_Event : ('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event')
    SRM.Regatta_H : (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('IRC', 'SRM.Handicap'), 'SRM.Regatta_H')
    SRM.Sailor : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), 'AUT', '499999', ('RORC', 'SRM.Club'), 'SRM.Sailor')
    SRM.Team : ((('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'foo', 'SRM.Team')
    SRM.Team_has_Boat_in_Regatta : (((('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'foo', 'SRM.Team'), ((('Laser', 'SRM.Boat_Class'), '2827', 'AUT', 'X', 'SRM.Boat'), (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), 'SRM.Team_has_Boat_in_Regatta')
    SWP.Clip_O : (('20101010_000042_137', 'SWP.Page'), (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SWP.Clip_O')
    SWP.Gallery : ('20101010_000042_137', 'SWP.Gallery')
    SWP.Page : ('20101010_000042_137', 'SWP.Page')
    SWP.Picture : (('20101010_000042_137', 'SWP.Gallery'), '42', 'SWP.Picture')
    SWP.Referral : ('/bar', '20101010_000042_137', 'SWP.Referral')

    >>> scope.destroy ()

    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> for tn in sorted (scope.MOM.Id_Entity.children_np, reverse = True) : ### nummero 3
    ...     ETM = scope [tn]
    ...     exa = ETM.example ()
    ...     print (tn, ":", portable_repr (exa.epk_raw) if exa is not None else "------")
    SWP.Referral : ('/bar', '20101010_000042_137', 'SWP.Referral')
    SWP.Picture : (('20101010_000042_137', 'SWP.Gallery'), '42', 'SWP.Picture')
    SWP.Page : ('20101010_000042_137', 'SWP.Page')
    SWP.Gallery : ('20101010_000042_137', 'SWP.Gallery')
    SWP.Clip_O : (('20101010_000042_137', 'SWP.Page'), (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SWP.Clip_O')
    SRM.Team_has_Boat_in_Regatta : (((('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'foo', 'SRM.Team'), ((('Laser', 'SRM.Boat_Class'), '2827', 'AUT', 'X', 'SRM.Boat'), (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), 'SRM.Team_has_Boat_in_Regatta')
    SRM.Team : ((('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'foo', 'SRM.Team')
    SRM.Sailor : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), 'AUT', '499999', ('RORC', 'SRM.Club'), 'SRM.Sailor')
    SRM.Regatta_H : (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('IRC', 'SRM.Handicap'), 'SRM.Regatta_H')
    SRM.Regatta_Event : ('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event')
    SRM.Regatta_C : (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C')
    SRM.Race_Result : (((('Laser', 'SRM.Boat_Class'), '2827', 'AUT', 'X', 'SRM.Boat'), (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), '5', 'SRM.Race_Result')
    SRM.Page : ('20101010_000042_137', ('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), 'SRM.Page')
    SRM.Handicap : ('IRC', 'SRM.Handicap')
    SRM.Crew_Member : (((('Laser', 'SRM.Boat_Class'), '2827', 'AUT', 'X', 'SRM.Boat'), (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta'), (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), 'AUT', '499999', ('RORC', 'SRM.Club'), 'SRM.Sailor'), 'SRM.Crew_Member')
    SRM.Club : ('RORC', 'SRM.Club')
    SRM.Boat_in_Regatta : ((('Laser', 'SRM.Boat_Class'), '2827', 'AUT', 'X', 'SRM.Boat'), (('Fastnet Race', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'SRM.Regatta_Event'), ('Laser', 'SRM.Boat_Class'), 'SRM.Regatta_C'), 'SRM.Boat_in_Regatta')
    SRM.Boat_Class : ('Laser', 'SRM.Boat_Class')
    SRM.Boat : (('Laser', 'SRM.Boat_Class'), '2827', 'AUT', 'X', 'SRM.Boat')
    PAP.Url : ('http://xkcd.com/327/', 'PAP.Url')
    PAP.Phone : ('+43', '1', '234567', 'PAP.Phone')
    PAP.Person_has_Url : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), ('http://xkcd.com/327/', 'PAP.Url'), 'PAP.Person_has_Url')
    PAP.Person_has_Phone : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), ('+43', '1', '234567', 'PAP.Phone'), '99', 'PAP.Person_has_Phone')
    PAP.Person_has_Email : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), ('john.doe@example.com', 'PAP.Email'), 'PAP.Person_has_Email')
    PAP.Person_has_Address : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), ('Mystery Lane 42', '9876', 'Middletown', 'Land Of The Brave', 'PAP.Address'), 'PAP.Person_has_Address')
    PAP.Person_has_Account : (('Doe', 'John', 'F.', 'Dr.', 'PAP.Person'), ('foo@bar.baz', 'Auth.Account'), 'PAP.Person_has_Account')
    PAP.Person : ('Doe', 'John', 'F.', 'Dr.', 'PAP.Person')
    PAP.Email : ('john.doe@example.com', 'PAP.Email')
    PAP.Company_has_Url : (('John Doe, Inc.', 'NY', 'PAP.Company'), ('http://xkcd.com/327/', 'PAP.Url'), 'PAP.Company_has_Url')
    PAP.Company_has_Phone : (('John Doe, Inc.', 'NY', 'PAP.Company'), ('+43', '1', '234567', 'PAP.Phone'), '99', 'PAP.Company_has_Phone')
    PAP.Company_has_Email : (('John Doe, Inc.', 'NY', 'PAP.Company'), ('john.doe@example.com', 'PAP.Email'), 'PAP.Company_has_Email')
    PAP.Company_has_Address : (('John Doe, Inc.', 'NY', 'PAP.Company'), ('Mystery Lane 42', '9876', 'Middletown', 'Land Of The Brave', 'PAP.Address'), 'PAP.Company_has_Address')
    PAP.Company : ('John Doe, Inc.', 'NY', 'PAP.Company')
    PAP.Address_Position : (('Mystery Lane 42', '9876', 'Middletown', 'Land Of The Brave', 'PAP.Address'), 'PAP.Address_Position')
    PAP.Address : ('Mystery Lane 42', '9876', 'Middletown', 'Land Of The Brave', 'PAP.Address')
    Auth.Group : ('foo', 'Auth.Group')
    Auth.Certificate : ('foo@bar.baz', (('finish', '2038-01-19'), ('start', '1970-01-01')), 'foo', 'Auth.Certificate')
    Auth.Account_in_Group : (('foo@bar.baz', 'Auth.Account'), ('foo', 'Auth.Group'), 'Auth.Account_in_Group')
    Auth.Account_Password_Reset : ------
    Auth.Account_Password_Change_Required : (('foo@bar.baz', 'Auth.Account'), 'Auth.Account_Password_Change_Required')
    Auth.Account_EMail_Verification : ------
    Auth.Account_Activation : (('foo@bar.baz', 'Auth.Account'), 'Auth.Account_Activation')
    Auth.Account : ('foo@bar.baz', 'Auth.Account')

"""

_test_get = r"""
    >>> server = run_server (%(p1)s, %(n1)s)

    >>> r = showf (R.options (""))
    { 'headers' :
        { 'allow' : 'GET, HEAD, OPTIONS'
        , 'cache-control' : 'no-cache'
        , 'content-length' : '0'
        , 'content-type' : 'text/plain; charset=utf-8'
        , 'date' : '<datetime instance>'
        , 'etag' : 'ETag value'
        , 'server' : '<server>'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/'
    }

    >>> r = showf (R.head (""))
    { 'headers' :
        { 'cache-control' : 'no-cache'
        , 'content-length' : '0'
        , 'content-type' : 'text/plain; charset=utf-8'
        , 'date' : '<datetime instance>'
        , 'etag' : 'ETag value'
        , 'server' : '<server>'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/'
    }

    >>> r = show (R.get (""))
    { 'json' :
        { 'entries' :
            [ '/v1'
            , '/Doc'
            , '/RAISE'
            ]
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/'
    }

    >>> r = show (R.get ("?brief"))
    { 'json' :
        { 'entries' :
            [ 'v1'
            , 'Doc'
            , 'RAISE'
            ]
        , 'url_template' : '/{entry}'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/?brief'
    }

    >>> r = show (R.get ("?verbose"))
    { 'json' :
        { 'entries' :
            [ '/v1'
            , '/Doc'
            , '/RAISE'
            ]
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/?verbose'
    }

    >>> r = show (R.get ("/v0"))
    { 'json' : {'description' : 'Not found'}
    , 'status' : 404
    , 'url' : 'http://localhost:9999/v0'
    }

    >>> r = show (R.get ("/v1?brief"))
    { 'json' :
        { 'entries' :
            [ 'Auth-Account'
            , 'Auth-Account_in_Group'
            , 'Auth-Certificate'
            , 'Auth-Group'
            , 'Auth-Id_Entity'
            , 'Auth-Link'
            , 'Auth-Link1'
            , 'Auth-Link2'
            , 'Auth-Object'
            , 'Auth-_Account_'
            , 'Auth-_Link_n_'
            , 'MOM-Id_Entity'
            , 'MOM-Link'
            , 'MOM-Link1'
            , 'MOM-Link2'
            , 'MOM-Object'
            , 'MOM-_Link_n_'
            , 'PAP-Address'
            , 'PAP-Address_Position'
            , 'PAP-Company'
            , 'PAP-Company_has_Address'
            , 'PAP-Company_has_Email'
            , 'PAP-Company_has_Phone'
            , 'PAP-Company_has_Url'
            , 'PAP-Email'
            , 'PAP-Group'
            , 'PAP-Id_Entity'
            , 'PAP-Legal_Entity'
            , 'PAP-Link'
            , 'PAP-Link1'
            , 'PAP-Link2'
            , 'PAP-Object'
            , 'PAP-Person'
            , 'PAP-Person_has_Account'
            , 'PAP-Person_has_Address'
            , 'PAP-Person_has_Email'
            , 'PAP-Person_has_Phone'
            , 'PAP-Person_has_Url'
            , 'PAP-Phone'
            , 'PAP-Property'
            , 'PAP-Subject'
            , 'PAP-Subject_has_Address'
            , 'PAP-Subject_has_Email'
            , 'PAP-Subject_has_Phone'
            , 'PAP-Subject_has_Property'
            , 'PAP-Subject_has_Url'
            , 'PAP-Url'
            , 'PAP-_Link_n_'
            , 'SRM-Boat'
            , 'SRM-Boat_Class'
            , 'SRM-Boat_in_Regatta'
            , 'SRM-Club'
            , 'SRM-Crew_Member'
            , 'SRM-Handicap'
            , 'SRM-Id_Entity'
            , 'SRM-Link'
            , 'SRM-Link1'
            , 'SRM-Link2'
            , 'SRM-Object'
            , 'SRM-Page'
            , 'SRM-Race_Result'
            , 'SRM-Regatta'
            , 'SRM-Regatta_C'
            , 'SRM-Regatta_Event'
            , 'SRM-Regatta_H'
            , 'SRM-Sailor'
            , 'SRM-Team'
            , 'SRM-Team_has_Boat_in_Regatta'
            , 'SRM-_Boat_Class_'
            , 'SRM-_Link_n_'
            , 'SWP-Clip_O'
            , 'SWP-Clip_X'
            , 'SWP-Gallery'
            , 'SWP-Id_Entity'
            , 'SWP-Link'
            , 'SWP-Link1'
            , 'SWP-Object'
            , 'SWP-Object_PN'
            , 'SWP-Page'
            , 'SWP-Page_Y'
            , 'SWP-Picture'
            , 'SWP-Referral'
            ]
        , 'url_template' : '/v1/{entry}'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1?brief'
    }

    >>> r = show (R.get ("/v1"))
    { 'json' :
        { 'entries' :
            [ '/v1/Auth-Account'
            , '/v1/Auth-Account_in_Group'
            , '/v1/Auth-Certificate'
            , '/v1/Auth-Group'
            , '/v1/Auth-Id_Entity'
            , '/v1/Auth-Link'
            , '/v1/Auth-Link1'
            , '/v1/Auth-Link2'
            , '/v1/Auth-Object'
            , '/v1/Auth-_Account_'
            , '/v1/Auth-_Link_n_'
            , '/v1/MOM-Id_Entity'
            , '/v1/MOM-Link'
            , '/v1/MOM-Link1'
            , '/v1/MOM-Link2'
            , '/v1/MOM-Object'
            , '/v1/MOM-_Link_n_'
            , '/v1/PAP-Address'
            , '/v1/PAP-Address_Position'
            , '/v1/PAP-Company'
            , '/v1/PAP-Company_has_Address'
            , '/v1/PAP-Company_has_Email'
            , '/v1/PAP-Company_has_Phone'
            , '/v1/PAP-Company_has_Url'
            , '/v1/PAP-Email'
            , '/v1/PAP-Group'
            , '/v1/PAP-Id_Entity'
            , '/v1/PAP-Legal_Entity'
            , '/v1/PAP-Link'
            , '/v1/PAP-Link1'
            , '/v1/PAP-Link2'
            , '/v1/PAP-Object'
            , '/v1/PAP-Person'
            , '/v1/PAP-Person_has_Account'
            , '/v1/PAP-Person_has_Address'
            , '/v1/PAP-Person_has_Email'
            , '/v1/PAP-Person_has_Phone'
            , '/v1/PAP-Person_has_Url'
            , '/v1/PAP-Phone'
            , '/v1/PAP-Property'
            , '/v1/PAP-Subject'
            , '/v1/PAP-Subject_has_Address'
            , '/v1/PAP-Subject_has_Email'
            , '/v1/PAP-Subject_has_Phone'
            , '/v1/PAP-Subject_has_Property'
            , '/v1/PAP-Subject_has_Url'
            , '/v1/PAP-Url'
            , '/v1/PAP-_Link_n_'
            , '/v1/SRM-Boat'
            , '/v1/SRM-Boat_Class'
            , '/v1/SRM-Boat_in_Regatta'
            , '/v1/SRM-Club'
            , '/v1/SRM-Crew_Member'
            , '/v1/SRM-Handicap'
            , '/v1/SRM-Id_Entity'
            , '/v1/SRM-Link'
            , '/v1/SRM-Link1'
            , '/v1/SRM-Link2'
            , '/v1/SRM-Object'
            , '/v1/SRM-Page'
            , '/v1/SRM-Race_Result'
            , '/v1/SRM-Regatta'
            , '/v1/SRM-Regatta_C'
            , '/v1/SRM-Regatta_Event'
            , '/v1/SRM-Regatta_H'
            , '/v1/SRM-Sailor'
            , '/v1/SRM-Team'
            , '/v1/SRM-Team_has_Boat_in_Regatta'
            , '/v1/SRM-_Boat_Class_'
            , '/v1/SRM-_Link_n_'
            , '/v1/SWP-Clip_O'
            , '/v1/SWP-Clip_X'
            , '/v1/SWP-Gallery'
            , '/v1/SWP-Id_Entity'
            , '/v1/SWP-Link'
            , '/v1/SWP-Link1'
            , '/v1/SWP-Object'
            , '/v1/SWP-Object_PN'
            , '/v1/SWP-Page'
            , '/v1/SWP-Page_Y'
            , '/v1/SWP-Picture'
            , '/v1/SWP-Referral'
            ]
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1'
    }

    >>> rp = show (R.get ("/v1/PAP-Person"))
    { 'json' :
        { 'entries' :
            [ '/v1/PAP-Person/1'
            , '/v1/PAP-Person/2'
            , '/v1/PAP-Person/3'
            ]
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/PAP-Person'
    }

    >>> _ = show (R.get ("/v1/PAP-Person?verbose&raw"))
    { 'json' :
        { 'attribute_names' :
            [ 'last_name'
            , 'first_name'
            , 'middle_name'
            , 'title'
            , 'lifetime.start'
            , 'lifetime.finish'
            , 'sex'
            ]
        , 'entries' :
            [ { 'attributes_raw' :
                  { 'first_name' : 'Christian'
                  , 'last_name' : 'Tanzer'
                  , 'middle_name' : ''
                  , 'title' : ''
                  }
              , 'cid' : 1
              , 'pid' : 1
              , 'type_name' : 'PAP.Person'
              , 'url' : '/v1/PAP-Person/1'
              }
            , { 'attributes_raw' :
                  { 'first_name' : 'Laurens'
                  , 'last_name' : 'Tanzer'
                  , 'middle_name' : 'William'
                  , 'title' : ''
                  }
              , 'cid' : 2
              , 'pid' : 2
              , 'type_name' : 'PAP.Person'
              , 'url' : '/v1/PAP-Person/2'
              }
            , { 'attributes_raw' :
                  { 'first_name' : 'Clarissa'
                  , 'last_name' : 'Tanzer'
                  , 'middle_name' : 'Anna'
                  , 'title' : ''
                  }
              , 'cid' : 3
              , 'pid' : 3
              , 'type_name' : 'PAP.Person'
              , 'url' : '/v1/PAP-Person/3'
              }
            ]
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/PAP-Person?verbose&raw'
    }

    >>> _ = show (R.get ("/v1/PAP-Person.csv?verbose&raw"))
    { 'content' :
        [ 'last_name,first_name,middle_name,title,lifetime.start,lifetime.finish,sex'
        , 'Tanzer,Christian,,,,,'
        , 'Tanzer,Laurens,William,,,,'
        , 'Tanzer,Clarissa,Anna,,,,'
        ]
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/PAP-Person.csv?verbose&raw'
    }

    >>> _ = show (R.get ("/v1/PAP-Person.csv"))
    { 'status' : 200
    , 'url' : 'http://localhost:9999/v1/PAP-Person.csv'
    }

    >>> rp_json = req_json (rp)
    >>> for e in rp_json ["entries"] :
    ...     print (e)
    ...     _ = show (requests.get ("http://localhost:9999" + e))
    /v1/PAP-Person/1
    { 'json' :
        { 'attributes' :
            { 'first_name' : 'christian'
            , 'last_name' : 'tanzer'
            , 'middle_name' : ''
            , 'title' : ''
            }
        , 'cid' : 1
        , 'pid' : 1
        , 'rels' :
            [ '/v1/PAP-Person/1/account_links'
            , '/v1/PAP-Person/1/address_links'
            , '/v1/PAP-Person/1/email_links'
            , '/v1/PAP-Person/1/phone_links'
            , '/v1/PAP-Person/1/sailors'
            , '/v1/PAP-Person/1/url_links'
            ]
        , 'type_name' : 'PAP.Person'
        , 'url' : '/v1/PAP-Person/1'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/PAP-Person/1'
    }
    /v1/PAP-Person/2
    { 'json' :
        { 'attributes' :
            { 'first_name' : 'laurens'
            , 'last_name' : 'tanzer'
            , 'middle_name' : 'william'
            , 'title' : ''
            }
        , 'cid' : 2
        , 'pid' : 2
        , 'rels' :
            [ '/v1/PAP-Person/2/account_links'
            , '/v1/PAP-Person/2/address_links'
            , '/v1/PAP-Person/2/email_links'
            , '/v1/PAP-Person/2/phone_links'
            , '/v1/PAP-Person/2/sailors'
            , '/v1/PAP-Person/2/url_links'
            ]
        , 'type_name' : 'PAP.Person'
        , 'url' : '/v1/PAP-Person/2'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/PAP-Person/2'
    }
    /v1/PAP-Person/3
    { 'json' :
        { 'attributes' :
            { 'first_name' : 'clarissa'
            , 'last_name' : 'tanzer'
            , 'middle_name' : 'anna'
            , 'title' : ''
            }
        , 'cid' : 3
        , 'pid' : 3
        , 'rels' :
            [ '/v1/PAP-Person/3/account_links'
            , '/v1/PAP-Person/3/address_links'
            , '/v1/PAP-Person/3/email_links'
            , '/v1/PAP-Person/3/phone_links'
            , '/v1/PAP-Person/3/sailors'
            , '/v1/PAP-Person/3/url_links'
            ]
        , 'type_name' : 'PAP.Person'
        , 'url' : '/v1/PAP-Person/3'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/PAP-Person/3'
    }

    >>> r = show (R.head ("/v1/PAP-Person/1"))
    { 'status' : 200
    , 'url' : 'http://localhost:9999/v1/PAP-Person/1'
    }

    >>> r = showf (R.get ("/v1/PAP-Person/1?fields=first_name,last_name"))
    { 'headers' :
        { 'cache-control' : 'no-cache'
        , 'content-length' : '<length>'
        , 'content-type' : 'application/json'
        , 'date' : '<datetime instance>'
        , 'etag' : 'ETag value'
        , 'link' : '/v1/PAP-Person/1/account_links; rel="Person_has_Account links", /v1/PAP-Person/1/address_links; rel="Person_has_Address links", /v1/PAP-Person/1/email_links; rel="Person_has_Email links", /v1/PAP-Person/1/phone_links; rel="Person_has_Phone links", /v1/PAP-Person/1/url_links; rel="Person_has_Url links", /v1/PAP-Person/1/sailors; rel="Sailor links", /Doc/PAP-Person; rel=doc'
        , 'server' : '<server>'
        , 'x-last-cid' : '1'
        }
    , 'json' :
        { 'attributes' :
            { 'first_name' : 'christian'
            , 'last_name' : 'tanzer'
            }
        , 'cid' : 1
        , 'pid' : 1
        , 'rels' :
            [ '/v1/PAP-Person/1/account_links'
            , '/v1/PAP-Person/1/address_links'
            , '/v1/PAP-Person/1/email_links'
            , '/v1/PAP-Person/1/phone_links'
            , '/v1/PAP-Person/1/sailors'
            , '/v1/PAP-Person/1/url_links'
            ]
        , 'type_name' : 'PAP.Person'
        , 'url' : '/v1/PAP-Person/1'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/PAP-Person/1?fields=first_name,last_name'
    }

    >>> r = showf (R.get ("/v1/PAP-Person/1?RELS"))
    { 'headers' :
        { 'cache-control' : 'no-cache'
        , 'content-length' : '<length>'
        , 'content-type' : 'application/json'
        , 'date' : '<datetime instance>'
        , 'etag' : 'ETag value'
        , 'link' : '/v1/PAP-Person/1/account_links; rel="Person_has_Account links", /v1/PAP-Person/1/address_links; rel="Person_has_Address links", /v1/PAP-Person/1/email_links; rel="Person_has_Email links", /v1/PAP-Person/1/phone_links; rel="Person_has_Phone links", /v1/PAP-Person/1/url_links; rel="Person_has_Url links", /v1/PAP-Person/1/sailors; rel="Sailor links", /Doc/PAP-Person; rel=doc'
        , 'server' : '<server>'
        , 'x-last-cid' : '1'
        }
    , 'json' :
        { 'attributes' :
            { 'first_name' : 'christian'
            , 'last_name' : 'tanzer'
            , 'middle_name' : ''
            , 'title' : ''
            }
        , 'cid' : 1
        , 'pid' : 1
        , 'rels' :
            { '/v1/PAP-Person/1/account_links' :
                []
            , '/v1/PAP-Person/1/address_links' :
                []
            , '/v1/PAP-Person/1/email_links' :
                []
            , '/v1/PAP-Person/1/phone_links' :
                []
            , '/v1/PAP-Person/1/sailors' : ['/v1/SRM-Sailor/4']
            , '/v1/PAP-Person/1/url_links' :
                []
            }
        , 'type_name' : 'PAP.Person'
        , 'url' : '/v1/PAP-Person/1'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/PAP-Person/1?RELS'
    }

    >>> last_etag = r.headers ["etag"]
    >>> r = showf (R.get ("/v1/PAP-Person/1", headers = { "If-None-Match" : last_etag }))
    { 'headers' :
        { 'cache-control' : 'no-cache'
        , 'date' : '<datetime instance>'
        , 'etag' : 'ETag value'
        , 'link' : '/v1/PAP-Person/1/account_links; rel="Person_has_Account links", /v1/PAP-Person/1/address_links; rel="Person_has_Address links", /v1/PAP-Person/1/email_links; rel="Person_has_Email links", /v1/PAP-Person/1/phone_links; rel="Person_has_Phone links", /v1/PAP-Person/1/url_links; rel="Person_has_Url links", /v1/PAP-Person/1/sailors; rel="Sailor links", /Doc/PAP-Person; rel=doc'
        , 'server' : '<server>'
        , 'x-last-cid' : '1'
        }
    , 'status' : 304
    , 'url' : 'http://localhost:9999/v1/PAP-Person/1'
    }

    >>> r = show (R.get ("/v1/SRM-Regatta?brief"))
    { 'json' :
        { 'entries' :
            [ 11
            , 12
            , 14
            ]
        , 'url_template' : '/v1/SRM-Regatta/{entry}'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/SRM-Regatta?brief'
    }

    >>> _ = show (R.get ("/v1/SRM-Regatta?verbose&closure&ckd"))
    { 'json' :
        { 'attribute_names' :
            [ 'left'
            , 'boat_class'
            , 'discards'
            , 'is_cancelled'
            , 'kind'
            , 'races'
            , 'result.date'
            , 'result.software'
            , 'result.status'
            , 'starters_rl'
            ]
        , 'entries' :
            [ { 'attributes' :
                  { 'boat_class' :
                      { 'attributes' :
                          { 'max_crew' : 1
                          , 'name' : 'optimist'
                          }
                      , 'cid' : 7
                      , 'pid' : 7
                      , 'type_name' : 'SRM.Boat_Class'
                      , 'url' : '/v1/SRM-Boat_Class/7'
                      }
                  , 'is_cancelled' : False
                  , 'left' :
                      { 'attributes' :
                          { 'date' :
                              { 'finish' : '2008-05-01'
                              , 'start' : '2008-05-01'
                              }
                          , 'name' : 'himmelfahrt'
                          }
                      , 'cid' : 10
                      , 'pid' : 10
                      , 'type_name' : 'SRM.Regatta_Event'
                      , 'url' : '/v1/SRM-Regatta_Event/10'
                      }
                  }
              , 'cid' : 11
              , 'pid' : 11
              , 'type_name' : 'SRM.Regatta_C'
              , 'url' : '/v1/SRM-Regatta/11'
              }
            , { 'attributes' :
                  { 'boat_class' :
                      { 'attributes' : {'name' : 'yardstick'}
                      , 'cid' : 9
                      , 'pid' : 9
                      , 'type_name' : 'SRM.Handicap'
                      , 'url' : '/v1/SRM-Handicap/9'
                      }
                  , 'is_cancelled' : False
                  , 'left' :
                      { 'pid' : 10
                      , 'url' : '/v1/SRM-Regatta_Event/10'
                      }
                  }
              , 'cid' : 12
              , 'pid' : 12
              , 'type_name' : 'SRM.Regatta_H'
              , 'url' : '/v1/SRM-Regatta/12'
              }
            , { 'attributes' :
                  { 'boat_class' :
                      { 'pid' : 7
                      , 'url' : '/v1/SRM-Boat_Class/7'
                      }
                  , 'is_cancelled' : False
                  , 'left' :
                      { 'attributes' :
                          { 'date' :
                              { 'finish' : '2008-06-21'
                              , 'start' : '2008-06-20'
                              }
                          , 'name' : 'guggenberger'
                          }
                      , 'cid' : 13
                      , 'pid' : 13
                      , 'type_name' : 'SRM.Regatta_Event'
                      , 'url' : '/v1/SRM-Regatta_Event/13'
                      }
                  }
              , 'cid' : 14
              , 'pid' : 14
              , 'type_name' : 'SRM.Regatta_C'
              , 'url' : '/v1/SRM-Regatta/14'
              }
            ]
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/SRM-Regatta?verbose&closure&ckd'
    }

    >>> _ = show (R.get ("/v1/SRM-Regatta?verbose&raw&closure"))
    { 'json' :
        { 'attribute_names' :
            [ 'left'
            , 'boat_class'
            , 'discards'
            , 'is_cancelled'
            , 'kind'
            , 'races'
            , 'result.date'
            , 'result.software'
            , 'result.status'
            , 'starters_rl'
            ]
        , 'entries' :
            [ { 'attributes_raw' :
                  { 'boat_class' :
                      { 'attributes_raw' :
                          { 'max_crew' : '1'
                          , 'name' : 'Optimist'
                          }
                      , 'cid' : 7
                      , 'pid' : 7
                      , 'type_name' : 'SRM.Boat_Class'
                      , 'url' : '/v1/SRM-Boat_Class/7'
                      }
                  , 'is_cancelled' : 'no'
                  , 'left' :
                      { 'attributes_raw' :
                          { 'date' :
                              { 'finish' : '2008-05-01'
                              , 'start' : '2008-05-01'
                              }
                          , 'name' : 'Himmelfahrt'
                          }
                      , 'cid' : 10
                      , 'pid' : 10
                      , 'type_name' : 'SRM.Regatta_Event'
                      , 'url' : '/v1/SRM-Regatta_Event/10'
                      }
                  }
              , 'cid' : 11
              , 'pid' : 11
              , 'type_name' : 'SRM.Regatta_C'
              , 'url' : '/v1/SRM-Regatta/11'
              }
            , { 'attributes_raw' :
                  { 'boat_class' :
                      { 'attributes_raw' : {'name' : 'Yardstick'}
                      , 'cid' : 9
                      , 'pid' : 9
                      , 'type_name' : 'SRM.Handicap'
                      , 'url' : '/v1/SRM-Handicap/9'
                      }
                  , 'is_cancelled' : 'no'
                  , 'left' :
                      { 'pid' : 10
                      , 'url' : '/v1/SRM-Regatta_Event/10'
                      }
                  }
              , 'cid' : 12
              , 'pid' : 12
              , 'type_name' : 'SRM.Regatta_H'
              , 'url' : '/v1/SRM-Regatta/12'
              }
            , { 'attributes_raw' :
                  { 'boat_class' :
                      { 'pid' : 7
                      , 'url' : '/v1/SRM-Boat_Class/7'
                      }
                  , 'is_cancelled' : 'no'
                  , 'left' :
                      { 'attributes_raw' :
                          { 'date' :
                              { 'finish' : '2008-06-21'
                              , 'start' : '2008-06-20'
                              }
                          , 'name' : 'Guggenberger'
                          }
                      , 'cid' : 13
                      , 'pid' : 13
                      , 'type_name' : 'SRM.Regatta_Event'
                      , 'url' : '/v1/SRM-Regatta_Event/13'
                      }
                  }
              , 'cid' : 14
              , 'pid' : 14
              , 'type_name' : 'SRM.Regatta_C'
              , 'url' : '/v1/SRM-Regatta/14'
              }
            ]
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/SRM-Regatta?verbose&raw&closure'
    }

    >>> _ = show (R.get ("/v1/SRM-Regatta?verbose&raw"))
    { 'json' :
        { 'attribute_names' :
            [ 'left'
            , 'boat_class'
            , 'discards'
            , 'is_cancelled'
            , 'kind'
            , 'races'
            , 'result.date'
            , 'result.software'
            , 'result.status'
            , 'starters_rl'
            ]
        , 'entries' :
            [ { 'attributes_raw' :
                  { 'boat_class' :
                      { 'pid' : 7
                      , 'url' : '/v1/SRM-Boat_Class/7'
                      }
                  , 'is_cancelled' : 'no'
                  , 'left' :
                      { 'pid' : 10
                      , 'url' : '/v1/SRM-Regatta_Event/10'
                      }
                  }
              , 'cid' : 11
              , 'pid' : 11
              , 'type_name' : 'SRM.Regatta_C'
              , 'url' : '/v1/SRM-Regatta/11'
              }
            , { 'attributes_raw' :
                  { 'boat_class' :
                      { 'pid' : 9
                      , 'url' : '/v1/SRM-Handicap/9'
                      }
                  , 'is_cancelled' : 'no'
                  , 'left' :
                      { 'pid' : 10
                      , 'url' : '/v1/SRM-Regatta_Event/10'
                      }
                  }
              , 'cid' : 12
              , 'pid' : 12
              , 'type_name' : 'SRM.Regatta_H'
              , 'url' : '/v1/SRM-Regatta/12'
              }
            , { 'attributes_raw' :
                  { 'boat_class' :
                      { 'pid' : 7
                      , 'url' : '/v1/SRM-Boat_Class/7'
                      }
                  , 'is_cancelled' : 'no'
                  , 'left' :
                      { 'pid' : 13
                      , 'url' : '/v1/SRM-Regatta_Event/13'
                      }
                  }
              , 'cid' : 14
              , 'pid' : 14
              , 'type_name' : 'SRM.Regatta_C'
              , 'url' : '/v1/SRM-Regatta/14'
              }
            ]
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/SRM-Regatta?verbose&raw'
    }

    >>> _ = show (R.get ("/v1/SRM-Regatta.csv?verbose&raw&brief"))
    { 'content' :
        [ 'left,boat_class,discards,is_cancelled,kind,races,result.date,result.software,result.status,starters_rl'
        , '10,7,,no,,,,,,'
        , '10,9,,no,,,,,,'
        , '13,7,,no,,,,,,'
        ]
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/SRM-Regatta.csv?verbose&raw&brief'
    }

    >>> _ = show (R.get ("/v1/SRM-Regatta.csv?verbose&raw"))
    { 'content' :
        [ 'left.pid,left.url,boat_class.pid,boat_class.url,discards,is_cancelled,kind,races,result.date,result.software,result.status,starters_rl'
        , '10,/v1/SRM-Regatta_Event/10,7,/v1/SRM-Boat_Class/7,,no,,,,,,'
        , '10,/v1/SRM-Regatta_Event/10,9,/v1/SRM-Handicap/9,,no,,,,,,'
        , '13,/v1/SRM-Regatta_Event/13,7,/v1/SRM-Boat_Class/7,,no,,,,,,'
        ]
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/SRM-Regatta.csv?verbose&raw'
    }

    >>> _ = show (R.get ("/v1/SRM-Regatta.csv?verbose&raw&brief&fields=left,boat_class,is_cancelled"))
    { 'content' :
        [ 'left,boat_class,is_cancelled'
        , '10,7,no'
        , '10,9,no'
        , '13,7,no'
        ]
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/SRM-Regatta.csv?verbose&raw&brief&fields=left,boat_class,is_cancelled'
    }

    >>> _ = show (R.get ("/v1/SRM-Regatta?verbose&raw&brief&fields=left,boat_class,is_cancelled"))
    { 'json' :
        { 'attribute_names' :
            [ 'left'
            , 'boat_class'
            , 'is_cancelled'
            ]
        , 'entries' :
            [ { 'attributes_raw' :
                  { 'boat_class' : 7
                  , 'is_cancelled' : 'no'
                  , 'left' : 10
                  }
              , 'cid' : 11
              , 'pid' : 11
              , 'type_name' : 'SRM.Regatta_C'
              , 'url' : '/v1/SRM-Regatta/11'
              }
            , { 'attributes_raw' :
                  { 'boat_class' : 9
                  , 'is_cancelled' : 'no'
                  , 'left' : 10
                  }
              , 'cid' : 12
              , 'pid' : 12
              , 'type_name' : 'SRM.Regatta_H'
              , 'url' : '/v1/SRM-Regatta/12'
              }
            , { 'attributes_raw' :
                  { 'boat_class' : 7
                  , 'is_cancelled' : 'no'
                  , 'left' : 13
                  }
              , 'cid' : 14
              , 'pid' : 14
              , 'type_name' : 'SRM.Regatta_C'
              , 'url' : '/v1/SRM-Regatta/14'
              }
            ]
        , 'url_template' : '/v1/SRM-Regatta/{entry}'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/SRM-Regatta?verbose&raw&brief&fields=left,boat_class,is_cancelled'
    }

    >>> _ = show (R.get ("/v1/SRM-Regatta_C?verbose&raw&brief&fields=left,boat_class,is_cancelled"))
    { 'json' :
        { 'attribute_names' :
            [ 'left'
            , 'boat_class'
            , 'is_cancelled'
            ]
        , 'entries' :
            [ { 'attributes_raw' :
                  { 'boat_class' : 7
                  , 'is_cancelled' : 'no'
                  , 'left' : 10
                  }
              , 'cid' : 11
              , 'pid' : 11
              , 'type_name' : 'SRM.Regatta_C'
              , 'url' : '/v1/SRM-Regatta_C/11'
              }
            , { 'attributes_raw' :
                  { 'boat_class' : 7
                  , 'is_cancelled' : 'no'
                  , 'left' : 13
                  }
              , 'cid' : 14
              , 'pid' : 14
              , 'type_name' : 'SRM.Regatta_C'
              , 'url' : '/v1/SRM-Regatta_C/14'
              }
            ]
        , 'url_template' : '/v1/SRM-Regatta_C/{entry}'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/SRM-Regatta_C?verbose&raw&brief&fields=left,boat_class,is_cancelled'
    }

    >>> _ = show (R.get ("/v1/SRM-Regatta?verbose&raw&closure"))
    { 'json' :
        { 'attribute_names' :
            [ 'left'
            , 'boat_class'
            , 'discards'
            , 'is_cancelled'
            , 'kind'
            , 'races'
            , 'result.date'
            , 'result.software'
            , 'result.status'
            , 'starters_rl'
            ]
        , 'entries' :
            [ { 'attributes_raw' :
                  { 'boat_class' :
                      { 'attributes_raw' :
                          { 'max_crew' : '1'
                          , 'name' : 'Optimist'
                          }
                      , 'cid' : 7
                      , 'pid' : 7
                      , 'type_name' : 'SRM.Boat_Class'
                      , 'url' : '/v1/SRM-Boat_Class/7'
                      }
                  , 'is_cancelled' : 'no'
                  , 'left' :
                      { 'attributes_raw' :
                          { 'date' :
                              { 'finish' : '2008-05-01'
                              , 'start' : '2008-05-01'
                              }
                          , 'name' : 'Himmelfahrt'
                          }
                      , 'cid' : 10
                      , 'pid' : 10
                      , 'type_name' : 'SRM.Regatta_Event'
                      , 'url' : '/v1/SRM-Regatta_Event/10'
                      }
                  }
              , 'cid' : 11
              , 'pid' : 11
              , 'type_name' : 'SRM.Regatta_C'
              , 'url' : '/v1/SRM-Regatta/11'
              }
            , { 'attributes_raw' :
                  { 'boat_class' :
                      { 'attributes_raw' : {'name' : 'Yardstick'}
                      , 'cid' : 9
                      , 'pid' : 9
                      , 'type_name' : 'SRM.Handicap'
                      , 'url' : '/v1/SRM-Handicap/9'
                      }
                  , 'is_cancelled' : 'no'
                  , 'left' :
                      { 'pid' : 10
                      , 'url' : '/v1/SRM-Regatta_Event/10'
                      }
                  }
              , 'cid' : 12
              , 'pid' : 12
              , 'type_name' : 'SRM.Regatta_H'
              , 'url' : '/v1/SRM-Regatta/12'
              }
            , { 'attributes_raw' :
                  { 'boat_class' :
                      { 'pid' : 7
                      , 'url' : '/v1/SRM-Boat_Class/7'
                      }
                  , 'is_cancelled' : 'no'
                  , 'left' :
                      { 'attributes_raw' :
                          { 'date' :
                              { 'finish' : '2008-06-21'
                              , 'start' : '2008-06-20'
                              }
                          , 'name' : 'Guggenberger'
                          }
                      , 'cid' : 13
                      , 'pid' : 13
                      , 'type_name' : 'SRM.Regatta_Event'
                      , 'url' : '/v1/SRM-Regatta_Event/13'
                      }
                  }
              , 'cid' : 14
              , 'pid' : 14
              , 'type_name' : 'SRM.Regatta_C'
              , 'url' : '/v1/SRM-Regatta/14'
              }
            ]
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/SRM-Regatta?verbose&raw&closure'
    }

    >>> _ = show (R.get ("/v1/SRM-Regatta?verbose&raw&closure&AQ=boat_class,EQ,9"))
    { 'json' :
        { 'attribute_names' :
            [ 'left'
            , 'boat_class'
            , 'discards'
            , 'is_cancelled'
            , 'kind'
            , 'races'
            , 'result.date'
            , 'result.software'
            , 'result.status'
            , 'starters_rl'
            ]
        , 'entries' :
            [ { 'attributes_raw' :
                  { 'boat_class' :
                      { 'attributes_raw' : {'name' : 'Yardstick'}
                      , 'cid' : 9
                      , 'pid' : 9
                      , 'type_name' : 'SRM.Handicap'
                      , 'url' : '/v1/SRM-Handicap/9'
                      }
                  , 'is_cancelled' : 'no'
                  , 'left' :
                      { 'attributes_raw' :
                          { 'date' :
                              { 'finish' : '2008-05-01'
                              , 'start' : '2008-05-01'
                              }
                          , 'name' : 'Himmelfahrt'
                          }
                      , 'cid' : 10
                      , 'pid' : 10
                      , 'type_name' : 'SRM.Regatta_Event'
                      , 'url' : '/v1/SRM-Regatta_Event/10'
                      }
                  }
              , 'cid' : 12
              , 'pid' : 12
              , 'type_name' : 'SRM.Regatta_H'
              , 'url' : '/v1/SRM-Regatta/12'
              }
            ]
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/SRM-Regatta?verbose&raw&closure&AQ=boat_class,EQ,9'
    }

    >>> _ = show (R.get ("/v1/SRM-Regatta?verbose&raw&closure&AQ=boat_class,EQ,7"))
    { 'json' :
        { 'attribute_names' :
            [ 'left'
            , 'boat_class'
            , 'discards'
            , 'is_cancelled'
            , 'kind'
            , 'races'
            , 'result.date'
            , 'result.software'
            , 'result.status'
            , 'starters_rl'
            ]
        , 'entries' :
            [ { 'attributes_raw' :
                  { 'boat_class' :
                      { 'attributes_raw' :
                          { 'max_crew' : '1'
                          , 'name' : 'Optimist'
                          }
                      , 'cid' : 7
                      , 'pid' : 7
                      , 'type_name' : 'SRM.Boat_Class'
                      , 'url' : '/v1/SRM-Boat_Class/7'
                      }
                  , 'is_cancelled' : 'no'
                  , 'left' :
                      { 'attributes_raw' :
                          { 'date' :
                              { 'finish' : '2008-05-01'
                              , 'start' : '2008-05-01'
                              }
                          , 'name' : 'Himmelfahrt'
                          }
                      , 'cid' : 10
                      , 'pid' : 10
                      , 'type_name' : 'SRM.Regatta_Event'
                      , 'url' : '/v1/SRM-Regatta_Event/10'
                      }
                  }
              , 'cid' : 11
              , 'pid' : 11
              , 'type_name' : 'SRM.Regatta_C'
              , 'url' : '/v1/SRM-Regatta/11'
              }
            , { 'attributes_raw' :
                  { 'boat_class' :
                      { 'pid' : 7
                      , 'url' : '/v1/SRM-Boat_Class/7'
                      }
                  , 'is_cancelled' : 'no'
                  , 'left' :
                      { 'attributes_raw' :
                          { 'date' :
                              { 'finish' : '2008-06-21'
                              , 'start' : '2008-06-20'
                              }
                          , 'name' : 'Guggenberger'
                          }
                      , 'cid' : 13
                      , 'pid' : 13
                      , 'type_name' : 'SRM.Regatta_Event'
                      , 'url' : '/v1/SRM-Regatta_Event/13'
                      }
                  }
              , 'cid' : 14
              , 'pid' : 14
              , 'type_name' : 'SRM.Regatta_C'
              , 'url' : '/v1/SRM-Regatta/14'
              }
            ]
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/SRM-Regatta?verbose&raw&closure&AQ=boat_class,EQ,7'
    }

    >>> _ = show (R.get ("/v1/SRM-Regatta?verbose&raw&closure&AQ=boat_class,EQ,7&AQ=left,EQ,13"))
    { 'json' :
        { 'attribute_names' :
            [ 'left'
            , 'boat_class'
            , 'discards'
            , 'is_cancelled'
            , 'kind'
            , 'races'
            , 'result.date'
            , 'result.software'
            , 'result.status'
            , 'starters_rl'
            ]
        , 'entries' :
            [ { 'attributes_raw' :
                  { 'boat_class' :
                      { 'attributes_raw' :
                          { 'max_crew' : '1'
                          , 'name' : 'Optimist'
                          }
                      , 'cid' : 7
                      , 'pid' : 7
                      , 'type_name' : 'SRM.Boat_Class'
                      , 'url' : '/v1/SRM-Boat_Class/7'
                      }
                  , 'is_cancelled' : 'no'
                  , 'left' :
                      { 'attributes_raw' :
                          { 'date' :
                              { 'finish' : '2008-06-21'
                              , 'start' : '2008-06-20'
                              }
                          , 'name' : 'Guggenberger'
                          }
                      , 'cid' : 13
                      , 'pid' : 13
                      , 'type_name' : 'SRM.Regatta_Event'
                      , 'url' : '/v1/SRM-Regatta_Event/13'
                      }
                  }
              , 'cid' : 14
              , 'pid' : 14
              , 'type_name' : 'SRM.Regatta_C'
              , 'url' : '/v1/SRM-Regatta/14'
              }
            ]
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/SRM-Regatta?verbose&raw&closure&AQ=boat_class,EQ,7&AQ=left,EQ,13'
    }

    >>> _ = show (R.get ("/v1/SRM-Regatta?verbose&raw&closure&AQ=boat_class,EQ,7&AQ=left,EQ,10"))
    { 'json' :
        { 'attribute_names' :
            [ 'left'
            , 'boat_class'
            , 'discards'
            , 'is_cancelled'
            , 'kind'
            , 'races'
            , 'result.date'
            , 'result.software'
            , 'result.status'
            , 'starters_rl'
            ]
        , 'entries' :
            [ { 'attributes_raw' :
                  { 'boat_class' :
                      { 'attributes_raw' :
                          { 'max_crew' : '1'
                          , 'name' : 'Optimist'
                          }
                      , 'cid' : 7
                      , 'pid' : 7
                      , 'type_name' : 'SRM.Boat_Class'
                      , 'url' : '/v1/SRM-Boat_Class/7'
                      }
                  , 'is_cancelled' : 'no'
                  , 'left' :
                      { 'attributes_raw' :
                          { 'date' :
                              { 'finish' : '2008-05-01'
                              , 'start' : '2008-05-01'
                              }
                          , 'name' : 'Himmelfahrt'
                          }
                      , 'cid' : 10
                      , 'pid' : 10
                      , 'type_name' : 'SRM.Regatta_Event'
                      , 'url' : '/v1/SRM-Regatta_Event/10'
                      }
                  }
              , 'cid' : 11
              , 'pid' : 11
              , 'type_name' : 'SRM.Regatta_C'
              , 'url' : '/v1/SRM-Regatta/11'
              }
            ]
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/SRM-Regatta?verbose&raw&closure&AQ=boat_class,EQ,7&AQ=left,EQ,10'
    }
    >>> _ = show (R.get ("/v1/SRM-Regatta?verbose&raw&closure&AQ=left,EQ,10"))
    { 'json' :
        { 'attribute_names' :
            [ 'left'
            , 'boat_class'
            , 'discards'
            , 'is_cancelled'
            , 'kind'
            , 'races'
            , 'result.date'
            , 'result.software'
            , 'result.status'
            , 'starters_rl'
            ]
        , 'entries' :
            [ { 'attributes_raw' :
                  { 'boat_class' :
                      { 'attributes_raw' :
                          { 'max_crew' : '1'
                          , 'name' : 'Optimist'
                          }
                      , 'cid' : 7
                      , 'pid' : 7
                      , 'type_name' : 'SRM.Boat_Class'
                      , 'url' : '/v1/SRM-Boat_Class/7'
                      }
                  , 'is_cancelled' : 'no'
                  , 'left' :
                      { 'attributes_raw' :
                          { 'date' :
                              { 'finish' : '2008-05-01'
                              , 'start' : '2008-05-01'
                              }
                          , 'name' : 'Himmelfahrt'
                          }
                      , 'cid' : 10
                      , 'pid' : 10
                      , 'type_name' : 'SRM.Regatta_Event'
                      , 'url' : '/v1/SRM-Regatta_Event/10'
                      }
                  }
              , 'cid' : 11
              , 'pid' : 11
              , 'type_name' : 'SRM.Regatta_C'
              , 'url' : '/v1/SRM-Regatta/11'
              }
            , { 'attributes_raw' :
                  { 'boat_class' :
                      { 'attributes_raw' : {'name' : 'Yardstick'}
                      , 'cid' : 9
                      , 'pid' : 9
                      , 'type_name' : 'SRM.Handicap'
                      , 'url' : '/v1/SRM-Handicap/9'
                      }
                  , 'is_cancelled' : 'no'
                  , 'left' :
                      { 'pid' : 10
                      , 'url' : '/v1/SRM-Regatta_Event/10'
                      }
                  }
              , 'cid' : 12
              , 'pid' : 12
              , 'type_name' : 'SRM.Regatta_H'
              , 'url' : '/v1/SRM-Regatta/12'
              }
            ]
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/SRM-Regatta?verbose&raw&closure&AQ=left,EQ,10'
    }

    >>> r = show (R.get ("/v1/SRM-Regatta_C?brief"))
    { 'json' :
        { 'entries' :
            [ 11
            , 14
            ]
        , 'url_template' : '/v1/SRM-Regatta_C/{entry}'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/SRM-Regatta_C?brief'
    }

    >>> r = show (R.get ("/v1/SRM-Regatta_H?brief"))
    { 'json' :
        { 'entries' : [12]
        , 'url_template' : '/v1/SRM-Regatta_H/{entry}'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/SRM-Regatta_H?brief'
    }

    >>> r = show (R.get ("/v1/MOM-Object?verbose&raw"))
    { 'json' :
        { 'attribute_names' :
            []
        , 'entries' :
            [ { 'attributes_raw' :
                  { 'first_name' : 'Christian'
                  , 'last_name' : 'Tanzer'
                  , 'middle_name' : ''
                  , 'title' : ''
                  }
              , 'cid' : 1
              , 'pid' : 1
              , 'type_name' : 'PAP.Person'
              , 'url' : '/v1/MOM-Object/1'
              }
            , { 'attributes_raw' :
                  { 'first_name' : 'Laurens'
                  , 'last_name' : 'Tanzer'
                  , 'middle_name' : 'William'
                  , 'title' : ''
                  }
              , 'cid' : 2
              , 'pid' : 2
              , 'type_name' : 'PAP.Person'
              , 'url' : '/v1/MOM-Object/2'
              }
            , { 'attributes_raw' :
                  { 'first_name' : 'Clarissa'
                  , 'last_name' : 'Tanzer'
                  , 'middle_name' : 'Anna'
                  , 'title' : ''
                  }
              , 'cid' : 3
              , 'pid' : 3
              , 'type_name' : 'PAP.Person'
              , 'url' : '/v1/MOM-Object/3'
              }
            , { 'attributes_raw' :
                  { 'max_crew' : '1'
                  , 'name' : 'Optimist'
                  }
              , 'cid' : 7
              , 'pid' : 7
              , 'type_name' : 'SRM.Boat_Class'
              , 'url' : '/v1/MOM-Object/7'
              }
            , { 'attributes_raw' : {'name' : 'Yardstick'}
              , 'cid' : 9
              , 'pid' : 9
              , 'type_name' : 'SRM.Handicap'
              , 'url' : '/v1/MOM-Object/9'
              }
            , { 'attributes_raw' :
                  { 'date' :
                      { 'finish' : '2008-05-01'
                      , 'start' : '2008-05-01'
                      }
                  , 'name' : 'Himmelfahrt'
                  }
              , 'cid' : 10
              , 'pid' : 10
              , 'type_name' : 'SRM.Regatta_Event'
              , 'url' : '/v1/MOM-Object/10'
              }
            , { 'attributes_raw' :
                  { 'date' :
                      { 'finish' : '2008-06-21'
                      , 'start' : '2008-06-20'
                      }
                  , 'name' : 'Guggenberger'
                  }
              , 'cid' : 13
              , 'pid' : 13
              , 'type_name' : 'SRM.Regatta_Event'
              , 'url' : '/v1/MOM-Object/13'
              }
            ]
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/MOM-Object?verbose&raw'
    }

    >>> r = show (R.get ("/v1/MOM-Link?verbose&raw"))
    { 'json' :
        { 'attribute_names' : ['left']
        , 'entries' :
            [ { 'attributes_raw' :
                  { 'club' : None
                  , 'left' :
                      { 'pid' : 1
                      , 'url' : '/v1/PAP-Person/1'
                      }
                  , 'mna_number' : '29676'
                  , 'nation' : 'AUT'
                  }
              , 'cid' : 4
              , 'pid' : 4
              , 'type_name' : 'SRM.Sailor'
              , 'url' : '/v1/MOM-Link/4'
              }
            , { 'attributes_raw' :
                  { 'club' : None
                  , 'left' :
                      { 'pid' : 2
                      , 'url' : '/v1/PAP-Person/2'
                      }
                  , 'mna_number' : ''
                  , 'nation' : 'AUT'
                  }
              , 'cid' : 5
              , 'pid' : 5
              , 'type_name' : 'SRM.Sailor'
              , 'url' : '/v1/MOM-Link/5'
              }
            , { 'attributes_raw' :
                  { 'club' : None
                  , 'left' :
                      { 'pid' : 3
                      , 'url' : '/v1/PAP-Person/3'
                      }
                  , 'mna_number' : ''
                  , 'nation' : 'AUT'
                  }
              , 'cid' : 6
              , 'pid' : 6
              , 'type_name' : 'SRM.Sailor'
              , 'url' : '/v1/MOM-Link/6'
              }
            , { 'attributes_raw' :
                  { 'left' :
                      { 'pid' : 7
                      , 'url' : '/v1/SRM-Boat_Class/7'
                      }
                  , 'nation' : 'AUT'
                  , 'sail_number' : '1107'
                  , 'sail_number_x' : ''
                  }
              , 'cid' : 8
              , 'pid' : 8
              , 'type_name' : 'SRM.Boat'
              , 'url' : '/v1/MOM-Link/8'
              }
            , { 'attributes_raw' :
                  { 'boat_class' :
                      { 'pid' : 7
                      , 'url' : '/v1/SRM-Boat_Class/7'
                      }
                  , 'is_cancelled' : 'no'
                  , 'left' :
                      { 'pid' : 10
                      , 'url' : '/v1/SRM-Regatta_Event/10'
                      }
                  }
              , 'cid' : 11
              , 'pid' : 11
              , 'type_name' : 'SRM.Regatta_C'
              , 'url' : '/v1/MOM-Link/11'
              }
            , { 'attributes_raw' :
                  { 'boat_class' :
                      { 'pid' : 9
                      , 'url' : '/v1/SRM-Handicap/9'
                      }
                  , 'is_cancelled' : 'no'
                  , 'left' :
                      { 'pid' : 10
                      , 'url' : '/v1/SRM-Regatta_Event/10'
                      }
                  }
              , 'cid' : 12
              , 'pid' : 12
              , 'type_name' : 'SRM.Regatta_H'
              , 'url' : '/v1/MOM-Link/12'
              }
            , { 'attributes_raw' :
                  { 'boat_class' :
                      { 'pid' : 7
                      , 'url' : '/v1/SRM-Boat_Class/7'
                      }
                  , 'is_cancelled' : 'no'
                  , 'left' :
                      { 'pid' : 13
                      , 'url' : '/v1/SRM-Regatta_Event/13'
                      }
                  }
              , 'cid' : 14
              , 'pid' : 14
              , 'type_name' : 'SRM.Regatta_C'
              , 'url' : '/v1/MOM-Link/14'
              }
            , { 'attributes_raw' :
                  { 'left' :
                      { 'pid' : 8
                      , 'url' : '/v1/SRM-Boat/8'
                      }
                  , 'right' :
                      { 'pid' : 11
                      , 'url' : '/v1/SRM-Regatta_C/11'
                      }
                  , 'skipper' :
                      { 'pid' : 5
                      , 'url' : '/v1/SRM-Sailor/5'
                      }
                  }
              , 'cid' : 15
              , 'pid' : 15
              , 'type_name' : 'SRM.Boat_in_Regatta'
              , 'url' : '/v1/MOM-Link/15'
              }
            , { 'attributes_raw' :
                  { 'left' :
                      { 'pid' : 8
                      , 'url' : '/v1/SRM-Boat/8'
                      }
                  , 'right' :
                      { 'pid' : 14
                      , 'url' : '/v1/SRM-Regatta_C/14'
                      }
                  , 'skipper' :
                      { 'pid' : 5
                      , 'url' : '/v1/SRM-Sailor/5'
                      }
                  }
              , 'cid' : 16
              , 'pid' : 16
              , 'type_name' : 'SRM.Boat_in_Regatta'
              , 'url' : '/v1/MOM-Link/16'
              }
            ]
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/MOM-Link?verbose&raw'
    }

    >>> r = show (R.get ("/v1/MOM-Link?verbose&raw&closure"))
    { 'json' :
        { 'attribute_names' : ['left']
        , 'entries' :
            [ { 'attributes_raw' :
                  { 'club' : None
                  , 'left' :
                      { 'attributes_raw' :
                          { 'first_name' : 'Christian'
                          , 'last_name' : 'Tanzer'
                          , 'middle_name' : ''
                          , 'title' : ''
                          }
                      , 'cid' : 1
                      , 'pid' : 1
                      , 'type_name' : 'PAP.Person'
                      , 'url' : '/v1/PAP-Person/1'
                      }
                  , 'mna_number' : '29676'
                  , 'nation' : 'AUT'
                  }
              , 'cid' : 4
              , 'pid' : 4
              , 'type_name' : 'SRM.Sailor'
              , 'url' : '/v1/MOM-Link/4'
              }
            , { 'attributes_raw' :
                  { 'club' : None
                  , 'left' :
                      { 'attributes_raw' :
                          { 'first_name' : 'Laurens'
                          , 'last_name' : 'Tanzer'
                          , 'middle_name' : 'William'
                          , 'title' : ''
                          }
                      , 'cid' : 2
                      , 'pid' : 2
                      , 'type_name' : 'PAP.Person'
                      , 'url' : '/v1/PAP-Person/2'
                      }
                  , 'mna_number' : ''
                  , 'nation' : 'AUT'
                  }
              , 'cid' : 5
              , 'pid' : 5
              , 'type_name' : 'SRM.Sailor'
              , 'url' : '/v1/MOM-Link/5'
              }
            , { 'attributes_raw' :
                  { 'club' : None
                  , 'left' :
                      { 'attributes_raw' :
                          { 'first_name' : 'Clarissa'
                          , 'last_name' : 'Tanzer'
                          , 'middle_name' : 'Anna'
                          , 'title' : ''
                          }
                      , 'cid' : 3
                      , 'pid' : 3
                      , 'type_name' : 'PAP.Person'
                      , 'url' : '/v1/PAP-Person/3'
                      }
                  , 'mna_number' : ''
                  , 'nation' : 'AUT'
                  }
              , 'cid' : 6
              , 'pid' : 6
              , 'type_name' : 'SRM.Sailor'
              , 'url' : '/v1/MOM-Link/6'
              }
            , { 'attributes_raw' :
                  { 'left' :
                      { 'attributes_raw' :
                          { 'max_crew' : '1'
                          , 'name' : 'Optimist'
                          }
                      , 'cid' : 7
                      , 'pid' : 7
                      , 'type_name' : 'SRM.Boat_Class'
                      , 'url' : '/v1/SRM-Boat_Class/7'
                      }
                  , 'nation' : 'AUT'
                  , 'sail_number' : '1107'
                  , 'sail_number_x' : ''
                  }
              , 'cid' : 8
              , 'pid' : 8
              , 'type_name' : 'SRM.Boat'
              , 'url' : '/v1/MOM-Link/8'
              }
            , { 'attributes_raw' :
                  { 'boat_class' :
                      { 'pid' : 7
                      , 'url' : '/v1/SRM-Boat_Class/7'
                      }
                  , 'is_cancelled' : 'no'
                  , 'left' :
                      { 'attributes_raw' :
                          { 'date' :
                              { 'finish' : '2008-05-01'
                              , 'start' : '2008-05-01'
                              }
                          , 'name' : 'Himmelfahrt'
                          }
                      , 'cid' : 10
                      , 'pid' : 10
                      , 'type_name' : 'SRM.Regatta_Event'
                      , 'url' : '/v1/SRM-Regatta_Event/10'
                      }
                  }
              , 'cid' : 11
              , 'pid' : 11
              , 'type_name' : 'SRM.Regatta_C'
              , 'url' : '/v1/MOM-Link/11'
              }
            , { 'attributes_raw' :
                  { 'boat_class' :
                      { 'attributes_raw' : {'name' : 'Yardstick'}
                      , 'cid' : 9
                      , 'pid' : 9
                      , 'type_name' : 'SRM.Handicap'
                      , 'url' : '/v1/SRM-Handicap/9'
                      }
                  , 'is_cancelled' : 'no'
                  , 'left' :
                      { 'pid' : 10
                      , 'url' : '/v1/SRM-Regatta_Event/10'
                      }
                  }
              , 'cid' : 12
              , 'pid' : 12
              , 'type_name' : 'SRM.Regatta_H'
              , 'url' : '/v1/MOM-Link/12'
              }
            , { 'attributes_raw' :
                  { 'boat_class' :
                      { 'pid' : 7
                      , 'url' : '/v1/SRM-Boat_Class/7'
                      }
                  , 'is_cancelled' : 'no'
                  , 'left' :
                      { 'attributes_raw' :
                          { 'date' :
                              { 'finish' : '2008-06-21'
                              , 'start' : '2008-06-20'
                              }
                          , 'name' : 'Guggenberger'
                          }
                      , 'cid' : 13
                      , 'pid' : 13
                      , 'type_name' : 'SRM.Regatta_Event'
                      , 'url' : '/v1/SRM-Regatta_Event/13'
                      }
                  }
              , 'cid' : 14
              , 'pid' : 14
              , 'type_name' : 'SRM.Regatta_C'
              , 'url' : '/v1/MOM-Link/14'
              }
            , { 'attributes_raw' :
                  { 'left' :
                      { 'pid' : 8
                      , 'url' : '/v1/SRM-Boat/8'
                      }
                  , 'right' :
                      { 'pid' : 11
                      , 'url' : '/v1/SRM-Regatta_C/11'
                      }
                  , 'skipper' :
                      { 'pid' : 5
                      , 'url' : '/v1/SRM-Sailor/5'
                      }
                  }
              , 'cid' : 15
              , 'pid' : 15
              , 'type_name' : 'SRM.Boat_in_Regatta'
              , 'url' : '/v1/MOM-Link/15'
              }
            , { 'attributes_raw' :
                  { 'left' :
                      { 'pid' : 8
                      , 'url' : '/v1/SRM-Boat/8'
                      }
                  , 'right' :
                      { 'pid' : 14
                      , 'url' : '/v1/SRM-Regatta_C/14'
                      }
                  , 'skipper' :
                      { 'pid' : 5
                      , 'url' : '/v1/SRM-Sailor/5'
                      }
                  }
              , 'cid' : 16
              , 'pid' : 16
              , 'type_name' : 'SRM.Boat_in_Regatta'
              , 'url' : '/v1/MOM-Link/16'
              }
            ]
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/MOM-Link?verbose&raw&closure'
    }

    >>> _ = show (R.get ("/v1/pid/"))
    { 'json' :
        { 'entries' :
            [ '/v1/MOM-Id_Entity/1'
            , '/v1/MOM-Id_Entity/2'
            , '/v1/MOM-Id_Entity/3'
            , '/v1/MOM-Id_Entity/4'
            , '/v1/MOM-Id_Entity/5'
            , '/v1/MOM-Id_Entity/6'
            , '/v1/MOM-Id_Entity/7'
            , '/v1/MOM-Id_Entity/8'
            , '/v1/MOM-Id_Entity/9'
            , '/v1/MOM-Id_Entity/10'
            , '/v1/MOM-Id_Entity/11'
            , '/v1/MOM-Id_Entity/12'
            , '/v1/MOM-Id_Entity/13'
            , '/v1/MOM-Id_Entity/14'
            , '/v1/MOM-Id_Entity/15'
            , '/v1/MOM-Id_Entity/16'
            ]
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/pid/'
    }

    >>> _ = show (R.get ("/v1/pid/1"))
    { 'json' :
        { 'attributes' :
            { 'first_name' : 'christian'
            , 'last_name' : 'tanzer'
            , 'middle_name' : ''
            , 'title' : ''
            }
        , 'cid' : 1
        , 'pid' : 1
        , 'type_name' : 'PAP.Person'
        , 'url' : '/v1/MOM-Id_Entity/1'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/pid/1'
    }

    >>> _ = show (R.get ("/v1/pid?count&strict"))
    { 'json' : {'count' : 0}
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/pid?count&strict'
    }

    >>> _ = show (R.get ("/v1/pid?count"))
    { 'json' : {'count' : 16}
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/pid?count'
    }

    >>> _ = show (R.get ("/RAISE"))
    { 'json' :
        { 'description' : 'Internal server error'
        , 'message' : 'Wilful raisement'
          }
    , 'status' : 500
    , 'url' : 'http://localhost:9999/RAISE'
    }

"""

_test_options = r"""
    >>> server = run_server (%(p1)s, %(n1)s)

    >>> _ = traverse ("http://localhost:9999/")
    / : GET, HEAD, OPTIONS
    /v1/Auth-Account : GET, HEAD, OPTIONS, POST
    /v1/MOM-Id_Entity/1 : DELETE, GET, HEAD, OPTIONS, PUT

"""

_test_post = r"""
    >>> server = run_server (%(p1)s, %(n1)s)

    >>> _ = show (R.get ("/v1/pid?count"))
    { 'json' : {'count' : 16}
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/pid?count'
    }

    >>> snoopy_cargo = json.dumps (
    ...   dict
    ...     ( attributes_raw = dict
    ...         ( last_name   = "Dog"
    ...         , first_name  = "Snoopy"
    ...         , middle_name = "the"
    ...         , lifetime    = dict (start = "20001122")
    ...         )
    ...     )
    ... )
    >>> headers = { "Content-Type": "application/json" }
    >>> _ = show (R.post ("/v1/PAP-Person", headers=headers))
    { 'json' : {'error' : 'You need to send the attributes defining the object with the request in `attributes_raw`(content-type "application/json")'}
    , 'status' : 400
    , 'url' : 'http://localhost:9999/v1/PAP-Person'
    }

    >>> _ = show (R.post ("/v1/PAP-Person", data=snoopy_cargo, headers = {}))
    { 'json' : {'error' : 'You need to send the attributes defining the object with the request in `attributes_raw`(content-type "application/json")'}
    , 'status' : 400
    , 'url' : 'http://localhost:9999/v1/PAP-Person'
    }

    >>> r = showf (R.post ("/v1/PAP-Person", data=snoopy_cargo, headers=headers))
    { 'headers' :
        { 'cache-control' : 'no-cache'
        , 'content-length' : '<length>'
        , 'content-type' : 'application/json'
        , 'date' : '<datetime instance>'
        , 'etag' : 'ETag value'
        , 'link' : '/Doc/PAP-Person; rel=doc'
        , 'location' : 'http://localhost:9999/v1/PAP-Person/17'
        , 'server' : '<server>'
        }
    , 'json' :
        { 'attributes_raw' :
            { 'first_name' : 'Snoopy'
            , 'last_name' : 'Dog'
            , 'lifetime' : {'start' : '2000-11-22'}
            , 'middle_name' : 'The'
            , 'title' : ''
            }
        , 'cid' : 17
        , 'pid' : 17
        , 'type_name' : 'PAP.Person'
        , 'url' : '/v1/PAP-Person/17'
        }
    , 'status' : 201
    , 'url' : 'http://localhost:9999/v1/PAP-Person'
    }

    >>> cargo_bir = json.dumps (
    ...   dict
    ...     ( attributes_raw = dict
    ...         ( left    = dict
    ...             ( left        = ["Optimist"]
    ...             , nation      = "AUT"
    ...             , sail_number = "1134"
    ...             )
    ...         , right   = 11
    ...         , skipper = dict
    ...             ( club        = dict (name = "SC-AMS")
    ...             , left        = 2
    ...             , nation      = "AUT"
    ...             )
    ...         )
    ...     )
    ... )
    >>> _ = show (R.post ("/v1/SRM-Boat_in_Regatta?verbose&raw&closure", data=cargo_bir))
    { 'json' :
        { 'attributes_raw' :
            { 'left' :
                { 'attributes_raw' :
                    { 'left' :
                        { 'attributes_raw' :
                            { 'max_crew' : '1'
                            , 'name' : 'Optimist'
                            }
                        , 'cid' : 7
                        , 'pid' : 7
                        , 'type_name' : 'SRM.Boat_Class'
                        , 'url' : '/v1/SRM-Boat_Class/7'
                        }
                    , 'nation' : 'AUT'
                    , 'sail_number' : '1134'
                    , 'sail_number_x' : ''
                    }
                , 'cid' : 18
                , 'pid' : 18
                , 'type_name' : 'SRM.Boat'
                , 'url' : '/v1/SRM-Boat/18'
                }
            , 'right' :
                { 'attributes_raw' :
                    { 'boat_class' :
                        { 'pid' : 7
                        , 'url' : '/v1/SRM-Boat_Class/7'
                        }
                    , 'is_cancelled' : 'no'
                    , 'left' :
                        { 'attributes_raw' :
                            { 'date' :
                                { 'finish' : '2008-05-01'
                                , 'start' : '2008-05-01'
                                }
                            , 'name' : 'Himmelfahrt'
                            }
                        , 'cid' : 10
                        , 'pid' : 10
                        , 'type_name' : 'SRM.Regatta_Event'
                        , 'url' : '/v1/SRM-Regatta_Event/10'
                        }
                    }
                , 'cid' : 11
                , 'pid' : 11
                , 'type_name' : 'SRM.Regatta_C'
                , 'url' : '/v1/SRM-Regatta_C/11'
                }
            , 'skipper' :
                { 'attributes_raw' :
                    { 'club' :
                        { 'attributes_raw' : {'name' : 'SC-AMS'}
                        , 'cid' : 19
                        , 'pid' : 19
                        , 'type_name' : 'SRM.Club'
                        , 'url' : '/v1/SRM-Club/19'
                        }
                    , 'left' :
                        { 'attributes_raw' :
                            { 'first_name' : 'Laurens'
                            , 'last_name' : 'Tanzer'
                            , 'middle_name' : 'William'
                            , 'title' : ''
                            }
                        , 'cid' : 2
                        , 'pid' : 2
                        , 'type_name' : 'PAP.Person'
                        , 'url' : '/v1/PAP-Person/2'
                        }
                    , 'mna_number' : ''
                    , 'nation' : 'AUT'
                    }
                , 'cid' : 20
                , 'pid' : 20
                , 'type_name' : 'SRM.Sailor'
                , 'url' : '/v1/SRM-Sailor/20'
                }
            }
        , 'cid' : 21
        , 'pid' : 21
        , 'type_name' : 'SRM.Boat_in_Regatta'
        , 'url' : '/v1/SRM-Boat_in_Regatta/21'
        }
    , 'status' : 201
    , 'url' : 'http://localhost:9999/v1/SRM-Boat_in_Regatta?verbose&raw&closure'
    }

    >>> _ = show (R.get ("/v1/pid?count"))
    { 'json' : {'count' : 21}
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/pid?count'
    }

    >>> cargo_c = json.dumps (
    ...   dict
    ...     ( attributes_raw = dict
    ...         ( last_name   = "Tin"
    ...         , first_name  = "Rin"
    ...         , middle_name = "Tin"
    ...         )
    ...     , cid = req_json (r) ["cid"]
    ...     )
    ... )
    >>> ru = requests.utils.urlparse (r.url)
    >>> p  = "%%s://%%s%%s" %% (ru.scheme, ru.netloc, req_json (r) ["url"])
    >>> s  = show (requests.put (p, data=cargo_c, headers=headers))
    { 'json' :
        { 'attributes_raw' :
            { 'first_name' : 'Rin'
            , 'last_name' : 'Tin'
            , 'lifetime' : {'start' : '2000-11-22'}
            , 'middle_name' : 'Tin'
            , 'title' : ''
            }
        , 'cid' : 22
        , 'pid' : 17
        , 'type_name' : 'PAP.Person'
        , 'url' : '/v1/PAP-Person/17'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/PAP-Person/17'
    }

    >>> s  = show (requests.put (p, data=cargo_c, headers=headers))
    { 'json' : {'error' : 'Cid mismatch: requested cid = 17, current cid = 22'}
    , 'status' : 409
    , 'url' : 'http://localhost:9999/v1/PAP-Person/17'
    }

    >>> _ = show (R.get ("/v1/pid?count"))
    { 'json' : {'count' : 21}
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/pid?count'
    }

    >>> cargo_g = json.dumps (
    ...   dict
    ...     ( attributes_raw = dict
    ...         ( last_name   = "Garfield"
    ...         , first_name  = "James"
    ...         , hates       = "mondays"
    ...         )
    ...     )
    ... )
    >>> _ = show (R.post ("/v1/PAP-Person", data=cargo_g, headers=headers))
    { 'json' : {'error' : "Request contains invalid attribute names ('hates',)"}
    , 'status' : 400
    , 'url' : 'http://localhost:9999/v1/PAP-Person'
    }

    >>> _ = show (R.get ("/v1/pid?count"))
    { 'json' : {'count' : 21}
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/pid?count'
    }

    >>> cargo_e = json.dumps (
    ...   dict
    ...     ( attributes_raw = dict
    ...         ( right = dict
    ...             ( address = "rin@tin.tin")
    ...         )
    ...     )
    ... )
    >>> _ = show (R.post ("/v1/PAP-Person/17/email_links", data=cargo_e, headers=headers))
    { 'json' :
        { 'attributes_raw' :
            { 'left' :
                { 'pid' : 17
                , 'url' : '/v1/PAP-Person/17'
                }
            , 'right' :
                { 'pid' : 22
                , 'url' : '/v1/PAP-Email/22'
                }
            }
        , 'cid' : 24
        , 'pid' : 23
        , 'type_name' : 'PAP.Person_has_Email'
        , 'url' : '/v1/PAP-Person_has_Email/23'
        }
    , 'status' : 201
    , 'url' : 'http://localhost:9999/v1/PAP-Person/17/email_links'
    }

    >>> _ = show (R.get ("/v1/PAP-Person/17/email_links?verbose"))
    { 'json' :
        { 'attribute_names' :
            [ 'left'
            , 'right'
            , 'desc'
            ]
        , 'entries' :
            [ { 'attributes' :
                  { 'left' :
                      { 'pid' : 17
                      , 'url' : '/v1/PAP-Person/17'
                      }
                  , 'right' :
                      { 'pid' : 22
                      , 'url' : '/v1/PAP-Email/22'
                      }
                  }
              , 'cid' : 24
              , 'pid' : 23
              , 'type_name' : 'PAP.Person_has_Email'
              , 'url' : '/v1/PAP-Person_has_Email/23'
              }
            ]
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/PAP-Person/17/email_links?verbose'
    }

    >>> _ = show (R.get ("/v1/PAP-Person/17?RELS"))
    { 'json' :
        { 'attributes' :
            { 'first_name' : 'rin'
            , 'last_name' : 'tin'
            , 'lifetime' : {'start' : '2000-11-22'}
            , 'middle_name' : 'tin'
            , 'title' : ''
            }
        , 'cid' : 22
        , 'pid' : 17
        , 'rels' :
            { '/v1/PAP-Person/17/account_links' :
                []
            , '/v1/PAP-Person/17/address_links' :
                []
            , '/v1/PAP-Person/17/email_links' : ['/v1/PAP-Person_has_Email/23']
            , '/v1/PAP-Person/17/phone_links' :
                []
            , '/v1/PAP-Person/17/sailors' :
                []
            , '/v1/PAP-Person/17/url_links' :
                []
            }
        , 'type_name' : 'PAP.Person'
        , 'url' : '/v1/PAP-Person/17'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/PAP-Person/17?RELS'
    }

    >>> _ = show (R.get ("/v1/PAP-Person/17?RELS&verbose"))
    { 'json' :
        { 'attributes' :
            { 'first_name' : 'rin'
            , 'last_name' : 'tin'
            , 'lifetime' : {'start' : '2000-11-22'}
            , 'middle_name' : 'tin'
            , 'title' : ''
            }
        , 'cid' : 22
        , 'pid' : 17
        , 'rels' :
            { '/v1/PAP-Person/17/account_links' :
                []
            , '/v1/PAP-Person/17/address_links' :
                []
            , '/v1/PAP-Person/17/email_links' :
                [ { 'attributes' :
                      { 'left' :
                          { 'pid' : 17
                          , 'url' : '/v1/PAP-Person/17'
                          }
                      , 'right' :
                          { 'pid' : 22
                          , 'url' : '/v1/PAP-Email/22'
                          }
                      }
                  , 'cid' : 24
                  , 'pid' : 23
                  , 'type_name' : 'PAP.Person_has_Email'
                  , 'url' : '/v1/PAP-Person_has_Email/23'
                  }
                ]
            , '/v1/PAP-Person/17/phone_links' :
                []
            , '/v1/PAP-Person/17/sailors' :
                []
            , '/v1/PAP-Person/17/url_links' :
                []
            }
        , 'type_name' : 'PAP.Person'
        , 'url' : '/v1/PAP-Person/17'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/PAP-Person/17?RELS&verbose'
    }

    >>> _ = show (R.post ("/v1/PAP-Person", data=cargo_c, headers=headers))
    { 'json' : {'error' : "The attribute values for ('last_name', 'first_name', 'middle_name', 'title') must be unique for each object\n  The new definition of Person PAP.Person ('Tin', 'Rin', 'Tin', '') would clash with 1 existing entities\n  Already existing:\n    PAP.Person ('Tin', 'Rin', 'Tin', '')"}
    , 'status' : 400
    , 'url' : 'http://localhost:9999/v1/PAP-Person'
    }

"""

_test_put = r"""
    >>> server  = run_server (%(p1)s, %(n1)s)
    >>> headers = { "Content-Type": "application/json" }

    >>> r = show (R.get ("/v1/PAP-Person/1?raw"))
    { 'json' :
        { 'attributes_raw' :
            { 'first_name' : 'Christian'
            , 'last_name' : 'Tanzer'
            , 'middle_name' : ''
            , 'title' : ''
            }
        , 'cid' : 1
        , 'pid' : 1
        , 'rels' :
            [ '/v1/PAP-Person/1/account_links'
            , '/v1/PAP-Person/1/address_links'
            , '/v1/PAP-Person/1/email_links'
            , '/v1/PAP-Person/1/phone_links'
            , '/v1/PAP-Person/1/sailors'
            , '/v1/PAP-Person/1/url_links'
            ]
        , 'type_name' : 'PAP.Person'
        , 'url' : '/v1/PAP-Person/1'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/PAP-Person/1?raw'
    }

    >>> rj = req_json (r)
    >>> cargo_c = json.dumps (
    ...   dict
    ...     ( attributes_raw = rj ["attributes_raw"]
    ...     , cid            = rj ["cid"]
    ...     )
    ... )
    >>> ru = requests.utils.urlparse (r.url)
    >>> p  = "%%s://%%s%%s" %% (ru.scheme, ru.netloc, req_json (r) ["url"])
    >>> s  = show (requests.put (p, data=cargo_c, headers=headers))
    { 'json' :
        { 'attributes_raw' :
            { 'first_name' : 'Christian'
            , 'last_name' : 'Tanzer'
            , 'middle_name' : ''
            , 'title' : ''
            }
        , 'cid' : 1
        , 'pid' : 1
        , 'type_name' : 'PAP.Person'
        , 'url' : '/v1/PAP-Person/1'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/PAP-Person/1'
    }

    >>> sj = req_json (s)
    >>> cargo_c = json.dumps (
    ...   dict
    ...     ( attributes_raw = dict (sj ["attributes_raw"], title = "Mag.")
    ...     , cid            = sj ["cid"]
    ...     )
    ... )
    >>> s2 = show (requests.put (p, data=cargo_c, headers=headers))
    { 'json' :
        { 'attributes_raw' :
            { 'first_name' : 'Christian'
            , 'last_name' : 'Tanzer'
            , 'middle_name' : ''
            , 'title' : 'Mag.'
            }
        , 'cid' : 17
        , 'pid' : 1
        , 'type_name' : 'PAP.Person'
        , 'url' : '/v1/PAP-Person/1'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/PAP-Person/1'
    }

"""

_test_query = r"""
    >>> server = run_server (%(p1)s, %(n1)s)

    >>> _ = show (R.get ("/v1/pid?brief"))
    { 'json' :
        { 'entries' :
            [ 1
            , 2
            , 3
            , 4
            , 5
            , 6
            , 7
            , 8
            , 9
            , 10
            , 11
            , 12
            , 13
            , 14
            , 15
            , 16
            ]
        , 'url_template' : '/v1/MOM-Id_Entity/{entry}'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/pid?brief'
    }

    >>> _ = show (R.get ("/v1/pid?order_by=pid&offset=0&limit=1&brief"))
    { 'json' :
        { 'entries' : [1]
        , 'url_template' : '/v1/MOM-Id_Entity/{entry}'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/pid?order_by=pid&offset=0&limit=1&brief'
    }

    >>> _ = show (R.get ("/v1/pid?order_by=pid&FIRST&limit=1&brief"))
    { 'json' :
        { 'entries' : [1]
        , 'url_template' : '/v1/MOM-Id_Entity/{entry}'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/pid?order_by=pid&FIRST&limit=1&brief'
    }

    >>> _ = show (R.get ("/v1/pid?order_by=pid&offset=-1&limit=1&brief"))
    { 'json' :
        { 'entries' : [16]
        , 'url_template' : '/v1/MOM-Id_Entity/{entry}'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/pid?order_by=pid&offset=-1&limit=1&brief'
    }

    >>> _ = show (R.get ("/v1/pid?order_by=pid&LAST&limit=1&brief"))
    { 'json' :
        { 'entries' : [16]
        , 'url_template' : '/v1/MOM-Id_Entity/{entry}'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/pid?order_by=pid&LAST&limit=1&brief'
    }

    >>> for i in range (10) :
    ...     r = R.get ("/v1/pid?brief&order_by=pid&limit=4&offset=" + str (i))
    ...     print (i, ":", portable_repr (req_json (r)))
    0 : {'entries' : [1, 2, 3, 4], 'url_template' : '/v1/MOM-Id_Entity/{entry}'}
    1 : {'entries' : [2, 3, 4, 5], 'url_template' : '/v1/MOM-Id_Entity/{entry}'}
    2 : {'entries' : [3, 4, 5, 6], 'url_template' : '/v1/MOM-Id_Entity/{entry}'}
    3 : {'entries' : [4, 5, 6, 7], 'url_template' : '/v1/MOM-Id_Entity/{entry}'}
    4 : {'entries' : [5, 6, 7, 8], 'url_template' : '/v1/MOM-Id_Entity/{entry}'}
    5 : {'entries' : [6, 7, 8, 9], 'url_template' : '/v1/MOM-Id_Entity/{entry}'}
    6 : {'entries' : [7, 8, 9, 10], 'url_template' : '/v1/MOM-Id_Entity/{entry}'}
    7 : {'entries' : [8, 9, 10, 11], 'url_template' : '/v1/MOM-Id_Entity/{entry}'}
    8 : {'entries' : [9, 10, 11, 12], 'url_template' : '/v1/MOM-Id_Entity/{entry}'}
    9 : {'entries' : [10, 11, 12, 13], 'url_template' : '/v1/MOM-Id_Entity/{entry}'}

    >>> r = show (R.get ("/v1/PAP-Person.csv?AQ=middle_name,CONTAINS,a&verbose&raw"))
    { 'content' :
        [ 'last_name,first_name,middle_name,title,lifetime.start,lifetime.finish,sex'
        , 'Tanzer,Laurens,William,,,,'
        , 'Tanzer,Clarissa,Anna,,,,'
        ]
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/PAP-Person.csv?AQ=middle_name,CONTAINS,a&verbose&raw'
    }

    >>> r = show (R.get ("/v1/PAP-Person.csv?AQ=middle_name,EQ,&verbose&raw"))
    { 'content' :
        [ 'last_name,first_name,middle_name,title,lifetime.start,lifetime.finish,sex'
        , 'Tanzer,Christian,,,,,'
        ]
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/PAP-Person.csv?AQ=middle_name,EQ,&verbose&raw'
    }

    >>> cargo = json.dumps (
    ...   dict
    ...     ( attributes_raw = dict
    ...         ( left        = "Optimist"
    ...         , nation      = "AUT"
    ...         , sail_number = "1134"
    ...         )
    ...     )
    ... )
    >>> _ = show (R.post ("/v1/SRM-Boat?brief", data=cargo))
    { 'json' :
        { 'attributes_raw' :
            { 'left' : 7
            , 'nation' : 'AUT'
            , 'sail_number' : '1134'
            , 'sail_number_x' : ''
            }
        , 'cid' : 17
        , 'pid' : 17
        , 'type_name' : 'SRM.Boat'
        , 'url' : '/v1/SRM-Boat/17'
        }
    , 'status' : 201
    , 'url' : 'http://localhost:9999/v1/SRM-Boat?brief'
    }

    >>> r = show (R.get ("/v1/SRM-Boat_in_Regatta.csv?verbose&raw&brief"))
    { 'content' :
        [ 'left,right,skipper,place,points,yardstick'
        , '8,11,5,,,'
        , '8,14,5,,,'
        ]
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/SRM-Boat_in_Regatta.csv?verbose&raw&brief'
    }

    ### API-style attribute query
    >>> r = show (R.get ("/v1/SRM-Boat_in_Regatta.csv?AQ=left,EQ,8&verbose&raw&brief"))
    { 'content' :
        [ 'left,right,skipper,place,points,yardstick'
        , '8,11,5,,,'
        , '8,14,5,,,'
        ]
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/SRM-Boat_in_Regatta.csv?AQ=left,EQ,8&verbose&raw&brief'
    }

    >>> r = show (R.get ("/v1/SRM-Boat_in_Regatta.csv?AQ=left,EQ,11&verbose&raw&brief"))
    { 'content' : ['left,right,skipper,place,points,yardstick']
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/SRM-Boat_in_Regatta.csv?AQ=left,EQ,11&verbose&raw&brief'
    }

    >>> r = show (R.get ("/v1/SRM-Boat_in_Regatta.csv?AQ=right,EQ,11&verbose&raw&brief"))
    { 'content' :
        [ 'left,right,skipper,place,points,yardstick'
        , '8,11,5,,,'
        ]
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/SRM-Boat_in_Regatta.csv?AQ=right,EQ,11&verbose&raw&brief'
    }

    >>> r = show (R.get ("/v1/SRM-Boat_in_Regatta.csv?AQ=skipper,EQ,5&verbose&raw&brief"))
    { 'content' :
        [ 'left,right,skipper,place,points,yardstick'
        , '8,11,5,,,'
        , '8,14,5,,,'
        ]
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/SRM-Boat_in_Regatta.csv?AQ=skipper,EQ,5&verbose&raw&brief'
    }

    ### HTML-form-style attribute query
    >>> r = show (R.get ("/v1/SRM-Boat_in_Regatta.csv?left___EQ=8&verbose&raw&brief"))
    { 'content' :
        [ 'left,right,skipper,place,points,yardstick'
        , '8,11,5,,,'
        , '8,14,5,,,'
        ]
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/SRM-Boat_in_Regatta.csv?left___EQ=8&verbose&raw&brief'
    }

    >>> r = show (R.get ("/v1/MOM-Object?count&AQ=last_name,EQ,tanzer"))
    { 'json' :
        { 'description' : 'Bad request'
        , 'message' : "Query restriction triggered error: AttributeError 'MOM.Object doesn't have an attribute named `last_name`'"
        }
    , 'status' : 400
    , 'url' : 'http://localhost:9999/v1/MOM-Object?count&AQ=last_name,EQ,tanzer'
    }
    >>> r = show (R.get ("/v1/PAP-Person?count&AQ=last_name,EQ,tanzer"))
    { 'json' : {'count' : 3}
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/PAP-Person?count&AQ=last_name,EQ,tanzer'
    }

"""

_test_qr_local = """

    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> PAP = scope.PAP
    >>> SRM = scope.SRM
    >>> b4  = SRM.Boat ("Optimist", "1134", "AUT", raw = True)
    >>> print (b4.pid, portable_repr (b4))
    17 SRM.Boat (('optimist', ), 1134, 'AUT', '')

    >>> SRM.Boat_in_Regatta.AQ.boat
    <left.AQ [Attr.Type.Querier Id_Entity]>
    >>> SRM.Boat_in_Regatta.AQ.boat.EQ
    <Attr.Id_Entity_Equal left.EQ [==]>
    >>> SRM.Boat_in_Regatta.AQ.boat.EQ ("8")
    Q.left == 8

    >>> SRM.Boat_in_Regatta.query_s ().all ()
    [SRM.Boat_in_Regatta ((('optimist', ), 1107, 'AUT', ''), (('guggenberger', ('2008-06-20', '2008-06-21')), ('optimist', ))), SRM.Boat_in_Regatta ((('optimist', ), 1107, 'AUT', ''), (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', )))]

    >>> b7 = SRM.Boat.query (sail_number = 1107).one ()
    >>> print (b7.pid, portable_repr (b7))
    8 SRM.Boat (('optimist', ), 1107, 'AUT', '')

    >>> SRM.Boat_in_Regatta.query_s (boat = b7).all ()
    [SRM.Boat_in_Regatta ((('optimist', ), 1107, 'AUT', ''), (('guggenberger', ('2008-06-20', '2008-06-21')), ('optimist', ))), SRM.Boat_in_Regatta ((('optimist', ), 1107, 'AUT', ''), (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', )))]
    >>> SRM.Boat_in_Regatta.query_s (boat = 8).all ()
    [SRM.Boat_in_Regatta ((('optimist', ), 1107, 'AUT', ''), (('guggenberger', ('2008-06-20', '2008-06-21')), ('optimist', ))), SRM.Boat_in_Regatta ((('optimist', ), 1107, 'AUT', ''), (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', )))]
    >>> SRM.Boat_in_Regatta.query_s (boat = "8").all ()
    [SRM.Boat_in_Regatta ((('optimist', ), 1107, 'AUT', ''), (('guggenberger', ('2008-06-20', '2008-06-21')), ('optimist', ))), SRM.Boat_in_Regatta ((('optimist', ), 1107, 'AUT', ''), (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', )))]

    >>> SRM.Boat_in_Regatta.query_s (SRM.Boat_in_Regatta.AQ.boat.EQ (8)).all ()
    [SRM.Boat_in_Regatta ((('optimist', ), 1107, 'AUT', ''), (('guggenberger', ('2008-06-20', '2008-06-21')), ('optimist', ))), SRM.Boat_in_Regatta ((('optimist', ), 1107, 'AUT', ''), (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', )))]
    >>> SRM.Boat_in_Regatta.query_s (SRM.Boat_in_Regatta.AQ.boat.EQ ("8")).all ()
    [SRM.Boat_in_Regatta ((('optimist', ), 1107, 'AUT', ''), (('guggenberger', ('2008-06-20', '2008-06-21')), ('optimist', ))), SRM.Boat_in_Regatta ((('optimist', ), 1107, 'AUT', ''), (('himmelfahrt', ('2008-05-01', '2008-05-01')), ('optimist', )))]

    >>> SRM.Boat_in_Regatta.query_s (boat = b4).all ()
    []
    >>> SRM.Boat_in_Regatta.query_s (boat = 17).all ()
    []
    >>> SRM.Boat_in_Regatta.query_s (SRM.Boat_in_Regatta.AQ.boat.EQ ("17")).all ()
    []


"""

_test_rat = r"""
    >>> server = run_server (%(p1)s, %(n1)s, "Scaffold_RAT")

    >>> _ = traverse ("http://localhost:9999/")
    / : GET, HEAD, OPTIONS
    /v1 : 401 {"description": "Unauthorized"}
    /RAT : OPTIONS, POST

    >>> headers = { "Content-Type": "application/json" }

    >>> rat_cargo = json.dumps (
    ...   dict (user_name = "test@test.test", password = "test"))
    >>> r = R.post ("/RAT", data = rat_cargo, headers = headers)
    >>> show (r)
    { 'json' :
        { 'errors' :
            { 'null' : ['Please enter a username']
            , 'username' : ['A user name is required to login.']
            }
        }
    , 'status' : 400
    , 'url' : 'http://localhost:9999/RAT'
    }
    <Response [400]>

    >>> rat_cargo = json.dumps (dict (username = "test@test.test", password = "test"))
    >>> r = R.post ("/RAT", data = rat_cargo, headers = headers)
    >>> show (r, normalize_json = True)
    { 'json' : {'RAT' : '<REST authorization token>'}
    , 'status' : 200
    , 'url' : 'http://localhost:9999/RAT'
    }
    <Response [200]>

    >>> cookies = r.cookies

    >>> rvo = R.options ("/v1/Auth-Account", cookies = cookies)
    >>> showf (rvo, cleaner = json_cleaner)
    { 'headers' :
        { 'allow' : 'GET, HEAD, OPTIONS, POST'
        , 'cache-control' : 'no-cache'
        , 'content-length' : '<length>'
        , 'content-type' : 'application/json'
        , 'date' : '<datetime instance>'
        , 'etag' : 'ETag value'
        , 'link' : '/Doc/Auth-Account; rel=doc'
        , 'server' : '<server>'
        , 'x-last-cid' : '17'
        }
    , 'json' :
        { 'METHODS' :
            [ 'GET'
            , 'HEAD'
            , 'OPTIONS'
            , 'POST'
            ]
        , 'attributes' :
            { 'editable' :
                [ { 'default_value' : ''
                  , 'description' : 'Email that serves as user name for this account'
                  , 'example' : 'foo@bar.baz'
                  , 'is_changeable' : True
                  , 'is_required' : True
                  , 'is_settable' : True
                  , 'kind' : 'primary'
                  , 'max_length' : 80
                  , 'name' : 'name'
                  , 'p_type' : 'str'
                  , 'type' : 'Email'
                  , 'ui_name' : 'Name'
                  }
                , { 'Choices' :
                      [ 'no'
                      , 'yes'
                      ]
                  , 'default_value' : 'no'
                  , 'description' : 'Specifies if this account is currently enabled, i.e.,\nthe user can login.'
                  , 'example' : 'no'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'optional'
                  , 'name' : 'enabled'
                  , 'p_type' : 'bool'
                  , 'syntax' : 'The following string values are accepted as valid Boolean values: no, yes'
                  , 'type' : 'Boolean'
                  , 'ui_name' : 'Enabled'
                  }
                , { 'Choices' :
                      [ 'no'
                      , 'yes'
                      ]
                  , 'default_value' : 'no'
                  , 'description' : 'Specifies if this account has super-user permissions.'
                  , 'example' : 'no'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'optional'
                  , 'name' : 'superuser'
                  , 'p_type' : 'bool'
                  , 'syntax' : 'The following string values are accepted as valid Boolean values: no, yes'
                  , 'type' : 'Boolean'
                  , 'ui_name' : 'Superuser'
                  }
                ]
            , 'queryable' :
                [ { 'default_value' : ''
                  , 'description' : 'Creation change of the object'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'query'
                  , 'name' : 'creation'
                  , 'p_type' : 'MD_Change'
                  , 'type' : 'Rev_Ref'
                  , 'type_name' : 'MOM.MD_Change'
                  , 'ui_name' : 'Creation'
                  , 'url' : None
                  }
                , { 'default_value' : ''
                  , 'description' : 'Last change of the object'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'query'
                  , 'name' : 'last_change'
                  , 'p_type' : 'MD_Change'
                  , 'type' : 'Rev_Ref'
                  , 'type_name' : 'MOM.MD_Change'
                  , 'ui_name' : 'Last change'
                  , 'url' : None
                  }
                , { 'default_value' : '0'
                  , 'description' : 'Change id of last change for this entity.'
                  , 'example' : '42'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'internal'
                  , 'name' : 'last_cid'
                  , 'p_type' : 'int'
                  , 'type' : 'Int'
                  , 'ui_name' : 'Last cid'
                  }
                , { 'default_value' : ''
                  , 'description' : 'Permanent id of the instance.'
                  , 'example' : '42'
                  , 'explanation' : 'The `pid` is unique over all entities in a given scope. Once\ncreated, the `pid` of an instance never changes and is not ever\nreused for a different instance.\n\nThe `pid` remains unchanged during database migrations.'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'internal'
                  , 'name' : 'pid'
                  , 'p_type' : 'int'
                  , 'type' : 'Surrogate'
                  , 'ui_name' : 'Pid'
                  }
                , { 'default_value' : ''
                  , 'description' : 'Name of type of this entity.'
                  , 'example' : 'foo'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'internal'
                  , 'name' : 'type_name'
                  , 'p_type' : 'str'
                  , 'type' : 'String'
                  , 'ui_name' : 'Type name'
                  }
                , { 'Choices' :
                      [ 'no'
                      , 'yes'
                      ]
                  , 'default_value' : ''
                  , 'description' : 'Specifies if this account is currently active.'
                  , 'example' : 'no'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'query'
                  , 'name' : 'active'
                  , 'p_type' : 'bool'
                  , 'syntax' : 'The following string values are accepted as valid Boolean values: no, yes'
                  , 'type' : 'Boolean'
                  , 'ui_name' : 'Active'
                  }
                , { 'Choices' :
                      [ 'no'
                      , 'yes'
                      ]
                  , 'default_value' : 'yes'
                  , 'description' : 'Specifies if this account is currently suspended\n(due to a pending action).'
                  , 'example' : 'no'
                  , 'is_changeable' : True
                  , 'is_required' : False
                  , 'is_settable' : True
                  , 'kind' : 'internal'
                  , 'name' : 'suspended'
                  , 'p_type' : 'bool'
                  , 'syntax' : 'The following string values are accepted as valid Boolean values: no, yes'
                  , 'type' : 'Boolean'
                  , 'ui_name' : 'Suspended'
                  }
                , { 'default_value' : ''
                  , 'description' : '`Group` linked to `Account`'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'query'
                  , 'name' : 'groups'
                  , 'p_type' : 'Group'
                  , 'role_name' : 'left'
                  , 'type' : 'Role_Ref_Set'
                  , 'type_name' : 'Auth.Group'
                  , 'ui_name' : 'Groups'
                  , 'url' : '/Doc/Auth-Group'
                  }
                , { 'default_value' : ''
                  , 'description' : '`_Account_Action_` links'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'query'
                  , 'name' : '_account_action_s'
                  , 'p_type' : '_Account_Action_'
                  , 'role_name' : 'left'
                  , 'type' : 'Link_Ref_List'
                  , 'type_name' : 'Auth._Account_Action_'
                  , 'ui_name' : ' account action s'
                  , 'url' : None
                  }
                , { 'default_value' : ''
                  , 'description' : '`Account_Activation` link'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'query'
                  , 'name' : 'activation'
                  , 'p_type' : 'Account_Activation'
                  , 'role_name' : 'left'
                  , 'type' : 'Link_Ref'
                  , 'type_name' : 'Auth.Account_Activation'
                  , 'ui_name' : 'Activation'
                  , 'url' : None
                  }
                , { 'default_value' : ''
                  , 'description' : '`Account_Password_Change_Required` link'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'query'
                  , 'name' : 'password_change_required'
                  , 'p_type' : 'Account_Password_Change_Required'
                  , 'role_name' : 'left'
                  , 'type' : 'Link_Ref'
                  , 'type_name' : 'Auth.Account_Password_Change_Required'
                  , 'ui_name' : 'Password change required'
                  , 'url' : None
                  }
                , { 'default_value' : ''
                  , 'description' : '`_Account_Token_Action_` links'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'query'
                  , 'name' : '_account_token_action_s'
                  , 'p_type' : '_Account_Token_Action_'
                  , 'role_name' : 'left'
                  , 'type' : 'Link_Ref_List'
                  , 'type_name' : 'Auth._Account_Token_Action_'
                  , 'ui_name' : ' account token action s'
                  , 'url' : None
                  }
                , { 'default_value' : ''
                  , 'description' : '`Account_EMail_Verification` links'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'query'
                  , 'name' : 'account_email_verifications'
                  , 'p_type' : 'Account_EMail_Verification'
                  , 'role_name' : 'left'
                  , 'type' : 'Link_Ref_List'
                  , 'type_name' : 'Auth.Account_EMail_Verification'
                  , 'ui_name' : 'Account email verifications'
                  , 'url' : None
                  }
                , { 'default_value' : ''
                  , 'description' : '`Account_Password_Reset` links'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'query'
                  , 'name' : 'account_password_resets'
                  , 'p_type' : 'Account_Password_Reset'
                  , 'role_name' : 'left'
                  , 'type' : 'Link_Ref_List'
                  , 'type_name' : 'Auth.Account_Password_Reset'
                  , 'ui_name' : 'Account password resets'
                  , 'url' : None
                  }
                , { 'default_value' : ''
                  , 'description' : '`Person` linked to `Account`'
                  , 'is_changeable' : False
                  , 'is_required' : False
                  , 'is_settable' : False
                  , 'kind' : 'query'
                  , 'name' : 'person'
                  , 'p_type' : 'Person'
                  , 'role_name' : 'right'
                  , 'type' : 'Role_Ref'
                  , 'type_name' : 'PAP.Person'
                  , 'ui_name' : 'Person'
                  , 'url' : '/Doc/PAP-Person'
                  }
                ]
            }
        , 'cross_references' :
            [ { 'attributes' : ['left']
              , 'lra' : 'group_links'
              , 'type_name' : 'Auth.Account_in_Group'
              , 'url' : '/Doc/Auth-Account_in_Group'
              }
            , { 'attributes' : ['right']
              , 'lra' : 'person_links'
              , 'type_name' : 'PAP.Person_has_Account'
              , 'url' : '/Doc/PAP-Person_has_Account'
              }
            ]
        , 'description' : 'An acount which uses passwords for authorization.'
        , 'is_partial' : False
        , 'parents' :
            [ { 'type_name' : 'Auth._Account_'
              , 'url' : '/Doc/Auth-_Account_'
              }
            ]
        , 'type_name' : 'Auth.Account'
        , 'ui_name' : 'Auth.Account'
        , 'url' : '/Doc/Auth-Account'
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/Auth-Account'
    }
    <Response [200]>

    >>> rvo_nc = R.options ("/v1/Auth-Account")
    >>> showf (rvo_nc)
    { 'headers' :
        { 'content-length' : '<length>'
        , 'content-type' : 'application/json'
        , 'date' : '<datetime instance>'
        , 'server' : '<server>'
        , 'www-authenticate' : 'Basic realm="basic-auth"'
        }
    , 'json' : {'description' : 'Unauthorized'}
    , 'status' : 401
    , 'url' : 'http://localhost:9999/v1/Auth-Account'
    }
    <Response [401]>

    >>> rvg = R.get ("/v1/Auth-Account?verbose", cookies = cookies)
    >>> show (rvg)
    { 'json' :
        { 'attribute_names' :
            [ 'name'
            , 'enabled'
            , 'superuser'
            ]
        , 'entries' :
            [ { 'attributes' :
                  { 'enabled' : True
                  , 'name' : 'test@test.test'
                  }
              , 'cid' : 17
              , 'pid' : 17
              , 'type_name' : 'Auth.Account'
              , 'url' : '/v1/Auth-Account/17'
              }
            ]
        }
    , 'status' : 200
    , 'url' : 'http://localhost:9999/v1/Auth-Account?verbose'
    }
    <Response [200]>

"""

__test__ = Scaffold.create_test_dict \
    ( dict
        ( test_client         = _test_client
        , test_cqf            = _test_cqf
        , test_delete         = _test_delete
        , test_doc            = _test_doc
        , test_example_1      = _test_example_1
        , test_example_2      = _test_example_2
        , test_example_3      = _test_example_3
        , test_example_4      = _test_example_4
        , test_get            = _test_get
        , test_options        = _test_options
        , test_rat            = _test_rat
        , test_post           = _test_post
        , test_put            = _test_put
        , test_query          = _test_query
        , test_qr_local       = _test_qr_local
        )
    )

if __name__ == "__main__" :
    rst_harness._main (Scaffold)
### __END__ GTW.__test__.RST
