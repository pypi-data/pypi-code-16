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
#    MOM.DBW.SAW.Manager
#
# Purpose
#    Database wrapper for RDBMS accessed by sqlalchemy wrapped by SAW
#
# Revision Dates
#    19-Jun-2013 (CT) Creation
#    21-Jun-2013 (CT) Add `PNS`, change `Pid_Manager` into property
#     1-Jul-2013 (CT) Redefine `_M_SAW_Manager_.__init__` to set `type_name`
#     1-Jul-2013 (CT) Implement `update_etype`
#     3-Jul-2013 (CT) Change `update_etype` to add `Partial_E_Type_Wrapper`
#     7-Jul-2013 (CT) Set `_SAW` for `Partial_E_Type_Wrapper`, too
#     8-Jul-2013 (CT) Add argument `app_type` to `finalize`
#     8-Jul-2013 (CT) Add `App_Type_Wrapper.finalize` to setup `tn_map`
#     8-Jul-2013 (CT) Use `PNS.SA_Type`, set `ATW.SA_Type`
#    16-Jul-2013 (CT) Fix `_Reload_Mixin_`
#    18-Jul-2013 (CT) Fix various bugs
#    26-Jul-2013 (CT) Put partial E_Types into `tn_map`, too
#    28-Jul-2013 (CT) Change `_saw_table_name` to remove `.`, change to lower
#    30-Jul-2013 (CT) Add `App_Type_Wrapper.seq_map`
#     1-Aug-2013 (CT) Add `App_Type_Wrapper.spk_names`
#     5-Aug-2013 (CT) Set `ems_check` of `P_uniqueness [0]` to `False` if a
#                     `UniqueConstraint` of the database is possible
#     6-Aug-2013 (CT) Don't define `Index` for `UniqueConstraint`
#     7-Aug-2013 (CT) Don't create `Partial_E_Type_Wrapper` unless `parent`
#                     has a `root_table`
#     9-Aug-2013 (CT) Change `update_etype` to fix `children` of partial
#                     descendents of relevant E_Types
#    20-Sep-2013 (CT) Use `QX.Mapper`, not `qs._saw_filter`
#    26-Sep-2013 (CT) Add `reset_cache`
#     4-Jul-2014 (CT) Add table-name to name of `UniqueConstraint`
#     2-Sep-2014 (CT) Add `no_identifier_pat`
#    23-Apr-2015 (CT) Change `_add_user_defined_indices` to support DESC indices
#    22-Jul-2016 (CT) Change `finalize` to filter for `has_identity`;
#                     add `App_Type_Wrapper.db_sig` to signal that change
#    20-Oct-2016 (CT) Add `iea_type_restrictions` to `update_etype`
#    25-Oct-2016 (CT) Increase `db_sig` because `iea_type_restrictions`
#    ««revision-date»»···
#--

from   __future__     import division, print_function
from   __future__     import absolute_import, unicode_literals

from   _MOM           import MOM
from   _TFL           import TFL
from   _TFL.pyk       import pyk

from   _MOM._DBW._SAW import SA

import _MOM._DBW
import _MOM._DBW._Manager_
import _MOM._DBW._SAW
import _MOM._DBW._SAW.DBS
import _MOM._DBW._SAW.Pid_Manager
import _MOM._DBW._SAW.SA_Type
import _MOM._DBW._SAW.Session
import _MOM._SCM.Change

from   _TFL._Meta.Single_Dispatch import Single_Dispatch_Method
from   _TFL.Regexp                import Regexp, re

from   itertools                  import chain as ichain

class _Reload_Mixin_ (object) :
    """Mixin which triggers a reload of an entity from the database on any
       attribute access
    """

    @classmethod
    def _RELOAD_INSTANCE (cls, self, e_type) :
        e_type._SAW.Reloader.reload (self, self.home_scope.ems.session)
    # end def _RELOAD_INSTANCE

# end class _Reload_Mixin_

