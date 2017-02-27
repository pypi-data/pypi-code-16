# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Mag. Christian Tanzer All rights reserved
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
#    MOM.DBW.SAW.QX
#
# Purpose
#    Adapt q-expressions to SQLAlchemy
#
# Revision Dates
#    30-Aug-2013 (CT) Creation
#    ...
#    25-Sep-2013 (CT) Continue creation...
#    26-Sep-2013 (CT) Redefine `Kind_Query._op_bin`, `_op_call`, `_op_una`
#    26-Sep-2013 (CT) Change `_add_join_parent` to honor `_polymorphic`
#    26-Sep-2013 (CT) Add optional arg `polymorphic` to `_add_join_parent`,
#                     `_add_joins_col`, `_add_joins_inner`
#    30-Sep-2013 (CT) Add support for `Q.SELF`
#     7-Oct-2013 (CT) Change `Kind_Rev_Query._ref_etw_col` to pass
#                     `akw.ETW.spk_col`, not `self.ETW.spk_col`, to
#                     `_add_joins_col`
#     7-Oct-2013 (CT) Change `_fixed_q_exp_get_` to reset `Ignore_Exception`;
#                     ditto for `_fixed_q_exp_get_raw_`
#    10-Oct-2013 (CT) Use `coalesce` and `label` in `_SUM_.apply`
#    10-Oct-2013 (CT) Add `Q` to `_Q_SUM_Proxy_`
#    11-Oct-2013 (CT) Generalize `_SUM_` to `_Aggr_`,
#                     `_Q_SUM_Proxy_` to `_Q_Aggr_Proxy_`
#    27-Jan-2014 (CT) Change `_Base_._xs_filter_rhs` to call `pickler.as_cargo`,
#                     if any
#    31-Jan-2014 (CT) Add support for `__{true,floor}div__` to `Bin.apply`
#     6-Mar-2014 (CT) Change `Kind_Composite._xs_filter_bin` to
#                     delegate `to lqx._xs_filter_bin`
#     6-Mar-2014 (CT) Add cache for `Kind_Composite._get_attr` results
#     2-Apr-2014 (CT) Fix `_xs_filter_una` to use `op._xs_filter_una_delegate`,
#                     not `self._xs_filter_una_delegate`
#     2-Apr-2014 (CT) Redefine `Una._xs_filter_una_delegate` to return
#                     `XS_FILTER` for `NOT`, `_XS_FILTER` for all other
#                     unary operators
#     3-Apr-2014 (CT) Use `LEFT OUTER` joins for `Kind_Rev_Query`
#     3-Apr-2014 (CT) Save `_SAW_ORIGINAL` in `Una.XS_ORDER_BY`
#    16-Apr-2014 (CT) Add `And_Distributive` and `Or_Distributive`
#    16-Apr-2014 (CT) Add `Q.NIL`
#    26-Aug-2014 (CT) Factor `_attr_kind_wrapper_and_col`, use in
#                     `Kind_EPK._get_attr` (to support `__raw_«name»`)
#    10-Sep-2014 (CT) Add support for type restriction
#                     + `Kind_EPK.__getitem__`
#                     + `_Kind_EPK_Restricted_`, `_Kind_Partial_Restricted_`
#                     + `_Q_ETR_Proxy_`, `_fixed_q_exp_get_etr_ `
#    12-Sep-2014 (CT) Use `A_Join.key`, not `A_Join.table`, for `_join_set`
#    12-Sep-2014 (CT) Add `_polymorphic_x`
#    12-Sep-2014 (CT) Add `_Bool_Distributive_.__getattr__`, `.__getitem__`
#    12-Sep-2014 (CT) Add `_etw_alias` to `Kind_EPK.__getitem__` and
#                     `_Kind_Partial_Restricted_._children`
#    23-Sep-2014 (CT) Use `_polymorphic_x` in `_add_joins_col` and
#                     `_add_join_parent`, too
#    10-Oct-2014 (CT) Protect access to `operator.__div__`
#                     (hack only needed for Python 2, anyway)
#    10-Oct-2014 (CT) Use `TFL.Q_Exp._Una_.name_map` to get operator names
#     7-Oct-2015 (CT) Fix `operator.__div__` handling for Python 3, too
#     8-Oct-2015 (CT) Change `__getattr__` to *not* handle `__XXX__`
#    21-Jul-2016 (CT) Add `_xs_filter_rhs_q_exp_`
#     2-Aug-2016 (CT) Factor `_Attr_CS_` from `Kind_Composite`
#     3-Aug-2016 (CT) Add `Kind_Structured_Field_Extractor`, factor `_Attr_S_`
#                     + add `_Attr_S_Field_Extractor_`
#    22-Sep-2016 (CT) Add call to `_saw_cooked` to `_Base_._xs_filter_rhs`
#    23-Sep-2016 (CT) Change `_Base_._xs_fixed_bool` to consider `Function` too
#    23-Sep-2016 (CT) Factor `_extract_field`, add `MOM_Kind` to its `result`
#     6-Oct-2016 (CT) Add `getattr_safe` to `Once_Property`
#     6-Oct-2016 (CT) Change `_Self_._attr` to return attr-type, not -kind
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _MOM                       import MOM
from   _TFL                       import TFL
from   _TFL.pyk                   import pyk

from   _MOM._DBW._SAW             import SAW, SA
from   _MOM.SQ                    import Q

import _MOM._DBW._SAW.Attr
import _MOM._DBW._SAW.Q_Result

from   _TFL._Meta.Single_Dispatch import Single_Dispatch, Single_Dispatch_Method
from   _TFL.Decorator             import getattr_safe
from   _TFL.predicate             import cartesian, split_hst

import _TFL._Meta.Object
import _TFL._Meta.Once_Property
import _TFL.Accessor
import _TFL.Decorator
import _TFL.Filter
import _TFL.Sorted_By
import _TFL.Undef

import itertools
import operator

TFL._Filter_.predicate_precious_p = True

def _attr_kind_wrapper_and_col (ETW, name) :
    col = None
    try :
        result = ETW.q_able_attrs [name]
    except KeyError as exc :
        ### raw names aren't in `.q_able_attrs`, but they are in `.QC`
        try :
            col = ETW.QC [name]
        except KeyError as exc :
            raise TypeError \
                ("Unknown attribute `%s` for %s" % (name, ETW.type_name))
        else :
            result = col.MOM_Wrapper
    return result, col
# end def _attr_kind_wrapper_and_col

@TFL.dict_from_class
class _Op_Map_ (object) :
    """Some functions need special handling"""

    ### the TFL.Q_Exp method implementing `between` contains code
    ### that doesn't map to SQL (inline boolean expression, doh!)
    def between (val, lhs, rhs) :
        return SA.expression.and_ (val != None, lhs <= val, val <= rhs)
    # end def between

    ### `operator.contains` cannot be applied to column objects
    def contains (val, rhs) :
        return val.contains (rhs)
    # end def contains

    ### the TFL.Q_Exp method implementing `in_` contains code
    ### that doesn't map to SQL (inline boolean expression, doh!)
    def in_ (val, rhs) :
        if isinstance (rhs, SAW.Q_Result._Base_) :
            rhs = rhs.sa_query
        elif isinstance (rhs, (list, tuple)) and not rhs :
            return False
        return val.in_ (rhs)
    # end def in_

# end class _Op_Map_

class _RAW_ (TFL.Meta.Object) :

    class _Attribute_Faker_ (object) :
        def __contains__ (self, item) :
            return True
        # end def __contains__
    # end class _Attribute_Faker_

    @TFL.Meta.Once_Property
    def attributes (self) :
        return self._Attribute_Faker_ ()
    # end def attributes

    def raw_attr (self, key) :
        result = getattr (self, "RAW.%s" % (key, ))
        return result
    # end def raw_attr

# end class _RAW_

class Mapper (_RAW_) :
    """Map a generic query expression into a SQLAlchemy specific
       expression.

       An instance of `Mapper` is related to a specific
       :class:`Q_Result<_MOM._DBW._SAW.Q_Result.Q_Result>` instance.
       When called with a generic query expression as argument,
       the mapper instance will evaluate the query expression and
       return a SQLAlchemy specific expression that is an instance of
       the appropriate subclass of :class:`_Base_`.
    """

    _is_raw               = False
    _outer                = None
    _polymorphic_x        = None

    def __init__ (self, QR, ETW = None) :
        self.QR           = QR
        self.ETW          = ETW if ETW is not None else QR.ETW
        self._polymorphic = QR.polymorphic
        self._joins       = []
        self._join_set    = set ()
    # end def __init__

    def __call__ (self, x) :
        """Map TFL.Q_Exp instance `x` to the appropriate QX instance"""
        fx     = fixed_q_exp (x)
        result = fx (self)
        return result
    # end def __call__

    @TFL.Meta.Once_Property
    def E_Type (self) :
        return self.ETW.e_type
    # end def E_Type

    def REF ( self, ETW
            , _is_raw         = False
            , _polymorphic    = False
            , _polymorphic_x  = None
            ) :
        result                = self.__class__ (self.QR, ETW)
        result._is_raw        = self._is_raw        or _is_raw
        result._polymorphic   = self._polymorphic   or _polymorphic
        result._polymorphic_x = self._polymorphic_x or _polymorphic_x
        result._joins         = self._joins
        result._join_set      = self._join_set
        return result
    # end def REF

    def _add_joins (self, * joins) :
        _joins    = self._joins
        _join_set = self._join_set
        for j in joins :
            table = j.table
            if j.key not in _join_set :
                _join_set.add (j.key)
                _joins.append (j)
    # end def _add_joins

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        ETW = self.ETW
        head, _, tail = split_hst (name, ".")
        is_raw = head == "RAW"
        if is_raw :
            head, _, tail = split_hst (tail, ".")
        akw, col = _attr_kind_wrapper_and_col (ETW, head)
        if col is not None :
            is_raw = is_raw or col.MOM_Is_Raw
        result = akw.QX (self, akw, _is_raw = is_raw, _outer = self._outer)
        if tail :
            result = getattr (result, tail)
        return result
    # end def __getattr__

    def __repr__ (self) :
        return "<QX.Mapper for %s>" % (self.ETW.type_name, )
    # end def __repr__

