# -*- coding: utf-8 -*-
# Copyright (C) 2016 Mag. Christian Tanzer All rights reserved
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
#    MOM.Attr.Range
#
# Purpose
#    Attributes types for ranges of specific types
#
# Revision Dates
#     5-Jul-2016 (CT) Creation
#    20-Sep-2016 (CT) Redefine `from_string` to allow `dict` arguments
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _MOM.import_MOM       import *
from   _MOM._Attr.Structured import _A_Structured_

from   _TFL.I18N             import _, _T, _Tn
from   _TFL.pyk              import pyk

import _TFL.Range

class _M_Range_ (_A_Structured_.__class__) :
    """Meta class for MOM.Attr._Range_ classes."""

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        if "C_Type" in dct or "P_Type" in dct :
            C_Type = dct.get ("C_Type")
            P_Type = dct.get ("P_Type")
            if C_Type is None :
                raise MOM.Error.Inconsistent_Attribute \
                    ( "%s: Attribute %s specifies `P_Type` %s"
                      "but no `C_Type`"
                    % (dct ["__module__"], name, P_Type)
                    )
            if P_Type is None :
                raise MOM.Error.Inconsistent_Attribute \
                    ( "%s: Attribute %s specifies `C_Type` %s"
                      "but no `P_Type`"
                    % (dct ["__module__"], name, C_Type)
                    )
        P_Type = getattr (cls, "P_Type", None)
        if P_Type is not None :
            for p in ("finite", "range_pattern") :
                if getattr (cls, p, None) is None :
                    setattr (cls, p, getattr (P_Type, p))
        ### XXX
        ### - max_ui_length
        ### - syntax
    # end def __init__

    def __call__ (cls, kind, e_type) :
        result = cls.__m_super.__call__ (kind, e_type)
        btype  = result.E_Type._Attributes.btype
        if btype.kind is not Attr.Const :
            ### Constrain `btype` to be constant
            ###
            ### If this constraint is lifted, the `op_*` methods of
            ### MOM.DBW.SAW.Attr__Range.Kind_Wrapper_Range need to be adapted
            raise TypeError \
                ( "Non-const attribute `btype` is not supported for %s; "
                  "got kind %s"
                % (result, btype.kind)
                )
        return result
    # end def __call__

# end class _M_Range_

class _A_Range_ (TFL.Meta.BaM (_A_Structured_, metaclass = _M_Range_)) :
    """Base class for range-types attributes of an object."""

    Kind_Mixins         = (MOM.Attr._Range_Mixin_, )
    Q_Ckd_Type          = MOM.Attr.Querier.Range

    class _Attributes (_A_Structured_._Attributes) :

        class btype (A_Enum) :
            """Boundary type of range."""

            C_Type             = A_String
            kind               = Attr.Const
            default            = "[)"
            max_length         = 2
            rank               = 3
            Table              = \
                { "[]" : "inclusive lower, inclusive upper bounds"
                , "[)" : "inclusive lower, exclusive upper bounds"
                , "(]" : "exclusive lower, inclusive upper bounds"
                , "()" : "exclusive lower, exclusive upper bounds"
                }
            typ                = \
            ui_name            = _ ("Boundary type")

        # end class btype

        class lower (A_Attr_Type) :
            """Lower boundary value of range."""

            kind               = Attr.Optional
            rank               = 1

        # end class lower

        class upper (A_Attr_Type) :
            """Upper boundary value of range."""

            kind               = Attr.Optional
            rank               = 2

        # end class upper

    # end class _Attributes

    @TFL.Meta.Class_and_Instance_Once_Property
    def db_sig (self) :
        return \
            ( self.__super.db_sig
            + (self.C_Type and self.C_Type.db_sig, )
            )
    # end def db_sig

    @TFL.Meta.Class_and_Instance_Once_Property_NI
    def default_btype (soc) :
        result = soc._Attributes.btype.default
        if not result :
            result = soc.P_Type.default_btype
        return result
    # end def default_btype

    @TFL.Meta.Class_and_Instance_Method
    def as_string (soc, value) :
        if value is not None :
            C_Type = soc.C_Type
            return "%s%s, %s%s" % \
                ( value.LB.btype
                , C_Type.as_string (value.lower)
                , C_Type.as_string (value.upper)
                , value.UB.btype
                )
        return ""
    # end def as_string

    def as_rest_cargo_ckd (self, obj, * args, ** kw) :
        value = self.kind.get_value (obj)
        if value is not None :
            C_Type = self.C_Type
            result = dict \
                ( lower       = value.lower
                , upper       = value.upper
                , bounds_type = value.btype
                )
            if not issubclass (C_Type, Atomic_Json_Mixin) :
                result.update \
                    ( lower   = C_Type.as_string (value.lower)
                    , upper   = C_Type.as_string (value.upper)
                    )
            return result
    # end def as_rest_cargo_ckd

    @TFL.Meta.Class_and_Instance_Method
    def cooked (soc, value) :
        P_Type = soc.P_Type
        if isinstance (value, pyk.string_types) :
            try :
                value = soc._from_string (value)
            except MOM.Error.Attribute_Syntax :
                raise
            except ValueError :
                msg   = _T ("%s expected, got %r") % (_T (soc.typ), value)
                raise MOM.Error.Attribute_Syntax (None, soc, value, msg)
        elif not isinstance (value, P_Type) :
            raise MOM.Error.Wrong_Type \
                (_T ("Value `%r` is not of type %s") % (value, P_Type))
        return value
    # end def cooked

    @TFL.Meta.Class_and_Instance_Method
    def from_attr_tuple (soc, lower = None, upper = None, btype = None) :
        if btype is None :
            btype = soc.default_btype
        result = soc.P_Type (lower, upper, btype)
        try :
            return soc.set_defaults (lower, upper, btype, result)
        except ValueError as exc :
            raise MOM.Error.Attribute_Syntax \
                (None, soc, result, pyk.text_type (exc))
    # end def from_attr_tuple

    @TFL.Meta.Class_and_Instance_Method
    def from_string (soc, s, obj = None) :
        if isinstance (s, dict) :
            RT     = soc.P_Type
            kw     = \
                {k : RT.bound_from_string (v) for k, v in pyk.iteritems (s)}
            result = soc.from_attr_tuple (** kw)
        else :
            result = super (_A_Range_, soc).from_string (s, obj)
        return result
    # end def from_string

    @TFL.Meta.Class_and_Instance_Method
    def set_defaults (soc, lower, upper, btype, value) :
        A_Type    = soc._Attributes
        P_Type    = soc.P_Type
        default_p = False
        if lower is None :
            lower = soc._default_bound (A_Type.lower, value)
            default_p = default_p or lower is not None
        if upper is None :
            upper = soc._default_bound (A_Type.upper, value)
            default_p = default_p or upper is not None
        if btype is None :
            btype = soc.default_btype
        elif btype != soc.default_btype :
            raise ValueError \
                ( "Wrong bounds_type: expected %s; got %s"
                % (btype, soc.default_btype)
                )
        result = P_Type (lower, upper, btype) if default_p else value
        return result
    # end def set_defaults

    @TFL.Meta.Class_and_Instance_Method
    def _default_bound (soc, attr, value) :
        if TFL.callable (attr.computed) :
            result = attr.computed (value)
        elif TFL.callable (attr.computed_default) :
            result = attr.computed_default ()
        else :
            result = attr.default
        return result
    # end def _default_bound

    @TFL.Meta.Class_and_Instance_Method
    def _from_string (soc, s, obj = None) :
        s = s.strip ()
        if s :
            P_Type = soc.P_Type
            args   = P_Type.args_from_string (s)
            if not args :
                ### ??? allow other input formats
                raise MOM.Error.Attribute_Syntax (obj, soc, s)
            else :
                try :
                    return soc.from_attr_tuple (* args)
                except MOM.Error.Attribute_Syntax as exc :
                    raise MOM.Error.Attribute_Syntax \
                        (obj, soc, s, exc.exc_str)
    # end def _from_string

