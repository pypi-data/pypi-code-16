# -*- coding: utf-8 -*-
# Copyright (C) 2012-2016 Mag. Christian Tanzer All rights reserved
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
#    CHJ.CSS.Color
#
# Purpose
#    Model a CSS color value
#
# Revision Dates
#    17-Jan-2012 (CT) Creation
#    18-Jan-2012 (CT) Add `C_TRBL0` and `C_TRBL`
#    11-Oct-2016 (CT) Move from `GTW` to `CHJ`
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division
from   __future__  import print_function, unicode_literals

from   _CHJ                       import CHJ
from   _TFL                       import TFL

import _CHJ._CSS
import _CHJ._CSS._TRBL_

import _TFL._Meta.Object
from   _TFL._Meta.Once_Property   import Once_Property

from   _TFL.Color                 import *
from   _TFL.Color                 import _Color_
from   _TFL.pyk                   import pyk
from   _TFL.Regexp                import Regexp, re

class _Color_Converter_ (TFL.Meta.Object) :
    """Convert CSS color strings to the appropriate `_Color_` instance.

    >>> print (Color ("rgb(255,0,0)"))
    rgb(255, 0, 0)
    >>> print (Color ("rgb (255,0,80)"))
    rgb(255, 0, 80)
    >>> print (Color ("rgb(100%, 0%, 0%) "))
    rgb(100%, 0%, 0%)
    >>> print (Color ("rgb(100%, 0%, 25%)"))
    rgb(100%, 0%, 25%)
    >>> print (Color ("rgb(110%, 0%, -25%)"))
    rgb(100%, 0%, 0%)
    >>> print (Color ("rgba(0,0,255,0.5)"))
    rgba(0, 0, 255, 0.5)
    >>> print (Color ("rgba(100%, 50%, 0%, 0.1)"))
    rgba(100%, 50%, 0%, 0.1)
    >>> print (Color ("hsl(120, 100%, 50%)"))
    hsl(120, 100%, 50%)
    >>> print (Color ("hsl(120, 100%, 50%, 0.75)"))
    hsla(120, 100%, 50%, 0.75)
    >>> print (Color ("olive").as_RGB_X)
    #808000
    >>> print (Color ("transparent"))
    transparent

    >>> print (Color (SVG_Color ("olive")).as_RGB_X)
    #808000

    """

    keywords      = set (("inherit", "transparent"))

    hsl_pattern   = Regexp \
        ( r"^"
        + r"hsla?\s*\("
          + r"\s* (\d{1,3})\s* "
          + r","
          + r"\s* (\d{1,3})\s*  \% \s*"
          + r","
          + r"\s* (\d{1,3})\s*  \% \s*"
          + r"(?:"
              + r","
              + r"\s* (?P<alpha> \d+ (?: \.\d*)?)\s* "
          + r")?"
        + r"\)"
        + r"$"
        , re.VERBOSE | re.IGNORECASE
        )


    rgb_8_pattern = Regexp \
        ( r"^"
        + r"rgba?\s*\("
          + r"\s* (\d{1,3})\s* "
          + r","
          + r"\s* (\d{1,3})\s* "
          + r","
          + r"\s* (\d{1,3})\s* "
          + r"(?:"
              + r","
              + r"\s* (?P<alpha> \d+ (?: \.\d*)?)\s* "
          + r")?"
        + r"\)"
        + r"$"
        , re.VERBOSE | re.IGNORECASE
        )

    rgb_p_pattern = Regexp \
        ( r"^"
        + r"rgba?\s*\("
          + r"\s* (-?\d{1,3})\s* \% \s*"
          + r","
          + r"\s* (-?\d{1,3})\s* \% \s*"
          + r","
          + r"\s* (-?\d{1,3})\s* \% \s*"
          + r"(?:"
              + r","
              + r"\s* (?P<alpha> \d+ (?: \.\d*)?)\s* "
          + r")?"
        + r"\)"
        + r"$"
        , re.VERBOSE | re.IGNORECASE
        )

    def __call__ (self, v) :
        if isinstance (v, pyk.string_types) :
            percent = lambda x : max (min (int (x), 100), 0)
            v = v.strip ()
            if v in self.keywords :
                result  = v
            elif v.startswith ("#") :
                result  = RGB_X (v)
            elif self.name_pattern.match (v) :
                result  = SVG_Color (v)
            elif self.hsl_pattern.match (v) :
                convert = (int, percent, percent)
                result  = self._convert (HSL,   convert, self.hsl_pattern)
            elif self.rgb_8_pattern.match (v) :
                result  = self._convert (RGB_8, int,     self.rgb_8_pattern)
            elif self.rgb_p_pattern.match (v) :
                result  = self._convert (RGB_P, percent, self.rgb_p_pattern)
            else :
                raise ValueError (v)
        elif isinstance (v, _Color_) :
            result = v
        else :
            raise ValueError (v)
        return result
    # end def __call__

    @property
    def formatter (self) :
        return _Color_.formatter
    # end def formatter

    @formatter.setter
    def formatter (self, value) :
        _Color_.formatter = value
    # end def formatter

    @Once_Property
    def name_pattern (self) :
        return Regexp \
            ( r"^"
            + "|".join (re.escape (u) for u in sorted (SVG_Color.Map))
            + r"$"
            , re.VERBOSE | re.IGNORECASE
            )
    # end def name_pattern

    def _convert (self, Type, convert, pat) :
        if not isinstance (convert, tuple) :
            convert = (convert, ) * 3
        vs    = (c (v) for c, v in zip (convert, pat.groups () [:3]))
        alpha = pat.alpha
        if alpha is not None :
            alpha = float (alpha)
        return Type (* vs, alpha = alpha)
    # end def _convert

# end class _Color_Converter_

Color = _Color_Converter_ ()

class C_TRBL0 (CHJ.CSS._TRBL0_) :
    """Top/right/bottom/left color spec, undefined values are `transparent`.

    >>> print (C_TRBL0 ())
    transparent
    >>> print (C_TRBL0 ("red"))
    red transparent transparent

    >>> print (C_TRBL0 (t = "#F00"))
    #F00 transparent transparent

    """ # "#"

    default = "transparent"
    Type    = Color

# end class C_TRBL0

class C_TRBL (CHJ.CSS._TRBL_, C_TRBL0) :
    """Top/right/bottom/left color spec, repeated values.

    >>> print (C_TRBL ("red"))
    red
    >>> print (C_TRBL ("red", "blue"))
    red blue

    """

# end class C_TRBL

__all__ = tuple (TFL._.Color.__all__ + ("Color", "C_TRBL", "C_TRBL0"))

if __name__ != "__main__" :
    CHJ.CSS._Export (* __all__)
### __END__ CHJ.CSS.Color
