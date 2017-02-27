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
#    GTW.__test__.readonly
#
# Purpose
#    Test `readonly` databases and state switches
#
# Revision Dates
#    11-Aug-2010 (MG) Creation
#    16-Aug-2010 (CT) Don't re-use `db_man` (destroy & re-connect, instead)
#    ««revision-date»»···
#--

_test_code = r"""

    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> p = scope.PAP.Person (u"LN", u"FN")
    >>> scope.commit () ### should work

    >>> scope.ems.session.readonly ### 1
    False

    >>> scope.destroy ()

    >>> apt, url = Scaffold.app_type_and_url (%(p1)s, %(n1)s)
    >>> db_man   = MOM.DB_Man.connect (apt, url)
    >>> db_man.change_readonly (True)
    >>> db_man.destroy ()

    >>> scope = Scaffold.scope (%(p1)s, %(n1)s, create = False) # doctest:+ELLIPSIS
    Loading scope MOMT__...

    >>> scope.ems.session.readonly ### 2
    True

    The scope is now readonly. So commiting a change should raise an error
    >>> p2 = scope.PAP.Person (u"LN2", u"FN")
    >>> with expect_except (MOM.Error.Readonly_DB) :
    ...     scope.commit () # commit after create fails
    Readonly_DB: Database is set to readonly.

    >>> scope.ems.session.readonly ### 3
    True

    The scope is now readonly. So commiting a change should raise an error
    >>> p = scope.PAP.Person.query ().one ()
    >>> p.set_raw    (title = u"Ing.")
    1
    >>> with expect_except (MOM.Error.Readonly_DB) :
    ...     scope.commit () ### update fails
    Readonly_DB: Database is set to readonly.

    >>> scope.ems.session.readonly ### 4
    True

    >>> scope.PAP.Person.query ().all () ### without title
    [PAP.Person ('ln', 'fn', '', '')]

    >>> scope.destroy ()

    Let's change the readonly back to False
    >>> db_man = MOM.DB_Man.connect (apt, url)
    >>> db_man.change_readonly (False)
    >>> db_man.destroy ()

    >>> scope = Scaffold.scope (%(p1)s, %(n1)s, create = False) # doctest:+ELLIPSIS
    Loading scope MOMT__...
    >>> p = scope.PAP.Person.query ().one ()

    >>> scope.ems.session.readonly ### 5
    False

    >>> p.set_raw (title = u"Ing.")
    1
    >>> scope.commit           () # last
    >>> apt.delete_database    (url)

"""

from _GTW.__test__.model import *

Scaffold.Backend_Default_Path ["SQL"] = "'test.sqlite'"
Scaffold.Backend_Default_Path ["sq"]  = "'test.sqlite'"
Scaffold.Backend_Default_Path ["HPS"] = "'test.hps'"

__test__ = Scaffold.create_test_dict (_test_code)

### __END__ GTW.__test__.readonly
