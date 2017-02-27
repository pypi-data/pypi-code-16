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
#    MOM.DBW.SAW.E_Type_Wrapper
#
# Purpose
#    SAW specific information about a E_Type
#
# Revision Dates
#    24-Jun-2013 (CT) Creation
#     1-Jul-2013 (CT) Add delete/insert/select/update, children/descendents
#     2-Jul-2013 (CT) Add `insert_cargo`, `reconstruct`, `reload`
#     3-Jul-2013 (CT) Add `Partial_E_Type_Wrapper`, factor `_E_Type_Wrapper_`
#     3-Jul-2013 (CT) Change `db_attrs_i` to use `.Derived`
#     3-Jul-2013 (CT) Add `q_able_attrs`
#     5-Jul-2013 (CT) Factor `sa_tables`
#     5-Jul-2013 (CT) Add `_Column_Mapper_`, `E_Type_Wrapper.QC`
#     7-Jul-2013 (CT) Factor `ancestors` to `_E_Type_Wrapper_`
#     7-Jul-2013 (CT) Add guard for `sa_table` to `ancestors`
#     8-Jul-2013 (CT) Use `.ATW.SA_Type`
#     8-Jul-2013 (CT) Add `_Column_Mapper_.__getitem__`
#    11-Jul-2013 (CT) Add all `q_able_names` to `q_able_attrs`
#    16-Jul-2013 (CT) Add properties `Reloader`, `sequences`
#    17-Jul-2013 (CT) Add property `Q_Result`
#    18-Jul-2013 (CT) Fix `delete`, `insert`, `update`
#    18-Jul-2013 (CT) Factor & fix `_exec_insert`, `_insert_kw`, `_insert_iter`
#    20-Jul-2013 (CT) Reverse order of `sa_tables_strict` (--> root first)
#    20-Jul-2013 (CT) Add `joined`, `joined_strict`
#    22-Jul-2013 (CT) Add `E_Type_Wrapper_Alias`, `_Column_Mapper_Alias_`
#    23-Jul-2013 (CT) Add `xtra` to `attr_join_etw_alias`
#    23-Jul-2013 (CT) Factor `spk_name`
#    24-Jul-2013 (CT) Add and use `sa_join_restriction`
#    26-Jul-2013 (CT) Create a table for each non-partial E_Type
#                     (even if it doesn't have db_attrs_o)
#    26-Jul-2013 (CT) Change `where` of `select_strict` to `False`
#    28-Jul-2013 (CT) Use `getattr (entity, self.spk_name)`, not `entity.pid`
#    30-Jul-2013 (CT) Change `sa_tables_descendents` to yield empty tables of
#                     types with descendents; otherwise, JOIN for `select` fails
#     1-Aug-2013 (CT) Use `spk_attr_name` and `spk` of `MOM.Entity`
#     2-Aug-2013 (CT) Enable `sa_join_restriction` even for `len (tables) == 1`
#     4-Aug-2013 (CT) Use `_saw_kind_wrapper`, not `_SAW_Wrapper`
#     5-Aug-2013 (CT) Factor `Q_Result_Type`, add `Q_Result_strict`
#     8-Aug-2013 (CT) Add guard to newly factored `q_able_attrs_i._gen`
#     9-Aug-2013 (CT) Change `Map` to use `q_able_attrs`
#     9-Aug-2013 (CT) Change `parent` to choose a grand-parent if necessary
#     9-Aug-2013 (CT) Add and use `sa_table_x`
#     9-Aug-2013 (CT) Change `sa_tables_descendents` to handle partial
#                     descendents of relevant E_Types
#     9-Aug-2013 (CT) Simplify `joined` and `joined_strict` to `set (tables)`
#    13-Aug-2013 (CT) Change `parent` to filter partial ancestors between a
#                     relevant root and the top-level class defining a sa_table
#    25-Aug-2013 (CT) Change `insert` to guard `seq.reserve` with
#                     `session.scope.reserve_surrogates`
#    26-Aug-2013 (CT) Use `sequence.insert` and `.extract`, not home-grown code
#    26-Aug-2013 (CT) Change `_setup` to include `seq._table_kw`, if any
#    28-Aug-2013 (CT) Factor `del_stmt`, `ins_stmt`, `upd_stmt`, `where_spk`,
#                     `_exec_update`, move MySQL specifics to `SAW.MY`
#    31-Aug-2013 (CT) Add explicit `alias_name` to `E_Type_Wrapper_Alias`
#     5-Sep-2013 (CT) Change `attr_join_etw_alias` to include both table
#                     names into `alias`
#    24-Sep-2013 (CT) Add optional argument `X_ETW` to `attr_join_etw_alias`
#    24-Sep-2013 (CT) Change `E_Type_Wrapper_Alias`:
#                     * change `table_name` to use `.sa_table_x.name`, if any
#                     * use `_mangled_alias` in `_get_sa_table_alias`
#    26-Sep-2013 (CT) Add `reset_cache`
#     2-Sep-2014 (CT) Quote table name if it's not a valid SQL identifier
#    12-Sep-2014 (CT) Factor `etw_alias`
#    23-Apr-2015 (CT) Add `pid_query`, `pid_query_stmt`, `type_name_select_stmt`
#                     + plus `_pid_query_direct`, `_pid_query_indirect`
#     8-Oct-2015 (CT) Change `__getattr__` to *not* handle `__XXX__`
#    20-Oct-2016 (CT) Add `iea_type_restrictions` to `E_Type_Wrapper._setup`
#    20-Oct-2016 (CT) Add `sa_table` guard to `del_stmt`, `ins_stmt`, `upd_stmt`
#                     `sa_tables_descendents`
#                     + Add guards for `stmt` to `_delete`, `_exec_insert`,
#                       `_exec_update`
#    24-Oct-2016 (CT) Add `iea_type_restriction_map` to `sa_joins_strict`
#    ««revision-date»»···
#--

