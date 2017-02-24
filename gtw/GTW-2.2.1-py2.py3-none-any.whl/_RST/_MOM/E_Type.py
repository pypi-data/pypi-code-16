# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Mag. Christian Tanzer All rights reserved
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
#    GTW.RST.MOM.E_Type
#
# Purpose
#    Provide RESTful resource for a MOM entity type
#
# Revision Dates
#    22-Jun-2012 (CT) Creation
#     3-Jul-2012 (CT) Factored from _GTW/_RST/MOM.py
#     4-Jul-2012 (CT) Run `entry.pid` through `int`
#                     (mySQL gives `long` which messes up the test output)
#    31-Jul-2012 (CT) Use `dw.writerow`, not `dw.writeheader`: 2.6 compatibility
#    31-Jul-2012 (CT) Add `_E_Type_CSV_.mime_type_parameters`
#     7-Aug-2012 (CT) Change `GTW.RST.MOM.RST_` to `GTW.RST.MOM.`
#     7-Aug-2012 (CT) Add prefix and suffix `_` to class names
#     4-Oct-2012 (CT) Add `href_obj`
#     4-Oct-2012 (CT) Add `request.brief` to `E_Type.GET`
#     5-Oct-2012 (CT) Pass `attributes` to `_new_entry`
#    16-Oct-2012 (CT) Use dotted names for `attribute_names`
#    18-Oct-2012 (CT) Register `E_Type` in `top.ET_Map` under `"rest_api"`
#    27-Nov-2012 (CT) Derive `E_Type.POST` from `GTW.RST.MOM._POST_Mixin_`
#                     not `GTW.RST.MOM._PUT_POST_Mixin_`
#     7-Dec-2012 (CT) Consider `dont_et_map`
#    17-Dec-2012 (CT) Redefine `et_map_name`, remove `__init__`
#     2-Mar-2013 (CT) Redefine `_handle_method` to call `add_doc_link_header`
#    15-Apr-2013 (CT) Protect `_resource_entries` against `result` of `None`
#     8-May-2013 (CT) Remove `.pid`, `.url` from `attribute_names`, unless CSV
#    17-May-2013 (CT) Factor `E_Type.GET._response_body_count`
#    17-May-2013 (CT) Add `_rbl_entry_type_map`
#    20-May-2013 (CT) Fix `_rbl_entry_type_map`
#                     (use E_Type.GTW.rst_mom_rbl_spec, not LET.GTW.rst_...)
#    14-Jun-2013 (CT) Factor `GTW.RST.Mime_Type.CSV.rendered`
#    30-Jan-2014 (CT) Change `E_Type.GET._response_entry` to always restrict
#                     `attributes` for `CSV`
#    27-Mar-2014 (CT) Redefine `E_Type.OPTIONS` to add doc to `_response_body`
#    28-Mar-2014 (CT) Remove partial links from `_rbl_entry_type_map`
#     1-Apr-2014 (CT) Change `E_Type.OPTIONS` to only consider `rest_doc`
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

import _GTW._RST.Resource
import _GTW._RST.HTTP_Method
import _GTW._RST.Mime_Type
import _GTW._RST._MOM.Mixin
import _GTW._RST._MOM.Entity

from   _MOM.import_MOM          import MOM, Q

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL.Decorator           import getattr_safe
from   _TFL.predicate           import dotted_dict

import _TFL._Meta.Object

from   posixpath                import join as pp_join

class _E_Type_CSV_ (GTW.RST.Mime_Type.CSV) :

    _real_name                 = "CSV"
    mime_type_parameters       = ("header=present", )

    def rendered (self, request, response, body) :
        names  = body.get ("attribute_names")
        an     = "attributes_raw" if request.raw else "attributes"
        if names :
            rs = list (dotted_dict (e [an]) for e in body ["entries"])
            return self.__super.rendered \
                (request, response, dict (names = names, rows = rs))
    # end def rendered

# end class _E_Type_CSV_

_Ancestor = GTW.RST.Dir_V

