# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package MOM.Graph.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    MOM.Graph.Spec
#
# Purpose
#    Specification of MOM Graphs
#
# Revision Dates
#    16-Aug-2012 (CT) Creation
#    26-Aug-2012 (CT) Change `setup_links` to use `sorted`
#    29-Aug-2012 (CT) Add and use `_setup_links_p`
#    31-Aug-2012 (CT) Add `Attr`, `IS_A`, `Child`, `Role`, and `Skip`
#     3-Sep-2012 (CT) Factor `_Spec_Rel_`, add `source_side`, `target_side`
#     3-Sep-2012 (CT) Call `add_guides`, `place_connectors` in `setup_links`
#     5-Sep-2012 (CT) Call `improve_connectors`, `add_guides` -> `set_guides`
#     6-Sep-2012 (CT) Add `guide_offset`
#    25-Sep-2012 (CT) Add `desc` and `title` to `Graph`
#     3-Jun-2013 (CT) Get attribute descriptors from `.attr_prop`
#    14-Sep-2015 (CT) Add `guide_prio`
#    14-Sep-2015 (CT) Add `Graph._graph_type`, `Graph._graph_type_map`
#                     + Change `Attr.instantiate` to use `MOM.Id_Entity` as
#                       `E_Type` for entries of `Graph._graph_type_map`
#    16-Sep-2015 (CT) Add `Graph.render`, `.render_to`
#     6-Oct-2015 (CT) Change `_Spec_Item_.__getattr__` to *not* handle `__XXX__`
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

from   _MOM               import MOM
from   _TFL               import TFL
from   _TFL.pyk           import pyk

import _MOM._Graph.Relation

import _TFL._Meta.Object
import _TFL._Meta.Once_Property
import _TFL.Accessor

import itertools

def _Instance (cls) :
    return cls ()
# end def _Instance

@pyk.adapt__str__
class _Spec_Item_ (TFL.Meta.Object) :
    """Base class for specs of entity, attribute, role, is_a"""

    anchor   = None
    r_offset = None

    def __init__ (self, name = None) :
        self._name = name
        self._args = ()
        self._kw   = {}
    # end def __init__

    def instantiate (self, graph, anchor = None, offset = None) :
        result = self._instantiate (graph, anchor = anchor, offset = offset)
        if result and anchor and self.r_offset and not anchor._offset :
            anchor.offset = self.r_offset
        return result
    # end def instantiate

    def __call__ (self, * args, ** kw) :
        if self._args or self._kw  :
            raise TypeError ("Can't call with args/kw twice")
        else :
            self.pop_to_self (kw, "r_offset")
            self._args = args
            self._kw   = kw
        return self
    # end def __call__

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        if self._args or self._kw  :
            raise TypeError \
                ( "Can't dereference %s after setting args/kw of %s"
                % (name, self)
                )
        full_name = ".".join ((self._name, name)) if self._name else name
        return self.__class__ (full_name)
    # end def __getattr__

    def __str__ (self) :
        return "<%s.%s %s %s>" % \
            ( self.__class__.__name__, self._name
            , self._args, sorted (pyk.iteritems (self._kw))
            )
    # end def __str__

# end class _Spec_Item_

class _Spec_Rel_ (_Spec_Item_) :
    """Base class for specs of relations"""

    guide_offset = None
    guide_prio   = 0
    source_side  = None
    target_side  = None

    _attr_names  = MOM.Graph.Relation._Relation_._attr_names

    def __call__ (self, * args, ** kw) :
        self.pop_to_self (kw, * self._attr_names)
        return self.__super.__call__ (* args, ** kw)
    # end def __call__

    @property
    def _rel_kw (self) :
        return dict \
            (  (rn, getattr (self, rn))
            for rn in self._attr_names
            if  getattr (self, rn) is not None
            )
    # end def _rel_kw

# end class _Spec_Rel_

@_Instance
class Attr (_Spec_Rel_) :
    """Specification of an attribute referring to another essential entity."""

    R_Type = MOM.Graph.Relation.Attr

    def _instantiate (self, graph, anchor, offset = None) :
        attr = anchor.e_type.attr_prop (self._name)
        attr_ET = attr.E_Type
        if attr_ET is None :
            if anchor.e_type.type_name in graph._graph_type_map :
                attr_ET = attr.E_Type = graph.app_type ["MOM.Id_Entity"]
        if attr_ET :
            spec = getattr (ET, attr_ET.type_name)
            if self._args or self._kw  :
                spec (* self._args, ** self._kw)
            result = spec._instantiate (graph, anchor = anchor, offset = offset)
            if result is not None :
                anchor.add_relation (attr, result, self.R_Type, ** self._rel_kw)
            return result
        else :
            raise TypeError \
                ("Unknown attr %s for e_type %s" % (self, anchor))
    # end def _instantiate

