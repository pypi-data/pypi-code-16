# -*- coding: utf-8 -*-
# Copyright (C) 2009-2014 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package GTW.OMP.PAP.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.OMP.PAP.Email
#
# Purpose
#    Model an email address
#
# Revision Dates
#    30-Dec-2009 (CT) Creation
#    14-Jan-2010 (CT) `ui_name` added to some attributes
#    22-Feb-2010 (CT) `ignore_case` set for primary attributes
#    26-Feb-2010 (CT) `address` is a `A_Email`, not `A_String`
#     7-Sep-2011 (CT) `address.completer` added
#    18-Nov-2011 (CT) Import `unicode_literals` from `__future__`
#     8-Aug-2012 (CT) Add `example`
#    12-Sep-2012 (CT) Derive from `Property`
#    16-Jan-2014 (CT) Remove explicit definition of `address.ui_name`
#                     (use default `Address`, not `Email address`, for it)
#     8-Sep-2014 (CT) Set `address.ui_name` to `Email address`
#    ««revision-date»»···
#--

from   __future__            import unicode_literals

from   _MOM.import_MOM        import *
from   _GTW                   import GTW
from   _GTW._OMP._PAP         import PAP
from   _TFL.I18N              import _

import _GTW._OMP._PAP.Property

_Ancestor_Essence = PAP.Property

class _PAP_Email_ (_Ancestor_Essence) :
    """Model an email address"""

    _real_name = "Email"

    class _Attributes (_Ancestor_Essence._Attributes) :

        class address (A_Email) :
            """Email address (including domain)"""

            kind           = Attr.Primary
            example        = "john.doe@example.com"
            ignore_case    = True
            max_length     = 80
            rank           = 1
            ui_name        = "Email address"

            completer      = Attr.Completer_Spec  (2, Attr.Selector.primary)

        # end class address

    # end class _Attributes

Email = _PAP_Email_ # end class

if __name__ != "__main__" :
    GTW.OMP.PAP._Export ("*")
### __END__ GTW.OMP.PAP.Email
