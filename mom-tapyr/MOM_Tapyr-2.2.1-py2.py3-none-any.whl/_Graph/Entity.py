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
#    MOM.Graph.Entity
#
# Purpose
#    Model MOM entities as displayed in a MOM.Graph
#
# Revision Dates
#    16-Aug-2012 (CT) Creation
#    26-Aug-2012 (CT) Add `add_guides`, improve placing
#    29-Aug-2012 (CT) Add `desc`, `rid`, and `title`
#    30-Aug-2012 (CT) Add and use `skip`
#    31-Aug-2012 (CT) Restructure API, auto-skip inherited roles
#     3-Sep-2012 (CT) Add support for `relation.side`
#     3-Sep-2012 (CT) Revamp placing of relations connectors and guides
#     4-Sep-2012 (CT) Add `Id_Entity`
#     5-Sep-2012 (CT) Add `improve_connectors`, `add_guides` -> `set_guides`
#    25-Sep-2012 (CT) Add `is_partial`
#    22-Oct-2012 (RS) Allocate opposite connector only for `delta` = 0
#    23-Oct-2012 (CT) Change `_offset_map [5]`
#    23-Oct-2012 (CT) Always `len (rels)` to index `_offset_map`
#     9-Nov-2012 (CT) Fix typo in `Dir_Placer.add`
#     6-Dec-2012 (CT) Allow anchor cycle in `Entity.anchor.setter`
#     3-Jun-2013 (CT) Get attribute descriptors from `.attr_prop`
#    14-Sep-2015 (CT) Add `guide_prio`
#    14-Sep-2015 (CT) Change `Entity.pos` to not use `anchor` for root element
#    14-Sep-2015 (CT) Guard against `AttributeError` in `auto_add_roles`
#     8-Oct-2015 (CT) Change `__getattr__` to *not* handle `__XXX__`
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

from   _MOM                   import MOM
from   _TFL                   import TFL

import _MOM.import_MOM
import _MOM._Graph.Relation

from   _TFL._D2               import Cardinal_Direction as CD
from   _TFL.Math_Func         import sign
from   _TFL.multimap          import mm_list
from   _TFL.predicate         import dusplit
from   _TFL.pyk               import pyk
from   _TFL.Regexp            import Regexp, re

import _TFL.Decorator
import _TFL.Sorted_By
import _TFL._Meta.Object
import _TFL._Meta.Once_Property

_word_sep = Regexp("([^A-Za-z0-9])")

