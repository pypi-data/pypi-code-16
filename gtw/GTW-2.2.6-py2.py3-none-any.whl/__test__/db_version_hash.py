# -*- coding: utf-8 -*-
# Copyright (C) 2010-2014 Martin Glueck All rights reserved
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
#    GTW.__test__.db_version_hash
#
# Purpose
#    Test for the database version hash check for the SAS backend
#
# Revision Dates
#    15-Jul-2010 (MG) Creation
#    11-Aug-2010 (MG) Real database test added
#    16-Aug-2010 (MG) `_simple_test` cleanup impooved to be able run multiple
#                     backend tests in one run
#    ««revision-date»»···
#--

from   __future__               import print_function

_simple_test = r"""
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> apt, url = scope.app_type, scope.db_url
    >>> dbv      = scope.ems.db_meta_data.dbv_hash
    >>> guid     = scope.guid
    >>> scope.destroy ()

Now, let's try to load this scope again (which should work since we have the
same database version):

    >>> scope = Scaffold.scope (%(p1)s, %(n1)s, create = False) # doctest:+ELLIPSIS
    Loading scope MOMT__...
    >>> scope.guid                      == guid
    True
    >>> scope.ems.db_meta_data.dbv_hash == dbv
    True
    >>> scope.destroy ()

Now let's simulate a change of the database version hash:

    >>> apt.db_version_hash = "<a version hash which should never happen>"
    >>> with expect_except (MOM.Error.Incompatible_DB_Version) :
    ...     scope = Scaffold.scope (%(p1)s, %(n1)s, create = False) # doctest:+ELLIPSIS
    Loading scope MOMT__...
    Incompatible_DB_Version: Cannot load database because of a database version hash missmatch:
      Tool  database version hash: <a version hash which should never happen>
      Scope database version hash: ...

Cleanup:

    >>> apt.db_version_hash = dbv
    >>> apt.delete_database (url)

"""

_real_db_create_cmd = r"""

"""

_real_db_test = r"""
    >>> env = dict (os.environ, GTW_FULL_OBJECT_MODEL = "False")
    >>> cmd = subprocess.Popen \
    ...     ( [ sys.executable, "-c"
    ...       , "from _GTW.__test__.model import *; print; scope = Scaffold.scope (%(p1)s, %(n1)s, create = True)"
    ...       ]
    ...     , stdout = subprocess.PIPE
    ...     , stderr = subprocess.PIPE
    ...     , env    = env
    ...     )
    >>> sout, serr = cmd.communicate ()
    >>> prepr (serr)
    ''
    >>> with expect_except (MOM.Error.Incompatible_DB_Version) :
    ...     scope = Scaffold.scope (%(p1)s, %(n1)s, create = False) # doctest:+ELLIPSIS
    Loading scope MOMT__...
    Incompatible_DB_Version: Cannot load database because of a database version hash missmatch:
      Tool  database version hash: ...
      Scope database version hash: ...

"""

from   _GTW.__test__.model import *
from   _TFL                import Environment
import subprocess
import sys
import os

Scaffold.Backend_Default_Path ["SQL"] = "'test.sqlite'"
Scaffold.Backend_Default_Path ["sq"]  = "'test.sqlite'"

# dict (simple_test = _simple_test)
__test__ = Scaffold.create_test_dict \
    ( dict ( simple_test  = _simple_test
           , real_db_test = _real_db_test
           )
    , ignore = "HPS" ### this test cannot work an the HPS backend
    )
### __END__ GTW.__test__.db_version_hash
