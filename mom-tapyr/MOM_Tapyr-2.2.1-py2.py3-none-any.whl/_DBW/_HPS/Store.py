# -*- coding: utf-8 -*-
# Copyright (C) 2009-2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package _MOM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    MOM.DBW.HPS.Store
#
# Purpose
#    Implement on-disk store for Hash-Pickle-Store
#
# Revision Dates
#    18-Dec-2009 (CT) Creation
#    21-Dec-2009 (CT) Creation continued
#    19-Jan-2010 (CT) `_save_context` changed to save `max_pid`, too
#    20-Jan-2010 (CT) `Info.NEW` factored from `Store._create_info`
#     4-Mar-2010 (CT) `load_info` changed to allow existence of uncompressed
#                     database
#     4-Mar-2010 (CT) Classmethod `X_Uri` factored
#    19-Mar-2010 (CT) `save_objects` and `_load_store` changed to
#                     save/restore `pid`
#    30-Apr-2010 (CT) `_load_store` corrected
#    30-Apr-2010 (CT) `save_objects` changed to store all entities into a
#                     single store `by_pid` sorted by `pid`
#    12-May-2010 (CT) s/ems._pid_map/ems.pm.table/
#    17-May-2010 (CT) `scope.add_from_pickle_cargo` factored from `_load_store`
#    18-May-2010 (CT) `Change_Manager` and `load_changes` added
#    18-May-2010 (CT) `_load_pending` changed to use `.restore` instead of
#                     `.redo`
#    18-May-2010 (CT) `save_treshold` added
#    25-Jun-2010 (CT) Use `scope.db_version_hash` instead of
#                     `Version.db_version`
#    29-Jun-2010 (CT) Adapted to change of `entity.as_pickle_cargo`
#    29-Jun-2010 (CT) `Store_S` factored from `Store`
#    30-Jun-2010 (CT) `last_changer` removed
#    30-Jun-2010 (CT) s/Info/DB_Meta_Data/; `MOM.DB_Meta_Data` factored
#    30-Jun-2010 (CT) `_save_info` factored,
#                     `_save_context` changed to yield `info`
#    30-Jun-2010 (CT) `readonly` and `change_readonly` added
#     1-Jul-2010 (CT) Adapted to `Id_Entity.as_pickle_cargo` change (`pid` last)
#     1-Jul-2010 (CT) `compact` added
#    12-Jul-2010 (CT) `consume` corrected
#    13-Jul-2010 (CT) `Store_PC.produce_entities` changed to apply `x_uri` to
#                     name of store
#    12-Aug-2010 (MG) `Store_S._save_context` fixed in regards to `readonly`
#                     handling
#    13-Aug-2010 (CT) `_check_sync_ro` factored
#    13-Aug-2010 (CT) `_rollback` factored
#    16-Aug-2010 (CT) `_check_sync_ro` changed to call `scope.rollback`
#                     insteaf of `_rollback`
#    16-Aug-2010 (CT) Adapted to change of signature of `DB_Meta_Data.COPY`
#    16-Aug-2010 (CT) `_copy_ignore` added and redefinition of `COPY` removed
#    16-Aug-2010 (CT) `close` change to use `_check_sync`, not `_check_sync_ro`
#    26-May-2013 (CT) Use `chmod` to limit readability of files
#     6-Jun-2013 (CT) Simplify signature of `_save_context`; add `max_surrs`
#     7-Jun-2013 (CT) Add/use argument `db_meta_data` to/in `consume`
#    12-Oct-2015 (CT) Add Python-3 future imports
#    25-Oct-2015 (CT) Use `pyk.pickle_protocol`
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

from   _MOM                  import MOM
from   _TFL                  import TFL

from   _TFL                  import sos
from   _TFL.predicate        import sliced
from   _TFL.pyk              import pyk

import _MOM.DB_Meta_Data
import _MOM.Error
import _MOM._DBW._HPS.Change_Manager

import _TFL._Meta.Object
import _TFL._Meta.Property
import _TFL.defaultdict
import _TFL.Error
import _TFL.FCM
import _TFL.Filename
import _TFL.module_copy
import _TFL.open_w_lock
import _TFL.Record

import contextlib
import stat
import zipfile               as     ZF

pickle = pyk.pickle