from   __future__                 import division, print_function
from   __future__                 import absolute_import, unicode_literals

from   _TFL                       import TFL
from   _TFL.pyk                   import pyk

from   _MOM.import_MOM            import MOM, Q
from   _MOM._DBW._SAW             import SA

import _MOM._DBW._SAW.Manager
import _MOM._DBW._SAW.Q_Result
import _MOM._DBW._SAW.Sequence
import _MOM.Entity

from   _TFL._Meta.Single_Dispatch import Single_Dispatch_Method
from   _TFL.predicate             import filtered_join, first, uniq

import _TFL._Meta.Object
import _TFL._Meta.Once_Property
import _TFL.Decorator

class _Column_Mapper_Base_ (TFL.Meta.Object) :

    def __init__ (self, ETW, prefix = None) :
        self._ETW    = ETW
        self._prefix = prefix
    # end def __init__

    @TFL.Meta.Once_Property
    @TFL.getattr_safe
    def Map (self) :
        result = {}
        prefix = self._prefix
        for qaw in pyk.itervalues (self._ETW.q_able_attrs) :
            qaw.update_col_map (self, result, prefix)
        return result
    # end def Map

    def __getattr__ (self, name) :
        try :
            return self.Map [name]
        except LookupError :
            raise AttributeError (name)
    # end def __getattr__

    def __getitem__ (self, key) :
        return self.Map [key]
    # end def __getitem__

    def __repr__ (self) :
        ETW = self._ETW
        return "<%s for %s>" % (self._repr_name, ETW.type_name)
    # end def __repr__

# end class _Column_Mapper_Base_

class _Column_Mapper_ (_Column_Mapper_Base_) :
    """Column map for E_Type_Wrapper"""

    _repr_name = "Col-Mapper"

# end class _Column_Mapper_

class _Column_Mapper_Alias_ (_Column_Mapper_Base_) :

    _repr_name = "Col-Mapper-Alias"

# end class _Column_Mapper_Alias_

