# -*- coding: utf-8 -*-
# Copyright (C) 2010-2017 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package CHJ.CSS.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    CHJ.CSS.Length
#
# Purpose
#    Model a CSS length value
#
# Revision Dates
#    29-Dec-2010 (CT) Creation
#     1-Jan-2011 (CT) `TRBL0` added
#     1-Jan-2011 (CT) `__truediv__` and `__floordiv__` added
#     2-Jan-2011 (CT) `TRBL` added
#    12-Jan-2011 (CT) `__neg__` and `__pos__` added
#    21-Feb-2011 (CT) `HV` added
#    29-Nov-2011 (CT) Add `Rem`
#    17-Jan-2012 (CT) Add `Ch`, `Vh`, `Vm`, `Vw`, function `Length`
#    18-Jan-2012 (CT) Add support for arithmetic operators to `TRBL`, `TRBL0`
#    18-Jan-2012 (CT) Factor `_TRBL_`
#    29-Oct-2015 (CT) Improve Python 3 compatibility
#    11-Oct-2016 (CT) Move from `GTW` to `CHJ`
#    23-Dec-2016 (CT) Add `adapt__str__` to `_Length_`
#    12-Jan-2017 (CT) Use `Calc` for mixed arithmetic
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division
from   __future__  import print_function, unicode_literals

from   _CHJ                       import CHJ
from   _TFL                       import TFL

import _CHJ._CSS
import _CHJ._CSS._TRBL_
import _CHJ._CSS.Calc

import _TFL._Meta.Object
from   _TFL._Meta.Once_Property   import Once_Property

from   _TFL.pyk                   import pyk
from   _TFL.Regexp                import Regexp, re

class M_Length (TFL.Meta.Object.__class__) :
    """Meta class for `_Length_`."""

    _Unit_Map = {}

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        if name != "_Length_" and cls.unit_name is None :
            cls.unit_name = name.lower ()
        if cls.unit_name :
            assert cls.unit_name not in cls._Unit_Map
            cls._Unit_Map [cls.unit_name] = cls
    # end def __init__

    @Once_Property
    def Pat (cls) :
        return Regexp \
            ( r"^"
            + r"(?P<number> [-+]? \d+ (?: \.\d*)?)"
            + r"(?P<unit>"
            + "|".join (re.escape (u) for u in sorted (cls._Unit_Map))
            + r")"
            + r"$"
            , re.VERBOSE | re.IGNORECASE
            )
    # end def Pat

# end class M_Length

