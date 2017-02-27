# -*- coding: utf-8 -*-
# Copyright (C) 2010-2014 Martin Glueck All rights reserved
# Langstrasse 4, A--2244 Spannberg, Austria. martin@mangari.org
# ****************************************************************************
# This module is part of the package GTW.__test__.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.__test__.Cached_Role_Test
#
# Purpose
#    Test cases for cached role behavior.
#
# Revision Dates
#    21-Apr-2010 (MG) Creation
#    20-Jul-2012 (RS) Add several left-sides (more than one `PAP.Person`)
#    13-Sep-2012 (CT) Add test for `auto_cache_roles`
#     6-Dec-2012 (CT) Add `Person_has_Account` role-cacher
#     6-Dec-2012 (CT) Remove `Entity_created_by_Person`
#    ««revision-date»»···
#--

_test_code = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> PAP      = scope.PAP
    >>> person   = PAP.Person  (u"Test", u"Person")
    >>> person2  = PAP.Person  (u"Another", u"Person")
    >>> address1 = PAP.Address (u"Street 1", u"Zip", u"City", u"Country")
    >>> address2 = PAP.Address (u"Street 2", u"Zip", u"City", u"Country")
    >>> email1   = PAP.Email   (u"person@example.com")
    >>> email2   = PAP.Email   (u"person2@example.com")
    >>> elink1   = PAP.Person_has_Email (person, email1)
    >>> elink2   = PAP.Person_has_Email (person2, email2)

    >>> PAP.Person.addresses
    Role_Ref_Set `addresses`

    >>> sorted (person.addresses) #1
    []
    >>> link = PAP.Person_has_Address (person, address1)
    >>> sorted (person.addresses) #2
    [PAP.Address ('street 1', 'zip', 'city', 'country')]
    >>> sorted (PAP.Person_has_Address.query ().all ())
    [PAP.Person_has_Address (('test', 'person', '', ''), ('street 1', 'zip', 'city', 'country'))]
    >>> link.set (address = address2)
    1
    >>> sorted (person.addresses) #3
    [PAP.Address ('street 2', 'zip', 'city', 'country')]
    >>> link
    PAP.Person_has_Address (('test', 'person', '', ''), ('street 2', 'zip', 'city', 'country'))
    >>> sorted (PAP.Person_has_Address.query ().all ())
    [PAP.Person_has_Address (('test', 'person', '', ''), ('street 2', 'zip', 'city', 'country'))]
    >>> link.set_raw (right = address1.epk_raw)
    1

    >>> prepr ([e.address for e in person.emails])
    ['person@example.com']
    >>> prepr ([e.address for e in person2.emails])
    ['person2@example.com']


"""

from _GTW.__test__.model import *

__test__ = dict \
    ( ** Scaffold.create_test_dict (dict (cache = _test_code))
    )

### __END__ GTW.__test__.Cached_Role_Test
