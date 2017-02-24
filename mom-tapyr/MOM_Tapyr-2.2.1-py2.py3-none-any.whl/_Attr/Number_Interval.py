# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package MOM.Attr.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    MOM.Attr.Number_Interval
#
# Purpose
#    Factory for composite attribute types modelling an interval of numbers
#
# Revision Dates
#    28-Mar-2012 (CT) Creation (factored from un-DRY `Float_Interval`)
#    29-Mar-2012 (CT) Add `__module__` to `__class__` calls
#    29-Mar-2012 (CT) Rename `new_interval_attr_type` to `make`, add doctest
#    20-Aug-2012 (RS) Fix typo, now `A_Frequency`
#    25-Feb-2013 (CT) Add `query_preconditions` to `center`, `length`
#                     remove `auto_up_depends` from `center`, `length`
#     5-Jun-2013 (CT) Use `is_attr_type`, not home-grown code
#    25-Jun-2013 (CT) Use `__mro__`, not `mro ()`
#     7-Aug-2013 (CT) Set `_Interval_.is_partial` to `True`
#    16-Jun-2014 (RS) Add `A_Int_Interval_C`
#    23-Jun-2014 (RS) Document traceback in `A_Int_Interval_C`
#    24-Jun-2014 (CT) Fix `A_Int_Interval_C.computed__upper`
#    24-Jun-2014 (CT) Force attribute names to `str`
#     4-Sep-2014 (RS) Fix interval limit: `lower` <= `upper` not '<'
#    11-Dec-2015 (CT) Use `attr_types_of_module`, not home-grown code
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

from   __future__            import unicode_literals

from   _MOM.import_MOM       import *
from   _MOM.import_MOM       import _A_Composite_, _A_Number_

from   _TFL.portable_repr    import portable_repr
from   _TFL.pyk              import pyk

import _TFL.Caller

_Ancestor_Essence = MOM.An_Entity

class _Interval_ (_Ancestor_Essence) :
    """Model an interval (lower, upper)."""

    is_partial     = True
    ui_display_sep = " - "

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class lower (_A_Number_) :
            """Lower bound of interval."""

            kind                   = Attr.Necessary

        # end class lower

        class upper (_A_Number_) :
            """Upper bound of interval."""

            kind                   = Attr.Necessary

        # end class upper

        class center (_A_Number_) :
            """Center of interval."""

            kind                   = Attr.Query
            query                  = (Q.lower + Q.upper) * 0.5
            query_preconditions    = (Q.lower, Q.upper)

        # end class center

        class length (_A_Number_) :
            """Length of interval."""

            kind                   = Attr.Query
            query                  = Q.upper - Q.lower
            query_preconditions    = (Q.lower, Q.upper)

        # end class length

    # end class _Attributes

    class _Predicates (_Ancestor_Essence._Predicates) :

        _Ancestor = _Ancestor_Essence._Predicates

        class is_valid (Pred.Condition) :
            """The upper bound must be greater or equal to the lower bound."""

            kind               = Pred.Object
            assertion          = "lower <= upper"
            attributes         = ("lower", "upper")

        # end class is_valid

    # end class _Predicates

# end class _Interval_

def make (bounds_type, name = None) :
    """Make a new composite type and a new attribute type for `bounds_type`.

    >>> Int_Interval, A_Int_Interval = MOM.Attr.Number_Interval.make (A_Int)
    >>> Int_Interval
    <class 'MOM.Int_Interval' [Spec Essence]>
    >>> Int_Interval._Attributes.lower.__mro__ [:2]
    (<class 'Number_Interval.lower'>, <class '_MOM._Attr.Type.A_Int'>)
    >>> print (portable_repr (Int_Interval._Attributes.lower.P_Type))
    <class 'builtins.int'>

    >>> Float_Interval._Attributes.lower.__mro__ [:2]
    (<class 'Number_Interval.lower'>, <class '_MOM._Attr.Type.A_Float'>)
    >>> print (portable_repr (Float_Interval._Attributes.lower.P_Type))
    <class 'builtins.float'>

    >>> Frequency_Interval._Attributes.lower.__mro__ [:2]
    (<class 'Number_Interval.lower'>, <class '_MOM._Attr.Type.A_Frequency'>)
    >>> print (portable_repr (Frequency_Interval._Attributes.lower.P_Type))
    <class 'builtins.float'>

    """
    if name is None and bounds_type.__name__.startswith ("A_") :
        name = bounds_type.__name__ [2:]
    def new_attr (_Attr, attr_name, module) :
        ancestor = getattr (_Attr, attr_name)
        return ancestor.__class__ \
            (attr_name, (bounds_type, ancestor), dict (__module__ = module))
    cls_name    = "%s_Interval" % (name, )
    module      = TFL.Caller.globals () ["__name__"]
    _Attributes = _Interval_._Attributes.__class__ \
        ( "_Attributes"
        , (_Interval_._Attributes, )
        , dict
            (  (str (n), new_attr (_Interval_._Attributes, str (n), module))
            for n in ("lower", "upper", "center", "length")
            )
        )
    Interval_Type =  _Interval_.__class__ \
        ( cls_name, (_Interval_, )
        , dict
            ( _Attributes = _Attributes
            , __doc__ = "Model an interval of %s values (lower, upper)."
                % (name.lower (), )
            , __module__ = module
            )
        )
    A_Interval_Type = _A_Composite_.__class__ \
        ( "A_%s" % (cls_name, ), (_A_Composite_, )
        , dict
            ( P_Type  = Interval_Type
            , typ     = cls_name
            , __doc__ =
                ( "Models an attribute holding a interval of %s "
                  "values (lower, upper)"
                % (name.lower (), )
                )
            , __module__ = module
            )
        )
    return Interval_Type, A_Interval_Type
# end def make

Float_Interval,     A_Float_Interval     = make (A_Float)
Frequency_Interval, A_Frequency_Interval = make (A_Frequency)
Int_Interval,       A_Int_Interval       = make (A_Int)

class A_Int_Interval_C (A_Int_Interval) :
    """Int interval (lower, upper [default: `lower`])."""

    class _Attributes :

        def computed__upper (self, obj) :
            if obj is not None and obj.lower :
                return obj.lower
        # end def computed__upper

        _Overrides = dict \
            ( upper = dict
                ( Kind_Mixins     = (Attr.Computed_Set_Mixin, )
                , computed        = computed__upper
                )
            )

    # end class _Attributes

# end class A_Int_Interval_C

__attr_types       = Attr.attr_types_of_module ()
__sphinx__members = __attr_types + \
    ("_Interval_", "Float_Interval", "Frequency_Interval", "Int_Interval"
    , "make"
    )

if __name__ != "__main__" :
    MOM.Attr._Export (* __attr_types)
    MOM.Attr._Export_Module ()
### __END__ MOM.Attr.Number_Interval
