# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Dr. Ralf Schlatterbeck All rights reserved
# Reichergasse 131, A-3411 Weidling, Austria. rsc@runtux.com
# #*** <License> ************************************************************#
# This module is part of the package GTW.__test__.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.__test__.Attr_DNS
#
# Purpose
#    Test GTW.OMP.DNS subclasses and links
#
# Revision Dates
#    06-Sep-2012 (RS) Creation
#    23-Sep-2012 (RS) Add `raw = True` to records
#     7-Aug-2013 (CT) Adapt to major surgery of GTW.OMP.NET.Attr_Type
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

_test_code = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> DNS = scope.GTW.OMP.DNS
    >>> print (DNS.Zone.count_strict, DNS.Record.count)
    0 0

    >>> z = DNS.Zone (name = 'example.com')
    >>> dnsa1 = DNS.A_Record \\
    ...     ( left    = z
    ...     , name    = "test.example.com"
    ...     , address = "1.2.3.4"
    ...     , raw     = True
    ...     )
    >>> dnsa1b = DNS.A_Record \\
    ...     ( left    = z
    ...     , name    = "test.example.com"
    ...     , address = "1.2.3.5"
    ...     , raw     = True
    ...     )
    >>> dnsa2 = DNS.A_Record \\
    ...     ( left    = z
    ...     , name    = "test2.example.com"
    ...     , address = "2.3.4.5"
    ...     , raw     = True
    ...     )
    >>> cn1 = DNS.CNAME_Record \\
    ...     ( left    = z
    ...     , name    = "test3.example.com"
    ...     , target  = "test2.example.com"
    ...     , raw     = True
    ...     )
"""

from   _GTW.__test__.model       import *
from   _MOM.import_MOM           import Q
import _GTW._OMP._DNS.import_DNS
import _GTW._OMP._DNS.UI_Spec

__test__ = Scaffold.create_test_dict (_test_code)

### __END__ GTW.__test__.Subjects
