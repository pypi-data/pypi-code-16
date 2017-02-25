# -*- coding: utf-8 -*-
# Copyright (C) 2016 Mag. Christian Tanzer All rights reserved
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
#    GTW.OMP.PAP.Subject_has_VAT_IDN
#
# Purpose
#    Link a subject to a VAT identification number
#
# Revision Dates
#    24-Feb-2016 (CT) Creation
#    24-Feb-2016 (CT) Add `left.link_ref_attr_name`
#     1-Jun-2016 (CT) Set `left.refuse_e_types` to "Adhoc_Group", "Company_1P"
#     1-Jun-2016 (CT) Remove `is_partial` from `left`
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _MOM.import_MOM             import *

from   _GTW._OMP._PAP.Attr_Type    import *

from   _GTW                        import GTW
from   _GTW._OMP._PAP              import PAP
from   _TFL.I18N                   import _

from   _GTW._OMP._PAP.VAT_IDN      import A_VAT_IDN

import _GTW._OMP._PAP.Subject

_Ancestor_Essence = PAP.Link1

class Subject_has_VAT_IDN (_Ancestor_Essence) :
    """Link a subject to a VAT identification number"""

    is_partial    = True
    is_relevant   = True

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        ### Primary attributes

        class left (_Ancestor.left) :
            """Subject that has a VAT identification number"""

            role_type          = PAP.Subject
            max_links          = 1
            link_ref_attr_name = "vat_idn_link"
            refuse_e_types     = ("PAP.Adhoc_Group", "PAP.Company_1P")

        # end class left

        class vin (A_VAT_IDN) :
            """VAT identification number of the subject"""

            kind               = Attr.Primary
            ui_name            = _ ("VAT id-no")
            unique_p           = True

        # end class vin

    # end class _Attributes

# end class Subject_has_VAT_IDN

if __name__ != "__main__" :
    GTW.OMP.PAP._Export ("*")
### __END__ GTW.OMP.PAP.Subject_has_VAT_IDN
