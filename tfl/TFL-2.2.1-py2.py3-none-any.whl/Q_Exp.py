# -*- coding: utf-8 -*-
# Copyright (C) 2009-2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Q_Exp
#
# Purpose
#    Query expression language
#
# Revision Dates
#     4-Dec-2009 (CT) Creation
#     7-Dec-2009 (CT) `Base.undef` and `Bin.undefs` added and used
#    10-Dec-2009 (CT) `Bin.__nonzero__` defined to raise a `TypeError` to
#                     avoid `Q.a < Q.b < Q.c` silently discarding `Q.a <`
#    10-Dec-2009 (CT) `Exp_B` added (and `_Exp_` factored),
#                     and used as base for `Bin_Bool`
#     9-Feb-2010 (CT) Support for queries of nested attributes added
#    10-Feb-2010 (CT) `ENDSWITH` and `STARTSWITH` changed to *not* use
#                     unbound methods of `str` (fail for unicode values, duh)
#    10-Feb-2010 (MG) Converted `lambda` in `startswith` and `endswith` to
#                     functions which have aproper `__name__` which is needed
#                     by the SA instrumentation
#    12-Feb-2010 (CT) `__nonzero__` added to `Base`, `Call`, and `_Exp_`
#     1-Sep-2010 (CT) Reflected binary operators added (__radd__ and friends)
#     2-Sep-2010 (CT) `Get.name`  changed to `Get._name` (ditto for
#                     `Get.getter`)
#    14-Dec-2010 (CT) `Exp.D`, `Exp.DT`, and `Q._Date_` added
#    14-Jan-2011 (CT) Common base `Q_Root` added to all query classes
#    14-Jan-2011 (CT) `Bin` and `__binary` changed to honor `reverse`
#    22-Jul-2011 (CT) `__call__` factored up to `Q_Root`
#    22-Jul-2011 (CT) `LOWER` (and `Func`) added
#    13-Sep-2011 (CT) All internal classes renamed to `_<<name>>_`
#    14-Sep-2011 (CT) `SUM` added
#    16-Sep-2011 (MG) `_SUM_._name` added
#    21-Sep-2011 (CT) `BETWEEN` changed to guard against `val is None`
#    22-Dec-2011 (CT) Change `_Bin_.__repr__` to honor `reverse`
#    22-Feb-2013 (CT) Use `TFL.Undef ()` not `object ()`
#    25-Feb-2013 (CT) Change `_Get_.predicate` to set `Q.undef.exc`
#     9-Jul-2013 (CT) Add support for unary minus (`_Una_Expr_`, `__neg__`)
#    11-Jul-2013 (CT) Add support for unary not   (`_Una_Bool_`, `__invert__`)
#    27-Jul-2013 (CT) Add `BVAR` to support bound variables
#    28-Jul-2013 (CT) Add `_BVAR_Get_.NEW`, `BVAR.bind`, `BVAR.predicate`
#    28-Jul-2013 (CT) Add `BVAR_Man`
#    30-Aug-2013 (CT) Fix `__div__`
#    30-Aug-2013 (CT) Add `display`
#    30-Aug-2013 (CT) Move `__invert__` up to `_Exp_Base_` (from `_Exp_`)
#    30-Aug-2013 (CT) Add and use `_una_bool`, `_una_expr`;
#                     add `_Bin_.Table`, `_Una_.Table`
#     5-Sep-2013 (CT) Change `_Func_` to inherit from `(_Call_, _Exp_)`,
#                     not `(_Exp_, _Call_)`; add `_Call_.Table`
#    25-Sep-2013 (CT) Remove `LOWER`, `_Func_`
#    30-Sep-2013 (CT) Remove obsolete `SET`
#    30-Sep-2013 (CT) Add `SELF`
#    10-Oct-2013 (CT) Factor `_derive_expr_class`
#    10-Oct-2013 (CT) Call `_derive_expr_class` for `_Call_` and `_Sum_`, too
#    11-Oct-2013 (CT) Factor `_Aggr_`, `_derive_aggr_class`, add `_Avg_`...
#    31-Mar-2014 (CT) Add `M_Q_Root`, `normalized_op_name` (3.4-compatibility)
#     3-Apr-2014 (CT) Remove `None` from `undefs` for `__not__`
#     4-Apr-2014 (CT) Add `AND`, `NOT`, `OR` to `Base`;
#                     add `__and__`, `__invert__`, `__or__` to `Root`
#    16-Apr-2014 (CT) Change `AND` and `OR` to distribute binary operations
#    16-Apr-2014 (CT) Add `NIL`
#    10-Sep-2014 (CT) Add `__getattr__` and `__getitem__` to `_Bool_Bin_Op_`
#    11-Sep-2014 (CT) Add `Q.APPLY`
#    11-Sep-2014 (CT) Add `_Distributive_` as mixin for `_Bool_Bin_Op_`, `_Get_`
#    27-Feb-2015 (CT) Add `Q.DATE`, `Q.DATE_TIME`, `Q.TIME`, and `_Date_.NOW`
#    16-Jul-2015 (CT) Use `expect_except` in doc-tests
#     8-Oct-2015 (CT) Change `__getattr__` to *not* handle `__XXX__`
#    24-May-2016 (CT) Add `_display_filter_q_`
#    20-Jul-2016 (CT) Add `_Exp_.OVERLAPS`
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
### importing `unicode_literals` from `__future__` wrecks 2.7 doctest

from   _TFL                       import TFL

import _TFL._Meta.Object
import _TFL.Accessor
import _TFL.Decorator
import _TFL.Filter
import _TFL.Undef

from   _TFL._Meta.Single_Dispatch import Single_Dispatch, Single_Dispatch_Method
from   _TFL.Math_Func             import average
from   _TFL.predicate             import callable
from   _TFL.portable_repr         import portable_repr
from   _TFL.pyk                   import pyk

import datetime
import operator

def normalized_op_name (name) :
    return name.strip ("_")
# end def normalized_op_name

