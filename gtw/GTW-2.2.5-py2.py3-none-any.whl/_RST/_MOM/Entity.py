# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 Mag. Christian Tanzer All rights reserved
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
#    GTW.RST.MOM.Entity
#
# Purpose
#    Provide RESTful resource for a MOM entity instance
#
# Revision Dates
#    22-Jun-2012 (CT) Creation
#     3-Jul-2012 (CT) Factored from _GTW/_RST/MOM.py
#     4-Jul-2012 (CT) Use `pid_query` for `long`, `basestring` pids, too
#     5-Jul-2012 (CT) Add support for `closure`, factor `_response_obj_attrs`
#     6-Jul-2012 (CT) Change `Entity.GET` to use `seen` to show each entity
#                     once only
#    19-Jul-2012 (CT) Factor `RST_Entity_Mixin`
#     7-Aug-2012 (CT) Change `GTW.RST.MOM.RST_` to `GTW.RST.MOM.`
#     7-Aug-2012 (CT) Add prefix and suffix `_` to class names
#     4-Oct-2012 (CT) Change `Entity.GET._response_attr` to use `request.brief`
#     5-Oct-2012 (CT) Pass `url` to nested `Entity.GET._response_obj` calls
#    16-Oct-2012 (CT) Add and use `as_rest_cargo_raw`, use `as_rest_cargo_ckd`
#     9-Jan-2013 (CT) Change `as_rest_cargo_raw`  to use `result.edit_attr`
#    21-Jan-2013 (CT) Check `.allow_method` for
#                     `_A_Id_Entity_.as_rest_cargo_raw`
#     2-Mar-2013 (CT) Redefine `_handle_method` to call `add_doc_link_header`
#     3-May-2013 (CT) Add `META` to REST query arguments
#    17-May-2013 (CT) Redefine `_get_objects` to return `[]`
#    17-May-2013 (CT) Add support for `rels`; derive from `Dir_V`, not `Leaf`
#    17-May-2013 (CT) Take `seen` from `request._rst_seen`
#     3-Jun-2013 (CT) Use `.attr_prop` to access attribute descriptors
#     4-Oct-2013 (CT) Add `fields` and `add_fields` to `_handle_method_context`
#     4-Oct-2013 (CT) Add `add_attributes` to `_response_obj_attrs`
#     4-Oct-2013 (CT) Use `attr_prop` for `add_attributes` in
#                     `_response_obj_attrs`
#    28-Mar-2014 (CT) Add guard for `show_in_ui` and `not is_partial` to
#                     `_entry_type_links`
#     1-Apr-2014 (CT) Redefine `Entity.OPTIONS` to add doc to `_response_body`
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

import _GTW._RST.Resource
import _GTW._RST.HTTP_Method
import _GTW._RST._MOM.Mixin

from   _MOM.import_MOM          import MOM, Q

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL.Decorator           import getattr_safe
from   _TFL.pyk                 import pyk

import _TFL._Meta.Object
import _TFL.Undef

from   posixpath                import join as pp_join

_undef_arg = TFL.Undef ("arg")

@TFL.Add_Method (MOM.Attr._A_Id_Entity_)
def as_rest_cargo_raw \
        (self, obj, method, resource, request, response, seen, getter, a_name) :
    result = self.kind.get_value (obj)
    if result is not None :
        res_vet = resource.resource_from_e_type (result.type_name)
        url     = res_vet.href_obj (result)
        if (   request.has_option ("closure")
           and result.pid not in seen
           and res_vet.allow_method (method, request.user)
           ) :
            result = method._response_obj \
                ( resource, request, response, result, result.edit_attr, seen
                , getter, a_name
                , url       = url
                , show_rels = None
                )
        elif request.brief :
            result = int (result.pid)
        else :
            result = dict (pid = int (result.pid), url = url)
    return result
# end def as_rest_cargo_raw

MOM.Attr._A_Id_Entity_.as_rest_cargo_ckd = as_rest_cargo_raw

_Ancestor = GTW.RST.Dir_V

