# -*- coding: utf-8 -*-
# Copyright (C) 2010-2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package GTW.OMP.SRM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.OMP.SRM.Boat
#
# Purpose
#    Model a sailboat
#
# Revision Dates
#    15-Apr-2010 (CT) Creation
#     5-May-2010 (CT) `sail_number` changed from `A_Int` to
#                     `A_Numeric_String` to allow autocompletion
#     7-May-2010 (CT) `sail_number` changed back to `A_Int` to fix sorting
#                     and set `needs_raw_value` to allow autocompletion
#    14-Oct-2010 (CT) `Init_Only_Mixin` added to `left`
#     9-Feb-2011 (CT) `Boat.left.ui_allow_new` set to `True`
#     2-May-2011 (CT) `sail_number_x` added
#    30-May-2011 (CT) `nation` changed from `Primary` to `Primary_Optional`
#     7-Sep-2011 (CT) `completer` added for `nation` and `sail_number`
#     9-Sep-2011 (CT) `completer` removed from `nation`
#    13-Sep-2011 (CT) `sail_number_x` changed from `Optional` to
#                     `Primary_Optional`
#    23-Sep-2011 (CT) `sail_number_x` and `sail_number` merged into a single
#                     attribute of type `A_String`, kind `Primary_Optional`
#     9-Nov-2011 (CT) Add cached attributes `sail_number_head` and `_tail`
#    17-Nov-2011 (CT) Split off `sail_number_x` again (to fix sorting)
#    17-Nov-2011 (CT) Redefine `ui_display_format` and `ui_display_sep`
#    18-Nov-2011 (CT) Import `unicode_literals` from `__future__`
#    20-Jan-2012 (CT) Add `sail_number.max_value`
#     8-Sep-2012 (CT) Add `valid_sail_number_x`
#     8-Sep-2012 (CT) Set `sail_number_x.ignore_case` to `"upper"`
#    11-Sep-2012 (CT) Add add `sail_number` to `valid_sail_number_x`
#    11-Sep-2012 (CT) Fix typo introduced in last change
#     3-Jun-2013 (CT) Use `.attr_prop` to access attribute descriptors
#    13-Aug-2013 (CT) Change `sail_number` from `Primary_Optional` to `Primary`
#    26-Mar-2014 (CT) Remove double quotes from `sail_number_x.description`
#    29-Aug-2014 (CT) Add `syntax` descriptions to `sail_number`, `sail_number_x`
#    26-Sep-2014 (CT) Add `sail_number.polisher`
#     5-Feb-2015 (CT) Paranoidify `sail_number.polisher`
#                     [somebody recently really tried to enter `NAT NAT 1234`]
#    11-Feb-2015 (CT) Remove `sail_number_head`, `sail_number_tail`
#    26-Feb-2015 (CT) Change `_Sail_Number_Polisher_` to override `__call__`,
#                     not `_polish`
#    29-Apr-2015 (CT) Remove obsolete predicate `valid_vintage`
#    30-Jul-2015 (CT) Add arguments `essence`, `picky` to
#                     `_Sail_Number_Polisher_`
#    26-Apr-2016 (CT) Add `buddies` to `_Sail_Number_Polisher_`
#    ««revision-date»»···
#--

from   __future__            import unicode_literals

from   _GTW                     import GTW
from   _MOM.import_MOM          import *

from   _GTW._OMP._SRM.Attr_Type import *

import _GTW._OMP._SRM.Boat_Class
import _GTW._OMP._SRM.Entity

from   _TFL.I18N                import _, _T, _Tn
from   _TFL.Regexp              import Multi_Regexp, Regexp, re

