# -*- coding: utf-8 -*-
# Copyright (C) 2012-2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.RST.TOP.MOM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.RST.TOP.MOM.Query_Restriction
#
# Purpose
#    Provide query restriction for RESTful TOP.MOM resources
#
# Revision Dates
#    30-Jul-2012 (CT) Creation (factored from GTW.NAV.E_Type.Query_Restriction)
#    11-Oct-2016 (CT) Change `GTW.HTML` to `TFL.HTML`
#    ««revision-date»»···
#--

from   __future__ import absolute_import, division, print_function, unicode_literals

from   _TFL.HTML                        import Styler_Safe

from   _GTW._RST._MOM.Query_Restriction import *
import _GTW._RST._TOP._MOM

from   _TFL.I18N                        import _, _T, _Tn
from   _TFL.pyk                         import pyk

_Ancestor = RST_Query_Restriction

class TOP_Query_Restriction (_Ancestor) :
    """Query restriction for RESTful TOP.MOM resources."""

    _real_name  = "Query_Restriction"

    @TFL.Meta.Class_and_Instance_Method
    def _qop_desc (soc, qop) :
        return TFL.Record \
            ( desc   = _T (qop.desc)
            , label  = Styler_Safe (_T (qop.op_sym))
            )
    # end def _qop_desc

Query_Restriction = TOP_Query_Restriction # end class

class TOP_Query_Restriction_Spec (MOM.Attr.Querier.E_Type) :
    """Query restriction spec for a E_Type-specific page."""

    _real_name = "Query_Restriction_Spec"

    def __init__ (self, E_Type, field_names = None) :
        sel = MOM.Attr.Selector.Name (* field_names) if field_names else None
        self.__super.__init__ (E_Type, sel)
    # end def __init__

    @property
    def As_Json_Cargo (self) :
        result = self.__super.As_Json_Cargo
        op_map = result ["op_map"]
        for k, v in pyk.iteritems (op_map) :
            v ["label"] = Styler_Safe (v ["sym"])
        return result
    # end def As_Json_Cargo

Query_Restriction_Spec = TOP_Query_Restriction_Spec # end class

if __name__ != "__main__" :
    GTW.RST.TOP.MOM._Export ("*")
### __END__ GTW.RST.TOP.MOM.Query_Restriction