@pyk.adapt__bool__
class Base (TFL.Meta.Object) :
    """Query generator.

       Exceptions occurring during the evaluation of q-expressions are
       ignored if they match `Ignore_Exception`, i.e., per default, they
       aren't.

       To ignore exceptions, pass an Exception class or a tuple of
       exception classes to :meth:`Base.__init__`.

       Examples::

       >>> from _TFL.Record import Record as R
       >>> r1 = R (foo = 42, bar = 137, baz = 11, quux = R (a = 1, b = 200))
       >>> Q  = Base ()
       >>> QQ = Base (Ignore_Exception = (AttributeError, ))

       >>> (Q.foo == 42)
       Q.foo == 42
       >>> (Q.foo == 42) (r1)
       True
       >>> (Q.bar == 42) (r1)
       False
       >>> with expect_except (AttributeError) :
       ...     Q.qux (r1) is Q.undef
       AttributeError: qux
       >>> QQ.qux (r1) is QQ.undef
       True

    """

    class Ignore_Exception (Exception) :
        pass

    NOT              = TFL.Filter_Not

    undef            = TFL.Undef ("value")

    def __init__ (self, Ignore_Exception = None) :
        if Ignore_Exception is not None :
            self.Ignore_Exception = Ignore_Exception
    # end def __init__

    @property
    def DATE (self) :
        return self._Date_ (self._Date_.Date)
    # end def DATE

    @property
    def DATE_TIME (self) :
        return self._Date_ (self._Date_.Date_Time)
    # end def DATE_TIME

    @property
    def TIME (self) :
        return self._Date_ (self._Date_.Time)
    # end def TIME

    @property
    def NIL (self) :
        """Evaluates to None, no matter what object the q-expression is applied to."""
        return self._NIL_ (self)
    # end def NIL

    @property
    def SELF (self) :
        """Evaluates to the object the q-expression is applied to."""
        return self._Self_ (self)
    # end def SELF

    def AND (self, * args) :
        """Logical AND of `args`."""
        return self._AND_ (self, * args)
    # end def AND

    @Single_Dispatch_Method
    def APPLY (self, getter, * args) :
        result = getter
        if args :
            result = result (* args)
        return result
    # end def APPLY

    @APPLY.add_type (* pyk.string_types)
    def APPLY_string (self, s, * args) :
        getter = getattr (self, s)
        return self.APPLY (getter, * args)
    # end def APPLY_string

    def OR (self, * args) :
        """Logical OR of `args`."""
        return self._OR_  (self, * args)
    # end def OR

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        if "." in name :
            getter = getattr (TFL.Getter, name)
        else :
            getter = operator.attrgetter (name)
        return self._Get_ (self, name, getter)
    # end def __getattr__

    def __getitem__ (self, item) :
        assert not isinstance (item, slice)
        return self._Get_ (self, item, operator.itemgetter (item))
    # end def __getitem__

    def __bool__ (self) :
        return TypeError \
            ("Result of `%s` cannot be used in a boolean context" % (self, ))
    # end def __bool__

# end class Base

Q = Base ()

class M_Q_Root (TFL.Meta.Object.__class__) :

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        for map_name in "op_map", "rop_map" :
            map = getattr (cls, map_name, None)
            if map :
                for k, v in list (pyk.iteritems (map)) :
                    map.setdefault (normalized_op_name (k), v)
    # end def __init__

# end class M_Q_Root

class Q_Root (TFL.Meta.BaM (TFL.Meta.Object, metaclass = M_Q_Root)) :
    """Base class for all classes modelling query operators and functions."""

    op_map               = dict \
        ( __and__        = "&"
        , __not__        = "~"
        , __or__         = "|"
        )

    def __and__ (self, rhs) :
        return self.Q.AND (self, rhs)
    # end def __add__

    def __call__ (self, obj) :
        return self.predicate (obj)
    # end def __call__

    def __invert__ (self) :
        return self.Q.NOT (self)
    # end def __invert__

    def __or__ (self, rhs) :
        return self.Q.OR (self, rhs)
    # end def __or__

# end class Q_Root

@TFL.Add_New_Method (Base)
class _Aggr_ (Q_Root) :
    """Base for aggregation functions"""

    Table          = {}

    def __init__ (self, Q, rhs = 1) :
        self.Q     = Q
        self.rhs   = rhs
    # end def __init__

    @classmethod
    def derived (cls, subcls) :
        name    = subcls.__name__
        op_name = subcls.op_name = name.strip ("_").upper ()
        cls.Table [op_name] = subcls
        setattr (Base, name, subcls)
        return subcls
    # end def derived

    def predicate (self, obj) :
        try :
            pred   = self.rhs.predicate
        except AttributeError :
            result = self.rhs
        else :
            result = pred (obj)
        return self._aggr_fun (result)
    # end def predicate

    def __repr__ (self) :
        return "Q.%s (%s)" % (self.op_name, portable_repr (self.rhs))
    # end def __repr__

# end class _Aggr_

@TFL.Add_New_Method (Base)
@pyk.adapt__bool__
@pyk.adapt__div__
class _Bin_ (Q_Root) :
    """Binary query expression"""

    op_map               = dict \
        ( __add__        = "+"
        , __eq__         = "=="
        , __div__        = "/"
        , __floordiv__   = "//"
        , __ge__         = ">="
        , __gt__         = ">"
        , __le__         = "<="
        , __lt__         = "<"
        , __mod__        = "%"
        , __mul__        = "*"
        , __rmul__       = "*"
        , __pow__        = "**"
        , __sub__        = "-"
        , __truediv__    = "/"
        )

    rop_map              = dict \
        ( __radd__       = "__add__"
        , __rdiv__       = "__truediv__"
        , __rfloordiv__  = "__floordiv__"
        , __rmod__       = "__mod__"
        , __rmul__       = "__mul__"
        , __rpow__       = "__pow__"
        , __rsub__       = "__sub__"
        , __rtruediv__   = "__truediv__"
        )

    predicate_precious_p = True

    Table                = {}

    def __new__ (cls, lhs, op, rhs, undefs, reverse = False) :
        if isinstance (lhs, _Bool_Bin_Op_) :
            return lhs.__class__ \
                (lhs.Q, * tuple (op (p, rhs) for p in lhs.predicates))
        else :
            return cls.__c_super.__new__ (cls, lhs, op, rhs, undefs, reverse)
    # end def __new__

    def __init__ (self, lhs, op, rhs, undefs, reverse = False) :
        self.Q       = lhs.Q
        self.lhs     = lhs
        self.op      = op
        self.rhs     = rhs
        self.undefs  = undefs
        self.reverse = reverse
    # end def __init__

    def predicate (self, obj) :
        l = self.lhs.predicate (obj)
        try :
            pred = self.rhs.predicate
        except AttributeError :
            r = self.rhs
        else :
            r = pred (obj)
        if not any ((v is u) for v in (l, r) for u in self.undefs) :
            ### Call `op` only if neither `l` nor `v` is an undefined value
            if self.reverse :
                l, r = r, l
            return self.op (l, r)
    # end def predicate

    def __bool__ (self) :
        return TypeError \
            ("Result of `%s` cannot be used in a boolean context" % (self, ))
    # end def __bool__

    def __repr__ (self) :
        op = self.op.__name__
        lhs, rhs = self.lhs, self.rhs
        if self.reverse :
            lhs, rhs = rhs, lhs
        return "%s %s %s" % \
            (portable_repr (lhs), self.op_map.get (op, op), portable_repr (rhs))
    # end def __repr__

