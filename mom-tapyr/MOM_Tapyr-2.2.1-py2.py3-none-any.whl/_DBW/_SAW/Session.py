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
#    MOM.DBW.SAW.Session
#
# Purpose
#    SAW session handling
#
# Revision Dates
#    16-Jul-2013 (CT) Creation
#    18-Jul-2013 (CT) Fix various bugs
#    25-Jul-2013 (CT) Implement `Session_PC`
#    26-Jul-2013 (CT) Change `delete` to not pop from `self._pid_map`
#    28-Jul-2013 (CT) Import `Q`, print exception info in `pid_query`
#    30-Jul-2013 (CT) Add `_Session_.max_cid`, `.needs_commit`
#    31-Jul-2013 (CT) Use `first`, not `fetchone`, to extract row
#    31-Jul-2013 (CT) Factor `Con_Man` to `DBS`; use `engine.con_man`
#     1-Aug-2013 (CT) Wrap `_cid_map` and `_pid_map` in `_spk_maps`
#     1-Aug-2013 (CT) Change `instance_from_row` to use `_spk_maps`
#     1-Aug-2013 (CT) Add `_Session_.max_pid`, `.pid_seq`
#     1-Aug-2013 (CT) Move `con_man` cleanup to `engine.close` and
#                     `.close_connections`
#     1-Aug-2013 (CT) Add `seq_high`
#     1-Aug-2013 (CT) Add `scm_change_from_row`
#     2-Aug-2013 (CT) Change `scm_change_from_row` to call
#                     `parent.add_change` for parents taken from cache, too
#     2-Aug-2013 (CT) Change `Session_PC.produce_changes` to use `ems.changes`
#     2-Aug-2013 (CT) Use `con_man_seq` for `readonly`;
#                     enforce Read/Modify/Update for `readonly` accesses
#     3-Aug-2013 (CT) Fix `insert` of changes in `Session_PC.consume`
#     3-Aug-2013 (CT) Simplify `pid_query` (use `MOM.Id_Entity.query`)
#     5-Aug-2013 (CT) Add and use `Q_Result`, `Id_Entity_Query`,
#                     `Id_Entity_Query_pid`, and `SCM_Change_Query`
#     5-Aug-2013 (CT) Add `rollback_pending_change`, `save_point`
#    25-Aug-2013 (CT) Increase `change_count` for `commit` and `rollback` to
#                     invalidate `q_cache`
#    29-Aug-2013 (CT) Pass `force=True` to `seq.reserve` (`Session_PC.consume`)
#    27-Nov-2013 (MG) `Session_PC.consume` used getattr for `max_surrs` for
#                     scopes which have an old meta data structure
#    11-Dec-2013 (CT) Change `load_info` to preserve `dbid`
#    15-Oct-2014 (CT) Pass `db_meta_data` to `Incompatible_DB_Version`
#    23-Apr-2015 (CT) Change `pid_query` to use optimized `ETW.pid_query`
#                     - remove `Id_Entity_Query_pid`
#    16-Feb-2016 (CT) Use `root_pid`, not `root_epk`, in `load_root`
#    ««revision-date»»···
#--

from   __future__      import division, print_function
from   __future__      import absolute_import, unicode_literals

from   _MOM.import_MOM import MOM, Q
from   _TFL            import TFL
from   _TFL.pyk        import pyk

from   _MOM._DBW._SAW  import SA
import _MOM.DB_Meta_Data

import itertools

