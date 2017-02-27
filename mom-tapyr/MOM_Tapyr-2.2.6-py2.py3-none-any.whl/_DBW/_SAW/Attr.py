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
#    MOM.DBW.SAW.Attr
#
# Purpose
#    Attribute handling for SAW
#
# Revision Dates
#    25-Jun-2013 (CT) Creation
#     1-Jul-2013 (CT) Change 3rd arg of `Kind_Wrapper` from `prefix` to `outer`
#     1-Jul-2013 (CT) Add `Kind_Wrapper.col_values`
#     2-Jul-2013 (CT) Factor `col_values_from_cargo`, add `row_as_pickle_cargo`
#     3-Jul-2013 (CT) Change `Kind_Wrapper.raw_name` to put `__raw` in front
#     3-Jul-2013 (CT) Add `Kind_Wrapper_Q`, factor `_Kind_Wrapper_`
#     3-Jul-2013 (CT) Add `_Kind_Wrapper_.Derived`, `.eff`, `.q_able_names`
#     4-Jul-2013 (CT) Change `Kind_Wrapper.columns` to return `eff.columns`,
#                     if any
#     4-Jul-2013 (CT) Add `Kind_Wrapper_C.q_able_attrs`
#     4-Jul-2013 (CT) Add `Kind_Wrapper.name` and use in `__str__`
#     4-Jul-2013 (CT) Factor `pc_transform`, `col_values*`, and
#                     `row_as_pickle_cargo` up to `_Kind_Wrapper_`
#     5-Jul-2013 (CT) Add `prefix` to `q_able_names`; add `update_col_map`
#     8-Jul-2013 (CT) Use `.ATW.SA_Type`; add `_saw_column_type_type_name`
#     8-Jul-2013 (CT) Add `q_exp_get` to `_Kind_Wrapper_`
#     8-Jul-2013 (CT) Add `Kind_Wrapper_S`
#     9-Jul-2013 (CT) Split `Kind_Wrapper_P` from `Kind_Wrapper_Q`,
#                     add `q_exp_get` to them and `Kind_Wrapper_C`
#     9-Jul-2013 (CT) Add `q_exp_bin` to `_Kind_Wrapper_`
#    10-Jul-2013 (CT) Set `_SAW` of kind descriptors
#    10-Jul-2013 (CT) Add `Kind_Wrapper_R` for `_Rev_Query_` attributes
#    11-Jul-2013 (CT) Implement `Kind_Wrapper_R.q_exp_get`
#    11-Jul-2013 (CT) Add `QR.polymorphic` to force `outerjoin` when necessary
#    12-Jul-2013 (CT) Add `q_exp_call`, `q_exp_func`, `q_exp_una`
#    12-Jul-2013 (CT) Add support for `sqx_filter` to `Kind_Wrapper_R`
#    12-Jul-2013 (CT) Reify `A_Join`
#    15-Jul-2013 (CT) Add `q_exp_get_ob`
#    15-Jul-2013 (CT) Redefine `_q_exp_bin_combine` for
#                     `Kind_Wrapper_C`, `Kind_Wrapper_S`,
#                     and `Kind_Wrapper_R`
#    18-Jul-2013 (CT) Deal with instances of `.attr.E_Type` in
#                     `Kind_Wrapper_C._q_exp_bin_combine`
#    19-Jul-2013 (CT) Add support for `Q.RAW`
#    21-Jul-2013 (CT) Change `Kind_Wrapper_C._q_exp_bin_combine` to
#                     delegate dealing with nested attributes to `.__super`
#    21-Jul-2013 (CT) Fix `Kind_Wrapper_Q.q_exp_get`
#                     (pass self.outer to `sf`, if any)
#    21-Jul-2013 (CT) Fix `Kind_Wrapper_S.q_exp_get` (`jxs`)
#    21-Jul-2013 (CT) Fix `Kind_Wrapper_R._q_exp_bin_combine` (don't add joins)
#    22-Jul-2013 (CT) Add `alias`, use `attr_join_etw_alias`
#    23-Jul-2013 (CT) Add `_setup_alias_columns`, `_setup_alias_attrs`
#    23-Jul-2013 (CT) Redefine `Kind_Wrapper_P.q_exp_bin` and
#                     change `Kind_Wrapper_R._wrap_super_q_exp` to
#                     * OR-combine children's expressions
#    23-Jul-2013 (CT) Add `Kind_Wrapper_C.__getattr__` to trigger `QC`
#    23-Jul-2013 (CT) Factor `_column_joins`, `_column_joins_pkn`
#    24-Jul-2013 (CT) Fix handling of extra columns due to `sqx_filter`
#    30-Jul-2013 (CT) Don't pass `tail_name` to kind-wrapper for `tail_name`
#    30-Jul-2013 (CT) Support `tail_name` in `Kind_Wrapper_Q.q_exp_get`
#    30-Jul-2013 (CT) Change `Kind_Wrapper_P.q_exp_bin` to use
#                     `_q_exp_bin_cols` and `_q_exp_bin_combine`,
#                     not `__super.q_exp_bin`
#    30-Jul-2013 (CT) Redefine `Kind_Wrapper_P.q_exp_call`, `.q_exp_func`
#    30-Jul-2013 (CT) Factor `_q_exp_bin_cols` and `_q_exp_call_parts`
#    30-Jul-2013 (CT) Add support for column attributes like `Date_Column.year`
#                     (`_col_from_key`, `_saw_col_from_key`)
#     1-Aug-2013 (CT) Add support for `MD_Change` to `_q_exp_bin_cols`
#     3-Aug-2013 (CT) Change `col_values_from_cargo` to use `default`, not
#                     `None`, for non-nullable columns
#     4-Aug-2013 (CT) Add `fix_bool` and `_saw_bool` methods
#     4-Aug-2013 (CT) Add and use Single_Dispatch_Method `_saw_kind_wrapper`
#     4-Aug-2013 (CT) Add `Kind_Wrapper_Date`, `Kind_Date_Time_Wrapper`, and
#                     `Kind_Wrapper_Time` plus the supporting infrastructure
#     6-Aug-2013 (CT) Factor `_q_exp_bin_apply`, `_q_exp_call_apply`
#     6-Aug-2013 (CT) Add optional argument `columns` to `update_col_map`
#     6-Aug-2013 (CT) Use `.attr._saw_kind_wrapper`, if any
#     9-Aug-2013 (CT) Factor `_col_q_able_names`, redefine for
#                     `Kind_Wrapper_S`
#     9-Aug-2013 (CT) Use `self.kind`, not `self.eff.kind`, unless accessing
#                     `columns`
#    25-Aug-2013 (CT) Use `MOM.Id_Entity.E_Spec._Attributes`
#    25-Aug-2013 (CT) Add `default` to `_saw_column_kw`, `_saw_columns_raw_kind`
#    26-Aug-2013 (CT) Add `col_args` to `_saw_columns_surrogate`
#    30-Aug-2013 (CT) Move defaults for `fields` to `_Kind_Wrapper_`
#     2-Sep-2013 (CT) Change `_Kind_Wrapper_.__init__` to set  `e_type`
#     2-Sep-2013 (CT) Change `A_Join.__repr__` to display table aliases properly
#    20-Sep-2013 (CT) Remove `q_exp_*` methods (superseded by SAW.QX)
#    30-Sep-2013 (CT) Return `Kind_Wrapper_P` if `self.is_partial` from
#                     `_saw_kind_wrapper_pq`
#     6-Mar-2014 (CT) Fix `parent` of nested attributes in
#                     `Kind_Wrapper_C._setup_attrs` and `._setup_alias_attrs`
#    11-Jul-2014 (CT) Fix `_saw_column_type` for `if pts._Pickler_Type`
#    12-Sep-2014 (CT) Add `A_Join.key` including `t_col`
#    27-Apr-2015 (CT) Add `unique_p`, `use_index` to `_saw_one_typed_column`
#    16-Jun-2016 (CT) Add `_saw_column_type` to `_A_Decimal_`, not `A_Decimal`
#    16-Jun-2016 (CT) Use `.SA_Type.Decimal`, not `..Numeric`, for `_A_Decimal_`
#    21-Jul-2016 (CT) Add `** kw` to `_saw_columns*`
#    22-Jul-2016 (CT) Factor `_Kind_Wrapper_C_`
#     3-Aug-2016 (CT) Add `Kind_Wrapper_Structured_Field_Extractor`
#                     + factor `_Kind_Wrapper_Structured_`
#     3-Aug-2016 (CT) Add `_Kind_Wrapper_CX_`, `_M_Kind_Wrapper_`
#     9-Aug-2016 (CT) Add optional arg `attr` to `_Kind_Wrapper_.__init__`
#    21-Sep-2016 (CT) Add `_saw_column_type` for `A_Time_X`
#    22-Sep-2016 (CT) Add `_saw_cooked`
#    23-Sep-2016 (CT) Remove unused `fix_bool`
#    ««revision-date»»···
#--

