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
#    GTW.RST.TOP.MOM.Mixin
#
# Purpose
#    Define mixin classes for GTW.RST.TOP.MOM
#
# Revision Dates
#    15-Jul-2012 (CT) Creation
#    18-Jul-2012 (CT) Factor `Entity_Mixin_Base`, `E_Type_Mixin_Base`
#    18-Jul-2012 (CT) Factor from `Display._E_Type_` to `E_Type_Mixin`
#    23-Jul-2012 (CT) Remove `has_children`
#    30-Jul-2012 (CT) Redefine `E_Type_Mixin_Base.QR`
#     7-Aug-2012 (CT) Change `GTW.RST.MOM.RST_` to `GTW.RST.MOM.`
#     7-Aug-2012 (CT) Fix typo (`.admin`, not `._admin`)
#     9-Nov-2012 (CT) Redefine `E_Type_Mixin._get_child_page`
#     7-Dec-2012 (CT) Rename `query_filters` to `query_filters_d`
#    15-Jan-2014 (CT) Factor `E_Type_Mixin._add_other_entries`
#    29-Jan-2014 (CT) Add super-call to `_add_other_entries`
#    13-Feb-2014 (CT) Add `object_entries`
#    14-Mar-2014 (CT) Redefine alias property `proper_entries`
#                     to `object_entries`
#    25-Jun-2014 (CT) Add `_TOP_MOM_Mixin_Base_`
#     2-Feb-2015 (CT) Factor `button_types`, `Renderers`, `_fields` and friends,
#                     `_renderer_template_iter` from `Admin.E_Type`
#    10-Feb-2015 (CT) Factor `Renderer_Mixin`
#    16-Apr-2015 (CT) Pass `default` to `getattr_safe` for `fields_default`
#    27-Apr-2015 (CT) Factor `E_Type_Mixin_Base._default_title`
#     8-Oct-2015 (CT) Change `__getattr__` to *not* handle `__XXX__`
#    12-May-2016 (CT) Change`referral_query` to use `abs_href_dynamic`
#                     - Using `abs_href` breaks queries for
#                       `Referral`/`A_Link` pairs
#    19-Oct-2016 (CT) Change `_field_type` to use attr-type, not attr-kind, as
#                     index into `_field_type_map`
#                     + Copy `_field_type_map` from class to instance
#                       (it is E_Type specific!)
#    ««revision-date»»···
#--

from   __future__ import absolute_import, division, print_function, unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

import _GTW._RST._MOM.Mixin
import _GTW._RST._TOP._MOM.Action
import _GTW._RST._TOP._MOM.Field
import _GTW._RST._TOP._MOM.Query_Restriction
import _GTW._RST._TOP._MOM.Renderer

from   _MOM.import_MOM          import Q

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL._Meta.Property      import Alias_Property
from   _TFL.Decorator           import getattr_safe
from   _TFL.I18N                import _, _T, _Tn
from   _TFL.predicate           import callable, filtered_join
from   _TFL.pyk                 import pyk

import _TFL.Ascii
import _TFL.Attr_Mapper

from   posixpath                import join as pp_join

import logging