class _SAW_DB_Meta_Data_ (MOM.DB_Meta_Data) :
    """Provide meta data for SAW backend."""

    _real_name   = "DB_Meta_Data"
    _max_props   = set (("max_cid", "max_pid", "max_surrs"))
    _properties  = MOM.DB_Meta_Data._properties | set (("scope", "_max_props"))
    scope        = None

    @classmethod
    def NEW (cls, app_type, scope = None, ** _kw) :
        result  = super (DB_Meta_Data, cls).NEW \
            ( app_type, scope
            , ** _kw
            )
        result.scope = scope
        return result
    # end def NEW

    @property
    def max_cid (self) :
        return getattr (self.scope, "max_cid", 0)
    # end def max_cid

    @property
    def max_pid (self) :
        return getattr (self.scope, "max_pid", 0)
    # end def max_pid

    @property
    def max_surrs (self) :
        return TFL.defaultdict (int) ### XXX
    # end def max_surrs

    def __getitem__ (self, name) :
        if name in self._max_props :
            return getattr (self, name)
        else :
            return self.__super.__getitem__ (name)
    # end def __getitem__

    def __iter__ (self) :
        for x in self.__super.__iter__ () :
            yield x
        for x in self._max_props :
            try :
                getattr (self, x)
            except LookupError :
                pass
            else :
                yield x
    # end def __iter__

    def __setitem__ (self, name, value) :
        if name in self._max_props :
            pass
        else :
            return self.__super.__setitem__ (name, value)
    # end def __setitem__

DB_Meta_Data = _SAW_DB_Meta_Data_ # end class