from   __future__                 import division, print_function
from   __future__                 import absolute_import, unicode_literals

from   _MOM                       import MOM
from   _TFL                       import TFL
from   _TFL.pyk                   import pyk

from   _MOM._DBW._SAW             import SAW, SA
from   _MOM.SQ                    import Q

import _MOM._Attr.Type
import _MOM._DBW._SAW.Manager

from   _TFL._Meta.Single_Dispatch import Single_Dispatch_Method
from   _TFL.Decorator             import getattr_safe
from   _TFL.predicate             import \
    bool_split, filtered_join, rsplit_hst, uniq

import _TFL._Meta.Object
import _TFL.Accessor
import _TFL.Decorator

import datetime
import functools
import itertools
import math
import operator

MOM.Attr.A_Attr_Type.SAW_Column_Type = SA.schema.Column

class A_Join (TFL.Meta.Object) :
    """Encapsulate a join bound to an attribute"""

    special_col_names = ("left", "middle", "pid", "right")

    def __init__ (self, toc, s_col, t_col, joiner, op = None) :
        self.table  = table = \
            toc if not isinstance (toc, SA.schema.Column) else toc.table
        self.cols   = s_col, t_col
        self.joiner = joiner
        self.key    = table if t_col.name in self.special_col_names \
            else (table, t_col)
        self.op     = op if op is not None else operator.__eq__
    # end def __init__

    def __call__ (self, toj) :
        """Join to table or join `toj`"""
        return self.joiner (toj, self.table, self.op (* self.cols))
    # end def __call__

    def __repr__ (self) :
        name = self.table.name
        return "<%s %s on (%s, %s)>" % \
            ((self.__class__.__name__, name) + self.cols)
    # end def __repr__

# end class A_Join

class _Kind_Wrapper_CX_ (TFL.Meta.Object) :

    is_required      = False

    def __init__ (self, cx, * args, ** kw) :
        self._cx = cx
        self.__super.__init__ (* args, ** kw)
        cx.MOM_Is_Raw  = False
        cx.MOM_Wrapper = self
    # end def __init__

    @TFL.Meta.Once_Property
    def columns (self) :
        return [self._cx]
    # end def columns

