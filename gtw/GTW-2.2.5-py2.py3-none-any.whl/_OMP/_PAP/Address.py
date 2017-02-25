# -*- coding: utf-8 -*-
# Copyright (C) 2009-2015 Mag. Christian Tanzer All rights reserved
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
#    GTW.OMP.PAP.Address
#
# Purpose
#    Model a (postal) address
#
# Revision Dates
#    30-Dec-2009 (CT) Creation
#    14-Jan-2010 (CT) `ui_name` added to some attributes
#     4-Feb-2010 (CT) Composite `position` instead of `lat` and `lon`
#    22-Feb-2010 (CT) `ignore_case` set for primary attributes
#    23-Mar-2011 (CT) `region` made `Optional`, not `Primary_Optional`
#     7-Sep-2011 (CT) `completer` specifications for primary attributes added
#    18-Nov-2011 (CT) Import `unicode_literals` from `__future__`
#     8-Aug-2012 (CT) Add `example`
#    12-Sep-2012 (CT) Derive from `Property`
#    11-Oct-2012 (CT) Factor attribute `position` to Link1 `Address_Position`
#    14-May-2014 (CT) Set `country.completer.treshold` to `0`
#    15-May-2014 (CT) Reduce `street.completer.treshold` to `1`
#    26-Sep-2014 (CT) Add `polisher`
#    26-Sep-2014 (CT) Use `Polisher.capitalize_if_not_mixed_case`,
#                     not `.capitalize`
#     3-Aug-2015 (CT) Set `_init_raw_default` to `True`
#    ««revision-date»»···
#--

from   __future__            import unicode_literals

from   _MOM.import_MOM        import *
from   _MOM._Attr.Position    import *

from   _GTW                   import GTW
from   _GTW._OMP._PAP         import PAP
import _GTW._OMP._PAP.Property

_Ancestor_Essence = PAP.Property

class _PAP_Address_ (_Ancestor_Essence) :
    """Model a (postal) address."""

    _real_name             = "Address"

    _init_raw_default      = True

    class _Attributes (_Ancestor_Essence._Attributes) :

        ### Primary attributes

        class street (A_String) :
            """Street (or place) and house number"""

            kind           = Attr.Primary
            example        = "Mystery Lane 42"
            ignore_case    = True
            max_length     = 60
            rank           = 1

            completer      = Attr.Completer_Spec  (1, Attr.Selector.primary)
            polisher       = \
                Attr.Polisher.capitalize_if_not_mixed_case_compress_spaces

        # end class street

        class zip (A_String) :
            """Zip code of address"""

            kind           = Attr.Primary
            example        = "9876"
            ignore_case    = True
            max_length     = 6
            rank           = 2
            ui_name        = "Zip code"

            completer      = Attr.Completer_Spec  \
                (1, Attr.Selector.Primary_Followers ())

        # end class zip

        class city (A_String) :
            """City, town, or village"""

            kind           = Attr.Primary
            example        = "Middletown"
            ignore_case    = True
            max_length     = 30
            rank           = 3

            completer      = Attr.Completer_Spec  \
                (1, Attr.Selector.Primary_Followers ())
            polisher       = \
                Attr.Polisher.capitalize_if_not_mixed_case_compress_spaces

        # end class city

        class country (A_String) :
            "Country"

            kind           = Attr.Primary
            example        = "Land of the Brave"
            ignore_case    = True
            max_length     = 20
            rank           = 4

            completer      = Attr.Completer_Spec  \
                (0, Attr.Selector.Primary_Followers ())
            polisher       = Attr.Polisher.capitalize_compress_spaces

        # end class country

        ### Non-primary attributes

        class region (A_String) :
            """State or province or region"""

            kind           = Attr.Optional
            ignore_case    = True
            max_length     = 20
            rank           = 5
            polisher       = \
                Attr.Polisher.capitalize_if_not_mixed_case_compress_spaces

        # end class region

    # end class _Attributes

    def components (self) :
        result = [self.FO.street, ", ".join ((self.FO.zip, self.FO.city))]
        if self.region :
            result.append (self.FO.region)
        result.append (self.FO.country)
        return result
    # end def components

Address = _PAP_Address_ # end class

if __name__ != "__main__" :
    GTW.OMP.PAP._Export ("*")
### __END__ GTW.OMP.PAP.Address
