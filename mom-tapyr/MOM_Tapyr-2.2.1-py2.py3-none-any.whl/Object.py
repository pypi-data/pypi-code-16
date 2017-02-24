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
#    MOM.Object
#
# Purpose
#    Root class for object-types of MOM meta object model
#
# Revision Dates
#    18-Sep-2009 (CT) Creation (factored from TOM.Object)
#    23-Sep-2009 (CT) Journal-related methods removed
#    23-Sep-2009 (CT) `name` replaced by `epk`
#     8-Oct-2009 (CT) s/Entity/Id_Entity/
#    12-Oct-2009 (CT) Methods moved to `Id_Entity`
#    13-Oct-2009 (CT) `Named_Object` added
#    24-Nov-2009 (CT) `all_links` added
#    28-Nov-2009 (CT) `is_partial = True` added to all classes
#     2-Dec-2009 (CT) `all_links` changed to use `ems.role_query`
#     9-Jun-2011 (MG) `epk_*` added
#    29-Mar-2012 (CT) Factor `all_links` to `MOM.Id_Entity`
#    18-Jun-2012 (CT) Add `_Object_Reload_Mixin_`
#     1-Aug-2012 (CT) Add `_Object_Destroyed_Mixin_`
#    17-Jun-2013 (CT) Remove `Named_Object`
#    16-Dec-2015 (CT) Add `_UI_Spec_Defaults`
#    ««revision-date»»···
#--

from   _TFL      import TFL
from   _MOM      import MOM

from   _MOM._Attr.Type import *
from   _MOM._Attr      import Attr
from   _MOM._Pred      import Pred

import  _MOM._Meta.M_Object

import _MOM.Entity

import itertools

class _MOM_Object_ \
          (TFL.Meta.BaM (MOM.Id_Entity, metaclass = MOM.Meta.M_Object)) :
    """Common base class for essential objects of MOM.

       `MOM.Object` provides the framework for defining essential classes.

       It is based on :class:`~_MOM.Entity.Id_Entity`.

    """

    _real_name            = "Object"
    is_partial            = True
    entity_kind           = "object"

    epk_split_characters  = "[;,+-/|\s]"

    _UI_Spec_Defaults     = dict \
        ( show_in_admin   = True
        )

    @classmethod
    def epk_splitter (cls, text) :
        result = []
        for m in cls.epk_split_pat.finditer (text) :
            result.append ((text [:m.start ()], text [m.end ():]))
        result.append  ((text, ))
        result.reverse ()
        return result
    # end def epk_splitter

Object = _MOM_Object_ # end class

@TFL.Add_To_Class ("_Destroyed_Mixin_", Object)
class _Object_Destroyed_Mixin_ \
          ( TFL.Meta.BaM
              ( MOM._Id_Entity_Destroyed_Mixin_
              , metaclass = MOM.Meta.M_E_Type_Object_Destroyed
              )
          ) :
    """Mixin triggering an exception on any attribute access to a
       destroyed object.
    """

# end class _Object_Destroyed_Mixin_

@TFL.Add_To_Class ("_Reload_Mixin_", Object)
class _Object_Reload_Mixin_ \
          ( TFL.Meta.BaM
              ( MOM._Id_Entity_Reload_Mixin_
              , metaclass = MOM.Meta.M_E_Type_Object_Reload
              )
          ) :
    """Mixin triggering a reload from the database on any attribute access."""

# end class _Object_Reload_Mixin_

__doc__ = """


"""

if __name__ != "__main__" :
    MOM._Export ("*")
### __END__ MOM.Object