# end class _Kind_Wrapper_CX_

class _M_Kind_Wrapper_ (TFL.Meta.Object.__class__) :

    @TFL.Meta.Once_Property_NI
    def CXT (cls) :
        if not cls.__name__.startswith ("_") :
            result = cls.__class__ \
                ( cls.__name__ + "__CX"
                , (_Kind_Wrapper_CX_, cls)
                , dict
                    ( __module__ = cls.__module__
                    )
                )
            return result
    # end def CXT

# end class _M_Kind_Wrapper_

class _Kind_Wrapper_ \
          (TFL.Meta.BaM (TFL.Meta.Object, metaclass = _M_Kind_Wrapper_)) :

    columns         = ()
    db_attrs_o      = db_attrs     = {}
    fields          = set ()
    q_able_attrs_o  = q_able_attrs = {}

    _ETW            = TFL.Meta.Alias_Property ("ETW")

    def __init__ (self, ETW, kind, outer = None, parent = None, attr = None) :
        self.ATW    = ETW.ATW
        self.ETW    = ETW
        self.PNS    = ETW.PNS
        self.DBW    = ETW.PNS.Manager
        self.e_type = ETW.e_type
        self.kind   = kind
        self.attr   = kind.attr if attr is None else attr
        self.outer  = outer
        self.eff    = parent if parent is not None else self
    # end def __init__

    @TFL.Meta.Once_Property
    def ckd_name (self) :
        return filtered_join \
            ("__", (self.prefix, self.eff.attr._saw_column_name))
    # end def ckd_name

    @TFL.Meta.Once_Property
    def is_required (self) :
        return self.kind.is_required
    # end def is_required

    @TFL.Meta.Once_Property
    def is_surrogate (self) :
        return isinstance (self.eff.attr, MOM.Attr.A_Surrogate)
    # end def is_surrogate

    @TFL.Meta.Once_Property
    def name (self) :
        return filtered_join (".", (self.prefix, self.eff.attr.name))
    # end def name

    @TFL.Meta.Once_Property
    def prefix (self) :
        outer = self.outer
        if outer :
            return outer.ckd_name
        return ""
    # end def prefix

    @TFL.Meta.Once_Property
    def q_able_names (self) :
        result = self.attr.q_able_names
        if self is not self.eff :
            result = uniq (itertools.chain (result, self.eff.q_able_names))
        prefix = self.prefix
        if prefix :
            result = (".".join ((prefix, name)) for name in result)
        return tuple (sorted (result))
    # end def q_able_names

    @TFL.Meta.Once_Property
    def raw_name (self) :
        return filtered_join ("__", (self.prefix, self.eff.attr.raw_name))
    # end def raw_name

    @TFL.Meta.Once_Property
    def unique (self) :
        return (self.ckd_name, ) if self.eff.kind.is_primary else ()
    # end def unique

    def alias (self, ETW_alias, ** kw) :
        cls    = self.__class__
        result = cls.__new__      (cls)
        result.__dict__.update    (self.__dict__, ETW = ETW_alias, ** kw)
        self._setup_alias_columns (ETW_alias, result)
        return result
    # end def alias

    def col_values (self, entity) :
        return self.col_values_from_cargo (self.kind.get_pickle_cargo (entity))
    # end def col_values

    def col_values_from_cargo (self, pickle_cargo) :
        is_surrogate = self.is_surrogate
        for column, value in zip (self.columns, pickle_cargo) :
            if value is None :
                if is_surrogate :
                    continue
                elif not column.nullable :
                    try :
                        kind  = column.MOM_Kind
                        value = kind.raw_default \
                            if column.MOM_Is_Raw else kind.default
                    except AttributeError as exc :
                        print \
                            ( "*" * 3, self
                            , ".col_values_from_cargo got exception for"
                            , column, "MOM_Kind.default: ", exc
                            )
                        continue
            yield column.name, value
    # end def col_values

    def Derived (self, ETW, kind, outer = None) :
        if kind is self.kind :
            return self
        else :
            return self.__class__ (ETW, kind, outer = outer, parent = self.eff)
    # end def Derived

    def row_as_pickle_cargo (self, row) :
        result = tuple (row [c] for c in self.columns)
        return result
    # end def row_as_pickle_cargo

    def update_col_map (self, mapper, col_map, prefix = None, columns = None) :
        if columns is None :
            columns = self.columns
        for col in columns :
            names = self._col_q_able_names (col)
            for n in names :
                if prefix :
                    if n.startswith (prefix) :
                        n = n [len (prefix) + 1:]
                if n in col_map :
                    c_col = col_map [n]
                    if c_col is not col :
                        print \
                            ( "%s Name conflict for %s %r %r"
                            % ("*" * 5, self, c_col, col)
                            )
                else :
                    col_map [n] = col
    # end def update_col_map

    def _col_q_able_names (self, col) :
        w = col.MOM_Wrapper
        return (w.raw_name, ) if col.MOM_Is_Raw else w.q_able_names
    # end def _col_q_able_names

    def _column_joins (self, cols, head_col, joiner) :
        for col in cols :
            try :
                ### only do this for real columns
                ctab = col.table
            except AttributeError :
                pass
            else :
                yield (A_Join (col, col, head_col, joiner))
    # end def _column_joins

    def _column_joins_pkn (self, ETW, cols, head_col, joiner) :
        pkn = ETW.spk_name
        for col in cols :
            try :
                ### only do this for real columns
                ctab = col.table
            except AttributeError :
                pass
            else :
                yield (A_Join (col, ctab.c [pkn], head_col, joiner))
    # end def _column_joins_pkn

    def _setup_alias_columns (self, ETW_alias, result) :
        def _gen (self, ETW_alias, result) :
            for c in self.columns :
                ac             = ETW_alias._get_sa_col_alias (c)
                ac.MOM_Is_Raw  = getattr (c, "MOM_Is_Raw", False)
                ac.MOM_Kind    = self.kind
                ac.MOM_Wrapper = result
                yield ac
        result.__dict__ ["columns"] = tuple (_gen (self, ETW_alias, result))
    # end def _setup_alias_columns

    def __repr__ (self) :
        attr = self.attr
        return "<SAW : %s `%s` [%s]>" % \
            (attr.typ, self.name, ", ".join (str (c) for c in self.columns))
    # end def __repr__

