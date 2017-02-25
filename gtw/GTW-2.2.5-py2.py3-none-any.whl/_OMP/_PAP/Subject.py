# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Mag. Christian Tanzer All rights reserved
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
#    GTW.OMP.PAP.Subject
#
# Purpose
#    Model a legal subject, i.e., person or company
#
# Revision Dates
#     6-Mar-2012 (CT) Creation
#    19-Mar-2012 (CT) Add `is_partial = True` to `Subject`
#     4-Sep-2014 (CT) Add query attribute `my_group`
#    12-Sep-2014 (CT) Remove `my_group`, `my_person`
#                     [use type restriction in queries, instead]
#    27-Feb-2015 (CT) Add `not_in_future` to `lifetime.start`  and `.finish`
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

from   _MOM.import_MOM             import *
from   _MOM._Attr.Date_Interval    import *

from   _GTW._OMP._PAP.Attr_Type    import *

from   _GTW                        import GTW
from   _GTW._OMP._PAP              import PAP
from   _TFL.I18N                   import _

import _GTW._OMP._PAP.Entity

_Ancestor_Essence = PAP.Object

class _PAP_Subject_ (_Ancestor_Essence) :
    """Model a legal subject, i.e., a person or company."""

    _real_name  = "Subject"

    is_partial  = True

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class lifetime (A_Date_Interval) :
            """Date of birth [`start`] (and death [`finish`])"""

            class _Attributes :
                _Overrides     = dict \
                    ( finish   = dict (not_in_future = True)
                    , start    = dict (not_in_future = True)
                    )
            # end class _Attributes

            kind           = Attr.Optional

        # end class lifetime

    # end class _Attributes

Subject = _PAP_Subject_ # end class

if __name__ != "__main__" :
    GTW.OMP.PAP._Export ("*")
### __END__ GTW.OMP.PAP.Subject