class _E_Type_Wrapper_Base_ (TFL.Meta.Object) :

    def __init__ (self) :
        self.QC       = self.QC_Type (self)
        self._aja_map = {}
    # end def __init__

    @TFL.Meta.Once_Property
    def db_attrs (self) :
        result = dict (self.db_attrs_i)
        result.update (self.db_attrs_o)
        return result
    # end def db_attrs

    @TFL.Meta.Once_Property
    def has_relevant_tables (self) :
        return \
            (   self.root_table is not None
            and (not self.is_partial or self.children)
            )
    # end def has_relevant_tables

    @TFL.Meta.Once_Property
    def is_partial (self) :
        return self.e_type.is_partial
    # end def is_partial

    @TFL.Meta.Once_Property
    def key_o (self) :
        return self.e_type.own_surrogate
    # end def key_o

    @TFL.Meta.Once_Property
    def last_cid_col (self) :
        sa_table = self.sa_table_x
        if sa_table is not None :
            lcw  = self.db_attrs.get  ("last_cid")
            if lcw is not None :
                return sa_table.c.get (lcw.ckd_name)
    # end def last_cid_col

    @TFL.Meta.Once_Property
    def q_able_attrs (self) :
        result = dict (self.q_able_attrs_i)
        result.update (self.q_able_attrs_o)
        for k, v in tuple (pyk.iteritems (result)) :
            for name in v.q_able_names :
                if name not in result :
                    result [name] = v
        return result
    # end def q_able_attrs

    @TFL.Meta.Once_Property
    def sa_join_restriction (self) :
        """Filter for unrelated MOM.Id_Entity rows.

           This is necessary for partial E_Types because the joins to
           descendents are all `LEFT OUTER` and thus MOM.Id_Entity rows of
           instances of non-descendents are otherwise included.
        """
        tables = self.sa_tables_descendents or ()
        if self.sa_table is None :
            def _gen (spk_name, root, tables) :
                root_spk = root.c [spk_name]
                for t in tables :
                    yield root_spk == t.c [spk_name]
            return SA.expression.or_ \
                (* _gen (self.spk_name, self.sa_tables_strict [0], tables))
    # end def sa_join_restriction

    @TFL.Meta.Once_Property
    def sa_joins (self) :
        """Joins with all ancestor and all descendent tables."""
        if self.has_relevant_tables :
            result = self.sa_joins_strict
            for t in self.sa_tables_descendents :
                result = result.outerjoin (t)
            return result
    # end def sa_joins

    @TFL.Meta.Once_Property
    def sa_joins_strict (self) :
        """Joins of all ancestor tables with `self.sa_table`, if any."""
        if self.has_relevant_tables :
            tables = self.sa_tables_strict
            result = tables [0]
            for t in tables [1:] :
                result = result.join (t)
            iea_tr_map = self.e_type.iea_type_restriction_map
            if iea_tr_map :
                for k, tn in sorted (pyk.iteritems (iea_tr_map)) :
                    if k not in self.db_attrs_o :
                        akw = self.db_attrs.get (k)
                        if akw is not None :
                            etw = self.ATW [tn]
                            if etw.sa_table is not None :
                                ac = akw.columns [0]
                                result = result.join \
                                    (etw.sa_table, ac == etw.spk_col)
            return result
    # end def sa_joins_strict

    @TFL.Meta.Once_Property
    def sa_tables (self) :
        ts = self.sa_tables_strict      or ()
        td = self.sa_tables_descendents or ()
        return ts + td
    # end def sa_tables

    @TFL.Meta.Once_Property
    def select (self) :
        """Select statement including children."""
        if self.has_relevant_tables :
            tables = self.sa_tables
            joins  = self.sa_joins
            result = SA.sql.select \
                (tables, from_obj = (joins, ), use_labels = True)
            jr = self.sa_join_restriction
            if jr is not None :
                result = result.where (jr)
            return result
    # end def select

    @TFL.Meta.Once_Property
    def select_strict (self) :
        """Select statement excluding children."""
        if self.has_relevant_tables :
            if self.e_type.is_partial :
                spk_col = self.spk_col
                if spk_col is not None :
                    return SA.sql.select ([spk_col]).where (False)
            else :
                tn_col = self.type_name_col
                if tn_col is not None :
                    tables = self.sa_tables_strict
                    joins  = self.sa_joins_strict
                    result = SA.sql.select \
                        (tables, from_obj = (joins, ), use_labels = True)
                    if len (tables) > 1 or self.descendents :
                        result = result.where (tn_col == self.e_type.type_name)
                    return result
    # end def select_strict

    @TFL.Meta.Once_Property
    def spk_col (self) :
        sa_table = self.sa_table_x if self.sa_table_x is not None \
            else self.root_table
        if sa_table is not None :
            return sa_table.c [self.spk_name]
    # end def spk_col

    @TFL.Meta.Once_Property
    def spk_name (self) :
        return self.e_type.spk_attr_name
    # end def spk_name

    @TFL.Meta.Once_Property
    def spk_wrapper (self) :
        return self.db_attrs [self.spk_name]
    # end def spk_wrapper

    @TFL.Meta.Once_Property
    def type_name_col (self) :
        tn_wrapper = self.type_name_wrapper
        if tn_wrapper is not None :
            return tn_wrapper.columns [0]
    # end def type_name_col

    @TFL.Meta.Once_Property
    def type_name_wrapper (self) :
        return self.db_attrs.get ("type_name")
    # end def type_name_wrapper

    def attr_join_etw_alias (self, akw, E_Type, X_ETW = None) :
        ETW    = E_Type._SAW
        a_name = akw.ckd_name
        t_name = ETW.table_name
        middle = (self if X_ETW is None else X_ETW).table_name
        key    = (t_name, middle, a_name)
        xtra   = ()
        result = self.etw_alias (ETW, * key)
        if akw.columns and a_name not in self.sa_table_x.c :
            ### need an extra join because `akw`'s column is not in
            ### `self.sa_table_x` but in that of a parent
            ###     --> join the parent's table, too
            akw_col = akw.columns [0]
            xtra    = (getattr (akw_col.table.c, self.spk_name), self.spk_col)
        return result, xtra
    # end def attr_join_etw_alias

    def etw_alias (self, ETW, * key) :
        try :
            result = self._aja_map [key]
        except KeyError :
            alias  = "%s____%s__%s" % key
            result = self._aja_map [key] = E_Type_Wrapper_Alias (ETW, alias)
        return result
    # end def etw_alias

    def reset_cache (self) :
        self._aja_map = {}
    # end def reset_cache

