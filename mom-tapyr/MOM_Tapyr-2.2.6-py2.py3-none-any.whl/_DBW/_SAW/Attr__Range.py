# -*- coding: utf-8 -*-
# Copyright (C) 2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package MOM.DBW.SAW.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    MOM.DBW.SAW.Attr__Range
#
# Purpose
#    Range-attribute handling for SAW
#
# Revision Dates
#    20-Jul-2016 (CT) Creation
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _MOM                       import MOM
from   _TFL                       import TFL
from   _TFL.pyk                   import pyk

import _MOM._DBW._SAW.QX

import _MOM._Attr.Range
import _MOM._Attr.Range_DT

from   _MOM._DBW._SAW             import QX, SAW, SA

from   _TFL._Meta.Single_Dispatch import Single_Dispatch_Method

import _TFL._Meta.Object
import _TFL.Decorator

import itertools
import operator

class Kind_Wrapper_Range \
          ( SAW.Attr._Kind_Wrapper_C_
          , SAW.Attr._Kind_Wrapper_Field_Extractor_
          ) :
    """SAW specific information about an range-attribute kind
       descriptor in the context of a specific E_Type_Wrapper
    """

    fields = set (("lower", "upper"))
    op_map = dict \
        ( __eq__        = TFL.Getter.op_cmp
        , __ge__        = TFL.Getter.op_cmp
        , __gt__        = TFL.Getter.op_cmp
        , __le__        = TFL.Getter.op_cmp
        , __lt__        = TFL.Getter.op_cmp
        , __ne__        = TFL.Getter.op_ne
        , contains      = TFL.Getter.op_contains
        , in_           = TFL.Getter.op_in
        , overlaps      = TFL.Getter.op_overlaps
        )

    @TFL.Meta.Once_Property
    def columns (self) :
        result = sorted \
            (self.__super.columns, key = lambda c : c.MOM_Kind.attr.rank)
        return result
    # end def columns

    def op_cmp (self, lhs, op_name, rhs) :
        AND    = SA.sql.and_
        op     = getattr (operator, op_name)
        if rhs.is_value :
            raise TypeError \
                ("%s doesn't allow non-range rhs-arguments" % (op_name,))
        else :
            result = AND \
                ( op (lhs.lower, rhs.lower)
                , op (lhs.upper, rhs.upper)
                )
        return result
    # end def op_cmp

    def op_contains (self, lhs, op_name, rhs) :
        AND    = SA.sql.and_
        OR     = SA.sql.or_
        ll, lu = lhs.lower, lhs.upper
        if rhs.is_value :
            attr       = self.attr
            l_range    = attr.P_Type (ll, lu, attr.default_btype)
            l_LB, l_UB = l_range.LB, l_range.UB
            value      = rhs.value
            return AND \
                ( OR (ll == None, l_LB.contains_op (ll, value))
                , OR (lu == None, l_UB.contains_op (lu, value))
                )
        else :
            rl, ru = rhs.lower, rhs.upper
            return AND \
                ( OR (ll == None, ll <= rl)
                , OR (lu == None, lu >= ru)
                )
    # end def op_contains

    def op_in (self, lhs, op_name, rhs) :
        AND  = SA.sql.and_
        OR   = SA.sql.or_
        Null = SA.expression.Null
        if rhs.is_value :
            raise TypeError ("IN doesn't allow non-range arguments")
        else :
            ll, lu = lhs.lower, lhs.upper
            rl, ru = rhs.lower, rhs.upper
            result = AND \
                ( True if rl is None else OR (rl == Null, ll >= rl)
                , True if ru is None else OR (ru == Null, lu <= ru)
                )
            return result
    # end def op_in

    def op_ne (self, lhs, op_name, rhs) :
        return SA.sql.not_ (self.op_cmp (lhs, "__eq__", rhs))
    # end def op_ne

    def op_overlaps (self, lhs, op_name, rhs) :
        if lhs.is_value or rhs.is_value :
            raise TypeError ("overlaps doesn't allow non-range arguments")
        AND        = SA.sql.and_
        OR         = SA.sql.or_
        attr       = self.attr
        ll, lu     = lhs.lower, lhs.upper
        rl, ru     = rhs.lower, rhs.upper
        l_range    = attr.P_Type (ll, lu, attr.default_btype)
        r_range    = attr.P_Type (rl, ru, attr.default_btype)
        l_LB, l_UB = l_range.LB, l_range.UB
        r_LB, r_UB = r_range.LB, r_range.UB
        return OR \
            ( AND (l_LB.contains_op  (ll, rl), l_UB.contains_op  (lu, rl))
            , AND (l_LB.contains_op  (ll, ru), l_UB.contains_op  (lu, ru))
            , AND (r_LB.contains_rop (ll, rl), r_UB.contains_rop (ll, ru))
            , AND (r_LB.contains_rop (lu, rl), r_UB.contains_rop (lu, ru))
            )
    # end def op_overlaps

    def row_as_pickle_cargo (self, row) :
        result = self.__super.row_as_pickle_cargo (row)
        return (result, )
    # end def row_as_pickle_cargo

    def _attr_e_type_wrapper (self, ETW, e_type) :
        try :
            result = ETW.ATW [e_type]
        except KeyError :
            ETW.DBW.etype_decorator (e_type)
            result = ETW.ATW [e_type]
        return result
    # end def _attr_e_type_wrapper

# end class Kind_Wrapper_Range