# end class _Kind_Wrapper_

@TFL.Add_To_Class ("_SAW_Wrapper", MOM.Attr._DB_Attr_)
class Kind_Wrapper (_Kind_Wrapper_) :
    """SAW specific information about a db-attribute kind descriptor in
       the context of a specific E_Type_Wrapper
    """

    @TFL.Meta.Once_Property
    def columns (self) :
        eff = self.eff
        if eff is self :
            return self.kind._saw_columns (self.DBW, self)
        else :
            return eff.columns
    # end def columns

# end class Kind_Wrapper

@TFL.Add_To_Class ("_SAW_Wrapper", MOM.Attr._EPK_Mixin_)
class Kind_Wrapper_S (Kind_Wrapper) :
    """SAW specific information about an epk-referring db-attribute kind
       descriptor in the context of a specific E_Type_Wrapper
    """

    def _col_q_able_names (self, col) :
        ### Use `self.q_able_names` here to support derived attributes with
        ### q-able additional names, e.g., link roles
        return self.q_able_names
    # end def _col_q_able_names

# end class Kind_Wrapper_S

class _Kind_Wrapper_PQ_ (_Kind_Wrapper_) :

    @property
    def MOM_Wrapper (self) :
        return self
    # end def MOM_Wrapper

    @property
    def type_name (self) :
        return "%-40.40s" % (self, )
    # end def type_name

    def update_col_map (self, mapper, col_map, prefix = None) :
        if self.outer :
            col_map [self.attr.name] = self
        else :
            col_map.update ((qn, self) for qn in self.q_able_names)
    # end def update_col_map

# end class _Kind_Wrapper_PQ_

@TFL.Add_To_Class ("_SAW_Wrapper_PQ", MOM.Attr._DB_Attr_)
class Kind_Wrapper_P (_Kind_Wrapper_PQ_) :
    """SAW specific information about a partial db-attribute kind
       descriptor in the context of a specific E_Type_Wrapper
    """

    def __repr__ (self) :
        tail = " (%s)" % \
            (" | ".join (sorted (c.type_name for c in self.ETW.children)), )
        return "<SAW : %s `%s`%s>" % (self.attr.typ, self.name, tail)
    # end def __repr__

# end class Kind_Wrapper_P

@TFL.Add_To_Class ("_SAW_Wrapper_PQ", MOM.Attr.Query)
class Kind_Wrapper_Q (_Kind_Wrapper_PQ_) :
    """SAW specific information about an Query kind
       descriptor in the context of a specific E_Type_Wrapper
    """

    def __repr__ (self) :
        return "<SAW : %s `%s`>" % (self.attr.typ, self.name)
    # end def __repr__

# end class Kind_Wrapper_Q

@TFL.Add_To_Class ("_SAW_Wrapper_PQ", MOM.Attr._Rev_Query_)
class Kind_Wrapper_R (_Kind_Wrapper_PQ_) :
    """SAW specific information about an _Rev_Query_ kind
       descriptor in the context of a specific E_Type_Wrapper
    """

    def __repr__ (self) :
        return "<SAW : %s `%s`>" % (self.attr.typ, self.name)
    # end def __repr__

# end class Kind_Wrapper_R

class _Kind_Wrapper_Structured_ (_Kind_Wrapper_) :
    """Common base class for attribute kinds with structure."""

    def update_col_map (self, mapper, col_map, prefix = None) :
        self.__super.update_col_map (mapper, col_map)
        self._setup_QC (mapper.__class__ (self, self.ckd_name), col_map)
    # end def update_col_map

    def _setup_QC (self, QC, col_map) :
        self.QC        = QC
        QC.MOM_Wrapper = self
        col_map.update ((qn, QC) for qn in self.q_able_names)
        for k, akw in pyk.iteritems (self.q_able_attrs) :
            if k not in self.db_attrs :
                col_map [akw.name] = akw
    # end def _setup_QC

    def __getattr__ (self, name) :
        if name == "QC" :
            try :
                self.ETW.QC.Map ### trigger setup of `QC`
            except Exception as exc :
                raise AttributeError \
                    ("Access to `QC` of %s triggered %s" % (self, exc))
            else :
                return self.QC
        raise AttributeError (name)
    # end def __getattr__

# end class _Kind_Wrapper_Structured_

