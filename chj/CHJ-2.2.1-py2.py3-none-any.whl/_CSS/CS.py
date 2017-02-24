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
#    CHJ.CSS.CS
#
# Purpose
#    Provide classes for various kinds of child selector
#
# Revision Dates
#     5-Jan-2017 (CT) Creation
#    20-Jan-2017 (CT) Add `prefixed`
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _CHJ                       import CHJ
from   _TFL                       import TFL

import _CHJ._CSS

import _TFL._Meta.Object

from   _TFL._Meta.Once_Property   import Once_Property
from   _TFL.predicate             import cartesian
from   _TFL.pyk                   import pyk

@pyk.adapt__str__
class _Child_Selector_ (TFL.Meta.Object) :
    """Base class for child selector classes"""

    parent_sep = None

    def __init__ (self, * selectors) :
        self._selectors = tuple (self._normalized (selectors))
    # end def __init__

    def __call__ (self, parent) :
        parent_sep = self.parent_sep
        if parent is not None :
            result = \
                [   parent_sep.join (s)
                for s in cartesian (parent.selectors, self._selectors)
                ]
        else :
            ps     = parent_sep.lstrip ()
            result = [(ps + s) for s in self._selectors]
        return result
    # end def __call__

    def prefixed (self, selector) :
        if len (self._selectors) != 1 :
            raise TypeError \
                ( "Can't prefix `%s` with multi-selector `%s`"
                % (selector, self)
                )
        return self.parent_sep.join ((self._selectors [0], selector))
    # end def prefixed

    def _normalized (self, selectors) :
        return selectors
    # end def _normalized

    def __str__ (self) :
        return ", ".join (self (parent = None))
    # end def __str__

# end class _Child_Selector_

class _Child_Selector_Strip_ (_Child_Selector_) :

    def _normalized (self, selectors) :
        parent_sep = self.parent_sep [0]
        for s in selectors :
            yield s.strip ().lstrip (parent_sep)
    # end def _normalized

# end class _Child_Selector_Strip_

class Attr (_Child_Selector_) :
    """Child selector for attribute value.

    >>> print (Attr ("href^=https:"))
    [href^=https:]

    >>> print (Attr ("title", "[data-title~=foo]"))
    [title], [data-title~=foo]

    """

    parent_sep = ""

    def _normalized (self, selectors) :
        for s in selectors :
            v = s.strip ()
            if v :
                if not (v.startswith ("[") and v.endswith ("]")) :
                    v = "[" + v + "]"
                yield v
    # end def _normalized

# end class Attr

class Child (_Child_Selector_) :
    """Child selector for a direct child.

    >>> print (Child (".foo"))
    > .foo

    """

    parent_sep = " > "

# end class Child

class Class (_Child_Selector_Strip_) :
    """Child selector for an element with a specific class.

    >>> print (Class ("foo.bar", ".bar.baz"))
    .foo.bar, .bar.baz

    """

    parent_sep = "."

# end class Class

class Descendant (_Child_Selector_) :
    """Child selector for descendent elements."""

    parent_sep = " "

# end class Descendant

class Id (_Child_Selector_Strip_) :
    """Child selector for an element with a specific ID.

    >>> print (Id ("foo", "#bar"))
    #foo, #bar

    """

    parent_sep = "#"

# end class Id

class Pseudo (_Child_Selector_Strip_) :
    """Child selector for a pseudo class.

    >>> print (Pseudo ("hover", ":first-child"))
    :hover, :first-child

    """

    parent_sep = ":"

Pseudo_C = Pseudo # end class Pseudo

class Pseudo_Element (Pseudo) :
    """Child selector for a pseudo element.

    >>> print (Pseudo_Element ("after"))
    ::after

    """

    parent_sep = "::"

Pseudo_E = Pseudo_Element # end class Pseudo_Element

class Sibling (_Child_Selector_) :
    """Child selector for adjacent sibling element.

    >>> print (Sibling ("input"))
    + input
    """

    parent_sep = " + "

# end class Sibling

class Sibling_General (Sibling) :
    """Child selector for general sibling, i.e., any following sibling.

    >>> print (Sibling_General ("aside"))
    ~ aside

    """

    parent_sep = " ~ "

Sibling_G = Sibling_General # end class Sibling_General

if __name__ != "__main__" :
    CHJ.CSS._Export_Module ()
### __END__ CHJ.CSS.CS