class _RST_MOM_E_Type_ (GTW.RST.MOM.E_Type_Mixin, _Ancestor) :
    """RESTful node for a specific essential type."""

    _real_name                 = "E_Type"

    _ETM                       = None

    Entity                     = GTW.RST.MOM.Entity

    et_map_name                = "rest_api"

    class _RST_MOM_E_Type_GET_ (_Ancestor.GET) :

        _real_name             = "GET"

        _renderers             = _Ancestor.GET._renderers + (_E_Type_CSV_, )

        def _response_body (self, resource, request, response) :
            if request.has_option ("count") :
                responder = self._response_body_count
            else :
                responder = self.__super._response_body
            return responder (resource, request, response)
        # end def _response_body

        def _response_body_count (self, resource, request, response) :
            ETM = resource.ETM
            if request.has_option ("strict") :
                qr = ETM.count_strict
            else :
                qr = ETM.count
            return dict (count = qr)
        # end def _response_body_count

        def _response_dict (self, resource, request, response, ** kw) :
            if request.verbose :
                def _gen (attributes) :
                    render_csv = response.renderer.name == "CSV"
                    for a in attributes :
                        n  = a.name
                        ts = []
                        if a.E_Type :
                            if issubclass (a.E_Type, MOM.Id_Entity) :
                                if render_csv and not request.brief :
                                    ts = ["pid", "url"]
                            else :
                                ts = [u.name for u in a.E_Type.user_attr]
                        if ts :
                            for t in ts :
                                yield ".".join ((n, t))
                        else :
                            yield n
                self.attributes = tuple (a.name for a in resource.attributes)
                kw ["attribute_names"] = tuple (_gen (resource.attributes))
            return self.__super._response_dict \
                (resource, request, response, ** kw)
        # end def _response_dict

        def _response_entry (self, resource, request, response, entry) :
            if request.verbose :
                ### Restrict `attributes` only for identical types
                ### **unless** renderer is CSV
                kw = {}
                render_csv = response.renderer.name == "CSV"
                if entry.type_name == resource.E_Type.type_name or render_csv :
                    kw = dict (attributes = self.attributes)
                e = resource._new_entry (entry, ** kw)
                result = e.GET ()._response_body \
                    (e, request, response, show_rels = None)
            elif request.brief :
                result = int (entry.pid)
            else :
                result = resource.href_obj (entry)
            return result
        # end def _response_entry

        def _resource_entries (self, resource, request, response) :
            result = resource.objects or []
            return sorted (result, key = Q.pid)
        # end def _resource_entries

    GET = _RST_MOM_E_Type_GET_ # end class

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

    class _RST_MOM_E_Type_POST_ (GTW.RST.MOM._POST_Mixin_, GTW.RST.POST) :

        _real_name                 = "POST"

        success_code               = 201

        def _apply_attrs (self, resource, request, response, attrs) :
            return resource.ETM (raw = True, ** attrs)
        # end def _apply_attrs

    POST = _RST_MOM_E_Type_POST_ # end class

    @Once_Property
    @getattr_safe
    def _rbl_entry_type_map (self) :
        import _GTW._RST._MOM.Role_Bound_Links
        E_Type = self.E_Type
        result = {}
        for lra in E_Type.link_ref_attr :
            LET  = lra.E_Type
            name = lra.name
            if LET.show_in_ui and not LET.is_partial :
                rbl_spec = E_Type.GTW.rst_mom_rbl_spec or {}
                result [name] = rbl_spec.get \
                    (name, GTW.RST.MOM.Role_Bound_Links)
        return result
    # end def _rbl_entry_type_map

    def allow_method (self, method, user) :
        if method.name == "POST" and self.ETM.is_partial :
            return False
        return self.__super.allow_method (method, user)
    # end def allow_method

    def href_obj (self, obj) :
        return pp_join (self.abs_href_dynamic, str (obj.pid))
    # end def href_obj

    def _handle_method (self, method, request, response) :
        self.add_doc_link_header (response)
        return self.__super._handle_method (method, request, response)
    # end def _handle_method

E_Type = _RST_MOM_E_Type_ # end class

if __name__ != "__main__" :
    GTW.RST.MOM._Export ("*")
### __END__ GTW.RST.MOM.E_Type
