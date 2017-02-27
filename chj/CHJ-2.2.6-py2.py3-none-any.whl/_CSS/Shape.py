# -*- coding: utf-8 -*-
# Copyright (C) 2017 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package CHJ.CSS.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    CHJ.CSS.Shape
#
# Purpose
#    Functions to create shapes with CSS rules
#
# Revision Dates
#    18-Jan-2017 (CT) Creation
#    ««revision-date»»···
#--

r"""
Functions creating CSS rules for shapes.

    >>> from _CHJ._CSS.Length   import Em, Px, Vw
    >>> def show (p) :
    ...     output = "\n".join \
    ...         (y for y in (x.strip () for x in str (p).split ("\n")) if y)
    ...     print (output)


    >>> show (Triangle_bottom_left ("red", Em (1)))
    { border-color : transparent transparent red
    ; border-width : 0 1em 1em 0
    }

    >>> show (Triangle_bottom_right ("red", Em (1)))
    { border-color : transparent transparent red
    ; border-width : 0 0 1em 1em
    }

    >>> show (Triangle_down ("red", Em (1)))
    { border-color : red transparent transparent
    ; border-width : 1em 1em 0
    }

    >>> show (Triangle_down ("red", Px (100), Px (50)))
    { border-color : red transparent transparent
    ; border-width : 100px 50px 0
    }

    >>> show (Triangle_left ("red", Em (1)))
    { border-color : transparent red transparent transparent
    ; border-width : 1em 1em 1em 0
    }

    >>> show (Triangle_left ("red", Px (100), Px (50)))
    { border-color : transparent red transparent transparent
    ; border-width : 50px 100px 50px 0
    }

    >>> show (Triangle_right ("red", Em (1)))
    { border-color : transparent transparent transparent red
    ; border-width : 1em 0 1em 1em
    }

    >>> show (Triangle_right ("red", Px (100), Px (50)))
    { border-color : transparent transparent transparent red
    ; border-width : 50px 0 50px 100px
    }

    >>> show (Triangle_top_left ("red", Em (1)))
    { border-color : red transparent transparent
    ; border-width : 1em 1em 0 0
    }

    >>> show (Triangle_top_right ("red", Em (1)))
    { border-color : red transparent transparent
    ; border-width : 1em 0 0 1em
    }

    >>> show (Triangle_up ("red", Em (1)))
    { border-color : transparent transparent red
    ; border-width : 0 1em 1em
    }

    >>> show (Triangle_up ("red", Px (100), Px (50)))
    { border-color : transparent transparent red
    ; border-width : 0 50px 100px
    }

    >>> show (Triangle_down ("red", Em (1), include_base = True))
    { border-color : red transparent transparent
    ; border-style : solid
    ; border-width : 1em 1em 0
    ; box-sizing   : content-box
    ; display      : inline-block
    ; height       : 0
    ; width        : 0
    }

    >>> args = (Em (3), Vw (100), "red", "blue")

    >>> show (Skew_Sep_h (* args))
    { border-color : red blue transparent transparent
    ; border-width : 3em 100vw 0 0
    }

    >>> show (Skew_Sep_h_r (* args))
    { border-color : red transparent transparent blue
    ; border-width : 3em 0 0 100vw
    }

    >>> show (Skew_Sep_v (* args))
    { border-color : transparent transparent blue red
    ; border-width : 0 0 3em 100vw
    }

    >>> show (Skew_Sep_v_r (* args))
    { border-color : transparent red blue transparent
    ; border-width : 0 100vw 3em 0
    }

    >>> show (Skew_Sep_h (* args, include_base = True))
    { border-color : red blue transparent transparent
    ; border-style : solid
    ; border-width : 3em 100vw 0 0
    ; box-sizing   : content-box
    ; display      : inline-block
    ; height       : 0
    ; width        : 0
    }

    >>> show (Square ("red", Em (1)))
    { background : red
    ; height     : 1em
    ; width      : 1em
    }

    >>> show (Rectangle ("blue", Em (1), Em (2)))
    { background : blue
    ; height     : 2em
    ; width      : 1em
    }

    >>> show (Circle ("red", Em (10)))
    { background    : red
    ; border-radius : 5em
    ; height        : 10em
    ; width         : 10em
    }

    >>> show (Oval ("blue", Em (10), Em (20)))
    { background    : blue
    ; border-radius : 5em / 10em
    ; height        : 20em
    ; width         : 10em
    }

    >>> show (Trapezoid ("red", Em (10)))
    { border-color : transparent transparent red
    ; border-width : 0 5em 10em
    ; height       : 0
    ; width        : 10em
    }

    >>> show (Trapezoid ("red", Em (10), Em (2)))
    { border-color : transparent transparent red
    ; border-width : 0 8em 10em
    ; height       : 0
    ; width        : 10em
    }

    >>> show (Parallelogram ("blue", 30, Em (10), Em (6)))
    { -ms-transform     : skew(30deg)
    ; -webkit-transform : skew(30deg)
    ; background        : blue
    ; height            : 6em
    ; transform         : skew(30deg)
    ; width             : 10em
    }

"""

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _CHJ                       import CHJ
from   _TFL                       import TFL