# end class Mapper

def _add_bin_op (cls, name, op, reverse) :
    def _ (self, rhs) :
        return self._op_bin (rhs, name, op, reverse)
    _.__doc__    = op.__doc__
    _.__name__   = name
    setattr (cls, name, _)
# end def _add_bin_op

def _add_call_op (cls, name, op) :
    def _ (self, rhs, * args, ** kw) :
        return self._op_call (name, op, rhs, * args, ** kw)
    _.__doc__    = op.__doc__
    _.__name__   = name
    _._op        = op
    setattr (cls, name, _)
# end def _add_call_op

def _add_una_op (cls, name, op) :
    op_name = op.__name__
    sq_op   = op if name == op_name else getattr (operator, name)
    sq_name = TFL.Q_Exp._Una_.name_map.get (op_name, name)
    def _ (self) :
        return self._op_una (sq_name, sq_op)
    _.__doc__    = sq_op.__doc__
    _.__name__   = sq_name
    setattr (cls, name, _)
# end def _add_una_op

def _add_operators (cls) :
    for name, (op, reverse) in pyk.iteritems (TFL.Q_Exp._Bin_.Table) :
        _add_bin_op  (cls, name, op, reverse)
    for name, op in pyk.iteritems (TFL.Q_Exp._Call_.Table) :
        _add_call_op (cls, name, op)
    for name, op in pyk.iteritems (TFL.Q_Exp._Una_.Table) :
        _add_una_op  (cls, name, op)
    return cls
# end def _add_operators

class _Q_Exp_Proxy_ (TFL.Meta.Object) :
    """Mixin for classes that masquerade as TFL.Q_Exp instances"""

    def __call__ (self, item, * args, ** kw) :
        """Called during execution of Mapper.__call__ to map a TFL.Q_Exp
           instance to a QX-specific instance.
        """
        return self.predicate (item, * args, ** kw)
    # end def __call__

# end class _Q_Exp_Proxy_

class _Q_Aggr_Proxy_ (_Q_Exp_Proxy_) :
    """Proxy for a TFL.Q._Aggr_ instance"""

    def __init__ (self, op_name, Q, rhs) :
        self.op_name = op_name
        self.Q       = Q
        self.rhs     = rhs
    # end def __init__

    def predicate (self, qx) :
        """Called during execution of Mapper.__call__ to map a Q._Call_
           instance to a QX-specific instance.
        """
        try :
            rhs = qx (self.rhs)
        except Exception :
            rhs = self.rhs
        return _Aggr_ (qx, rhs, self.op_name)
    # end def predicate

# end class _Q_Aggr_Proxy_

class _Q_Call_Proxy_ (_Q_Exp_Proxy_) :
    """Proxy for a TFL.Q._Call_ instance"""

    def __init__ (self, lhs, op, * args, ** kw) :
        self.lhs    = lhs
        self.op     = op
        self.args   = args
        self.kw     = kw
    # end def __init__

    def predicate (self, qx) :
        """Called during execution of Mapper.__call__ to map a Q._Call_
           instance to a QX-specific instance.
        """
        lhs  = qx (self.lhs)
        op   = self.op
        name = op.__name__
        op   = _Op_Map_.get (name, op)
        return lhs._op_call (name, op, * self.args, ** self.kw)
    # end def predicate

# end class _Q_Call_Proxy_

class _Q_ETR_Proxy_ (_Q_Exp_Proxy_) :
    """Proxy for a MOM.Q._Get_._E_Type_Restriction_ instance"""

    def __init__ (self, q_etr) :
        self.Q           = q_etr.Q
        self.head_getter = q_etr._head_getter
        self.tail_getter = q_etr._tail_getter
        self.type_name   = q_etr._type_name
    # end def __init__

    def predicate (self, qx) :
        """Called during execution of Mapper.__call__ to map a
            Q._Get_._E_Type_Restriction_ instance to a QX-specific instance.
        """
        hg     = self.head_getter
        tg     = self.tail_getter
        tn     = self.type_name
        result = qx (hg) [tn]
        if tg is not None :
            result = tg (result)
        return result
    # end def predicate

# end class _Q_ETR_Proxy_

class _Q_NIL_Proxy_ (Q._NIL_) :
    """Proxy for a Q.NIL expression"""

    def predicate (self, obj) :
        if isinstance (obj, Mapper) :
            return _NIL_ (obj)
        return None
    # end def predicate

# end class _Q_NIL_Proxy_

class _Q_Self_Proxy_ (Q._Self_) :
    """Proxy for a Q.SELF expression"""

    def predicate (self, obj) :
        if isinstance (obj, Mapper) :
            return _Self_ (obj)
        return obj
    # end def predicate

# end class _Q_Self_Proxy_

@_add_operators
class _Base_ (TFL.Meta.Object) :
    """Base class for SQLAlchemy specific expression nodes.

       All SQLAlchemy specific expression nodes provide the
       properties:

       * :attr:`JOINS`: the joins necessary for the evaluation of the query
         expression.

       * :attr:`XS_ATTR`: SQLAlchemy specific query expressions usable
         for the `.attr` and `.attrs` methods of a
         :class:`Q_Result<_MOM._DBW._SAW.Q_Result.Q_Result>` instance.

         These can be used as arguments for a call to the SQLAlchemy
         method `select_from`.

       * :attr:`XS_FILTER`: SQLAlchemy specific query expressions usable
         for the `.filter` method of a
         :class:`Q_Result<_MOM._DBW._SAW.Q_Result.Q_Result>` instance.

         These can be used as arguments for a call to the SQLAlchemy
         method `where`.

       * :attr:`XS_GROUP_BY`: SQLAlchemy specific query expressions usable
         for the `.group_by` method of a
         :class:`Q_Result<_MOM._DBW._SAW.Q_Result.Q_Result>` instance.

         These can be used as arguments for a call to the SQLAlchemy
         method `group_by`.

       * :attr:`XS_ORDER_BY`: SQLAlchemy specific query expressions usable
         for the `.order_by` method of a
         :class:`Q_Result<_MOM._DBW._SAW.Q_Result.Q_Result>` instance.

         These can be used as arguments for a call to the SQLAlchemy
         method `order_by`.

       The most important classes derived from `_Base_` are:

       .. autoclass:: _Attr_()
       .. autoclass:: Kind()
       .. autoclass:: Kind_Composite()
       .. autoclass:: Kind_EPK()
       .. autoclass:: Kind_Partial()
       .. autoclass:: Kind_Query()
       .. autoclass:: Kind_Rev_Query()
       .. autoclass:: Bin()
       .. autoclass:: Call()
       .. autoclass:: Func()
       .. autoclass:: Una()

    """

    exclude_constraint_op   = "="

    undef                   = TFL.Undef ("arg")

    _field                  = None
    _is_raw                 = False
    _qx_attr                = None
    _XS_FILTER              = TFL.Meta.Alias_Property ("XS_FILTER")
    _xs_filter_una_delegate = "_XS_FILTER"

    @property
    def JOINS (self) :
        return self.X._joins
    # end def JOINS

    @TFL.Meta.Once_Property
    def QR (self) :
        return self.X.QR
    # end def QR

    @TFL.Meta.Once_Property
    def _columns (self) :
        return []
    # end def _columns

    @TFL.Meta.Once_Property
    def _columns_ob (self) :
        return self._columns
    # end def _columns_ob

    @TFL.Meta.Once_Property
    def _xtra_qxs (self) :
        return []
    # end def _xtra_qxs

    @Single_Dispatch_Method
    def _op_bin (self, rhs, name, op, reverse) :
        return Bin (self, name, op, rhs, reverse)
    # end def _op_bin

    def _op_call (self, name, op, * args, ** kw) :
        return Call (self, name, op, * args, ** kw)
    # end def _op_call

    def _op_una (self, name, op) :
        return Una (self, name, op)
    # end def _op_una

    def _xs_filter_bin (self, rhs, op, reversed = False) :
        rhs = self._xs_filter_rhs (rhs)
        if isinstance (rhs, SA.expression.Null) :
            return None
        return op.apply (self._XS_FILTER, rhs, reversed)
    # end def _xs_filter_bin

    def _xs_filter_expression (self, * fs) :
        extras = (qx.XS_FILTER for qx in self._xtra_qxs)
        xs     = tuple (itertools.chain (extras, fs))
        return xs [0] if len (xs) == 1 else SA.expression.and_ (* xs)
    # end def _xs_filter_expression

    @Single_Dispatch_Method
    def _xs_filter_rhs (self, rhs) :
        DBW    = self.QR.ETW.DBW
        result = rhs
        qxa    = self._qx_attr
        if qxa is not None and self._field is None :
            attr    = qxa._attr
            pickler = attr.Pickler
            if qxa._is_raw :
                if not attr.needs_raw_value :
                    result = attr.from_string (result)
            elif isinstance (result, pyk.string_types) :
                if attr.P_Type not in pyk.string_types :
                    result = attr.cooked (result)
            if isinstance (result, (MOM.Id_Entity, MOM.MD_Change)) :
                result = result.spk
            elif pickler and not qxa._field :
                result = pickler.as_cargo (attr.kind, attr, result)
            result = attr._saw_cooked (DBW, result)
        return result
    # end def _xs_filter_rhs

    @_xs_filter_rhs.add_type (MOM.Id_Entity, MOM.MD_Change)
    def _xs_filter_rhs_spk_ (self, rhs) :
        return rhs.spk
    # end def _xs_filter_rhs_spk_

    @_xs_filter_rhs.add_type (TFL.Q_Exp.Q_Root)
    def _xs_filter_rhs_q_exp_ (self, rhs) :
        return self.X (rhs)
    # end def _xs_filter_rhs_q_exp_

    @_xs_filter_rhs.add_type (SAW.Q_Result._Base_)
    def _xs_filter_rhs_q_result_ (self, rhs) :
        return rhs.sa_query
    # end def _xs_filter_rhs_q_result_

    def _xs_filter_una (self, lhs, op) :
        if isinstance (lhs, SAW.Q_Result._Base_) :
            lhs = lhs.sa_query
        else :
            lhs = getattr (lhs, op._xs_filter_una_delegate, lhs)
        return op.apply (lhs)
    # end def _xs_filter_una

    def _xs_fixed_bool (self, xs) :
        DBW = self.QR.ETW.DBW
        for x in xs :
            if isinstance (x, (SA.schema.Column, SA.sql.functions.Function)) :
                try :
                    ak = x.MOM_Kind
                except AttributeError :
                    pass
                else :
                    x = ak._saw_bool (DBW, x)
            yield x
    # end def _xs_fixed_bool

