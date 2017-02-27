# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Martin Glueck All rights reserved
# Langstrasse 4, A--2244 Spannberg, Austria. martin@mangari.org
# #*** <License> ************************************************************#
# This module is part of the package GTW.__test__.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.__test__.Query_Attribute
#
# Purpose
#    Test for query attributes
#
# Revision Dates
#    23-Jan-2013 (MG) Creation
#    26-Jan-2013 (CT) Add test for query attribute referring to cached role
#    27-Jan-2013 (CT) Add another test for `.qt.last_name`
#    31-Jan-2013 (CT) Add tests for `Q.person` passed to `Account.query`
#     1-Feb-2013 (RS) Tests for query attribute via auto_cache attribute
#     1-Feb-2013 (RS) Add queries for transitive query attribute
#    12-Feb-2013 (CT) Add more tests for `wrzlbrmft`
#    12-Feb-2013 (CT) Set `Person_has_Wrzlbrmft.left.max_links` to `1`,
#                     remove `Person_has_Wrzlbrmft.right.max_links`
#    15-May-2013 (CT) Disable tests for SAS backends
#    13-Jun-2013 (CT) Remove `PNS_Aliases`
#    ««revision-date»»···
#--

from   __future__ import absolute_import, division, print_function, unicode_literals

_query_test = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> Auth  = scope.Auth
    >>> PAP   = scope.PAP
    >>> p1    = PAP.Person ("ln", "fn", lifetime = ("20130101", ), raw = True)
    >>> p2    = PAP.Person ("ln", "nf", lifetime = ("20130101", ), raw = True)
    >>> p3    = PAP.Person ("nl", "fn", lifetime = ("20130101", ), raw = True)
    >>> a1    = Auth.Account_T ("test-ln+fn@foo.bar")
    >>> a2    = Auth.Account_T ("test-ln+nf@foo.bar")
    >>> a3    = Auth.Account_T ("test-nl-fn@foo.bar")
    >>> pha1  = PAP.Person_has_Account_Test (p1, a1)
    >>> pha2  = PAP.Person_has_Account_Test (p2, a2)
    >>> pha3  = PAP.Person_has_Account_Test (p3, a3)
    >>> scope.commit ()

    >>> a1.person
    PAP.Person ('ln', 'fn', '', '')

    >>> a1.qt
    PAP.Person ('ln', 'fn', '', '')

    >>> prepr (p1.accounts)
    {Auth.Account_T ('test-ln+fn@foo.bar')}

    >>> pha1.owner
    PAP.Person ('ln', 'fn', '', '')

    >>> PAP.Person_has_Account_Test.query (Q.owner.last_name == "nl").all ()
    [PAP.Person_has_Account_Test (('nl', 'fn', '', ''), ('test-nl-fn@foo.bar', ))]

    >>> Auth.Account_T.query (Q.qt.last_name == "ln").count ()
    2

    >>> Auth.Account_T.query_s (Q.qt.last_name == "ln").all ()
    [Auth.Account_T ('test-ln+fn@foo.bar'), Auth.Account_T ('test-ln+nf@foo.bar')]

    >>> Auth.Account.query_s (Q.person == p1).all ()
    [Auth.Account_T ('test-ln+fn@foo.bar')]

    >>> Auth.Account.query_s (Q.person.first_name == "nf").all ()
    [Auth.Account_T ('test-ln+nf@foo.bar')]

    >>> nicky = PAP.Person_Nickname_Test (p1, 'nicky', raw = True)
    >>> nicky
    PAP.Person_Nickname_Test (('ln', 'fn', '', ''), 'nicky')

    >>> wolp = PAP.Wolperdinger ("Wolp", raw = True)
    >>> wolp
    PAP.Wolperdinger ('Wolp')
    >>> w = PAP.Wrzlbrmft ('WRZL', wolp, raw = True)
    >>> w
    PAP.Wrzlbrmft ('WRZL', ('Wolp', ))
    >>> phw = PAP.Person_has_Wrzlbrmft (p1, w)
    >>> phw
    PAP.Person_has_Wrzlbrmft (('ln', 'fn', '', ''), ('WRZL', ('Wolp', )))

    >>> PAP.Wrzlbrmft.query (Q.my_wolp == wolp).all ()
    [PAP.Wrzlbrmft ('WRZL', ('Wolp', ))]

    >>> PAP.Person_has_Wrzlbrmft.query_s (Q.right == w).all ()
    [PAP.Person_has_Wrzlbrmft (('ln', 'fn', '', ''), ('WRZL', ('Wolp', )))]

    >>> PAP.Person_has_Wrzlbrmft.query_s (Q.wrzlbrmft == w).all ()
    [PAP.Person_has_Wrzlbrmft (('ln', 'fn', '', ''), ('WRZL', ('Wolp', )))]

    >>> PAP.Person_has_Wrzlbrmft.query_s (Q.wrzlbrmft.my_wolp == wolp).all ()
    [PAP.Person_has_Wrzlbrmft (('ln', 'fn', '', ''), ('WRZL', ('Wolp', )))]

    >>> PAP.Person.query_s (Q.wrzlbrmft == w).all ()
    [PAP.Person ('ln', 'fn', '', '')]

    >>> PAP.Person.query_s (Q.wrzlbrmft.wolp == wolp).all ()
    [PAP.Person ('ln', 'fn', '', '')]

    >>> PAP.Person.query_s (Q.wrzlbrmft.my_wolp == wolp).all ()
    [PAP.Person ('ln', 'fn', '', '')]

    >>> Auth.Account_T.query_s (Q.person.wrzlbrmft.wolp == wolp).all ()
    [Auth.Account_T ('test-ln+fn@foo.bar')]

    >>> Auth.Account_T.query_s (Q.person.wrzlbrmft.my_wolp == wolp).all ()
    [Auth.Account_T ('test-ln+fn@foo.bar')]

    >>> Auth.Account_T.query_s (Q.p_wrzl.my_wolp == wolp).all ()
    [Auth.Account_T ('test-ln+fn@foo.bar')]

    >>> Auth.Account_T.query_s (Q.p_nick.name == "nicky").all ()
    [Auth.Account_T ('test-ln+fn@foo.bar')]

