# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package MOM.SCM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    MOM.SCM.Summary
#
# Purpose
#    Convert a list of changes into a change summary per object
#
# Revision Dates
#     2-Sep-2010 (CT) Creation
#     3-Sep-2010 (CT) Creation continued
#     8-Sep-2010 (CT) Creation continued..
#    14-Sep-2010 (CT) `Summary` rewritten to store `changes`,
#                     `Pid.changed_attrs` added
#    14-Sep-2010 (CT) `entities` added
#    15-Sep-2010 (CT) Use `SCM.Change.modified_attrs` instead of home-grown code
#    16-Sep-2010 (CT) `Summary`: s/clear/_clear/
#    22-Sep-2010 (CT) `Summary.change_conflicts` and `_check_*_conflicts` added
#    24-Sep-2010 (CT) `Attr_Summary.check_conflict` and `.check_ini_vs_cur`
#                     factored
#    24-Sep-2010 (CT) `Pid.epk`, `.by_epk`, and `.type_name` added,
#                     `.check_attr_conflicts` and `.check_ini_vs_cur` factored
#    24-Sep-2010 (CT) `Pid.apply` added
#    28-Sep-2010 (CT) `_Entity_Summary_` factored from `Pid`
#    28-Sep-2010 (CT) `Attr_C_Summary.check_conflict` and `.check_ini_vs_cur`
#                     added
#     7-May-2012 (CT) Add `entities_transitive`
#    24-Apr-2013 (CT) Remove idempodent changes from `attribute_changes`
#    24-Apr-2013 (CT) Add check for `is_born and is_dead` to `Pid.__nonzero__`
#    24-Apr-2013 (CT) Don't add `new` for `is_dead` to `attribute_changes`
#    24-Apr-2013 (CT) Add `Summary.entity_changes`
#     3-Jun-2013 (CT) Use `.attr_prop` to access attribute descriptors
#     5-May-2015 (CT) Add `as_json_cargo`, `from_pickle_cargo`;
#                     add `json_encode_change` to `TFL.json_dump.default`
#     6-May-2015 (CT) Add `redo`, `restore`, `undo`
#    ««revision-date»»···
#--

from   _MOM                  import MOM
from   _TFL                  import TFL

import _MOM._SCM.Change

from   _TFL.portable_repr    import portable_repr
from   _TFL.pyk              import pyk

import _TFL._Meta.Object
import _TFL._Meta.Once_Property
import _TFL.Accessor
import _TFL.defaultdict
import _TFL.json_dump
import _TFL.predicate
import _TFL.Undef

import itertools

class _Entity_Summary_ (TFL.Meta.Object) :

    def check_attr_conflicts (self, entity, initial_values) :
        result = False
        for name, acs in pyk.iteritems (self.attribute_changes) :
            attr    = entity.attr_prop   (name)
            ini     = initial_values.get (name)
            result += acs.check_conflict (attr, entity, ini)
        return result
    # end def check_attr_conflicts

    def check_ini_vs_cur (self, entity, initial_values, r_name) :
        result    = False
        check_all = not self.is_dead
        for name, ini in pyk.iteritems (initial_values) :
            attr  = entity.attr_prop (name)
            if check_all or not attr.electric :
                result += acs.check_ini_vs_cur (attr, entity, ini, r_name)
        return result
    # end def check_ini_vs_cur

# end class _Entity_Summary_

@pyk.adapt__bool__
class Attr_Summary (TFL.Meta.Object) :
    """Change summary for a single attribute of a single `pid`."""

    conflicts = False
    merges    = False

    cur = ini = None
    new = old = undef = TFL.Undef ("attr")

    def add (self, old, new) :
        if self.old is self.undef :
            self.old = old
        self.new = new
    # end def add

    def check_conflict (self, attr, entity, ini) :
        self.conflicts = False
        self.cur = cur = attr.get_raw (entity)
        self.ini = ini
        if not attr.electric :
            self.conflicts = (self.new != cur and ini != cur)
        self.merges = (self.new != ini)
        return self.conflicts
    # end def check_conflict

    def check_ini_vs_cur (self, attr, entity, ini, r_name) :
        self.ini = ini
        self.cur = cur = attr.get_raw (entity)
        result   = (ini != cur)
        setattr (self, r_name, result)
        return result
    # end def check_ini_vs_cur

    def __bool__ (self) :
        return self.old is not self.undef
    # end def __bool__

    def __repr__ (self) :
        return "(old = %s, new = %s)" % \
            (portable_repr (self.old), portable_repr (self.new))
    # end def __repr__

