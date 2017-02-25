# -*- coding: utf-8 -*-
# Copyright (C) 2012-2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.RST.MOM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.RST.MOM.Doc
#
# Purpose
#    Provide RESTful resources for the documentation of a MOM object model
#
# Revision Dates
#     7-Aug-2012 (CT) Creation
#     8-Aug-2012 (CT) Continue creation
#    10-Aug-2012 (CT) Continue creation..
#    11-Aug-2012 (CT) Add `cross_references`
#    13-Sep-2012 (CT) Sort `App_Type._gen_entries` by `type_name`
#    26-Sep-2012 (CT) Remove `is_relevant` from `e_type_filter`
#    26-Sep-2012 (CT) Add `is_partial` to `_response_body`
#    18-Oct-2012 (CT) Register `E_Type` in `top.ET_Map` under `.map_name`
#    20-Oct-2012 (CT) Set `E_Type_Desc._prop_map [self.E_Type.map_name]`
#     7-Dec-2012 (CT) Consider `dont_et_map`
#    17-Dec-2012 (CT) s/map_name/et_map_name/
#    28-Mar-2013 (CT) Always include `is_changeable` in `_response_attr`;
#                     display `E_Type.ui_attr`, not `.edit_attr`
#    15-May-2013 (CT) Add `show_in_ui` to `e_type_filter`
#    27-Mar-2014 (CT) Add alias `rest_doc_response_body` to `E_Type.GET`
#    28-Mar-2014 (CT) Add `queryable` attributes to `E_Type.GET._response_body`
#    28-Mar-2014 (CT) Add link-ref-attribute to `cross_references`
#     1-Apr-2014 (CT) Add `max_value` and `min_value` to
#                     `E_Type.GET._response_attr`
#    19-Jul-2016 (CT) Change guard for `attr.E_Type` in `_response_attr`
#    14-Dec-2016 (CT) Add `Choices` to `_response_attr`
#    ««revision-date»»···
#--

from   __future__ import absolute_import, division, print_function, unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

import _GTW._RST.Resource
import _GTW._RST.HTTP_Method
import _GTW._RST.Mime_Type
import _GTW._RST._MOM.Mixin

from   _MOM.import_MOM          import MOM

from   _TFL.Decorator           import getattr_safe
from   _TFL.I18N                import _, _T, _Tn
from   _TFL.pyk                 import pyk
from   _TFL._Meta.Once_Property import Once_Property

import _TFL._Meta.Object
import _TFL.Record

import logging

class _RST_MOM_Doc_Mixin_ (TFL.Meta.Object) :
    """Mixin for MOM documentation resources"""

    _real_name                 = "Mixin"

    @Once_Property
    @getattr_safe
    def change_info (self) :
        return TFL.Record (etag = self.top.App_Type.db_version_hash)
    # end def change_info

    def e_type_filter (self, e_type) :
        return \
            (   issubclass (e_type, MOM.Id_Entity)
            and e_type.show_in_ui
            and not e_type.is_locked ()
            )
    # end def e_type_filter

Mixin = _RST_MOM_Doc_Mixin_ # end class

class _RST_MOM_Doc_Dir_Mixin_ (Mixin) :
    """Mixin for MOM documentation directory resources"""

    _real_name                 = "Dir_Mixin"

    @property
    @getattr_safe
    def entries (self) :
        if not self._entries :
            try :
                self.add_entries (* self._gen_entries ())
            except Exception as exc :
                logging.exception (exc)
        return self._entries
    # end def entries

    def e_type_href (self, e_type) :
        resource = self.resource_from_e_type (e_type)
        if resource is not None :
            return resource.abs_href
    # end def e_type_href

Dir_Mixin = _RST_MOM_Doc_Dir_Mixin_ # end class

_Ancestor = GTW.RST.Leaf

