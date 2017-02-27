# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package MOM.Attr.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    MOM.Attr.A_2D
#
# Purpose
#    Composite attribute type for 2D values (positions, sizes, ...)
#
# Revision Dates
#    22-Mar-2010 (CT) Creation
#    22-Sep-2011 (CT) s/C_Type/P_Type/ for _A_Composite_ attributes
#    18-Nov-2011 (CT) Import `unicode_literals` from `__future__`
#     5-Jun-2013 (CT) Use `is_attr_type`, not home-grown code
#    27-Jun-2013 (CT) Add `_D2_Value_.is_partial`
#    11-Dec-2015 (CT) Use `attr_types_of_module`, not home-grown code
#    ««revision-date»»···
#--

from   __future__            import unicode_literals

from   _MOM.import_MOM       import *
from   _MOM.import_MOM       import _A_Composite_

from   _TFL.I18N             import _, _T, _Tn
from   _TFL.pyk              import pyk

_Ancestor_Essence = MOM.An_Entity

class _D2_Value_ (_Ancestor_Essence) :
    """Base class for two-dimensional values (e.g., position or size)."""

    is_partial    = True

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class x (A_Attr_Type) :
            """Value in x (horizontal) direction."""

            kind               = Attr.Necessary
            rank               = 1
            typ                = "X"

        # end class x

        class y (A_Attr_Type) :
            """Value in y (vertical) direction."""

            kind               = Attr.Necessary
            rank               = 2
            typ                = "Y"

        # end class y

    # end class _Attributes

# end class _D2_Value_

_Ancestor_Essence = _D2_Value_

class D2_Value_Int (_Ancestor_Essence) :
    """Model a two-dimensional integer-based value."""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class x (_Ancestor.x, A_Int) :
            pass
        # end class x


        class y (_Ancestor.y, A_Int) :
            pass
        # end class y

    # end class _Attributes

# end class D2_Value_Int

_Ancestor_Essence = _D2_Value_

class D2_Value_Float (_Ancestor_Essence) :
    """Model a two-dimensional float-based value."""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class x (_Ancestor.x, A_Float) :
            pass
        # end class x


        class y (_Ancestor.y, A_Float) :
            pass
        # end class y

    # end class _Attributes

# end class D2_Value_Float

class A_2D_Int (_A_Composite_) :
    """Models an attribute holding a two-dimensional integer-based value."""

    P_Type           = D2_Value_Int
    typ              = "D2_Value_Int"

# end class A_2D_Int

class A_2D_Float (_A_Composite_) :
    """Models an attribute holding a two-dimensional float-based value."""

    P_Type           = D2_Value_Float
    typ              = "D2_Value_Float"

# end class A_2D_Float

__attr_types      = Attr.attr_types_of_module ()
__sphinx__members = \
    ("_D2_Value_", "D2_Value_Int", "D2_Value_Float") + __attr_types

if __name__ != "__main__" :
    MOM.Attr._Export (*  __attr_types)
### __END__ MOM.Attr.A_2D
