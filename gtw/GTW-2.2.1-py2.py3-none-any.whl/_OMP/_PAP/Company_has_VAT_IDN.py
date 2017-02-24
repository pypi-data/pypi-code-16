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
#    GTW.OMP.PAP.Company_has_VAT_IDN
#
# Purpose
#    Link a company to a VAT identification number
#
# Revision Dates
#    24-Feb-2016 (CT) Creation
#    24-Feb-2016 (CT) Inject attribute `vat_idn` into `Company`, `Company_1P`
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

import _GTW._OMP._PAP.Subject_has_VAT_IDN

from   _TFL.Decorator             import eval_function_body

_Ancestor_Essence = PAP.Subject_has_VAT_IDN

class Company_has_VAT_IDN (_Ancestor_Essence) :
    """Link a company to a VAT identification number"""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        ### Primary attributes

        class left (_Ancestor.left) :
            """Company that has a VAT identification number"""

            role_type          = PAP.Company

        # end class left

        class vin (_Ancestor.vin) :
            """VAT identification number of the company"""

        # end class vin

    # end class _Attributes

# end class Company_has_VAT_IDN

@eval_function_body
def _inject_vat_idn () :
    class vat_idn (A_VAT_IDN) :
        """VAT identification number of Company."""

        kind                = Attr.Query
        query               = Q.vat_idn_link.vin
    # end class vat_idn
    PAP.Company.add_attribute (vat_idn, override = True)

    @GTW._Add_Import_Callback ("_GTW._OMP._PAP.Company_1P")
    def _inject_vat_idn (module) :
        class vat_idn (A_VAT_IDN) :
            """VAT identification number of Company_1P."""

            kind                = Attr.Query
            query               = Q.person.vat_idn
        # end class vat_idn
        ET = getattr (module, "Company_1P")
        ET.add_attribute (vat_idn, override = True)
    # end def _inject_vat_idn
# end def _inject_vat_idn

if __name__ != "__main__" :
    GTW.OMP.PAP._Export ("*")
### __END__ GTW.OMP.PAP.Company_has_VAT_IDN