class App_Type_Wrapper (TFL.Meta.Object) :
    """SAW specific information about a derived App_Type"""

    db_sig              = (2, )
    """Change `db_sig` when a code change in SAW makes db incompatible"""

    no_identifier_pat   = Regexp(r"\W")

    def __init__ (self, app_type) :
        self.app_type   = app_type
        self.DBW        = DBW = app_type.DBW
        self.PNS        = PNS = DBW.PNS
        self.e_types_t  = []
        self.et_map     = {}
        self.tn_map     = {}
        self.metadata   = SA.schema.MetaData ()
        self.SA_Type    = PNS.SA_Type (self)
        self.sequences  = []
        self.seq_map    = {}
        self.spk_names  = set ()
    # end def __init__

    def add (self, etw) :
        tn = etw.type_name
        if etw.sa_table is not None :
            self.e_types_t.append (etw)
            seq = etw.sequence
            if seq :
                self.sequences.append (seq)
                name         = seq.attr.name
                seq_map      = self.seq_map
                seq_map [tn] = seq
                if name in ("cid", "pid") :
                    assert not name in seq_map
                    seq_map [name] = seq
        self.et_map [tn] = etw
        spk_name = etw.spk_name
        if spk_name :
            self.spk_names.add (spk_name)
    # end def add

    def finalize (self) :
        tn_map = self.tn_map
        names  = ichain \
            ( [""]
            , sorted
                ( k for k, etw in pyk.iteritems (self.et_map)
                    if  etw.e_type.has_identity
                )
            )
        for tid, tn in enumerate (names) :
            tn_map.update (((tid, tn), (tn, tid)))
    # end def finalize

    def reset_cache (self) :
        for etw in pyk.itervalues (self.et_map) :
            etw.reset_cache ()
    # end def reset_cache

    def __getitem__ (self, key) :
        key = getattr (key, "type_name", key)
        return self.et_map [key]
    # end def __getitem__

# end class App_Type_Wrapper