# end class _Bin_

@TFL.Add_New_Method (Base)
@pyk.adapt__bool__
class _Una_ (Q_Root) :
    """Unary query expression"""

    ### Python 3 uses non-thunder names, map everything to canonical names
    name_map             = dict \
        ( __invert__     = "__not__"
        , __neg__        = "__neg__"
        , __not__        = "__not__"
        , invert         = "__not__"
        , neg            = "__neg__"
        , not_           = "__not__"
        )
    op_map               = dict \
        ( __invert__     = "~"
        , __not__        = "~"
        , __neg__        = "-"
        , invert         = "~"
        , neg            = "-"
        , not_           = "~"
        )
    op_patch             = dict \
        ( _Una_Bool_     = dict
            ( __invert__ = "__not__"
            )
        , _Una_Expr_     = {}
        )

    predicate_precious_p = True

    Table                = {}

    def __init__ (self, lhs, op, undefs) :
        self.Q       = lhs.Q
        self.lhs     = lhs
        self.op      = op
        self.undefs  = undefs
    # end def __init__

    def predicate (self, obj) :
        l = self.lhs.predicate (obj)
        if not any ((l is u) for u in self.undefs) :
            ### Call `op` only if `l` is not an undefined value
            return self.op (l)
    # end def predicate

    def __bool__ (self) :
        return TypeError \
            ("Result of `%s` cannot be used in a boolean context" % (self, ))
    # end def __bool__

    def __repr__ (self) :
        op  = self.op.__name__
        lhs = self.lhs
        return "%s %s" % (self.op_map.get (op, op), portable_repr (lhs))
    # end def __repr__

# end class _Una_

@TFL.Add_New_Method (Base)
@pyk.adapt__bool__
class _Call_ (Q_Root) :
    """Query expression calling a method."""

    predicate_precious_p = True

    op_map               = {}
    Table                = {}

    def __init__ (self, lhs, op, * args, ** kw) :
        self.Q      = lhs.Q
        self.lhs    = lhs
        self.op     = op
        self.args   = args
        self.kw     = kw
    # end def __init__

    def predicate (self, obj) :
        l = self.lhs.predicate (obj)
        if l is not self.Q.undef :
            return self.op (l, * self.args, ** self.kw)
    # end def predicate

    def __bool__ (self) :
        return TypeError \
            ("Result of `%s` cannot be used in a boolean context" % (self, ))
    # end def __bool__

    def __repr__ (self) :
        op = self.op.__name__
        return "%s.%s %s" % (self.lhs, op, portable_repr (self.args))
    # end def __repr__

# end class _Call_

def __binary (op_fct, Class) :
    name    = op_fct.__name__
    reverse = name in _Bin_.rop_map
    key     = _Bin_.rop_map [name] if reverse else name
    op      = getattr (operator, key)
    if name in ("__eq__", "__ne__") :
        ### Allow `x == None` and `x != None`
        undefs = (Q.undef, )
    else :
        ### Ignore `None` for all other operators
        undefs = (None, Q.undef)
    def _ (self, rhs) :
        if isinstance (self, Q._NIL_) :
            rhs, self = self, rhs
        return getattr (self.Q, Class) (self, op, rhs, undefs, reverse)
    _.__doc__    = op.__doc__
    _.__name__   = name
    _.__module__ = op_fct.__module__
    if op not in _Bin_.Table :
        _Bin_.Table [name] = (op, reverse)
    return _
# end def __binary

def _bin_bool (op) :
    return __binary (op, "_Bin_Bool_")
# end def _bin_bool

def _bin_expr (op) :
    return __binary (op, "_Bin_Expr_")
# end def _bin_expr

def _method (meth) :
    name = meth.__name__
    op   = meth ()
    def _ (self, * args, ** kw) :
        return self.Q._Call_Bool_ (self, op, * args, ** kw)
    _.__doc__    = op.__doc__
    _.__name__   = name
    _.__module__ = meth.__module__
    if op.__name__ not in _Call_.Table :
        _Call_.Table  [op.__name__] = op
        _Call_.op_map [op.__name__] = name
    return _
# end def _method

def _type_error (op) :
    name = op.__name__
    def _ (self, rhs) :
        raise TypeError \
            ( "Operator `%s` not applicable to boolean result of `%s`"
              ", rhs: `%s`"
            % (_Bin_.op_map.get (name, name), self, rhs)
            )
    _.__doc__    = op.__doc__
    _.__name__   = name
    _.__module__ = op.__module__
    return _
# end def _type_error

def __unary (op_fct, Class) :
    name   = op_fct.__name__
    op     = getattr (operator, _Una_.op_patch [Class].get (name, name))
    undefs = (Q.undef, ) if op is operator.__not__ else (None, Q.undef)
    def _ (self) :
        return getattr (self.Q, Class) (self, op, undefs)
    _.__doc__    = op.__doc__
    _.__name__   = name
    _.__module__ = op_fct.__module__
    if name not in _Una_.Table :
        _Una_.Table [name] = op
    return _
# end def __unary

def _una_bool (op) :
    return __unary (op, "_Una_Bool_")
# end def _una_bool

def _una_expr (op) :
    return __unary (op, "_Una_Expr_")
# end def _una_expr