class _RST_MOM_Doc_E_Type_ (Mixin, GTW.RST.MOM.Base_Mixin, _Ancestor) :
    """RESTful node documenting a specific essential type."""

    _real_name                 = "E_Type"
    _ETM                       = None

    dont_et_map                = False
    et_map_name                = "rest_doc"
    page_template_name         = "e_type_doc_bare"

    class _RST_MOM_Doc_E_Type_GET_ (_Ancestor.GET) :

        _real_name             = "GET"
        _renderers             = \
            _Ancestor.GET._renderers + (GTW.RST.Mime_Type.HTML_T, )

        def _add_attr_prop (self, attr, k, result, fct = None) :
            v = getattr (attr, k, None)
            if v :
                if fct is not None :
                    v = fct (v)
                result [k] = v
        # end def _add_attr_prop

        def _add_attr_props (self, attr, ks, result, fct = None) :
            for k in ks :
                self._add_attr_prop (attr, k, result, fct)
        # end def _add_attr_props

        def _response_attr (self, resource, request, response, attr) :
            result = dict \
                ( default_value = attr.raw_default
                , description   = _T (attr.description)
                , is_changeable = attr.is_changeable
                , is_required   = attr.is_required
                , is_settable   = attr.is_settable
                , kind          = _T (attr.kind)
                , name          = attr.name
                , type          = _T (attr.typ)
                )
            self._add_attr_props \
                ( attr
                , ("group", "max_length", "max_value", "min_value", "role_name")
                , result
                )
            self._add_attr_props (attr, ("explanation", "syntax"), result, _T)
            if attr.ui_name_T != attr.name :
                result ["ui_name"] = attr.ui_name_T
            if isinstance (attr.E_Type, MOM.Meta.M_E_Type) :
                result ["type_name"] = tn = attr.E_Type.type_name
                if isinstance (attr.attr, MOM.Attr._A_Composite_) :
                    result ["attributes"] = list \
                        (   self._response_attr (resource, request, response, a)
                        for a in attr.E_Type.ui_attr
                        )
                else :
                    result ["url"] = resource.e_type_href (tn)
            else :
                self._add_attr_props (attr, ("Choices", "example"), result)
            if attr.P_Type :
                result ["p_type"] = attr.P_Type.__name__
            return result
        # end def _response_attr

        def _response_body (self, resource, request, response) :
            E_Type   = resource.E_Type
            attrs    = resource.attributes
            q_attrs  = resource.q_able_attributes
            children = E_Type.children
            parents  = E_Type.parents
            ref_map  = E_Type.Ref_Map
            rel_root = E_Type.relevant_root
            result   = dict \
                ( description = _T (E_Type.__doc__)
                , is_partial  = E_Type.is_partial
                , type_name   = E_Type.type_name
                , ui_name     = _T (E_Type.type_name)
                , url         = resource.abs_href
                )
            if attrs or q_attrs :
                result ["attributes"] = rats = {}
                _response_attr = self._response_attr
                for k, vs in (("editable", attrs), ("queryable", q_attrs)) :
                    if vs :
                        rats [k] = list \
                            (   _response_attr (resource, request, response, a)
                            for a in vs
                            )
            if children :
                v = self._response_children \
                    (resource, request, response, children)
                if v :
                    result ["children"] = v
            if parents :
                v = self._response_parents \
                    (resource, request, response, parents)
                if v :
                    result ["parents"] = v
            if rel_root and rel_root is not E_Type :
                v = self._response_ref_e_type (resource, rel_root)
                if v :
                    result ["relevant_root"] = v
            if ref_map :
                v = list (self._response_ref_map (resource, ref_map))
                if v :
                    result ["cross_references"] = v
            try :
                resource.scope.rollback () ### Remove example objects, if any
            except Exception as exc :
                logging.exception ("Rollback error: %s", exc)
            return result
        # end def _response_body

        rest_doc_response_body = _response_body

        def _response_children (self, resource, request, response, children) :
            return list \
                ( self._response_ref_e_types
                    (resource, pyk.itervalues (children))
                )
        # end def _response_children

        def _response_parents (self, resource, request, response, parents) :
            return list (self._response_ref_e_types (resource, parents))
        # end def _response_parents

        def _response_ref_e_types (self, resource, e_types) :
            for et in sorted (e_types, key = TFL.Getter.type_name) :
                if issubclass (et, MOM.Id_Entity) :
                    ref = self._response_ref_e_type (resource, et)
                    if ref :
                        yield ref
        # end def _response_ref_e_types

        def _response_ref_e_type (self, resource, e_type, ** kw) :
            url = resource.e_type_href (e_type)
            if url :
                lra = resource.E_Type.link_ref_map.get (e_type)
                if lra is not None :
                    kw ["lra"] = lra.name
                return dict \
                    ( type_name = e_type.type_name
                    , url       = url
                    , ** kw
                    )
        # end def _response_ref_e_type

        def _response_ref_map (self, resource, ref_map) :
            for et in sorted (ref_map, key = TFL.Getter.type_name) :
                if et.show_in_ui :
                    eias = ref_map [et]
                    ref = self._response_ref_e_type \
                        (resource, et, attributes = sorted (eias))
                    if ref :
                        yield ref
        # end def _response_ref_map

    GET = _RST_MOM_Doc_E_Type_GET_ # end class

    def __init__ (self, ** kw) :
        self.pop_to_self (kw, "ETM", prefix = "_")
        etn = self.type_name
        if "name" not in kw :
            kw ["name"] = etn.replace (".", "-")
        self.__super.__init__ (** kw)
        if not self.dont_et_map :
            setattr (self.top.ET_Map [self.type_name], self.et_map_name, self)
        if not getattr (self, "short_title", None) :
            self.short_title = _T (etn)
    # end def __init__

E_Type = _RST_MOM_Doc_E_Type_ # end class

_Ancestor = GTW.RST.Dir

class _RST_MOM_Doc_App_Type_ (Dir_Mixin, _Ancestor) :
    """RESTful node documenting the essential types of a specific App_Type."""

    _real_name                 = "App_Type"

    E_Type                     = E_Type

    def __init__ (self, ** kw) :
        self.__super.__init__ (** kw)
        self.top.E_Type_Desc._prop_map [self.E_Type.et_map_name] = self
    # end def __init__

    def resource_from_e_type (self, e_type) :
        if not isinstance (e_type, pyk.string_types) :
            e_type = getattr (e_type, "type_name")
        result = self._entry_map.get (e_type.replace (".", "-"))
        return result
    # end def resource_from_e_type

    def _gen_entries (self) :
        etf = self.e_type_filter
        for et in sorted \
                (self.top.App_Type._T_Extension, key = TFL.Getter.type_name) :
            if etf (et) :
                yield self.E_Type (ETM = str (et.type_name), parent = self)
    # end def _gen_entries

App_Type = _RST_MOM_Doc_App_Type_ # end class

if __name__ != "__main__" :
    GTW.RST.MOM._Export_Module ()
### __END__ GTW.RST.MOM.Doc
