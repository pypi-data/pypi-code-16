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
#    GTW.__test__.Nested_Change_Recorder
#
# Purpose
#    Test the behavior of the nested change recorder
#
# Revision Dates
#    19-Oct-2010 (MG) Creation
#    30-Jul-2013 (CT) Factor `nested_change_n_query` to improve debug-ability
#    ««revision-date»»···
#--

def nested_change_n_query (PAP, per, scope, fn2) :
    with scope.nested_change_recorder (MOM.SCM.Change.Undoable) :
        per.set_raw (first_name = fn2)
        result = PAP.Person.query (Q.first_name == fn2).all ()
        return result
# end def nested_change_n_query

test_code = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...

    >>> PAP = scope.PAP
    >>> per = PAP.Person ("ln", "fn")
    >>> scope.commit     ()

    >>> fn2 = u"fn2"
    >>> nested_change_n_query (PAP, per, scope, fn2)
    [PAP.Person ('ln', 'fn2', '', '')]

    >>> PAP.Person.query (Q.first_name == fn2).all () ## outside
    [PAP.Person ('ln', 'fn2', '', '')]
"""

from   _GTW.__test__.model                      import *
from   _MOM.import_MOM                          import Q
__test__ = Scaffold.create_test_dict (test_code)

### __END__ GTW.__test__.Nested_Change_Recorder