class _QX_Operand_Proxy_ (TFL.Meta.Object) :

    col_values = None
    is_akw     = is_range = is_value = False

    def __init__ (self, akw, entity) :
        self.akw    = akw
        self.entity = entity
        P_Type      = akw.attr.P_Type
        if isinstance (entity, _QX_Range_) :
            self.col_values = cols = entity._akw.columns
            self.is_akw     = True
            for c in cols :
                self._set_col_value (c, c)
        else :
            range = entity
            if isinstance (range, pyk.string_types) :
                range = P_Type.from_string (range)
            elif isinstance (range, tuple) :
                range = P_Type.from_attr_tuple (* range)
            if isinstance (range, P_Type) :
                def _gen_col_values () :
                    for c in akw.columns :
                        v = getattr (range, c.MOM_Wrapper.attr.name)
                        self._set_col_value (c, v)
                        yield v
                self.col_values = list (_gen_col_values ())
                self.is_range   = True
            else :
                self.is_value   = True
                self.value      = entity
    # end def __init__

    def _set_col_value (self, c, v) :
        setattr (self, c.name, v)
        setattr (self, c.MOM_Wrapper.attr.name, v)
    # end def _set_col_value

# end class _QX_Operand_Proxy_

class _QX_Operator_Proxy_ (TFL.Meta.Object) :

    def __init__ (self, qx, akw, name, op) :
        self.qx    = qx
        self.akw   = akw
        self.name  = name
        self.op    = op
    # end def __init__

    def __call__ (self, lhs, rhs) :
        akw = self.akw
        l   = _QX_Operand_Proxy_ (akw, lhs)
        r   = _QX_Operand_Proxy_ (akw, rhs)
        return self.op (l, self.name, r)
    # end def __call__

# end class _QX_Operator_Proxy_

class _QX_Call_Proxy_ (_QX_Operator_Proxy_) :
    """Proxy for a Range method call"""

    def __call__ (self, lhs, rhs) :
        if not isinstance (rhs, lhs.__class__) :
            rhs = self.qx._xs_filter_rhs (rhs)
        return self.__super.__call__ (lhs, rhs)
    # end def __call__

# end class _QX_Call_Proxy_

class _QX_Bin_Proxy_ (_QX_Operator_Proxy_) :
    """Proxy for a binary Range operator"""

# end class _QX_Bin_Proxy_

@TFL.Add_To_Class ("QX", Kind_Wrapper_Range)
class _QX_Range_ (QX._Attr_CS_) :
    """QX mapper base class for Range attributes"""

    @TFL.Meta.Once_Property
    def XS_FILTER (self) :
        NOT        = SA.sql.not_
        akw        = self._akw
        attr       = akw.attr
        l, u       = akw.columns
        range      = attr.P_Type (l, u, attr.default_btype)
        l_LB, l_UB = range.LB, range.UB
        return NOT (l_LB.contains_op (l, u))
    # end def XS_FILTER

    @TFL.Meta.Once_Property
    def _columns (self) :
        return self._akw.columns
    # end def _columns

    @TFL.Meta.Once_Property
    def _columns_ob (self) :
        return self._akw.columns
    # end def _columns_ob

    @Single_Dispatch_Method
    def _op_bin (self, rhs, name, op, reverse) :
        akw = self._akw
        if name not in akw.op_map :
            return self.__super._op_bin (rhs, name, op, reverse)
        else :
            op_getter = akw.op_map [name]
            op_name   = op_getter  (akw)
            op_proxy  = _QX_Bin_Proxy_ (self, akw, name, op_name)
            result    = QX.Bin (self, name, op_proxy, rhs, reverse)
            return result
    # end def _op_bin

    def _op_call (self, name, op, * args, ** kw) :
        akw = self._akw
        if name not in akw.op_map :
            return self.__super._op_call (name, op, * args, ** kw)
        else :
            op_getter = akw.op_map [name]
            op_name   = op_getter  (akw)
            op_proxy  = _QX_Call_Proxy_ (self, akw, name, op_name)
            result    = QX.Call (self, name, op_proxy, * args, ** kw)
            return result
    # end def _op_call

    def _xs_filter_bin (self, rhs, op, reversed = False) :
        if not isinstance (rhs, self.__class__) :
            rhs = self._xs_filter_rhs (rhs)
        if isinstance (rhs, SA.expression.Null) :
            return None
        return op.apply (self, rhs, reversed)
    # end def _xs_filter_bin

    def _xs_filter_una (self, lhs, op) :
        if self is lhs :
            return op.apply (lhs)
        else :
            return self.__super._xs_filter_una (lhs, op)
    # end def _xs_filter_una

# end class _QX_Range_

@TFL.Add_To_Class ("_saw_bool", MOM.Attr._A_Range_)
@Single_Dispatch_Method (T = SAW.Manager.__class__)
def _saw_bool_range (self, DBW, col) :
    pass
# end def _saw_bool_range

@TFL.Add_To_Class ("_saw_extract_field", MOM.Attr._A_Range_)
@Single_Dispatch_Method (T = SAW.Manager.__class__)
def _saw_extract_field_Range (self, DBW, col, field) :
    ### all valid `field` names are handled by `_QX_Range_._get_attr`
    raise AttributeError (field)
# end def _saw_extract_field_Range

@TFL.Add_To_Class ("_saw_kind_wrapper", MOM.Attr._A_Range_)
@Single_Dispatch_Method (T = SAW.Manager.__class__)
def _saw_kind_wrapper_Range (self, DBW, ETW, kind, ** kw) :
    return Kind_Wrapper_Range (ETW, kind, ** kw)
# end def _saw_kind_wrapper_Range

if __name__ != "__main__" :
    MOM.DBW.SAW._Export_Module ()
### __END__ MOM.DBW.SAW.Attr__Range