class _Session_ (TFL.Meta.Object) :
    """Session handling for SAW"""

    def __init__ (self, scope, engine) :
        self.scope        = scope
        self.engine       = engine
        self.change_count = 0
        self.con_man      = engine.con_man
        self.con_man_seq  = engine.con_man_seq
        self.in_rollback  = 0
        self.seq_high     = {}
        self._scm_map     = {}
        self._spk_maps    = dict ((k, {}) for k in self.ATW.spk_names)
        self._q_cache     = {}
        self._q_count     = self.change_count
        self._qr_cache    = {}
    # end def __init__

    @TFL.Meta.Once_Property
    def ATW (self) :
        return self.scope.app_type._SAW
    # end def ATW

    @TFL.Meta.Once_Property
    def cid_seq (self) :
        return self.ATW.seq_map ["cid"]
    # end def cid_seq

    @property
    def connection (self) :
        return self.con_man.connection
    # end def connection

    @TFL.Meta.Once_Property
    def Id_Entity_Query (self) :
        ### Use `scope.entity_type` because that works for `MOM.Scope` and
        ### `MOM.DB_Man`
        Id_Entity = self.scope.entity_type ("MOM.Id_Entity")
        return self.Q_Result (Id_Entity).order_by (Q.pid)
    # end def Id_Entity_Query

    @property
    def max_cid (self) :
        seq = self.cid_seq
        return seq.max_value (self)
    # end def max_cid

    @property
    def max_pid (self) :
        seq = self.pid_seq
        return seq.max_value (self)
    # end def max_pid

    @property
    def needs_commit (self) :
        return self.con_man.needs_commit
    # end def needs_commit

    @needs_commit.setter
    def needs_commit (self, value) :
        self.con_man.needs_commit = True
    # end def needs_commit

    @TFL.Meta.Once_Property
    def pid_seq (self) :
        return self.ATW.seq_map ["pid"]
    # end def pid_seq

    @property
    def q_cache (self) :
        result = self._q_cache
        if self._q_count != self.change_count :
            result.clear ()
            self._q_count = self.change_count
        return result
    # end def q_cache

    @property
    def readonly (self) :
        ### re-read the readonly flag from the database to be sure to be
        ### up-to-date
        return self.con_man_seq.connection.execute \
            (self.readonly_select).scalar ()
    # end def readonly

    @TFL.Meta.Once_Property
    def readonly_select (self) :
        ro_col = self.smd_table.c.readonly
        return SA.sql.select ([ro_col]).limit (1)
    # end def readonly_select

    @TFL.Meta.Once_Property
    def SCM_Change_Query (self) :
        ### Use `scope.entity_type` because that works for `MOM.Scope` and
        ### `MOM.DB_Man`
        MD_Change = self.scope.entity_type ("MOM.MD_Change")
        return self.Q_Result (MD_Change).order_by (Q.cid)
    # end def SCM_Change_Query

    @TFL.Meta.Once_Property
    def SCM_Change_Query_cid (self) :
        return self.SCM_Change_Query.filter (Q.cid == Q.BVAR.cid)
    # end def SCM_Change_Query_cid

    @TFL.Meta.Once_Property
    def SCM_Change_Query_parent (self) :
        return self.SCM_Change_Query.filter (Q.parent_cid == Q.BVAR.parent)
    # end def SCM_Change_Query_parent

    @TFL.Meta.Once_Property
    def smd_table (self) :
        """Table holding scope meta data"""
        return self.ATW.scope_metadata
    # end def scope_table

    @property
    def transaction (self) :
        return self.con_man.transaction
    # end def transaction

    @property
    def _cid_map (self) :
        return self._spk_maps ["cid"]
    # end def _cid_map

    @_cid_map.setter
    def _cid_map (self, value) :
        self._spk_maps ["cid"] = value
    # end def _cid_map

    @property
    def _pid_map (self) :
        return self._spk_maps ["pid"]
    # end def _pid_map

    @_pid_map.setter
    def _pid_map (self, value) :
        self._spk_maps ["pid"] = value
    # end def _pid_map

    def change_readonly (self, state) :
        self.db_meta_data.readonly = state
        self._change_readonly (state)
        self.commit ()
    # end def change_readonly

    def close (self) :
        self.close_connections ()
        self.engine.close      ()
        self.engine = self.con_man = self.con_man_seq = None
    # end def close

    def close_connections (self) :
        self.engine.close_connections ()
    # end def close_connections

    def commit (self) :
        if self.needs_commit :
            if self.readonly :
                self.scope.rollback  ()
                raise MOM.Error.Readonly_DB
            ### enforce conflict if other process tries to set readonly
            ### before
            self._change_readonly (False)
        self.con_man.commit ()
    # end def commit

    def compact (self) :
        pass
    # end def compact

    def create (self) :
        self.db_meta_data = self._new_db_meta_data (self.scope)
    # end def create

    def execute (self, * args, ** kw) :
        return self.connection.execute (* args, ** kw)
    # end def execute

    def instance_from_row (self, ETW, row) :
        ### if ETW has children, need to find the right E_Type_Wrapper for
        ### the instance in `row`, using the `type_name` of `row`
        spk     = row [ETW.spk_col]
        tn      = row [ETW.type_name_col]
        ETW_r   = self.ATW [tn]
        spk_map = self._spk_maps [ETW_r.spk_name]
        entity  = spk_map.get (spk, None)
        if entity is None :
            entity = spk_map [spk] = ETW_r.reconstruct (self, row)
        elif isinstance (entity, ETW_r.PNS._Reload_Mixin_) :
            ### cached instance that needs reloading
            entity.__class__._RESTORE_CLASS (entity)
            ETW_r.reload (entity, row)
        return entity
    # end def instance_from_row

    def load_info (self) :
        scope = self.scope
        row   = self.connection.execute \
            (self.smd_table.select ().limit (1)).first ()
        self.db_meta_data = meta_data = row.meta_data
        meta_readonly     = getattr (meta_data, "readonly", False)
        scope.guid        = meta_data.guid
        if meta_data.dbv_hash != scope.app_type.db_version_hash :
            self.close ()
            raise MOM.Error.Incompatible_DB_Version \
                ( meta_data
                , TFL.I18N._T
                   ( "Cannot load database because of a database version hash "
                     "missmatch:\n"
                     "  Tool  database version hash: %s\n"
                     "  Scope database version hash: %s\n"
                   )
                % (scope.app_type.db_version_hash, meta_data.dbv_hash)
                )
        if meta_readonly != row.readonly :
            self.change_readonly (meta_readonly)
        self.db_meta_data = DB_Meta_Data.COPY (meta_data, scope.app_type, scope)
        self.db_meta_data.dbid = meta_data.dbid
    # end def load_info

    def Q_Result (self, Type, strict = False) :
        try :
            result = self._qr_cache [Type, strict]
        except KeyError :
            ETW    = Type._SAW
            QR     = ETW.Q_Result_strict if strict else ETW.Q_Result
            result = QR.bind (_session = self)
            self._qr_cache [Type, strict] = result
        return result
    # end def Q_Result

    def register_scope (self, scope) :
        kw  = dict \
            ( meta_data  = self.db_meta_data
            , readonly   = getattr (self.db_meta_data, "readonly", False)
            )
        self.execute (self.smd_table.insert ().values (** kw))
        self.con_man.commit   ()
    # end def register_scope

    def rollback (self, * args, ** kw) :
        self.con_man.rollback ()
    # end def rollback

    def scm_change_from_row (self, ETW, row) :
        scm_map    = self._scm_map
        cid        = row [ETW.spk_col]
        try :
            result = scm_map [cid]
        except KeyError :
            result = scm_map [cid] = MOM.SCM.Change._Change_.from_pickle \
                (row [ETW.QC.scm_change])
            p_cid  = row [ETW.QC.parent_cid]
            if p_cid :
                try :
                    parent = scm_map [p_cid]
                except KeyError :
                    ### load parent of `result`
                    parent = scm_map [p_cid] = \
                        self.SCM_Change_Query_cid.bind (cid = p_cid).one ()
                parent.add_change (result)
            ### load children or `result`
            ### - the recursive call will link them to `result`
            self.SCM_Change_Query_parent.bind (parent = cid).all ()
        return result
    # end def scm_change_from_row

    def _change_readonly (self, state) :
        meta_data       = self.db_meta_data
        kw              = dict \
            ( meta_data = meta_data
            # pk        = self._scope_pk ### ??? what for ???
            , readonly  = state
            )
        ### read value from database to enforce
        ### Read/Modify/Update cycle
        _   = self.readonly
        cms = self.con_man_seq
        cms.connection.execute (self.smd_table.update ().values (** kw))
        cms.commit ()
    # end def change_readonly

    def _new_db_meta_data (self, scope) :
        return DB_Meta_Data.NEW (scope.app_type, scope)
    # end def _new_db_meta_data