# end class Attr_Summary

@pyk.adapt__bool__
class Attr_C_Summary (_Entity_Summary_) :
    """Change summary for a composite attribute of a single `pid`."""

    def __init__ (self, attr_summary, is_dead) :
        self.attribute_changes = acs = TFL.defaultdict (Attr_Summary)
        if attr_summary :
            old = dict (attr_summary.old)
            if not is_dead :
                new = dict (attr_summary.new)
            else :
                n = None
            for a in set (itertools.chain (old, new)) :
                o = old.get (a)
                if not is_dead :
                    n = new.get (a)
                acs [a].add (o, n)
    # end def __init__

    @property
    def cur (self) :
        return tuple \
            (   (k, v.cur)
            for (k, v) in sorted (pyk.iteritems (self.attribute_changes))
            )
    # end def cur

    @property
    def new (self) :
        return tuple \
            (   (k, v.new)
            for (k, v) in sorted (pyk.iteritems (self.attribute_changes))
            )
    # end def new

    @property
    def old (self) :
        return tuple \
            (   (k, v.old)
            for (k, v) in sorted (pyk.iteritems (self.attribute_changes))
            )
    # end def old

    def check_conflict (self, attr, entity, ini) :
        if ini is None :
            ini        = {}
        an_entity      = attr.get_value (entity)
        self.conflicts = result = self.check_attr_conflicts (an_entity, ini)
        self.entity    = an_entity
        self.ini       = ini
        return result
    # end def check_conflict

    def check_ini_vs_cur (self, attr, entity, ini, r_name) :
        if ini is None :
            ini        = {}
        an_entity      = attr.get_value (entity)
        self.entity    = an_entity
        self.ini       = ini
        self.merges    = result = self.__super.check_ini_vs_cur \
            (an_entity, ini, r_name)
        return result
    # end def check_ini_vs_cur

    def items (self) :
        return self.attribute_changes.items ()
    # end def items

    def iteritems (self) :
        return pyk.iteritems (self.attribute_changes)
    # end def iteritems

    def iterkeys (self) :
        return pyk.iterkeys (self.attribute_changes)
    # end def iterkeys

    def itervalues (self) :
        return pyk.itervalues (self.attribute_changes)
    # end def itervalues

    def keys (self) :
        return self.attribute_changes.keys ()
    # end def keys

    def values (self) :
        return self.attribute_changes.values ()
    # end def values

    def __getitem__ (self, key) :
        return self.attribute_changes [key]
    # end def __getitem__

    def __iter__ (self) :
        return iter (self.attribute_changes)
    # end def __iter__

    def __len__ (self) :
        return len (self.attribute_changes)
    # end def __len__

    def __bool__ (self) :
        return bool (self.attribute_changes)
    # end def __bool__

    def __getitem__ (self, key) :
        return self.attribute_changes [key]
    # end def __getitem__

    def __repr__ (self) :
        return "(old = %s, new = %s)" % \
            (portable_repr (self.old), portable_repr (self.new))
    # end def __repr__

# end class Attr_C_Summary