TZF = TFL.module_copy \
    ( "zipfile"
    , stringFileHeader = b"MM\004\003"
    , stringCentralDir = b"MM\002\001"
    , stringEndArchive = b"MM\006\005"
    )

class _HPS_DB_Meta_Data_ (MOM.DB_Meta_Data) :
    """Provide meta data for Hash-Pickle-Store."""

    _real_name   = "DB_Meta_Data"
    _copy_ignore = MOM.DB_Meta_Data._copy_ignore | set \
        (("commits", "pending", "stores"))

    def __init__ (self, commits = None, pending = None, stores = None, ** kw) :
        return self.__super.__init__ \
            ( commits = commits if commits is not None else []
            , pending = pending if pending is not None else []
            , stores  = stores  if stores  is not None else []
            , ** kw
            )
    # end def __init__

    def FILES (self, x_uri, head = None) :
        def _ (x) :
            fn = TFL.Filename (x, x_uri)
            return fn.name, fn.base_ext
        if head is not None :
            yield _ (head)
        for s in self.stores :
            yield _ (s)
        for cid, p in self.pending :
            yield _ (p)
        for cid, c in self.commits :
            yield _ (c)
    # end def FILES

    @classmethod
    def NEW (cls, app_type, scope = None, ** _kw) :
        ems     = TFL.Record\
            ( max_cid   = getattr (scope, "max_cid",   0)
            , max_pid   = getattr (scope, "max_pid",   0)
            , max_surrs = getattr (scope, "max_surrs", TFL.defaultdict (int))
            )
        kw      = dict (_kw)
        result  = super (DB_Meta_Data, cls).NEW \
            ( app_type, scope
            , max_cid   = kw.pop ("max_cid",   ems.max_cid)
            , max_pid   = kw.pop ("max_pid",   ems.max_pid)
            , max_surrs = kw.pop ("max_surrs", ems.max_surrs)
            , ** kw
            )
        return result
    # end def NEW

DB_Meta_Data = _HPS_DB_Meta_Data_ # end class

class _TZF_ (TFL.Meta.Object) :

    ZF = TZF

# end class _TZF_

