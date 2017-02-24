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
#    MOM.EMS.Hash
#
# Purpose
#    Entity manager strategy using hash tables for entities
#
# Revision Dates
#    14-Oct-2009 (CT) Creation
#    15-Oct-2009 (CT) Creation continued
#    16-Oct-2009 (CT) Creation continued..
#    28-Oct-2009 (CT) I18N
#     4-Nov-2009 (CT) `sort_key` argument added to `s_role` and `t_role`
#     4-Nov-2009 (CT) `epk_to_hpk` and `hpk` for `MOM.Link` fixed
#    19-Nov-2009 (CT) Use `Type.sort_key (sort_key)` instead of
#                     `sort_key or Type.sorted_by` (3-compatibility)
#    20-Nov-2009 (CT) `sort_key = None` means no sorting,
#                     `sort_key = False` means use default sort-key for sorting
#    23-Nov-2009 (CT) `t_extension` changed to filter siblings of `Type` that
#                     are derived from the same `relevant_root`
#    23-Nov-2009 (CT) `exists`, `instance` and `s_extension` changed to
#                     filter siblings of `Type` that are derived from the
#                     same `relevant_root`
#    25-Nov-2009 (CT) `rename` (and `add`) changed to preserve `id`
#    27-Nov-2009 (CT) `add` and `remove` changed to call `register_dependency`
#                     and `unregister_dependency`, respectively
#    27-Nov-2009 (CT) `all_links` added
#     2-Dec-2009 (CT) `_Manager_` factored
#     2-Dec-2009 (CT) Query interface changed
#                     - added `count`, `query`, `r_query`, `_query_multi_root`,
#                       `_query_single_root`, and `_role_query`
#                     - removed `s_count`, `s_extension`, `s_role`,
#                       `t_extension`, and `t_role`
#                     - s/t_count/_t_count/
#     3-Dec-2009 (CT) `r_query` corrected
#     3-Dec-2009 (CT) `count` simplified
#     4-Dec-2009 (MG) `__init__`  changed to take `db_uri`
#    10-Dec-2009 (CT) s/id/pid/
#    10-Dec-2009 (CT) Stubs for `load_scope` and `_load_objects` added
#    14-Dec-2009 (CT) `__iter__` factored to `MOM.EMS._Manager_`
#    16-Dec-2009 (CT) `register_change` added, s/__id/__pid/, `__cid` added
#    16-Dec-2009 (CT) `commit` added
#    17-Dec-2009 (CT) `changes` and `async_changes` added
#    21-Dec-2009 (CT) s/load_scope/load_root/;
#                     `commit` factored to `EMS.Manager`
#    19-Jan-2010 (CT) `rollback` added
#    20-Jan-2010 (CT) `pid_as_lid` and `pid_from_lid` added
#     8-Feb-2010 (CT) `_remove` factored; `remove` changed to set `pid` to None
#     9-Feb-2010 (CT) `epk_to_hpk` changed to use `get_hash`
#     3-Mar-2010 (CT) `rename` changed to allow rename to same `epk`
#    19-Mar-2010 (CT) `_pid_map` added and `pid_query` redefined to use it
#    12-May-2010 (CT) Use `Pid_Manager` instead of home-grown code
#    12-May-2010 (CT) `pid_as_lid` and `pid_from_lid` removed
#    17-May-2010 (CT) `register_change` changed to accept `change` with `cid`
#    18-May-2010 (CT) Use `Change_Manager` instead of home-grown code
#    28-Sep-2010 (CT) s/rollback/_rollback/
#    17-Nov-2011 (CT) Change `rename` to not remove `entity` from `table`
#                     if `renamer` raises an exception
#    16-Apr-2012 (MG) `add` renamed to `_add`
#    19-Apr-2012 (CT) Use translated `.ui_name` instead of `.type_name` for
#                     exceptions
#     2-Jul-2012 (MG) `_add` renamed back to `add`
#     4-Aug-2012 (CT) Factor `remove` to `MOM.EMS._Manager_`
#     4-Aug-2012 (CT) Call `_rollback_uncommitted_changes`
#     8-Aug-2012 (CT) Change `add` to check roles amiss before touching tables
#                     (ditto for `_remove`)
#    11-Aug-2012 (CT) Change `instance` to delegate non-root types to `__super`
#    12-Aug-2012 (CT) Change `instance` to not use `logging.error`
#    11-Jan-2013 (CT) Add support for `primary_ais`
#    16-Jan-2013 (CT) Use `.E_Type.primary_ais`, not `.primary_ais`
#    16-Jan-2013 (CT) Use `setattr`, not `.set`, to set value of `primary_ais`
#    30-Jan-2013 (CT) Add optional argument `keep_zombies` to `rollback`
#    30-Jan-2013 (CT) Replace `add` by `_add` (called by `__super.add`)
#    30-Jan-2013 (CT) Call `.pm.flush_zombies` in `commit` and `_rollback`
#    26-Apr-2013 (CT) Remove support for `primary_ais`
#     6-Jun-2013 (CT) Add `max_surrs`; add support for surrogates to `_add`
#    26-Jun-2013 (CT) Add `lazy_load_p`
#     5-Jul-2013 (CT) Change sig of `_query_single_root`, `_query_multi_root`
#    17-Jul-2013 (CT) Remove `async_changes`, `db_cid`
#     1-Aug-2013 (CT) Don't reset `max_pid` in `rollback`
#    21-Aug-2013 (CT) Redefine `query` to kludgely support `MD_Change`
#    25-Aug-2013 (CT) Change `_add` to check `hpk in table` (optimization)
#    28-Aug-2013 (CT) Change `instance` to use `relevant_roots`, not `query`
#    22-Feb-2016 (CT) Change `load_root` do not call `scope._setup_root`
#    ««revision-date»»···
#--