# end class _Base_

@_Base_._xs_filter_rhs.add_type (_Base_)
def _xs_filter_rhs_QX_ (self, rhs) :
    return rhs._XS_FILTER
# end def _xs_filter_rhs_QX_

class _BVAR_ (_Base_, Q.BVAR.BVAR) :
    """Map a reference to a bound variable to a SQLAlchemy bound variable."""

    @TFL.Meta.Once_Property
    def XS_ATTR (self) :
        raise TypeError \
            ( "Cannot use BVAR for attr: %s"
            % (self, )
            )
    # end def XS_ATTR

    @TFL.Meta.Once_Property
    def XS_FILTER (self) :
        return SA.sql.bindparam (self._name)
    # end def XS_FILTER

    @TFL.Meta.Once_Property
    def XS_GROUP_BY (self) :
        raise TypeError \
            ( "Cannot use BVAR for group_by: %s"
            % (self, )
            )
    # end def XS_GROUP_BY

    @TFL.Meta.Once_Property
    def XS_ORDER_BY (self) :
        raise TypeError \
            ( "Cannot use BVAR for order_by: %s"
            % (self, )
            )
    # end def XS_ORDER_BY

    def predicate (self, X) :
        """Called during execution of Mapper.__call__ to map a TFL.Q_Exp
           instance to a QX-specific instance.
        """
        self.X = X
        X.QR.bvar_man.add (self)
        return self
    # end def predicate

# end class _BVAR_

class _Bool_ (_Q_Exp_Proxy_, _Base_) :

    _polymorphic_x        = None

    def __init__ (self, predicates) :
        self.predicates = predicates
    # end def __init__

    @TFL.Meta.Once_Property
    @getattr_safe
    def X (self) :
        return self.predicates [0].X
    # end def X

    @TFL.Meta.Once_Property
    def XS_ATTR (self) :
        raise TypeError \
            ( "Cannot use %s operator for attr/attrs: %s"
            % (self.name, self)
            )
    # end def XS_ATTR

    @TFL.Meta.Once_Property
    @getattr_safe
    def XS_FILTER (self) :
        ps = tuple (p.XS_FILTER for p in self.predicates)
        return self._xs_filter_expression (self.op (* ps))
    # end def XS_FILTER

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def XS_GROUP_BY (self) :
        return [self.XS_FILTER]
    # end def XS_GROUP_BY

    @TFL.Meta.Once_Property
    def XS_ORDER_BY (self) :
        raise TypeError \
            ( "Cannot use %s operator for order-by: %s"
            % (self.name, self)
            )
    # end def XS_ORDER_BY

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def _columns (self) :
        ps = self.predicates
        return tuple (itertools.chain (* tuple (p._columns for p in ps)))
    # end def _columns

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def _columns_ob (self) :
        ps = self.predicates
        return tuple (itertools.chain (* tuple (p._columns_ob for p in ps)))
    # end def _columns_ob

    def predicate (self, X, * args, ** kw) :
        """Called during execution of Mapper.__call__ to map a TFL.Q_Exp
           instance to a QX-specific instance.
        """
        XR = X.REF (X.ETW, _polymorphic_x = self._polymorphic_x)
        self.predicates = list \
            (p.predicate (XR, * args, ** kw) for p in self.predicates)
        return self
    # end def predicate

    def __repr__ (self) :
        return "<:%s: (%s)>" % \
            (self.name, ", ".join (repr (p) for p in self.predicates))
    # end def __repr__

# end class _Bool_

class _Bool_Distributive_ (_Bool_) :
    """A Boolean operator that distributes a binary operation to its
       operands.
    """

    def _op_bin (self, rhs, name, op, reverse) :
        result = self._Ancestor \
            ([p._op_bin (rhs, name, op, reverse) for p in self.predicates])
        return result
    # end def _op_bin

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        self.predicates = list (getattr (p, name) for p in self.predicates)
        return self
    # end def __getattr__

    def __getitem__ (self, type_name) :
        self.predicates = list (p [type_name] for p in self.predicates)
        return self
    # end def __getitem__

# end class _Bool_Distributive_

class And (_Bool_) :
    """Map a Filter_And expression to the corresponding SQLAlchemy expression.
    """

    name = "AND"
    op   = staticmethod (SA.expression.and_)

# end class And

class And_Distributive (And, _Bool_Distributive_) :
    """Map a Q.AND expression to the corresponding SQLAlchemy expression."""

    _Ancestor = And

# end class And_Distributive

class Or (_Bool_) :
    """Map a Filter_Or expression to the corresponding SQLAlchemy expression.
    """

    name = "OR"
    op   = staticmethod (SA.expression.or_)

    ### The `predicates` of the `OR` expression must be joined with
    ### `LEFT OUTER JOIN`
    _polymorphic_x        = True

# end class Or

class Or_Distributive (Or, _Bool_Distributive_) :
    """Map a Q.OR expression to the corresponding SQLAlchemy expression."""

    _Ancestor = Or

# end class Or_Distributive

class _Op_ (_Base_) :

    def __init__ (self, lhs, name, op, * args, ** kw) :
        self.lhs     = lhs
        self.name    = name
        self.op      = op
        self.args    = args
        self.kw      = kw
    # end def __init__

    def apply (self, lhs) :
        return self.op (lhs, * self.args, ** self.kw)
    # end def apply

    @TFL.Meta.Once_Property
    @getattr_safe
    def X (self) :
        return self.lhs.X
    # end def X

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def XS_ATTR (self) :
        return [self.XS_FILTER]
    # end def XS_ATTR

    @TFL.Meta.Once_Property
    @getattr_safe
    def XS_FILTER (self) :
        lhs = self.lhs._xs_filter_una (self.lhs, self)
        return self._xs_filter_expression (lhs)
    # end def XS_FILTER

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def XS_GROUP_BY (self) :
        return [self.XS_FILTER]
    # end def XS_GROUP_BY

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def XS_ORDER_BY (self) :
        return [self.XS_FILTER]
    # end def XS_ORDER_BY

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def _columns (self) :
        return self.lhs._columns
    # end def _columns

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def _columns_ob (self) :
        return self.lhs._columns_ob
    # end def _columns_ob

    @TFL.Meta.Once_Property
    @getattr_safe
    def _qx_attr (self) :
        return self.lhs._qx_attr
    # end def _qx_attr

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def _xtra_qxs (self) :
        try :
            return self.lhs._xtra_qxs
        except AttributeError :
            return ()
    # end def _xtra_qxs

    def __repr__ (self) :
        kind = self.__class__.__name__
        return "<%s:%s: (%s)>" % (kind, self.name, self.lhs)
    # end def __repr__

# end class _Op_

class _Aggr_ (_Op_) :

    _need_coalesce = set (("sum", "count"))

    def __init__ (self, X, lhs, name) :
        self._X   = X
        self.lhs  = lhs
        self.name = name
    # end def __init__

    def apply (self, lhs) :
        name   = self.name.lower ()
        op     = getattr (SA.func, name)
        result = op (lhs)
        if isinstance (lhs, SA.Operators) and name in self._need_coalesce :
            ### use `coalesce` to avoid contamination with `null` values
            result = SA.func.coalesce (result, 0)
        if isinstance (lhs, SA.schema.Column) :
            result = result.label ("%s_%s" % (lhs.name, name))
        return result
    # end def apply

    @TFL.Meta.Once_Property
    def X (self) :
        return self._X
    # end def X

    @TFL.Meta.Once_Property
    @getattr_safe
    def XS_FILTER (self) :
        lhs = self._xs_filter_una (self.lhs, self)
        return self._xs_filter_expression (lhs)
    # end def XS_FILTER

    def _super_once_prop (f) :
        name = f.__name__
        def _ (self) :
            try :
                return getattr (self.__super, name)
            except AttributeError :
                return f (self)
        _.__name__ = name
        return TFL.Meta.Once_Property (_)
    # end def _super_once_prop

    @_super_once_prop
    def _columns (self) :
        return []
    # end def _columns

    @_super_once_prop
    def _columns_ob (self) :
        return []
    # end def _columns_ob

    @_super_once_prop
    def _qx_attr (self) :
        return None
    # end def _qx_attr

    @_super_once_prop
    def _xtra_qxs (self) :
        return []
    # end def _xtra_qxs