@pyk.adapt__bool__
class Pid (_Entity_Summary_) :
    """Change summary for a single `pid`."""

    entity = None

    def __init__ (self, pid) :
        self.pid      = pid
        self._changes = set ()
    # end def __init__

    @TFL.Meta.Once_Property
    def attribute_changes (self) :
        result  = TFL.defaultdict (Attr_Summary)
        is_dead = self.is_dead
        new     = None
        for c in self.changes :
            r = result
            if isinstance (c, MOM.SCM.Change.Attr_Composite) :
                r = result [c.attr_name] = Attr_C_Summary \
                    (result.get (c.attr_name), is_dead)
            for a in set (itertools.chain (c.old_attr, c.new_attr)) :
                old = c.old_attr.get (a)
                if not is_dead :
                    new = c.new_attr.get (a)
                res = (result if a == "last_cid" else r)
                res [a].add (old, new)
        for a, ra in list (pyk.iteritems (result)) :
            if ra.old == ra.new :
                del result [a]
        return result
    # end def attribute_changes

    @TFL.Meta.Once_Property
    def changed_attrs (self) :
        result = set ()
        for c in self.changes :
            result.update (c.modified_attrs)
        return result
    # end def changed_attrs

    @TFL.Meta.Once_Property
    def changes (self) :
        return sorted (self._changes, key = TFL.Getter.cid)
    # end def changes

    @TFL.Meta.Once_Property
    def epk (self) :
        changes = self.changes
        return changes and changes [-1].epk
    # end def epk

    @TFL.Meta.Once_Property
    def is_born (self) :
        changes = self.changes
        return changes and isinstance (changes [0], MOM.SCM.Change.Create)
    # end def is_born

    @TFL.Meta.Once_Property
    def is_dead (self) :
        changes = self.changes
        return changes and isinstance (changes [-1], MOM.SCM.Change.Destroy)
    # end def is_dead

    @TFL.Meta.Once_Property
    def type_name (self) :
        changes = self.changes
        return changes and changes [0].type_name
    # end def type_name

    def add (self, c) :
        self._changes.add (c)
    # end def add

    def apply (self, scope) :
        kw = dict \
            ( (name, acs.new)
            for name, acs in pyk.iteritems (self.attribute_changes)
            if  acs.merges and not acs.conflicts
            )
        if self.is_born and not self.entity :
            etm = scope [self.type_name]
            self.entity = etm (* self.epk, raw = True)
        if self.entity :
            self.entity.set_raw (kw)
    # end def apply

    def _repr (self) :
        parts = []
        n     = len (self) - self.is_born - self.is_dead
        if self.is_born :
            parts.append ("newborn")
        if n > 0 :
            parts.append ("%s change%s" % (n, "s" if n > 1 else ""))
        if self.is_dead :
            parts.append ("just died")
        return "Change Summary for pid %s: %s" % (self.pid, ", ".join (parts))
    # end def _repr

    def _repr_lines (self, level = 0) :
        result = ["%s<%s>" % ("  " * level, self._repr ())]
        for c in self.changes :
            result.extend (c._repr_lines (level + 1))
        return result
    # end def _repr_lines

    def __len__ (self) :
        return len (self._changes)
    # end def __len__

    def __bool__ (self) :
        return bool (self._changes) and not (self.is_born and self.is_dead)
    # end def __bool__

    def __repr__ (self) :
        return "\n  ".join (self._repr_lines ())
    # end def __repr__

# end class Pid