class _Kind_Wrapper_C_ (_Kind_Wrapper_Structured_) :
    """Common base class for composite- and structured-attribute kind
       descriptors in the context of a specific E_Type_Wrapper
    """

    is_surrogate   = False
    q_able_attrs_i = {}

    def __init__ (self, ETW, kind, outer = None, parent = None, attr = None) :
        self.__super.__init__ \
            (ETW, kind, outer = outer, parent = parent, attr = attr)
        self.e_type = self.attr.E_Type
        self._setup_attrs (ETW, parent)
    # end def __init__

    @TFL.Meta.Once_Property
    def columns (self) :
        def _gen (self) :
            for an, akw in sorted (pyk.iteritems (self.db_attrs_o)) :
                yield akw.columns
        return tuple (itertools.chain (* _gen (self)))
    # end def columns

    @TFL.Meta.Once_Property
    def type_name (self) :
        return self.attr.E_Type.type_name
    # end def type_name

    @TFL.Meta.Once_Property
    def unique (self) :
        if self.kind.is_primary :
            return tuple \
                (akw.ckd_name for akw in pyk.itervalues (self.db_attrs))
        return ()
    # end def unique

    def alias (self, ETW_alias, ** kw) :
        result = self.__super.alias (ETW_alias, ** kw)
        self._setup_alias_attrs     (ETW_alias, result)
        return result
    # end def alias

    def col_values (self, entity) :
        c_entity = self.kind.get_value (entity)
        for kind_wrapper in pyk.itervalues (self.db_attrs) :
            for k, v in kind_wrapper.col_values (c_entity) :
                yield k, v
    # end def col_values

    def col_values_from_cargo (self, pickle_cargos) :
        pickle_cargo = pickle_cargos [0]
        for name, kind_wrapper in pyk.iteritems (self.db_attrs) :
            attr_pc = pickle_cargo.get (name)
            if attr_pc is not None :
                for k, v in kind_wrapper.col_values_from_cargo (attr_pc) :
                    yield k, v
    # end def col_values

    def _setup_alias_attrs (self, ETW_alias, result) :
        parent = result.eff
        parent_attrs = parent.db_attrs if parent is not result else {}
        result.db_attrs_o = result.db_attrs = dict \
            ( ( k, v.alias
                    (ETW_alias, outer = result, parent = parent_attrs.get (k))
              )
            for k, v in pyk.iteritems (self.db_attrs)
            )
        result.q_able_attrs_o = result.q_able_attrs = dict (result.db_attrs)
        result.q_able_attrs.update \
            ( ( k, v.alias
                    (ETW_alias, outer = result, parent = parent_attrs.get (k))
              )
            for k, v in pyk.iteritems (self.q_able_attrs)
            if  k not in result.db_attrs
            )
    # end def _setup_alias_attrs

    def _setup_alias_columns (self, ETW_alias, result) :
        ### let Once_Property `columns` do its work for `result`
        result.__dict__.pop ("columns", None)
    # end def _setup_alias_columns

    def _setup_attrs (self, ETW, parent) :
        e_type          = self.attr.E_Type
        PTW             = self._attr_e_type_wrapper (ETW, e_type)
        parent_attrs    = parent.db_attrs if parent else {}
        def _gen (self, attrs, e_type, PTW, parent_attrs, kind_wrapper) :
            for a in attrs :
                akw = kind_wrapper \
                    ( a, PTW.DBW, PTW
                    , outer  = self
                    , parent = parent_attrs.get (a.name)
                    )
                yield a.name, akw
        self.db_attrs_o = self.db_attrs = dict \
            ( _gen
                ( self
                , e_type.db_attr
                , e_type, PTW, parent_attrs, TFL.Method._saw_kind_wrapper
                )
            )
        self.q_able_attrs_o = self.q_able_attrs = dict (self.db_attrs)
        self.q_able_attrs.update \
            ( _gen
                ( self
                , (a for a in e_type.q_able if a.name not in self.db_attrs)
                , e_type, PTW, parent_attrs, TFL.Method._saw_kind_wrapper_pq
                )
            )
    # end def _setup_attrs

# end class _Kind_Wrapper_C_

@TFL.Add_To_Class ("_SAW_Wrapper", MOM.Attr._Composite_Mixin_)
class Kind_Wrapper_C (_Kind_Wrapper_C_) :
    """SAW specific information about an composite-attribute kind descriptor in
       the context of a specific E_Type_Wrapper
    """

    def row_as_pickle_cargo (self, row) :
        return (self.ETW.row_as_pickle_cargo (row, self.db_attrs), )
    # end def row_as_pickle_cargo

    def _attr_e_type_wrapper (self, ETW, e_type) :
        return ETW.ATW [e_type]
    # end def _attr_e_type_wrapper

# end class Kind_Wrapper_C

class _Kind_Wrapper_Field_Extractor_ (_Kind_Wrapper_) :
    """Kind wrapper that can extract fields from the column"""
# end class _Kind_Wrapper_Field_Extractor_

class Kind_Wrapper_Structured_Field_Extractor \
          ( _Kind_Wrapper_Field_Extractor_
          , _Kind_Wrapper_Structured_
          , Kind_Wrapper
          ) :
    """Kind wrapper for structured-attribute kind that can extract fields from
       the column
    """

    is_surrogate   = False
    q_able_attrs_i = {}

    def __init__ (self, ETW, kind, outer = None, parent = None, attr = None) :
        self.__super.__init__ \
            (ETW, kind, outer = outer, parent = parent, attr = attr)
        if self.fields :
            self._setup_attrs (ETW, parent)
    # end def __init__

    @property
    def type_name (self) :
        return "%-40.40s" % (self, )
    # end def type_name

    def _attr_e_type_wrapper (self, ETW, e_type) :
        try :
            result = ETW.ATW [e_type]
        except KeyError :
            ETW.DBW.etype_decorator (e_type)
            result = ETW.ATW [e_type]
        return result
    # end def _attr_e_type_wrapper

    def _setup_attrs (self, ETW, parent) :
        e_type          = self.attr.E_Type
        PTW             = self._attr_e_type_wrapper (ETW, e_type)
        self.db_attrs_o = self.db_attrs = {}
        self.q_able_attrs_o = self.q_able_attrs = dict (self.db_attrs)
        def _gen (self, e_type, PTW) :
            for f in self.fields :
                a = e_type.attributes [f]
                f = a._saw_kind_wrapper \
                    if hasattr (a, "_SAW_Wrapper") else a._saw_kind_wrapper_pq
                w = f (PTW.DBW, PTW, outer = self, parent = None)
                yield a.name, w
        self.q_able_attrs.update (_gen (self, e_type, PTW))
    # end def _setup_attrs

