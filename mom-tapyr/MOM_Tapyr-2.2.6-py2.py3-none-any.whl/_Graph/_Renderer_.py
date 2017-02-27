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
#    MOM.Graph._Renderer_
#
# Purpose
#    Base class for renderers of MOM.Graphs
#
# Revision Dates
#    19-Aug-2012 (CT) Creation
#    26-Aug-2012 (CT) Add `Link.points`, `_Renderer_.render_link`
#    29-Aug-2012 (CT) Factor `render_link`, `_render_node` to descendants
#     3-Sep-2012 (CT) Factor `points_gen` to `Relation`
#     6-Sep-2012 (CT) Fix `transform`, `min_x`, `min_y`
#    20-Sep-2012 (CT) Call `render_link` in `render`, not in `render_node`
#    25-Sep-2012 (CT) Change `render` to sort by `type_name`
#    25-Sep-2012 (CT) Change `render` to sort links by `rid`
#    26-Sep-2012 (CT) Change `transform` to minimum render coordinates to 0
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

from   _MOM                   import MOM
from   _TFL                   import TFL

import _MOM._Graph.Entity
import _MOM._Graph.Relation

from   _TFL.predicate         import pairwise
from   _TFL.pyk               import pyk
from   _TFL._D2               import D2, Cardinal_Direction as CD
from   _TFL._D2.Screen        import Rect

import _TFL._D2.Affine
import _TFL._D2.Point

import _TFL.Accessor
import _TFL.Decorator
import _TFL._Meta.Object
import _TFL._Meta.Once_Property

class Link (TFL.Meta.Object) :
    """Link representing a MOM.Graph.Relation"""

    def __init__ (self, relation, source, target) :
        self.relation = relation
        self.source   = source
        self.target   = target
        self.points   = tuple (self._points (relation, source, target))
    # end def __init__

    @TFL.Meta.Once_Property
    def max_x (self) :
        return max (p.x for p in self.points)
    # end def max_x

    @TFL.Meta.Once_Property
    def max_y (self) :
        return max (p.y for p in self.points)
    # end def max_y

    @TFL.Meta.Once_Property
    def min_x (self) :
        return min (p.x for p in self.points)
    # end def min_x

    @TFL.Meta.Once_Property
    def min_y (self) :
        return min (p.y for p in self.points)
    # end def min_y

    def _points (self, relation, source, target) :
        return relation.points_gen \
            ( self._ref_point (source, relation.source_connector)
            , self._ref_point (target, relation.target_connector)
            , source.renderer.node_size
            )
    # end def _points

    def _ref_point (self, node, connector) :
        side, offset = connector
        line         = getattr (node.box, side.side)
        result       = line.point (offset)
        return result
    # end def _ref_point

# end class Link

class Node (TFL.Meta.Object) :
    """Node representing a MOM.Graph.Entity"""

    def __init__ (self, entity, renderer) :
        self.entity    = entity
        self.renderer  = renderer
        self.pos = pos = entity.pos.transformed (renderer.transform)
        self.box       = Rect (pos, renderer.node_size)
        self.link_map  = {}
    # end def __init__

    @TFL.Meta.Once_Property
    def max_x (self) :
        link_map = self.link_map
        max_x_links = \
            max (l.max_x for l in pyk.itervalues (link_map)) if link_map else 0
        return max (self.box.bottom_right.x, max_x_links)
    # end def max_x

    @TFL.Meta.Once_Property
    def max_y (self) :
        link_map = self.link_map
        max_y_links = \
            max (l.max_y for l in pyk.itervalues (link_map)) if link_map else 0
        return max (self.box.bottom_right.y, max_y_links)
    # end def max_y

    @TFL.Meta.Once_Property
    def min_x (self) :
        link_map = self.link_map
        min_x_links = min (l.min_x for l in pyk.itervalues (link_map)) \
            if link_map else self.max_x
        return min (self.box.top_left.x, min_x_links)
    # end def min_x

    @TFL.Meta.Once_Property
    def min_y (self) :
        link_map = self.link_map
        min_y_links = min (l.min_y for l in pyk.itervalues (link_map)) \
            if link_map else self.max_y
        return min (self.box.top_left.y, min_y_links)
    # end def min_y

    def setup_links (self) :
        renderer = self.renderer
        entity   = self.entity
        Link     = renderer.Link
        link_map = self.link_map
        node_map = renderer.node_map
        for k, r in sorted (pyk.iteritems (entity.rel_map)) :
            link_map [k] = Link (r, self, node_map [r.target.type_name])
    # end def setup_links