from   __future__            import unicode_literals, print_function

from   _MOM                  import MOM
from   _TFL                  import TFL

import _MOM._EMS._Manager_
import _MOM.Error
import _MOM.Link
import _MOM.Object

import _TFL._Meta.Object

import _TFL.Accessor
import _TFL.Decorator
import _TFL.defaultdict

from   _TFL.I18N             import _, _T, _Tn
from   _TFL.predicate        import intersection_n
from   _TFL.pyk              import pyk

import itertools
import logging

class Manager (MOM.EMS._Manager_) :
    """Entity manager using hash tables to hold entities."""

    type_name           = "Hash"

    cm                  = property (TFL.Getter.session.cm)
    lazy_load_p         = False
    max_cid             = property (TFL.Getter.cm.max_cid)
    max_pid             = property (TFL.Getter.pm.max_pid)

    def __init__ (self, scope, db_url) :
        self.__super.__init__ (scope, db_url)
        self._counts    = TFL.defaultdict (int)
        self.max_surrs  = TFL.defaultdict (int)
        self._r_map     = TFL.defaultdict (lambda : TFL.defaultdict (set))
        self._tables    = TFL.defaultdict (dict)
    # end def __init__

    def all_links (self, obj_id) :
        r_map  = self._r_map
        result = sorted \
            ( itertools.chain (* (rm [obj_id] for rm in pyk.itervalues (r_map)))
            , key = self.scope.MOM.Id_Entity.sort_key_pm ()
            )
        return result
    # end def all_links

    def changes (self, * filters, ** kw) :
        if self.cm.to_load :
            self.session.load_changes ()
        result = self.Q_Result (self.cm)
        if filters or kw :
            result = result.filter (* filters, ** kw)
        return result
    # end def changes

    def commit (self) :
        self.__super.commit   ()
        self.pm.flush_zombies ()
    # end def commit

    def count (self, Type, strict) :
        if strict :
            result = self._counts  [Type.type_name]
        else :
            result = self._t_count (Type)
        return result
    # end def count

    def exists (self, Type, epk) :
        scope  = self.scope
        tables = self._tables
        root   = Type.relevant_root
        if root :
            roots = {root.type_name : root}
        else :
            roots = Type.relevant_roots
        return \
            [ getattr (scope, e.type_name)
            for e in (   tables [n].get (R.epk_to_hpk (* epk))
                     for (n, R) in pyk.iteritems (roots)
                     )
            if  isinstance (e, Type.Essence)
            ]
    # end def exists

    def instance (self, Type, epk) :
        root   = Type.relevant_root
        tables = self._tables
        if root :
            hpk    = Type.epk_to_hpk (* epk)
            result = tables [root.type_name].get (hpk)
            if not isinstance (result, Type.Essence) :
                result = None
        else :
            roots   = Type.relevant_roots
            results = \
                [   e
                for e in (   tables [n].get (R.epk_to_hpk (* epk))
                         for (n, R) in pyk.iteritems (roots)
                         )
                if  isinstance (e, Type.Essence)
                ]
            if len (results) > 1 :
                raise LookupError ("Multiple matches for %s" % (epk, ))
            else :
                result = results [0] if results else None
        return result
    # end def instance

    def load_root (self) :
        scope           = self.scope
        info            = self.session.info
        self.cm.max_cid = info.max_cid
        self.pm.max_pid = info.max_pid
        scope.guid      = info.guid
        scope.add_init_callback (self._load_objects)
    # end def load_root

    def query (self, Type, * filters, ** kw) :
        if Type.type_name == "MOM.MD_Change" :
            ### XXX
            ### * returns MOM.SCM.Change, not MOM.MD_Change, instances
            ### * change that
            kw.pop ("strict", None)
            result = self.changes (* filters, ** kw)
        else :
            result = self.__super.query (Type, * filters, ** kw)
        return result
    # end def query

    def register_change (self, change) :
        self.cm.add                  (change)
        self.__super.register_change (change)
    # end def register_change

    def rename (self, entity, new_epk, renamer) :
        new_hpk = entity.epk_to_hpk (* new_epk)
        root    = entity.relevant_root
        table   = self._tables [root.type_name]
        if new_hpk in table :
            old = table [new_hpk]
            if entity is old :
                return
            else :
                raise MOM.Error.Name_Clash (entity, old)
        self._remove (entity)
        try :
            renamer ()
        except :
            self.add (entity, entity.pid)
            raise
        self.add (entity, entity.pid)
    # end def rename

    def r_query (self, Type, rkw, * filters, ** kw) :
        r_map   = self._r_map
        strict  = kw.pop ("strict", False)
        q       = [self._r_query_t, self._r_query_s] [strict]
        queries = []
        for (rn, obj) in pyk.iteritems (rkw) :
            try :
                i = Type.role_map [rn]
            except KeyError :
                print (Type, Type.Roles, Type.role_map)
                raise
            role = Type.Roles [i]
            queries.append (q (r_map, role, obj))
        result = self.Q_Result (intersection_n (* queries), * filters, ** kw)
        return result
    # end def r_query

    def _add (self, entity, pid = None) :
        count = self._counts
        root  = entity.relevant_root
        table = self._tables [root.type_name]
        hpk   = entity.hpk
        if hpk in table :
            ### `hpk in table` is way more efficient than predicate checking
            ### the uniqueness predicate gives a nicer (and
            ### backend-independent) error message
            ### --> let redundant check of uniqueness predicate trigger error
            self._check_uniqueness (entity, entity.E_Type.uniqueness_dbw)
        if entity.max_count and entity.max_count <= count [entity.type_name] :
            raise MOM.Error.Too_Many_Objects (entity, entity.max_count)
        self.pm (entity, pid)
        if entity.Roles :
            refs  = tuple ((r, r.get_role (entity)) for r in entity.Roles)
            amiss = tuple (r for r, o in refs if o is None)
            if amiss :
                raise TypeError ("Roles %s of %r are empty" % (amiss, entity))
            r_map = self._r_map
            for r, obj in refs :
                obj.register_dependency (entity.__class__)
                r_map [r] [obj.pid].add (entity)
        count [entity.type_name] += 1
        table [hpk] = entity
        max_surrs   = self.max_surrs
        for sk in entity.surrogate_attr [1:] :
            v  = sk.get_value (entity)
            ms = max_surrs [sk.q_name]
            if v is None :
                ms += 1
                sk.__set__ (entity, ms)
            else :
                ms = max (v, ms)
            max_surrs [sk.q_name] = ms
    # end def _add

    def _load_objects (self, scope = None) :
        self.session.load_objects ()
    # end def _load_objects

    def _query_multi_root (self, Type, strict = False) :
        tables = self._tables
        return self.Q_Result_Composite \
            ( [   self.Q_Result (pyk.itervalues (tables [t]))
              for t in Type.relevant_roots
              ]
            )
    # end def _query_multi_root

    def _query_single_root (self, Type, strict = False) :
        root   = Type.relevant_root
        tables = self._tables
        result = pyk.itervalues (tables [root.type_name])
        if root is not Type :
            ### filter siblings derived from same `relevant_root`
            result = pyk.ifilter (lambda x : isinstance (x, Type), result)
        return self.Q_Result (result)
    # end def _query_single_root

    def _r_query_s (self, r_map, role, obj) :
        return r_map [role] [obj.pid]
    # end def _r_query_s

    def _r_query_t (self, r_map, role, obj) :
        i = role.role_index
        return itertools.chain \
            ( r_map [role] [obj.pid]
            , * ( r_map [c.Roles [i]] [obj.pid]
                for c in pyk.itervalues (role.assoc.children)
                )
            )
    # end def _r_query_t

    def _remove (self, entity) :
        count = self._counts
        hpk   = entity.hpk
        root  = entity.relevant_root
        table = self._tables [root.type_name]
        if entity.Roles :
            refs  = tuple ((r, r.get_role (entity)) for r in entity.Roles)
            amiss = tuple (r for r, o in refs if o is None)
            if amiss :
                raise TypeError ("Roles %s of %r are empty" % (amiss, entity))
            r_map = self._r_map
            for r, obj in refs :
                obj.unregister_dependency  (entity.__class__)
                r_map [r] [obj.pid].remove (entity)
        try :
            del table [hpk]
            count [entity.type_name] -= 1
        except KeyError :
            logging.exception ("%r: hpk = %s", entity, hpk)
    # end def _remove

    def _rollback (self, keep_zombies) :
        self._rollback_uncommitted_changes ()
        self.cm.rollback (self.session)
        self.__super._rollback (keep_zombies)
        if not keep_zombies :
            self.pm.flush_zombies ()
    # end def _rollback

    def _t_count (self, Type, seen = None) :
        if seen is None :
            seen = set ()
        result = self._counts [Type.type_name]
        for n, c in pyk.iteritems (Type.children) :
            if n not in seen :
                seen.add (n)
                result += self._t_count (c, seen)
        return result
    # end def _t_count

# end class Manager

@TFL.Add_Method (MOM.Id_Entity)
@TFL.Meta.Class_Method
def epk_to_hpk (cls, * epk) :
    return tuple (a.get_hash (None, k) for a, k in zip (cls.primary, epk))
# end def epk_to_hpk

@TFL.Add_Method (MOM.Id_Entity, decorator = property)
def hpk (self) :
    return self.epk_to_hpk (* self.epk)
# end def hpk

if __name__ != "__main__" :
    MOM.EMS._Export_Module ()
### __END__ MOM.EMS.Hash