# end class Attr

@_Instance
class ET (_Spec_Item_) :
    """Specification of an essential entity as part of a Graph."""

    def _instantiate (self, graph, anchor = None, offset = None) :
        e_type = graph [self._name]
        kw     = dict  (self._kw)
        if e_type.anchor is None :
            if anchor is not None :
                kw.setdefault ("anchor", anchor)
            if offset is not None :
                kw.setdefault ("offset", offset)
        result = e_type (* self._args, ** kw)
        return result
    # end def _instantiate

# end class ET

@_Instance
class IS_A (_Spec_Rel_, ET.__class__) :
    """Specification of an inheritance relationship."""

    R_Type = MOM.Graph.Relation.IS_A

    def _instantiate (self, graph, anchor, offset = None) :
        result = self.__super._instantiate \
            (graph, anchor = anchor, offset = offset)
        if result is not None :
            self._add_relation (result, anchor)
        return result
    # end def _instantiate

    def _add_relation (self, parent, child) :
        rel = "IS_A_%s" %  (parent.type_name, )
        child.add_relation (rel, parent, self.R_Type, ** self._rel_kw)
    # end def _add_relation

# end class IS_A

@_Instance
class Child (IS_A.__class__) :
    """Reverse specification of an inheritance relationship."""

    def _add_relation (self, child, parent) :
        self.__super._add_relation (parent, child)
    # end def _add_relation

# end class Child

@_Instance
class Role (Attr.__class__) :
    """Specification of a role attribute referring to another essential entity."""

    R_Type = MOM.Graph.Relation.Role

# end class Role

@_Instance
class Skip (_Spec_Item_) :
    """Specify that a role should be skipped"""

    def _instantiate (self, graph, anchor, offset = None) :
        attr = anchor.e_type.attr_prop (self._name)
        anchor.skip.add (attr)
    # end def _instantiate

# end class Skip

class Graph (TFL.Meta.Object) :
    """Specification of a graph describing (part of) a MOM-based object model."""

    _setup_links_p  = False

    desc            = None
    title           = None

    def __init__ (self, app_type, * entities, ** kw) :
        self.pop_to_self (kw, "desc", "title")
        self.app_type = app_type
        self.cid      = 0
        self.node_map = {}
        self.add (* entities)
    # end def __init__

    @TFL.Meta.Once_Property
    def _graph_type_map (self) :
        ### for MOM.Link1, ..., use `Graph.Id_Entity`, not `Graph.Link1`, ...
        return \
            { "MOM.Link1"    : MOM.Graph.Id_Entity
            , "MOM.Link2"    : MOM.Graph.Id_Entity
            , "MOM.Link3"    : MOM.Graph.Id_Entity
            , "MOM._Link_n_" : MOM.Graph.Id_Entity
            }
    # end def _graph_type_map

    def add (self, * entities) :
        i = len (self.node_map)
        for e_spec in entities :
            e_spec.instantiate (self)
        for e in self.nodes () [i:] :
            e.auto_add_roles ()
    # end def add

    def nodes (self, sort_key = TFL.Getter.index) :
        return sorted (pyk.itervalues (self.node_map), key = sort_key)
    # end def nodes

    def render (self, Renderer, ** kw) :
        """Render this graph via `Renderer` with arguments in `kw`"""
        r = Renderer (self, ** kw)
        return r.render ()
    # end def render

    def render_to (self, file, Renderer, ** kw) :
        print (self.render (Renderer, ** kw), file = file)
    # end def render_to

    def setup_links (self) :
        if not self._setup_links_p :
            sort_key = TFL.Sorted_By ("slack", "type_name")
            nodes    = sorted (pyk.itervalues (self.node_map), key = sort_key)
            for n in nodes :
                n.setup_links ()
            for n in nodes :
                n.set_guides ()
            placers = sorted \
                ( itertools.chain (*  (n.placers for n in nodes))
                , key = TFL.Sorted_By ("prio")
                )
            for p in placers :
                p.place_connectors ()
            for p in placers :
                p.improve_connectors ()
            self._setup_links_p = True
    # end def setup_links

    def _graph_type (self, e_type) :
        result_type = self._graph_type_map.get (e_type.type_name)
        if result_type is None :
            result_type = e_type.Graph_Type
        return result_type (self, e_type)
    # end def _graph_type

    def __contains__ (self, item) :
        return item in self.node_map
    # end def __contains__

    def __getitem__ (self, key) :
        try :
            result = self.node_map [key]
        except KeyError :
            e_type = self.app_type [key]
            result = self.node_map [key] = self._graph_type (e_type)
        return result
    # end def __getitem__

    def __len__ (self) :
        return len (self.node_map)
    # end def __len__

# end class Graph

if __name__ != "__main__" :
    MOM.Graph._Export_Module ()
### __END__ MOM.Graph.Spec