"""

_test_saw = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> Auth  = scope.Auth
    >>> PAP   = scope.PAP

    >>> from   _MOM._DBW._SAW import QX

    >>> qfa = Q.qt.wrzlbrmft.wolp == 42
    >>> qra = Auth.Account_T.query ()
    >>> qxa = QX.Mapper (qra)
    >>> qza = qxa (qfa)

    >>> print (QX.display (qza))
    Bin:__eq__:
      <PAP.Wrzlbrmft | QX.Kind_EPK for
           <SAW : Entity `wolp` [pap_wrzlbrmft__1.wolp]>>
          <PAP.Person | QX.Kind_Rev_Query for
               <SAW : Role_Ref `wrzlbrmft`>>
              <Auth.Account | QX.Kind_Rev_Query for
                   <SAW : Role_Ref `person`>>
                  <Auth.Account_T | QX.Kind_Query for
                       <SAW : Entity `qt`>>
      42

    >>> qra.filter (qfa)
    SQL: SELECT
           auth_account.enabled AS auth_account_enabled,
           auth_account.name AS auth_account_name,
           auth_account.password AS auth_account_password,
           auth_account.ph_name AS auth_account_ph_name,
           auth_account.pid AS auth_account_pid,
           auth_account.superuser AS auth_account_superuser,
           auth_account.suspended AS auth_account_suspended,
           auth_account_t.pid AS auth_account_t_pid,
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked
         FROM mom_id_entity
           JOIN auth_account ON mom_id_entity.pid = auth_account.pid
           JOIN auth_account_t ON auth_account.pid = auth_account_t.pid
           LEFT OUTER JOIN pap_person_has_account AS pap_person_has_account__1 ON pap_person_has_account__1."right" = auth_account.pid
           LEFT OUTER JOIN pap_person AS pap_person__1 ON pap_person__1.pid = pap_person_has_account__1."left"
           LEFT OUTER JOIN pap_person_has_wrzlbrmft AS pap_person_has_wrzlbrmft__1 ON pap_person_has_wrzlbrmft__1."left" = pap_person__1.pid
           LEFT OUTER JOIN pap_wrzlbrmft AS pap_wrzlbrmft__1 ON pap_wrzlbrmft__1.pid = pap_person_has_wrzlbrmft__1."right"
         WHERE pap_wrzlbrmft__1.wolp = :wolp_1

    >>> qfh = Q.owner.wrzlbrmft.my_wolp == 17
    >>> qrh = PAP.Person_has_Account_Test.query ()
    >>> qxh = QX.Mapper (qrh)

    >>> print (QX.display (qxh (qfh)))
    Bin:__eq__:
      <PAP.Wrzlbrmft | QX.Kind_EPK for
           <SAW : Entity `wolp` [pap_wrzlbrmft__2.wolp]>>
          <PAP.Wrzlbrmft | QX.Kind_Query for
               <SAW : Entity `my_wolp`>>
              <PAP.Person | QX.Kind_Rev_Query for
                   <SAW : Role_Ref `wrzlbrmft`>>
                  <PAP.Person_has_Account | QX.Kind_EPK for
                       <SAW : Person `left` [pap_person_has_account.left]>>
                      <PAP.Person_has_Account_Test | QX.Kind_Query for
                           <SAW : Entity `owner`>>
      17

    >>> qrh.filter (qfh)
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
           pap_person_has_account."left" AS pap_person_has_account_left,
           pap_person_has_account."right" AS pap_person_has_account_right,
           pap_person_has_account.pid AS pap_person_has_account_pid,
           pap_person_has_account_test.pid AS pap_person_has_account_test_pid
         FROM mom_id_entity
           JOIN pap_person_has_account ON mom_id_entity.pid = pap_person_has_account.pid
           JOIN pap_person_has_account_test ON pap_person_has_account.pid = pap_person_has_account_test.pid
           JOIN pap_person AS pap_person__2 ON pap_person__2.pid = pap_person_has_account."left"
           LEFT OUTER JOIN pap_person_has_wrzlbrmft AS pap_person_has_wrzlbrmft__2 ON pap_person_has_wrzlbrmft__2."left" = pap_person__2.pid
           LEFT OUTER JOIN pap_wrzlbrmft AS pap_wrzlbrmft__2 ON pap_wrzlbrmft__2.pid = pap_person_has_wrzlbrmft__2."right"
         WHERE pap_wrzlbrmft__2.wolp = :wolp_1

    >>> qfp = Q.wrzlbrmft.wolp == 23
    >>> qrp = PAP.Person.query ()
    >>> qxp = QX.Mapper (qrp)

    >>> print (QX.display (qxp (qfp)))
    Bin:__eq__:
      <PAP.Wrzlbrmft | QX.Kind_EPK for
           <SAW : Entity `wolp` [pap_wrzlbrmft__3.wolp]>>
          <PAP.Person | QX.Kind_Rev_Query for
               <SAW : Role_Ref `wrzlbrmft`>>
      23

    >>> qrp.filter (qfp)
    SQL: SELECT
           mom_id_entity.electric AS mom_id_entity_electric,
           mom_id_entity.last_cid AS mom_id_entity_last_cid,
           mom_id_entity.pid AS mom_id_entity_pid,
           mom_id_entity.type_name AS mom_id_entity_type_name,
           mom_id_entity.x_locked AS mom_id_entity_x_locked,
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
           JOIN pap_person ON mom_id_entity.pid = pap_person.pid
           LEFT OUTER JOIN pap_person_has_wrzlbrmft AS pap_person_has_wrzlbrmft__3 ON pap_person_has_wrzlbrmft__3."left" = pap_person.pid
           LEFT OUTER JOIN pap_wrzlbrmft AS pap_wrzlbrmft__3 ON pap_wrzlbrmft__3.pid = pap_person_has_wrzlbrmft__3."right"
         WHERE pap_wrzlbrmft__3.wolp = :wolp_1


    >>> str (Auth.Account_T.query (Q.p_wrzl.my_wolp == 42)) == str(Auth.Account_T.query (Q.p_wrzl.wolp == 42))
    True

"""

