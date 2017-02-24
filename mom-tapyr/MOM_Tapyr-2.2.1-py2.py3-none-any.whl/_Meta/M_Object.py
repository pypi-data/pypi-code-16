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
#    MOM.Meta.M_Object
#
# Purpose
#    Meta class of object-types of MOM meta object model
#
# Revision Dates
#    23-Sep-2009 (CT) Creation (factored from `TOM.Meta.M_Object`)
#    18-Oct-2009 (CT) `_m_new_e_type_dict` redefined (add `Roles`)
#    27-Oct-2009 (CT) s/Scope_Proxy/E_Type_Manager/
#     4-Nov-2009 (CT) s/E_Type_Manager_O/E_Type_Manager.Object/
#    24-Nov-2009 (CT) `link_map` added
#    12-Mar-2010 (CT) `link_map` moved to `M_E_Type_Id`
#     9-Jun-2011 (MG) `epk_split_pat` added
#    18-Jun-2012 (CT) Add `M_E_Type_Object_Reload`
#     1-Aug-2012 (CT) Add `M_E_Type_Object_Destroyed`
#    17-Aug-2012 (CT) Add `role_map`
#     4-Sep-2012 (CT) Move `Roles` and `role_map` to `M_Id_Entity`
#    ««revision-date»»···
#--

from   _MOM        import MOM
from   _TFL        import TFL
from   _TFL.Regexp import *

import _MOM._Meta.M_Entity
import _MOM.E_Type_Manager

import _TFL._Meta.Once_Property
import _TFL.defaultdict

class M_Object (MOM.Meta.M_Id_Entity) :
    """Meta class of MOM.Object."""

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__         (name, bases, dct)
        cls.epk_split_pat = TFL.Regexp (cls.epk_split_characters)
    # end def __init__

# end class M_Object

@TFL.Add_To_Class ("M_E_Type", M_Object)
class M_E_Type_Object (MOM.Meta.M_E_Type_Id) :
    """Meta class for essence of MOM.Object."""

    Manager = MOM.E_Type_Manager.Object

# end class M_E_Type_Object

class M_E_Type_Object_Destroyed (MOM.Meta.M_E_Type_Id_Destroyed, M_E_Type_Object) :
    """Meta class for `_Destroyed` classes of descendents of MOM.Object."""

# end class M_E_Type_Object_Destroyed

class M_E_Type_Object_Reload (MOM.Meta.M_E_Type_Id_Reload, M_E_Type_Object) :
    """Meta class for `_Reload` classes of descendents of MOM.Object."""

# end class M_E_Type_Object_Reload

### «text» ### start of documentation
__doc__ = """

    `MOM.Meta.M_Object` provides the meta machinery for defining
    essential object types and instances. It is based on
    :class:`~_MOM._Meta.M_Entity.M_Entity`.

"""

if __name__ != "__main__" :
    MOM.Meta._Export ("*")
### __END__ MOM.Meta.M_Object