# end class _Aggr_

class Bin (_Op_) :
    """Map a binary expression to the corresponding SQLAlchemy expression."""

    def __init__ (self, lhs, name, op, rhs, reverse) :
        self.__super.__init__ (lhs, name, op)
        self.rhs     = rhs
        self.reverse = reverse
    # end def __init__

    def apply (self, lhs, rhs, reversed = False) :
        reverse = (not self.reverse) if reversed else self.reverse
        if reverse :
            lhs, rhs = rhs, lhs
        op = self.op
        op_div = getattr (operator, "__div__", operator.__truediv__)
        if op is operator.__truediv__ :
            typ = SA.types.Float ### XXX use SA.types.Decimal if necessary
            lhs = SA.expression.cast (lhs, typ)
            rhs = SA.expression.cast (rhs, typ)
        elif op is operator.__floordiv__ :
            ### avoid TypeError raised by sqlalchemy ::
            ###     unsupported operand type(s) for //: 'Column' and 'Column'
            op = op_div
        return op (lhs, rhs)
    # end def apply

    @TFL.Meta.Once_Property
    @getattr_safe
    def XS_FILTER (self) :
        return self._xs_filter_expression \
            (self.lhs._xs_filter_bin (self.rhs, self))
    # end def XS_FILTER

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def qxs (self) :
        rhs = self.rhs
        if isinstance (rhs, _Attr_) :
            return self.lhs, rhs
        else :
            return self.lhs,
    # end def qxs

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def _columns (self) :
        return list (itertools.chain (* (qx._columns for qx in self.qxs)))
    # end def _columns

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def _columns_ob (self) :
        return list (itertools.chain (* (qx._columns_ob for qx in self.qxs)))
    # end def _columns_ob

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def _xtra_qxs (self) :
        return list (itertools.chain (* (qx._xtra_qxs for qx in self.qxs)))
    # end def _xtra_qxs

    def _xs_filter_bin (self, rhs, op, reversed = False) :
        if isinstance (rhs, Kind_Composite) :
            return rhs._xs_filter_bin (self, op, not reversed)
        else :
            rhs = self._xs_filter_rhs (rhs)
            return op.apply \
                (self.lhs._xs_filter_bin (self.rhs, self), rhs, reversed)
    # end def _xs_filter_bin

    def __repr__ (self) :
        rs = "/r" if self.reverse else ""
        return "<Bin:%s%s: (%s, %s)>" % (self.name, rs, self.lhs, self.rhs)
    # end def __repr__

# end class Bin

class Call (_Op_) :
    """Map a method call to the corresponding SQLAlchemy call."""

# end class Call

class Func (_Op_) :
    """Map a function call to the corresponding SQL function."""

    def apply (self, lhs) :
        op_name = self.op.__name__.lower ()
        op      = getattr (SA.func, op_name)
        return op (lhs)
    # end def apply

# end class Func

class Not (_Q_Exp_Proxy_, _Op_) :
    """Map a Q.NOT expression to the corresponding SQL expression ."""

    _xs_filter_una_delegate = "XS_FILTER"

    def __init__ (self, lhs) :
        self.__super.__init__ (lhs, "NOT", operator.__invert__)
    # end def __init__

    def predicate (self, X, * args, ** kw) :
        """Called during execution of Mapper.__call__ to map a TFL.Q_Exp
           instance to a QX-specific instance.
        """
        self.lhs = self.lhs.predicate (X, * args, ** kw)
        return self
    # end def predicate

# end class Not

class Una (_Op_) :
    """Map an unary expression to the corresponding SQLAlchemy expression."""

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def XS_ORDER_BY (self) :
        if self.op == operator.__neg__ :
            def _gen (cs) :
                ### save original query expression (without `DESC`) to
                ### allow later insertion into `select` list
                ### (needed for `SELECT DISTINCT`)
                for c in cs :
                    cd = c.desc ()
                    cd._SAW_ORIGINAL = getattr (c, "_SAW_ORIGINAL", c)
                    yield cd
            result = list (_gen (self.lhs.XS_ORDER_BY))
        else :
            result = [self.XS_FILTER]
        return result
    # end def XS_ORDER_BY

    @TFL.Meta.Once_Property
    @getattr_safe
    def _xs_filter_una_delegate (self) :
        return "XS_FILTER" if self.op == operator.__invert__ else "_XS_FILTER"
    # end def _xs_filter_una_delegate

# end class Una

@pyk.adapt__bool__
class _Attr_ (_RAW_, _Base_) :
    """Map one attribute expression to column(s) expressions of SQLAlchemy"""

    XS_ATTR          = \
    XS_GROUP_BY      = TFL.Meta.Alias_Property ("_columns")
    XS_ORDER_BY      = TFL.Meta.Alias_Property ("_columns_ob")

    def __init__ (self, X, _akw, ETW = None, _is_raw = False, _outer = None, _polymorphic = None) :
        self.X              = X
        self._akw           = _akw
        self.ETW            = ETW if ETW is not None else _akw.ETW
        self._is_raw        = _is_raw or X._is_raw
        self._outer         = _outer
        self._polymorphic   = \
            _polymorphic if _polymorphic is not None else X._polymorphic
    # end def __init__

    @TFL.Meta.Once_Property
    def E_Type (self) :
        return self._akw.e_type
    # end def E_Type

    @TFL.Meta.Once_Property
    @getattr_safe
    def XS_FILTER (self) :
        return self._xs_filter_expression \
            (* tuple (self._xs_fixed_bool (self._qxs)))
    # end def XS_FILTER

    @TFL.Meta.Once_Property
    @getattr_safe
    def _XS_FILTER (self) :
        qxs = self._qxs
        if len (qxs) != 1 :
            raise NotImplementedError \
                ( "_XS_FILTER needs to return a single column; "
                  "%s has %s columns"
                % (self, len (qxs))
                )
        return qxs [-1 if self._is_raw else 0]
    # end def _XS_FILTER

    @TFL.Meta.Once_Property
    def _attr (self) :
        return self._akw.attr
    # end def _attr

    @TFL.Meta.Once_Property
    def _qx_attr (self) :
        return self
    # end def _qx_attr

    @TFL.Meta.Once_Property
    def _qxs (self) :
        return self._columns
    # end def _qxs

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def _xtra_qxs (self) :
        result = []
        if self._outer :
            result.extend (self._outer._xtra_qxs)
        return result
    # end def _xtra_qxs

    def _add_joins_col (self, head_col, * cols, ** kw) :
        def _gen (head_col, cols, joiner) :
            A_Join  = SAW.Attr.A_Join
            for col in cols :
                try :
                    ### only do this for real columns
                    ctab = col.table
                except AttributeError :
                    pass
                else :
                    yield A_Join (col, col, head_col, joiner)
        X           = self.X
        polymorphic = kw.get ("polymorphic", self.X._polymorphic_x)
        joiner      = TFL.Method.outerjoin \
            if polymorphic or self._polymorphic else TFL.Method.join
        joins       = tuple (_gen (head_col, cols, joiner))
        X._add_joins (* joins)
    # end def _add_joins_col

    def _add_joins_inner (self, inner, head_col, polymorphic = None) :
        def _gen (ETW, head_col, cols, joiner) :
            A_Join = SAW.Attr.A_Join
            pkn    = ETW.spk_name
            for col in cols :
                try :
                    ### only do this for real columns
                    ctab = col.table
                except AttributeError :
                    pass
                else :
                    yield A_Join (col, ctab.c [pkn], head_col, joiner)
        if polymorphic is None :
            polymorphic = self.X._polymorphic_x
        if polymorphic is None :
            polymorphic = self._polymorphic or inner._polymorphic
        joiner = TFL.Method.outerjoin if polymorphic else TFL.Method.join
        if inner._columns :
            self.X._add_joins \
                (* _gen (inner.ETW, head_col, inner._columns, joiner))
    # end def _add_joins_inner

    def _add_join_parent (self, pj, polymorphic = None) :
        if pj :
            s_col, t_col = pj
            if polymorphic is None :
                polymorphic = self.X._polymorphic_x
            joiner = TFL.Method.outerjoin \
                if polymorphic or self._polymorphic else TFL.Method.join
            self.X._add_joins (SAW.Attr.A_Join (s_col, s_col, t_col, joiner))
    # end def _add_join_parent

    def _add_join_partial_child_outer (self, inner) :
        pass
    # end def _add_join_partial_child_outer

    def _columns_ob_epk_iter (self, ET) :
        for k in ET.epk_sig :
            qx = getattr (self, k)
            for c in qx._columns_ob :
                yield c
    # end def _columns_ob_epk_iter

    def _etw_alias (self, ETW, col_name) :
        return ETW.etw_alias \
            (ETW, ETW.table_name, self.ETW.table_name, col_name)
    # end def _etw_alias

    def _extract_field (self, col, name) :
        result = self._akw.attr._saw_extract_field (self.ETW.DBW, col, name)
        result.MOM_Kind = getattr (col.MOM_Kind.E_Type, name, None)
        return result
    # end def _extract_field

    def _get_attr (self, name) :
        raise AttributeError (name)
    # end def _get_attr

    def _get_field (self, name, head, tail) :
        if head in self._akw.fields and not tail :
            self._field = head
            return self
    # end def _get_field

    def _inner (self, _akw, ** kw) :
        ikw    = self._inner_kw (_akw, ** kw)
        result = _akw.QX        (** ikw)
        return result
    # end def _inner

    def _inner_kw (self, _akw, ** kw) :
        _outer   = kw.pop ("_outer", self)
        _outer_p = _outer is not None
        result   = dict \
            ( _akw         = _akw
            , ETW          = _outer.ETW     if _outer_p else self.ETW
            , X            = _outer.X       if _outer_p else self.X
            , _is_raw      = _outer._is_raw if _outer_p else self._is_raw
            , _outer       = _outer
            , _polymorphic =
                        _outer._polymorphic if _outer_p else self._polymorphic
            )
        result.update (kw)
        return result
    # end def _inner_kw

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        if self._field is not None :
            raise AttributeError (name)
        head, _, tail = split_hst (name, ".")
        result = self
        if head == "RAW" :
            self._is_raw = True
        else :
            try :
                result = self._get_attr (head)
            except AttributeError as exc :
                result = self._get_field (name, head, tail)
                if result is None :
                    raise
        if tail :
            result = getattr (result, tail)
        return result
    # end def __getattr__

    def __repr__ (self) :
        r = "RAW " if self._is_raw else ""
        if self._field is not None :
            r = "%sfield %s of " % (r, self._field)
        return "<%s | QX.%s for %s%s>" % \
            (self.E_Type.type_name, self.__class__.__name__, r, self._akw)
    # end def __repr__

