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
#    CHJ.CSS.Calc
#
# Purpose
#    Model a CSS calc expression
#
# Revision Dates
#    12-Jan-2017 (CT) Creation
#    17-Jan-2017 (CT) Add attribute `args` to `Calc`
#                     + Allow later resolution of symbolic parameters
#    ««revision-date»»···
#--

"""
Model CSS calc expressions with support for CSS.Length operands::

    >>> from _CHJ._CSS.Length   import *
    >>> from _CHJ._CSS.Property import *

    >>> from _TFL.portable_repr import portable_repr
    >>> def show (p) :
    ...     print (portable_repr (p))

    >>> show (Calc (Px (100), "+ 3em"))
    'calc(100px + 3em)'
    >>> show (Calc (Vw (100), "-", Em (2)))
    'calc(100vw - 2em)'

    >>> show (Px (10) + Em (1) + Percent (25))
    'calc(10px + 1em + 25%)'

    >>> show ((Px (10) + Em (1)) * 25)
    'calc(calc(10px + 1em) * 25)'

    >>> show (2 * (Px (10) + Em (1)))
    'calc(2 * calc(10px + 1em))'

    Need to use `"2"` here to avoid immediate multiplication by `Px`
    >>> show ("2" * Px (10) + Em (1))
    'calc(calc(2 * 10px) + 1em)'

    >>> show (Flex ("0 0", Calc (Vw (100), "-", Em (2))))
    {'-ms-flex' : '0 0 calc(100vw - 2em)', 'flex' : '0 0 calc(100vw - 2em)'}

    >>> show (Flex ("0 0", Vw (100) - Em (2)))
    {'-ms-flex' : '0 0 calc(100vw - 2em)', 'flex' : '0 0 calc(100vw - 2em)'}

    >>> show ((Vw (100) - Em (2)) / 2)
    'calc(calc(100vw - 2em) / 2)'
    >>> show (2 * (Vw (100) - Em (2)))
    'calc(2 * calc(100vw - 2em))'

"""

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _CHJ                       import CHJ
from   _TFL                       import TFL

import _CHJ._CSS

import _TFL._Meta.Object

from   _TFL.pyk                   import pyk
from   _TFL.Regexp                import Regexp, re

@pyk.adapt__div__
@pyk.adapt__str__
class Calc (TFL.Meta.Object) :
    """Model a CSS calc expression."""

    _expr_pat    = Regexp (r"(?: |[*/])")
    _product_pat = Regexp (r"[*/]")
    _sub_pat     = Regexp (r" - ")

    def __init__ (self, * args) :
        as_text    = pyk.text_type
        self.args  = args
        self.value = " ".join (as_text (a) for a in args)
    # end def __init__

    def __add__ (self, rhs) :
        product_p = self._product_pat.search (self.value)
        lhs       = self if product_p else self.value
        return self.__class__ (lhs, "+", rhs)
    # end def __add__

    def __mul__ (self, rhs) :
        expr_p    = self._expr_pat.search (self.value)
        lhs       = self if expr_p else self.value
        return self.__class__ (lhs, "*", rhs)
    # end def __mul__

    def __radd__ (self, rhs) :
        value     = self.value
        product_p = self._product_pat.search (value)
        sub_p     = self._sub_pat.search     (value)
        lhs       = self if product_p or sub_p else value
        return self.__class__ (rhs, "+", lhs)
    # end def __radd__

    def __repr__ (self) :
        return repr (str (self))
    # end def __repr__

    def __rmul__ (self, rhs) :
        expr_p    = self._expr_pat.search (self.value)
        lhs       = self if expr_p else self.value
        return self.__class__ (rhs, "*", lhs)
    # end def __rmul__

    def __rsub__ (self, rhs) :
        expr_p    = self._expr_pat.search (self.value)
        lhs       = self if expr_p else self.value
        return self.__class__ (rhs, "-", lhs)
    # end def __rsub__

    def __sub__ (self, rhs) :
        expr_p    = self._expr_pat.search (self.value)
        lhs       = self if expr_p else self.value
        return self.__class__ (lhs, "-", rhs)
    # end def __sub__

    def __truediv__ (self, rhs) :
        expr_p    = self._expr_pat.search (self.value)
        lhs       = self if expr_p else self.value
        return self.__class__ (lhs, "/", rhs)
    # end def __truediv__

    def __str__ (self) :
        return "calc(%s)" % (self.value, )
    # end def __str__

# end class Calc

if __name__ != "__main__" :
    CHJ.CSS._Export ("Calc")
### __END__ CHJ.CSS.Calc