from   _GTW.__test__.Test_Command import *
import _GTW._OMP._Auth.import_Auth
import _GTW._OMP._PAP .import_PAP

_Ancestor_Essence = GTW.OMP.PAP.Link1

class Person_Nickname_Test (_Ancestor_Essence) :
    """ A nickname with `max_links = 1` for testing """

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class left (_Ancestor.left) :

            role_type          = GTW.OMP.PAP.Person
            max_links          = 1
            auto_rev_ref       = True
            link_ref_attr_name = "nick"

        # end class left

        class name (A_String) :

            kind            = Attr.Primary
            max_length      = 32

        # end class name

    # end class _Attributes

# end class Person_Nickname_Test

_Ancestor_Essence = GTW.OMP.PAP.Object

class Wolperdinger (_Ancestor_Essence) :
    """A class for testing an ID entitiy attribute"""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class name (A_String) :

            kind               = Attr.Primary
            max_length         = 32

        # end class name

    # end class _Attributes

# end class Wolperdinger

_Ancestor_Essence = GTW.OMP.PAP.Object

class Wrzlbrmft (_Ancestor_Essence) :
    """ Wrzlbrmft: A special Person property for testing """

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class name (A_String) :

            kind               = Attr.Primary
            max_length         = 32

        # end class name

        class wolp (A_Id_Entity) :

            kind               = Attr.Primary
            P_Type             = Wolperdinger

        # end class wolp

        class my_wolp (A_Id_Entity) :
            """ model my own attribute as query """

            kind               = Attr.Query
            P_Type             = Wolperdinger
            hidden             = True
            query              = Q.wolp

        # end class my_wolp

    # end class _Attributes

