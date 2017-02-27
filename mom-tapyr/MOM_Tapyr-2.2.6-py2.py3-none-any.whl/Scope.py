# -*- coding: utf-8 -*-
# Copyright (C) 2009-2016 Mag. Christian Tanzer. All rights reserved
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
#    MOM.Scope
#
# Purpose
#    Provide scopes for objects and links of MOM meta object model
#
# Revision Dates
#    16-Oct-2009 (CT) Creation (factored from `TOM.Scope`)
#    27-Oct-2009 (CT) s/Scope_Proxy/E_Type_Manager/
#    27-Oct-2009 (CT) `_etm` and `_get_etm` added and used in `__getattr__`
#                     and `__getitem__`
#    26-Nov-2009 (CT) Use `except ... as ...` (3-compatibility)
#     4-Dec-2009 (MG) `Scope.new` added, `name` changed to `root_epk`
#     4-Dec-2009 (CT) Handling of `root_epk` corrected (needs to be a tuple)
#    10-Dec-2009 (CT) `as_active` changed to use `Scope.LET` instead of
#                     home-grown code
#    10-Dec-2009 (CT) `compute_defaults_internal` and `check_inv` corrected
#    10-Dec-2009 (CT) Scope initialization revamped
#    10-Dec-2009 (CT) `id` added
#    10-Dec-2009 (CT) Allow instance-specific `init_callbacks`
#    14-Dec-2009 (CT) `copy` added
#    14-Dec-2009 (CT) `unlocked` made method
#    16-Dec-2009 (CT) `commit` added
#    16-Dec-2009 (CT) Calls to `ems.register_change` added to `record_change`
#                     and `nested_change_recorder`
#    17-Dec-2009 (CT) `_init_context` changed to call `start_change_recorder`
#    17-Dec-2009 (CT) Don't record `add` and `remove` of electric objects
#    17-Dec-2009 (CT) Don't `register_change` for empty composite changes
#    17-Dec-2009 (CT) `async_changes` and `query_changes` added
#    17-Dec-2009 (CT) `user_diff` and `user_equal` added
#    21-Dec-2009 (CT) `relevant_roots` added, `_register_root` factored
#    21-Dec-2009 (CT) `destroy` changed to call `ems.close`
#    30-Dec-2009 (MG) `Scope.copy` use `epk_raw` instead of `epk`
#    14-Jan-2010 (CT) `_setup_pkg_ns` changed to handle `_Outer` and
#                     `PNS_Aliases`
#    16-Jan-2010 (CT) `_outer_pgk_ns` factored
#    19-Jan-2010 (CT) `rollback` added
#    27-Jan-2010 (CT) `rollback` changed to call `count_change`
#     8-Feb-2010 (CT) `remove` changed to call `entity._destroy` before
#                     `ems.remove`
#     8-Feb-2010 (CT) `snapshot` removed
#    15-Feb-2010 (CT) `attr_changes` added
#    16-Mar-2010 (CT) `record_change` changed to call `result.callbacks`, if any
#    17-May-2010 (CT) `add_from_pickle_cargo` added and used for `copy`
#    17-May-2010 (CT) `migrate` added
#    17-May-2010 (CT) `nested_change_recorder` and `record_change` changed to
#                     set `result.user`
#    18-May-2010 (CT) `migrate` changed to not filter `query_changes` to
#                     `parent = None`
#    19-May-2010 (MG) `rollback` clear `attr_changes` added
#    26-May-2010 (CT) `self.db_errors = []` added to `_init_context`
#    24-Jun-2010 (CT) Adpated to change of `db_url`
#    29-Jun-2010 (CT) s/from_pickle_cargo/from_attr_pickle_cargo/
#    29-Jun-2010 (CT) Adapted to change of `entity.as_pickle_cargo`
#    30-Jun-2010 (CT) `_locked` and friends removed
#    30-Jun-2010 (CT) `ilk` added
#     1-Jul-2010 (CT) Adapted to `Id_Entity.as_pickle_cargo` change (`pid` last)
#     1-Jul-2010 (CT) `migrate` renamed to `copy`
#    11-Aug-2010 (CT) Optional argument `ignore` added to `user_diff`
#    17-Aug-2010 (CT) Properties `db_meta_data` and `readonly` added
#    14-Sep-2010 (CT) `r_incorrect` added (and optional argument `eiter`
#                     added to `_check_inv`)
#    14-Sep-2010 (CT) Call to `r_incorrect` added to `commit`
#    15-Sep-2010 (CT) `attr_changes` removed
#    28-Sep-2010 (CT) `temp_change_recorder` added
#    30-Nov-2010 (CT) `Fatal_Exceptions` added
#     8-Mar-2011 (CT) `pid_query` added
#    21-Mar-2011 (MG) `copy` assert fixed
#     9-Sep-2011 (CT) Use `.E_Type` instead of `._etype`
#    19-Jan-2012 (CT) Change `add` to consider `entity._home_scope`
#    11-Apr-2012 (CT) Change `add` and `add_from_pickle_cargo` to call
#                     `._finish__init__` after `self.ems.add`
#    15-Apr-2012 (CT) Adapted to changes of `MOM.Error`
#    27-Apr-2012 (CT) Add call to `.rollback` to `commit` in case of errors
#    27-Apr-2012 (CT) Add exception handler around `rollback` to `commit`
#     7-May-2012 (CT) Pass `ucc.entities_transitive` to `r_incorrect` (`commit`)
#    22-Jun-2012 (MG) Add `close_connections`
#    26-Jun-2012 (CT) Add and use `T_Extension`
#    27-Jun-2012 (CT) Rename `_canonical_name` to`canonical_type_name`
#    29-Jun-2012 (CT) Add `max_pid`
#    16-Jul-2012 (CT) Add and register `_atexit`
#     1-Aug-2012 (CT) Change `remove` to set __class__ to `._DESTROYED_E_TYPE`
#     1-Aug-2012 (CT) Remove call to `.ems.rollback` from `commit`
#     4-Aug-2012 (CT) Move `_DESTROYED_E_TYPE` to `.ems.remove`
#    12-Aug-2012 (CT) Use `ems.commit_context`
#    11-Sep-2012 (CT) Add `rollback_pending_change`; factored from `MOM.EMS.SAS`
#    12-Sep-2012 (CT) Call `record_change` and `do_callbacks` unconditionally
#    27-Sep-2012 (CT) Remove references to `Entity.rank`
#     6-Dec-2012 (CT) Don't set `change.user` in `nested_change_recorder`
#    21-Jan-2013 (CT) Add `destroy_all`, populate `Scope.Table`
#    21-Jan-2013 (MG) Call change callbacks for nested change
#    30-Jan-2013 (CT) Add optional argument `keep_zombies` to `rollback`
#    30-Jan-2013 (CT) Add optional argument `allow_zombie` to `pid_query`
#    10-May-2013 (CT) Allow non-string arguments to `__getitem__`
#     3-Jun-2013 (CT) Print exception info to stderr, not stdout
#    13-Jun-2013 (CT) Simplify `_setup_pkg_ns` using new `PNS_Map` semantics
#    17-Jul-2013 (CT) Remove `async_changes`, `db_cid`
#     5-Aug-2013 (CT) Use `with ems.save_point ()` in `add` and `record_change`
#    25-Aug-2013 (CT) Add `reserve_surrogates`
#    12-Jun-2014 (CT) Add `_cleaned_url` and use in `Scope.__str__`
#     5-May-2015 (CT) Remove obsolete class variable `is_universe`
#     5-May-2015 (CT) Add `after_commit_callback`
#     6-Aug-2015 (CT) Improve documentation (access to E_Type_Managers)
#    12-Aug-2015 (CT) Remove obsolete `compute_defaults_internal`
#     8-Oct-2015 (CT) Change `__getattr__` to *not* handle `__XXX__`
#    16-Feb-2016 (CT) Add `Root_Type`
#    16-Feb-2016 (CT) Change `add_from_pickle_cargo` to call `_register_root`
#                     if `pid == self.root_pid`
#    22-Feb-2016 (CT) Change `copy` to set `result.root_pid`
#    22-Feb-2016 (CT) Convert `qname` to property
#    22-Feb-2016 (CT) Change `root_epk` to `root_spec` (callable or epk-tuple)
#     6-May-2016 (CT) Add class attribute `playback_p`
#    17-Oct-2016 (CT) Correct typo in `__doc__`
#    ««revision-date»»···
#--