class Rel_Placer (TFL.Meta.Object) :
    """Place attachement points of all relations of an Entity."""

    @pyk.adapt__bool__
    @pyk.adapt__str__
    class Dir_Placer (TFL.Meta.Object) :
        """Placer for relations in one cardinal direction"""

        _offset_7       = [0.125, 0.250, 0.375, 0.500, 0.625, 0.750, 0.875]
        _offset_map     = \
            { 1         : [0.500]
            , 2         : [0.250, 0.750]
            , 3         : [0.250, 0.500, 0.750]
            , 4         : [0.125, 0.375, 0.625, 0.875]
            , 5         : [0.250, 0.375, 0.500, 0.625, 0.750]
            , 6         : [0.125, 0.250, 0.375, 0.625, 0.750, 0.875]
            , 7         : _offset_7
            , "default" : _offset_7
            }

        def __init__ (self, rp) :
            self.rp    = rp
            P          = self.predicate
            self.rels  = list \
                ( r for r in rp.entity.all_rels
                if r.side in (self.opposite_name, self.side)
                or (r.side is None and P (r))
                )
            self.slack = self.max_rels - len (self.rels)
        # end def __init__

        @TFL.Meta.Once_Property
        def neighbors (self) :
            placers = self.rp.placers
            return [placers [n] for n in self.neighbor_names]
        # end def neighbors

        @property
        def opposite (self) :
            return self.rp [self.opposite_name]
        # end def opposite

        @property
        def prio (self) :
            return - len (self.rels)
        # end def prio

        @property
        def willing_neighbor (self) :
            result = max (self.neighbors, key = TFL.Getter.slack)
            if result.slack > 0 :
                return result
        # end def willing_neighbor

        def add (self, rel) :
            self.rels.append (rel)
            self.slack -= 1
        # end def add

        def improve_connectors (self) :
            map = mm_list ()
            for r in self.rels :
                if len (r.points) > 3 :
                    p   = r.points [-2]
                    key = \
                        ( sign (getattr (r.delta, self.other_dim))
                        , getattr (p, self.dim)
                        )
                    map [key].append (r)
            for k, rs in pyk.iteritems (map) :
                step = k [0] * self.sort_sign
                if len (rs) > 1 :
                    for i, r in enumerate (rs [1::step]) :
                        r.shift_guide (i + 1)
        # end def improve_connectors

        def is_opposite (self, other) :
            return self.opposite_name == other.name
        # end def is_opposite

        def place_connectors (self) :
            def _opposites (self, rels) :
                for r in rels :
                    o = r.reverse
                    if self.is_opposite (o.connector.side) :
                        yield r, o.connector.side
            rels      = self.rels
            opposites = tuple (_opposites (self, rels))
            rels.sort (key = TFL.Sorted_By \
                ("guide_sort_key", "guide_prio", "type_name"))
            n = len (rels)
            try :
                offset_s = self._offset_map [n]
            except IndexError :
                raise NotImplementedError \
                    ("Too many relations for automatic placement: %s" % (n, ))
            side = self.side
            seen = set ()
            for r, o in opposites :
                other_offset = r.other_connector.offset
                if other_offset is not None :
                    delta = getattr (r.delta, self.other_dim)
                    if not delta :
                        r.connector.offset = o = other_offset
                        seen.add (o)
            def gen_offset (offset_s, seen) :
                for o in offset_s :
                    if o not in seen :
                        seen.add (o)
                        yield o
            offset = gen_offset (offset_s, seen)
            for r in rels :
                if r.connector.offset is None :
                    r.connector.offset = next (offset)
        # end def place_connectors

        def setup_connectors (self) :
            for r in self.rels :
                r.set_connector (MOM.Graph.Relation.Connector (self))
        # end def setup_connectors

        def slacker (self) :
            """Try to improve slack"""
            rels  = self.rels
            slack = self.slack
            while slack < 0 :
                willing = self.willing_neighbor
                if willing :
                    willing.add (rels.pop ())
                    slack += 1
                else :
                    break
            self.slack = slack
            return slack
        # end def slacker

        def __getattr__ (self, name) :
            if name.startswith ("__") and name.endswith ("__") :
                ### Placate inspect.unwrap of Python 3.5,
                ### which accesses `__wrapped__` and eventually throws
                ### `ValueError`
                return getattr (self.__super, name)
            return getattr (self.rp, name)
        # end def __getattr__

        def __bool__ (self) :
            return bool (self.rels)
        # end def __bool__

        def __str__ (self) :
            return self.side
        # end def __str__

    # end class Dir_Placer

    class Dir_Placer_X (Dir_Placer) :

        dim            = "x"
        max_rels       = 3
        other_dim      = "y"

        def guide_offset (self, v) :
            return CD.Point (self.sign * v, 0)
        # end def guide_offset

        def guide_point (self, v) :
            return CD.Point (v, 1)
        # end def guide_point

    # end class Dir_Placer_X

    class Dir_Placer_Y (Dir_Placer) :

        dim            = "y"
        max_rels       = 7
        other_dim      = "x"

        def guide_offset (self, v) :
            return CD.Point (0, self.sign * v)
        # end def guide_offset

        def guide_point (self, v) :
            return CD.Point (1, v)
        # end def guide_point

    # end class Dir_Placer_Y

    class N_Placer (Dir_Placer_Y) :
        """Placer for relations in direction north."""

        name           = "N"
        neighbor_names = ("E", "W")
        opposite_name  = "S"
        side           = "bottom"
        sign           = +1
        sort_sign      = -1
        sort_key_p     = TFL.Sorted_By ("-delta.x")

        def predicate (self, r) :
            return r.delta.y > 0
        # end def predicate

    # end class N_Placer

    class E_Placer (Dir_Placer_X) :
        """Placer for relations in direction east."""

        name           = "E"
        neighbor_names = ("N", "S")
        opposite_name  = "W"
        side           = "left"
        sign           = -1
        sort_sign      = +1
        sort_key_p     = TFL.Sorted_By ("delta.y")

        def predicate (self, r) :
            return r.delta.y == 0 and r.delta.x > 0
        # end def predicate

    # end class E_Placer

    class S_Placer (Dir_Placer_Y) :
        """Placer for relations in direction south."""

        name           = "S"
        neighbor_names = ("E", "W")
        opposite_name  = "N"
        side           = "top"
        sign           = -1
        sort_sign      = -1
        sort_key_p     = TFL.Sorted_By ("-delta.x")

        def predicate (self, r) :
            return r.delta.y < 0
        # end def predicate

    # end class S_Placer

    class W_Placer (Dir_Placer_X) :
        """Placer for relations in direction west."""

        name           = "W"
        neighbor_names = ("N", "S")
        opposite_name  = "E"
        side           = "right"
        sign           = +1
        sort_sign      = +1
        sort_key_p     = TFL.Sorted_By ("delta.y")

        def predicate (self, r) :
            return r.delta.y == 0 and r.delta.x < 0
        # end def predicate

    # end class W_Placer

    def __init__ (self, entity) :
        self.entity  = entity
        self.placers = placers = dict \
            ( (p.name, p) for p in
                ( self.N_Placer (self)
                , self.E_Placer (self)
                , self.S_Placer (self)
                , self.W_Placer (self)
                )
            )
        sort_key = TFL.Sorted_By ("slack", "max_rels", "name")
        by_slack = sorted (pyk.itervalues (placers), key = sort_key)
        for dp in by_slack :
            if dp.slack < 0 :
                dp.slacker ()
        by_slack = sorted ((dp for dp in by_slack if dp), key = sort_key)
        for dp in by_slack :
            dp.setup_connectors ()
    # end def __init__

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        return self.placers [name]
    # end def __getattr__

    def __getitem__ (self, key) :
        return self.placers [key]
    # end def __getitem__