# end class Wrzlbrmft

_Ancestor_Essence = GTW.OMP.PAP.Link2

class Person_has_Wrzlbrmft (_Ancestor_Essence) :
    """ A Person property for testing """

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class left (_Ancestor.left) :

            role_type          = GTW.OMP.PAP.Person
            max_links          = 1

        # end class left

        class right (_Ancestor.right) :

            role_type          = Wrzlbrmft
            auto_rev_ref       = True

        # end class right

    # end class _Attributes

# end class Person_has_Wrzlbrmft

_Ancestor_Essence = GTW.OMP.Auth.Account

class Account_T (_Ancestor_Essence) :
    """Test of query attributes"""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class qt (A_Id_Entity) :
            """Test of access to cached role attribute"""

            kind               = Attr.Query
            P_Type             = GTW.OMP.PAP.Person
            query              = Q.person

        # end class qt

        class p_nick (A_Id_Entity) :
            """Test of access to query attributes via cached role"""

            kind               = Attr.Query
            P_Type             = Person_Nickname_Test
            query              = Q.person.nick

        # end class p_nick

        class p_wrzl (A_Id_Entity) :
            """ Test of access to query attribute via cached role """

            kind               = Attr.Query
            P_Type             = Wrzlbrmft
            query              = Q.person.wrzlbrmft

        # end class p_wrzl

    # end class _Attributes

# end class Account_T

_Ancestor_Essence = GTW.OMP.PAP.Person_has_Account

class Person_has_Account_Test (_Ancestor_Essence) :
    """Test of query attribute"""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        ### Primary attributes

        ### Non-primary attributes

        class owner (A_Id_Entity) :
            """Alias for the person"""

            kind               = Attr.Query
            query              = Q.left

        # end class owner

    # end class _Attributes

# end class Person_has_Account_Test

Scaffold = GTW_Test_Command ()

__test__ = Scaffold.create_test_dict \
    ( dict (query = _query_test)
    )

__test__.update \
    ( Scaffold.create_test_dict
        ( dict
            ( test_saw = _test_saw
            )
        , ignore = ("HPS", )
        )
    )


### __END__ GTW.__test__.Query_Attribute