# end class _E_Type_Wrapper_Base_

class _E_Type_Wrapper_ (_E_Type_Wrapper_Base_) :

    QC_Type             = _Column_Mapper_
    sa_table            = None
    sequence            = None

    def __init__ (self, e_type) :
        self.ATW = ATW  = e_type.app_type._SAW
        self.DBW        = ATW.DBW
        self.PNS        = ATW.PNS
        self.e_type     = e_type
        self.type_name  = e_type.type_name
        self.__super.__init__ ()
    # end def __init__

    @TFL.Meta.Once_Property
    def ancestors (self) :
        def _gen (self) :
            p = self.parent
            if p :
                if p.sa_table is not None :
                    yield p
                for a in p.ancestors :
                    yield a
        return tuple (uniq (_gen (self)))
    # end def ancestors

    @TFL.Meta.Once_Property
    def ancestors_r (self) :
        return self.ancestors [::-1]
    # end def ancestors_r

    @TFL.Meta.Once_Property
    def db_attrs_i (self) :
        p = self.parent
        if p :
            et_attrs = self.e_type.attributes
            return dict \
                (  (name, pw.Derived (self, et_attrs [name]))
                for name, pw in pyk.iteritems (p.db_attrs)
                )
        return {}
    # end def db_attrs_i

    @TFL.Meta.Once_Property
    def descendents (self) :
        def _gen (self) :
            for c in self.children :
                yield c
                for d in c.descendents :
                    yield d
        return tuple (uniq (_gen (self)))
    # end def descendents

    @TFL.Meta.Once_Property
    def joined (self) :
        return set (self.sa_tables)
    # end def joined

    @TFL.Meta.Once_Property
    def joined_strict (self) :
        return set (self.sa_tables_strict)
    # end def joined_strict

    @TFL.Meta.Once_Property
    def key_p (self) :
        ancestors = self.ancestors
        if ancestors :
            return ancestors [-1].key_o
    # end def key_p

    @TFL.Meta.Once_Property
    def pid_query (self) :
        if self.e_type.is_partial :
            return self._pid_query_indirect
        else :
            return self._pid_query_direct
    # end def pid_query

    @TFL.Meta.Once_Property
    def pid_query_stmt (self) :
        return self.Q_Result.filter (Q.pid == Q.BVAR.pid).limit (1)
    # end def pid_query_stmt

    @TFL.Meta.Once_Property
    def type_name_select_stmt (self) :
        pid_col = self.root_table.c.pid
        tn_col  = self.type_name_col
        return SA.sql.select \
            ([tn_col]).where (pid_col == SA.sql.bindparam ("pid")).limit (1)
    # end def type_name_select_stmt

    @TFL.Meta.Once_Property
    def q_able_attrs_i (self) :
        p = self.parent
        if p :
            et_attrs = self.e_type.attributes
            def _gen (self, p, et_attrs) :
                for k, pw in pyk.iteritems (p.q_able_attrs) :
                    ak = et_attrs.get (pw.name)
                    if ak is not None :
                        yield k, pw.Derived (self, ak)
            return dict (_gen (self, p, et_attrs))
        return {}
    # end def q_able_attrs_i

    @TFL.Meta.Once_Property
    def q_able_attrs_o (self) :
        DBW    = self.DBW
        e_type = self.e_type
        ignore = set  (self.q_able_attrs_i)
        result = dict (self.db_attrs_o)
        ignore.update (result)
        result.update \
            (  (a.name, a._saw_kind_wrapper_pq (DBW, self))
            for a in e_type.q_able if a.name not in ignore
            )
        return result
    # end def q_able_attrs_o

    @TFL.Meta.Once_Property
    def Q_Result (self) :
        return self.Q_Result_Type (self.e_type, _strict = False)
    # end def Q_Result

    @TFL.Meta.Once_Property
    def Q_Result_strict (self) :
        return self.Q_Result_Type (self.e_type, _strict = True)
    # end def Q_Result_strict

    @TFL.Meta.Once_Property
    def Q_Result_Type (self) :
        return getattr (self.PNS.Q_Result, self.e_type._SAW_Q_Result.__name__)
    # end def Q_Result_Type

    @TFL.Meta.Once_Property
    def Reloader (self) :
        return self.PNS.Q_Result.E_Type_Reload (self.e_type)
    # end def Reloader

    @TFL.Meta.Once_Property
    def root_table (self) :
        ancestors = self.ancestors
        if ancestors :
            return ancestors [-1].sa_table
        return self.sa_table
    # end def root_table

    @TFL.Meta.Once_Property
    def sa_tables_descendents (self) :
        """SA tables of all descendents."""
        if self.root_table is not None :
            def _gen (self) :
                is_pr = self.sa_table is None and self.e_type.is_relevant
                for d in self.descendents :
                    if (is_pr or d.db_attrs_o or d.descendents) \
                           and d.sa_table is not None :
                        ### don't yield empty tables
                        yield d.sa_table
            return tuple (_gen (self))
    # end def sa_tables_descendents

    @TFL.Meta.Once_Property
    def sa_tables_strict (self) :
        """SA Tables excluding children."""
        if self.root_table is not None:
            def _gen (self) :
                for a in self.ancestors_r :
                    yield a.sa_table
                if self.sa_table is not None :
                    yield self.sa_table
            return tuple (_gen (self))
    # end def sa_tables_strict

    @TFL.Meta.Once_Property
    def sequences (self) :
        def _gen (self) :
            for a in self.ancestors_r :
                if a.sequence :
                    yield a.sequence
            if self.sequence :
                yield self.sequence
        return tuple (_gen (self))
    # end def sequences

    @TFL.Meta.Once_Property
    def unique (self) :
        result = set  (self.unique_i)
        result.update (self.unique_o)
        return tuple (sorted (result))
    # end def unique

    @TFL.Meta.Once_Property
    def unique_i (self) :
        p = self.parent
        if p :
            return p.unique
        return ()
    # end def unique

    def _pid_query_direct (self, session, pid) :
        result = first (self.pid_query_stmt.bind (session, pid = pid))
        return result
    # end def _pid_query_direct

    def _pid_query_indirect (self, session, pid) :
        pqs = self.pid_query_stmt
        tnq = session.connection.execute (self.type_name_select_stmt, pid = pid)
        tn  = first (tnq) [0]
        ETW = session.scope.entity_type (tn)._SAW
        return ETW._pid_query_direct (session, pid)
    # end def _pid_query_indirect

    def __repr__ (self) :
        tns = list (str (t) for t in reversed (self.sa_tables_strict or ()))
        return "<SAW : %s [%s]>" % (self.type_name, " : ".join (tns))
    # end def __repr__