class _TOP_MOM_Mixin_Base_ (GTW.RST.MOM.Mixin) :
    """Base mixin for RST.TOP classes displaying MOM instances."""

    Field                         = GTW.RST.TOP.MOM.Field.AQ
    Renderer                      = None

    button_types                  = dict \
        ( ADD                     = "button"
        , APPLY                   = "submit"
        , CANCEL                  = "button"
        , CLEAR                   = "button"
        , CLOSE                   = "button"
        , FIRST                   = "submit"
        , LAST                    = "submit"
        , NEXT                    = "submit"
        , PREV                    = "submit"
        )

    _attrs_to_update_combine      = \
        ("_field_class_map", "_field_pred_map", "_field_type_map")
    _attrs_uniq_to_update_combine = ("_field_type_attr_names", )
    _field_type_attr_names        = ("_gtw_admin_field_type", "_gtw_field_type")
    _field_class_map              = {}
    _field_pred_map               = {}
    _field_type_map               = {}

    def __init__ (self, ** kw) :
        self._field_map      = {}
        self._field_type_map = dict (self.__class__._field_type_map)
        self.__super.__init__ (** kw)
    # end def __init__

    @Once_Property
    def referral_query_unbound (self) :
        sk = TFL.Sorted_By ("perma_name")
        return self.scope.SWP.Referral.query \
            (Q.parent_url ==  Q.BVAR.parent_url, sort_key = sk)
    # end def referral_query_unbound

    @property
    def referral_query (self) :
        return self.referral_query_unbound.bind \
            (parent_url = self.abs_href_dynamic)
    # end def referral_query

    def _add_referral_entries (self) :
        refs = tuple \
            (self._new_referral_entry (ref) for ref in self._get_referrals ())
        if refs :
            self.add_entries (* refs)
    # end def _add_referral_entries

    def _get_referrals (self) :
        q      = self.referral_query
        result = q.all ()
        return result
    # end def _get_referrals

    def _new_referral_entry (self, ref) :
        return GTW.RST.TOP.A_Link \
            ( download    = ref.download_name
            , name        = ref.perma_name
            , parent      = self
            , short_title = ref.short_title
            , target_url  = ref.target_url
            , title       = ref.title
            )
    # end def _new_referral_entry

# end class _TOP_MOM_Mixin_Base_

class Renderer_Mixin (_TOP_MOM_Mixin_Base_) :
    """Mixin for RST.TOP classes that use `GTW.RST.TOP.MOM.Renderer`."""

    ### `Renderer_Mixin` might be used as very specific mixin
    ### --> define class attributes in _TOP_MOM_Mixin_Base_, not here:
    ###     that way, less specific mixins
    ###     * can override `Field` or `Renderer`
    ###     * can add to or override `_field_{class,pred,type}_map`

    @Once_Property
    @getattr_safe (default = ())
    def fields_default (self) :
        return self._fields (self.list_display)
    # end def fields_default

    @Once_Property
    def Renderers (self) :
        Renderer = self.Renderer
        return (Renderer, ) if Renderer is not None else ()
    # end def Renderers

    def add_field_classes (self, field) :
        try :
            super_afc = self.__super.add_field_classes
        except AttributeError :
            result  = ()
        else :
            result  = super_afc (field)
        afc = self._field_class_map.get (field.field_name)
        if afc :
            result += (afc, )
        return result
    # end def add_field_classes

    def template_iter (self) :
        for t in self.__super.template_iter () :
            yield t
        for t in self._renderer_template_iter () :
            yield t
    # end def template_iter

    def _field (self, name, E_Type, map = None) :
        if map is None :
            map = self._field_map
        try :
            result = map [name]
        except KeyError :
            Field  = self._field_type (name, E_Type)
            result = Field (self, name, E_Type)
            afcs   = self.add_field_classes (result)
            if afcs :
                result.css_class_add = filtered_join \
                    (" ", (result.css_class_add, ) + afcs)
            map [name] = map [result.name] = map [result.attr_name] = result
        return result
    # end def _field

    def _field_type (self, name, E_Type) :
        ft_map = self._field_type_map
        result = ft_map.get (name)
        if result is None :
            ak = E_Type.attr_prop (name)
            if ak is not None :
                at     = ak.attr
                result = ft_map.get (at)
                if result is None :
                    result = self._field_type_by_attr  (name, at)
            if result is None and "." in name :
                FT_Coll = GTW.RST.TOP.MOM.Field._Id_Entity_Collection_
                head = name
                while "." in head :
                    head, t = head.rsplit (".", 1)
                    ft      = self._field_type (head, E_Type)
                    if ft is not None and issubclass (ft, FT_Coll) :
                        ### XXX would like to have a special type that properly
                        ###     formats the nested attributes of the
                        ###     _Id_Entity_Collection_
                        ### without that, output is a portable repr of the
                        ### tuple of nested values
                        break
            if result is None :
                result = self.Field
        else :
            result     = self._field_type_callable (name, result)
        ft_map [name]  = result
        return result
    # end def _field_type

    def _field_type_by_attr (self, name, at) :
        for k in self._field_type_attr_names :
            result = self._field_type_callable (k, getattr (at, k, None))
            if result is not None :
                return result
    # end def _field_type_by_attr

    def _field_type_callable (self, name, FT) :
        M_Field = GTW.RST.TOP.MOM.Field.M_Field
        result  = FT
        if callable (result) and not isinstance (result, M_Field) :
            try :
                result = result (self)
            except (TypeError, ValueError, LookupError) :
                logging.exception \
                    ( "Evaluating callable "
                      "field-type-property %s %s failed"
                    % (name, result)
                    )
                result = None
        return result
    # end def _field_type_callable

    def _fields (self, names, E_Type = None) :
        def _gen (self, names, E_Type) :
            if E_Type is None :
                E_Type = self.E_Type
            _f    = self._field
            p_map = self._field_pred_map
            for name in names :
                pred = p_map.get (name)
                if pred is None or (pred (self) if callable (pred) else pred) :
                    f = _f (name, E_Type)
                    yield f
        return tuple (_gen (self, names, E_Type))
    # end def _fields

    @TFL.Contextmanager
    def _handle_method_context (self, method, request, response) :
        with self.__super._handle_method_context (method, request, response) :
            renderer = self.Renderer         (self)
            fields   = self._renderer_fields ()
            with self.LET \
                    ( fields   = fields
                    , renderer = renderer
                    ) :
                yield
    # end def _handle_method_context

    def _renderer_fields (self) :
        return self.fields_default
    # end def _renderer_fields

    def _renderer_template_iter (self) :
        T = self.top.Templateer
        for Renderer in self.Renderers :
            renderer = Renderer (self)
            yield T.get_template \
                ( self.template_name
                , tuple
                    (   T.get_template (r)
                    for r in renderer.template_module_iter ()
                    )
                )
    # end def _renderer_template_iter