from   __future__            import print_function

from   _MOM                  import MOM
from   _TFL                  import TFL

import _MOM.Error
import _MOM._Pred.Err_and_Warn_List
import _MOM._SCM.Summary
import _MOM._SCM.Tracker

from   _TFL.Gauge_Logger      import Gauge_Logger
from   _TFL.predicate         import callable, split_hst, rsplit_hst
from   _TFL.pyk               import pyk
from   _TFL.Regexp            import Re_Replacer

import _TFL.Accessor
import _TFL.Context
import _TFL.Decorator
import _TFL.Ordered_Set
import _TFL._Meta.Lazy_Method
import _TFL._Meta.Object
import _TFL._Meta.Once_Property

import atexit
import itertools
import sys
import traceback
import uuid

class _Example_ (TFL.Meta.Object) :
    """Encapsulate example app_type and scope."""

    Table = {}

    def __init__ (self, p_scope, db_url = "sqlite:///:memory:") :
        self.p_scope   = p_scope
        self.db_url    = db_url
    # end def __init__

    @TFL.Meta.Once_Property
    def app_type (self) :
        p_scope = self.p_scope
        p_apt   = p_scope.app_type.parent
        try :
            result = self.Table [p_apt.name]
        except KeyError :
            import _MOM._EMS.Backends
            import _MOM.App_Type
            EMS, DBW, DBS = MOM.EMS.Backends.get (self.db_url)
            result = self.Table [p_apt.name] = p_apt.Derived (EMS, DBW)
        return result
    # end def app_type

    @TFL.Contextmanager
    def context (self, current_scope) :
        if getattr (current_scope, "_is_example_scope", False) :
            yield current_scope
        else :
            scope = self.scope
            try :
                scope.rollback ()
            except Exception :
                logging.exception ("Example scope rollback error")
            with scope.as_active () :
                yield scope
    # end def context

    @TFL.Meta.Once_Property
    def scope (self) :
        result = Scope.new (self.app_type, self.db_url)
        result._is_example_scope = True
        result.stop_change_recorder ()
        return result
    # end def scope