class _RST_MOM_Entity_ (GTW.RST.MOM.Entity_Mixin, _Ancestor) :
    """RESTful node for a specific instance of an essential type."""

    _real_name                 = "Entity"

    implicit                   = True

    class _RST_MOM_Entity_DELETE_ (GTW.RST.DELETE) :

        _real_name             = "DELETE"

        def _response_body (self, resource, request, response) :
            result = resource.GET ()._response_body \
                (resource, request, response)
            if resource._check_cid (request, response, result) :
                obj = resource.obj
                pid = obj.pid
                obj.destroy ()
                result ["status"] = \
                    ("Object with pid %s successfully deleted" % pid)
            return result
        # end def _response_body

    DELETE = _RST_MOM_Entity_DELETE_ # end class

    class _RST_MOM_Entity_GET_ (_Ancestor.GET) :

        _real_name             = "GET"

        def _response_attr \
                ( self, resource, request, response, obj, attr, seen
                , getter, a_name
                ) :
            value = getter (attr) \
                (obj, self, resource, request, response, seen, getter, a_name)
            return attr.name, value
        # end def _response_attr

        def _response_body \
                (self, resource, request, response, show_rels = _undef_arg) :
            attrs = resource.attributes
            obj   = resource.obj
            seen  = request._rst_seen
            try :
                result = self._response_obj \
                    ( resource, request, response, obj, attrs, seen
                    , url = resource.abs_href, show_rels = show_rels
                    )
            except Exception as exc :
                response.status_code = 400
                result = dict (error = str (exc))
            return result
        # end def _response_body

        def _response_obj \
                ( self, resource, request, response, obj, attrs, seen
                , getter = None, a_name = None, show_rels = _undef_arg
                , ** kw
                ) :
            if isinstance (show_rels, TFL.Undef) :
                show_rels = resource.show_rels
            seen.add (obj.pid)
            result = dict \
                ( cid        = obj.last_cid
                , pid        = obj.pid
                , type_name  = obj.type_name
                , ** kw
                )
            if request.has_option ("META") :
                creation    = dict \
                    (date   = str (obj.creation_date).split (".") [0])
                last_change = dict \
                    (date   = str (obj.last_changed).split (".") [0])
                if obj.created_by :
                    creation ["user"] = obj.created_by
                if obj.last_changed_by :
                    last_change ["user"] = obj.last_changed_by
                result.update \
                    ( creation    = creation
                    , last_change = last_change
                    )
            et_map = resource._entry_type_map
            if et_map :
                if show_rels :
                    result ["rels"] = rmap = {}
                    for rel in show_rels :
                        rbl = resource._get_child (rel)
                        if rbl is None :
                            raise ValueError \
                                ( "Unknown value %r for 'rels'; "
                                  "possible value are: %s"
                                % (rel, ", ".join (sorted (et_map)))
                                )
                        bod = rbl.GET ()._response_body (rbl, request, response)
                        rmap [rbl.abs_href] = bod.get ("entries", [])
                elif show_rels is not None :
                    result ["rels"] = list \
                        (l for l, r in resource._entry_type_links)
            if getter is not None :
                result [a_name] = self._response_obj_attrs \
                    ( resource, request, response, obj, attrs, seen
                    , getter, a_name
                    )
            else :
                G = TFL.Getter
                for k, n, g in \
                        ( ("raw", "attributes_raw", G.as_rest_cargo_raw)
                        , ("ckd", "attributes",     G.as_rest_cargo_ckd)
                        ) :
                    if getattr (request, k) :
                        result [n] = self._response_obj_attrs \
                            ( resource, request, response, obj, attrs, seen
                            , g, n
                            )
            return result
        # end def _response_obj

        def _response_obj_attrs \
                ( self, resource, request, response, obj, attrs, seen
                , getter, a_name
                ) :
            result = dict \
                ( self._response_attr
                    (resource, request, response, obj, a, seen, getter, a_name)
                for a in attrs
                if  a.to_save (obj)
                )
            add_attrs = getattr (resource, "add_attributes", ())
            if add_attrs :
                def _gen (obj, add_attrs) :
                    ET = obj.E_Type
                    for a in add_attrs :
                        yield obj.attr_prop (a.name)
                result.update \
                    ( self._response_attr
                        ( resource, request, response
                        , obj, a, seen, getter, a_name
                        )
                    for a in _gen (obj, add_attrs)
                    )
            return result
        # end def _response_obj_attrs

    GET = _RST_MOM_Entity_GET_ # end class

    class _RST_MOM_E_Type_OPTIONS_ (_Ancestor.OPTIONS) :

        _real_name             = "OPTIONS"

        def _response_body (self, resource, request, response) :
            top    = resource.top
            etd    = top.ET_Map.get (resource.type_name)
            result = {}
            doc    = getattr (etd, "rest_doc", None)
            if doc is not None :
                result = doc.GET ().rest_doc_response_body \
                    (doc, request, response)
            result ["METHODS"] = self.methods
            return result
        # end def _response_body

    OPTIONS = _RST_MOM_E_Type_OPTIONS_ # end class

    class _RST_MOM_Entity_PUT_ (GTW.RST.MOM._PUT_POST_Mixin_, GTW.RST.PUT) :

        _real_name                 = "PUT"

        success_code               = 200

        def _apply_attrs (self, resource, request, response, attrs) :
            obj  = resource.obj
            body = {}
            if resource._check_cid (request, response, body) :
                obj.set_raw (** attrs)
            else :
                self.failure_code = response.status_code
                raise ValueError (body ["error"])
            return obj
        # end def _apply_attrs

    PUT = _RST_MOM_Entity_PUT_ # end class

    def __init__ (self, ** kw) :
        assert "name" not in kw
        self.pop_to_self (kw, "ETM", prefix = "_")
        obj = kw.pop ("obj")
        if isinstance (obj, pyk.int_types + pyk.string_types) :
            obj   = self.scope.pid_query (obj)
        self.obj  = obj
        self.name = str (obj.pid)
        self.pop_to_self (kw, "attributes")
        self.__super.__init__ (** kw)
    # end def __init__

    @Once_Property
    def E_Type (self) :
        return self.obj.__class__
    # end def E_Type

    @Once_Property
    @getattr_safe
    def _default_rels (self) :
        def _gen (et_map) :
            E_Type = self.E_Type
            for k in et_map :
                a = E_Type.attr_prop (k)
                if not a.Ref_Type.is_partial :
                    yield k
        return sorted (_gen (self._entry_type_map))
    # end def _default_rels

    @Once_Property
    @getattr_safe
    def _entry_type_links (self) :
        def _gen (href, ET) :
            for lra in ET.link_ref_attr :
                LET = lra.E_Type
                if LET.show_in_ui and not LET.is_partial :
                    yield \
                        ( pp_join (href, lra.name)
                        , lra.__doc__.replace ("`", "")
                        )
        return tuple (sorted (_gen (self.abs_href, self.E_Type)))
    # end def _entry_type_links

    @Once_Property
    @getattr_safe
    def _entry_type_map (self) :
        return self._rbl_entry_type_map
    # end def _entry_type_map

    def _check_cid (self, request, response, result) :
        cid_c  = request.req_data.get ("cid")
        if cid_c is None :
            cid_c = request.json.get ("cid")
        cid_s  = self.change_info and self.change_info.cid
        error  = None
        if cid_c is None :
            code  = 400 ### Bad request
            error = "You need to send the object's `cid` with the request"
        elif int (cid_c) != cid_s :
            code  = 409 ### Conflict
            error = \
                ( "Cid mismatch: requested cid = %s, current cid = %s"
                % (cid_c, cid_s)
                )
        if error is not None :
            result ["error"] = error
            response.status_code = code
        return not error
    # end def _check_cid

    def _get_objects (self) :
        ### nothing to return here
        return []
    # end def _get_objects

    def _handle_method (self, method, request, response) :
        self.add_doc_link_header (response)
        for link, rel in self._entry_type_links :
            response.add_link (rel, link)
        return self.__super._handle_method (method, request, response)
    # end def _handle_method

    @TFL.Contextmanager
    def _handle_method_context (self, method, request, response) :
        with self.__super._handle_method_context (method, request, response) :
            show_rels = request.has_option ("RELS")
            if show_rels :
                rels = request.req_data_list.get ("RELS")
                if len (rels) == 1 :
                    show_rels = (rels [0],) if rels [0] else self._default_rels
                else :
                    show_rels = sorted (rels)
            kw = dict (show_rels = show_rels)
            if "fields" in request.req_data :
                kw ["attributes"] = request.req_data ["fields"].split (",")
            if "add_fields" in request.req_data :
                kw ["add_attributes"] = self._gen_attr_kinds \
                    (request.req_data ["add_fields"].split (","))
            with self.LET (** kw) :
                yield
    # end def _handle_method_context

Entity = _RST_MOM_Entity_ # end class

if __name__ != "__main__" :
    GTW.RST.MOM._Export ("*")
### __END__ GTW.RST.MOM.Entity