@TFL.Add_New_Method (Base)
class _Date_ (TFL.Meta.Object) :

    class Date (TFL.Meta.Object) :

        type       = datetime.date
        lom_delta  = datetime.timedelta (days=1)
        now        = type.today

    # end class Date

    class Date_Time (TFL.Meta.Object) :

        type       = datetime.datetime
        lom_delta  = datetime.timedelta (seconds=1)
        now        = type.today

    # end class Date_Time

    class Time (TFL.Meta.Object) :

        type       = datetime.time
        lom_delta  = datetime.timedelta (seconds=1)

        @classmethod
        def now (cls) :
            result = cls.datetime.datetime.today ()
            return result.time ().replace (microsecond = 0)
        # end def now

    # end class Time

    def __init__ (self, D_Type, exp = None) :
        self.D_Type = D_Type
        self.exp    = exp
    # end def __init__

    @property
    def NOW (self) :
        """Return date/datetime instance for right now."""
        return self.D_Type.now ()
    # end def NOW

    def MONTH (self, m, y) :
        D_Type = self.D_Type
        m      = int (m)
        y      = int (y)
        if m < 12 :
            n  = m + 1
            z  = y
        else :
            n  = 1
            z  = y + 1
        lhs    = D_Type.type (y, m, 1)
        rhs    = D_Type.type (z, n, 1) - D_Type.lom_delta
        return self.exp.BETWEEN (lhs, rhs)
    # end def MONTH

    def QUARTER (self, q, y) :
        D_Type = self.D_Type
        q      = int (q)
        y      = int (y)
        m      = 1 + 3 * (q - 1)
        if q < 4 :
            n  = m + 3
            z  = y
        else :
            n  = 1
            z  = y + 1
        lhs    = D_Type.type (y, m, 1)
        rhs    = D_Type.type (z, n, 1) - D_Type.lom_delta
        return self.exp.BETWEEN (lhs, rhs)
    # end def QUARTER

    def YEAR (self, y) :
        D_Type = self.D_Type
        y      = int (y)
        return self.exp.BETWEEN \
            ( D_Type.type (y,   1, 1)
            , D_Type.type (y+1, 1, 1) - D_Type.lom_delta
            )
    # end def YEAR

# end class _Date_

class _Distributive_ (Q_Root) :
    """Mixin for classes that should distribute AND and OR"""

    def AND (self, * args) :
        if len (args) < 1 :
            raise TypeError \
                ("AND needs at least 1 argument (%s given)" % len (args))
        return self.Q.AND (* tuple (Q.APPLY (a, self) for a in args))
    # end def AND

    def OR (self, * args) :
        if len (args) < 1 :
            raise TypeError \
                ("OR needs at least 1 argument (%s given)" % len (args))
        return self.Q.OR (* tuple (Q.APPLY (a, self) for a in args))
    # end def OR

# end class _Distributive_

@pyk.adapt__bool__
class _Exp_Base_ (Q_Root) :

    ### Equality queries
    @_bin_bool
    def __eq__ (self, rhs) : pass

    @_bin_bool
    def __ne__ (self, rhs) : pass

    def __bool__ (self) :
        return TypeError \
            ("Result of `%s` cannot be used in a boolean context" % (self, ))
    # end def __bool__

    def __hash__ (self) :
        ### Override `__hash__` just to silence DeprecationWarning:
        ###     Overriding __eq__ blocks inheritance of __hash__ in 3.x
        raise NotImplementedError
    # end def __hash__

    ### Unary queries
    @_una_bool
    def __invert__ (self) : pass

# end class _Exp_Base_

@pyk.adapt__div__
class _Exp_ (_Exp_Base_) :
    """Query expression"""

    ### Order queries
    @_bin_bool
    def __ge__ (self, rhs) : pass

    @_bin_bool
    def __gt__ (self, rhs) : pass

    @_bin_bool
    def __le__ (self, rhs) : pass

    @_bin_bool
    def __lt__ (self, rhs) : pass

    ### Binary non-boolean queries
    @_bin_expr
    def __add__ (self, rhs) : pass

    @_bin_expr
    def __floordiv__ (self, rhs) : pass

    @_bin_expr
    def __mod__ (self, rhs) : pass

    @_bin_expr
    def __mul__ (self, rhs) : pass

    @_bin_expr
    def __pow__ (self, rhs) : pass

    @_bin_expr
    def __sub__ (self, rhs) : pass

    @_bin_expr
    def __truediv__ (self, rhs) : pass

    ### Binary non-boolean reflected queries
    @_bin_expr
    def __radd__ (self, rhs) : pass

    @_bin_expr
    def __rfloordiv__ (self, rhs) : pass

    @_bin_expr
    def __rmod__ (self, rhs) : pass

    @_bin_expr
    def __rmul__ (self, rhs) : pass

    @_bin_expr
    def __rpow__ (self, rhs) : pass

    @_bin_expr
    def __rsub__ (self, rhs) : pass

    @_bin_expr
    def __rtruediv__ (self, rhs) : pass

    ### Unary queries
    @_una_expr
    def __neg__ (self) : pass

    ### Method calls
    @_method
    def BETWEEN () :
        def between (val, lhs, rhs) :
            """between(lhs, rhs) -- Returns result of `lhs <= val <= rhs`"""
            return val is not None and lhs <= val <= rhs
        return between
    # end def BETWEEN

    @_method
    def CONTAINS () :
        return operator.contains
    # end def CONTAINS

    @property
    def D (self) :
        return self.Q._Date_ (self.Q._Date_.Date, self)
    DATE = D # end def D

    @property
    def DT (self) :
        return self.Q._Date_ (self.Q._Date_.Date_Time, self)
    DATE_TIME = DT # end def DT

    @_method
    def ENDSWITH () :
        def endswith (l, r) :
            """endswith(r) -- Returns True if `val` ends with the suffix `r`"""
            return l.endswith (r)
        return endswith
    # end def ENDSWITH

    @_method
    def IN () :
        def in_ (val,  rhs) :
            """in_(lhs) -- Returns result of `val in rhs`"""
            return val in rhs
        return in_
    # end def IN

    @_method
    def STARTSWITH () :
        def startswith (l, r) :
            """startswith(r) -- Returns True if `val` starts with the prefix `r`"""
            return l.startswith (r)
        return startswith
    # end def STARTSWITH

    @_method
    def OVERLAPS () :
        def overlaps (l, r) :
            """overlaps(r) -- Returns True if `val` overlaps `r`"""
            return l.overlaps (r)
        return overlaps
    # end def OVERLAPS

# end class _Exp_