# end class Kind_Wrapper_Structured_Field_Extractor

@TFL.Add_To_Class ("_SAW_Wrapper", MOM.Attr.A_Date)
class Kind_Wrapper_Date (Kind_Wrapper_Structured_Field_Extractor) :

    fields = set (("year", "month", "day"))

# end class Kind_Wrapper_Date

@TFL.Add_To_Class ("_SAW_Wrapper", MOM.Attr._A_Time_)
class Kind_Wrapper_Time (Kind_Wrapper_Structured_Field_Extractor) :

    fields = set (("hour", "minute", "second"))

# end class Kind_Wrapper_Time

@TFL.Add_To_Class ("_SAW_Wrapper", MOM.Attr.A_Date_Time)
class Kind_Date_Time_Wrapper (Kind_Wrapper_Structured_Field_Extractor) :

    fields = Kind_Wrapper_Date.fields | Kind_Wrapper_Time.fields

# end class Kind_Date_Time_Wrapper

### Attr-Kind specific functions returning the right Kind_Wrapper ##############
MOM.Attr.A_Attr_Type._SAW_Wrapper      = None
MOM.Attr.A_Attr_Type._saw_kind_wrapper = None

@TFL.Add_To_Class ("_saw_kind_wrapper", MOM.Attr.Kind)
@Single_Dispatch_Method (T = SAW.Manager.__class__)
def _saw_kind_wrapper (self, DBW, ETW, ** kw) :
    attr = self.attr
    skw  = attr._saw_kind_wrapper
    if skw is not None :
        result = skw (DBW, ETW, self, ** kw)
    else :
        SW     = attr._SAW_Wrapper if attr._SAW_Wrapper else self._SAW_Wrapper
        result = SW  (ETW, self, ** kw)
    return result
# end def _saw_kind_wrapper

@TFL.Add_To_Class ("_saw_kind_wrapper_pq", MOM.Attr.Kind)
@Single_Dispatch_Method (T = SAW.Manager.__class__)
def _saw_kind_wrapper_pq (self, DBW, ETW, ** kw) :
    W_PQ = Kind_Wrapper_P if self.is_partial else self._SAW_Wrapper_PQ
    return W_PQ (ETW, self, ** kw)
# end def _saw_kind_wrapper_pq

### Attr-Kind specific functions returning column keyword arguments ############
@TFL.Add_To_Class ("_saw_column_kw", MOM.Attr.Kind)
@Single_Dispatch_Method (T = SAW.Manager.__class__)
def _saw_column_kw (self, DBW, ** kw) :
    default = self.attr.default
    is_None = default is None
    result  = dict (kw, nullable = is_None)
    if not is_None :
        result.update (default = default)
    return result
# end def _saw_column_kw

@TFL.Add_To_Class ("_saw_column_kw", MOM.Attr.Primary)
@Single_Dispatch_Method (T = SAW.Manager.__class__)
def _saw_column_kw_primary (self, DBW, ** kw) :
    result              = super \
        (MOM.Attr.Primary, self)._saw_column_kw (DBW, ** kw)
    result ["nullable"] = False
    return result
# end def _saw_column_kw_primary

### Attr-Kind specific functions returning columns #############################
@TFL.Add_To_Class ("_saw_columns", MOM.Attr.Kind)
@Single_Dispatch_Method (T = SAW.Manager.__class__)
def _saw_columns_kind (self, DBW, wrapper, ** kw) :
    attr = self.attr
    return attr._saw_columns (DBW, wrapper, ** self._saw_column_kw (DBW, ** kw))
# end def _saw_columns_kind

@TFL.Add_To_Class ("_saw_columns", MOM.Attr._Raw_Value_Mixin_)
@Single_Dispatch_Method (T = SAW.Manager.__class__)
def _saw_columns_raw_kind (self, DBW, wrapper, ** kw) :
    attr     = self.attr
    raw_name = wrapper.raw_name
    raw_type = DBW.PNS.Attr._saw_column_type_string \
        (self, DBW, wrapper, attr.Pickled_Type_Raw)
    raw_col  = SA.schema.Column \
        (raw_name, raw_type, default = attr.raw_default or "")
    raw_col.MOM_Is_Raw  = True
    raw_col.MOM_Kind    = wrapper.kind
    raw_col.MOM_Wrapper = wrapper
    return super (MOM.Attr._Raw_Value_Mixin_, self)._saw_columns \
        (DBW, wrapper, ** kw) + (raw_col, )
# end def _saw_columns_raw_kind

### Attr-Type specific functions returning column names ########################
@TFL.Add_To_Class ("_saw_column_name", MOM.Attr.A_Attr_Type)
@property
def _saw_column_name (self) :
    return self.name.lower ()
# end def _saw_column_name