# end class Rel_Placer

@pyk.adapt__bool__
class Entity (TFL.Meta.Object) :

    attr            = None

    _anchor         = None
    _label          = None
    _offset         = None
    _pos            = None
    _sync_cid       = -1

    @property
    def anchor (self) :
        return self._anchor
    # end def anchor

    @anchor.setter
    def anchor (self, value) :
        if value :
            if self._anchor is not None :
                raise TypeError \
                    ( "%s cannot have multiple anchors: %s <-> %s"
                    % (self.type_name, self._anchor, value)
                    )
            if isinstance (value, MOM.Graph.Spec._Spec_Item_) :
                value = value.instantiate (self.graph, self)
            if value.anchor is not self :
                self.graph.cid +=1
                self._anchor = value
    # end def anchor

    @TFL.Meta.Once_Property
    def desc (self) :
        return self.e_type.__doc__
    # end def desc

    @TFL.Meta.Once_Property
    def is_partial (self) :
        return self.e_type.is_partial
    # end def is_partial

    @property
    def label (self) :
        result = self._label
        if result is None :
            result = self._label = self.type_name
        return result
    # end def label

    @TFL.Meta.Once_Property
    def label_parts (self) :
        def _gen (label) :
            parts = _word_sep.split (label)
            yield parts [0]
            it = iter (parts [1:])
            while True :
                try :
                    s = next (it)
                    p = next (it)
                except StopIteration :
                    break
                yield s + p
        label = self.label
        if label.startswith ("_") :
            return (label, )
        else :
            return tuple (_gen (label))
    # end def label_parts

    @property
    def offset (self) :
        result = self._offset
        if result is None :
            anchor = self.anchor
            if anchor is not None :
                pass ### XXX calculate automatic offset
        return result
    # end def offset

    @offset.setter
    def offset (self, value) :
        if value != self._offset :
            self.graph.cid +=1
            self._offset = value
    # end def offset

    @property
    def placers (self) :
        for p in pyk.itervalues (self.placer.placers) :
            if p :
                yield p
    # end def placers

    @property
    def pos (self) :
        result = self._pos
        if result is None or self._sync_cid != self.graph.cid :
            self._sync_cid = self.graph.cid
            anchor = self.anchor
            if anchor is not None and self.index :
                result = CD.Pp    (anchor.pos, self.offset)
            else :
                result = CD.Point (* (self.offset or ()))
            self._pos = result
        return result
    # end def pos

    @property
    def slack (self) :
        return - len (self.all_rels)
    # end def slack

    @TFL.Meta.Once_Property
    def title (self) :
        return self.e_type.type_name
    # end def title

    @TFL.Meta.Once_Property
    def type_name (self) :
        return self.e_type.type_name
    # end def type_name

    def __init__ (self, graph, e_type) :
        self.graph      = graph
        self.e_type     = e_type
        self.index      = len (graph.node_map)
        self.all_rels   = []
        self.rel_map    = {}
        self.placer     = None
        self.skip       = set ()
    # end def __init__

    def __call__ (self, * args, ** kw) :
        self.pop_to_self (kw, "anchor", "offset")
        self.pop_to_self (kw, "label", prefix = "_")
        if kw :
            raise TypeError \
                ("Unknown arguments: %s" % (sorted (pyk.iteritems (kw)), ))
        for a in args :
            self._add (a)
        return self
    # end def __call__

    def add_relation (self, rel, other, R_Type, ** kw) :
        r_name = getattr (rel, "name", rel)
        try :
            result = self.rel_map [r_name]
        except KeyError :
            result = self.rel_map [r_name] = \
                R_Type (self, other, rel, ** kw)
            self.all_rels.append  (result)
            other.all_rels.append (result.reverse)
        return result
    # end def add_relation

    def auto_add_roles (self) :
        graph    = self.graph
        e_type   = self.e_type
        rel_map  = self.rel_map
        skip     = self.skip
        for role in e_type.Roles :
            try :
                ra_tn = role.assoc.type_name
            except AttributeError as exc :
                continue
            if ra_tn in graph :
                assoc = graph [ra_tn]
                if role.name in assoc.rel_map :
                    continue
            r_etn = role.E_Type.type_name
            if (   role.name not in rel_map
               and role      not in skip
               ) :
                is_new = r_etn not in graph
                e      = graph [r_etn]
                if is_new :
                    e.instantiate (graph, anchor = self)
                self.add_relation (role, e, MOM.Graph.Relation.Role)
    # end def auto_add_roles

    def instantiate (self, graph, anchor = None, offset = None) :
        if graph != self.graph :
            raise ValueError ("Non-matching graph")
        kw = {}
        if anchor is not None :
            kw ["anchor"] = anchor
        if offset is not None :
            kw ["offset"] = offset
        return self (** kw)
    # end def instantiate

    def set_guides (self) :
        """Set guide points to relations in `self.rel_map`."""
        for r in pyk.itervalues (self.rel_map) :
            r.set_guides ()
    # end def set_guides

    def setup_links (self) :
        self.placer = Rel_Placer (self)
    # end def setup_links

    def _add (self, et, ** kw) :
        ikw     = dict (kw, anchor = et.anchor or self)
        result  = et.instantiate (self.graph, ** ikw)
        if result is not None :
            e_type = self.e_type
            try :
                rel = e_type.Roles [e_type.role_map [result.type_name]]
            except KeyError :
                pass
            else :
                self.add_relation (rel, result, MOM.Graph.Relation.Role)
    # end def _add

    def __repr__ (self) :
        return "%s @ %s" % (self, self.pos)
    # end def __repr__

    def __str__ (self) :
        result = "<Graph.%-6s %s>" % (self.__class__.__name__, self.type_name)
        return result
    # end def __str__

