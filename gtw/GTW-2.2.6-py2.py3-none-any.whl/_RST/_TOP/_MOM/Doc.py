# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Mag. Christian Tanzer All rights reserved
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
#    GTW.RST.TOP.MOM.Doc
#
# Purpose
#    Directories and pages for documenting MOM E-types
#
# Revision Dates
#     8-Aug-2012 (CT) Creation
#    10-Aug-2012 (CT) Continue creation
#    25-Sep-2012 (CT) Add support for `graph.svg` to `PNS`
#    25-Sep-2012 (CT) Split `PNS_svg` and `PNS_svg_doc`
#    26-Sep-2012 (CT) Add `App_Type.GET` to handle `?E_Type` queries
#    26-Sep-2012 (CT) Set `hidden` dependent on `is_relevant`
#     9-Oct-2012 (CT) Don't put `__doc__` into `title`; add `PNS_desc`
#    18-Oct-2012 (CT) Redefine `E_Type.map_name` to `doc`
#    20-Oct-2012 (CT) Set `E_Type_Desc._prop_map ["doc"]`
#     3-Dec-2012 (CT) Add guard against unknown E_Type
#    17-Dec-2012 (CT) s/map_name/et_map_name/
#    28-Mar-2013 (CT) Hide associations with more than one role
#    20-Feb-2014 (CT) Set `E_Type.nav_off_canvas` to True
#    14-Apr-2014 (CT) Set `App_Type.pid` to `ET_Doc`
#    24-Sep-2014 (CT) Prefer PNS-alias over PNS-name
#    16-Sep-2015 (CT) Add guard to `PNS_graph` against inherited graph
#    16-Sep-2015 (CT) DRY and simplify `_get_svg`
#    ««revision-date»»···
#--

from   __future__ import absolute_import, division, print_function, unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

import _GTW._RST._MOM.Doc
import _GTW._RST._TOP.Dir
import _GTW._RST._TOP.Page

from   _MOM.import_MOM          import MOM

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL.Decorator           import getattr_safe
from   _TFL.I18N                import _, _T, _Tn
from   _TFL.pyk                 import pyk

from   posixpath                import join as pp_join

import logging

_Ancestor = GTW.RST.TOP.Page

class _RST_TOP_MOM_Doc_E_Type_ (_Ancestor, GTW.RST.MOM.Doc.E_Type) :
    """Page displaying documentation for a specific E_Type."""

    _real_name                 = "E_Type"

    document_class             = "E-Type-Doc"
    et_map_name                = "doc"
    nav_off_canvas             = True
    page_template_name         = "e_type_doc"

    class _RST_TOP_MOM_Doc_E_Type_GET_ (_Ancestor.GET) :

        _real_name             = "GET"

        def _render_context (self, resource, request, response, ** kw) :
            get    = GTW.RST.MOM.Doc.E_Type.GET ()
            cargo  = get._response_body (resource, request, response)
            result = self.__super._render_context \
                ( resource, request, response
                , rst_cargo = cargo
                , ** kw
                )
            result ["resource"] = resource
            return result
        # end def _render_context

    GET = _RST_TOP_MOM_Doc_E_Type_GET_ # end class

    def __init__ (self, ** kw) :
        self.pop_to_self (kw, "ETM", prefix = "_")
        if "name" not in kw :
            kw ["name"] = self.E_Type.type_base_name
        if "short_title" not in kw :
            kw ["short_title"] = self.E_Type.type_base_name
        self.__super.__init__ (** kw)
        if not self.title :
            self.title = self.E_Type.__doc__
    # end def __init__

E_Type = _RST_TOP_MOM_Doc_E_Type_ # end class

_Ancestor = GTW.RST.TOP.Dir