# end class _Example_

@pyk.adapt__str__
class Scope (TFL.Meta.Object) :

    active                 = None
    ilk                    = "S"
    playback_p             = False
    Table                  = {}

    after_commit_callback  = TFL.Ordered_Set ()
    init_callback          = TFL.Ordered_Set ()
    kill_callback          = TFL.Ordered_Set ()

    _cleaned_url           = Re_Replacer (r"(://\w+:)(\w+)@", r"\1<elided>@")
    _deprecated_type_names = {}
    _pkg_ns                = None
    __id                   = 0

    root                   = None
    _roots                 = None

    changes                = property (TFL.Getter.historian.total_changes)
    changes_to_save        = property \
        (lambda s : len (s.ems.uncommitted_changes))
    db_meta_data           = property (TFL.Getter.ems.db_meta_data)
    etypes                 = property (TFL.Getter.app_type.etypes)
    Fatal_Exceptions       = property (TFL.Getter.ems.pm.dbs.Fatal_Exceptions)
    max_cid                = property (TFL.Getter.ems.max_cid)
    max_pid                = property (TFL.Getter.ems.max_pid)
    max_surrs              = property (TFL.Getter.ems.max_surrs)
    name                   = property (lambda s : s.qname)
    readonly               = property (TFL.Getter.ems.db_meta_data.readonly)
    reserve_surrogates     = True
    T_Extension            = property (TFL.Getter.app_type._T_Extension)
    uncommitted_changes    = property (TFL.Getter.ems.uncommitted_changes)

    PNS_Proxy              = None

    @property
    def qname (self) :
        return self.bname or self.app_type.name
    # end def qname

    @TFL.Meta.Once_Property
    def relevant_roots (self) :
        """Return the relevant roots of the application."""
        Top = self.MOM.Id_Entity.E_Type
        return sorted \
            (pyk.itervalues (Top.relevant_roots), key = Top.m_sorted_by)
    # end def relevant_roots

    @property
    def root_pid (self) :
        try :
            return self.db_meta_data.root_pid
        except AttributeError :
            pass
    # end def root_pid

    @root_pid.setter
    def root_pid (self, value) :
        root_pid = self.root_pid
        if not (root_pid is None or root_pid == value) :
            raise TypeError \
                ( "Root pid of scope %s was already set to %r; "
                  "cannot change to %r"
                % (self, root_pid, value)
                )
        try :
            dbmd = self.db_meta_data
        except AttributeError :
            self._root_pid = value
        else :
            dbmd.root_pid = value
    # end def root_pid

    @TFL.Meta.Once_Property
    def Root_Type (self) :
        RTN = self.app_type.Root_Type_Name
        if RTN :
            return self.etypes [RTN]
    # end def Root_Type

    @TFL.Meta.Once_Property
    def _Example (self) :
        return _Example_ (self)
    # end def _Example

    class Pkg_NS :
        """Just a container for the scope-specific etype-proxies for the
           essential classes of a package-namespace (delegates everything
           else to the original package namespace).
        """

        def __init__ (self, scope, pns, qn) :
            self._scope = scope
            self._pns   = pns
            self._qname = qn
        # end def __init__

        def __getattr__ (self, name) :
            if name.startswith ("__") and name.endswith ("__") :
                ### Placate inspect.unwrap of Python 3.5,
                ### which accesses `__wrapped__` and eventually throws
                ### `ValueError`
                return getattr (self.__super, name)
            scope  = self._scope
            etypes = scope.etypes
            pkg_ns = scope._pkg_ns
            qname  = ".".join ((self._qname, name))
            result = None
            if qname in pkg_ns :
                result = pkg_ns [qname]
            elif qname in etypes :
                etype  = etypes [qname]
                result = scope._etm [qname] = etype.Manager (etype, scope)
                setattr (self, name, result)
            else :
                result = getattr (self._pns, name)
            return result
        # end def __getattr__

    # end class Pkg_NS

    ### Scope creation methods

    @classmethod
    def load (cls, app_type, db_url, user = None) :
        """Load a scope for `app_type` from `db_url`.

           Depending on `app_type.EMS`, `load` might load all instances from
           `db_url` into the application or it might just connect to the
           database and load instances on demand in answer to queries.
        """
        db_url = app_type.Url (db_url)
        with cls._init_context (app_type, db_url, user) as self :
            app_type  = self.app_type
            self.ems  = ems = app_type.EMS.connect (self, db_url)
            with self._init_root_context () :
                self._register_root (ems.load_root ())
        return self
    # end def load

    @classmethod
    def new (cls, app_type, db_url, user = None, root_spec = None) :
        """Create a scope for `app_type` for a new database `db_url`.

           If `app_type` has a :attr:`~_MOM.App_Type.App_Type.Root_Type`,
           `new` requires a `root_spec` passed in.

           `root_spec` must be one of:

           * a proper epk-tuple for :attr:`~_MOM.App_Type.App_Type.Root_Type`

           * a callable that takes the scope as its single parameter and
             returns the root object.
        """
        db_url = app_type.Url (db_url)
        with cls._init_context (app_type, db_url, user, root_spec) as self :
            app_type  = self.app_type
            self.guid = self._new_guid ()
            self.ems  = ems = app_type.EMS.new (self, db_url)
            with self._init_root_context (root_spec) :
                self._setup_root   (app_type, root_spec)
                ems.register_scope ()
        return self
    # end def new

    @classmethod
    @TFL.Contextmanager
    def _init_context (cls, app_type, db_url, user, root_spec = None) :
        self                = cls.__new__ (cls)
        self.app_type       = app_type
        self.db_url         = db_url
        self.user           = user
        self.bname          = ""
        self.id             = self._new_id ()
        self.root           = None
        self.historian      = MOM.SCM.Tracker (self)
        self.db_errors      = []
        self._attr_errors   = []
        self._etm           = {}
        self._roots         = {}
        self._setup_pkg_ns  (app_type)
        ### copy `*_callback` from cls to self
        self.after_commit_callback = self.after_commit_callback.copy ()
        self.init_callback         = self.init_callback.copy         ()
        self.kill_callback         = self.kill_callback.copy         ()
        old_active = Scope.active
        try :
            Scope.active = self
            yield self
            self._run_init_callbacks   ()
            self.start_change_recorder ()
            Scope.Table [self.id] = self
        except :
            Scope.active = old_active
            raise
    # end def _init_context

    @TFL.Contextmanager
    def _init_root_context (self, root_spec = None) :
        yield
    # end def _init_root_context

    def __init__ (self) :
        raise TypeError \
            ( "Use {name}.new or {name}.load to create new scopes".format
                (name = self.__class__.__name__)
            )
    # end def __init__

    ### Scope methods

    def add (self, entity, pid = None) :
        """Adds `entity` to scope `self`."""
        if entity._home_scope is None :
            entity.home_scope = self
        with self.ems.save_point () :
            self.ems.add (entity, pid = pid)
            if not entity.init_finished :
                entity._finish__init__ ()
            self.record_change (MOM.SCM.Change.Create, entity)
    # end def add

    def add_from_pickle_cargo (self, type_name, cargo, pid) :
        """Add an entity defined by (`type_name`, `pid`, `cargo`)."""
        Type = self.entity_type (type_name)
        if Type :
            try :
                result = Type.from_attr_pickle_cargo (self, cargo)
            except Exception as exc :
                self.db_errors.append ((type_name, pid, cargo))
                if __debug__ :
                    traceback.print_exc ()
                print (repr (exc), file = sys.stderr)
                print \
                    ( "   add_from_pickle_cargo: couldn't restore"
                      " %s %s %s (app-type %s)"
                    % (type_name, pid, cargo, self.app_type)
                    , file = sys.stderr
                    )
            else :
                self.ems.add (result, pid = pid)
                if pid == self.root_pid :
                    self._register_root (result)
                if not result.init_finished :
                    result._finish__init__ ()
                return result
    # end def add_from_pickle_cargo

    @TFL.Meta.Class_and_Instance_Method
    def add_after_commit_callback (soc, * callbacks) :
        """Add all `callbacks` to `after_commit_callback`. These
           callbacks are executed after each `.commit` of a scope
           (the scope and the MOM.SCM.Summary instance of the just commited
           changes are passed as arguments to each callback).
        """
        soc.after_commit_callback.extend (callbacks)
    # end def add_after_commit_callback

    @TFL.Meta.Class_and_Instance_Method
    def add_init_callback (soc, * callbacks) :
        """Add all `callbacks` to `init_callback`. These
           callbacks are executed whenever a scope is
           created (the new scope is passed as the single argument to each
           callback).
        """
        soc.init_callback.extend (callbacks)
    # end def add_init_callback

    @TFL.Meta.Class_and_Instance_Method
    def add_kill_callback (soc, * callbacks) :
        """Add all `callbacks` to `kill_callback` of the scope class
           or instance. These callbacks` are executed whenever the
           scope is destroyed (the scope to be destroyed is passed as
           the single argument to each callback).
        """
        soc.kill_callback.extend (callbacks)
    # end def add_kill_callback

    @TFL.Contextmanager
    def as_active (self) :
        """Provide context with `self` as active scope."""
        with Scope.LET (active = self) :
            yield
    # end def as_active

    def canonical_type_name (self, type_name) :
        return self._deprecated_type_names.get (type_name, type_name)
    # end def canonical_type_name

    def commit (self) :
        """Commit all outstanding changes to the database."""
        ems = self.ems
        ucc = ems.uncommitted_changes
        with ems.commit_context () :
            if ucc :
                errs = self.r_incorrect (eiter = ucc.entities_transitive (ems))
                if errs :
                    exc = MOM.Error.Invariants (errs.errors)
                    raise exc
            ems.commit ()
            for cb in self.after_commit_callback :
                cb (self, ucc)
    # end def commit

    def copy (self, app_type, db_url) :
        """Copy all entities and change-history  of `self` into a new
           scope for `app_type` and `db_url`.
        """
        assert self.app_type.parent is app_type.parent
        db_url = app_type.Url (db_url)
        assert (      db_url is None
               or not db_url.path
               or self.db_url.path != db_url.path
               )
        with self.as_active () :
            result = self.__class__.new (app_type, db_url, user = self.user)
            result.root_pid = self.root_pid
            for e in sorted (self, key = TFL.Getter.pid) :
                result.add_from_pickle_cargo (* e.as_pickle_cargo ())
            for c in self.query_changes ().order_by (TFL.Sorted_By ("cid")) :
                result.ems.register_change (c)
            result.ems.compact ()
        return result
    # end def copy

    def count_change (self) :
        self.historian.count_change ()
    # end def count_change

    def close_connections (self) :
        self.ems.close_connections ()
    # end def close_connections

    def destroy (self) :
        """Close connection to database and destroy all cached instances."""
        self.ems.close ()
        if self.id in Scope.Table :
            del Scope.Table [self.id]
        self.stop_change_recorder ()
        self.app_type.run_kill_callbacks (self)
        for c in self.kill_callback :
            c (self)
        del self.kill_callback
        self.root = None
        for d in (self._roots, self._pkg_ns) :
            d.clear ()
        ### XXX break circular links (references to this scope from
        ###     importers... )
        if Scope.active == self :
            Scope.active = None
        self.__dict__.clear ()
    # end def destroy

    @classmethod
    def destroy_all (cls) :
        """Destroy all scopes."""
        for i, s in sorted (pyk.iteritems (Scope.Table), reverse = True) :
            try :
                s.destroy ()
            except Exception :
                pass
    # end def destroy_all

    def entity_iter (self) :
        """Yields all objects and links alive in `self` in unspecified
           order.
        """
        return iter (self.ems)
    # end def entity_iter

    def entity_iter_gauge (self, gauge = Gauge_Logger (), sort_key = None, label = None) :
        """Yields all entities alive in `self` in the
           order specified by `sort_key`.
        """
        gauge.reset \
            ( g_delta = 100
            , g_range = self.ems.count (self.MOM.Id_Entity, strict = False)
            , label   = label
            )
        entities = iter (self.ems)
        if sort_key :
            entities = sorted (entities, key = sort_key)
        i = 1
        for e in entities :
            yield e
            if i == 100 :
                gauge.inc (100)
                i = 0
            i += 1
    # end def entity_iter_gauge

    def entity_type (self, entity) :
        """Return scope specific entity type for `entity` (-name)."""
        if isinstance (entity, pyk.string_types) :
            name = entity
        else :
            name = entity.type_name
        return self.app_type.entity_type (self.canonical_type_name (name))
    # end def entity_type

    @TFL.Contextmanager
    def example_etm (self, etm) :
        """Return a E_Type_Manager for the E_Type of `etm` in an example scope."""
        with self._Example.context (self) as x_scope :
            x_etm = x_scope [etm.type_name]
            yield x_etm
    # end def example_etm

    @TFL.Meta.Lazy_Method_RLV
    def g_incorrect (self, gauge = Gauge_Logger ()) :
        """Returns all objects which are globally incorrect (i.e., violating
           the object's `system` predicates).
        """
        with self.as_active () :
            return self._check_inv (gauge, "system")
    # end def g_incorrect

    def has_changed (self) :
        """Indicates whether something saveworthy has changed, i.e., there if
           there are outstanding changes to be commited.
        """
        return bool (self.ems.uncommitted_changes)
    # end def has_changed

    @TFL.Meta.Lazy_Method_RLV
    def i_incorrect (self, gauge = Gauge_Logger ()) :
        """Returns all objects which are object-wise incorrect (i.e., violating
           the object's `object` predicates).
        """
        with self.as_active () :
            return self._check_inv (gauge, "object")
    # end def i_incorrect

    @TFL.Contextmanager
    def nested_change_recorder (self, Change, * args, ** kw) :
        """Return context with `Change (* args, ** kw)` acting as nested
           change recorder.
        """
        with self.historian.nested_recorder (Change, * args, ** kw) as c :
            yield c
            if c :
                c.user = self.user
                self.ems.register_change (c)
                c.do_callbacks           (self)
    # end def nested_change_recorder

    def pid_query (self, pid, allow_zombie = False) :
        """Returns entity with permanent id `pid`, if any."""
        result = self.ems.pid_query (pid)
        if ( not allow_zombie
           and isinstance (result, MOM._Id_Entity_Destroyed_Mixin_)
           ) :
            raise LookupError (pid)
        return result
    # end def pid_query

    def query_changes (self, * filter, ** kw) :
        """Return changes matching `filter` and `kw`"""
        return self.ems.changes (* filter, ** kw)
    # end def query_changes

    @TFL.Meta.Lazy_Method_RLV
    def r_incorrect (self, gauge = Gauge_Logger (), eiter = None) :
        """Returns all objects which are region-wise incorrect (i.e., violating
           the object's `region` predicates).
        """
        with self.as_active () :
            return self._check_inv (gauge, "region", eiter)
    # end def i_incorrect

    def record_change (self, Change, * args, ** kw) :
        """Record the `Change` specified by `args` and `kw`"""
        with self.ems.save_point () :
            result = self.historian.record (Change, * args, ** kw)
            if result is not None :
                result.user = self.user
                self.ems.register_change (result)
                result.do_callbacks      (self)
            return result
    # end def record_change

    def remove (self, entity) :
        """Remove `entity` from scope `self`"""
        assert (entity != self.root)
        Change = MOM.SCM.Change.Destroy
        with self.nested_change_recorder (Change, entity) :
            entity._destroy ()
            self.ems.remove (entity)
    # end def remove

    def rename (self, entity, new_epk, renamer) :
        self.ems.rename (entity, new_epk, renamer)
    # end def rename

    def rollback (self, keep_zombies = False) :
        """Rollback and discard the outstanding changes."""
        self.ems.rollback (keep_zombies)
        self.count_change ()
    # end def rollback

    def rollback_pending_change (self) :
        """Rollback the last, not yet recorded, change but keep all earlier
           outstanding changes.
        """
        changes = tuple (self.uncommitted_changes.changes)
        self.rollback (keep_zombies = True)
        for c in changes :
            c.redo (self)
    # end def rollback_pending_change

    def start_change_recorder (self) :
        if not self.historian._rec_stack :
            self.historian.push_recorder (MOM.SCM.Tracker.Preferred_Recorder)
    # end def start_change_recorder

    def stop_change_recorder (self) :
        if self.historian._rec_stack :
            self.historian.pop_recorder ()
    # end def stop_change_recorder

    @TFL.Contextmanager
    def temp_change_recorder (self, Recorder) :
        with self.historian.temp_recorder (Recorder) :
            yield
    # end def temp_change_recorder

    def user_diff (self, other, ignore = ()) :
        """Return differences of entities `self` and `other` concerning user attributes."""
        result = {}
        seen   = set ()
        def diff (lhs, rhs) :
            for e in lhs :
                k = e.epk_raw
                t = e.type_name
                if k not in seen :
                    seen.add (k)
                    o = rhs [t].instance (* k, raw = True)
                    if o is None :
                        diff = "Present in %s, missing in %s" % (lhs, rhs)
                    else :
                        diff = e.user_diff (o, ignore)
                    if diff :
                        result [(t, k)] = diff
        diff (self,  other)
        diff (other, self)
        return result
    # end def user_diff

    def user_equal (self, other) :
        """Compare entities of `self` and `other` regarding user attributes."""
        s_count = self.ems.count  (self.MOM.Id_Entity.E_Type,  strict = False)
        o_count = other.ems.count (other.MOM.Id_Entity.E_Type, strict = False)
        if s_count == o_count :
            for e in self :
                o = other [e.type_name].instance (* e.epk_raw, raw = True)
                if not (o and e.user_equal (o)) :
                    break
            else :
                return True
        return False
    # end def user_equal

    def _check_inv (self, gauge, kind, eiter = None) :
        err_result = []
        wrn_result = []
        sk         = self.MOM.Id_Entity.sort_key
        if eiter is None :
            eiter  = self.entity_iter_gauge \
                (gauge, label = "Checking %s invariants" % kind)
        for e in eiter :
            try :
                ews = e._pred_man.check_kind (kind, e)
                if ews.errors :
                    err_result.append (e)
                if ews.warnings :
                    wrn_result.append (e)
            except Exception :
                print \
                    ( "Error during evaluation of", kind, "invariant for ", e
                    , file = sys.stderr
                    )
                traceback.print_exc ()
                err_result.append (e)
        return MOM.Pred.Err_and_Warn_List \
            (sorted (err_result, key = sk), sorted (wrn_result, key = sk))
    # end def _check_inv

    def _get_etm (self, name) :
        try :
            result = self._etm [name]
        except KeyError :
            pn, _, rest = split_hst (name, ".")
            try :
                result = self._pkg_ns [pn]
            except KeyError :
                raise AttributeError (name)
            for k in rest.split (".") :
                result = getattr (result, k)
            self._etm [name] = result
        return result
    # end def _get_etm

    def _new_guid (self) :
        return str (uuid.uuid4 ())
    # end def _new_guid

    def _new_id (self) :
        result = Scope.__id
        Scope.__id += 1
        return result
    # end def _new_id

    def _outer_pgk_ns (self, outer, pns, _pkg_ns) :
        while True :
            outer, _, name = rsplit_hst (outer, ".")
            if (not outer) or outer in _pkg_ns :
                break
            pns = pns._Outer
            yield outer, pns
    # end def _outer_pgk_ns

    def _register_root (self, root) :
        if root is not None :
            if self.root is None :
                self.root     = self._roots [root.type_base_name] = root
                self.root_pid = root.pid
                self.bname    = root.ui_display
            else :
                raise TypeError ("Root was already set to %r" % (self.root, ))
    # end def _register_root

    def _run_init_callbacks (self) :
        for c in self.init_callback :
            c (self)
        self.app_type.run_init_callbacks (self)
    # end def _run_init_callbacks

    def _setup_pkg_ns (self, app_type) :
        _pkg_ns = self._pkg_ns = {}
        Pkg_NS  = self.Pkg_NS
        for name, pns in sorted \
                (pyk.iteritems (app_type.PNS_Map), key = TFL.Getter [0]) :
            _pkg_ns [name]  = Pkg_NS (self, pns, name)
            for outer, pns in self._outer_pgk_ns (name, pns, _pkg_ns):
                _pkg_ns [outer] = Pkg_NS (self, pns, outer)
    # end def _setup_pkg_ns

    def _setup_root (self, app_type, root_spec) :
        RT = self.Root_Type
        if root_spec and RT :
            if callable (root_spec) :
                result = root_spec (self)
                if not isinstance (result, RT.Essence) :
                    raise TypeError \
                        ( "%s returned %s %r, expected %s"
                        % (root_spec, result.__class__, result, RT)
                        )
            else :
                result = RT (* root_spec)
            self._register_root (result)
            return result
    # end def _setup_root

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        if "." in name :
            if name in self._etm :
                return self._etm [name]
            else :
                return self._get_etm (name)
        else :
            for dict in self._roots, self._pkg_ns :
                try :
                    result = dict [name]
                except KeyError :
                    pass
                else :
                    setattr (self, name, result)
                    return result
            return getattr (self.app_type, name)
    # end def __getattr__

    def __getitem__ (self, name) :
        if not isinstance (name, pyk.string_types) :
            name = name.type_name
        try :
            return self._get_etm (name)
        except AttributeError :
            raise KeyError (name)
    # end def __getitem__

    def __iter__ (self) :
        """Generate all essential instances stored in database"""
        return iter (self.ems)
    # end def __iter__

    def __str__ (self) :
        url = self._cleaned_url (pyk.text_type (self.db_url))
        return "%s %s<%s>" % (self.__class__.__name__, self.bname, url)
    # end def __str__

