# -*- coding: utf-8 -*-
# Copyright (C) 2012-2017 Mag. Christian Tanzer All rights reserved
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
#    GTW.__test__.Subjects
#
# Purpose
#    Test PAP.Subject subclasses and links
#
# Revision Dates
#    24-Mar-2012 (CT) Creation
#    14-Sep-2012 (CT) Add test for role attributes of `Person_has_Address`
#    20-Sep-2012 (CT) Add tests for `Person_has_Phone`, `Subject_has_Property`
#    21-Sep-2012 (CT) Add test for polymorphic link creation
#     6-Mar-2013 (CT) Add import of `Association`
#     6-Mar-2013 (CT) Adapt to new attribute `Company.registered_in`
#     6-Mar-2013 (CT) Add test for `polymorphic_epk` using `children_trans_iter`
#     8-Mar-2013 (CT) Add subclasses of `Association` to test
#                     `polymorphic_epk` over multiple inheritance levels
#    13-Jun-2014 (RS) Fix tests for `PAP.Group`
#     9-Sep-2014 (CT) Add tests for query expressions with type restriction
#    13-Apr-2015 (CT) Add `_test_json`
#    29-Jul-2015 (CT) Adapt to name change of PAP.Phone attributes
#    24-May-2016 (CT) Add test for `ET.AQ.left ['PAP.Person'].middle_name`
#    20-Oct-2016 (CT) Add test for `iea_type_restriction_map`
#    24-Feb-2017 (CT) Import `MOM.Inspect`, not `MOM.inspect`
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