class _RST_TOP_MOM_Doc_PNS_ (GTW.RST.MOM.Doc.Dir_Mixin, _Ancestor) :
    """Directory of pages displaying documentation for E_Types of a specific
       Package Namespace
    """

    _real_name                 = "PNS"

    dir_template_name          = "pns_e_type_doc"
    E_Type                     = E_Type
    nav_off_canvas             = True

    class Grapher (GTW.RST.TOP.Page) :

        class Grapher_GET (GTW.RST.TOP.Page.GET) :

            _real_name             = "GET"
            _renderers             = (GTW.RST.Mime_Type.SVG, )

            def _response_body (self, resource, request, response) :
                return resource.PNS_svg_doc
            # end def _response_body

        GET = Grapher_GET # end class

    # end class Grapher

    def __init__ (self, ** kw) :
        self.pop_to_self      (kw, "PNS", prefix = "_")
        self.__super.__init__ (** kw)
        PNS  = self.PNS
        name = kw.get ("name") or PNS._._bname
        if not self.short_title :
            self.short_title = name
        if not self.title :
            self.title = _T ("Documentation for package namespace %s") % (name,)
    # end def __init__

    @Once_Property
    @getattr_safe
    def PNS (self) :
        result = self._PNS
        if isinstance (result, pyk.string_types) :
            result = self._PNS = self.top.App_Type.PNS_Map [result]
        return result
    # end def PNS

    @Once_Property
    @getattr_safe
    def PNS_desc (self) :
        PNS = self.PNS
        if PNS :
            desc = PNS._desc_
            if desc :
                from _ReST.To_Html import to_html
                try :
                    return to_html (desc, encoding = "utf8")
                except Exception as exc :
                    logging.exception \
                        ("Converting %r to HTML failed with exception" % (r, ))
    # end def PNS_desc

    @Once_Property
    @getattr_safe
    def PNS_graph (self) :
        PNS = self.PNS
        if PNS :
            try :
                result = PNS._Import_Module ("graph")
            except ImportError as exc :
                pass
            else :
                ### Don't return if graph is inherited from parent PNS
                if result.Command.PNS is PNS :
                    return result
    # end def PNS_graph

    @Once_Property
    @getattr_safe
    def PNS_svg (self) :
        return self._get_svg (want_document = False)
    # end def PNS_svg

    @Once_Property
    @getattr_safe
    def PNS_svg_doc (self) :
        return self._get_svg (want_document = True)
    # end def PNS_svg_doc

    @property
    @getattr_safe
    def dir_template (self) :
        if self.PNS_graph :
            return self.__super.dir_template
    # end def dir_template

    dir_template.setter (_Ancestor.dir_template.fset)

    @Once_Property
    @getattr_safe
    def href_svg (self) :
        if self.PNS_svg_doc is not None :
            return pp_join (self.abs_href_dynamic, "graph.svg")
    # end def href_svg

    def _add_index (self, l) :
        self._entries.sort (key = TFL.Getter.short_title)
        self.__super._add_index (0)
    # end def _add_index

    def _gen_entries (self) :
        PNS      = self.PNS
        app_type = self.top.App_Type
        etf      = self.e_type_filter
        for ET in app_type.etypes_by_pns [PNS.__name__] :
            if etf (ET) :
                yield self.E_Type \
                    ( ETM    = str (ET.type_name)
                    , hidden = (not ET.is_relevant) or len (ET.Roles) > 1
                    , parent = self
                    )
    # end def _gen_entries

    def _get_child (self, child, * grandchildren) :
        if child == "graph" and not grandchildren :
            result = self.Grapher (name = child, parent = self)
        else :
            result = self.__super._get_child (child, * grandchildren)
        return result
    # end def _get_child

    def _get_svg (self, want_document) :
        PNS_graph = self.PNS_graph
        if PNS_graph is not None :
            from _MOM._Graph.SVG import Renderer
            graph  = PNS_graph.graph (self.top.App_Type)
            result = graph.render    (Renderer, want_document = want_document)
            return result
    # end def _get_svg

PNS = _RST_TOP_MOM_Doc_PNS_ # end class

_Ancestor = GTW.RST.TOP.Dir

class _RST_TOP_MOM_Doc_App_Type_ (GTW.RST.MOM.Doc.Dir_Mixin, _Ancestor) :
    """Directory of PNS directories of E_Types for a specific App_Type."""

    _real_name                 = "App_Type"

    pid                        = "ET_Doc"
    PNS                        = PNS

    class _RST_TOP_MOM_Doc_App_Type_GET (_Ancestor.GET) :

        _real_name             = "GET"

        def __call__ (self, resource, request, response) :
            req_data = request.req_data
            if "E_Type" in req_data :
                name = req_data ["E_Type"]
                etr  = resource.resource_from_e_type (name)
                if etr is not None :
                    return etr.top._http_response (etr, request, response)
                else :
                    raise resource.top.Status.Not_Found \
                        (_T ("Unknown E_Type '%s'") % (name, ))
            else :
                if resource.dir_template is None :
                    eff = resource._effective_entry
                    if eff is not resource :
                        return eff.top._http_response (eff, request, response)
                else :
                    return self.__super.__call__ (resource, request, response)
        # end def __call__

    GET = _RST_TOP_MOM_Doc_App_Type_GET # end class

    def __init__ (self, ** kw) :
        self.__super.__init__ (** kw)
        self.top.E_Type_Desc._prop_map [E_Type.et_map_name] = self
    # end def __init__

    def resource_from_e_type (self, e_type) :
        if isinstance (e_type, pyk.string_types) :
            e_type = self.App_Type.entity_type (e_type)
        if e_type :
            names  = e_type.type_name.split (".")
            result = self._get_child (* names)
            return result
    # end def resource_from_e_type

    @property
    def _effective (self) :
        return self
    # end def _effective

    def _gen_entries (self) :
        app_type = self.top.App_Type
        for k, pns in sorted (pyk.iteritems (app_type.PNS_Set)) :
            parent = self
            names  = [k]
            if "." in k :
                names  = k.split (".")
                parent = self._get_child (* names [:-1])
            entry = self.PNS (PNS = pns, name = names [-1], parent = parent)
            if entry.entries :
                entry.hidden = all (e.hidden for e in entry.entries)
                if parent is self :
                    yield entry
                else :
                    parent.add_entries (entry)
    # end def _gen_entries

App_Type = _RST_TOP_MOM_Doc_App_Type_ # end class

if __name__ != "__main__" :
    GTW.RST.TOP.MOM._Export_Module ()
### __END__ GTW.RST.TOP.MOM.Doc