# end class Renderer_Mixin

class TOP_MOM_Entity_Mixin_Base \
          (GTW.RST.MOM.Entity_Mixin, _TOP_MOM_Mixin_Base_) :
    """Base mixin for RST.TOP classes displaying MOM instances."""

    _real_name      = "Entity_Mixin_Base"

    attr_mapper     = TFL.Attr_Mapper ()

    _exclude_robots = False

    def __init__ (self, ** kw) :
        obj = kw ["obj"]
        if "name" not in kw :
            name = pyk.text_type (getattr (obj, "perma_name", None))
            if name is None :
                name = getattr (obj, "name", obj.pid)
            kw ["name"] = TFL.Ascii.sanitized_filename (name)
        self.__super.__init__ (** kw)
        ### Get `short_title` and `title` from `obj`
        if "short_title" not in kw :
            self.short_title = self.__getattr__ ("short_title")
        if "title" not in kw :
            self.title       = self.__getattr__ ("title")
    # end def __init__

    @Once_Property
    @getattr_safe
    def FO (self) :
        return GTW.FO (self.obj, self.top.encoding)
    # end def FO

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        if self.attr_mapper :
            try :
                return self.attr_mapper (self.obj.FO, name)
            except AttributeError :
                pass
        return self.__super.__getattr__  (name)
    # end def __getattr__

Entity_Mixin_Base = TOP_MOM_Entity_Mixin_Base # end class

class TOP_MOM_Entity_Mixin (Entity_Mixin_Base) :
    """Mixin for RST.TOP classes displaying MOM instances."""

    _real_name      = "Entity_Mixin"

    def __init__ (self, ** kw) :
        obj = kw ["obj"]
        kw.setdefault ("manager", self.parent)
        kw.setdefault ("hidden",  getattr (obj, "hidden", False))
        self.__super.__init__ (** kw)
    # end def __init__

    @Once_Property
    @getattr_safe
    def E_Type (self) :
        return self.obj.__class__
    # end def E_Type

    @property
    @getattr_safe
    def admin (self) :
        return self.manager.admin
    # end def admin

    @property
    @getattr_safe
    def permalink (self) :
        result = self.manager.href_display (self.obj)
        if not self.top.dynamic_p :
            result = "".join ((result, self.static_page_suffix))
        return result
    # end def permalink

Entity_Mixin = TOP_MOM_Entity_Mixin # end class

