# -*- coding: utf-8 -*-
# Copyright (C) 2009-2015 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package _MOM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    MOM.Meta.M_Prop_Kind
#
# Purpose
#    Meta class for `Kind` properties of MOM
#
# Revision Dates
#    24-Sep-2009 (CT) Creation (factored from `TOM.Meta.M_Property_Kind`)
#    ««revision-date»»···
#--

from   _TFL                  import TFL
from   _MOM                  import MOM

import _TFL._Meta.M_Class
import _MOM._Meta

class M_Prop_Kind (TFL.Meta.M_Class) :
    """Meta class for `Kind` properties of MOM meta object model."""

    def __init__ (cls, name, bases, dict) :
        kind = dict.get ("kind")
        if kind :
            cls.Table [kind] = cls
        cls.__m_super.__init__ (name, bases, dict)
    # end def __init__

# end class M_Prop_Kind

### «text» ### start of documentation
__doc__ = """
    `MOM.Meta.M_Prop_Kind` provides the meta machinery for defining
    :class:`attribute<_MOM._Attr.Kind.Kind>` and
    :class:`predicate<_MOM._Pred.Kind.Kind>` kinds.

    `M_Prop_Kind` adds the value of the class attribute `kind` to the
    class variable `Table`.

"""

if __name__ != "__main__" :
    MOM.Meta._Export ("*")
### __END__ MOM.Meta.M_Prop_Kind
