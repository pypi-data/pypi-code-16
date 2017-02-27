# -*- coding: utf-8 -*-
# Copyright (C) 2009-2016 Mag. Christian Tanzer All rights reserved
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
#    MOM.EMS._Manager_
#
# Purpose
#    Base class for entity manager strategies
#
# Revision Dates
#     2-Dec-2009 (CT) Creation
#     3-Dec-2009 (CT) `count` simplified
#     4-Dec-2009 (MG) `__init__` changed to support database related
#                     parameter and to create the `session`
#    10-Dec-2009 (CT) Class methods `connect` and `new` added,
#                     `__init__` revamped
#    10-Dec-2009 (CT) Empty methods `load_scope` and `register_scope` added
#    14-Dec-2009 (CT) `__iter__` (and relevant_roots) added
#    16-Dec-2009 (MG) Add `scope` parameter to `DWB.create_database` and
#                     `DBW.connect_database`
#    16-Dec-2009 (CT) `pid_query` added
#    16-Dec-2009 (CT) `commit`, `register_change`, and `uncommitted_changes`
#                     added
#    17-Dec-2009 (CT) `async_changes` added
#    17-Dec-2009 (CT) `pid_query` fixed (needs to call `one`)
#    21-Dec-2009 (CT) s/load_scope/load_root/
#    21-Dec-2009 (CT) `relevant_roots` factored to `MOM.Scope`
#    21-Dec-2009 (CT) `commit` changed to update `scope.db_cid`
#    21-Dec-2009 (CT) `close` added
#    19-Jan-2010 (CT) `rollback` added
#    11-May-2010 (CT) `Pid_Manager` added to `__init__`
#    11-May-2010 (MG) Pass `ems` and `db_uri` to `pid_manager`
#    12-May-2010 (CT) `pid_query` rewritten to use `pm.query`
#    12-May-2010 (CT) `pid_query` changed to apply `int` to `pid`
#    17-May-2010 (CT) `register_change` changed to not set `change.user`
#    30-Jun-2010 (CT) `db_meta_data` added
#    30-Jun-2010 (CT) `change_readonly` added
#    30-Jun-2010 (CT) `pcm` added
#     1-Jul-2010 (CT) `compact` added
#    11-Aug-2010 (CT) `register_change` changed to call `change.register`
#    16-Aug-2010 (CT) `commit` changed to check for `uncommitted_changes`
#    14-Sep-2010 (CT) Use `MOM.SCM.Summary` instance instead of `list` to
#                     hold `uncommitted_changes`
#    14-Sep-2010 (CT) Argument `Type` of `pid_query` made optional
#    15-Sep-2010 (CT) `Change_Summary` defined as class variable
#    16-Sep-2010 (CT) Replace `uncommitted_changes` by new object instead of
#                     calling `clear` on the existing one
#    28-Sep-2010 (CT) `rollback` changed to use `temp_change_recorder`,
#                     `_rollback` factored
#    16-Apr-2012 (MG) `add` added
#    19-Apr-2012 (CT) Use translated `.ui_name` instead of `.type_name` for
#                     exceptions
#     2-Jul-2012 (MG) `add` removed again
#     4-Aug-2012 (CT) Add `remove` and `restored`, factor `_reset_transaction`
#     4-Aug-2012 (CT) Add `_rollback_uncommitted_changes`
#    11-Aug-2012 (CT) Allow non-root queries in `instance`
#    12-Aug-2012 (CT) Change `instance` to not use `logging.error`
#    12-Aug-2012 (CT) Add `commit_context`
#     9-Sep-2012 (CT) Add `convert_creation_change`
#    11-Sep-2012 (CT) Add `update` (and a stub for `add`)
#    30-Jan-2013 (CT) Add optional argument `keep_zombies` to `rollback`
#    30-Jan-2013 (CT) Add `add` and `_check_uniqueness`
#    30-Jan-2013 (CT) Fix handling of `Integrity_Error` in `add`
#     6-Jun-2013 (CT) Use `@subclass_responsibility`
#    24-Jun-2013 (CT) Add `close_connections`
#    26-Jun-2013 (CT) Add `lazy_load_p`
#     5-Jul-2013 (CT) Change sig of `_query_single_root`, `_query_multi_root`
#    17-Jul-2013 (CT) Remove `async_changes`, `db_cid`
#    24-Jul-2013 (CT) Use `SCM.Change.Create.update` method, not home-grown code
#     3-Aug-2013 (CT) Re-raise `Integrity_Error` if it wasn't a uniqueness
#                     constraint
#     5-Aug-2013 (CT) Add `rollback_pending_change`
#                     * calls `scope.rollback_pending_change`; can be redefined
#     5-Aug-2013 (CT) Add `save_point`
#    ««revision-date»»···
#--