class Store (TFL.Meta.Object) :
    """Implement on-disk store for Hash-Pickle-Store."""

    ZF = ZF

    db_meta_data  = TFL.Meta.Alias_Property ("info")
    save_treshold = 3

    try :
        import zlib
    except ImportError :
        zip_compression = ZF.ZIP_STORED
    else :
        zip_compression = ZF.ZIP_DEFLATED
        del zlib

    def __init__ (self, db_uri, app_type) :
        self.app_type = app_type
        self.Version  = app_type.ANS.Version
        self.db_uri   = db_uri
        self.x_uri    = self.X_Uri (db_uri.name)
        self.info_uri = TFL.Filename ("info", self.x_uri)
        self.cm       = MOM.DBW.HPS.Change_Manager ()
    # end def __init__

    def change_readonly (self, state) :
        with TFL.lock_file (self.x_uri.name) :
            info = self.info
            self._check_sync     (info)
            info.readonly = bool (state)
            self._save_info      (info)
    # end def change_readonly

    def close (self) :
        assert sos.path.exists (self.x_uri.name), self.x_uri.name
        db_uri = self.db_uri
        x_name = self.x_uri.name
        bak    = TFL.Filename (".bak", db_uri).name
        with TFL.lock_file (x_name) :
            info = self.info
            self._check_sync (info)
            with TFL.open_to_replace \
                     (db_uri.name, mode = "wb", backup_name = bak) as file:
                sos.fchmod (file.fileno (), stat.S_IRUSR | stat.S_IWUSR)
                with contextlib.closing (self.ZF.ZipFile (file, "w")) as zf :
                    for abs, rel in info.FILES (self.x_uri, self.info_uri) :
                        zf.write (abs, rel)
        sos.rmdir (x_name, deletefiles = True)
    # end def close

    def compact (self) :
        pass
    # end def compact

    def create (self) :
        assert not sos.path.exists (self.db_uri.name), self.db_uri.name
        assert not sos.path.exists (self.x_uri.name), self.x_uri.name
        x_name = self.x_uri.name
        with TFL.lock_file (x_name) :
            sos.mkdir  (x_name)
            sos.system ("chmod go= %s" % x_name)
            self._create_info ()
    # end def create

    def load_changes (self) :
        assert sos.path.exists (self.x_uri.name), self.x_uri.name
        info  = self.info
        x_uri = self.x_uri
        with TFL.lock_file (x_uri.name) :
            for (cid, name) in info.commits :
                file_name = TFL.Filename (name, x_uri).name
                for c in self._loaded_changes (file_name) :
                    pass ### `_loaded_changes` adds the changes to `self.cm`
        self.cm.to_load = []
    # end def load_changes

    def load_info (self) :
        assert sos.path.exists (self.db_uri.name), self.db_uri.name
        x_name = self.x_uri.name
        with TFL.lock_file (x_name) :
            if not sos.path.exists (x_name) :
                sos.mkdir (x_name)
                sos.system ("chmod go= %s" % x_name)
                with contextlib.closing \
                         (self.ZF.ZipFile (self.db_uri.name, "r")) as zf :
                    zf.extractall (x_name)
            self.info = self._load_info ()
    # end def load_info

    @classmethod
    def X_Uri (cls, name) :
        return TFL.Dirname (name + ".X")
    # end def X_Uri

    def _check_sync (self, info) :
        db_info = self._load_info ()
        if info.max_cid != db_info.max_cid :
            self.db_info = db_info
            raise TFL.Sync_Conflict (self)
        return db_info
    # end def _check_sync

    def _check_sync_ro (self, info) :
        result = self._check_sync (info)
        if info.readonly or result.readonly :
            self.scope.rollback ()
            raise MOM.Error.Readonly_DB
        return result
    # end def _check_sync_ro

    def _create_info (self) :
        assert not sos.path.exists (self.info_uri.name)
        info = self.info = self._new_info ()
        self._save_info (info)
    # end def _create_info

    def _loaded_changes (self, name) :
        with open (name, "rb") as file :
            add     = self.cm.add
            changes = pickle.load (file)
            for cargo in changes :
                c = MOM.SCM.Change._Change_.from_pickle_cargo (cargo)
                yield c
                add (c)
                for cc in c.children :
                    add (cc)
    # end def _loaded_changes

    def _load_info (self) :
        with open (self.info_uri.name, "rb") as file :
            result = pickle.load (file)
        ### XXX Check result.dbv_hash vs. self.app_type.db_version_hash
        return result
    # end def _load_info

    def _save_info (self, info) :
        with open (self.info_uri.name, "wb") as file :
            pickle.dump (info, file, pyk.pickle_protocol)
        self.info = info
    # end def _save_info

# end class Store

class Store_PC (Store) :
    """Scopeless store dealing with pickle-cargos only."""

    scope = TFL.Meta.Alias_Property ("db_man")

    def __init__ (self, db_uri, db_man) :
        self.__super.__init__ (db_uri, db_man.app_type)
        self.db_man = db_man
    # end def __init__

    def commit (self) :
        pass
    # end def commit

    def consume (self, e_iter, c_iter, chunk_size, db_meta_data) :
        assert sos.path.exists (self.x_uri.name), self.x_uri.name
        assert not self.info.commits
        assert not self.info.pending
        assert not self.info.stores
        db_uri  = self.db_uri
        x_name  = self.x_uri.name
        with TFL.lock_file (x_name) :
            info    = self.info
            stores  = info.stores  = []
            commits = info.commits = []
            for i, cargo in enumerate (sliced (e_iter, chunk_size)) :
                s_name  = TFL.Filename ("by_pid_%d" % i, self.x_uri)
                with open (s_name.name, "wb") as file :
                    pickle.dump (cargo, file, pyk.pickle_protocol)
                stores.append   (s_name.base_ext)
            for cargo in sliced (c_iter, chunk_size) :
                max_cid = cargo [-1] [1] ["cid"]
                c_name  = TFL.Filename ("%d.commit" % max_cid, self.x_uri)
                with open (c_name.name, "wb") as file :
                    pickle.dump (cargo, file, pyk.pickle_protocol)
                commits.append ((max_cid, c_name.base_ext))
            info.max_cid = db_meta_data.max_cid
            info.max_pid = db_meta_data.max_pid
            self._save_info (info)
    # end def consume

    def produce_changes (self) :
        assert sos.path.exists (self.x_uri.name), self.x_uri.name
        assert not self.info.pending
        info  = self.info
        x_uri = self.x_uri
        with TFL.lock_file (x_uri.name) :
            for (cid, name) in info.commits + info.pending :
                file_name = TFL.Filename (name, x_uri).name
                with open (file_name, "rb") as file :
                    changes = pickle.load (file)
                    for cargo in changes :
                        yield cargo
    # end def produce_changes

    def produce_entities (self) :
        assert sos.path.exists (self.x_uri.name), self.x_uri.name
        assert not self.info.pending
        info  = self.info
        x_uri = self.x_uri
        with TFL.lock_file (x_uri.name) :
            for s in info.stores :
                with open (TFL.Filename (s, x_uri).name, "rb") as file :
                    for epc in pickle.load (file) :
                        yield epc
    # end def produce_entities

    def _new_info (self) :
        return DB_Meta_Data.COPY \
            (self.db_man.src.db_meta_data, self.db_man.app_type, self.db_man)
    # end def _new_info

    def _rollback (self) :
        pass
    # end def _rollback