class TOP_MOM_E_Type_Mixin_Base \
          (GTW.RST.MOM.E_Type_Mixin, _TOP_MOM_Mixin_Base_) :

    _real_name      = "E_Type_Mixin_Base"

    QR              = GTW.RST.TOP.MOM.Query_Restriction

    attr_mapper     = None
    page_args       = {}

    _exclude_robots = False

    def __init__ (self, ** kw) :
        ### Set `self.top` early because it's needed before initialized properly
        self.top = self.parent.top
        self.pop_to_self (kw, "ETM", prefix = "_")
        E_Type      = self.E_Type
        name        = kw.pop  ("name", E_Type.ui_name)
        a           = "a" ### Fool Babel extract
        short_title = kw.pop  \
            ( "short_title"
            , _T (name.capitalize () if name [0] >= a else name)
            )
        title       = kw.pop ("title", None) \
            or self._default_title (E_Type, name, short_title)
        self.__super.__init__ \
            ( name          = TFL.Ascii.sanitized_filename
                (pyk.text_type (name))
            , short_title   = short_title
            , title         = title
            , ** kw
            )
    # end def __init__

    def _default_title (self, E_Type, name, short_title) :
        return _T (self.E_Type.__doc__)
    # end def _default_title

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        if self.attr_mapper :
            try :
                return self.attr_mapper (self.obj, name)
            except AttributeError :
                pass
        return self.__super.__getattr__  (name)
    # end def __getattr__

E_Type_Mixin_Base = TOP_MOM_E_Type_Mixin_Base # end class

class TOP_MOM_E_Type_Mixin (E_Type_Mixin_Base) :

    _real_name      = "E_Type_Mixin"

    disp_filter     = None
    proper_entries  = Alias_Property ("object_entries")

    _old_objects    = None

    @Once_Property
    @getattr_safe
    def admin (self) :
        return self.top.ET_Map [self.type_name].admin
    # end def admin

    @property
    @getattr_safe
    def entries (self) :
        objects = self.objects
        if self._old_objects is not objects :
            self._entry_map = {}
            self._entries   = []
            entries         = tuple (self._new_entry (o) for o in objects)
            self.add_entries        (* entries)
            self._add_other_entries ()
            if objects :
                self._old_objects = objects
        return self._entries
    # end def entries

    @property
    @getattr_safe
    def object_entries (self) :
        return self.entries [:len (self.objects)]
    # end def object_entries

    @property
    @getattr_safe
    def query_filters_d (self) :
        result = list (self.__super.query_filters_d)
        if self.disp_filter is not None :
            result.append (self.disp_filter)
        return tuple (result)
    # end def query_filters_d

    def href_create (self) :
        admin = self.admin
        if admin :
            return admin.href_create ()
    # end def href_create

    def href_display (self, obj) :
        return pp_join \
            (self.abs_href_dynamic, getattr (obj, "perma_name", str (obj.pid)))
    # end def href_display

    def page_from_obj (self, obj) :
        href   = self.href_display  (obj)
        result = self.top.Table.get (href.strip ("/"))
        if result is None :
            result = self._new_entry (obj)
        return result
    # end def page_from_obj

    def template_iter (self) :
        for t in self.__super.template_iter () :
            yield t
        if self.admin :
            for t in self.admin.template_iter () :
                yield t
    # end def template_iter

    def _add_other_entries (self) :
        admin = self.admin
        if admin and admin is not self :
            self.add_entries (admin)
        self.__super._add_other_entries ()
    # end def _add_other_entries

    def _get_child_page (self, obj) :
        return self.page_from_obj (obj)
    # end def _get_child_page

    def _get_child_query (self, child) :
        try :
            n, result = self.ETM.query_1 \
                (perma_name = child, * self.query_filters)
        except Exception :
            result = None
        if result is None :
            result = self.__super._get_child_query (child)
        return result
    # end def _get_child_query

    def _new_entry (self, instance, ** kw) :
        kw.setdefault ("ETM", instance.ETM)
        return self.__super._new_entry \
            (instance, ** dict (self.page_args, ** kw))
    # end def _new_entry

E_Type_Mixin = TOP_MOM_E_Type_Mixin # end class

if __name__ != "__main__" :
    GTW.RST.TOP.MOM._Export ("*")
### __END__ GTW.RST.TOP.MOM.Mixin
