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
#    GTW.RST.TOP.MOM.Renderer
#
# Purpose
#    Define classes rendering E_Type sets and E_Type instances
#
# Revision Dates
#    21-Jan-2015 (CT) Creation
#    27-Jan-2015 (CT) Change `fields` to fall back on `resource.fields_default`
#    27-Jan-2015 (CT) Add `template_module_iter`
#     4-Feb-2015 (CT) Add `index` to `Instance`
#    28-May-2015 (CT) Add `Instance.obj_href`
#     1-Jun-2015 (CT) Add guard for `admin` to `Instance.obj_href`
#    22-Jun-2015 (CT) Add guard for `obj ` type to `Instance.obj_href`
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _GTW                     import GTW
from   _MOM                     import MOM
from   _TFL                     import TFL

from   _MOM.import_MOM          import Q

import _MOM.Entity

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL._Meta.Property      import Alias_Property
from   _TFL.Decorator           import Add_New_Method, getattr_safe
from   _TFL.I18N                import _, _T, _Tn
from   _TFL.predicate           import filtered_join

import _TFL._Meta.Object
import _TFL.Accessor

from   itertools                import chain as iter_chain

class _M_Renderer_ (TFL.Meta.Object.__class__) :
    """Metaclass for renderer classes."""

# end class _M_Renderer_

class _Renderer_ (TFL.Meta.BaM (TFL.Meta.Object, metaclass = _M_Renderer_)) :
    """Base class for renderer classes."""

    css_classes         = ()
    css_id              = None
    template_module     = "ETR_table"

    @Once_Property
    @getattr_safe (default = ())
    def actions (self) :
        def _gen (self) :
            obj         = self.obj
            resource    = self.resource
            for A in self.Actions :
                if A.allowed (resource, obj) :
                    yield A (resource, obj)
        return tuple (_gen (self))
    # end def actions

    @Once_Property
    @getattr_safe
    def css_class (self) :
        cc = self.css_classes
        return filtered_join  (" ", cc) if cc else ""
    # end def css_class

    @Once_Property
    @getattr_safe
    def E_Type (self) :
        return self.resource.E_Type
    # end def E_Type

    @Once_Property
    @getattr_safe (default = ())
    def fields (self) :
        resource = self.resource
        return getattr (resource, "fields", resource.fields_default)
    # end def fields

    def action_title (self, action) :
        result = _T (action.description) % dict \
            ( tn    = self.E_Type.ui_name_T
            , obj   = self.obj.FO if self.obj else ""
            ) if action.description else ""
        return result.strip ()
    # end def action_title

# end class _Renderer_

class E_Type (_Renderer_) :
    """Renderer for a set of instances of a specific E_Type."""

    Actions_I           = ()
    Actions_T           = ()
    obj                 = None
    objects_attr_name   = "objects"

    def __init__ (self, resource) :
        self.resource   = resource
    # end def __init__

    @Once_Property
    @getattr_safe (default = ())
    def Actions (self) :
        return self.Actions_T
    # end def Actions

    @property
    @getattr_safe (default = ())
    def actions_at_top (self) :
        return self.actions if len (self.resource.objects) > 15 else ()
    # end def actions_at_top

    @property
    @getattr_safe (default = ())
    def actions_at_bottom (self) :
        return self.actions
    # end def actions_at_bottom

    @Once_Property
    @getattr_safe
    def need_rel_nav (self) :
        r = self.resource.response
        return any ((r.rel_first, r.rel_next, r.rel_prev, r.rel_last))
    # end def need_rel_nav

    @property
    def objects (self) :
        resource  = self.resource
        Instance  = self.Instance
        r_objects = getattr (resource, self.objects_attr_name)
        try :
            start = resource.query_restriction.offset + 1
        except (AttributeError, TypeError) :
            start = 1
        for i, obj in enumerate (r_objects, start) :
            yield Instance (self, obj, i)
    # end def objects

    @Once_Property
    @getattr_safe (default = ())
    def td_cols (self) :
        def _gen (fields) :
            for f in fields :
                for td in f.td_cols :
                    yield td
        return tuple (_gen (self.fields))
    # end def td_cols

    @Once_Property
    @getattr_safe (default = ())
    def th_cols (self) :
        def _gen (fields) :
            for f in fields :
                for th in f.th_cols :
                    yield th
        return tuple (_gen (self.fields))
    # end def th_cols

    @Once_Property
    @getattr_safe (default = ())
    def th_cols0 (self) :
        def _gen (fields) :
            for f in fields :
                for th in f.th_cols0 :
                    if th is not None :
                        yield th
        return tuple (_gen (self.fields))
    # end def th_cols

    def template_module_iter (self) :
        yield self.template_module
        xs = ([self.Instance], self.fields, self.Actions_I, self.Actions_T)
        for x in iter_chain (xs) :
            tm = getattr (x, "template_module", None)
            if tm :
                yield tm
    # end def template_module_iter

# end class E_Type

@Add_New_Method (E_Type)
class Instance (_Renderer_) :
    """Renderer for one instance of an E_Type."""

    def __init__ (self, etr, obj, index) :
        self.etr        = etr
        self.obj        = obj
        self.index      = index
    # end def __init__

    @Once_Property
    @getattr_safe (default = ())
    def Actions (self) :
        return self.etr.Actions_I
    # end def Actions

    @Once_Property
    @getattr_safe
    def css_id (self) :
        try :
            return "pk-%s" % (self.obj.pid, )
        except AttributeError :
            pass
    # end def css_id

    @Once_Property
    @getattr_safe
    def obj_href (self) :
        admin     = None
        obj       = self.obj
        resource  = self.resource
        if isinstance (obj, MOM.Id_Entity) :
            admin = resource.top.ET_Map [obj.type_name].admin
        if admin is None :
            admin = resource.top.ET_Map [resource.type_name].admin
        if admin is not None :
            return admin.href_instance (obj)
    # end def obj_href

    @Once_Property
    @getattr_safe
    def resource (self) :
        return self.etr.resource
    # end def resource

# end class Instance

if __name__ != "__main__" :
    GTW.RST.TOP.MOM._Export_Module ()
### __END__ GTW.RST.TOP.MOM.Renderer