# end class _E_Type_Wrapper_

class E_Type_Wrapper (_E_Type_Wrapper_) :
    """SAW specific information about a E_Type"""

    def __init__ (self, e_type) :
        self.__super.__init__ (e_type)
        self.table_name         = e_type._saw_table_name (self.ATW.DBW)
        self.children           = []
        self.fk_cols            = []
        self._sa_alias_name_map = {}
        self._setup (e_type)
    # end def __init__

    @TFL.Meta.Once_Property
    def db_attrs_o (self) :
        inherited = self.db_attrs_i
        result    = dict \
            (  (a.name, a._saw_kind_wrapper (self.DBW, self))
            for a in self.e_type.db_attr
            if  a.name not in inherited
            )
        return result
    # end def db_attrs_o

    @TFL.Meta.Once_Property
    def del_stmt (self) :
        if self.sa_table is not None :
            return self.sa_table.delete ().where (self.where_spk)
    # end def del_stmt

    @TFL.Meta.Once_Property
    def ins_stmt (self) :
        if self.sa_table is not None :
            return self.sa_table.insert ()
    # end def ins_stmt

    @TFL.Meta.Once_Property
    def parent (self) :
        e_type  = self.e_type
        sk      = lambda x : bool (getattr (x, "relevant_root", None))
        parents = list \
            ( p for p in sorted (e_type.parents, key = sk, reverse = True)
              if getattr (p, "_SAW", None) and p._SAW.sa_table is not None
            )
        if not parents :
            rr = e_type.relevant_root
            if rr :
                if rr is e_type :
                    ### there might be partial classes between `e_type` and
                    ### a top-level class with a table
                    ### --> look for that one in all ancestors
                    ancestors = list \
                        ( p for p in sorted
                            (e_type.ancestors, key = sk, reverse = True)
                          if  getattr (p, "_SAW", None)
                          and p._SAW.sa_table is not None
                        )
                    parents = list \
                        (a for a in ancestors if a._SAW.e_type is a) [:1]
                else :
                    ### there are partial classes between `e_type` and
                    ### `e_type.relevant_root` that don't have `_SAW`
                    ### --> select `e_type.relevant_root` as `parent` even
                    ###     though it's a grand-parent or greater-grand-parent
                    parents = [e_type.relevant_root]
        if len (parents) > 1 :
            np_parents = list (p for p in parents if p.is_relevant)
            if len (np_parents) > 1 :
                raise NotImplementedError \
                    ( "Multiple inheritance currently not supported\n"
                      "%s, %s"
                    % (e_type.type_name, parents)
                    )
        if parents and parents [0] :
            return  parents [0]._SAW
    # end def parents

    @TFL.Meta.Once_Property
    def sa_table_x (self) :
        result = self.sa_table
        if result is None and self.e_type.is_relevant :
            result = self.parent.sa_table
        return result
    # end def sa_table_x

    @TFL.Meta.Once_Property
    def upd_stmt (self) :
        if self.sa_table is not None :
            return self.sa_table.update ().where (self.where_spk)
    # end def upd_stmt

    @TFL.Meta.Once_Property
    def where_spk (self) :
        return self.spk_col == SA.sql.bindparam ("spk")
    # end def where_spk

    def delete (self, session, entity) :
        self._delete (session, entity)
        for a in self.ancestors :
            a._delete (session, entity)
    # end def delete

    def insert (self, session, entity, ** spks) :
        kw = {}
        for a in self.ancestors_r :
            a._insert (session, entity, spks, kw)
        self._insert  (session, entity, spks, kw)
        result = kw [self.spk_name]
        return result
    # end def insert

    def insert_cargo (self, session, pid, pickle_cargo) :
        kw  = { self.spk_name : pid }
        for a in self.ancestors_r :
            a._insert_cargo (session, pickle_cargo, kw)
        self._insert_cargo (session, pickle_cargo, kw)
    # end def insert_cargo

    def reconstruct (self, session, row) :
        scope        = session.scope
        pickle_cargo = self.row_as_pickle_cargo (row)
        entity       = self.e_type.from_attr_pickle_cargo (scope, pickle_cargo)
        if self.last_cid_col is not None :
            entity._reloaded_last_cid = entity.last_cid
        entity._finish__init__ ()
        return entity
    # end def reconstruct

    def reload (self, entity, row) :
        pickle_cargo = self.row_as_pickle_cargo (row)
        entity.reload_from_pickle_cargo (pickle_cargo)
        if self.last_cid_col is not None :
            entity._reloaded_last_cid = entity.last_cid
        return entity
    # end def reload

    def reset_cache (self) :
        self._sa_alias_name_map = {}
        self.__super.reset_cache ()
    # end def reset_cache

    def row_as_pickle_cargo (self, row, db_attrs = None) :
        result = TFL.defaultdict (tuple)
        if db_attrs is None :
            db_attrs = self.db_attrs
        for name, kind_wrapper in pyk.iteritems (db_attrs) :
            result [name] = kind_wrapper.row_as_pickle_cargo (row)
        return result
    # end def row_as_pickle_cargo

    def update (self, session, entity, attrs = ()) :
        if not attrs :
            attrs = self.db_attrs
        for a in self.ancestors_r :
            a._update (session, entity, attrs)
        self._update (session, entity, attrs)
    # end def update

    def _delete (self, session, entity) :
        stmt = self.del_stmt
        if stmt is not None :
            session.connection.execute (stmt, spk = entity.spk)
    # end def _delete

    def _exec_insert (self, session, values) :
        stmt = self.ins_stmt
        if stmt is not None :
            return session.connection.execute (stmt.values (values))
    # end def _exec_insert

    def _exec_update (self, session, entity, values, ** xkw) :
        stmt = self.upd_stmt
        if stmt is not None :
            return session.connection.execute (stmt.values (values), ** xkw)
    # end def _exec_update

    def _insert (self, session, entity, spks, kw) :
        seq = self.sequence
        if seq :
            seq.insert (session, entity, spks, kw)
        ikw = self._insert_kw (session, kw)
        for name, kind_wrapper in self._insert_iter (self.db_attrs_o, ikw) :
            ikw.update (kind_wrapper.col_values (entity))
        result = self._exec_insert (session, ikw)
        if seq :
            seq.extract (session, entity, kw, result)
        return result
    # end def _insert

    def _insert_cargo (self, session, pickle_cargo, kw) :
        ikw = self._insert_kw (session, kw)
        for name, kind_wrapper in self._insert_iter (self.db_attrs_o, ikw) :
            attr_pc = pickle_cargo.get (name)
            if attr_pc is not None :
                ikw.update (kind_wrapper.col_values_from_cargo (attr_pc))
        return self._exec_insert (session, ikw)
    # end def _insert_cargo

    def _insert_kw (self, session, kw) :
        db_attrs_o = self.db_attrs_o
        spk_name   = self.spk_name
        ikw        = dict \
             ( (k, v) for k, v in pyk.iteritems (kw)
             if k == spk_name or k in db_attrs_o
             )
        return ikw
    # end def _insert_kw

    def _insert_iter (self, db_attrs_o, ikw) :
        for name, kind_wrapper in pyk.iteritems (db_attrs_o) :
            if name not in ikw :
                yield name, kind_wrapper
    # end def _insert_iter

    def _mangled_alias (self, alias) :
        map = self._sa_alias_name_map
        try :
            result = map [alias]
        except KeyError :
            result = map [alias] = "%s__%d" % (self.table_name, len (map) + 1)
        return result
    # end def _mangled_alias

    def _setup (self, e_type) :
        db_attrs_o = self.db_attrs_o
        if db_attrs_o or \
               not (e_type.is_partial or e_type.iea_type_restrictions) :
            ATW           = self.ATW
            PNS           = self.PNS
            cols, unique  = self._setup_columns (e_type, db_attrs_o, PNS)
            t_name        = self.table_name
            if self.key_o or self.key_p :
                kw  = dict (PNS.DBS.table_kw)
                if ATW.no_identifier_pat.search (t_name) :
                    kw ["quote"] = True
                seq = self.sequence
                if seq and seq.sa_column is None :
                    kw.update (seq._table_kw)
                self.sa_table = sa_table = SA.schema.Table \
                    (t_name, ATW.metadata,  * cols, ** kw)
                sa_table.MOM_Wrapper = self
            self.unique_o = tuple (sorted (unique))
        parent = self.parent
        if parent :
            parent.children.append (self)
    # end def _setup

    def _setup_columns (self, e_type, db_attrs_o, PNS) :
        result  = []
        unique  = []
        key_o   = self.key_o
        key_p   = self.key_p
        if key_o :
            seq = self.sequence = key_o.attr._saw_sequence (self)
        if key_p :
            spk_name  = self.spk_name
            key_p_col = SA.schema.Column \
                ( spk_name
                , self.ATW.SA_Type.sized_int_type (key_p.Pickled_Type)
                , SA.schema.ForeignKey (self.parent.sa_table.c [spk_name])
                , primary_key = not key_o
                , unique      = True
                )
            key_p_col.MOM_Kind    = key_p
            key_p_col.MOM_Wrapper = None
            result.append (key_p_col)
        for name, kind_wrapper in pyk.iteritems (db_attrs_o) :
            result.extend (kind_wrapper.columns)
            unique.extend (kind_wrapper.unique)
        return result, unique
    # end def _setup_columns

    def _update (self, session, entity, attrs) :
        values = {}
        for name, kind_wrapper in pyk.iteritems (self.db_attrs_o) :
            if name in attrs and not kind_wrapper.is_surrogate :
                ### surrogate attributes can't be updated
                ### even if the surrogate value is the same, `update` raises
                ### SA.Exception.IntegrityError
                values.update (kind_wrapper.col_values (entity))
        if values :
            result = self._exec_update \
                (session, entity, values, spk = entity.spk)
            if not result.rowcount :
                session.scope.rollback          ()
                raise MOM.Error.Commit_Conflict ()
    # end def _update