# end class Scope

atexit.register (Scope.destroy_all)

### «text» ### start of documentation
__doc__ = """
.. class:: Scope

    `MOM.Scope` maps the object model of a specific derived
    :class:`~_MOM.App_Type.App_Type` to a concrete database storing
    instances of the essential objects and links.

    `Scope` instances cannot be created by just calling the `Scope` class,
    like normal Python types. Instead, :meth:`load` and :meth:`new` create
    scopes connected to existing or newly created databases, respectively.

    For each package namespace defining essential object types, `Scope`
    provides an attribute with the name of the package namespace. That
    attribute lets one access all essential types of the package namespace.

    For instance, if the scope contains a package namespace ``PAP``, one can
    access ``scope.PAP.Person`` or ``scope.PAP.Phone``. Each attribute of
    ``scope.PAP`` refers to the :class:`~_MOM.E_Type_Manager.Object` or
    :class:`~_MOM.E_Type_Manager.Link` instance of the corresponding essential
    type.

    **`Scope` provides the attributes:**

    .. attribute:: app_type

        The derived app_type of the scope.

    .. attribute:: changes

        The number of changes up to now.

    .. attribute:: changes_to_save

        The number of outstanding changes waiting to be commited (or
        rollbacked).

    .. attribute:: db_meta_data

        Meta data about the scope and its database.

    .. attribute:: db_url

        The URL of the database the scope is connected to.

    .. attribute:: max_cid

        The currently maximum change-id.

    .. attribute:: max_pid

        The currently maximum permanent id in use.

    .. attribute:: relevant_roots

        A list of all relevant roots of the application.

            A relevant root is an etype that has its own table in the
            database.

    .. attribute:: uncommitted_changes

       The list of outstanding changes waiting to be commited (or
       rollbacked).

    **`Scope` provides the class methods:**

    .. automethod:: load

    .. automethod:: new

    **`Scope` provides the class and instance methods:**

    .. automethod:: add_after_commit_callback(* callbacks)

    .. automethod:: add_init_callback(* callbacks)

    .. automethod:: add_kill_callback(* callbacks)

    **`Scope` provides the instance methods:**

    .. automethod:: add

    .. automethod:: as_active

    .. automethod:: commit

    .. automethod:: copy

    .. automethod:: destroy

    .. automethod:: entity_iter

    .. automethod:: entity_iter_gauge

    .. automethod:: entity_type

    .. automethod:: g_incorrect()

    .. automethod:: has_changed

    .. automethod:: i_incorrect()

    .. automethod:: nested_change_recorder

    .. automethod:: pid_query

    .. automethod:: query_changes

    .. automethod:: r_incorrect()

    .. automethod:: record_change

    .. automethod:: remove

    .. automethod:: rollback

    .. automethod:: rollback_pending_change

    .. automethod:: __iter__


"""
if __name__ != "__main__" :
    MOM._Export ("*")
### __END__ MOM.Scope
