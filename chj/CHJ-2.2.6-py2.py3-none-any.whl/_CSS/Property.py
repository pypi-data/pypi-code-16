# -*- coding: utf-8 -*-
# Copyright (C) 2014-2017 Mag. Christian Tanzer All rights reserved
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
#    CHJ.CSS.Property
#
# Purpose
#    CSS property specification with necessary vendor prefixes, if any
#
# Revision Dates
#    12-Apr-2014 (CT) Creation
#    13-Apr-2014 (CT) Add `Value`, `Align_Items`, `Align_Self`, `Display`,
#                     `Justify_Content`, `Order`, `Width`; factor `_Prop_`
#     9-Jul-2014 (CT) Add `* args` to `Property.__call__`
#    11-Oct-2016 (CT) Move from `GTW` to `CHJ`
#    27-Dec-2016 (CT) Add `Flex_Direction`, `Scroll_Snap_Align`,
#                     `Scroll_Snap_Type`
#    27-Dec-2016 (CT) Remove `-webkit` prefix from flex properties/values
#    27-Dec-2016 (CT) Remove `-moz` prefix from `Box`, `Font_Feat`
#    11-Jan-2017 (CT) Add `Align_Content`
#    12-Jan-2017 (CT) Support symbolic arguments in `Property.__call__`
#                     * add `as_text`
#    12-Jan-2017 (CT) Remove `Calc`
#    18-Jan-2017 (CT) Remove `-webkit` prefix from `Box`
#    ««revision-date»»···
#--

"""
Specification of CSS properties with automatically generated
vendor prefixes::

    >>> from   _TFL.portable_repr import portable_repr
    >>> def show (p) :
    ...     print (portable_repr (p))

    >>> Border    = Property ("border")

    >>> show (Border (color = "red", width = "2px"))
    {'border-color' : 'red', 'border-width' : '2px'}
    >>> show (Border (color = "red", width = "2px", radius = "2px"))
    {'border-color' : 'red', 'border-radius' : '2px', 'border-width' : '2px'}

    >>> Border_pr = Property ("border", radius = ("-moz", "-webkit"))

    >>> show (Border_pr (color = "red", width = "2px"))
    {'border-color' : 'red', 'border-width' : '2px'}
    >>> show (Border_pr (color = "red", width = "2px", radius = "2px"))
    {'-moz-border-radius' : '2px', '-webkit-border-radius' : '2px', 'border-color' : 'red', 'border-radius' : '2px', 'border-width' : '2px'}

    >>> show (Transform (origin = "60% 100%", translate = "100px"))
    {'-ms-transform-origin' : '60% 100%', '-ms-transform-translate' : '100px', '-webkit-transform-origin' : '60% 100%', '-webkit-transform-translate' : '100px', 'transform-origin' : '60% 100%', 'transform-translate' : '100px'}

    >>> show (Transform ("rotate(-45deg)", origin = "60% 100%", translate = "100px"))
    {'-ms-transform' : 'rotate(-45deg)', '-ms-transform-origin' : '60% 100%', '-ms-transform-translate' : '100px', '-webkit-transform' : 'rotate(-45deg)', '-webkit-transform-origin' : '60% 100%', '-webkit-transform-translate' : '100px', 'transform' : 'rotate(-45deg)', 'transform-origin' : '60% 100%', 'transform-translate' : '100px'}

    >>> show (Align_Items ("center"))
    {'-ms-align-items' : 'center', 'align-items' : 'center'}

    >>> show (Display ("flex"))
    {'display' : ['flex', '-ms-flex']}

    >>> show (Flex  (flow = "row wrap", grow = 8))
    {'-ms-flex-flow' : 'row wrap', '-ms-flex-grow' : 8, 'flex-flow' : 'row wrap', 'flex-grow' : 8}

    >>> show (Order (3))
    {'-ms-order' : '3', 'order' : '3'}

    >>> show (Width ("min_content"))
    {'width' : ['min-content', '-moz-min-content', '-webkit-min-content']}

"""

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _CHJ                       import CHJ
from   _TFL                       import TFL

from   _CHJ.Parameters            import P_dict
import _CHJ._CSS

from   _TFL._Meta.Once_Property   import Once_Property
from   _TFL.pyk                   import pyk

import _TFL._Meta.Object