# end class E_Type_Wrapper

class E_Type_Wrapper_Alias (_E_Type_Wrapper_Base_) :
    """Alias for tables of an E_Type_Wrapper"""

    QC_Type                 = _Column_Mapper_Alias_

    def __init__ (self, ETW, alias_name) :
        self._ETW           = ETW
        self._alias_name    = alias_name
        self._sa_table_map  = {}
        self.__super.__init__ ()
    # end def __init__

    @TFL.Meta.Once_Property
    def db_attrs_i (self) :
        return dict \
            (  (k, v.alias (self))
            for k, v in pyk.iteritems (self._ETW.db_attrs_i)
            )
    # end def db_attrs_i

    @TFL.Meta.Once_Property
    def db_attrs_o (self) :
        return dict \
            (  (k, v.alias (self))
            for k, v in pyk.iteritems (self._ETW.db_attrs_o)
            )
    # end def db_attrs_o

    @TFL.Meta.Once_Property
    def e_type (self) :
        return self._ETW.e_type
    # end def e_type

    @TFL.Meta.Once_Property
    def q_able_attrs_i (self) :
        return dict \
            (  (k, v.alias (self))
            for k, v in pyk.iteritems (self._ETW.q_able_attrs_i)
            )
    # end def q_able_attrs_i

    @TFL.Meta.Once_Property
    def q_able_attrs_o (self) :
        return dict \
            (  (k, v.alias (self))
            for k, v in pyk.iteritems (self._ETW.q_able_attrs_o)
            )
    # end def q_able_attrs_o

    @TFL.Meta.Once_Property
    def root_table (self) :
        table = self._ETW.root_table
        if table is not None :
            return self._get_sa_table_alias (table)
    # end def root_table

    @TFL.Meta.Once_Property
    def sa_table (self) :
        table = self._ETW.sa_table
        if table is not None :
            return self._get_sa_table_alias (table)
    # end def sa_table

    @TFL.Meta.Once_Property
    def sa_table_x (self) :
        table = self._ETW.sa_table_x
        if table is not None :
            return self._get_sa_table_alias (table)
    # end def sa_table_x

    @TFL.Meta.Once_Property
    def sa_tables_descendents (self) :
        tables = self._ETW.sa_tables_descendents
        if tables is not None :
            return tuple (self._get_sa_table_alias (t) for t in tables)
    # end def sa_tables_descendents

    @TFL.Meta.Once_Property
    def sa_tables_strict (self) :
        tables = self._ETW.sa_tables_strict
        if tables is not None :
            return tuple (self._get_sa_table_alias (t) for t in tables)
    # end def sa_tables_strict

    @TFL.Meta.Once_Property
    def table_name (self) :
        table = self.sa_table_x
        if table is not None :
            result = table.name
        else :
            table  = self._ETW.sa_table_x
            result = table.name if table is not None else \
                self.e_type._saw_table_name (self.ATW.DBW)
        return result
    # end def table_name

    def _get_sa_col_alias (self, col) :
        table  = self._get_sa_table_alias (col.table)
        result = table.c [col.name]
        return result
    # end def _get_sa_col_alias

    def _get_sa_table_alias (self, table) :
        ETW   = table.MOM_Wrapper
        name  = table.name
        alias = self._alias_name
        if self._ETW.e_type != table.MOM_Wrapper.e_type :
            alias = "%s____%s" % (name, self._alias_name)
        alias  = ETW._mangled_alias (alias)
        map    = self._sa_table_map
        result = map.get (alias)
        if result is None :
            result = map [alias] = table.alias (alias)
            result.MOM_Wrapper   = self
        return result
    # end def _get_sa_table

    def _mangled_alias (self, alias) :
        ### `self.e_type._SAW` is the outermost, i.e., un-aliased, ETW
        return self.e_type._SAW._mangled_alias (alias)
    # end def _mangled_alias

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        return getattr (self._ETW, name)
    # end def __getattr__

    def __repr__ (self) :
        tns = list \
            (str (t.element) for t in reversed (self.sa_tables_strict or ()))
        return "<SAW Alias : %s [%s]>" % (self.type_name, " : ".join (tns))
    # end def __repr__

