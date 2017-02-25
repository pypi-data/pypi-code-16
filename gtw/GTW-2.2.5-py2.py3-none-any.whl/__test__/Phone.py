# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016 Mag. Christian Tanzer All rights reserved
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
#    GTW.__test__.Phone
#
# Purpose
#    Test PAP.Phone semantics
#
# Revision Dates
#     3-Aug-2015 (CT) Creation
#    15-Sep-2015 (CT) Adapt to bug fixes in `E164.Country`
#    27-Apr-2016 (CT) Add test for `sn.polisher`
#    22-May-2016 (CT) Add test for `ndc_length_valid`
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _GTW.__test__.model      import *

_test_code = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> PAP = scope.PAP

    >>> at = PAP.Phone ("43", "1", "234567")

    >>> print (at.ui_display)
    +43-1-23 45 67

    >>> print (at.country)
    Country (43) [Austria]

    >>> print (at.cc_info, at.ndc_info)
    Austria Wien

    >>> print (at.ndc_min_length, at.ndc_max_length, at.sn_min_length, at.sn_max_length)
    1 4 3 12

    >>> atp = PAP.Phone ("+43 1 234 56 78")

    >>> print (atp.ui_display)
    +43-1-234 56 78

    >>> print (atp.country)
    Country (43) [Austria]

    >>> with expect_except (MOM.Error.Invariants) :
    ...     at1 = PAP.Phone ("43", "2287", "1234567890")
    Invariants: Can't set primary attribute Phone.sn to '1234567890'.
        Not a proper phone number for Country (43) [Austria]: 2287-1234567890; subscriber number must have at most 9 digits; got 10 digits instead

    >>> at1 = PAP.Phone ("43", "2287", "123456789")
    >>> print (at1.ui_display)
    +43-2287-123 456 789

    >>> print (at1.cc_info, at1.ndc_info)
    Austria Strasshof an der Nordbahn

    >>> print (at1.ndc_min_length, at1.ndc_max_length, at1.sn_min_length, at1.sn_max_length)
    1 4 3 9

    Test polisher splitting `cc` and `ndc` from raw value passed for `sn`
    >>> _ = at1.set_raw (sn = "+43 664 9876543")
    >>> print (at1.ui_display)
    +43-664-987 65 43

    >>> scope.rollback ()

    >>> dk = PAP.Phone ("45", "", "12345678")

    >>> print (dk.ui_display)
    +45-12 34 56 78

    >>> print (portable_repr ([dk.cc, dk.ndc, dk.sn]))
    ['45', '', '12345678']

    >>> print (dk.country)
    Country (45) [Denmark]

    >>> print (dk.cc_info, dk.ndc_info)
    Denmark None

    >>> with expect_except (MOM.Error.Invariants) :
    ...     PAP.Phone ("45", "", "")
    Invariants: Condition `AC_check_sn_length` : Value for sn must contain at least 3 characters; must not be longer than 14 characters (3 <= length <= 14)
        length = 0 << len (sn)
        sn = None
    >>> scope.rollback ()

    >>> with expect_except (MOM.Error.Invariants) :
    ...     dk = PAP.Phone ("45", "12", "345678")
    Invariants: Can't set primary attribute Phone.ndc to '12'.
        Unknown network destination code 12
    >>> scope.rollback ()

    >>> with expect_except (MOM.Error.Invariants) :
    ...     PAP.Phone ("", "", "123")
    Invariants: Condition `AC_check_cc_length` : Value for cc must contain at least 1 characters; must not be longer than 3 characters (1 <= length <= 3)
        cc = None
        length = 0 << len (cc)

    >>> with expect_except (MOM.Error.Invariants) :
    ...     PAP.Phone ("43", "", "")
    Invariants: Condition `AC_check_sn_length` : Value for sn must contain at least 3 characters; must not be longer than 14 characters (3 <= length <= 14)
        length = 0 << len (sn)
        sn = None

    >>> with expect_except (MOM.Error.Invariants) :
    ...     x = PAP.Phone ("699", "123", "456789")
    Invariants: Can't set primary attribute Phone.cc to '699'.
        Unknown country code 699
      Can't set primary attribute Phone.ndc to '123'.
        Unknown country code 699
      Can't set primary attribute Phone.sn to '456789'.
        Unknown country code 699

    >>> with expect_except (MOM.Error.Invariants) :
    ...     for i in range (3, 14) :
    ...         n = "1234567890123" [:i]
    ...         p = PAP.Phone ("43", "1", n)
    ...         print ("%%-15s : %%s" %% (n, p.FO))
    123             : +43-1-123
    1234            : +43-1-12 34
    12345           : +43-1-12 345
    123456          : +43-1-12 34 56
    1234567         : +43-1-123 45 67
    12345678        : +43-1-123 456 78
    123456789       : +43-1-123 456 789
    1234567890      : +43-1-123 456 7890
    12345678901     : +43-1-1234 567 8901
    123456789012    : +43-1-1234 5678 9012
    Invariants: Can't set primary attribute Phone.sn to '1234567890123'.
        Not a proper phone number for Country (43) [Austria]: 1-1234567890123; subscriber number must have at most 12 digits; got 13 digits instead


    >>> _ = PAP.Phone (sn = "918273", cc = "43", raw = 1)
    >>> with expect_except (MOM.Error.Invariants) :
    ...     scope.commit ()
    Invariants: Condition `ndc_length_valid` : Value for `ndc` must contain at least `ndc_min_length`
    digits, must not be longer than `ndc_max_length` digits. (ndc_min_length <= length <= ndc_max_length)
        length = 0 << len (ndc)
        ndc = None
        ndc_max_length = 4
        ndc_min_length = 1

"""

__test__ = Scaffold.create_test_dict \
    ( dict
        ( test_code           = _test_code
        )
    )

### __END__ GTW.__test__.Phone
