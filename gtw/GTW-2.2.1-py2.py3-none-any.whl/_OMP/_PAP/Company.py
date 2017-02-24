# -*- coding: utf-8 -*-
# Copyright (C) 2012-2013 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.OMP.PAP.
# 
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.OMP.PAP.Company
#
# Purpose
#    Model a company
#
# Revision Dates
#     6-Mar-2012 (CT) Creation
#    23-Mar-2012 (CT) Change `short_name` from `Primary_Optional` to `Optional`
#     4-Mar-2013 (CT) Factor `PAP.Legal_Entity`
#     6-Mar-2013 (CT) Add attribute `registered_in`
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

from   _MOM.import_MOM             import *

from   _GTW._OMP._PAP.Attr_Type    import *

from   _GTW                        import GTW
from   _GTW._OMP._PAP              import PAP
from   _TFL.I18N                   import _

import _GTW._OMP._PAP.Legal_Entity

_Ancestor_Essence = PAP.Legal_Entity

class _PAP_Company_ (_Ancestor_Essence) :
    """Model a company."""

    _real_name = "Company"

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class name (_Ancestor.name) :

            example            = "John Doe, Inc."

        # end class name

        class registered_in (A_String) :
            """Place where this %(type_base_name.lower ())s is registered."""

            kind               = Attr.Primary_Optional
            max_length         = 64
            ignore_case        = True
            completer          = Attr.Completer_Spec  (1, Attr.Selector.primary)
            example            = "NY"

        # end class registered_in

        class short_name (_Ancestor.short_name) :

            example            = "JDI"

        # end class short_name

    # end class _Attributes

Company = _PAP_Company_ # end class

if __name__ != "__main__" :
    GTW.OMP.PAP._Export ("*")
### __END__ GTW.OMP.PAP.Company
