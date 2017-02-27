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
#    MOM.Meta.M_Attr_Kind
#
# Purpose
#    Meta class for `MOM.Attr.Kind` properties
#
# Revision Dates
#    22-Oct-2009 (CT) Creation
#    ««revision-date»»···
#--
from   _TFL                  import TFL
from   _MOM                  import MOM

import _MOM._Meta.M_Prop_Kind

class M_Attr_Kind (MOM.Meta.M_Prop_Kind) :
    """Meta class for `MOM.Attr.Kind` properties of MOM meta object model."""

    def __init__ (cls, name, bases, dict) :
        cls.__m_super.__init__ (name, bases, dict)
        cls.kind_name = cls.__name__.replace ("Mixin", "").strip ("_")
    # end def __init__

# end class M_Attr_Kind

__doc__ = """


"""

if __name__ != "__main__" :
    MOM.Meta._Export ("*")
### __END__ MOM.Meta.M_Attr_Kind