from   _CHJ._CSS.Color            import C_TRBL0
from   _CHJ._CSS.Length           import HV, TRBL, TRBL0
from   _CHJ._CSS.Property         import Box, Transform
from   _CHJ._CSS.Rule             import Rule

Base = Rule \
    ( Box
        ( sizing         = "content-box"
        )
    , border_style   = "solid"
    , display        = "inline-block"
    , height         = 0
    , width          = 0
    )

def _rule (kw, * args, ** kwargs) :
    include_base = kwargs.pop ("include_base", False)
    args         = args + ((Base, kw) if include_base else (kw, ))
    return Rule (* args, ** kwargs)
# end def _rule

def Circle (color, radius, ** kwargs) :
    """Rule for a CSS circle."""
    rkw = dict \
        ( kwargs
        , background    = color
        , border_radius = radius // 2
        , height        = radius
        , width         = radius
        )
    return _rule (rkw)
# end def Circle

def Oval (color, size_x, size_y, ** kwargs) :
    """Rule for a CSS oval."""
    rkw = dict \
        ( kwargs
        , background    = color
        , border_radius = HV (size_x // 2, size_y // 2)
        , height        = size_y
        , width         = size_x
        )
    return _rule (rkw)
# end def oval

def Parallelogram (color, angle, size_x, size_y, ** kwargs) :
    """Rule for a CSS rectangle."""
    rkw = dict \
        ( kwargs
        , background = color
        , height     = size_y
        , width      = size_x
        )
    return _rule (rkw, Transform ("skew(%ddeg)" % (angle, )))
# end def Rectangle

def Rectangle (color, size_x, size_y, ** kwargs) :
    """Rule for a CSS rectangle."""
    rkw = dict \
        ( kwargs
        , background = color
        , height     = size_y
        , width      = size_x
        )
    return _rule (rkw)
# end def Rectangle

def Skew_Sep_h (height, width, top_color, bottom_color, include_base = False, ** kwargs) :
    """Rule for a horizontal skew separator..

       The angle is controlled by the `height` value.
    """
    rkw = dict \
        ( kwargs
        , border_color = C_TRBL0 (t = top_color,  r = bottom_color)
        , border_width = TRBL0   (t = height,     r = width)
        )
    return _rule (rkw, include_base = include_base)
# end def Skew_Sep_h

def Skew_Sep_h_r (height, width, top_color, bottom_color, include_base = False, ** kwargs) :
    """Rule for a reversed horizontal skew separator..

       The angle is controlled by the `height` value.
    """
    rkw = dict \
        ( kwargs
        , border_color = C_TRBL0 (t = top_color,  l = bottom_color)
        , border_width = TRBL0   (t = height,     l = width)
        )
    return _rule (rkw, include_base = include_base)
# end def Skew_Sep_h_r

def Skew_Sep_v (height, width, left_color, right_color, include_base = False, ** kwargs) :
    """Rule for a vertical skew separator..

       The angle is controlled by the `height` value.
    """
    rkw = dict \
        ( kwargs
        , border_color = C_TRBL0 (b = right_color, l = left_color)
        , border_width = TRBL0   (b = height,      l = width)
        )
    return _rule (rkw, include_base = include_base)
# end def Skew_Sep_v

def Skew_Sep_v_r (height, width, left_color, right_color, include_base = False, ** kwargs) :
    """Rule for a reversed vertical skew separator..

       The angle is controlled by the `height` value.
    """
    rkw = dict \
        ( kwargs
        , border_color = C_TRBL0 (b = right_color, r = left_color)
        , border_width = TRBL0   (b = height,      r = width)
        )
    return _rule (rkw, include_base = include_base)
# end def Skew_Sep_v_r

def Square (color, size, ** kwargs) :
    """Rule for a CSS square."""
    rkw = dict \
        ( kwargs
        , background = color
        , height     = size
        , width      = size
        )
    return _rule (rkw)
# end def Square

def Trapezoid (color, size_b, size_t = None, ** kwargs) :
    """Rule for a CSS trapezoid."""
    if size_t is None :
        size_t = size_b // 2
    size_lr = size_b - size_t
    rkw = dict \
        ( kwargs
        , border_color = C_TRBL0 (b = color)
        , border_width = TRBL    (0, size_lr, size_b, size_lr)
        , height       = 0
        , width        = size_b
        )
    return _rule (rkw)
# end def Trapezoid

def Triangle_bottom_left (color, size, include_base = False, ** kwargs) :
    """Rule for a CSS triangle in bottom left corner."""
    rkw = dict \
        ( kwargs
        , border_color = C_TRBL0 (b = color)
        , border_width = TRBL    (0, size, size, 0)
        )
    return _rule (rkw, include_base = include_base)
# end def Triangle_bottom_left

def Triangle_bottom_right (color, size, include_base = False, ** kwargs) :
    """Rule for a CSS triangle in bottom right corner."""
    rkw = dict \
        ( kwargs
        , border_color = C_TRBL0 (b = color)
        , border_width = TRBL    (0, 0, size, size)
        )
    return _rule (rkw, include_base = include_base)
# end def Triangle_bottom_right

def Triangle_down (color, long, short = None, include_base = False, ** kwargs) :
    """Rule for a CSS triangle pointing down with `color`."""
    if short is None :
        short = long
    rkw = dict \
        ( kwargs
        , border_color = C_TRBL0 (t = color)
        , border_width = TRBL    (long, short, 0, short)
        )
    return _rule (rkw, include_base = include_base)
# end def Triangle_down

def Triangle_left (color, long, short = None, include_base = False, ** kwargs) :
    """Rule for a CSS triangle pointing left with `color`."""
    if short is None :
        short = long
    rkw = dict \
        ( kwargs
        , border_color = C_TRBL0 (r = color)
        , border_width = TRBL    (short, long, short, 0)
        )
    return _rule (rkw, include_base = include_base)
# end def Triangle_left

def Triangle_right (color, long, short = None, include_base = False, ** kwargs) :
    """Rule for a CSS triangle pointing right with `color`."""
    if short is None :
        short = long
    rkw = dict \
        ( kwargs
        , border_color = C_TRBL0 (l = color)
        , border_width = TRBL    (short, 0, short, long)
        )
    return _rule (rkw, include_base = include_base)
# end def Triangle_right

def Triangle_top_left (color, size, include_base = False, ** kwargs) :
    """Rule for a CSS triangle in top left corner."""
    rkw = dict \
        ( kwargs
        , border_color = C_TRBL0 (t = color)
        , border_width = TRBL    (size, size, 0, 0)
        )
    return _rule (rkw, include_base = include_base)
# end def Triangle_top_left

def Triangle_top_right (color, size, include_base = False, ** kwargs) :
    """Rule for a CSS triangle in top right corner."""
    rkw = dict \
        ( kwargs
        , border_color = C_TRBL0 (t = color)
        , border_width = TRBL    (size, 0, 0, size)
        )
    return _rule (rkw, include_base = include_base)
# end def Triangle_top_right

def Triangle_up (color, long, short = None, include_base = False, ** kwargs) :
    """Rule for a CSS triangle pointing up with `color`."""
    if short is None :
        short = long
    rkw = dict \
        ( kwargs
        , border_color = C_TRBL0 (b = color)
        , border_width = TRBL    (0, short, long, short)
        )
    return _rule (rkw, include_base = include_base)
# end def Triangle_up

if __name__ != "__main__" :
    CHJ.CSS._Export_Module ()
### __END__ CHJ.CSS.Shape