@pyk.adapt__div__
class _Exp_B_ (_Exp_Base_) :
    """Query expression for query result of type Boolean"""

    ### Order queries
    @_type_error
    def __ge__ (self, rhs) : pass

    @_type_error
    def __gt__ (self, rhs) : pass

    @_type_error
    def __le__ (self, rhs) : pass

    @_type_error
    def __lt__ (self, rhs) : pass

    ### Binary non-boolean queries
    @_type_error
    def __add__ (self, rhs) : pass

    @_type_error
    def __floordiv__ (self, rhs) : pass

    @_type_error
    def __mod__ (self, rhs) : pass

    @_type_error
    def __mul__ (self, rhs) : pass

    @_type_error
    def __pow__ (self, rhs) : pass

    @_type_error
    def __sub__ (self, rhs) : pass

    @_type_error
    def __truediv__ (self, rhs) : pass

    ### Binary non-boolean reflected queries
    @_type_error
    def __radd__ (self, rhs) : pass

    @_type_error
    def __rfloordiv__ (self, rhs) : pass

    @_type_error
    def __rmod__ (self, rhs) : pass

    @_type_error
    def __rmul__ (self, rhs) : pass

    @_type_error
    def __rpow__ (self, rhs) : pass

    @_type_error
    def __rsub__ (self, rhs) : pass

    @_type_error
    def __rtruediv__ (self, rhs) : pass

# end class _Exp_B_

class _Bool_Bin_Op_ (_Distributive_, _Exp_) :
    """Base class for boolean binary operations `AND` and `OR`"""

    def __new__ (cls, Q, * qs) :
        ### We only want to distribute binary operators if all `qs` are
        ### getters
        if all (isinstance (a, (BVAR, _Distributive_)) for a in qs) :
            return cls.__c_super.__new__ (cls, Q, * qs)
        else :
            return cls._Ancestor (* qs)
    # end def __new__

    def __init__ (self, Q, * qs) :
        self.Q = Q
        self.__super.__init__ (* qs)
    # end def __init__

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        return self.__class__ \
            (Q, * (getattr (p, name) for p in self.predicates))
    # end def __getattr__

    def __getitem__ (self, key) :
        return self.__class__ (Q, * (p [key] for p in self.predicates))
    # end def __getitem__

# end class _Bool_Bin_Op_

@TFL.Add_New_Method (Base)
class _AND_ (_Bool_Bin_Op_, TFL.Filter_And) :
    """Boolean AND operator"""

    _Ancestor = TFL.Filter_And

# end class _AND_

@TFL.Add_New_Method (Base)
class _OR_ (_Bool_Bin_Op_, TFL.Filter_Or) :
    """Boolean OR operator"""

    _Ancestor = TFL.Filter_Or

# end class _OR_

@TFL.Add_New_Method (Base)
class _Get_ (_Distributive_, _Exp_) :
    """Query getter"""

    predicate_precious_p = True

    def __init__ (self, Q, name, getter) :
        self.Q       = Q
        self._name   = name
        self._getter = getter
    # end def __init__

    def predicate (self, obj) :
        Q = self.Q
        try :
            return self._getter (obj)
        except Q.Ignore_Exception as exc :
            return Q.undef
    # end def predicate

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        full_name = ".".join ((self._name, name))
        getter    = getattr (TFL.Getter, full_name)
        return self.__class__ (self.Q, full_name, getter)
    # end def __getattr__

    def __repr__ (self) :
        return "Q.%s" % (self._name, )
    # end def __repr__

# end class _Get_

@TFL.Add_New_Method (Base)
class _NIL_ (_Get_) :
    """Query expression that always evaluates to None."""

    _name      = "NIL"

    def __init__ (self, Q) :
        self.Q = Q
    # end def __init__

    def predicate (self, obj) :
        return None
    # end def predicate

# end class _NIL_

@TFL.Add_New_Method (Base)
class _Self_ (_Get_) :
    """Query reference to object to which query is applied."""

    _name      = "SELF"

    def __init__ (self, Q) :
        self.Q = Q
    # end def __init__

    def predicate (self, obj) :
        return obj
    # end def predicate

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        return getattr (self.Q, name)
    # end def __getattr__

# end class _Self_

class _BVAR_Get_ (TFL.Meta.Object) :
    """Syntactic sugar for creating bound variables for query expressions."""

    _unique_count = 0

    def __init__ (self, Q) :
        self.Q = Q
    # end def __init__

    @property
    def NEW (self) :
        """Create a new unique BVAR"""
        cls                = self.__class__
        cls._unique_count += 1
        name               = "__bv_%d" % (cls._unique_count, )
        return self.BVAR (self.Q, name)
    # end def NEW

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        return self.BVAR (self.Q, name)
    # end def __getattr__

# end class _BVAR_Get_

class _BVAR_Descriptor_ (object) :
    """Descriptor to create bound variables for query expression.

       The descriptor is assigned to `Base` and returns a `_BVAR_Get_`
       instance that is bound to the `Q` object for which the descriptor was
       invoked. The `_BVAR_Get_` instance returns a bound variable for
       each attribute access. Bound variable are `_Exp_` instances and can
       therefore participate in further query expressions like operator
       application or function calls...
    """

    def __get__ (self, obj, cls) :
        if obj is None :
            return self
        return _BVAR_Get_ (obj)
    # end def __get__

# end class _RAW_DESC_

Base.BVAR = _BVAR_Descriptor_ ()

@TFL.Add_New_Method (_BVAR_Get_)
class BVAR (_Exp_) :
    # """Bound variable for query expression."""

    predicate_precious_p = True

    def __init__ (self, Q, name) :
        self.Q      = Q
        self._name  = name
        self._value = None
    # end def __init__

    def bind (self, value) :
        self._value = value
    # end def bind

    def predicate (self, obj) :
        return self._value
    # end def predicate

    def __repr__ (self) :
        return "Q.BVAR.%s" % (self._name, )
    # end def __repr__

# end class BVAR

@TFL.Add_New_Method (Base)
@pyk.adapt__bool__
class BVAR_Man (TFL.Meta.Object) :
    # """Manager for bound variables"""

    def __init__ (self, bvar_man = None) :
        self.bvars    = bvars    = {}
        self.bindings = bindings = {}
        if bvar_man is not None :
            bvars.update    (bvar_man.bvars)
            bindings.update (bvar_man.bindings)
    # end def __init__

    def add (self, * bvars) :
        for bv in bvars :
            self.bvars [bv._name] = bv
    # end def add

    def bind (self, ** bindings) :
        self.bindings.update (bindings)
    # end def bind

    def clone (self) :
        return self.__class__ (self)
    # end def clone

    def __bool__ (self) :
        return bool (self.bvars)
    # end def __bool__

# end class BVAR_Man

def _derive_expr_class (cls, base, name) :
    derived  = base.__class__ \
        ( "_Q_Exp_%s" % name
        , (cls, base)
        , dict
            ( __doc__    = base.__doc__
            , _real_name = name
            )
        )
    setattr (Base, name, derived)
    return derived
# end def _derive_expr_class