# end class Node

class _Renderer_ (TFL.Meta.Object) :
    """Base class for MOM.Graph renderers."""

    node_size          = D2.Point (90, 20)
    default_grid_scale = D2.Point ( 2,  4)
    _grid_size         = None

    Canvas             = None ### redefine in descendants
    Link               = Link
    Node               = Node

    def __init__ (self, graph, ** kw) :
        self.pop_to_self (kw, "node_size", "default_grid_scale")
        self.pop_to_self (kw, "grid_size", prefix = "_")
        self.graph      = graph
        Node            = self.Node
        g_nodes         = self.graph.nodes ()
        self.nodes = ns = list (Node (e, self) for e in g_nodes)
        self.node_map   = dict ((n.entity.type_name, n) for n in ns)
        graph.setup_links ()
        for n in ns :
            n.setup_links ()
        self.canvas = self.Canvas \
            (self.min_x, self.min_y, self.max_x, self.max_y)
    # end def __init__

    @property
    def grid_size (self) :
        result = self._grid_size
        if result is None :
            result = self._grid_size = self.node_size * self.default_grid_scale
        return result
    # end def grid_size

    @grid_size.setter
    def grid_size (self, value) :
        self._grid_size = value
    # end def grid_size

    @TFL.Meta.Once_Property
    def max_x (self) :
        return int (max (n.max_x for n in self.nodes) + self.grid_size.x // 4)
    # end def max_x

    @TFL.Meta.Once_Property
    def max_x_spec (self) :
        return max (v.pos.x for v in pyk.itervalues (self.graph.node_map))
    # end def max_x_spec

    @TFL.Meta.Once_Property
    def max_y (self) :
        return int (max (n.max_y for n in self.nodes) + self.grid_size.y // 4)
    # end def max_y

    @TFL.Meta.Once_Property
    def max_y_spec (self) :
        return max (v.pos.y for v in pyk.itervalues (self.graph.node_map))
    # end def max_y_spec

    @TFL.Meta.Once_Property
    def min_x (self) :
        result = int (min (n.min_x for n in self.nodes) - self.grid_size.x // 4)
        return max (result, 0)
    # end def min_x

    @TFL.Meta.Once_Property
    def min_x_spec (self) :
        return min (v.pos.x for v in pyk.itervalues (self.graph.node_map))
    # end def min_x_spec

    @TFL.Meta.Once_Property
    def min_y (self) :
        result = int (min (n.min_y for n in self.nodes) - self.grid_size.y // 4)
        return max (result, 0)
    # end def min_y

    @TFL.Meta.Once_Property
    def min_y_spec (self) :
        return min (v.pos.y for v in pyk.itervalues (self.graph.node_map))
    # end def min_y_spec

    @TFL.Meta.Once_Property
    def transform (self) :
        dx     = - self.min_x_spec ### shift minimum to zero
        dy     = - self.max_y_spec ### shift maximum to zero: to be reflected
        gs     = self.grid_size
        result = \
            ( D2.Affine.Trans      (gs.x // 4,  gs.y // 4)
            * D2.Affine.Scale      (gs.x,       gs.y)
            * D2.Affine.Reflection (1,          0)
            * D2.Affine.Trans      (dx,         dy)
            )
        return result
    # end def transform

    def render (self) :
        canvas = self.canvas
        nodes  = sorted (self.nodes, key = TFL.Getter.entity.type_name)
        for n in nodes :
            self.render_node (n, canvas)
        link_sort_key = TFL.Sorted_By ("relation.rid")
        for n in nodes :
            for l in sorted (pyk.itervalues (n.link_map), key = link_sort_key) :
                self.render_link (l, canvas)
    # end def render

    def render_link (self, link, canvas) :
        raise NotImplementedError \
            ("%s needs to implement render_link" % (self.__class__.__name__, ))
    # end def render_link

    def render_node (self, node, canvas) :
        raise NotImplementedError \
            ("%s needs to implement render_node" % (self.__class__.__name__, ))
    # end def render_node

# end class _Renderer_

if __name__ != "__main__" :
    MOM.Graph._Export ("_Renderer_")
### __END__ MOM.Graph._Renderer_
