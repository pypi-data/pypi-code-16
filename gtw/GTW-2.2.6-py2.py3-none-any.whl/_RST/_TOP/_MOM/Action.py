# -*- coding: utf-8 -*-
# Copyright (C) 2015 Mag. Christian Tanzer All rights reserved
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
#    GTW.RST.TOP.MOM.Action
#
# Purpose
#    Define classes modelling actions for E_Types and their instances
#
# Revision Dates
#    20-Jan-2015 (CT) Creation
#    28-May-2015 (CT) Add action to `Change`, `Delete`;
#                     remove `css_class`, `href` from `Change`, `Delete`
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _GTW                     import GTW
from   _MOM                     import MOM
from   _TFL                     import TFL

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL.Decorator           import getattr_safe
from   _TFL.I18N                import _, _T, _Tn

import _TFL._Meta.Object

class M_Action (TFL.Meta.Object.__class__) :
    """Metaclass for `_Action_`"""

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        name = cls.__name__ ### allow for `_real_name`
        if not (name.startswith ("_") or getattr (cls, "name", None)) :
            cls.name = name.lower ()
            if cls.css_class is None :
                cls.css_class = cls.name
    # end def __init__

# end class M_Action

class _Action_ (TFL.Meta.BaM (TFL.Meta.Object, metaclass = M_Action)) :
    """Action that can be applied to an E_Type or its instance."""

    ### define in descendent classes
    action          = None
    css_class       = None
    description     = None
    icon            = None
    template_macro  = "action_button"
    text            = ""

    def __init__ (self, resource, obj = None) :
        self.resource = resource
        self.obj      = obj
    # end def __init__

    @classmethod
    def allowed (cls, resource, obj) :
        return resource.allow_child (cls.name, resource.user, obj)
    # end def allowed

    @Once_Property
    @getattr_safe
    def href (self) :
        href_getter = getattr (self.resource, "_".join (("href", self.name)))
        result = href_getter (self.obj)
        return result
    # end def href

    def __bool__ (self) :
        return self.allowed (self.resource, self.obj)
    # end def __bool__

# end class _Action_

class Create (_Action_) :

    description     = _ ("Create a new %(tn)s")
    icon            = "plus-circle"
    template_macro  = "action_button_create"

    @Once_Property
    @getattr_safe
    def href (self) :
        return self.resource.href_create ()
    # end def href

# end class Create

class Change (_Action_) :

    action          = "change"
    css_class       = ""
    description     = _ ("Change %(tn)s %(obj)s")
    href            = None
    icon            = "pencil"

# end class Change

class Delete (_Action_) :

    action          = "remove"
    css_class       = ""
    description     = _ ("Delete %(tn)s %(obj)s")
    href            = None
    icon            = "trash-o"

# end class Delete

class Display (_Action_) :

    description     = _ ("Display details of %(tn)s %(obj)s")
    icon            = "eye"

# end class Display

class Filter (_Action_) :

    description     = _ ("Restrict to objects belonging to %(tn)s %(obj)s")
    icon            = "filter"

# end class Filter

if __name__ != "__main__" :
    GTW.RST.TOP.MOM._Export_Module ()
### __END__ GTW.RST.TOP.MOM.Action