_derive_expr_class (_Bin_,  _Exp_B_, "_Bin_Bool_")
_derive_expr_class (_Bin_,  _Exp_,   "_Bin_Expr_")
_derive_expr_class (_Call_, _Exp_B_, "_Call_Bool_")
_derive_expr_class (_Una_,  _Exp_B_, "_Una_Bool_")
_derive_expr_class (_Una_,  _Exp_,   "_Una_Expr_")

def _derive_aggr_class (name, fun, doc) :
    _aggr_fun = staticmethod (fun)
    cls = _Aggr_.derived \
        ( _Aggr_.__class__
            (name, (_Aggr_, ), dict (__doc__ = doc, _aggr_fun = _aggr_fun))
        )
    expr_cls = _derive_expr_class (cls, _Exp_, "%sExpr" % (name, ))
    @TFL.Attributed (__name__ = cls.op_name)
    def _ (self, rhs = 1) :
        T = getattr (self, expr_cls.__name__)
        return T (self, rhs)
    setattr (Base, cls.op_name, _)
    return cls
# end def _derive_aggr_class

_derive_aggr_class ("_Avg_",   average, "Query function building the average")
_derive_aggr_class ("_Count_", len,     "Query function finding the count")
_derive_aggr_class ("_Max_",   max,     "Query function finding the maximum")
_derive_aggr_class ("_Min_",   min,     "Query function finding the minimum")
_derive_aggr_class ("_Sum_",   sum,     "Query function building the sum")

###############################################################################
### Generic functions to display Q expressions
@TFL.Add_To_Class ("DISPLAY", Base)
@Single_Dispatch
def display (q) :
    return str (q)
# end def display

@display.add_type (_Bin_)
def _display_bin_ (q) :
    rs = "/r" if q.reverse else ""
    lhs, rhs = q.lhs, q.rhs
    return "%s%s (%s, %s)" % \
        (normalized_op_name (q.op.__name__), rs, display (lhs), display (rhs))
# end def _display_bin_

@display.add_type (_Una_)
def _display_una_ (q) :
    return "%s (%s)" % (normalized_op_name (q.op.__name__), display (q.lhs))
# end def _display_una_

@display.add_type (_Call_)
def _display_call_ (q) :
    args = (q.lhs, ) + q.args
    return "Call:%s: (%s)" % \
        ( normalized_op_name (q.op.__name__)
        , ", ".join (display (a) for a in args)
        )
# end def _display_call_

@display.add_type (TFL._Filter_Q_)
def _display_filter_q_ (q) :
    return "Q.%s (%s)" % \
        ( q.op_name.upper ()
        , ", ".join (display (a) for a in q.predicates)
        )
# end def _display_filter_q_

### «text» ### start of documentation
__doc__ = r"""
This module implements a query expression language. It exports the query
generator instance :obj:`Q` which is used to define symbolic query expressions.
A query expression generated by `Q` is a Python callable: applying a
Q-expression to a python object evaluates the query expression for that object
and returns the result of that evaluation.

One can pass Q-expressions to `filter` or use them as `key` argument
to Python's `sorted` function.

You can use the following binary operators in Q-expressions:

    >>> print (", ".join (sorted (set (Q._Bin_.op_map.values()))))
    %, *, **, +, -, /, //, <, <=, ==, >, >=

You can use the following unary operators in Q-expressions:

    >>> print (", ".join (sorted (set (Q._Una_.op_map.values()))))
    -, ~

You can use the following query functions in Q-expressions:

    >>> print (", ".join (sorted (set (Q._Call_.op_map.values()))))
    BETWEEN, CONTAINS, ENDSWITH, IN, OVERLAPS, STARTSWITH

You can use the following logical operators in Q-expressions:

    >>> print (", ".join (sorted (set (Q.Q_Root.op_map.values()))))
    &, |, ~

Beware: the predecence of the logical operators is very low, i.e., parentheses
around the operands are strongly recommended. Alternatively, one can use:

    `Q.AND (lhs, rhs)`

instead of:

   `lhs & rhs`

`Q.OR` instead of `|`, and `Q.NOT` instead of `~`. `Q.AND` and `Q.OR` take
arbitrarily many operands.

`Q.AND` and `Q.OR` are distributive, i.e., an expression like:

    `Q.OR (Q.foo, Q.bar) == 42`

will evaluate like:

    `Q.OR (Q.foo == 42, Q.bar == 42)`

.. data:: Q

  `Q` is an instance of :class:`Base`.

  - `Q.foo` accesses the attribute with name ``foo``.

  - `Q.foo.qux` accesses the attribute `qux` of the attribute `foo`.

  - `Q.foo == 42` evaluates to True if attribute ``foo`` has the value 42.

  - `Q.foo.STARTSWITH (Q.bar)` evaluates to True if the value of attribute
    ``foo`` starts with the value of the attribute ``bar``.

  - `Q.NIL` always evaluates to None, no matter what object the q-expression is
    applied to.

  - `Q.SELF` evaluates to the object the q-expression is applied to.

Python handles `a < b < c` as `(a < b) and (b < c)`. Unfortunately, there is
no way to simulate this by defining operator methods. Therefore,
Q-expressions raise a TypeError to signal that an expression like
`Q.a < Q.b < Q.c` isn't possible::

    >>> with expect_except (TypeError) :
    ...     Q.a < Q.b < Q.c # doctest:+ELLIPSIS
    TypeError: ...

Query operators with boolean results, i.e., equality and ordering operators,
cannot be used with any operators except `==` and `!=`::

    >>> (Q.a < Q.b) == Q.c
    Q.a < Q.b == Q.c
    >>> with expect_except (TypeError) :
    ...     (Q.a < Q.b) < Q.c
    TypeError: Operator `<` not applicable to boolean result of `Q.a < Q.b`, rhs: `Q.c`

.. autoclass:: _Exp_
  :members:

"""