# end class _Attr_

class _Attr_S_ (_Attr_) :
    """Common base class for attribute kinds with structure"""

    def __init__ (self, * args, ** kw) :
        self._attr_map = {}
        self.__super.__init__ (* args, ** kw)
    # end def __init__

    def _get_attr (self, name) :
        amap   = self._attr_map
        result = amap.get (name)
        if result is None :
            outer = self._outer
            if  (   outer is not None
                and isinstance (outer, Kind_EPK)
                and outer._akw.attr.E_Type.is_partial
                ) :
                ### need to add join, using the right join alias
                ETW, pj = self.ETW.attr_join_etw_alias \
                    (outer._akw, self.ETW.e_type, outer._akw.ETW)
                akw     = ETW.QC [".".join ((self._akw.name, name))].MOM_Wrapper
                result  = self._inner (akw, ETW = ETW)
                self._add_join_parent (pj, polymorphic = True)
                self._add_joins_inner (result, outer._head_col, polymorphic = 1)
            else :
                try :
                    akw    = self._akw.q_able_attrs [name]
                except KeyError :
                    raise AttributeError (name)
                result = self._inner (akw)
            amap [name] = result
        return result
    # end def _get_attr

# end class _Attr_S_

class _Attr_CS_ (_Attr_S_) :
    """Common base class for composite- and structured-attribute kinds"""

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def XS_ATTR (self) :
        return [self._akw]
    # end def XS_ATTR

# end class _Attr_CS_

class _Attr_S_Field_Extractor_ (_Attr_S_) :
    """Common base class for attribute kinds with structure & fields"""

    def _inner (self, _akw, ** kw) :
        KWT    = getattr (_akw.attr, "_SAW_Wrapper", SAW.Attr.Kind_Wrapper)
        CXT    = KWT.CXT
        name   = _akw.eff.attr.name
        cx     = self._extract_field (self._akw.columns [0], name)
        cxt    = CXT \
            (cx, _akw.ETW, self._akw.kind, _akw.outer, attr = _akw.attr)
        result = self.__super._inner (cxt, ** kw)
        return result
    # end def _inner

# end class _Attr_S_Field_Extractor_

@TFL.Add_To_Class ("QX", SAW.Attr.Kind_Wrapper)
class Kind (_Attr_) :
    """Map a reference to a simple attribute to a single SQLAlchemy column."""

    XS_ATTR          = \
    XS_GROUP_BY      = TFL.Meta.Alias_Property ("_qxs")

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def XS_ORDER_BY (self) :
        field  = self._field
        if field is not None :
            return self._qxs
        else :
            return self._columns_ob
    # end def XS_ORDER_BY

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def _columns (self) :
        columns = self._akw.columns
        return [columns [-1 if self._is_raw else 0]]
    # end def _columns

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def _qxs (self) :
        result = list (self._columns)
        field  = self._field
        if field is not None :
            result [0] = self._extract_field (result [0], field)
        return result
    # end def _qxs

# end class Kind

@TFL.Add_To_Class ("QX", SAW.Attr.Kind_Wrapper_C)
class Kind_Composite (_Attr_CS_) :
    """Map a reference to a composite attribute to one or more
       SQLAlchemy columns.
    """

    @TFL.Meta.Once_Property
    def XS_FILTER (self) :
        raise TypeError \
            ( "Cannot filter by composite attribute %s.%s"
            % (self.E_Type.type_name, self._akw.name)
            )
    # end def XS_FILTER

    @TFL.Meta.Once_Property
    def XS_GROUP_BY (self) :
        raise TypeError \
            ( "Cannot group by composite attribute %s.%s"
            % (self.E_Type.type_name, self._akw.name)
            )
    # end def XS_GROUP_BY

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def _columns_ob (self) :
        def _gen (self) :
            ET = self._akw.attr.E_Type
            for k in ET.usr_sig :
                qx = getattr (self, k)
                for c in qx._columns_ob :
                    yield c
        return list (_gen (self))
    # end def _columns_ob

    def _xs_filter_bin (self, rhs, op, reversed = False) :
        ET  = self._akw.attr.E_Type
        lhs = self._columns_ob
        if isinstance (rhs, ET) :
            rhs = rhs.attr_tuple ()
        elif isinstance (rhs, Kind_Composite) :
            rhs = rhs._columns_ob
        elif isinstance (rhs, (tuple, list)) :
            lhs = lhs [:len (rhs)]
        elif isinstance (rhs, dict) :
            lc_map  = dict (zip (ET.usr_sig, lhs))
            try :
                lrs = tuple \
                    ((lc_map [k], v) for k, v in sorted (pyk.iteritems (rhs)))
            except KeyError as exc :
                raise TypeError \
                    ("Unknown attribute of composite %s: %s" % (self, exc))
            else :
                lhs, rhs = zip (* lrs)
        else :
            lhs = lhs [:1]
            rhs = [rhs]
        def _gen (self, lhs, rhs, op) :
            for l, r in zip (lhs, rhs) :
                try :
                    lqx = self._get_attr (l.MOM_Wrapper.attr.name)
                    v   = lqx._xs_filter_bin (r, op, reversed)
                except Exception as exc :
                    import logging
                    logging.exception \
                        ("%s: %s %s %s; %s %r" % (self, lhs, op, rhs, l, r))
                    v   = op.apply (l, r, reversed)
                yield v
        result = tuple (_gen (self, lhs, rhs, op))
        return SA.expression.and_ (* result)
    # end def _xs_filter_bin

    def _xs_filter_una (self, lhs, op) :
        raise TypeError \
            ( "Cannot apply unary operator %s to composite attribute %s"
            % (op.name, self)
            )
    # end def _xs_filter_una

# end class Kind_Composite

@TFL.Add_To_Class ("QX", SAW.Attr.Kind_Wrapper_S)
class Kind_EPK (_Attr_) :
    """Map a reference to an attribute that refers to another entity
       to one or more SQLAlchemy columns of a different table plus the
       necessary joins.
    """

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def _columns (self) :
        columns = self._akw.columns
        return [columns [0]] if columns else ()
    # end def _columns

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def _columns_ob (self) :
        return list (self._columns_ob_epk_iter (self._akw.attr.E_Type))
    # end def _columns_ob

    @TFL.Meta.Once_Property
    @getattr_safe
    def _head_col (self) :
        columns = self._columns
        if columns :
            return columns [0]
    # end def _head_col

    def _get_attr (self, name) :
        if name == "pid" or not name :
            result  = self
        else :
            akw     = self._akw
            ETW, pj = self.ETW.attr_join_etw_alias \
                (akw, akw.attr.E_Type, akw.ETW)
            r_akw, col = _attr_kind_wrapper_and_col (ETW, name)
            ikw     = {}
            if col is not None and col.MOM_Is_Raw :
                ikw = dict (_is_raw = True)
            result  = self._inner (r_akw, ETW = ETW, ** ikw)
            self._add_join_parent (pj)
            head_col = self._head_col
            if head_col is not None :
                self._add_joins_col   (head_col, ETW.spk_col)
                self._add_joins_inner (result, head_col)
        return result
    # end def _get_attr

    def __getitem__ (self, type_name) :
        akw     = self._akw
        apt     = self.ETW.e_type.app_type
        E_Type  = apt.entity_type (type_name)
        if E_Type is None :
            raise TypeError \
                ( "App-type %s doesn't have E-Type with name %s"
                % (apt, type_name)
                )
        elif not issubclass (E_Type, akw.attr.E_Type) :
            raise TypeError \
                ( "E-Type %s must be subclass of %s, but isn't"
                % (type_name, self.E_Type.type_name)
                )
        ETW = E_Type._SAW
        KT  = _Kind_Partial_Restricted_ if E_Type.is_partial \
            else _Kind_EPK_Restricted_
        head_col = self._head_col
        if head_col.name not in SAW.Attr.A_Join.special_col_names :
            ETW = self._etw_alias (ETW, head_col.name)
        result             = KT \
            ( X            = self.X
            , _akw         = akw
            , ETW          = ETW
            , _is_raw      = self._is_raw
            , _outer       = self
            )
        self._add_joins_inner (result, head_col)
        return result
    # end def __getitem__

# end class Kind_EPK

