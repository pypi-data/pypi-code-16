# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Martin Glueck All rights reserved
# Langstrasse 4, A--2244 Spannberg. martin@mangari.org
# ****************************************************************************
# This module is part of the package GTW.__test__.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.__test__.Missing_Primary_Key
#
# Purpose
#    Test what happens if one tries to create an object where a primary key
#    is correctly specified during object creation
#
# Revision Dates
#    22-Jun-2010 (MG) Creation
#    22-Jun-2010 (CT) Creation continued
#    12-Apr-2012 (CT) Extend tests for `on_error`
#    15-Apr-2012 (CT) Adapt to changes of `MOM.Error`
#    16-Apr-2012 (CT) Adapt to more changes of `MOM.Error`
#    17-Apr-2012 (CT) Add test for `as_json_cargo (* errors)`
#    15-Jun-2015 (CT) Add tests where `None` is passed for primary attribute
#    ««revision-date»»···
#--

from   __future__               import print_function

_test_code = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> PAP = scope.PAP
    >>> errors = []
    >>> print (PAP.Person.count)
    0
    >>> with expect_except (MOM.Error.Invariants) :
    ...     PAP.Person (last_name = u"", first_name = u"", raw = True)
    Invariants: Condition `first_name_not_empty` : The attribute first_name needs a non-empty value
        first_name = None
      Condition `last_name_not_empty` : The attribute last_name needs a non-empty value
        last_name = None
    >>> errors
    []
    >>> print (PAP.Person.count)
    0

    >>> with expect_except (MOM.Error.Invariants) :
    ...     PAP.Person (last_name = None, first_name = None, raw = True)
    Invariants: Condition `first_name_not_empty` : The attribute first_name needs a non-empty value
        first_name = None
      Condition `last_name_not_empty` : The attribute last_name needs a non-empty value
        last_name = None

    >>> with expect_except (MOM.Error.Invariants) :
    ...     PAP.Person (last_name = None, first_name = None)
    Invariants: Condition `first_name_not_empty` : The attribute first_name needs a non-empty value
        first_name = None
      Condition `last_name_not_empty` : The attribute last_name needs a non-empty value
        last_name = None

    >>> with expect_except (MOM.Error.Invariants, save_error = errors) :
    ...     PAP.Person \
    ...     ( last_name  = u"last_name"
    ...     , first_name = u""
    ...     , raw        = True
    ...     )
    ...
    Invariants: Condition `first_name_not_empty` : The attribute first_name needs a non-empty value
        first_name = None

    >>> errors
    [<Invariants: <Required_Empty: PAP.Person ('', '', '', ''), Condition `first_name_not_empty` : The attribute first_name needs a non-empty value
        first_name = None>>]
    >>> for e in errors :
    ...     print (e)
    Condition `first_name_not_empty` : The attribute first_name needs a non-empty value
        first_name = None

    >>> print (formatted (MOM.Error.as_json_cargo (* errors)))
    [ { 'attributes' : ['first_name']
      , 'bindings' :
          [ ( 'first_name'
            , "''"
            )
          ]
      , 'head' : 'The attribute first_name needs a non-empty value'
      , 'is_required' : True
      }
    ]

    >>> errors = []
    >>> with expect_except (MOM.Error.Invariants, save_error = errors) :
    ...     PAP.Person (last_name = u"", first_name = u"", raw = True)
    Invariants: Condition `first_name_not_empty` : The attribute first_name needs a non-empty value
        first_name = None
      Condition `last_name_not_empty` : The attribute last_name needs a non-empty value
        last_name = None
    >>> print (formatted (MOM.Error.as_json_cargo (* errors)))
    [ { 'attributes' : ['first_name']
      , 'bindings' :
          [ ( 'first_name'
            , "''"
            )
          ]
      , 'head' : 'The attribute first_name needs a non-empty value'
      , 'is_required' : True
      }
    , { 'attributes' : ['last_name']
      , 'bindings' :
          [ ( 'last_name'
            , "''"
            )
          ]
      , 'head' : 'The attribute last_name needs a non-empty value'
      , 'is_required' : True
      }
    ]

    >>> print (PAP.Person.count)
    0

    >>> prepr (PAP.Person.epkified_ckd.args)
    "last_name, first_name, middle_name = '', title = ''"
    >>> PAP.Person.epk_sig
    ('last_name', 'first_name', 'middle_name', 'title')
    >>> PAP.Person.primary_required
    [String `last_name`, String `first_name`]

"""

from _GTW.__test__.model import *

__test__ = Scaffold.create_test_dict (_test_code)

### __END__ GTW.__test__.Missing_Primary_Key
