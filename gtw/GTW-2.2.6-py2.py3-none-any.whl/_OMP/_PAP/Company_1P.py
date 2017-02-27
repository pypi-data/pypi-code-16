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
#    GTW.OMP.PAP.Company_1P
#
# Purpose
#    A one-person company
#
# Revision Dates
#     5-Feb-2016 (CT) Creation
#     9-Feb-2016 (CT) Redefine `ui_display` to DRY result
#    22-Feb-2016 (CT) Remove `unique_p` from `person`
#    26-Apr-2016 (CT) Add `buddies` to `_Name_Polisher_`
#     4-May-2016 (CT) Add `PAP.Subject_has_VAT_IDN` to `refuse_links`
#    10-May-2016 (CT) Add missing `P_Type` to attribute `person`
#     1-Jun-2016 (CT) Remove `refuse_links`
#                     * Better done by `Subject_has_VAT_IDN.left.refuse_e_types`
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

import _GTW._OMP._PAP.Company
import _GTW._OMP._PAP.Person

class _Name_Polisher_ (MOM.Attr.Polisher._Polisher_) :
    """Polisher for `name` attribute of `Company_1P`"""

    buddies      = ("person", )
    polish_empty = True

    def _attr_value (self, attr, name, value, value_dict, essence) :
        result = self.__super._attr_value \
            (attr, name, value, value_dict, essence)
        if result is None and name != attr.name :
            result = getattr (essence, name, "")
        return result or ""
    # end def _attr_value

    def _polished (self, attr, name, value, value_dict, essence, picky) :
        result = {}
        if not value :
            p = self._attr_value (attr, "person", None, value_dict, essence)
            if p and isinstance (p, PAP.Person) :
                result [name] = p.ui_display
        return result
    # end def _polished

# end class _Name_Polisher_

_Ancestor_Essence = PAP.Company

class Company_1P (_Ancestor_Essence) :
    """A one-person company"""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class person (A_Id_Entity) :
            """Person owning the company"""

            kind               = Attr.Primary
            P_Type             = PAP.Person
            ui_allow_new       = True
            ui_rank            = -1

        # end class person

        class name (_Ancestor.name) :

            ### redefine `kind` to `Primary_Optional` to allow `polisher` to
            ### use `person.ui_display` as default
            kind               = Attr.Primary_Optional
            completer          = Attr.Completer_Spec  (1, Attr.Selector.primary)
            polisher           = _Name_Polisher_ ()

        # end class name

    # end class _Attributes

    @property
    def ui_display_format (self) :
        result = ["%(person.ui_display)s"]
        if self.person.ui_display != self.raw_attr ("name") :
            result.append (" %(name)s")
        return "".join (result)
    # end def ui_display_format

# end class Company_1P

if __name__ != "__main__" :
    GTW.OMP.PAP._Export ("*")
### __END__ GTW.OMP.PAP.Company_1P