@pyk.adapt__bool__
class Summary (TFL.Meta.Object) :
    """Summary of changes per `pid`"""

    def __init__ (self) :
        self._clear ()
    # end def __init__

    @property
    def as_json_cargo (self) :
        return list (c.as_json_cargo for c in self._changes)
    # end def as_json_cargo

    @property
    def by_pid (self) :
        result = self._by_pid
        if result is None :
            result = self._by_pid = TFL.defaultdict_kd (Pid)
            self._add_to_by_pid (self._changes)
        return result
    # end def by_pid

    @property
    def changed_attrs (self) :
        result = dict ()
        for pid, csp in pyk.iteritems (self.by_pid) :
            if csp.changed_attrs and not csp.is_dead :
                result [pid] = csp.changed_attrs
        return result
    # end def changed_attrs

    @property
    def changes (self) :
        return self._changes
    # end def changes

    @classmethod
    def from_json_cargo (cls, cargo) :
        result = cls ()
        fjc    = MOM.SCM.Change._Change_.from_json_cargo
        result._changes = list (fjc (c) for c in cargo)
        return result
    # end def from_json_cargo

    def add (self, c) :
        self._changes.append (c)
        self._by_pid = None
    # end def add

    def change_conflicts (self, initial_values, scope) :
        """Determine conflicts between `self.changes` and the entities of
           `scope`, compared to attribute values in `initial_values`.
        """
        result = self.conflicts, self.merges = set (), set ()
        by_epk = self.by_epk
        for csp in pyk.itervalues (self.by_pid) :
            args = (initial_values.get (csp.pid, {}), scope, csp) + result
            by_epk [(csp.type_name, csp.epk)] = csp
            if csp.is_dead :
                self._check_dead_conflicts (* args)
            elif csp.is_born :
                self._check_born_conflicts (* args)
            else :
                self._check_attr_conflicts (* args)
        return result
    # end def change_conflicts

    def entities (self, ems) :
        for pid, csp in pyk.iteritems (self.by_pid) :
            if not csp.is_dead :
                yield ems.pid_query (pid)
    # end def entities

    def entities_transitive (self, ems) :
        def _gen (self, ems) :
            for e in self.entities (ems) :
                yield e
                for iea in e.id_entity_attr :
                    v = iea.get_value (e)
                    if v is not None :
                        yield v
        return TFL.uniq (_gen (self, ems))
    # end def entities_transitive

    def entity_changes (self, scope) :
        by_pid = self.by_pid
        for e in self.entities (scope.ems) :
            c = by_pid [e.pid]
            yield e, c.attribute_changes
    # end def entity_changes

    def redo (self, scope) :
        for c in self :
            c.redo (scope)
    # end def redo

    def restore (self, scope) :
        for c in self :
            c.restore (scope)
    # end def restore

    def undo (self, scope) :
        for c in reversed (self) :
            c.undo (scope)
    # end def undo

    def _add_to_by_pid (self, changes) :
        by_pid = self._by_pid
        for c in changes :
            if c.pid :
                by_pid [c.pid].add (c)
            if c.children :
                self._add_to_by_pid (c.children)
    # end def _add_to_by_pid

    def _check_attr_conflicts (self, initial_values, scope, csp, conflicts, merges) :
        try :
            entity = csp.entity = scope.ems.pid_query (csp.pid)
        except LookupError :
            conflicts.add (csp.pid)
        else :
            if csp.check_attr_conflicts (entity, initial_values) :
                conflicts.add (csp.pid)
            if csp.check_ini_vs_cur (entity, initial_values, "merges") :
                merges.add (csp.pid)
    # end def _check_attr_conflicts

    def _check_born_conflicts (self, initial_values, scope, csp, conflicts, merges) :
        etm    = scope [csp.type_name]
        entity = csp.entity = etm.instance (* csp.epk, raw = True)
        if entity :
            if csp.check_attr_conflicts (entity, initial_values) :
                conflicts.add (csp.pid)
    # end def _check_born_conflicts

    def _check_dead_conflicts (self, initial_values, scope, csp, conflicts, merges) :
        try :
            entity = csp.entity = scope.ems.pid_query (csp.pid)
        except LookupError :
            pass
        else :
            if csp.check_ini_vs_cur (entity, initial_values, "conflicts") :
                conflicts.add (csp.pid)
    # end def _check_dead_conflicts

    def _clear (self) :
        self._changes = []
        self._by_pid  = None
        self.by_epk   = {}
    # end def _clear

    def __getitem__ (self, index) :
        return self._changes [index]
    # end def __getitem__

    def __iter__ (self) :
        return iter (self._changes)
    # end def __iter__

    def __len__ (self) :
        return len (self._changes)
    # end def __len__

    def __bool__ (self) :
        return bool (self._changes)
    # end def __bool__

# end class Summary

@TFL.json_dump.default.add_type (Summary)
def json_encode_change (s) :
    return s.as_json_cargo
# end def json_encode_change

if __name__ != "__main__" :
    MOM.SCM._Export ("Summary")
### __END__ MOM.SCM.Summary