# end class Store_PC

class Store_S (Store) :
    """Store connected to a scope."""

    def __init__ (self, db_uri, scope) :
        self.__super.__init__ (db_uri, scope.app_type)
        self.scope = scope
    # end def __init__

    def close (self) :
        if len (self.info.pending) > self.save_treshold :
            self._save_objects ()
        self.__super.close ()
    # end def close

    def commit (self) :
        assert sos.path.exists (self.x_uri.name), self.x_uri.name
        info  = self.info
        scope = self.scope
        ucc   = scope.ems.uncommitted_changes
        if ucc :
            cargo   = [c.as_pickle_cargo (transitive = True) for c in ucc]
            max_cid = scope.ems.max_cid
            x_name  = self.x_uri.name
            with self._save_context (x_name, scope, info) :
                c_name = TFL.Filename ("%d.commit" % max_cid, self.x_uri)
                with open (c_name.name, "wb") as file :
                    pickle.dump (cargo, file, pyk.pickle_protocol)
                info.pending.append ((max_cid, c_name.base_ext))
    # end def commit

    def compact (self) :
        if self.info.pending :
            self._save_objects ()
    # end def compact

    def load_objects (self) :
        assert sos.path.exists (self.x_uri.name), self.x_uri.name
        info  = self.info
        x_uri = self.x_uri
        with TFL.lock_file (x_uri.name) :
            self.scope.db_errors = []
            for s in info.stores :
                self._load_store   (TFL.Filename (s, x_uri).name)
            for (cid, name) in info.pending :
                self._load_pending (TFL.Filename (name, x_uri).name)
        self.cm.to_load  = [name for (cid, name) in info.commits]
    # end def load_objects

    def _load_pending (self, name) :
        scope = self.scope
        for c in self._loaded_changes (name) :
            c.restore (scope)
    # end def _load_pending

    def _load_store (self, s) :
        with open (s, "rb") as file :
            cargo   = pickle.load (file)
            scope   = self.scope
            for ec in cargo :
                ### XXX Add legacy lifting
                scope.add_from_pickle_cargo (* ec)
    # end def _load_store

    def _new_info (self) :
        return DB_Meta_Data.NEW (self.app_type, self.scope)
    # end def _new_info

    def _rollback (self) :
        self.scope.rollback ()
    # end def _rollback

    @TFL.Contextmanager
    def _save_context (self, x_name, scope, info) :
        Version = self.Version
        with TFL.lock_file (x_name) :
            self._check_sync_ro (info)
            yield info
            ems            = scope.ems
            info.max_cid   = ems.max_cid
            info.max_pid   = ems.max_pid
            info.max_surrs = ems.max_surrs
            self._save_info (info)
    # end def _save_context

    def _save_objects (self) :
        info    = self.info
        scope   = self.scope
        stores  = info.stores = []
        x_name  = self.x_uri.name
        with self._save_context (x_name, scope, info) :
            s_name = TFL.Filename ("by_pid", self.x_uri)
            cargo  = \
                [   e.as_pickle_cargo ()
                for pid, e in sorted (pyk.iteritems (scope.ems.pm.table))
                ]
            with open (s_name.name, "wb") as file :
                pickle.dump (cargo, file, pyk.pickle_protocol)
            stores.append   (s_name.base_ext)
            info.commits.extend (info.pending)
            info.pending = []
    # end def _save_objects

# end class Store_S

if __name__ != '__main__':
    MOM.DBW.HPS._Export ("*")
### __END__ MOM.DBW.HPS.Store