class _Kind_EPK_Restricted_ (_Attr_) :

    _XS_FILTER              = TFL.Meta.Alias_Property ("XS_FILTER")

    @TFL.Meta.Once_Property
    def E_Type (self) :
        return self.ETW.e_type
    # end def E_Type

    @TFL.Meta.Once_Property
    @getattr_safe
    def XS_FILTER (self) :
        return self._head_col != None
    # end def XS_FILTER

    @TFL.Meta.Once_Property
    @getattr_safe
    def _XS_FILTER (self) :
        return self._head_col
    # end def _XS_FILTER

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def _columns (self) :
        return [self.ETW.spk_col]
    # end def _columns

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def _columns_ob (self) :
        return list (self._columns_ob_epk_iter (self.E_Type))
    # end def _columns_ob

    @TFL.Meta.Once_Property
    @getattr_safe
    def _head_col (self) :
        return self.ETW.spk_col
    # end def _head_col

    def _get_attr (self, name) :
        if name == "pid" or not name :
            result  = self
        else :
            ETW        = self.ETW
            r_akw, col = _attr_kind_wrapper_and_col (ETW, name)
            result     = self._inner (r_akw)
        return result
    # end def _get_attr

    def _get_field (self, name, head, tail) :
        pass ### no fields here
    # end def _get_field

# end class _Kind_EPK_Restricted_

@TFL.Add_To_Class ("QX", SAW.Attr.Kind_Wrapper_P)
class Kind_Partial (_Attr_) :
    """Map a reference to a polymorphic attribute to a set of
       SQLAlchemy columns of one or more different tables plus the
       necessary joins.
    """

    _postfix         = None
    __is_raw         = False

    @TFL.Meta.Once_Property
    @getattr_safe
    def XS_ATTR (self) :
        xs = tuple (c.XS_ATTR for c in self._children)
        return SA.func.coalesce (* xs)
    # end def XS_ATTR

    @TFL.Meta.Once_Property
    @getattr_safe
    def XS_FILTER (self) :
        xs = tuple (c.XS_FILTER for c in self._children)
        return SA.expression.or_ (* xs)
    # end def XS_FILTER

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def XS_GROUP_BY (self) :
        xs = tuple (c.XS_GROUP_BY for c in self._children)
        return SA.func.coalesce (* xs)
    # end def XS_GROUP_BY

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def XS_ORDER_BY (self) :
        xs = tuple (c.XS_ORDER_BY for c in self._children)
        return SA.func.coalesce (* xs)
    # end def XS_ORDER_BY

    @TFL.Meta.Once_Property
    @getattr_safe
    def _XS_FILTER (self) :
        xs = tuple (c._XS_FILTER for c in self._children)
        return SA.expression.or_ (* xs)
    # end def _XS_FILTER

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def _children (self) :
        ### `Once_Property` because `_is_raw` might be set after `__init__`
        with self.X.LET (_polymorphic = True) :
            def _gen (self) :
                akw  = self._akw
                name = akw.name
                for ETW in akw.ETW.children :
                    i_akw = ETW.q_able_attrs [name]
                    yield self._inner \
                        ( i_akw
                        , ETW          = ETW
                        , _is_raw      = self._is_raw
                        , _outer       = self._outer
                        , _polymorphic = True
                        )
            return list (_gen (self))
    # end def _children

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def _columns (self) :
        def _gen (self) :
            for c in self._children :
                for col in c._columns :
                    yield col
        with self.X.LET (_polymorphic = True) :
            return list (_gen (self))
    # end def _columns

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def _columns_ob (self) :
        def _gen (self) :
            for c in self._children :
                for col in c._columns_ob :
                    yield col
        with self.X.LET (_polymorphic = True) :
            return list (_gen (self))
    # end def _columns_ob

    @property
    def _is_raw (self) :
        return self.__is_raw
    # end def _is_raw

    @_is_raw.setter
    def _is_raw (self, value) :
        self.__is_raw = value
        if "_children" in self.__dict__ :
            for c in self._children :
                c._is_raw = value
    # end def _is_raw

    @Single_Dispatch_Method
    def _op_bin (self, rhs, name, op, reverse) :
        children     = self._children
        children [:] = (c._op_bin (rhs, name, op, reverse) for c in children)
        return self
    # end def _op_bin

    def _op_call (self, name, op, * args, ** kw) :
        children     = self._children
        children [:] = (c._op_call (name, op, * args, ** kw) for c in children)
        return self
    # end def _op_call

    def _op_una (self,  name, op) :
        children     = self._children
        children [:] = (c._op_una (name, op) for c in children)
        return self
    # end def _op_una

    def _get_attr (self, name) :
        ### reset `Once_Property` values, if any
        for k in ("attributes", "_columns", "_columns_ob") :
            self.__dict__.pop (k, None)
        ### `_children` is `Once_Property`
        ### --> replace elements of list instead of assigning a new list
        self._postfix = ".".join \
            ((self._postfix, name)) if self._postfix else name
        def _gen (children) :
            for c in children :
                if c._outer is not None :
                    c._outer._add_join_partial_child_outer (c)
                i = c._get_attr (name)
                yield i
        with self.X.LET (_polymorphic = True) :
            children     = self._children
            children [:] = _gen (children)
        return self
    # end def _get_attr

    def _xs_filter_una (self, lhs, op) :
        name = op._xs_filter_una_delegate
        xs   = tuple (getattr (c, name) for c in self._children)
        return SA.expression.or_ (* tuple (op.apply (x) for x in xs))
    # end def _xs_filter_una

# end class Kind_Partial

class _Kind_Partial_Restricted_ (Kind_Partial) :

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def _children (self) :
        ### `Once_Property` because `_is_raw` might be set after `__init__`
        with self.X.LET (_polymorphic = True) :
            def _gen (self) :
                akw = self._akw
                for ETW in self.ETW.children :
                    ETW = self._etw_alias (ETW, akw.ckd_name)
                    yield _Kind_EPK_Restricted_ \
                        ( X            = self.X
                        , _akw         = akw
                        , ETW          = ETW
                        , _is_raw      = self._is_raw
                        , _outer       = self._outer
                        , _polymorphic = True
                        )
            return list (_gen (self))
    # end def _children

# end class _Kind_Partial_Restricted_

@_Base_._op_bin.add_type (Kind_Partial)
def _op_bin_partial_r_ (self, rhs, name, op, reverse) :
    return rhs._op_bin (self, name, op, not reverse)
# end def _op_bin_partial_r_

@Kind_Partial._op_bin.add_type (Kind_Partial)
def _op_bin_partial_lr_ (self, rhs, name, op, reverse) :
    def _cartesian (self, rhs, name, op, reverse) :
        for lc, rc in cartesian (self._children, rhs._children) :
            yield lc._op_bin (rc, name, op, reverse)
    self._children [:] = _cartesian (self, rhs, name, op, reverse)
    return self
# end def _op_bin_partial_lr_

@TFL.Add_To_Class ("QX", SAW.Attr.Kind_Wrapper_Q)
class Kind_Query (_Attr_) :
    """Map a reference to a query attribute to whatever columns that
       query resolves to.
    """

    @TFL.Meta.Once_Property
    @getattr_safe
    def XS_ATTR (self) :
        return self._inner_qx.XS_ATTR
    # end def XS_ATTR

    @TFL.Meta.Once_Property
    @getattr_safe
    def XS_FILTER (self) :
        iqx = self._inner_qx
        ixf = iqx.XS_FILTER
        return self._xs_filter_expression (ixf)
    # end def XS_FILTER

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def XS_GROUP_BY (self) :
        return self._inner_qx.XS_GROUP_BY
    # end def XS_GROUP_BY

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def XS_ORDER_BY (self) :
        return self._inner_qx.XS_ORDER_BY
    # end def XS_ORDER_BY

    @TFL.Meta.Once_Property
    @getattr_safe
    def _XS_FILTER (self) :
        return self._xs_filter_expression (self._inner_qx._XS_FILTER)
    # end def _XS_FILTER

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def _columns (self) :
        qx = self._inner_qx
        return qx._columns
    # end def _columns

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def _columns_ob (self) :
        return self._inner_qx._columns_ob
    # end def _columns_ob

    @TFL.Meta.Once_Property
    @getattr_safe
    def _inner_qx (self) :
        akw           = self._akw
        ETW           = akw.outer if akw.outer else akw.ETW
        XR            = self.X.REF (ETW, self._is_raw, self._polymorphic)
        result        = XR (akw.attr.query)
        result._outer = self
        return result
    # end def _inner_qx

    def _op_bin (self, rhs, name, op, reverse) :
        return self._inner_qx._op_bin (rhs, name, op, reverse)
    # end def _op_bin

    def _op_call (self, name, op, * args, ** kw) :
        return self._inner_qx._op_call (name, op, * args, ** kw)
    # end def _op_call

    def _op_una (self, name, op) :
        return self._inner_qx._op_una (name, op)
    # end def _op_una

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def _xtra_qxs (self) :
        akw     = self._akw
        attr    = akw.attr
        result  = []
        if attr.query_preconditions :
            result.extend (self.X (p) for p in attr.query_preconditions)
        return result
    # end def _xtra_qxs

    def _get_attr (self, name) :
        qx = self._inner_qx
        try :
            result = getattr (qx, name)
        except AttributeError :
            raise TypeError \
                ("%s doesn't support access to attribute `%s`" % (self, name))
        else :
            return result
    # end def _get_attr

# end class Kind_Query