class _Sail_Number_Polisher_ (MOM.Attr.Polisher.Match_Split) :
    """Polisher splitting a sail-number into nation, sail_number, sail_number_x"""

    buddies      = ("nation", "sail_number", "sail_number_x")

    def __init__ (self, ** kw) :
        matcher = Regexp \
            ( r"^"
              r"(?:(?P<nation>[A-Za-z]{3}) +)?"
              r"(?:(?P<sail_number_x>[A-Za-z]+)[- ]*)?"
              r"(?P<sail_number>\d+)"
            )
        self.__super.__init__ (matcher = matcher, ** kw)
    # end def __init__

    def __call__ \
            ( self, attr, value_dict
            , essence = None
            , picky   = False
            , value   = None
            ) :
        result  = self.__super.__call__ \
            (attr, value_dict, essence, picky, value)
        undef   = object ()
        snx     = result.get ("sail_number_x", "")
        if snx :
            nat = result.get ("nation",      "")
            num = result.get ("sail_number", "")
            if nat :
                l = len (nat)
                while snx.startswith (nat) :
                    snx = snx [l:].strip ()
            if num :
                l = len (num)
                while snx.endswith (num) :
                    snx = snx [:-l].strip ()
            result ["sail_number_x"] = snx
        return result
    # end def __call__

# end class _Sail_Number_Polisher_

_sail_number_split = _Sail_Number_Polisher_ ()

_Ancestor_Essence = GTW.OMP.SRM.Link1

class Boat (_Ancestor_Essence) :
    """Boat of a specific boat-class."""

    ui_display_sep        = " "

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        ### Primary attributes

        class left (_Ancestor.left) :
            """Boat-class of boat."""

            role_type          = GTW.OMP.SRM.Boat_Class
            role_name          = "b_class"
            ui_name            = "Class"
            ui_allow_new       = True

        # end class left

        class nation (A_Nation) :
            """Country for which the boat is registered."""

            kind               = Attr.Primary_Optional
            example            = "AUT"

        # end class nation

        class sail_number (A_Int) :
            """Sail number of boat (without nation!)"""

            kind               = Attr.Primary
            example            = "2827"
            min_value          = 0
            max_value          = 999999
            needs_raw_value    = True
            completer          = Attr.Completer_Spec  (1, Attr.Selector.primary)
            polisher           = _sail_number_split
            syntax             = """
                This field contains only the numeric part of the sail number,
                not the nation, nor modifiers like `X`!
            """

        # end class sail_number

        class sail_number_x (A_String) :
            """Sail number prefix of boat (e.g., 'X', not the nation code!)."""

            kind               = Attr.Primary_Optional
            example            = "X"
            ignore_case        = "upper"
            max_length         = 8
            completer          = Attr.Completer_Spec  (1, Attr.Selector.primary)
            syntax             = """
                This field contains only additional modifiers `X` but not the
                sailnumber itself or the nation!
            """

        # end class sail_number_x

        ### Non-primary attributes

        class name (A_String) :
            """Name of sailboat."""

            kind               = Attr.Optional
            example            = "Albatross"
            max_length         = 48

        # end class name

    # end class _Attributes

    class _Predicates (_Ancestor_Essence._Predicates) :

        _Ancestor = _Ancestor_Essence._Predicates

        class valid_sail_number_x (Pred.Condition) :
            """`sail_number_x` must not repeat either `nation` or `sail_number`."""

            kind               = Pred.Object
            assertion          = \
              "sail_number_x not in (nation, str (sail_number))"
            attributes         = ("nation", "sail_number", "sail_number_x")

        # end class valid_sail_number_x

    # end class _Predicates

    @property
    def ui_display_format (self) :
        prop = self.attr_prop
        head = result = "%(left)s"
        tail = self.ui_display_sep.join \
            (   "%%(%s)s" % (a.name, )
            for a in
                (prop (n) for n in ("nation", "sail_number_x", "sail_number"))
            if  a.has_substance (self)
            )
        if tail :
            result = ", ".join ((head, tail))
        return result
    # end def ui_display_format

# end class Boat

if __name__ != "__main__" :
    GTW.OMP.SRM._Export ("*")
### __END__ GTW.OMP.SRM.Boat