### Attr-Type specific functions returning columns #############################
@TFL.Add_To_Class ("_saw_one_typed_column", MOM.Attr.A_Attr_Type)
@Single_Dispatch_Method (T = SAW.Manager.__class__)
def _saw_one_typed_column (self, DBW, wrapper, col_type, * args, ** kw) :
    attr = wrapper.attr
    if attr.unique_p :
        kw.setdefault ("unique", True)
    if attr.use_index :
        kw.setdefault ("index",  True)
    ckd_name = kw.pop ("ckd_name", wrapper.ckd_name)
    col = self.SAW_Column_Type (ckd_name, col_type, * args, ** kw)
    col.MOM_Is_Raw  = False
    col.MOM_Kind    = wrapper.kind
    col.MOM_Wrapper = wrapper
    return (col, )
# end def _saw_one_typed_column

@TFL.Add_To_Class ("_saw_columns", MOM.Attr.A_Attr_Type)
@Single_Dispatch_Method (T = SAW.Manager.__class__)
def _saw_columns_type (self, DBW, wrapper, ** kw) :
    col_type = self._saw_column_type  (DBW, wrapper, self.Pickled_Type)
    return self._saw_one_typed_column (DBW, wrapper, col_type, ** kw)
# end def _saw_columns_type

@TFL.Add_To_Class ("_saw_columns", MOM.Attr._A_Composite_)
@Single_Dispatch_Method (T = SAW.Manager.__class__)
def _saw_columns_composite (self, DBW, wrapper, ** kw) :
    raise RuntimeError \
        ( "_saw_columns_composite should never be called for %s.%s"
        % (self.det, self.name)
        )
# end def _saw_columns_composite

@TFL.Add_To_Class ("_saw_columns", MOM.Attr._A_Id_Entity_)
@Single_Dispatch_Method (T = SAW.Manager.__class__)
def _saw_columns_id_entity (self, DBW, wrapper, ** kw) :
    col_type = wrapper.ATW.SA_Type.Id_Entity
    result = self._saw_one_typed_column (DBW, wrapper, col_type, ** kw)
    wrapper.ETW.fk_cols.append (result [0])
    return result
# end def _saw_columns_id_entity

@TFL.Add_To_Class ("_saw_columns", MOM.Attr._A_Named_Value_)
@Single_Dispatch_Method (T = SAW.Manager.__class__)
def _saw_columns_named_value (self, DBW, wrapper, ** kw) :
    Type = self.C_Type
    if Type :
        if MOM.Attr.is_attr_type (Type) :
            pts            = self.Pickled_Type
            col_type       = Type._saw_column_type (self, DBW, wrapper, pts)
        else :
            pts            = Type.Pickled_Type
            pts._attr_type = self
            col_type       = self._saw_column_type (DBW, wrapper, pts)
        result = self._saw_one_typed_column (DBW, wrapper, col_type, ** kw)
    else :
        result = super (MOM.Attr._A_Named_Value_, self)._saw_columns \
            (DBW, wrapper, ** kw)
    return result
# end def _saw_columns_named_value

@TFL.Add_To_Class ("_saw_columns", MOM.Attr.A_Surrogate)
@Single_Dispatch_Method (T = SAW.Manager.__class__)
def _saw_columns_surrogate (self, DBW, wrapper, ** kw) :
    seq      = wrapper.ETW.sequence
    col_args = seq.col_args if seq.sa_column is None else ()
    col_type = DBW.PNS.Attr._saw_column_type_int \
        (self, DBW, wrapper, self.Pickled_Type)
    return self._saw_one_typed_column \
        (DBW, wrapper, col_type, * col_args, primary_key = True, ** kw)
# end def _saw_columns_surrogate

### Attr-Type specific functions returning sa-specific types ###################
@TFL.Add_To_Class ("_saw_column_type", MOM.Attr.A_Attr_Type)
@Single_Dispatch_Method (T = SAW.Manager.__class__)
def _saw_column_type (self, DBW, wrapper, pts) :
    p_type = pts.p_type
    if p_type is None :
        raise TypeError \
            ( "Attribute %s.%s needs either a `Pickler` with `Type` or "
              "a `P_Type` definition"
            % (wrapper.kind.e_type.type_name, wrapper.kind, )
            )
    elif p_type is pyk.text_type :
        result = DBW.PNS.Attr._saw_column_type_string (self, DBW, wrapper, pts)
    else :
        if pts._Pickler_Type is not None :
            ### need an instance of `pts._Pickler_Type` to call generic
            ### function `_saw_column_type` on (otherwise, infinite recursion)
            pta     = pts._Pickler_Type    (self.kind, self.e_type)
            result  = pta._saw_column_type (DBW, wrapper, pta.Pickled_Type)
        else :
            p_type_map = wrapper.ATW.SA_Type.P_Type_Map
            try :
                col_type = p_type_map [p_type]
            except KeyError :
                raise TypeError \
                    ( "`P_Type` %s is not supported for `%s`; "
                      "use one of `%s` or extend MOM.DBW.SAW.Attr"
                    % ( p_type, wrapper.kind
                      , sorted (t.__name__ for t in p_type_map)
                      )
                    )
            else :
                result = col_type ()
    return result
# end def _saw_column_type

@TFL.Add_To_Class ("_saw_column_type", MOM.Attr._A_Binary_String_)
@Single_Dispatch_Method (T = SAW.Manager.__class__)
def _saw_column_type_binary_string (self, DBW, wrapper, pts) :
    return wrapper.ATW.SA_Type.LargeBinary (pts.max_length)
# end def _saw_column_type_binary_string

