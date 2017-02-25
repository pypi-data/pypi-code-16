# -*- coding: utf-8 -*-
# Copyright (C) 2014-2015 Dr. Ralf Schlatterbeck All rights reserved
# Reichergasse 131, A--3411 Weidling, Austria. rsc@runtux.com
# #*** <License> ************************************************************#
# This module is part of the package GTW.OMP.PAP.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.OMP.PAP.Group
#
# Purpose
#    Model a group of persons
#
# Revision Dates
#    13-Jun-2014 (RS) Creation
#     4-Sep-2014 (CT) Add query attribute `my_group`
#    12-Sep-2014 (CT) Remove `my_group`
#                     [use type restriction in queries, instead]
#    26-Sep-2014 (CT) Add `name.polisher`
#    26-Sep-2014 (CT) Use `Polisher.capitalize_if_not_mixed_case`,
#                     not `.capitalize`
#     3-Aug-2015 (CT) Set `_init_raw_default` to `True`
#    ««revision-date»»···
#--

from   __future__ import absolute_import, division, print_function, unicode_literals

from   _MOM.import_MOM             import *
from   _GTW._OMP._PAP.Attr_Type    import *

from   _GTW                        import GTW
from   _GTW._OMP._PAP              import PAP
from   _TFL.I18N                   import _

import _GTW._OMP._PAP.Subject

_Ancestor_Essence = PAP.Subject

class _PAP_Group_ (_Ancestor_Essence) :
    """Model a group of persons."""

    _real_name                 = "Group"

    is_partial                 = True

    _init_raw_default          = True

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class name (A_String) :
            """Name of %(type_base_name.lower ())s."""

            kind               = Attr.Primary
            max_length         = 64
            ignore_case        = True
            completer          = Attr.Completer_Spec  (2, Attr.Selector.primary)
            polisher           = \
                Attr.Polisher.capitalize_if_not_mixed_case_compress_spaces

        # end class name

        class short_name (A_String) :
            """Short name of %(type_base_name.lower ())s."""

            kind               = Attr.Optional
            max_length         = 12
            ignore_case        = True
            completer          = Attr.Completer_Spec  (1, Attr.Selector.primary)

        # end class short_name

    # end class _Attributes

Group = _PAP_Group_ # end class

if __name__ != "__main__" :
    GTW.OMP.PAP._Export ("*")
### __END__ GTW.OMP.PAP.Group