from   _MOM                  import MOM
from   _TFL                  import TFL

import _MOM._EMS
import _MOM._SCM.Summary

import _TFL._Meta.Object
import _TFL._Meta.Once_Property
import _TFL.Decorator
import _TFL.defaultdict
import _TFL.Q_Result

from   _TFL.Decorator        import subclass_responsibility
from   _TFL.I18N             import _, _T, _Tn

import itertools
import logging

class _Manager_ (TFL.Meta.Object) :
    """Base class for entity managers."""

    type_name           = "XXX"

    Change_Summary      = MOM.SCM.Summary

    Q_Result            = TFL.Q_Result
    Q_Result_Composite  = TFL.Q_Result_Composite

    lazy_load_p         = False
    max_surrs           = TFL.defaultdict (int)

    class Integrity_Error (Exception) :
        """Raised when `DBW` signals an integrity error."""
    # end class Integrity_Error

    @property
    def db_meta_data (self) :
        return self.session.db_meta_data
    # end def db_meta_data

    @property
    def pcm (self) :
        return self.session.pcm
    # end def pcm

    @classmethod
    def connect (cls, scope, db_url) :
        self         = cls (scope, db_url)
        self.session = self.DBW.connect_database (db_url, scope)
        return self
    # end def connect

    @classmethod
    def new (cls, scope, db_url) :
        self         = cls (scope, db_url)
        self.session = self.DBW.create_database (db_url, scope)
        return self
    # end def new

    def __init__ (self, scope, db_url) :
        self.scope        = scope
        self.db_url       = db_url
        self.DBW          = DBW = scope.app_type.DBW
        self.pm           = DBW.Pid_Manager (self, db_url)
        scope.lazy_load_p = self.lazy_load_p
        self._reset_transaction ()
    # end def __init__

    def add (self, entity, pid = None) :
        e_type = entity.E_Type
        self._check_uniqueness (entity, e_type.uniqueness_ems)
        try :
            return self._add (entity, pid)
        except self.Integrity_Error as exc :
            self.rollback_pending_change ()
            self._check_uniqueness (entity, e_type.uniqueness_dbw)
            ### if it wasn't a uniqueness constraint,
            ### re-raise the original exception
            raise
    # end def add

    def change_readonly (self, state) :
        self.session.change_readonly (state)
        self.commit                  ()
    # end def change_readonly

    def close (self) :
        if self.uncommitted_changes :
            self.commit ()
        self.session.close ()
    # end def close

    def close_connections (self) :
        self.session.close_connections ()
    # end def close_connections

    def commit (self) :
        if self.uncommitted_changes :
            self.session.commit     ()
            self._reset_transaction ()
    # end def commit

    @TFL.Contextmanager
    def commit_context (self) :
        ### override as necessary, e.g., to lock tables in a database
        yield
    # end def commit_context

    def compact (self) :
        if self.uncommitted_changes :
            self.commit ()
        self.session.compact ()
    # end def compact

    def convert_creation_change (self, pid, ** kw) :
        """Convert creation-change for `pid` to passed values of `kw`"""
        cc  = self.changes (pid = pid).one ()
        ckw = dict \
            ( (n, v) for n, v in
                ( (n, kw.pop (n, None)) for n in
                    ("c_time", "c_user", "time", "user")
                )
            if v is not None
            )
        if kw :
            raise TypeError \
                ( "Unknown arguments to convert_creation_change: %s"
                % (sorted (kw), )
                )
        cc.update (ckw)
        self.session._commit_creation_change (cc, kw)
    # end def convert_creation_change

    def count (self, Type, strict) :
        return self.query (Type, strict = strict).count ()
    # end def count

    def exists (self, Type, epk) :
        epk_dict = dict (zip (Type.epk_sig, epk))
        entities = self.query (Type).filter (** epk_dict)
        scope    = self.scope
        result   = list (getattr (scope, e.type_name) for e in entities)
        return result
    # end def exists

    def instance (self, Type, epk) :
        result   = None
        epk_dict = dict (zip (Type.epk_sig, epk))
        try :
            qr     = self.query (Type, ** epk_dict)
            result = qr.one ()
        except IndexError :
            pass
        else :
            if not isinstance (result, Type.Essence) :
                result = None
        return result
    # end def instance

    @subclass_responsibility
    def load_root (self) :
        """Redefine to load `root` of scope from database."""
    # end def load_root

    def pid_query (self, pid, Type = None) :
        result = self.pm.query (int (pid))
        if Type is not None and not isinstance (result, Type.Essence) :
            raise LookupError \
                ( _T ("Pid `%r` is instance of type %s, not of type `%s`")
                % (pid, _T (result.ui_name), _T (Type.ui_name))
                )
        return result
    # end def pid_query

    def query (self, Type, * filters, ** kw) :
        root   = Type.relevant_root
        strict = kw.pop ("strict", False)
        _query = self._query_single_root if root else self._query_multi_root
        result = _query (Type, strict)
        if filters or kw :
            result = result.filter (* filters, ** kw)
        if strict :
            result = result.filter (type_name = Type.type_name)
        return result
    # end def query

    def r_query (self, Type, rkw, * filters, ** kw) :
        return self.query (Type, * filters, ** dict (rkw, ** kw))
    # end def r_query

    def register_change (self, change) :
        if change.parent is None :
            self.uncommitted_changes.add (change)
        change.register (self.scope)
    # end def register_change

    def register_scope (self) :
        """Redefine to store `guid` and `root`-info of scope in database."""
        pass
    # end def register_scope

    def remove (self, entity) :
        self._removed_entities [entity.pid] = entity
        self._remove   (entity)
        self.pm.retire (entity)
        entity.__class__ = entity.__class__._DESTROYED_E_TYPE
    # end def remove

    def restored (self, pid) :
        result = self._removed_entities.pop (pid, None)
        if result is not None :
            result.__class__ = result.E_Type
        return result
    # end def restored

    def rollback (self, keep_zombies = False) :
        with self.scope.temp_change_recorder (MOM.SCM.Ignorer) :
            self._rollback (keep_zombies)
        self._reset_transaction ()
    # end def rollback

    def rollback_pending_change (self) :
        self.scope.rollback_pending_change ()
    # end def rollback_pending_change

    def update (self, entity, change) :
        pass ### redefine as necessary in descendents
    # end def update

    @TFL.Contextmanager
    def save_point (self) :
        ### override if the backend supports savepoints
        yield
    # end def save_point

    @subclass_responsibility
    def _add (self, entity, pid = None) :
        pass
    # end def _add

    def _check_uniqueness (self, entity, uniqueness_predicates) :
        def _gen (entity, uniqueness_predicates) :
            for p in uniqueness_predicates :
                result = p.check_predicate (entity)
                if not result :
                    yield result.error
        errors = list (_gen (entity, uniqueness_predicates))
        if errors :
            raise MOM.Error.Invariants (errors)
    # end def _check_uniqueness

    @subclass_responsibility
    def _query_multi_root (self, Type, strict = False) :
        pass
    # end def _query_multi_root

    @subclass_responsibility
    def _query_single_root (self, Type, strict = False) :
        pass
    # end def _query_single_root

    @subclass_responsibility
    def _remove (self, entity) :
        pass
    # end def _remove

    def _reset_transaction (self) :
        self.uncommitted_changes = self.Change_Summary ()
        self._removed_entities   = {}
    # end def _reset_transaction

    def _rollback (self, keep_zombies) :
        self.session.rollback (keep_zombies)
    # end def _rollback

    def _rollback_uncommitted_changes  (self) :
        scope = self.scope
        for c in reversed (self.uncommitted_changes) :
            if c.undoable :
                c.undo (scope)
    # end def _rollback_uncommitted_changes

    def __iter__ (self) :
        sk = TFL.Sorted_By ("pid")
        return itertools.chain \
            (* (   self._query_single_root (r).order_by (sk)
               for r in self.scope.relevant_roots
               )
            )
    # end def __iter__

# end class _Manager_

if __name__ != "__main__" :
    MOM.EMS._Export ("_Manager_")
### __END__ MOM.EMS._Manager_