@TFL.Add_To_Class ("_saw_column_type", MOM.Attr.A_Binary_String_P)
@Single_Dispatch_Method (T = SAW.Manager.__class__)
def _saw_column_type_binary_string_pickled (self, DBW, wrapper, pts) :
    return wrapper.ATW.SA_Type.PickleType ()
# end def _saw_column_type_binary_string_pickled

@TFL.Add_To_Class ("_saw_column_type", MOM.Attr._A_Decimal_)
@Single_Dispatch_Method (T = SAW.Manager.__class__)
def _saw_column_type_decimal (self, DBW, wrapper, pts) :
    return wrapper.ATW.SA_Type.Decimal (pts.max_digits, pts.decimal_places)
# end def _saw_column_type_decimal

@TFL.Add_To_Class ("_saw_column_type", MOM.Attr._A_Int_)
@Single_Dispatch_Method (T = SAW.Manager.__class__)
def _saw_column_type_int (self, DBW, wrapper, pts) :
    return wrapper.ATW.SA_Type.sized_int_type (pts)
# end def _saw_column_type_int

@TFL.Add_To_Class ("_saw_column_type", MOM.Attr.A_Time_X)
@Single_Dispatch_Method (T = SAW.Manager.__class__)
def _saw_column_type_time_x (self, DBW, wrapper, pts) :
    return wrapper.ATW.SA_Type._Time_X_ ()
# end def _saw_column_type_time_x

@TFL.Add_To_Class ("_saw_column_type", MOM.Attr._A_String_Base_)
@Single_Dispatch_Method (T = SAW.Manager.__class__)
def _saw_column_type_string (self, DBW, wrapper, pts) :
    kw     = dict (convert_unicode = pts.p_type is pyk.text_type)
    length = pts.length
    if length :
        kw.update (length = length)
        sa_type = wrapper.ATW.SA_Type.String
    else :
        sa_type = wrapper.ATW.SA_Type.Text
    return sa_type (** kw)
# end def _saw_column_type_string

@TFL.Add_To_Class \
    ( "_saw_column_type"
    , MOM.Id_Entity.E_Spec._Attributes.type_name
    , MOM.MD_Change.E_Spec._Attributes.type_name
    )
@Single_Dispatch_Method (T = SAW.Manager.__class__)
def _saw_column_type_type_name (self, DBW, wrapper, pts) :
    return wrapper.ATW.SA_Type.Type_Name
# end def _saw_column_type_type_name

### Functions to cook a value used in a query expression #######################
@TFL.Add_To_Class ("_saw_cooked", MOM.Attr.A_Attr_Type)
@Single_Dispatch_Method (T = SAW.Manager.__class__)
def _saw_cooked (self, DBW, value) :
    return value
# end def _saw_cooked

@TFL.Add_To_Class ("_saw_cooked", MOM.Attr.A_Time_X)
@Single_Dispatch_Method (T = SAW.Manager.__class__)
def _saw_cooked_time_x (self, DBW, value) :
    return SAW.SA_Type._Time_X_.process_bind_param (value, None)
# end def _saw_cooked

### Functions to check column for truth ########################################

@TFL.Add_To_Class ("_saw_bool", MOM.Attr.Kind)
@Single_Dispatch_Method (T = SAW.Manager.__class__)
def _saw_bool_kind (self, DBW, col) :
    not_null = col != None
    result   = self.attr._saw_bool (DBW, col)
    if result is None :
        result = not_null
    elif col.nullable :
        result = not_null & result
    return result
# end def _saw_bool_kind

@TFL.Add_To_Class ("_saw_bool", MOM.Attr._Raw_Value_Mixin_)
@Single_Dispatch_Method (T = SAW.Manager.__class__)
def _saw_bool_raw (self, DBW, col) :
    if col.MOM_Is_Raw :
        result = col != ""
        if col.nullable :
            result = (col != None) & result
    else :
        result = super (MOM.Attr._Raw_Value_Mixin_, self)._saw_bool (DBW, col)
    return result
# end def _saw_bool_raw

@TFL.Add_To_Class ("_saw_bool", MOM.Attr.A_Attr_Type)
@Single_Dispatch_Method (T = SAW.Manager.__class__)
def _saw_bool_type (self, DBW, col) :
    pass
# end def _saw_bool_type

@TFL.Add_To_Class ("_saw_bool", MOM.Attr.A_Boolean)
@Single_Dispatch_Method (T = SAW.Manager.__class__)
def _saw_bool_bool (self, DBW, col) :
    return col == True
# end def _saw_bool_bool

@TFL.Add_To_Class ("_saw_bool", MOM.Attr._A_Number_)
@Single_Dispatch_Method (T = SAW.Manager.__class__)
def _saw_bool_number (self, DBW, col) :
    return col != self.cooked (0)
# end def _saw_bool_number

@TFL.Add_To_Class ("_saw_bool", MOM.Attr._A_String_Base_)
@Single_Dispatch_Method (T = SAW.Manager.__class__)
def _saw_bool_string (self, DBW, col) :
    if self.default == "" :
        return col != ""
# end def _saw_bool_string

### Functions to extract fields from date column ##############################
@TFL.Add_To_Class ("_saw_extract_field", MOM.Attr._A_DT_)
@Single_Dispatch_Method (T = SAW.Manager.__class__)
def _saw_extract_date_field (self, DBW, col, field) :
    return SA.sql.extract (field, col)
# end def _saw_extract_date_field

if __name__ != "__main__" :
    MOM.DBW.SAW._Export_Module ()
### __END__ MOM.DBW.SAW.Attr
