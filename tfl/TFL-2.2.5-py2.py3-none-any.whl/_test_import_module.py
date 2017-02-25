# -*- coding: utf-8 -*-
# Copyright (C) 2004-2013 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL._test_import_module
#
# Purpose
#    Test if `import_module` works correctly
#
# Revision Dates
#    17-Jun-2004 (CT) Creation
#    ««revision-date»»···
#--

"""
This module tests _TFL.import_module in two ways. The doctest tests the
normal use of the module and can be triggered by running this module through
/swing/python/run_doctest.py as in

    python /swing/system/python/run_doctest.py \
        lib/python/_TFL/_test_import_module.py -p lib/python/_TFL

The other way tests the use of `import_module` for importing a module while
it is still being imported. This can be tested by importing this module into
a running python interpreter as in

    import _TFL._test_import_module

>>> import_module ("_TFL.import_module").__name__
'_TFL.import_module'
>>> import_module ("os").__name__
'os'
"""

from   __future__  import print_function

from _TFL.import_module import *

print ("Importing ", import_module ("_TFL._test_import_module"), "works")
try :
    import_module_brittle ("_TFL._test_import_module")
except ImportError as exc :
    print \
        ( "Importing _TFL._test_import_module with "
          "import_module_brittle fails as expected: \n    "
        , exc
        )
### __END__ TFL._test_import_module