class _M_SAW_Manager_ (MOM.DBW._Manager_.__class__) :
    """Meta class of MOM.DBW.SAW.Manager"""

    @TFL.Meta.Once_Property
    def db_sig (cls) :
        return tuple \
            (   ( k
                , tuple
                    (  (c.name, str (c.type), c.nullable, c.primary_key)
                    for c in columns
                    )
                )
            for (k, columns) in sorted (pyk.iteritems (cls.meta_table_columns))
            ) + App_Type_Wrapper.db_sig
    # end def db_sig

    @TFL.Meta.Once_Property
    def meta_table_columns (cls) :
        SA_Type = cls.PNS.SA_Type
        return dict \
            ( scope_metadata     =
                ( SA.schema.Column ("pk", SA_Type.Integer, primary_key = True)
                , SA.schema.Column ("readonly",  SA_Type.Boolean)
                , SA.schema.Column ("meta_data", SA_Type.PickleType)
                ,
                )
            )
    # end def meta_table_columns

    @property
    def Pid_Manager (cls) :
        return cls.PNS.Pid_Manager
    # end def Pid_Manager

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        cls.type_name = cls.PNS.__name__.rsplit (".", 1) [-1]
    # end def __init__

    def connect_database (cls, db_url, scope) :
        dbs     = cls.DBS_map       [db_url.scheme]
        engine  = dbs.create_engine (db_url)
        return cls._create_session  (engine, scope, TFL.Method.load_info)
    # end def connect_database

    def create_database (cls, db_url, scope) :
        ATW    = scope.app_type._SAW
        dbs    = cls.DBS_map        [db_url.scheme]
        dbs.create_database         (db_url, cls)
        engine = dbs.create_engine  (db_url)
        engine.create_tables        (ATW.metadata)
        return cls._create_session  (engine, scope, TFL.Method.create)
    # end def create_database

    def delete_database (cls, db_url) :
        dbs = cls.DBS_map   [db_url.scheme]
        dbs.delete_database (db_url, cls)
    # end def delete_database

    def etype_decorator (cls, e_type) :
        if not hasattr (e_type, "_SAW") :
            e_type._SAW = None
        if (  getattr (e_type, "relevant_root", None)
           or e_type.type_name == "MOM.Id_Entity"
           or not e_type.is_partial ### descendents of An_Entity, ...
           ) :
            etw = e_type._SAW = cls.PNS.E_Type_Wrapper (e_type)
            etw.ATW.add (etw)
        return e_type
    # end def etype_decorator

    def finalize (cls, app_type) :
        app_type._SAW.finalize ()
    # end def finalize

    def prepare (cls, app_type) :
        atw = app_type._SAW = App_Type_Wrapper (app_type)
        cls._create_meta_table (atw, "scope_metadata")
    # end def prepare

    def update_etype (cls, e_type, app_type) :
        ETW = e_type._SAW
        if ETW is not None :
            if ETW.e_type is e_type :
                sa_table = ETW.sa_table
                if sa_table is None :
                    if e_type.is_relevant :
                        needs_table = not \
                            (e_type.is_partial or e_type.iea_type_restrictions)
                        if needs_table :
                            raise TypeError \
                                ( "Non-partial revelant type %s "
                                  "without a table?"
                                % (e_type.type_name, )
                                )
                        ### partial e_type with relevant_root
                        ### fix children (the children's ETW refer to the first
                        ### ancestor with a sa_table)
                        ETW.children = sorted \
                            ( (c._SAW for c in pyk.itervalues (e_type.children))
                            , key = TFL.Getter.type_name
                            )
                else :
                    unique   = ETW.unique
                    unique_o = ETW.unique_o
                    if (   unique
                       and unique == unique_o
                       and not e_type.polymorphic_relevant_epk
                       ) :
                        sa_table.append_constraint \
                            (SA.schema.UniqueConstraint (* unique))
                        e_type.P_uniqueness [0].ems_check = False
                    cls._add_check_constraints    (e_type, ETW, sa_table)
                    cls._add_user_defined_indices (e_type, ETW, sa_table)
                if e_type._Reload_Mixin_ is not None and not e_type.is_partial :
                    e_type._Reload_Mixin_.define_e_type \
                        (e_type, _Reload_Mixin_)
            elif ETW.root_table is not None :
                etw = e_type._SAW = cls.PNS.Partial_E_Type_Wrapper (e_type, ETW)
                ETW.ATW.add (etw)
    # end def update_etype

    def _add_check_constraints (cls, e_type, ETW, sa_table) :
        own_names = e_type._Predicates._own_names
        QR        = ETW.Q_Result
        QX        = QR.QX
        for pk in e_type.P_uniqueness :
            if pk.name in own_names :
                pred    = pk.pred
                columns = []
                tables  = set ((sa_table, ))
                for qs in pred.aqs :
                    qx  = QX.Mapper (QR) (qs)
                    columns.extend (qx.XS_ATTR)
                    for join in qx.JOINS :
                        tables.update (j.table for j in join)
                if len (tables) == 1 :
                    unique = SA.schema.UniqueConstraint \
                        ( * columns
                        , name = "__".join ([sa_table.name, pk.name])
                        )
                    sa_table.append_constraint (unique)
                    pred.ems_check = False
    # end def _add_check_constraints

    def _add_user_defined_indices (cls, e_type, ETW, sa_table) :
        def _gen (sa_table, col_names) :
            for cn in col_names :
                n = cn.lstrip ("-")
                c = getattr (sa_table.c, n)
                if cn != n :
                    c = c.desc ()
                yield c
        for col_names in e_type.use_indices :
            if not isinstance (col_names, (tuple, list)) :
                col_names = (col_names, )
            name = "__".join \
                ( ichain
                    ( [sa_table.name] ### ensure uniqueness of the index' name
                    , (cn.lstrip ("-") for cn in col_names)
                    )
                )
            columns = tuple (_gen (sa_table, col_names))
            SA.schema.Index (name, * columns)
    # end def _add_user_defined_indices

    def _create_meta_table (cls, atw, t_name) :
        columns = tuple (c.copy () for c in cls.meta_table_columns [t_name])
        result  = SA.schema.Table \
            (t_name, atw.metadata, * columns, ** cls.PNS.DBS.table_kw)
        setattr (atw, t_name, result)
        return result
    # end def _create_meta_table

    def _create_session  (cls, engine, scope, method) :
        result = getattr (cls.PNS, "Session_%s" % scope.ilk) (scope, engine)
        method           (result)
        return result
    # end def _create_session

# end class _M_SAW_Manager_

class _SAW_Manager_ \
          (TFL.Meta.BaM (MOM.DBW._Manager_, metaclass = _M_SAW_Manager_)) :
    """Database wrapper for SAW-wrapped sqlalchemy """

    _real_name    = "Manager"

    PNS           = MOM.DBW.SAW

Manager = _SAW_Manager_ # end class

@TFL.Add_To_Class ("_saw_table_name", MOM.Meta.M_E_Type)
@Single_Dispatch_Method (T = Manager.__class__)
def _saw_table_name (cls, DBW) :
    return cls.type_name.replace (".", "_").lower ()
# end def _saw_table_name

if __name__ != "__main__" :
    MOM.DBW.SAW._Export ("*", "_Reload_Mixin_")

    ### The following modules dispatch on `Manager.__class__` and therefore
    ### need to import `Manager`. Due to the cycle we need to import them
    ### after defining and exporting `Manager`
    import _MOM._DBW._SAW.Attr
    import _MOM._DBW._SAW.E_Type_Wrapper
### __END__ MOM.DBW.SAW.Manager