# end class Entity

@TFL.Add_To_Class ("Graph_Type", MOM.Id_Entity)
class Id_Entity (Entity) :
    """Model display of a MOM.Id_Entity in a MOM graph"""

# end class Id_Entity

@TFL.Add_To_Class ("Graph_Type", MOM.Object)
class Object (Entity) :
    """Model display of a MOM.Object in a MOM graph"""

# end class Object

@TFL.Add_To_Class ("Graph_Type", MOM.Link1)
class Link1 (Entity) :
    """Model display of a MOM.Link1 in a MOM graph"""
# end class Link1

@TFL.Add_To_Class ("Graph_Type", MOM.Link2)
class Link2 (Entity) :
    """Model display of a MOM.Link2 in a MOM graph"""

    @property
    def label (self) :
        result = self._label
        if result is None :
            e_type = self.e_type
            label  = e_type.type_base_name
            l_tbn  = e_type.attr_prop ("left").E_Type.type_base_name
            if label.startswith (l_tbn) :
                label = label [len (l_tbn):]
            r_tbn  = e_type.attr_prop ("right").E_Type.type_base_name
            if label.endswith (r_tbn) :
                label = label [:- len (r_tbn)]
            if label == e_type.type_base_name :
                label = e_type.type_name
            result = self._label = label
        return result
    # end def label

# end class Link2

@TFL.Add_To_Class ("Graph_Type", MOM.Link3)
class Link3 (Entity) :
    """Model display of a MOM.Link3 in a MOM graph"""
# end class Link3

if __name__ != "__main__" :
    MOM.Graph._Export ("*")
### __END__ MOM.Graph.Entity