# end class _Session_

class Session_S (_Session_) :
    """Scope-bound session handling for SAW"""

    def __init__ (self, scope, engine) :
        self.__super.__init__ (scope, engine)
        self._save_point = None
    # end def __init__

    def add (self, entity, pid = None) :
        if not self.in_rollback :
            self.change_count += 1
            self.needs_commit  = True
            ETW           = entity.__class__._SAW
            spk           = ETW.insert (self, entity, pid = pid)
            spk_map       = self._spk_maps [ETW.spk_name]
            spk_map [spk] = entity
    # end def add

    def add_change (self, change) :
        if not self.in_rollback :
            self.needs_commit  = True
            entity = self.scope.MOM.MD_Change.E_Type (change)
            ETW    = entity.__class__._SAW
            cid    = ETW.insert (self, entity)
            self._cid_map [cid] = entity
            if change.children :
                table = ETW.sa_table
                wx    = ETW.spk_col.in_ (c.cid for c in change.children)
                self.execute \
                    (table.update ().where (wx).values (parent_cid = cid))
    # end def add_change

    def commit (self) :
        try :
            self.change_count += self.needs_commit
            self.__super.commit             ()
            self._mark_entities_for_reload  ()
        except self.engine.Commit_Conflict_Exception as exc:
            self.scope.rollback             ()
            raise MOM.Error.Commit_Conflict ()
    # end def commit

    def delete (self, entity) :
        ### deleted entities are saved by EMS.Manager (in _removed_entities)
        if not self.in_rollback :
            self.change_count += 1
            self.needs_commit  = True
            def _find_entites (ref_map) :
                for ET, attrs in pyk.iteritems (ref_map) :
                    if not ET.is_partial :
                        QR         = self.Q_Result (ET)
                        query_args = TFL.Filter_Or \
                            (* (getattr (MOM.Q, a) == entity for a in attrs))
                        for e in QR.filter (query_args) :
                            yield e, attrs
            # end def _find_entites
            ET  = entity.__class__
            ETW = ET._SAW
            with self.LET (_pid_map = self._pid_map.copy ()) :
                ref_map  = getattr (ET, "Ref_Req_Map", {})
                for e, _ in _find_entites (ref_map) :
                    e.destroy ()
                ref_map = getattr (ET, "Ref_Opt_Map", {})
                for e, attrs in _find_entites (ref_map) :
                    e.set (** dict ((a, None) for a in attrs))
            ETW.delete (self, entity)
    # end def delete

    def expunge (self, clear_cache = False) :
        self._mark_entities_for_reload ()
        if clear_cache :
            self._spk_maps.update ((k, {}) for k in tuple (self._spk_maps))
    # end def expunge

    def load_root (self, scope) :
        root_pid = self.db_meta_data.root_pid
        if root_pid is not None :
            return self.pid_query (root_pid, scope.Root_Type)
    # end def load_root

    def pid_query (self, pid, Type = None) :
        result  = self._pid_map.get (pid)
        if result is None :
            tn  = "MOM.Id_Entity" if Type is None else Type.type_name
            ETW = self.scope.entity_type (tn)._SAW
            try :
                result = ETW.pid_query (self, pid = pid)
            except IndexError as exc :
                raise LookupError \
                    ("No object with pid `%d` found" % (pid, ))
        if Type is not None and not isinstance (result, Type.Essence) :
            raise LookupError \
                ( "Pid `%r` is instance of type %s, not of type `%s`"
                % (pid, result.type_name, Type.type_name)
                )
        return result
    # end def pid_query

    def rollback (self, keep_zombies = False) :
        if self.con_man.transaction :
            self.in_rollback += 1
            try :
                scope = self.scope
                with scope.ems.pm.dbs.rollback_context (scope, self.__super) :
                    if keep_zombies :
                        ### we need to copy the pid map because rolling back the
                        ### uncommitted changes will remove the created entities
                        ### from this map
                        pid_map = self._pid_map.copy ()
                    with scope.historian.temp_recorder (MOM.SCM.Ignorer) :
                        scope.ems._rollback_uncommitted_changes ()
                    self.change_count += self.needs_commit
                    self.__super.rollback ()
                    if keep_zombies :
                        self._pid_map = pid_map
                    self._mark_entities_for_reload (keep_zombies = keep_zombies)
            finally :
                self.in_rollback -= 1
    # end def rollback

    def rollback_pending_change (self) :
        save_point = self._save_point
        if save_point :
            ### if not true, it already was rolled back by a nested call
            save_point.rollback ()
    # end def rollback_pending_change

    @TFL.Contextmanager
    def save_point (self) :
        save_point = self.con_man.save_point ()
        with self.LET (_save_point = save_point) :
            try :
                yield
            except Exception as exc :
                save_point.rollback ()
                raise
            else :
                save_point.commit ()
    # end def save_point

    def update (self, entity, new_attr) :
        if not self.in_rollback :
            if entity is not None :
                self.needs_commit  = True
                attrs = set (new_attr)
                ET    = entity.__class__
                for an in new_attr :
                    a = ET.attr_prop (an) or getattr (ET, an, None)
                    if a is not None :
                        attrs.update (d.name for d in a.dependent_attrs)
                        if isinstance (a, MOM.Attr._EPK_Mixin_) :
                            self.change_count += 1
                ETW = entity.__class__._SAW
                ETW.update (self, entity, attrs)
    # end def update

    def update_change (self, change) :
        if not self.in_rollback :
            entity = self.scope.MOM.MD_Change.E_Type (change)
            ETW    = entity.__class__._SAW
            ETW.update (self, entity)
    # end def update_change

    def _commit_creation_change (self, change, kw) :
        self.update_change (change)
    # end def _commit_creation_change

    def _mark_entities_for_reload (self, keep_zombies = False) :
        ### dict will be modified
        for pid, e in tuple (pyk.iteritems (self._pid_map)) :
            if isinstance (e, MOM._Id_Entity_Destroyed_Mixin_) :
                if not keep_zombies :
                    del self._pid_map [pid]
            elif not isinstance (e, MOM._Id_Entity_Reload_Mixin_) :
                e.__class__ = e.__class__._RELOAD_E_TYPE
    # end def _mark_entities_for_reload