from   itertools                  import chain as ichain

class _Prop_ (TFL.Meta.Object) :

    def __init__ (self, _name, * _prefixes, ** kw) :
        """`_prefixes` specify the vendor prefixes needed for all values,
           `kw` specify the vendor prefixes needed for the `keys` in `kw`.
        """
        self.name      = _name
        self.prefixes  = _prefixes
        self.vp_map    = dict (kw)
    # end def __init__

# end class _Prop_

class Property (_Prop_) :
    """CSS property specification with necessary vendor prefixes, if any."""

    def __call__ (self, * args, ** decls) :
        """Return a dict with `decls` plus any necessary prefixed declarations.
        """
        result    = {}
        name      = self.name
        prefixes  = self.prefixes
        vp_map    = self.vp_map
        as_text   = pyk.text_type
        if args :
            v = result [name] = " ".join (as_text (a) for a in args)
            for p in prefixes :
                result ["-".join ((p, name))] = v
        for k, v in pyk.iteritems (decls) :
            k = k.replace ("_", "-")
            n = "-".join ((name, k))
            result [n] = v
            t = k.split ("-") [-1]
            for p in ichain (vp_map.get (t, ()), prefixes) :
                result ["-".join ((p, n))] = v
        return result
    # end def __call__

    @Once_Property
    def P (self) :
        """Property parameter dict: supports lazy evaluation of dict arguments.
        """
        cls = self.__class__
        def _P__call__ (this, P) :
            return self (** P_dict.__call__ (this, P))
        return P_dict.__class__ \
            ( "P_%s" % (cls.__name__)
            , (P_dict, )
            , dict
                ( __call__   = _P__call__
                , __module__ = cls.__module__
                )
            )
    # end def P

# end class Property

class Value (_Prop_) :
    """CSS value specification with necessary vendor prefixes, if any."""

    def __call__ (self, value) :
        name   = self.name.replace       ("_", "-")
        v      = pyk.text_type (value).replace ("_", "-")
        prefs  = self.vp_map.get (value, ())
        if prefs :
            values = [v]
            for p in prefs :
                values.append ("-".join ((p, v)))
        else :
            values = v
        result = {name : values}
        for p in self.prefixes :
            result ["-".join ((p, name))] = values
        return result
    # end def __call__

# end class Value

Border         = Property ("border")
Box            = Property ("box")
Column         = Property ("column",                "-moz",        "-webkit")
Filter         = Property ("filter",                               "-webkit")
Flex           = Property ("flex",                          "-ms")
Flex_Direction = Property ("flex-direction",                "-ms")
Font_Feat      = Property ("font-feature-settings",                "-webkit")
Gradient       = Property ("gradient",                             "-webkit")
Transform      = Property ("transform",                     "-ms", "-webkit")
Transition     = Property ("transition",                           "-webkit")

### http://www.adobe.com/devnet/html5/articles/working-with-flexbox-the-new-spec.html
### http://caniuse.com/#feat=flexbox
Align_Content     = Value ("align_content",   "-ms")
Align_Items       = Value ("align_items",     "-ms")
Align_Self        = Value ("align_self",      "-ms")
Display           = Value \
    ( "display"
    , flex        = ("-ms", )
    , inline_flex = ("-ms", )
    )
Justify_Content   = Value ("justify_content", "-ms")
Order             = Value ( "order",          "-ms")

### http://dev.w3.org/csswg/css-sizing/#column-sizing
### http://caniuse.com/#feat=intrinsic-width
Width             = Value    \
    ( "width"
    , fill        = ("-moz", "-webkit")
    , fit_content = ("-moz", "-webkit")
    , max_content = ("-moz", "-webkit")
    , min_content = ("-moz", "-webkit")
    )

### https://drafts.csswg.org/css-scroll-snap/#properties-on-the-scroll-container
### https://drafts.csswg.org/css-scroll-snap/#properties-on-the-elements
### http://caniuse.com/#search=scroll-snap
Scroll_Snap_Align = Value ("scroll-snap-align",           "-ms", "-webkit")
Scroll_Snap_Type  = Value ("scroll-snap-type",            "-ms", "-webkit")

if __name__ != "__main__" :
    CHJ.CSS._Export ("*")
### __END__ CHJ.CSS.Property
