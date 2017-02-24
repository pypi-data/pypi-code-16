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
#    MOM.Graph.Ascii
#
# Purpose
#    ASCII renderer for MOM graphs
#
# Revision Dates
#    19-Aug-2012 (CT) Creation
#    26-Aug-2012 (CT) Add `Canvas.line`, `Ascii.render_link`
#     5-Sep-2012 (CT) Add `_clean_rendered`
#    26-Sep-2012 (CT) Remove `_clean_rendered` (fix `_Renderer_.transform`)
#    16-Sep-2015 (CT) Add `Renderer.extension`
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

from   _MOM                   import MOM
from   _TFL                   import TFL

import _MOM._Graph._Renderer_
import _MOM._Graph.Entity
import _MOM._Graph.Relation

from   _TFL.predicate         import pairwise
from   _TFL.Regexp            import Regexp, Multi_Re_Replacer, Re_Replacer, re
from   _TFL._D2               import D2, Cardinal_Direction as CD
import _TFL._D2.Point
import _TFL._D2.Rect

import _TFL._Meta.Object
import _TFL._Meta.Once_Property

class Canvas (TFL.Meta.Object) :
    """Canvas for ASCII renderer"""

    _strip_empty = Multi_Re_Replacer \
        ( Re_Replacer ("^( *\n)+", "")
        , Re_Replacer ("(\n *)+$", "")
        )

    def __init__ (self, min_x, min_y, max_x, max_y) :
        self._body = list ([" "] * max_x for i in range (max_y))
    # end def __init__

    def line (self, line, chars = {}) :
        h, t = line
        d    = t - h
        if d.x == 0 :
            return self._line_v (line, chars.get ("y"))
        elif d.y == 0 :
            return self._line_h (line, chars.get ("x"))
        else :
            print ("Slanted line [%s -> %s] not implemented " % (h, t))
    # end def line

    def rectangle (self, rect) :
        self._line_h (rect.top)
        self._line_h (rect.bottom)
        self._line_v (rect.left)
        self._line_v (rect.right)
        for p in rect.corners :
            self [p] = "+"
    # end def rectangle

    def rendered (self) :
        result = "\n".join ("".join (l).rstrip () for l in self._body)
        return self._strip_empty (result)
    # end def rendered

    def text (self, p, v) :
        self [p] = v
    # end def text

    def _line_h (self, line, char = None) :
        if char is None :
            char = "-"
        head, tail = line
        assert head.y == tail.y
        if head.x > tail.x :
            head, tail = tail, head
        l = int (tail.x - head.x)
        self [head] = char * l
    # end def _line_h

    def _line_v (self, line, char = None) :
        if char is None :
            char = "|"
        head, tail = line
        assert head.x == tail.x
        if head.y > tail.y :
            head, tail = tail, head
        x, y = head
        while y <= tail.y :
            self [x, y] = char
            y += 1
    # end def _line_v

    def __setitem__ (self, key, value) :
        if value :
            x, y = tuple (int (k) for k in key)
            l    = len (value)
            line = self._body [y]
            line [x : x+l] = list (value)
    # end def __setitem__

# end class Canvas

class Renderer (MOM.Graph._Renderer_) :
    """ASCII renderer for MOM.Graph"""

    Canvas             = Canvas
    default_grid_scale = D2.Point ( 2,  3)
    extension          = "txt"
    node_size          = D2.Point (16,  4) ### in characters

    conn_chars         = dict \
        ( bottom       = "v"
        , left         = "<"
        , right        = ">"
        , top          = "^"
        )
    link_chars         = dict \
        ( Attr         = dict (x = "_", y = ":")
        , IS_A         = dict (x = ".", y = ".")
        , Role         = dict (x = "-", y = "|")
        )
    rect_chars         = dict \
        ( bottom       = "-"
        , left         = "|"
        , right        = "|"
        , top          = "-"
        )

    def render (self) :
        self.__super.render ()
        return self.canvas.rendered ()
    # end def render

    def render_link (self, link, canvas) :
        chars = self.link_chars [link.relation.kind]
        head  = link.points [ 0]
        tail  = link.points [-1]
        side  = link.relation.source_connector [0].side
        for line in pairwise (link.points) :
            canvas.line (line, chars = chars)
        for p in link.points [1:-1] :
            canvas.text (p, "+")
        canvas.text (head, self.conn_chars [side])
        canvas.text (tail, self.conn_chars [side])
    # end def render_link

    def render_node (self, node, canvas) :
        box    = node.box
        pos    = box.top_left + D2.Point (2, 1)
        width  = box.size.x   - 2
        height = box.size.y   - 2
        def _label_parts (parts, width, height) :
            i = 0
            l = len (parts)
            x = ""
            while i < l and height > 0:
                p  = x + parts [i]
                i += 1
                while i < l and len (p) < width :
                    if len (p) + len (parts [i]) < width :
                        p += parts [i]
                        i += 1
                    else :
                        break
                yield p
                height -= 1
                x = " "
        for lp in _label_parts (node.entity.label_parts, width, height) :
            canvas.text (pos, lp)
            pos.shift   ((0, 1))
        canvas.rectangle (box)
    # end def render_node

# end class Renderer

if __name__ != "__main__" :
    MOM.Graph._Export_Module ()
### __END__ MOM.Graph.Ascii