_test_code = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> PAP = scope.PAP

    >>> print (PAP.Subject.count, PAP.Company.count_strict, PAP.Person.count_strict)
    0 0 0

    >>> pg = PAP.Person ("Glueck", "Martin")
    >>> ps = PAP.Person ("Schlatterbeck", "Ralf")
    >>> pt = PAP.Person ("Tanzer", "Christian")
    >>> print (PAP.Subject.count, PAP.Company.count_strict, PAP.Person.count_strict)
    3 0 3

    >>> cl = PAP.Company ("Lucky Software", short_name = "LS")
    >>> co = PAP.Company ("Open Source Consulting", short_name = "OSC")
    >>> print (PAP.Subject.count, PAP.Company.count_strict, PAP.Person.count_strict)
    5 2 3

    >>> prepr (PAP.Subject.query_s ().all ())
    [PAP.Person ('glueck', 'martin', '', ''), PAP.Company ('lucky software', ''), PAP.Company ('open source consulting', ''), PAP.Person ('schlatterbeck', 'ralf', '', ''), PAP.Person ('tanzer', 'christian', '', '')]
    >>> prepr (PAP.Company.query_s ().all ())
    [PAP.Company ('lucky software', ''), PAP.Company ('open source consulting', '')]
    >>> prepr (PAP.Person.query_s ().all ())
    [PAP.Person ('glueck', 'martin', '', ''), PAP.Person ('schlatterbeck', 'ralf', '', ''), PAP.Person ('tanzer', 'christian', '', '')]

    >>> eg  = PAP.Email ("martin@mangari.org")
    >>> es  = PAP.Email ("ralf@runtux.com")
    >>> et1 = PAP.Email ("tanzer@swing.co.at")
    >>> et2 = PAP.Email ("tanzer@gg32.com")

    >>> _ = PAP.Subject_has_Property (pg, eg)
    >>> _ = PAP.Subject_has_Property (ps, es)
    >>> _ = PAP.Subject_has_Property (pt, et1)
    >>> _ = PAP.Subject_has_Property (pt, et2)

    >>> _ = PAP.Company_has_Email (cl, PAP.Email ("lucky@mangari.org"))
    >>> _ = PAP.Company_has_Email (co, PAP.Email ("office@runtux.com"))

    >>> _ = PAP.Person_has_Phone  (pg, PAP.Phone ("43", "1", "234567", raw = True))
    >>> _ = PAP.Person_has_Phone  (ps, PAP.Phone ("43", "1", "987654", raw = True))
    >>> _ = PAP.Person_has_Phone  (pt, PAP.Phone ("43", "1", "135790", raw = True))
    >>> _ = PAP.Company_has_Phone (co, PAP.Phone ("43", "1", "246802", raw = True), extension = "16", raw = True)

    >>> PAP.Subject_has_Property.query ().count ()
    10

    >>> PAP.Subject_has_Property.query (Q.left ["PAP.Association"]).count ()
    0

    >>> PAP.Subject_has_Property.query (Q.left ["PAP.Legal_Entity"]).count ()
    3

    >>> PAP.Subject_has_Property.query (Q.left ["PAP.Company"]).count ()
    3

    >>> PAP.Subject_has_Property.query (Q.left ["PAP.Person"]).count ()
    7

    >>> PAP.Subject_has_Property.query (Q.right ["PAP.Address"]).count ()
    0

    >>> PAP.Subject_has_Property.query (Q.right ["PAP.Email"]).count ()
    6

    >>> PAP.Subject_has_Property.query (Q.right ["PAP.Email"].address.CONTAINS (".co")).count ()
    4

    >>> PAP.Subject_has_Property.query (Q.right ["PAP.Email"].address.ENDSWITH ("@mangari.org")).count ()
    2

    >>> PAP.Subject_has_Property.query (Q.right [Q.PAP.Phone]).count ()
    4

    >>> prepr (PAP.Subject_has_Email.query_s ().all ())
    [PAP.Person_has_Email (('glueck', 'martin', '', ''), ('martin@mangari.org', )), PAP.Company_has_Email (('lucky software', ''), ('lucky@mangari.org', )), PAP.Company_has_Email (('open source consulting', ''), ('office@runtux.com', )), PAP.Person_has_Email (('schlatterbeck', 'ralf', '', ''), ('ralf@runtux.com', )), PAP.Person_has_Email (('tanzer', 'christian', '', ''), ('tanzer@gg32.com', )), PAP.Person_has_Email (('tanzer', 'christian', '', ''), ('tanzer@swing.co.at', ))]
    >>> prepr (PAP.Company_has_Email.query_s ().all ())
    [PAP.Company_has_Email (('lucky software', ''), ('lucky@mangari.org', )), PAP.Company_has_Email (('open source consulting', ''), ('office@runtux.com', ))]
    >>> prepr (PAP.Person_has_Email.query_s ().all ())
    [PAP.Person_has_Email (('glueck', 'martin', '', ''), ('martin@mangari.org', )), PAP.Person_has_Email (('schlatterbeck', 'ralf', '', ''), ('ralf@runtux.com', )), PAP.Person_has_Email (('tanzer', 'christian', '', ''), ('tanzer@gg32.com', )), PAP.Person_has_Email (('tanzer', 'christian', '', ''), ('tanzer@swing.co.at', ))]

    >>> prepr (PAP.Subject_has_Email.query_s (Q.right.address.ENDSWITH ("@mangari.org")).all ())
    [PAP.Person_has_Email (('glueck', 'martin', '', ''), ('martin@mangari.org', )), PAP.Company_has_Email (('lucky software', ''), ('lucky@mangari.org', ))]
    >>> prepr (PAP.Subject_has_Email.query_s (Q.right.address.CONTAINS (".co")).all ())
    [PAP.Company_has_Email (('open source consulting', ''), ('office@runtux.com', )), PAP.Person_has_Email (('schlatterbeck', 'ralf', '', ''), ('ralf@runtux.com', )), PAP.Person_has_Email (('tanzer', 'christian', '', ''), ('tanzer@gg32.com', )), PAP.Person_has_Email (('tanzer', 'christian', '', ''), ('tanzer@swing.co.at', ))]
    >>> prepr (PAP.Person_has_Email.query_s (Q.right.address.ENDSWITH ("@mangari.org")).all ())
    [PAP.Person_has_Email (('glueck', 'martin', '', ''), ('martin@mangari.org', ))]
    >>> prepr (PAP.Person_has_Email.query_s (Q.right.address.CONTAINS (".co")).all ())
    [PAP.Person_has_Email (('schlatterbeck', 'ralf', '', ''), ('ralf@runtux.com', )), PAP.Person_has_Email (('tanzer', 'christian', '', ''), ('tanzer@gg32.com', )), PAP.Person_has_Email (('tanzer', 'christian', '', ''), ('tanzer@swing.co.at', ))]

    >>> prepr (sorted (pg.emails, key = PAP.Email.sorted_by))
    [PAP.Email ('martin@mangari.org')]
    >>> prepr (sorted (ps.emails, key = PAP.Email.sorted_by))
    [PAP.Email ('ralf@runtux.com')]
    >>> prepr (sorted (pt.emails, key = PAP.Email.sorted_by))
    [PAP.Email ('tanzer@gg32.com'), PAP.Email ('tanzer@swing.co.at')]

    >>> _ = PAP.Company_has_Email (co, "ralf@runtux.com")

    >>> prepr (sorted (cl.emails, key = PAP.Email.sorted_by))
    [PAP.Email ('lucky@mangari.org')]
    >>> prepr (sorted (co.emails, key = PAP.Email.sorted_by))
    [PAP.Email ('office@runtux.com'), PAP.Email ('ralf@runtux.com')]

    >>> rr = PAP.Email.instance ("ralf@runtux.com")
    >>> prepr (sorted (rr.persons, key = PAP.Person.sorted_by))
    [PAP.Person ('schlatterbeck', 'ralf', '', '')]
    >>> prepr (sorted (rr.companies, key = PAP.Company.sorted_by))
    [PAP.Company ('open source consulting', '')]

    >>> prepr (PAP.Subject_has_Property.query_s ().all ())
    [PAP.Person_has_Phone (('glueck', 'martin', '', ''), ('43', '1', '234567'), ''), PAP.Person_has_Email (('glueck', 'martin', '', ''), ('martin@mangari.org', )), PAP.Company_has_Email (('lucky software', ''), ('lucky@mangari.org', )), PAP.Company_has_Phone (('open source consulting', ''), ('43', '1', '246802'), '16'), PAP.Company_has_Email (('open source consulting', ''), ('office@runtux.com', )), PAP.Company_has_Email (('open source consulting', ''), ('ralf@runtux.com', )), PAP.Person_has_Phone (('schlatterbeck', 'ralf', '', ''), ('43', '1', '987654'), ''), PAP.Person_has_Email (('schlatterbeck', 'ralf', '', ''), ('ralf@runtux.com', )), PAP.Person_has_Phone (('tanzer', 'christian', '', ''), ('43', '1', '135790'), ''), PAP.Person_has_Email (('tanzer', 'christian', '', ''), ('tanzer@gg32.com', )), PAP.Person_has_Email (('tanzer', 'christian', '', ''), ('tanzer@swing.co.at', ))]
    >>> prepr (PAP.Subject_has_Property.query_s (left = pt).all ())
    [PAP.Person_has_Phone (('tanzer', 'christian', '', ''), ('43', '1', '135790'), ''), PAP.Person_has_Email (('tanzer', 'christian', '', ''), ('tanzer@gg32.com', )), PAP.Person_has_Email (('tanzer', 'christian', '', ''), ('tanzer@swing.co.at', ))]

    >>> prepr (PAP.Subject_has_Property.query_s (subject = pt).all ())
    [PAP.Person_has_Phone (('tanzer', 'christian', '', ''), ('43', '1', '135790'), ''), PAP.Person_has_Email (('tanzer', 'christian', '', ''), ('tanzer@gg32.com', )), PAP.Person_has_Email (('tanzer', 'christian', '', ''), ('tanzer@swing.co.at', ))]

    >>> prepr (PAP.Subject_has_Phone.query_s (Q.right.sn.CONTAINS ("2")).all ())
    [PAP.Person_has_Phone (('glueck', 'martin', '', ''), ('43', '1', '234567'), ''), PAP.Company_has_Phone (('open source consulting', ''), ('43', '1', '246802'), '16')]

    >>> prepr (PAP.Subject_has_Phone.query_s (Q.extension != "").all ())
    [PAP.Company_has_Phone (('open source consulting', ''), ('43', '1', '246802'), '16')]

    >>> def show_emails (ET) :
    ...     attr = ET.emails
    ...     print (attr.attr.__class__, ":", attr.description, "[", attr.Ref_Type.type_name, "]")
    >>> show_emails (PAP.Subject)
    <class '_GTW._OMP._PAP.Subject.emails'> : `Email` linked to `Subject` [ PAP.Subject_has_Email ]

    >>> show_emails (PAP.Company)
    <class '_GTW._OMP._PAP.Company.emails'> : `Email` linked to `Company` [ PAP.Company_has_Email ]

    >>> show_emails (PAP.Person)
    <class '_GTW._OMP._PAP.Person.emails'> : `Email` linked to `Person` [ PAP.Person_has_Email ]

    >>> ET = PAP.Person_has_Address.E_Type
    >>> prepr (sorted (ET.role_map))
    ['Address', 'PAP.Address', 'PAP.Person', 'Person', 'address', 'left', 'person', 'right']
    >>> ET.Roles
    (Person `left`, Address `right`)
    >>> ET.edit_attr
    (Person `left`, Address `right`, String `desc`)
    >>> ET.attributes ["left"], ET.attributes ["person"]
    (Person `left`, Person `left`)
    >>> ET.attributes ["right"], ET.attributes ["address"]
    (Address `right`, Address `right`)

    >>> for T, l in children_trans_iter (scope.PAP.Subject_has_Property) :
    ...     rr = T.relevant_root.type_name if T.relevant_root else sorted (T.relevant_roots)
    ...     print ("%%-32s %%-5s %%s" %% ("%%s%%s" %% ("  " * l, T.type_name), T.is_partial, rr))
    PAP.Subject_has_Property         True  PAP.Subject_has_Property
      PAP.Subject_has_Address        True  PAP.Subject_has_Property
        PAP.Company_has_Address      False PAP.Subject_has_Property
        PAP.Person_has_Address       False PAP.Subject_has_Property
        PAP.Association_has_Address  False PAP.Subject_has_Property
      PAP.Subject_has_Email          True  PAP.Subject_has_Property
        PAP.Company_has_Email        False PAP.Subject_has_Property
        PAP.Person_has_Email         False PAP.Subject_has_Property
        PAP.Association_has_Email    False PAP.Subject_has_Property
      PAP.Subject_has_Phone          True  PAP.Subject_has_Property
        PAP.Company_has_Phone        False PAP.Subject_has_Property
        PAP.Person_has_Phone         False PAP.Subject_has_Property
        PAP.Association_has_Phone    False PAP.Subject_has_Property
      PAP.Subject_has_Url            True  PAP.Subject_has_Property
        PAP.Company_has_Url          False PAP.Subject_has_Property
        PAP.Person_has_Url           False PAP.Subject_has_Property
        PAP.Association_has_Url      False PAP.Subject_has_Property

    >>> fmt = "%%(type_name)-20s %%(is_relevant)-5s %%(polymorphic_epk)-5s %%(polymorphic_epks)-6s %%(epk_sig)s"
    >>> for i, et in enumerate (scope.app_type._T_Extension) :
    ...   if not i :
    ...     print (fmt %% (dict (type_name = "type_name", is_relevant = "relev", epk_sig = "epk_sig", polymorphic_epk = "p_epk", polymorphic_epks = "p_epks")))
    ...     print ("=" * 75)
    ...   if issubclass (et, scope.PAP.Subject.E_Type) :
    ...     print (fmt %% TFL.Caller.Object_Scope (et))
    type_name            relev p_epk p_epks epk_sig
    ===========================================================================
    PAP.Subject          False True  True   ()
    PAP.Group            False True  True   ('name',)
    PAP.Legal_Entity     False True  True   ('name',)
    PAP.Company          True  False False  ('name', 'registered_in')
    PAP.Person           True  False False  ('last_name', 'first_name', 'middle_name', 'title')
    PAP.Association      True  True  True   ('name',)
    PAP.Association_S    True  True  True   ('name',)
    PAP.Association_T    True  False False  ('name', 'epk_new')

    >>> sk = lambda x : (not bool (x.children), x.i_rank)
    >>> for i, (T, l) in enumerate (children_trans_iter (scope.MOM.Id_Entity, sort_key = sk)) :
    ...     if not i :
    ...         print ("%%-50s   %%6s %%6s %%6s %%6s" %% ("type_name", "relev", "p_epk", "p_epks", "pr_epk"))
    ...         print ("=" * 80)
    ...     et = T.E_Type
    ...     fs = (et.is_relevant, et.polymorphic_epk, et.polymorphic_epks, et.polymorphic_relevant_epk)
    ...     if any (fs) :
    ...         hd  = "%%s%%s" %% ("  " * l, et.type_name)
    ...         hdl = len (hd)
    ...         sep = (" " if hdl %% 2 else "") + ". " * ((50 - hdl) // 2)
    ...         ts  = tuple ((x or "") for x in fs)
    ...         print (("%%s %%s %%6s %%6s %%6s %%6s" %% ((hd, sep) + ts)).rstrip ())
    type_name                                             relev  p_epk p_epks pr_epk
    ================================================================================
    MOM.Id_Entity  . . . . . . . . . . . . . . . . . .           True   True
      MOM.Link . . . . . . . . . . . . . . . . . . . .           True   True
        MOM.Link1  . . . . . . . . . . . . . . . . . .           True   True
          Auth.Link1 . . . . . . . . . . . . . . . . .           True   True
            Auth._Account_Action_  . . . . . . . . . .           True   True
                Auth.Account_EMail_Verification  . . .    True
                Auth.Account_Password_Reset  . . . . .    True
              Auth.Account_Activation  . . . . . . . .    True
              Auth.Account_Password_Change_Required  .    True
          EVT.Link1  . . . . . . . . . . . . . . . . .           True   True
            EVT._Recurrence_Mixin_ . . . . . . . . . .           True   True
              EVT.Recurrence_Spec  . . . . . . . . . .    True          True
              EVT.Recurrence_Rule  . . . . . . . . . .    True          True
            EVT.Event  . . . . . . . . . . . . . . . .    True          True
            EVT.Event_occurs . . . . . . . . . . . . .    True          True
            PAP.Address_Position . . . . . . . . . . .    True
          SRM.Link1  . . . . . . . . . . . . . . . . .           True   True
            SRM.Regatta  . . . . . . . . . . . . . . .    True
              SRM.Regatta_C  . . . . . . . . . . . . .    True
              SRM.Regatta_H  . . . . . . . . . . . . .    True
            SRM.Boat . . . . . . . . . . . . . . . . .    True
            SRM.Sailor . . . . . . . . . . . . . . . .    True
            SRM.Race_Result  . . . . . . . . . . . . .    True
            SRM.Team . . . . . . . . . . . . . . . . .    True
          SWP.Link1  . . . . . . . . . . . . . . . . .           True   True
            SWP.Clip_O . . . . . . . . . . . . . . . .    True          True
            SWP.Picture  . . . . . . . . . . . . . . .    True
        MOM._Link_n_ . . . . . . . . . . . . . . . . .           True   True
          MOM.Link2  . . . . . . . . . . . . . . . . .           True   True
              Auth.Account_in_Group  . . . . . . . . .    True
            PAP.Link2  . . . . . . . . . . . . . . . .           True   True
              PAP.Subject_has_Property . . . . . . . .    True   True   True   True
                PAP.Subject_has_Address  . . . . . . .    True          True
                  PAP.Company_has_Address  . . . . . .    True
                  PAP.Person_has_Address . . . . . . .    True
                  PAP.Association_has_Address  . . . .    True          True
                PAP.Subject_has_Email  . . . . . . . .    True          True
                  PAP.Company_has_Email  . . . . . . .    True
                  PAP.Person_has_Email . . . . . . . .    True
                  PAP.Association_has_Email  . . . . .    True          True
                PAP.Subject_has_Phone  . . . . . . . .    True          True   True
                  PAP.Company_has_Phone  . . . . . . .    True
                  PAP.Person_has_Phone . . . . . . . .    True
                  PAP.Association_has_Phone  . . . . .    True          True
                PAP.Subject_has_Url  . . . . . . . . .    True          True
                  PAP.Company_has_Url  . . . . . . . .    True
                  PAP.Person_has_Url . . . . . . . . .    True
                  PAP.Association_has_Url  . . . . . .    True          True
              PAP.Person_has_Account . . . . . . . . .    True
              SRM.Boat_in_Regatta  . . . . . . . . . .    True
              SRM.Crew_Member  . . . . . . . . . . . .    True
              SRM.Team_has_Boat_in_Regatta . . . . . .    True
          PAP._Link_n_ . . . . . . . . . . . . . . . .           True   True
        Auth.Link  . . . . . . . . . . . . . . . . . .           True   True
        EVT.Link . . . . . . . . . . . . . . . . . . .           True   True
        PAP.Link . . . . . . . . . . . . . . . . . . .           True   True
        SRM.Link . . . . . . . . . . . . . . . . . . .           True   True
        SWP.Link . . . . . . . . . . . . . . . . . . .           True   True
      MOM.Object . . . . . . . . . . . . . . . . . . .           True   True
        Auth.Object  . . . . . . . . . . . . . . . . .           True   True
            Auth.Account . . . . . . . . . . . . . . .    True
          Auth.Certificate . . . . . . . . . . . . . .    True
          Auth.Group . . . . . . . . . . . . . . . . .    True
        EVT.Object . . . . . . . . . . . . . . . . . .           True   True
          EVT.Calendar . . . . . . . . . . . . . . . .    True
        PAP.Object . . . . . . . . . . . . . . . . . .           True   True
          PAP.Property . . . . . . . . . . . . . . . .           True   True
            PAP.Address  . . . . . . . . . . . . . . .    True
            PAP.Email  . . . . . . . . . . . . . . . .    True
            PAP.Phone  . . . . . . . . . . . . . . . .    True
            PAP.Url  . . . . . . . . . . . . . . . . .    True
          PAP.Subject  . . . . . . . . . . . . . . . .           True   True
            PAP.Group  . . . . . . . . . . . . . . . .           True   True
              PAP.Legal_Entity . . . . . . . . . . . .           True   True
                PAP.Association  . . . . . . . . . . .    True   True   True   True
                  PAP.Association_S  . . . . . . . . .    True   True   True   True
                    PAP.Association_T  . . . . . . . .    True                 True
                PAP.Company  . . . . . . . . . . . . .    True
            PAP.Person . . . . . . . . . . . . . . . .    True
        SRM.Object . . . . . . . . . . . . . . . . . .           True   True
          SRM._Boat_Class_ . . . . . . . . . . . . . .    True
            SRM.Boat_Class . . . . . . . . . . . . . .    True
            SRM.Handicap . . . . . . . . . . . . . . .    True
          SRM.Club . . . . . . . . . . . . . . . . . .    True
          SRM.Regatta_Event  . . . . . . . . . . . . .    True
          SRM.Page . . . . . . . . . . . . . . . . . .    True                 True
        SWP.Object . . . . . . . . . . . . . . . . . .           True   True
          SWP.Object_PN  . . . . . . . . . . . . . . .           True   True
            SWP.Page . . . . . . . . . . . . . . . . .    True   True   True   True
              SWP.Page_Y . . . . . . . . . . . . . . .    True                 True
              SWP.Clip_X . . . . . . . . . . . . . . .    True
            SWP.Gallery  . . . . . . . . . . . . . . .    True
            SWP.Referral . . . . . . . . . . . . . . .    True
      Auth.Id_Entity . . . . . . . . . . . . . . . . .           True   True
      EVT.Id_Entity  . . . . . . . . . . . . . . . . .           True   True
      PAP.Id_Entity  . . . . . . . . . . . . . . . . .           True   True
      SRM.Id_Entity  . . . . . . . . . . . . . . . . .           True   True
      SWP.Id_Entity  . . . . . . . . . . . . . . . . .           True   True

"""

_test_json = r"""

    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> PAP = scope.PAP

    >>> print (PAP.Subject.count, PAP.Company.count_strict, PAP.Person.count_strict)
    0 0 0

    >>> pg  = PAP.Person ("Glück", "Martin")
    >>> php = PAP.Person_has_Phone  (pg, PAP.Phone ("43", "1", "234567", raw = True))

    >>> from _TFL.json_dump import to_string as jsonified
    >>> prepr(jsonified ({ "obj" : pg.FO}))
    '{"obj": "Gl\\u00fcck Martin"}'

    >>> prepr (jsonified (pg))
    '{"display": "Gl\\u00fcck Martin", "pid": 1}'

    >>> for et in scope.app_type._T_Extension :
    ...     if et.iea_type_restriction_map :
    ...         print ("%%-40s : %%s" %% (et.type_name, et.iea_type_restrictions))
    PAP.Subject_has_Address                  : (Q.right ["PAP.Address"],)
    PAP.Subject_has_Email                    : (Q.right ["PAP.Email"],)
    PAP.Subject_has_Phone                    : (Q.right ["PAP.Phone"],)
    PAP.Subject_has_Url                      : (Q.right ["PAP.Url"],)
    PAP.Company_has_Url                      : (Q.left ["PAP.Company"], Q.right ["PAP.Url"])
    PAP.Person_has_Url                       : (Q.left ["PAP.Person"], Q.right ["PAP.Url"])
    PAP.Association_has_Url                  : (Q.left ["PAP.Association"], Q.right ["PAP.Url"])
    PAP.Company_has_Phone                    : (Q.left ["PAP.Company"], Q.right ["PAP.Phone"])
    PAP.Person_has_Phone                     : (Q.left ["PAP.Person"], Q.right ["PAP.Phone"])
    PAP.Association_has_Phone                : (Q.left ["PAP.Association"], Q.right ["PAP.Phone"])
    PAP.Company_has_Email                    : (Q.left ["PAP.Company"], Q.right ["PAP.Email"])
    PAP.Person_has_Email                     : (Q.left ["PAP.Person"], Q.right ["PAP.Email"])
    PAP.Association_has_Email                : (Q.left ["PAP.Association"], Q.right ["PAP.Email"])
    PAP.Company_has_Address                  : (Q.left ["PAP.Company"], Q.right ["PAP.Address"])
    PAP.Person_has_Address                   : (Q.left ["PAP.Person"], Q.right ["PAP.Address"])
    PAP.Association_has_Address              : (Q.left ["PAP.Association"], Q.right ["PAP.Address"])

"""

_test_saw = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> PAP = scope.PAP

    >>> print (PAP.Subject_has_Property.query (Q.left ["PAP.Legal_Entity"]))
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_subject_has_phone.extension AS pap_subject_has_phone_extension,
           pap_subject_has_phone.pid AS pap_subject_has_phone_pid,
           pap_subject_has_property."desc" AS pap_subject_has_property_desc,
           pap_subject_has_property."left" AS pap_subject_has_property_left,
           pap_subject_has_property."right" AS pap_subject_has_property_right,
           pap_subject_has_property.pid AS pap_subject_has_property_pid
         FROM mom_id_entity
           JOIN pap_subject_has_property ON mom_id_entity.pid = pap_subject_has_property.pid
           LEFT OUTER JOIN pap_subject_has_phone ON pap_subject_has_property.pid = pap_subject_has_phone.pid
           LEFT OUTER JOIN pap_company AS pap_company__1 ON pap_company__1.pid = pap_subject_has_property."left"
           LEFT OUTER JOIN pap_association AS pap_association__1 ON pap_association__1.pid = pap_subject_has_property."left"
         WHERE pap_company__1.pid IS NOT NULL
            OR pap_association__1.pid IS NOT NULL

    >>> print (PAP.Subject_has_Property.query (Q.left ["PAP.Legal_Entity"].name == "ISAF").formatted ())
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_subject_has_phone.extension AS pap_subject_has_phone_extension,
           pap_subject_has_phone.pid AS pap_subject_has_phone_pid,
           pap_subject_has_property."desc" AS pap_subject_has_property_desc,
           pap_subject_has_property."left" AS pap_subject_has_property_left,
           pap_subject_has_property."right" AS pap_subject_has_property_right,
           pap_subject_has_property.pid AS pap_subject_has_property_pid
         FROM mom_id_entity
           JOIN pap_subject_has_property ON mom_id_entity.pid = pap_subject_has_property.pid
           LEFT OUTER JOIN pap_subject_has_phone ON pap_subject_has_property.pid = pap_subject_has_phone.pid
           LEFT OUTER JOIN pap_company AS pap_company__1 ON pap_company__1.pid = pap_subject_has_property."left"
           LEFT OUTER JOIN pap_association AS pap_association__1 ON pap_association__1.pid = pap_subject_has_property."left"
         WHERE pap_company__1.name = :name_1
            OR pap_association__1.name = :name_2
    Parameters:
         name_1               : 'ISAF'
         name_2               : 'ISAF'

    >>> ETM    = PAP.Subject_has_Property
    >>> ET     = ETM.E_Type
    >>> aq     = getattr (ET.AQ, "left[PAP.Person]middle_name")
    >>> aq1    = ET.AQ.left ['PAP.Person'].middle_name
    >>> aqacat = aq.AC  ('ta')
    >>> aqaca1 = aq1.AC ('ta')
    >>> manual = Q.left ["PAP.Person"].middle_name.STARTSWITH ('ta')

    >>> print (ETM.query (manual).formatted ())
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_subject_has_phone.extension AS pap_subject_has_phone_extension,
           pap_subject_has_phone.pid AS pap_subject_has_phone_pid,
           pap_subject_has_property."desc" AS pap_subject_has_property_desc,
           pap_subject_has_property."left" AS pap_subject_has_property_left,
           pap_subject_has_property."right" AS pap_subject_has_property_right,
           pap_subject_has_property.pid AS pap_subject_has_property_pid
         FROM mom_id_entity
           JOIN pap_subject_has_property ON mom_id_entity.pid = pap_subject_has_property.pid
           LEFT OUTER JOIN pap_subject_has_phone ON pap_subject_has_property.pid = pap_subject_has_phone.pid
           LEFT OUTER JOIN pap_person ON pap_person.pid = pap_subject_has_property."left"
         WHERE (pap_person.middle_name LIKE :middle_name_1 || '%%%%')
    Parameters:
         middle_name_1          : 'ta'

    >>> print (ETM.query (aqacat).formatted ())
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_subject_has_phone.extension AS pap_subject_has_phone_extension,
           pap_subject_has_phone.pid AS pap_subject_has_phone_pid,
           pap_subject_has_property."desc" AS pap_subject_has_property_desc,
           pap_subject_has_property."left" AS pap_subject_has_property_left,
           pap_subject_has_property."right" AS pap_subject_has_property_right,
           pap_subject_has_property.pid AS pap_subject_has_property_pid
         FROM mom_id_entity
           JOIN pap_subject_has_property ON mom_id_entity.pid = pap_subject_has_property.pid
           LEFT OUTER JOIN pap_subject_has_phone ON pap_subject_has_property.pid = pap_subject_has_phone.pid
           LEFT OUTER JOIN pap_person ON pap_person.pid = pap_subject_has_property."left"
         WHERE (pap_person.middle_name LIKE :middle_name_1 || '%%%%')
    Parameters:
         middle_name_1          : 'ta'

    >>> print (ETM.query (aqaca1).formatted ())
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_subject_has_phone.extension AS pap_subject_has_phone_extension,
           pap_subject_has_phone.pid AS pap_subject_has_phone_pid,
           pap_subject_has_property."desc" AS pap_subject_has_property_desc,
           pap_subject_has_property."left" AS pap_subject_has_property_left,
           pap_subject_has_property."right" AS pap_subject_has_property_right,
           pap_subject_has_property.pid AS pap_subject_has_property_pid
         FROM mom_id_entity
           JOIN pap_subject_has_property ON mom_id_entity.pid = pap_subject_has_property.pid
           LEFT OUTER JOIN pap_subject_has_phone ON pap_subject_has_property.pid = pap_subject_has_phone.pid
           LEFT OUTER JOIN pap_person ON pap_person.pid = pap_subject_has_property."left"
         WHERE (pap_person.middle_name LIKE :middle_name_1 || '%%%%')
    Parameters:
         middle_name_1          : 'ta'

"""

### XXX auto cached roles are currently not supported
### XXX * either remove _test_acr or re-add auto-cached roles and fix _test_acr
_test_acr = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> PAP = scope.PAP

    >>> PAP.Subject_has_Email.acr_map.get ("left", False)
    False
    >>> PAP.Company_has_Email.acr_map.get ("left", False)
    <Role_Cacher_n (GTW.OMP.PAP.Company_has_Email) company --> companies [GTW.OMP.PAP.Email]>
    >>> PAP.Person_has_Email.acr_map.get ("left", False)
    <Role_Cacher_n (GTW.OMP.PAP.Person_has_Email) person --> persons [GTW.OMP.PAP.Email]>

    >>> PAP.Subject_has_Email.acr_map.get ("right", False)
    <Role_Cacher_n (GTW.OMP.PAP.Subject_has_Email) email --> emails [GTW.OMP.PAP.Subject]>
    >>> PAP.Company_has_Email.acr_map.get ("right", False)
    <Role_Cacher_n (GTW.OMP.PAP.Company_has_Email) email --> emails [GTW.OMP.PAP.Company]>
    >>> PAP.Person_has_Email.acr_map.get ("right", False)
    <Role_Cacher_n (GTW.OMP.PAP.Person_has_Email) email --> emails [GTW.OMP.PAP.Person]>

    >>> sorted (PAP.Subject_has_Email.acr_map.values (), key = TFL.Getter.attr_name)
    [<Role_Cacher_n (GTW.OMP.PAP.Subject_has_Email) email --> emails [GTW.OMP.PAP.Subject]>]
    >>> sorted (PAP.Company_has_Email.acr_map.values (), key = TFL.Getter.attr_name)
    [<Role_Cacher_n (GTW.OMP.PAP.Company_has_Email) company --> companies [GTW.OMP.PAP.Email]>, <Role_Cacher_n (GTW.OMP.PAP.Company_has_Email) email --> emails [GTW.OMP.PAP.Company]>]
    >>> sorted (PAP.Person_has_Email.acr_map.values (), key = TFL.Getter.attr_name)
    [<Role_Cacher_n (GTW.OMP.PAP.Person_has_Email) email --> emails [GTW.OMP.PAP.Person]>, <Role_Cacher_n (GTW.OMP.PAP.Person_has_Email) person --> persons [GTW.OMP.PAP.Email]>]

"""

from   _GTW.__test__.model      import *
from   _MOM.import_MOM          import Q
from   _MOM.Inspect             import children_trans_iter

from   itertools                import chain as ichain

import _GTW._OMP._PAP.Association

_Ancestor_Essence = GTW.OMP.PAP.Association

class Association_S (_Ancestor_Essence) :
    """Descendent of Association with identical epk_sig"""
# end class Association_S

_Ancestor_Essence = Association_S

class Association_T (_Ancestor_Essence) :
    """Descendent of Association_S with different epk_sig"""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class epk_new (A_Int) :
            """Additional epk attribute"""

            kind               = Attr.Primary

        # end class epk_new

    # end class _Attributes

# end class Association_T

__test__ = Scaffold.create_test_dict \
    ( dict
        ( test_code           = _test_code
        , test_json           = _test_json
        )
    )

__test__.update \
    ( Scaffold.create_test_dict
        ( dict
            ( test_saw = _test_saw
            )
        , ignore = ("HPS", )
        )
    )


### __END__ GTW.__test__.Subjects
