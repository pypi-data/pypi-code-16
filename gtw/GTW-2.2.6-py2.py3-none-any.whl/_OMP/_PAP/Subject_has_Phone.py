# -*- coding: utf-8 -*-
# Copyright (C) 2009-2016 Mag. Christian Tanzer All rights reserved
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
#    GTW.OMP.PAP.Subject_has_Phone
#
# Purpose
#    Model the link between a subject and a phone number
#
# Revision Dates
#    30-Dec-2009 (CT) Creation
#     3-Feb-2010 (CT) `_Person_has_Property_` factored
#    19-Feb-2010 (MG) `left.auto_cache` added
#    28-Feb-2010 (CT) `extension` is a `A_Numeric_String` (instead of `A_Int`)
#    18-Nov-2011 (CT) Import `unicode_literals` from `__future__`
#    22-Mar-2012 (CT) Change from `Person_has_Phone` to `Subject_has_Phone`
#    12-Sep-2012 (CT) Add `extension`
#    16-Apr-2013 (CT) Update `auto_derive_np_kw` instead of explicit class
#    15-Aug-2015 (CT) Use `@eval_function_body` for scoped setup code
#    24-Feb-2016 (CT) Remove incorrect `is_partial = True` from `right`
#    ««revision-date»»···
#--

from   __future__             import unicode_literals

from   _MOM.import_MOM        import *

from   _GTW._OMP._PAP.Subject_has_Property   import Subject_has_Property
from   _TFL.Decorator                        import eval_function_body

@eval_function_body
def _setup_Subject_has_Phone_auto_derivation ():
    class extension (A_Numeric_String) :
        """Extension number used in PBX"""

        kind            = Attr.Primary_Optional
        example         = "99"
        max_length      = 5

    # end class extension

    _kw = Subject_has_Property.auto_derive_np_kw ["Subject_has_Phone"]

    _kw ["extra_attributes"].update \
        ( extension = extension
        )

    _kw ["properties"].update \
        ( __doc__ = """Link a %(left.role_name)s to a phone number"""
        )

    _kw ["right"].update \
        ( __doc__    = """Phone number of %(left.role_name)s"""
        )

### __END__ GTW.OMP.PAP.Subject_has_Phone
