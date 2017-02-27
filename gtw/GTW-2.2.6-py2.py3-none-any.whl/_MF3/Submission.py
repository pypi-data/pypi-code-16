# -*- coding: utf-8 -*-
# Copyright (C) 2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.MF3.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.MF3.Submission
#
# Purpose
#    Model submission of MF3 fields and entities
#
# Revision Dates
#    17-Oct-2016 (CT) Creation (factor from MF3.Element)
#    17-Oct-2016 (CT) Change `Field_Entity._init_from_cargo` to set `elem_p`
#                     if edit.pid is None
#                     - either, it was never set
#                     - or, the user cleared the form and put new values in
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

import _GTW._MF3

import _TFL._Meta.Object

class _Base_ (TFL.Meta.Object) :
    """Base class for `Field` and `Entity`."""

    changed = False

    def __init__ (self, elem, scope, cargo, ** kw) :
        if cargo :
            self._init_from_cargo (elem, scope, cargo, ** kw)
        else :
            self.value = elem.undef
    # end def __init__

# end class _Base_

class Entity_Mixin (_Base_) :
    """Submission for a MF3 element derived from `...Element._Entity_Mixin_`"""

    elem_p  = False
    essence = None

    def _init_from_cargo (self, entity, scope, cargo, essence) :
        self.entity   = entity
        self.essence  = essence
        self.value    = None
    # end def _init_from_cargo

    @property
    def changed (self) :
        return self.value is not self.essence
    # end def changed

# end class Entity_Mixin

class Field_Entity (Entity_Mixin) :
    """Submission for a MF3 field entity"""

    def _init_from_cargo (self, entity, scope, cargo, essence) :
        self.__super._init_from_cargo (entity, scope, cargo, essence)
        if entity.readonly :
            ### readonly `essence` cannot be changed in UI, use init value
            pid           = cargo.get ("init", {}).get ("pid")
            self.value    = scope.pid_query (pid)
        else :
            init  = cargo.get ("init", {})
            edit  = cargo.get ("edit", init)
            pid   = edit.get  ("pid") or None
            if pid == -1 :
                ### `essence` was deleted in UI
                self.essence  = entity.undef
            elif pid is not None :
                pid = int (pid)
                if essence is None or pid != essence.pid :
                    ### new `essence` selected in UI
                    self.value    = scope.pid_query (pid)
                else :
                    ### existing `essence` changed in UI
                    ### -> want to get changed value from
                    ###    submissions of entity.elements
                    ### will change linked objects inline
                    ### <- only permitted if `field.ui_allow_change` allows
                    ###    see MF3.Element.Field_Entity._change_from_submission
                    self.elem_p   = True
                    self.value    = essence
            else :
                ### pid was initially None or reset to None in UI
                ### -> want to get value from submissions of entity.elements
                self.elem_p   = True
                self.essence  = None
    # end def _init_from_cargo

    @property
    def changed (self) :
        if self.elem_p :
            return any (f.submission.changed for f in self.entity.elements)
        else :
            return self.__super.changed
    # end def changed

# end class Field_Entity

class Field (_Base_) :
    """Submission for a MF3 field."""

    def _init_from_cargo (self, field, scope, cargo) :
        default      = field.attr.kind.get_raw (None)
        self.init    = init = cargo.get ("init", default)
        self.edit    = edit = cargo.get ("edit", init)
        self.changed = edit != init
        self.value   = edit
    # end def _init_from_cargo

    def __bool__ (self) :
        return bool (self.changed)
    # end def __bool__

# end class Field

class Field_Ref_Hidden (_Base_) :
    """Submission for a MF3 hidden entity field."""

    def __init__ (self, field, scope, cargo) :
        self.field = field
    # end def __init__

    @property
    def changed (self) :
        return self.field.ref.submission.changed
    # end def changed

    @property
    def value (self) :
        return self.field.ref.submission.value
    # end def value

# end class Field_Ref_Hidden

if __name__ != "__main__" :
    GTW.MF3._Export_Module ()
### __END__ GTW.MF3.Submission