# end class E_Type_Wrapper_Alias

class Partial_E_Type_Wrapper (_E_Type_Wrapper_) :
    """SAW specific information about a partial E_Type without its own table"""

    def __init__ (self, e_type, parent) :
        self.__super.__init__ (e_type)
        self.p_parent = parent
        self.parent   = \
            (    parent
            if   parent.sa_table is not None
            else first (p for p in parent.ancestors if p.sa_table is not None)
            )
    # end def __init__

    @TFL.Meta.Once_Property
    def children (self) :
        e_type = self.e_type
        return tuple \
            (c for c in self.p_parent.children if issubclass (c.e_type, e_type))
    # end def children

    @TFL.Meta.Once_Property
    def db_attrs_o (self) :
        return {}
    # end def db_attrs_o

    @TFL.Meta.Once_Property
    def sa_table_x (self) :
        return self.parent.sa_table
    # end def sa_table_x

    @TFL.Meta.Once_Property
    def table_name (self) :
        return self.e_type._saw_table_name (self.ATW.DBW)
    # end def table_name

    @TFL.Meta.Once_Property
    def unique_o (self) :
        return ()
    # end def unique_o

# end class Partial_E_Type_Wrapper

if __name__ != "__main__" :
    MOM.DBW.SAW._Export ("*")
### __END__ MOM.DBW.SAW.E_Type_Wrapper