### «text» ### start of test
_test_q = """
This module implements a query expression language::

    >>> from _TFL.Record import Record as R
    >>> from datetime import date, datetime
    >>> r1 = R (foo = 42, bar = 137, baz = 11, quux = R (a = 1, b = 200))
    >>> r2 = R (foo = 3,  bar = 9,   qux = "abcdef", d = date (2010, 12, 14), dt = datetime (2010, 12, 14, 11, 36))
    >>> r3 = R (foo = 42, bar = "AbCd", baz = "ABCD", qux = "abcd")
    >>> r4 = R (foo = 45)
    >>> q0 = Q.foo
    >>> q0._name
    'foo'
    >>> q0.predicate (r1)
    42

    >>> qm = - q0
    >>> qm
    - Q.foo
    >>> qm.predicate (r1)
    -42

    >>> q1 = Q.foo == Q.bar
    >>> q1, q1.lhs, q1.rhs, normalized_op_name (q1.op.__name__)
    (Q.foo == Q.bar, Q.foo, Q.bar, 'eq')
    >>> q1.lhs._name, q1.rhs._name
    ('foo', 'bar')
    >>> q1.predicate (r1)
    False

    >>> q2 = Q.foo + Q.bar
    >>> q2, q2.lhs, q2.rhs, normalized_op_name (q2.op.__name__)
    (Q.foo + Q.bar, Q.foo, Q.bar, 'add')
    >>> q2.predicate (r1)
    179

    >>> q3 = Q.foo % Q.bar == Q.baz
    >>> q3, q3.lhs, q3.rhs
    (Q.foo % Q.bar == Q.baz, Q.foo % Q.bar, Q.baz)
    >>> q3.predicate (r1)
    False
    >>> q4 = Q.bar % Q.foo
    >>> q4.predicate (r1), Q.baz.predicate (r1)
    (11, 11)
    >>> (q4 == Q.baz).predicate (r1)
    True
    >>> (~ (q4 == Q.baz)).predicate (r1)
    False

    >>> q3.lhs.predicate (r1)
    42

    >>> q5 = Q.foo.BETWEEN (10, 100)
    >>> q5, q5.lhs, q5.args, normalized_op_name (q5.op.__name__)
    (Q.foo.between (10, 100), Q.foo, (10, 100), 'between')
    >>> q5.predicate (r1)
    True
    >>> q5.predicate (r2)
    False

    >>> q6 = Q.foo.IN ((1, 3, 9, 27))
    >>> q6.predicate (r1)
    False
    >>> q6.predicate (r2)
    True

    >>> QQ = Q.__class__ (Ignore_Exception = (AttributeError, ))
    >>> QQ.qux.predicate (r1) is QQ.undef
    True
    >>> with expect_except (AttributeError) :
    ...     Q.qux.predicate (r1) is Q.undef
    AttributeError: qux

    >>> q7 = QQ.qux.CONTAINS ("bc")
    >>> q7.predicate (r1)
    >>> q7.predicate (r2)
    True
    >>> q8 = QQ.qux.ENDSWITH ("fg")
    >>> q8.predicate (r1)
    >>> q8.predicate (r2)
    False
    >>> q9 = QQ.qux.ENDSWITH ("ef")
    >>> q9.predicate (r1)
    >>> q9.predicate (r2)
    True

    >>> qa = QQ.qux.STARTSWITH ("abc")
    >>> qa.predicate (r1)
    >>> qa.predicate (r2)
    True

    >>> Q [0] ((2,4))
    2
    >>> Q [1] ((2,4))
    4
    >>> Q [-1] ((2,4))
    4
    >>> Q [-2] ((2,4))
    2

    >>> Q.foo * -1
    Q.foo * -1
    >>> -1 * Q.foo
    -1 * Q.foo

    >>> qm = Q.foo.D.MONTH (2, 2010)
    >>> qm, qm.lhs, normalized_op_name (qm.op.__name__)
    (Q.foo.between (datetime.date(2010, 2, 1), datetime.date(2010, 2, 28)), Q.foo, 'between')

    >>> Q.foo.D.MONTH (2, 2000)
    Q.foo.between (datetime.date(2000, 2, 1), datetime.date(2000, 2, 29))

    >>> Q.foo.DT.QUARTER (4, 2010)
    Q.foo.between (datetime.datetime(2010, 10, 1, 0, 0), datetime.datetime(2010, 12, 31, 23, 59, 59))

    >>> Q.foo.D.YEAR (2011)
    Q.foo.between (datetime.date(2011, 1, 1), datetime.date(2011, 12, 31))
    >>> Q.foo.DT.YEAR (2012)
    Q.foo.between (datetime.datetime(2012, 1, 1, 0, 0), datetime.datetime(2012, 12, 31, 23, 59, 59))

    >>> Q.d.D.MONTH (12, 2010) (r2)
    True
    >>> Q.d.D.MONTH (1, 2010) (r2)
    False
    >>> Q.d.D.QUARTER (4, 2010) (r2)
    True
    >>> with expect_except (TypeError) :
    ...     Q.dt.D.QUARTER (4, 2010) (r2)
    TypeError: can't compare datetime.datetime to datetime.date
    >>> Q.dt.DT.QUARTER (4, 2010) (r2)
    True

    >>> (Q.bar == Q.baz) (r3)
    False
    >>> Q.bar.STARTSWITH ("ab") (r3)
    False
    >>> Q.bar.CONTAINS ("bc") (r3)
    False

    >>> print ("%.3f" % ((Q.foo / 7) (r4), ))
    6.429
    >>> (Q.foo // 7) (r4)
    6
    >>> print ("%.3f" % ((70 / Q.foo) (r4), ))
    1.556
    >>> (70 // Q.foo) (r4)
    1

    >>> Q.a < Q.b + Q.c
    Q.a < Q.b + Q.c
    >>> Q.z + Q.a < Q.b + Q.c
    Q.z + Q.a < Q.b + Q.c
    >>> (Q.a < Q.b) == (Q.a % 2)
    Q.a < Q.b == Q.a % 2
    >>> (Q.a < Q.b) == (Q.a > 2)
    Q.a < Q.b == Q.a > 2
    >>> q = (Q.a < Q.b) == (Q.a % 2)
    >>> q.lhs
    Q.a < Q.b
    >>> q.rhs
    Q.a % 2
    >>> display (q)
    'eq (lt (Q.a, Q.b), mod (Q.a, 2))'

But explicit parenthesis are necessary in some cases::

    >>> with expect_except (TypeError) :
    ...     Q.a < Q.b == Q.a % 2 # doctest:+ELLIPSIS
    TypeError: ...

Queries for nested attributes are also possible::

    >>> qn = Q.quux.a
    >>> qn._name
    'quux.a'
    >>> qn.predicate (r1)
    1
    >>> qm = Q.quux.b
    >>> qm.predicate (r1)
    200
    >>> (qn > Q.foo) (r1)
    False
    >>> (qm > Q.foo) (r1)
    True

`display` (also available as `TFL.Q.DISPLAY`) displays the structure of
Q-expressions::

    >>> display (Q.foo < 42)
    'lt (Q.foo, 42)'
    >>> display (42 <= Q.foo)
    'ge (Q.foo, 42)'

    >>> display (Q.foo * 42)
    'mul (Q.foo, 42)'
    >>> display (Q.foo / 42)
    'truediv (Q.foo, 42)'
    >>> display (Q.foo // 42)
    'floordiv (Q.foo, 42)'

    >>> display (42 / Q.foo)
    'truediv/r (Q.foo, 42)'
    >>> display (42 * Q.foo)
    'mul/r (Q.foo, 42)'

    >>> Q.DISPLAY (Q.foo % 2 == 0)
    'eq (mod (Q.foo, 2), 0)'
    >>> Q.DISPLAY (Q.foo % 2 == Q.bar * 3)
    'eq (mod (Q.foo, 2), mul (Q.bar, 3))'
    >>> Q.DISPLAY (Q.foo % 2 == -Q.bar * 3)
    'eq (mod (Q.foo, 2), mul (neg (Q.bar), 3))'
    >>> Q.DISPLAY (- (Q.foo % 2 * -Q.bar / 3))
    'neg (truediv (mul (mod (Q.foo, 2), neg (Q.bar)), 3))'

    >>> Q.DISPLAY (~ (Q.foo % 2 * -Q.bar / 3))
    'not (truediv (mul (mod (Q.foo, 2), neg (Q.bar)), 3))'

    >>> Q.DISPLAY (Q.baz.STARTSWITH ("qux"))
    'Call:startswith: (Q.baz, qux)'

    >>> Q.DISPLAY (Q.foo.D.YEAR (2013))
    'Call:between: (Q.foo, 2013-01-01, 2013-12-31)'

    >>> Q.DISPLAY (Q.foo.IN ((1, 2, 3)))
    'Call:in: (Q.foo, (1, 2, 3))'

`Q.BVAR` supports queries with bound variables::

    >>> Q.foo == Q.BVAR.bar
    Q.foo == Q.BVAR.bar

    >>> Q.BVAR.foo == 42
    Q.BVAR.foo == 42

    >>> Q.baz == Q.BVAR.NEW
    Q.baz == Q.BVAR.__bv_1

`Base` examples::

    >>> r1 = R (foo = 42, bar = 137, baz = 11)
    >>> q0 = Q.foo
    >>> q0
    Q.foo
    >>> q0._name
    'foo'
    >>> q0.predicate (r1)
    42

    >>> Q.fool.STARTSWITH ("bar") (R (fool = "barfly"))
    True
    >>> Q.fool.STARTSWITH ("fly") (R (fool = "barfly"))
    False
    >>> Q.fool.ENDSWITH ("fly") (R (fool = "barfly"))
    True
    >>> Q.fool.ENDSWITH ("bar") (R (fool = "barfly"))
    False
    >>> Q.fool.BETWEEN (2, 8) (R (fool = 1))
    False
    >>> Q.fool.BETWEEN (2, 8) (R (fool = 2))
    True
    >>> Q.fool.BETWEEN (2, 8) (R (fool = 3))
    True
    >>> Q.fool.BETWEEN (2, 8) (R (fool = 8))
    True
    >>> Q.fool.BETWEEN (2, 8) (R (fool = 9))
    False
    >>> (Q.fool == "barfly") (R (fool = "barfly"))
    True
    >>> (Q.fool != "barfly") (R (fool = "barfly"))
    False
    >>> (Q.fool != "barflyz") (R (fool = "barfly"))
    True
    >>> (Q.fool <= "barflyz") (R (fool = "barfly"))
    True
    >>> (Q.fool >= "barflyz") (R (fool = "barfly"))
    False
    >>> Q.fool.CONTAINS ("barf") (R (fool = "a barfly "))
    True
    >>> Q.fool.IN ([2,4,8]) (R (fool = 1))
    False
    >>> Q.fool.IN ([2,4,8]) (R (fool = 2))
    True
    >>> Q.fool.IN ([2,4,8]) (R (fool = 3))
    False
    >>> Q.fool.IN ([2,4,8]) (R (fool = 4))
    True
    >>> (Q.fool % 2) (R (fool = 20))
    0

    >>> r3 = R (foo = 42, bar = "AbCd", baz = "ABCD", qux = "abcd")
    >>> ((Q.bar == Q.baz) & (Q.baz == Q.qux)) (r3)
    False

    >>> Q.DISPLAY (Q.NOT (Q.foo % 2 * -Q.bar / 3))
    '<Filter_Not NOT Q.foo % 2 * - Q.bar / 3>'

    >>> Q.foo & Q.bar
    <_AND_ [Q.foo, Q.bar]>

    >>> (Q.foo | Q.bar) > 0
    <Filter_Or [Q.foo > 0, Q.bar > 0]>

    >>> Q.OR (Q.foo, Q.bar, Q.baz)
    <_OR_ [Q.foo, Q.bar, Q.baz]>

    >>> Q.OR (Q.foo, Q.bar, Q.baz).qux
    <_OR_ [Q.foo.qux, Q.bar.qux, Q.baz.qux]>

    >>> Q.OR (Q.foo, Q.bar, Q.baz) == 42
    <Filter_Or [Q.foo == 42, Q.bar == 42, Q.baz == 42]>

    >>> Q.OR (Q.foo, Q.bar, Q.baz).qux < 137
    <Filter_Or [Q.foo.qux < 137, Q.bar.qux < 137, Q.baz.qux < 137]>

    >>> Q.foo.bar.OR (Q.baz, Q.qux)
    <_OR_ [Q.foo.bar.baz, Q.foo.bar.qux]>

    >>> Q.foo.bar.OR (Q.baz, Q.qux) > 23
    <Filter_Or [Q.foo.bar.baz > 23, Q.foo.bar.qux > 23]>

    >>> r1
    Record (bar = 137, baz = 11, foo = 42)

    >>> (Q.OR (Q.foo, Q.bar, Q.baz) == 42) (r1)
    True

    >>> (Q.OR (Q.foo, Q.bar, Q.baz) == 137) (r1)
    True

    >>> (Q.OR (Q.foo, Q.bar, Q.baz) == 11) (r1)
    True

    >>> (Q.OR (Q.foo, Q.bar, Q.baz) == 23) (r1)
    False

"""

__test__ = dict \
    ( test_doc = __doc__
    , test_q   = _test_q
    )

if __name__ != "__main__" :
    TFL._Export ("Q")
    TFL._Export_Module ()
### __END__ TFL.Q_Exp