# end class _A_Range_

class A_Int_Range (_A_Range_) :
    """Integer range."""

    C_Type         = A_Int
    P_Type         = TFL.Int_Range
    example        = "[1, 5]"
    typ            = _ ("Int_Range")

    class _Attributes (_A_Range_._Attributes) :

        _Ancestor = _A_Range_._Attributes

        class btype (_Ancestor.btype) :

            default            = "[]"

        # end class btype

        class lower (_Ancestor.lower, A_Int) :

            pass

        # end class lower

        class upper (_Ancestor.upper, A_Int) :

            pass

        # end class upper

    # end class _Attributes

# end class A_Int_Range

class A_Int_Range_C (A_Int_Range) :
    """Integer range [lower, upper]; default for `upper`: `lower`."""

    class _Attributes (A_Int_Range._Attributes) :

        _Ancestor = A_Int_Range._Attributes

        class upper (_Ancestor.upper) :

            @TFL.Meta.Class_and_Instance_Method
            def computed (soc, range) :
                if range is not None and range.lower is not None :
                    return range.lower
            # end def computed

        # end class upper

    # end class _Attributes

# end class A_Int_Range_C

__sphinx__members = __all__ = __attr_types = attr_types_of_module ()

_test_cooked = r"""
    >>> b = A_Int_Range.cooked ("[1, 4]")
    >>> print (A_Int_Range.as_string (b))
    [1, 4]

    >>> c = A_Int_Range.cooked ("[1, ]")
    >>> print (A_Int_Range.as_string (c))
    [1, ]

    >>> cc = A_Int_Range_C.cooked ("[1, ]")
    >>> print (A_Int_Range.as_string (cc))
    [1, 1]

    >>> with expect_except (MOM.Error.Attribute_Syntax) :
    ...     a = A_Int_Range.cooked ("(1, 3)")
    Attribute_Syntax: `Wrong bounds_type: expected (); got []` for : `<class 'Range.A_Int_Range'>`
         expected type  : 'Int_Range'
         got      value : '(1, 3)'

"""

__test__ = dict \
    ( test_cooked = _test_cooked
    )

if __name__ != "__main__" :
    MOM.Attr._Export (* __attr_types)

    @MOM._Add_Import_Callback ("_MOM._DBW._SAW.Attr")
    def _import_saw (module) :
        import _MOM._DBW._SAW.Attr__Range
    # end def _import_saw

    @MOM._Add_Import_Callback ("_MOM._DBW._SAW._PG.Attr")
    def _import_saw (module) :
        import _MOM._DBW._SAW._PG.Attr__Range
    # end def _import_saw
### __END__ MOM.Attr.Range