@pyk.adapt__bool__
@pyk.adapt__div__
@pyk.adapt__str__
class _Length_ (TFL.Meta.BaM (TFL.Meta.Object, metaclass = M_Length)) :
    """Model a CSS length value.

    >>> print (Px (3))
    3px
    >>> print (Px (3) * 2)
    6px
    >>> print (Px (3) + Px (2))
    5px
    >>> print (Px (3) % 2)
    1px

    >>> print (Px (3) + In (2))
    calc(3px + 2in)
    >>> print (Px (3) - In (2))
    calc(3px - 2in)
    >>> print (Px (3) * In (2))
    calc(3px * 2in)
    >>> print (Px (3) / In (2))
    calc(3px / 2in)

    >>> print (Percent (100), Percent (100) / 2, Percent (100) / 2.5)
    100% 50.0% 40.0%

    >>> print (Rem (2))
    2rem
    >>> print (Rem (2.5))
    2.5rem

    >>> print (Rem (-2))
    -2rem
    >>> print (abs (Rem (-2)))
    2rem

    """

    unit_name     = None

    def __init__ (self, value = 0) :
        self.value = value
    # end def __init__

    def __abs__ (self) :
        return self.__class__ (abs (self.value))
    # end def __abs__

    def __add__ (self, rhs) :
        if not isinstance (rhs, self.__class__) :
            result = CHJ.CSS.Calc   (self, "+", rhs)
        else :
            result = self.__class__ (self.value + rhs.value)
        return result
    # end def __add__

    def __truediv__ (self, rhs) :
        if not isinstance (rhs, (int, float)) :
            result = CHJ.CSS.Calc   (self, "/", rhs)
        else :
            result = self.__class__ (self.value / rhs)
        return result
    # end def __truediv__

    def __eq__ (self, rhs) :
        ru = getattr (rhs, "unit_name", None)
        if self.unit_name == ru :
            return self.value == rhs.value
        else :
            if not rhs :
                return not self
        return False
    # end def __eq__

    def __float__ (self) :
        return float (self.value)
    # end def __float__

    def __floordiv__ (self, rhs) :
        if not isinstance (rhs, (int, float)) :
            raise TypeError \
                ( "Cannot divide %r and %r objects"
                % (self.__class__.__name__, rhs.__class__.__name__)
                )
        return self.__class__ (self.value // rhs)
    # end def __floordiv__

    def __int__ (self) :
        return int (self.value)
    # end def __int__

    def __hash__ (self) :
        return hash (self.unit_name, self.value)
    # end def __hash__

    def __mod__ (self, rhs) :
        if not isinstance (rhs, (int, float)) :
            raise TypeError \
                ( "Cannot take remainer of %r and %r objects"
                % (self.__class__.__name__, rhs.__class__.__name__)
                )
        return self.__class__ (self.value % rhs)
    # end def __mod__

    def __mul__ (self, rhs) :
        if not isinstance (rhs, (int, float)) :
            result = CHJ.CSS.Calc   (self, "*", rhs)
        else :
            result = self.__class__ (self.value * rhs)
        return result
    # end def __mul__

    def __rmul__ (self, rhs) :
        if not isinstance (rhs, (int, float)) :
            result = CHJ.CSS.Calc   (rhs, "*", self)
        else :
            result = self.__class__ (self.value * rhs)
        return result
    # end def __rmul__

    def __neg__ (self) :
        return self.__class__ (- self.value)
    # end def __neg__

    def __bool__ (self) :
        return bool (self.value)
    # end def __bool__

    def __pos__ (self) :
        return self
    # end def __pos__

    def __sub__ (self, rhs) :
        if not isinstance (rhs, self.__class__) :
            result = CHJ.CSS.Calc   (self, "-", rhs)
        else :
            result = self.__class__ (self.value - rhs.value)
        return result
    # end def __sub__

    def __str__ (self) :
        if self.value :
            return "%s%s" % (self.value, self.unit_name)
        else :
            return "0"
    # end def __str__

# end class _Length_

_length_keywords = set (("auto", "inherit"))

def Length (v) :
    """Convert strings and length objects to the appropriate `_Length_` instances.

    >>> print (Length ("1em"))
    1em
    >>> print (Length ("1ch"))
    1ch
    >>> print (Length ("1vw"))
    1vw
    >>> print (Length (Px (5)))
    5px
    >>> print (Length (0))
    0
    >>> print (Length (0.0))
    0
    >>> print (Length ("0"))
    0
    >>> print (Length (1))
    Traceback (most recent call last):
      ...
    ValueError: 1
    >>> print (Length ("1"))
    Traceback (most recent call last):
      ...
    ValueError: 1
    >>> print (Length ("1vx"))
    Traceback (most recent call last):
      ...
    ValueError: 1vx

    """
    if v in (0, "0") :
        result = Px (0)
    elif isinstance (v, pyk.string_types) :
        pat = _Length_.Pat
        v   = v.strip ()
        if v in _length_keywords :
            result = v
        elif pat.match (v) :
            T      = _Length_._Unit_Map [pat.unit.lower ()]
            n      = pat.number
            result = T (float (n) if ("." in n) else int (n, 10))
        else :
            raise ValueError (v)
    elif isinstance (v, _Length_) :
        result = v
    else :
        raise ValueError (v)
    return result
# end def Length

class Ch (_Length_) :
    """Relative CSS length unit: width of the "0" glyph in the element's font."""

# end class Ch

class Cm (_Length_) :
    """Absolute CSS length unit: centimeters."""

# end class Cm

class Em (_Length_) :
    """Relative CSS length unit: font size of the element."""

# end class Em

class Ex (_Length_) :
    """Relative CSS length unit: x-height of the element's font."""

# end class Ex

class In (_Length_) :
    """Absolute CSS length unit: inches."""

# end class In

class Mm (_Length_) :
    """Absolute CSS length unit: millimeters."""

# end class Mm

class Pc (_Length_) :
    """Absolute CSS length unit: picas (1 pc == 12 points)."""

# end class Pc

class Percent (_Length_) :
    """Relative CSS unit: percentages."""

    unit_name = "%"

    def __add__ (self, rhs) :
        if isinstance (rhs, (int, float)) :
            return self.__class__ (self.value + rhs)
        return self.__super.__add__ (rhs)
    # end def __add__

    def __sub__ (self, rhs) :
        if isinstance (rhs, (int, float)) :
            return self.__class__ (self.value - rhs)
        return self.__super.__sub__ (rhs)
    # end def __sub__

# end class Percent

class Pt (_Length_) :
    """Absolute CSS length unit: points (1pt == 1/72 inch)."""

# end class Pt

class Px (_Length_) :
    """Relative CSS length unit: pixels (1px == 1/96 inch)."""

# end class Px

class Rem (_Length_) :
    """Relative CSS3 length unit: font size of the element relative to the root font size."""

# end class Rem

class Vh (_Length_) :
    """Relative CSS3 length unit: 1/100th of the viewport's height."""

# end class Vh

class Vm (_Length_) :
    """Relative CSS3 length unit: minimum of `Vh` or `Vw`."""

# end class Vm

class Vw (_Length_) :
    """Relative CSS3 length unit: 1/100th of the viewport's width."""

# end class Vw

@pyk.adapt__div__
class TRBL0 (CHJ.CSS._TRBL0_) :
    """Top/right/bottom/left spec, undefined values are 0.

    >>> print (TRBL0 (0))
    0
    >>> print (TRBL0 (Px (1), Px (2), Px (1), Px (2)))
    1px 2px
    >>> print (TRBL0 (Px (1), Px (2), Px (3), Px (2)))
    1px 2px 3px
    >>> print (TRBL0 (Px (1), Px (2), Px (3), Px (4)))
    1px 2px 3px 4px
    >>> print (TRBL0 (Px (1), Em (1)))
    1px 1em 0 0
    >>> print (TRBL0 (Px (1), 0, Em (1)))
    1px 0 1em
    >>> print (TRBL0 (Px (1), 0, Px (1)))
    1px 0
    >>> print (TRBL0 (t = Px (1)))
    1px 0 0
    >>> print (TRBL0 (r = Px (1)))
    0 1px 0 0
    >>> print (TRBL0 (b = Px (1)))
    0 0 1px
    >>> print (TRBL0 (l = Px (1)))
    0 0 0 1px
    >>> print (TRBL0 (default = Px(2)))
    2px
    >>> print (TRBL0 (t = Px (1), default = Px(2)))
    1px 2px 2px
    >>> print (TRBL0 (r = Px (1), default = Px(2)))
    2px 1px 2px 2px
    >>> print (TRBL0 (b = Px (1), default = Px(2)))
    2px 2px 1px
    >>> print (TRBL0 (l = Px (1), default = Px(2)))
    2px 2px 2px 1px

    """

    default = 0
    Type    = staticmethod (Length)

    def __abs__ (self) :
        return self.__class__ (* tuple (abs (v) for v in self.values))
    # end def __abs__

    def __add__ (self, rhs) :
        if isinstance (rhs, _Length_) :
            rhs = (rhs, ) * 4
        elif isinstance (rhs, (tuple, list)) :
            rhs = self.__class__ (* rhs)
        return self.__class__ \
            (* tuple (v + r for v, r in zip (self.values, rhs)))
    # end def __add__

    def __truediv__ (self, rhs) :
        return self.__class__ (* tuple (v / rhs for v in self.values))
    # end def __truediv__

    def __floordiv__ (self, rhs) :
        return self.__class__ (* tuple (v // rhs for v in self.values))
    # end def __floordiv__

    def __mod__ (self, rhs) :
        return self.__class__ (* tuple (v % rhs for v in self.values))
    # end def __mod__

    def __mul__ (self, rhs) :
        return self.__class__ (* tuple (v * rhs for v in self.values))
    # end def __mul__

    __rmul__ = __mul__

    def __neg__ (self) :
        return self.__class__ (* tuple (-v for v in self.values))
    # end def __neg__

    def __pos__ (self) :
        return self
    # end def __pos__

    def __sub__ (self, rhs) :
        if isinstance (rhs, _Length_) :
            rhs = (rhs, ) * 4
        elif isinstance (rhs, (tuple, list)) :
            rhs = self.__class__ (* rhs)
        return self.__class__ \
            (* tuple (v - r for v, r in zip (self.values, rhs)))
    # end def __sub__

# end class TRBL0

class TRBL (CHJ.CSS._TRBL_, TRBL0) :
    """Top/right/bottom/left spec, repeated values.

    >>> print (TRBL ())
    0
    >>> print (TRBL (Em (1)))
    1em
    >>> print (TRBL (Em (1), Px (2)))
    1em 2px
    >>> print (TRBL (Em (1), Px (2), Ex (3)))
    1em 2px 3ex
    >>> print (TRBL (Em (1), Px (2), Ex (3)).l)
    2px
    >>> print (TRBL (Em (1), Px (2), Ex (3), Cm (4)))
    1em 2px 3ex 4cm
    >>> print (TRBL (Em (1), Px (0), Ex (3), Cm (4)))
    1em 0 3ex 4cm

    >>> print (-TRBL (Em (1), Px (2)))
    -1em -2px

    >>> print (TRBL ("1em", "8vw"))
    1em 8vw
    >>> print (TRBL ("1em", "8vw") + (Em (3), "7vw"))
    4em 15vw
    >>> print (TRBL ("1em", "8em") + Em (4))
    5em 12em
    >>> print (TRBL ("1em", "8em") * 2)
    2em 16em
    >>> print ((TRBL ("1em", "8em") * 2) - Em (1))
    1em 15em
    >>> print (4 * TRBL ("1em", "8em"))
    4em 32em

    >>> print (TRBL ("1em", "auto"))
    1em auto

    """

# end class TRBL

@pyk.adapt__bool__
class HV (TFL.Meta.Object) :
    """Horizontal/vertical pair of `Length` of `TRBL`.

    >>> print (HV (Px (100), Px (50)))
    100px / 50px
    >>> print (HV (TRBL (Px (5), Px (10)), TRBL (Px (10), Px (5), Px (10))))
    5px 10px / 10px 5px
    """

    def __init__ (self, h, v) :
        self.h = h
        self.v = v
    # end def __init__

    def __bool__ (self) :
        return self.h or self.v
    # end def __bool__

    def __str__ (self) :
        return "%s / %s" % (self.h, self.v)
    # end def __str__

# end class HV

__all__ = tuple \
    ( k for (k, v) in pyk.iteritems (globals ())
        if  getattr (v, "unit_name", None)
    ) + ("Length", "TRBL0", "TRBL", "HV")

if __name__ != "__main__" :
    CHJ.CSS._Export (* __all__)
### __END__ CHJ.CSS.Length