@TFL.Add_To_Class ("QX", SAW.Attr.Kind_Wrapper_R)
class Kind_Rev_Query (_Attr_) :
    """Map a reference to a reverse query attribute to whatever
       columns that reverse query resolves to.
    """

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def _columns (self) :
        return [self._ref_col]
    # end def _columns

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def _columns_ob (self) :
        ET = self._akw.attr.E_Type
        if ET.epk_sig :
            return list (self._columns_ob_epk_iter (ET))
        else :
            return self._columns
    # end def _columns_ob

    @TFL.Meta.Once_Property
    @getattr_safe
    def _head_col (self) :
        ref_etw, ref_col, head_col = self._ref_etw_col
        return head_col
    # end def _head_col

    @TFL.Meta.Once_Property
    @getattr_safe
    def _ref_col (self) :
        ref_etw, ref_col, head_col = self._ref_etw_col
        return ref_col
    # end def _ref_col

    @TFL.Meta.Once_Property
    @getattr_safe
    def _ref_etw (self) :
        ref_etw, ref_col, head_col = self._ref_etw_col
        return ref_etw
    # end def _ref_etw

    @TFL.Meta.Once_Property
    @getattr_safe
    def _ref_etw_col (self) :
        ### Pass `polymorphic = True` to `_add_joins_col` to allow
        ### queries like `~ Q.rev_ref` (i.e., select all entities who
        ### don't are not referenced)
        akw         = self._akw
        attr        = akw.attr
        ref_etw, pj = self.ETW.attr_join_etw_alias (akw, attr.Ref_Type)
        ref_col     = ref_etw.QC [attr.ref_name]
        rev_sq      = self._rev_sq
        head_col    = ref_col
        self._add_join_parent (pj)
        self._add_joins_col   (akw.ETW.spk_col, ref_col, polymorphic = True)
        if rev_sq._attr :
            ### `A_Role_Ref` and `A_Role_Ref_Set` need this
            ref_col     = ref_etw.QC [rev_sq._attr]
            ref_wrapper = ref_col.MOM_Wrapper
            ref_etw, pj = ref_wrapper.ETW.attr_join_etw_alias \
                ( ref_wrapper
                , ref_wrapper.attr.E_Type
                )
            self._add_join_parent (pj)
            self._add_joins_col   (ref_col, ref_etw.spk_col, polymorphic = True)
        return ref_etw, ref_col, head_col
    # end def _ref_etw_col

    @TFL.Meta.Once_Property
    @getattr_safe
    def _rev_sq (self) :
        return self._akw.attr.sqx (self.ETW.spk_col)
    # end def _rev_sq

    @TFL.Meta.Once_Property
    @getattr_safe
    def _xtra_qx (self) :
        akw     = self._akw
        attr    = akw.attr
        ref_etw = self._ref_etw
        result  = None
        if attr.sqx_filter is not None :
            XR     = self.X.REF (ref_etw)
            result = XR (attr.sqx_filter)
        return result
    # end def _xtra_qx

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def _xtra_qxs (self) :
        xtra_qx = self._xtra_qx
        result  = [xtra_qx] if xtra_qx is not None else []
        if self._outer :
            result.extend (self._outer._xtra_qxs)
        return result
    # end def _xtra_qxs

    def _add_join_partial_child_outer (self, inner) :
        col = inner.ETW.QC [self._head_col.name]
        try :
            table = col.table
        except AttributeError :
            pass
        else :
            self._add_joins_col (self.ETW.spk_col, col, polymorphic = True)
    # end def _add_join_partial_child_outer

    def _get_attr (self, name) :
        if name == "pid" or not name :
            result  = self
        else :
            ref_etw = self._ref_etw
            r_akw   = ref_etw.QC [name].MOM_Wrapper
            result  = self._inner (r_akw)
        return result
    # end def _get_attr

# end class Kind_Rev_Query

@TFL.Add_To_Class ("QX", SAW.Attr.Kind_Wrapper_Structured_Field_Extractor)
class Kind_Structured_Field_Extractor (_Attr_S_Field_Extractor_, Kind) :
    """Map a reference to a structured-attribute kind & fields"""
# end class Kind_Structured_Field_Extractor

class _Self_ (_Attr_) :
    """Map a Q.SELF query attribute to column(s) expressions of SQLAlchemy"""

    def __init__ (self, X, ETW = None, _is_raw = False, _outer = None, _polymorphic = None) :
        self.X            = X
        self.ETW          = ETW if ETW is not None else X.ETW
        self._is_raw      = _is_raw or X._is_raw
        self._outer       = _outer
        self._polymorphic = \
            _polymorphic if _polymorphic is not None else X._polymorphic
    # end def __init__

    @TFL.Meta.Once_Property
    def XS_FILTER (self) :
        return True
    # end def XS_FILTER

    @TFL.Meta.Once_Property
    def E_Type (self) :
        return self.ETW.e_type
    # end def E_Type

    @TFL.Meta.Once_Property
    def _attr (self) :
        return self.E_Type.spk.attr
    # end def _attr

    @TFL.Meta.Once_Property
    def _columns (self) :
        return [self._head_col]
    # end def _columns

    @TFL.Meta.Once_Property
    @getattr_safe (default = ())
    def _columns_ob (self) :
        return list (self._columns_ob_epk_iter (self.E_Type))
    # end def _columns_ob

    @TFL.Meta.Once_Property
    @getattr_safe
    def _head_col (self) :
        return self.ETW.spk_col
    # end def _head_col

    def _get_attr (self, name) :
        if name == self.E_Type.spk_attr_name or not name :
            result  = self
        else :
            result  = getattr (self.X, name)
        return result
    # end def _get_attr

    def _get_field (self, name, head, tail) :
        pass ### no fields here
    # end def _get_field

    def __repr__ (self) :
        return "<%s | QX.%s for SELF>" % \
            (self.E_Type.type_name, self.__class__.__name__)
    # end def __repr__

# end class _Self_

class _NIL_ (_Self_) :
    """Map a Q.NIL query attribute to  SQLAlchemy"""

    XS_ATTR          = \
    XS_GROUP_BY      = \
    XS_ORDER_BY      = TFL.Meta.Alias_Property ("XS_FILTER")

    @TFL.Meta.Once_Property
    def XS_FILTER (self) :
        return False
    # end def XS_FILTER

    def __repr__ (self) :
        return "<%s | QX.%s for NIL>" % \
            (self.E_Type.type_name, self.__class__.__name__)
    # end def __repr__

# end class _NIL_

###############################################################################
### Generic functions to display a tree of QX instances
@Single_Dispatch
def display (q, level = 0, sep0 = "", show_inner = True) :
    import datetime
    if q in (datetime.date.today (), datetime.datetime.today ()) :
        q = "<<today>>"
    indent  = "  " * level if sep0 not in ("", " ") else ""
    return "%s%s%s" % (sep0, indent, q)
# end def display

@display.add_type (_Attr_)
def _display_qx_attr_ (q, level = 0, sep0 = "", show_inner = True) :
    indent  = "  " * level
    indent1 = indent + "    "
    sep     = "\n" + indent1
    r       = "RAW " if q._is_raw else " "
    parts   = \
        [ "%s%s<%s | QX.%s for%s%s%s>"
        % ( sep0, indent
          , q.E_Type.type_name, q.__class__.__name__, sep, r, q._akw
          )
        ]
    if q._outer :
        parts.append (display (q._outer, level + 2, show_inner = False))
    return "\n".join (parts)
# end def _display_qx_attr_

@display.add_type (_Self_)
def _display_qx_self_ (q, level = 0, sep0 = "", show_inner = True) :
    indent  = "  " * level
    parts   = \
        [ "%s%s<%s | QX.%s for SELF>"
        % ( sep0, indent
          , q.E_Type.type_name, q.__class__.__name__
          )
        ]
    if q._outer :
        parts.append (display (q._outer, level + 2, show_inner = False))
    return "\n".join (parts)
# end def _display_qx_self_

@display.add_type (_BVAR_)
def _display_qx_bvar_ (q, level = 0, sep0 = "", show_inner = True) :
    indent  = "  " * level
    return "%s%s%s:%s:" % (sep0, indent, "BVAR", q._name)
# end def _display_qx_bvar_

@display.add_type (_Bool_)
def _display_qx_bool_ (q, level = 0, sep0 = "", show_inner = True) :
    indent  = "  " * level
    return "%s%s:%s:%s" % \
        ( sep0, indent, q.name
        , "".join
            (display (p, level + 1, "\n", show_inner) for p in q.predicates)
        )
# end def _display_qx_bool_

@display.add_type (_Op_)
def _display_qx_op_ (q, level = 0, sep0 = "", show_inner = True) :
    indent   = "  " * level
    kind     = q.__class__.__name__
    if q.name.lower () == kind.lower () :
        kind = ""
    return "%s%s%s:%s:%s" % \
        ( sep0, indent, kind, q.name
        , display (q.lhs, level + 1, "\n", show_inner)
        )
# end def _display_qx_op_

@display.add_type (Kind_Partial)
def _display_qx_kind_partial_ (q, level = 0, sep0 = "", show_inner = True) :
    indent  = "  " * level
    indent1 = indent + "    "
    sep     = "\n" + indent1
    r       = "RAW " if q._is_raw else " "
    parts   = \
        [ "%s%s<%s | QX.%s for%s%s%s>"
        % ( sep0, indent
          , q.E_Type.type_name, q.__class__.__name__, sep, r, q._akw
          )
        ]
    if q._outer :
        parts.append (display (q._outer, level + 2, show_inner = False))
    for c in q._children :
        parts.append (display (c, level + 1))
    return "\n".join (parts)
# end def _display_qx_kind_partial_