# end class Session_S

class Session_PC (_Session_) :
    """DB_Man-bound session handling for SAW"""

    def consume (self, e_iter, c_iter, chunk_size, db_meta_data) :
        ATW     = self.ATW
        pm      = self.scope.ems.pm
        self.register_scope (self.scope)
        for (tn, pickle_cargo, pid) in self._chunked_iter (e_iter, chunk_size) :
            ETW = ATW [tn]
            ETW.insert_cargo (self, pid, pickle_cargo)
        for entity in self._chunked_iter \
                (self._change_entity_iter (c_iter), chunk_size) :
            entity._SAW.insert (self, entity)
        for seq in ATW.sequences :
            attr = seq.attr
            ### XXX Once all backends fully support `max_surrs` in
            ###     DB_Meta_Data.COPY,
            ###     --> remove the `else` clause of the following `if`
            if attr.q_name in getattr (db_meta_data, "max_surrs", {}) :
                max_value = db_meta_data.max_surrs [attr.q_name]
            else :
                max_value = getattr (db_meta_data, "max_" + attr.name, None)
            if max_value is not None :
                seq.reserve (self, max_value, commit = False, force = True)
        self.commit ()
    # end def consume

    def produce_changes (self) :
        ### Cannot use `SCM_Change_Query_parent` here because `bind` doesn't
        ### work for value `None`
        for c in self.SCM_Change_Query.filter (Q.parent_cid == None) :
            yield c.as_pickle_cargo (transitive = True)
    # end def produce_changes

    def produce_entities (self) :
        ATW     = self.ATW
        ETW     = ATW ["MOM.Id_Entity"]
        spk_col = ETW.spk_col
        tn_col  = ETW.type_name_col
        qr      = self.Id_Entity_Query
        for row in qr.row_iter (self) :
            pid    = row [spk_col]
            tn     = row [tn_col]
            ETW_r  = ATW [tn]
            yield tn, ETW_r.row_as_pickle_cargo (row), pid
    # end def produce_entities

    def _change_entity_iter (self, c_iter) :
        E_Type = self.scope.app_type ["MOM.MD_Change"]
        for pickle_cargo in c_iter :
            change = MOM.SCM.Change._Change_.from_pickle_cargo (pickle_cargo)
            for c in itertools.chain ([change], change.children) :
                entity = E_Type (c)
                yield entity
    # end def _change_entity_iter

    def _chunked_iter (self, it, chunk_size) :
        """Commit after `chunk_size` iterations"""
        for i, x in enumerate (it) :
            yield x
            if i and not (i % chunk_size) :
                ### don't let transaction grow too big
                self.commit ()
        self.commit ()
    # end def _chunked_iter

    def _new_db_meta_data (self, scope) :
        if scope.src :
            return DB_Meta_Data.COPY \
                (scope.src.db_meta_data, scope.app_type, scope)
        else :
            return self.__super._new_db_meta_data (scope)
    # end def _new_db_meta_data

# end class Session_PC

if __name__ != "__main__" :
    MOM.DBW.SAW._Export ("*")
### __END__ MOM.DBW.SAW.Session
