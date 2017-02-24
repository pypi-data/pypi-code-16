# -*- coding: utf-8 -*-
# Copyright (C) 2014-2015 Mag. Christian Tanzer All rights reserved
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
#    GTW.__test__.Attr_polisher
#
# Purpose
#    Test attribute polishers
#
# Revision Dates
#    25-Sep-2014 (CT) Creation
#    26-Sep-2014 (CT) Add `test_address`
#    29-Jul-2015 (CT) Adapt to name change of PAP.Phone attributes
#    31-Jul-2015 (CT) Adapt to changes of PAP.Phone polishers
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _GTW.__test__.model      import *
from   _MOM.import_MOM          import Q

_test_address = """

    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> PAP = scope.PAP

    >>> def test (* args, ** kw) :
    ...    a = PAP.Address (* args, raw = True, ** kw)
    ...    print (a.ui_display)
    ...    a.destroy ()

    >>> test ("An der langen Lacke", "1220", "Wien", "Austria")
    An der langen Lacke, 1220, Wien, Austria

    >>> test ("an der langen lacke", "1220", "wien", "austria")
    An Der Langen Lacke, 1220, Wien, Austria

    >>> test ("AN DER LANGEN LACKE", "1220", "WIEN", "AUSTRIA")
    An Der Langen Lacke, 1220, Wien, Austria

    >>> test ("An der langen Lacke", "1220", "wIEn", "Austria")
    An der langen Lacke, 1220, wIEn, Austria

"""

_test_person = """

    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> PAP = scope.PAP

    >>> p0 = PAP.Person ("tanzer", "christian", raw = True)
    >>> print (p0.ui_display)
    Tanzer Christian

    >>> p0.destroy ()

    >>> p1 = PAP.Person ("Tanzer", "Christian", raw = True)
    >>> print (p1.ui_display)
    Tanzer Christian

    >>> p1.destroy ()

    >>> p2 = PAP.Person ("TANZER", "CHRISTIAN", raw = True)
    >>> print (p2.ui_display)
    Tanzer Christian

    >>> p2.destroy ()

    >>> p3 = PAP.Person ("tanZer", "ChRiStIaN", raw = True)
    >>> print (p3.ui_display)
    tanZer ChRiStIaN

    >>> p3.destroy ()

"""

_test_phone = """
    >>> scope = Scaffold.scope (%(p1)s, %(n1)s) # doctest:+ELLIPSIS
    Creating new scope MOMT__...
    >>> PAP = scope.PAP

    >>> p0  = PAP.Phone (sn = "+43 123 4567890", raw = True)
    >>> print (p0.ui_display)
    +43-1-234 567 890

    >>> p1  = PAP.Phone ("43", "1", "234567", raw = True)

    >>> print (p1.ui_display)
    +43-1-23 45 67

    >>> with expect_except (MOM.Error.Invariants) :
    ...     _   = p1.set_raw (sn = "+44 9 123456")
    Invariants: Can't set primary attribute Phone.sn to '+44 9 123456'.
        Not a proper phone number for Country (44) [United Kingdom of Great Britain and Northern Ireland]: 9-123456; subscriber number must have at least 8 digits; got 6 digits instead

    >>> _   = p1.set_raw (sn = "+44 9 12345678")

    >>> print (p1.ui_display)
    +44-9-123 456 78

"""

__test__ = Scaffold.create_test_dict \
    ( dict
        ( test_address        = _test_address
        , test_person         = _test_person
        , test_phone          = _test_phone
        )
    )

### __END__ GTW.__test__.Attr_polisher