@display.add_type (Kind_Query)
def _display_qx_kind_query_ (q, level = 0, sep0 = "", show_inner = True) :
    parts   = [_display_qx_attr_ (q, level, sep0, show_inner = False)]
    if show_inner :
        parts.append (display (q._inner_qx, level+2, show_inner = False))
    return "\n".join (parts)
# end def _display_qx_kind_query_

@display.add_type (Bin)
def _display_qx_bin_ (q, level = 0, sep0 = "", show_inner = True) :
    indent  = "  " * level
    rs      = "/r" if q.reverse else ""
    return "%s%sBin:%s%s:%s%s" % \
        ( sep0, indent, q.name, rs
        , display (q.lhs, level + 1, "\n", show_inner)
        , display (q.rhs, level + 1, "\n", show_inner)
        )
# end def _display_qx_bin_

###############################################################################
### `fixed_q_exp` will make a copy of a `TFL.Q_Exp` instance and all its nodes
### - for some types of nodes, QX-specific instances will replace
###   TFL.Q_Exp (and MOM.Q_Exp_Raw) instances

@Single_Dispatch
def fixed_q_exp (x) :
    return x
# end def fixed_q_exp

@fixed_q_exp.add_type (Q._Aggr_)
def _fixed_q_exp_aggr_ (x) :
    result = _Q_Aggr_Proxy_ (x.op_name, x.Q, fixed_q_exp (x.rhs))
    return result
# end def _fixed_q_exp_aggr_

@fixed_q_exp.add_type (Q._Bin_)
def _fixed_q_exp_bin_ (x) :
    return x.__class__ \
        (fixed_q_exp (x.lhs), x.op, fixed_q_exp (x.rhs), x.undefs, x.reverse)
# end def _fixed_q_exp_bin_

@fixed_q_exp.add_type (Q._Call_)
def _fixed_q_exp_call_ (x) :
    args = tuple (fixed_q_exp (a) for a in x.args)
    return _Q_Call_Proxy_ (fixed_q_exp (x.lhs), x.op, * args, ** x.kw)
# end def _fixed_q_exp_call_

@fixed_q_exp.add_type (Q._Get_)
def _fixed_q_exp_get_ (x) :
    QC = x.Q.__class__
    Q  = QC (Ignore_Exception = QC.Ignore_Exception)
    return x.__class__ (Q, x._name, x._getter)
# end def _fixed_q_exp_get_

@fixed_q_exp.add_type (Q._Get_._E_Type_Restriction_)
def _fixed_q_exp_get_etr_ (x) :
    return _Q_ETR_Proxy_ (x)
# end def _fixed_q_exp_get_etr_

@fixed_q_exp.add_type (Q.RAW._Get_Raw_)
def _fixed_q_exp_get_raw_ (x) :
    QC = x.Q.__class__
    Q  = QC (Ignore_Exception = QC.Ignore_Exception)
    return x.__class__ (Q, x._postfix, x._prefix)
# end def _fixed_q_exp_get_raw_

@fixed_q_exp.add_type (Q._NIL_)
def _fixed_q_exp_nil_ (x) :
    return _Q_NIL_Proxy_ (x.Q)
# end def _fixed_q_exp_nil_

@fixed_q_exp.add_type (Q._Self_)
def _fixed_q_exp_self_ (x) :
    return _Q_Self_Proxy_ (x.Q)
# end def _fixed_q_exp_self_

@fixed_q_exp.add_type (Q._Una_)
def _fixed_q_exp_una_ (x) :
    op = x.op
    if op == operator.__not__ :
        ### * `Q_Exp` uses `~` (which maps to __invert__) to implement
        ###   boolean NOT (__not__)
        ### * to apply `~` properly to `_Attr_` instances we have to force
        ###   evaluation of `__invert__`
        op = operator.__invert__
    return x.__class__ (fixed_q_exp (x.lhs), op, x.undefs)
# end def _fixed_q_exp_una_

@fixed_q_exp.add_type (TFL.Filter_And)
def _fixed_filter_and_ (x) :
    ps = tuple (fixed_q_exp (p) for p in x.predicates)
    return And (ps)
# end def _fixed_filter_and_

@fixed_q_exp.add_type (Q._AND_)
def _fixed_q_exp_and_ (x) :
    ps = tuple (fixed_q_exp (p) for p in x.predicates)
    return And_Distributive (ps)
# end def _fixed_q_exp_and_

@fixed_q_exp.add_type (Q.BVAR.BVAR)
def _fixed_q_exp_bvar_ (x) :
    return _BVAR_ (x.Q, x._name)
# end def _fixed_q_exp_bvar_

@fixed_q_exp.add_type (Q.NOT)
def _fixed_q_exp_not_ (x) :
    p = fixed_q_exp (x._not_predicate)
    return Not (p)
# end def _fixed_q_exp_not_

@fixed_q_exp.add_type (TFL.Filter_Or)
def _fixed_filter_or_ (x) :
    ps = tuple (fixed_q_exp (p) for p in x.predicates)
    return Or (ps)
# end def _fixed_filter_or_

@fixed_q_exp.add_type (Q._OR_)
def _fixed_q_exp_or_ (x) :
    ps = tuple (fixed_q_exp (p) for p in x.predicates)
    return Or_Distributive (ps)
# end def _fixed_q_exp_or_

###############################################################################
### `fixed_order_by` maps `TFL.Sorted_By` instances to Q expressions
@Single_Dispatch
def fixed_order_by (x) :
    raise ValueError ("Cannot order by %s %r" % (x.__class__.__name__, x))
# end def fixed_order_by

@fixed_order_by.add_type (TFL.Sorted_By)
def _fixed_order_by_sorted_by_ (x) :
    for c in x.criteria :
        for r in fixed_order_by (c) :
            yield r
# end def _fixed_order_by_sorted_by_

@fixed_order_by.add_type (_Base_, TFL.Q_Exp.Q_Root, SA.Operators)
def _fixed_order_by_q_exp_ (x) :
    yield x
# end def _fixed_order_by_q_exp_

@fixed_order_by.add_type (* pyk.string_types)
def _fixed_order_by_str_ (x) :
    desc   = x.startswith ("-") or ".-" in x
    crit   = x.replace ("-", "")
    result = getattr (Q, crit)
    if desc :
        result = - result
    yield result
# end def _fixed_order_by_str_

@fixed_order_by.add_type (tuple)
def _fixed_order_by_tuple (xs) :
    for x in xs :
        for r in fixed_order_by (x) :
            yield r
# end def _fixed_order_by_tuple

__doc__ = """
Module MOM.DBW.SAW.QX
=======================

.. moduleauthor:: Christian Tanzer <tanzer@swing.co.at>

The functions and classes of this module map generic query expressions
into expressions usable for SQLAlchemy queries.

The method :meth:`query <_MOM.E_Type_Manager.Entity.query>`
returns a query object that provides the methods `filter`, `group_by`,
`order_by`, `attr` and `attrs`. `query` and its methods accept generic
query expressions as arguments.

A generic query expression looks like ::

    Q.lifetime.start > "2012-07-01"

where `Q` is a query generator provided by `MOM` --- it is an instance
of the :class:`TFL.Q_Exp.Base<_TFL.Q_Exp.Base>`. `Q`
expressions represent symbolic expressions. Calling a `Q` expression
instance triggers the evaluation of the symbolic expression as applied
to the single argument passed.

For instance, if `p` is an instance of the essential class
`PAP.Person` and `q` is a reference to the example expression given
above,

    q (p)

will evaluate to `True` or `False`, depending on the value of
`p.lifetime.start`.

Given a :class:`scope<_MOM.Scope.Scope>` instance `s`, you can find
all persons born after the turn of the last century by using the
query ::

    s.PAP.Person.query \\
        (Q.lifetime.start >= "2000-01-01").order_by (Q.lifetime)

In general, a Q expression is a tree of Q instances. The leafs of such
a tree are either literal values or references to attributes of
essential objects. Inner nodes of the tree represent either operators or
function calls. Calling a Q expression instance leads to the
evaluation of all nodes of the tree, starting with the leaf nodes.

If the scope `s` is connected to a relational database management
system (RDBMS) wrapped by SQLAlchemy, such Q expressions need to be
mapped to SQLAlchemy expressions. For simple expressions, there is a
one-to-one correspondence between the generic tree and the SQLAlchemy
tree. For more complex expressions, the SQLAlchemy tree contains many
additional nodes.

The complexity of a Q expression depends on the type of attributes
referenced by the expression. Whereas operators and function calls map
directly to SQLAlchemy, the mapping of attribute references depends on
the type of attributes:

* References to simple attributes, e.g., `A_Int` or `A_String`, map to
  a single SQLAlchemy column instance.

* References to composite attributes, e.g., `A_Date_Interval`, map to
  one or more SQLAlchemy column instances.

* References to attributes referring to other instances map to
  one or more SQLAlchemy column instances of a different table and
  need one or more joins.

* References to polymorphic attributes, i.e., attributes referring to
  instances of any of a set of essential types, map to a set of
  SQLAlchemy column instances of different tables, needing several
  joins.

  + If such references are used as operands in an expression, that
    expression needs to be evaluated for each of the possible types
    (SQL tables).

* References to query and reverse query attributes can resolve to any
  of the above cases.

* There are some special types of attributes that need specific
  mapping. For instance, an attribute referring to a network address
  (CIDR) might be stored as a number of columns unless the RDBMS
  supports a native datatype for CIDR (currently only supported by
  PostgreSQL).

.. autoclass:: Mapper
.. autoclass:: _Base_

"""

if __name__ != "__main__" :
    MOM.DBW.SAW._Export_Module ()
### __END__ MOM.DBW.SAW.QX
