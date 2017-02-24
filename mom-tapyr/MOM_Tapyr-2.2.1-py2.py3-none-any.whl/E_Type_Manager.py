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
#    MOM.E_Type_Manager
#
# Purpose
#    Scope-specific manager for essential object- and link-types
#
# Revision Dates
#    16-Oct-2009 (CT) Creation
#    27-Oct-2009 (CT) s/Scope_Proxy/E_Type_Manager/
#     3-Nov-2009 (CT) Type conversions for `epk` added
#     4-Nov-2009 (CT) Rename classes to `Id_Entity`, `Object`, and `Link` and
#                     call `MOM._Export_Module` instead of `MOM._Export`
#     4-Nov-2009 (CT) Type conversions for `epk` fixed
#     4-Nov-2009 (CT) `Link.s_links_of_obj`, `Link.t_links_of_obj` added
#     4-Nov-2009 (CT) `Link2` added
#    20-Nov-2009 (CT) `Link3` and `Link2_Ordered` added
#    22-Nov-2009 (CT) Documentation added
#    23-Nov-2009 (CT) `Link.__init__` added to define queries for `role_names`
#    23-Nov-2009 (CT) `_check_multiplicity` added
#    23-Nov-2009 (CT) `_role_query` changed to sue `_cooked_role`
#    23-Nov-2009 (CT) `__repr__` added
#    24-Nov-2009 (CT) Support for `No_Such_Object` added to
#                     `_cooked_epk_iter` and `_role_to_cooked_iter`
#    25-Nov-2009 (CT) `_role_query` guarded agains `No_Such_Object`
#     1-Dec-2009 (CT) `role_names` queries changed from `s_` to `t_`
#     2-Dec-2009 (CT) Queries `count` and `query` added
#     2-Dec-2009 (CT) Use `ems.role_query` instead of `s_role` and `t_role`
#     3-Dec-2009 (CT) `count` changed to be a property,
#                     `t_count` renamed to `count_transitive`
#     3-Dec-2009 (MG) `r_query` type check of role objects added
#    14-Dec-2009 (CT) `__call__` changed to call `scope.add`
#    22-Dec-2009 (CT) `Link2_Ordered` removed
#    18-Jan-2010 (CT) s/_check_multiplicity/_checked_roles/
#    20-Jan-2010 (CT) `pid_query`, `pid_as_lid`, and `pid_from_lid` added
#    21-Jan-2010 (CT) `epkified` used
#    21-Jan-2010 (CT) `_cooked_epk_iter` changed to check
#                     `if v is not None` instead of `if v`
#     4-Feb-2010 (CT) `Link.__call__` changed to use `epkified`, too
#     4-Feb-2010 (CT) `Entity` factored, `An_Entity` added
#     8-Feb-2010 (CT) `__getattr__` and `__repr__` moved from `Id_Entity` to
#                     `Entity`
#    18-Feb-2010 (CT) `Link1` added
#    26-Feb-2010 (CT) `Object.singleton` added
#     3-Mar-2010 (CT) `instance_or_new` added
#     3-Mar-2010 (CT) Guard for `kw` removed from `instance`
#    27-Apr-2010 (CT) `Object._cooked_epk` factored and changed to use
#                     `_cooked_epk_iter` and `_raw_epk_iter`, depending on `raw`
#    27-Apr-2010 (CT) `Link._cooked_epk` factored;
#                     s/Link._cooked_epk_iter/Link._raw_epk_iter/
#    27-Apr-2010 (CT) `Link._role_to_cooked_iter` changed to call `cooked`
#                     for non-role epk attributes
#     3-May-2010 (CT) `_epkified` added instead of direct calls to `epkified`
#     3-May-2010 (CT) `this` added to return of `_cooked_epk`
#    12-May-2010 (CT) `pid_as_lid` and `pid_from_lid` removed
#    13-Oct-2010 (CT) `default_child` added and used in `_role_to_cooked_iter`
#    13-Oct-2010 (CT) `example` added
#    24-Feb-2011 (CT) `Link._role_to_raw_iter` changed to use `v.epk_raw`
#                     instead of `r.as_code (v)`
#    24-Feb-2011 (CT) DRY cleanups for `instance` and `exists` (Object, Link)
#     9-Jun-2011 (MG) `Object.ac_query` added
#    16-Jul-2011 (CT) `attr_completion` (and `_acq_gen`) added
#    18-Jul-2011 (CT) `attr_completion` changed to return a `Q_Result` instead
#                     of a `list`
#    18-Jul-2011 (CT) `query_1` added
#    19-Jul-2011 (CT) s/_cooked_epk/cooked_epk/ and factored up to `Id_Entity`
#    19-Jul-2011 (CT) `attr_completion` changed to use `Q.RAW` if argument `raw`
#    22-Jul-2011 (CT) `attr_completion` removed, s/ac_query/ac_query_auto_split/
#    22-Jul-2011 (CT) `_acq_gen` renamed to `ac_query_attrs`
#    26-Jul-2011 (CT) `ckd_query_attrs` and `raw_query_attrs` added
#    28-Jul-2011 (CT) `ckd_query_attrs` and `raw_query_attrs` changed to
#                     support `values = None`
#     9-Sep-2011 (CT) Property `E_Type` added
#    21-Sep-2011 (CT) `get_etype_attribute` added and used for `raw_query_attrs`
#    22-Sep-2011 (CT) s/Class/P_Type/ for _A_Id_Entity_ attributes
#     8-Nov-2011 (CT) Add exception handler to `ac_query_attrs` (for some
#                     attribute types, partial completions can trigger errors)
#    11-Nov-2011 (CT) Replace `ac_query` by `Q.AC`
#    15-Nov-2011 (CT) Change `query_s` and `r_query_s`
#     4-Dec-2011 (CT) Change `ac_query_attrs` and `ac_query_auto_split` to
#                     use `E_Type.AQ`
#    20-Dec-2011 (CT) Remove `ckd_query_attrs`
#    20-Dec-2011 (CT) Add guard against `None` to `ac_query_attrs`
#    15-Feb-2012 (CT) Adapt to change of `max_links` (now `-1` means unlimited)
#    15-Apr-2012 (CT) Adapted to changes of `MOM.Error`
#    19-Apr-2012 (CT) Use translated `.ui_name` instead of `.type_name` for
#                     exceptions
#    20-Apr-2012 (CT) Change `Link.__call__` and `instance_or_new` to let
#                     `MOM.Entity` handle `MOM.Error.Required_Missing`
#    30-Apr-2012 (CT) Add `epk, kw` to call of `Duplicate_Link`
#    29-Jun-2012 (CT) Rename `count` to `count_strict`,
#                     rename `count_transitive` to `count`
#                     (to make it consistent with `query`)
#     4-Aug-2012 (CT) Add `pid` to `Id_Entity.__call__`
#     5-Aug-2012 (CT) Change `_cooked_role` to accept `int`
#     7-Aug-2012 (CT) Change `An_Entity.example` default of `full` to `True`
#     8-Aug-2012 (CT) Guard against exceptions in `example`
#    11-Aug-2012 (CT) Change `Id_Entity.example` to ignore `Partial_Type`
#    21-Sep-2012 (CT) Change `Link.__call__` to call `E_Type.child_np`
#    24-Sep-2012 (CT) Remove `Link._role_to_raw_iter`
#    10-Oct-2012 (CT) Change `raw_query_attrs` to return `tuple`
#    11-Dec-2012 (CT) Add `Entity.__instancecheck__`, `.__subclasscheck__`
#    13-Dec-2012 (CT) Move `ac_query_attrs` and `raw_query_attrs` to `Entity`,
#                     add optional argument `AQ` to both
#    30-Jan-2013 (CT) Remove check for `Duplicate_Link` from `_checked_roles`
#                     (is checked by Unique predicate anyway)
#    26-Feb-2013 (CT) Adapt to change of `MOM.Error.Multiplicity`
#    13-May-2013 (CT) Change `r_query` to look at non-role id-entity
#                     attributes, not call `ems.r_query`
#     3-Jun-2013 (CT) Get attribute descriptors from `etype.attributes`
#     4-Jun-2013 (CT) Change `getattr` to try `etype` first, then `.attributes`
#    11-Jun-2013 (CT) Add error guards to `raw_query_attrs`
#    21-Aug-2013 (CT) Factor `ems` and `query` from `Id_Entity` to `Entity`
#    19-Aug-2014 (CT) Factor `ac_ui_display` in here
#    30-Aug-2014 (CT) Add `dict` to `isinstance` check in `Link._cooked_role`
#    26-Sep-2014 (CT) Change `_epkified` to use `_kw_polished`, if possible
#    26-Sep-2014 (CT) Use `_kw_polished` for `raw` only
#    15-Jun-2015 (CT) Add guard for `None` to `_cooked_role`
#    30-Jul-2015 (CT) Pass idempotent `on_error` to `_kw_polished`
#     8-Oct-2015 (CT) Change `__getattr__` to *not* handle `__XXX__`
#     8-Jun-2016 (CT) Change `get_etype_attribute` to use `etype.AQ`
#                     * DRY
#                     * Home-grown code didn't support type restriction
#    20-Oct-2016 (CT) Add `limit (2)` to `query_1` and `singleton`
#    20-Oct-2016 (CT) Change `r_query` to use `self.query`, not `ems.query`
#    ««revision-date»»···
#--

from   _MOM import MOM
from   _TFL import TFL

import _TFL._Meta.Object
import _TFL._Meta.Once_Property

from   _TFL.predicate        import first, paired
from   _TFL.Decorator        import getattr_safe
from   _TFL.I18N             import _, _T, _Tn

import itertools
import logging

class Entity (TFL.Meta.Object) :
    """Base class for scope-specific E_Type managers."""

    def __init__ (self, etype, scope) :
        self._etype     = etype
        self.home_scope = scope
    # end def __init__

    def __call__ (self, * args, ** kw) :
        return self._etype (* args, scope = self.home_scope, ** kw)
    # end def __call__

    @TFL.Meta.Once_Property
    @getattr_safe
    def default_child (self) :
        """The default child of partial entity types, if any."""
        dc = self._etype.default_child
        if dc is not None :
            try :
                return self.home_scope [dc]
            except KeyError :
                pass
    # end def default_child

    @property
    @getattr_safe
    def ems (self) :
        return self.home_scope.ems
    # end def ems

    @property
    @getattr_safe
    def E_Type (self) :
        return self._etype
    # end def E_Type

    @TFL.Meta.Once_Property
    @getattr_safe
    def is_partial (self) :
        return self._etype.is_partial
    # end def is_partial

    def ac_query_attrs (self, names, values, AQ = None) :
        if AQ is None :
            AQ = self._etype.AQ
        for n in names :
            if n in values :
                try :
                    vq = getattr (AQ, n).AC (values [n])
                except (ValueError, TypeError) :
                    pass
                else :
                    if vq is not None :
                        yield vq
    # end def ac_query_attrs

    def ac_ui_display (self, names, matches) :
        def _gen (self, names) :
            for n in names :
                try :
                    attr = self.get_etype_attribute (n)
                except AttributeError :
                    disp = lambda v : getattr (v, "ui_display", v)
                else :
                    disp = attr.ac_ui_display
                yield disp
        attr_displayers = list (_gen (self, names))
        for match in matches :
            yield tuple (d (v) for d, v in zip (attr_displayers, match))
    # end def ac_ui_display

    def get_etype_attribute (self, name) :
        etype  = self._etype
        result = getattr (etype.AQ, name)._attr.kind
        return result
    # end def get_etype_attribute

    def query (self, * filters, ** kw) :
        """Return all entities matching the conditions in `filters` and `kw`.

           When no `filters` or `kw` are specified, `query` returns the
           transitive extension of the type in question, i.e., all instances
           of the type and all its subclasses.

           When `strict = True` is specified as the only argument, `query`
           returns the strict extension, i.e., all instances of the type in
           question, but none of its subclasses.

           All other filters reduce the number of instances returned to those
           that satisfy the filter conditions.
        """
        sort_key = kw.pop ("sort_key", None)
        Type     = self._etype
        result   = self.ems.query (Type, * filters, ** kw)
        if sort_key is not None :
            result = result.order_by (sort_key)
        return result
    # end def query

    def raw_query_attrs (self, names, values = None, AQ = None) :
        if AQ is None :
            AQ = self._etype.AQ
        def _gen (self, names, values, AQ) :
            if values is None :
                for n in names :
                    aq = getattr (AQ, n)
                    if aq is not None :
                        yield aq
                    else :
                        raise MOM.Error.Attribute_Unknown (None, n, None)
            else :
                for n in names :
                    if n in values :
                        aq = getattr (AQ, n)
                        v  = values [n]
                        if aq is not None :
                            eq = aq.EQ (v)
                            if eq is not None :
                                yield eq
                            else :
                                raise MOM.Error.Attribute_Syntax \
                                    (None, aq._attr, v)
                        else :
                            raise MOM.Error.Attribute_Unknown (None, n, v)
        return tuple (_gen (self, names, values, AQ))
    # end def raw_query_attrs

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        etype = self._etype
        try :
            return getattr (etype, name)
        except Exception :
            try :
                return etype.attributes [name]
            except KeyError :
                raise AttributeError
    # end def __getattr__

    def __instancecheck__ (self, instance) :
        return isinstance (instance, self.E_Type.Essence)
    # end def __instancecheck__

    def __subclasscheck__ (self, subclass) :
        return issubclass (subclass, self.E_Type.Essence)
    # end def __subclasscheck__

    def __repr__ (self) :
        return "<E_Type_Manager for %s of scope %s>" % \
            (self._etype.type_name, self.home_scope.name)
    # end def __repr__

# end class Entity

class An_Entity (Entity) :
    """Scope-specific manager for a specific type of anonymous entities."""

    def example (self, full = True) :
        return self (raw = True, ** self._etype.example_attrs (full))
    # end def example

    def query (self, * args, ** kw) :
        ### we need to define this function to hide the `query` attribute of
        ### the entities (which is a list of all attributes with the kind
        ### `Query`)
        return TFL.Q_Result (())
    # end def query

# end class An_Entity

class Id_Entity (Entity) :
    """Scope-specific manager for a specific essential object- or link-type."""

    def __call__ (self, * args, ** kw) :
        pid = kw.pop ("__pid", None)
        result = self.__super.__call__ (* args, ** kw)
        self.home_scope.add (result, pid = pid)
        return result
    # end def __call__

    @property
    @getattr_safe
    def count (self) :
        """Return the transitive count of objects or links."""
        return self.ems.count (self._etype, strict = False)
    # end def count

    @property
    @getattr_safe
    def count_strict (self) :
        """Return the strict count of objects or links."""
        result = self.ems.count (self._etype, strict = True)
        assert (not self.E_Type.is_partial) or result == 0
        return result
    # end def count_strict

    def cooked_epk (self, epk, kw) :
        (epk, kw), this  = self._epkified (* epk, ** kw)
        raw      = kw.get ("raw", False)
        epk_iter = (this._raw_epk_iter if raw else this._cooked_epk_iter)
        return tuple (epk_iter (epk)), kw, this
    # end def cooked_epk

    def example (self, full = False) :
        with self.home_scope.example_etm (self) as x_etm :
            try :
                return x_etm.instance_or_new \
                    (raw = True, ** x_etm._etype.example_attrs (full))
            except MOM.Error.Partial_Type as exc :
                pass
            except Exception as exc :
                if __debug__ :
                    logging.exception ("\n    %s.example", self.type_name)
    # end def example

    def exists (self, * epk, ** kw) :
        """Return true if an object or link with primary key `epk` exists."""
        epk, kw, this = self.cooked_epk (epk, kw)
        kw.pop ("on_error", None)
        if kw :
            raise TypeError (kw)
        return this.ems.exists (this._etype, epk)
    # end def exists

    def instance (self, * epk, ** kw) :
        """Return the object or link with primary key `epk` or None."""
        epk, kw, this = self.cooked_epk (epk, kw)
        return this.ems.instance (this._etype, epk)
    # end def instance

    def instance_or_new (self, * epk, ** kw) :
        try :
            result = self.instance (* epk, ** kw)
        except MOM.Error.Error :
            ### let MOM.Entity handle this case
            result = None
        if result is None :
            result = self (* epk, ** kw)
        return result
    # end def instance_or_new

    def pid_query (self, pid) :
        """Return entity with persistent id `pid`."""
        return self.ems.pid_query (pid, self._etype)
    # end def pid_query

    def query_s (self, * filters, ** kw) :
        """Return `self.query (* filters, ** kw)`
           sorted by `kw.get ("sort_key", Type.sort_key)`.
        """
        ### Need to use `Q_Result_Composite` because `Type.sort_key` doesn't
        ### work with some backends (SQL, I am looking at you)
        Type     = self._etype
        sort_key = kw.pop ("sort_key", Type.sort_key)
        result   = self.query (* filters, ** kw)
        result   = self.ems.Q_Result_Composite ([result], sort_key)
        return result
    # end def query_s

    def query_1 (self, * filters, ** kw) :
        """Return the number of matches and the one single entity, if any,
           for the conditions in `filters` and `kw`.
        """
        q = self.query (* filters, ** kw).limit (2)
        c = q.count ()
        return c, q.first () if c == 1 else None
    # end def query_1

    def _epkified (self, * epk, ** kw) :
        this  = self
        etype = self._etype
        if epk and isinstance (epk [-1], etype.Type_Name_Type) :
            this  = self.home_scope [epk [-1]]
            epk   = epk [:-1]
            etype = this._etype
        ### Don't pass `on_error` through here to avoid `Link.__call__`
        ### ending up with doubled error messages in case of
        ### `MOM.Error.Required_Missing`
        kw = pkw = dict (kw)
        kw.pop ("on_error", None)
        if etype.args_as_kw and kw.get ("raw", False) :
            pkw = etype._kw_polished \
                ( etype.epk_as_kw (* epk, ** kw)
                , on_error = lambda * args, ** kw : False
                )
            epk = ()
        return etype.epkified (* epk, ** pkw), this
    # end def _epkified

# end class Id_Entity

class MD_Entity (Entity) :
    """Scope-specific manager for a specific type of meta-data entities."""


# end class MD_Entity

class Object (Id_Entity) :
    """Scope-specific manager for essential object-types."""

    def ac_query_auto_split (self, text) :
        result     = []
        et         = self._etype
        AQ         = et.AQ
        epk_aqc    = [getattr (AQ, en).AC for en in et.epk_sig]
        for epks in et.epk_splitter (text) :
            single_value_queries = []
            for v in epks :
                acqs = [acq (v) for acq in epk_aqc]
                single_value_queries.append (TFL.Filter_Or (* acqs))
            result.append (self.query (* single_value_queries))
        return result
    # end def ac_query_auto_split

    @property
    @getattr_safe
    def singleton (self) :
        Type = self._etype
        if Type.max_count == 1 :
            try :
                return first (self.query ().limit (2))
            except IndexError :
                pass
    # end def singleton

    def _cooked_epk_iter (self, epk) :
        for (pka, v) in zip (self._etype.primary, epk) :
            if v is not None :
                try :
                    yield pka.cooked (v)
                except MOM.Error.No_Such_Entity :
                    yield None
            else :
                yield None
    # end def _cooked_epk_iter

    def _raw_epk_iter (self, epk) :
        for (pka, v) in zip (self._etype.primary, epk) :
            if v is not None :
                try :
                    yield pka.from_string (v)
                except MOM.Error.No_Such_Entity :
                    yield None
            else :
                yield None
    # end def _raw_epk_iter

# end class Object

class Link (Id_Entity) :
    """Scope-specific manager for essential link-types."""

    def __call__ (self, * args, ** kw) :
        try :
            (args, kw), this = self._epkified (* args, ** kw)
            self._checked_roles (* args, ** kw)
            if not kw.get ("raw", False) :
                args = tuple \
                    (self._role_to_cooked_iter (args, auto_create = True))
        except MOM.Error.Required_Missing :
            ### let MOM.Entity handle this case
            pass
        else :
            E_Type = self.E_Type
            if E_Type.is_partial :
                ### try to find non-partial child fitting e-types of `roles`
                roles = args [:E_Type.number_of_roles]
                scope = self.home_scope
                BT    = scope.MOM.Id_Entity.E_Type
                if all (isinstance (r, BT) for r in roles) :
                    CT = E_Type.child_np (roles)
                    if CT is not None :
                        return scope [CT.type_name] (* args, ** kw)
        return self.__super.__call__ (* args, ** kw)
    # end def __call__

    def applicable_objects (self, objects) :
        """Returns all `objects` not refusing to be linked by `self._etype`."""
        type_name = self._etype.Essence.type_name
        return [o for o in objects if type_name not in o.refuse_links]
    # end def applicable_objects

    def r_query (self, * filters, ** kw) :
        """Return all links matching the conditions in `filters` and `kw`.

           `r_query` behaves similar to `query` but provides the additional
           features:

           - if `kw` contains role names or other id-entity-attributes,

             * the name can be a generic or a specific role name (`query`
               only allows generic role names)

             * the values passed can be `epk` in cooked or raw form (for
               `query`, objects must be passed)

             * the returned links are restricted to those linking the
               specified objects
        """
        Type = self._etype
        map  = getattr (Type, "role_map", None)
        rkw  = {}
        if map :
            for k in list (kw) :
                aie = None
                if k in map :
                    aie = Type.Roles [map [k]]
                elif k in Type.attributes :
                    a = Type.attributes [k]
                    if isinstance (a.attr, MOM.Attr.A_Id_Entity) :
                        aie = a.attr
                if aie is not None :
                    try :
                        obj = self._cooked_role (aie, kw.pop (k))
                        if not isinstance (obj, aie.P_Type) :
                            return []
                        rkw [aie.name] = obj
                    except MOM.Error.No_Such_Entity :
                        return TFL.Q_Result (())
        if rkw :
            kw = dict (kw, ** rkw)
        result = self.query (* filters, ** kw)
        return result
    # end def r_query

    def r_query_s (self, * filters, ** kw) :
        """Return `self.r_query (* filters, ** kw)`
           sorted by `kw.get ("sort_key", Type.sort_key)`.
        """
        ### Need to use `Q_Result_Composite` because `Type.sort_key` doesn't
        ### work with some backends (SQL, I am looking at you)
        sort_key = kw.pop ("sort_key", self._etype.sort_key)
        result   = self.r_query (* filters, ** kw)
        result   = self.ems.Q_Result_Composite ([result], sort_key)
        return result
    # end def r_query_s

    def links_of (self, obj, * filters, ** kw) :
        """Return all links to `obj` (considers `obj` for each of the roles)."""
        queries  = []
        r_query  = self.ems.r_query
        sort_key = kw.pop ("sort_key", False)
        strict   = kw.pop ("strict",   False)
        Type     = self._etype
        for r in Type.Roles :
            if isinstance (obj, r.role_type) :
                pk = self._cooked_role (r, obj)
                queries.append \
                    (r_query (r.assoc, {r.name : pk}, strict = strict))
        result = self.ems.Q_Result_Composite (queries)
        if sort_key is not None :
            result = result.order_by (Type.sort_key_pm (sort_key))
        return result
    # end def links_of

    def _checked_roles (self, * epk, ** kw) :
        if kw.get ("raw", False) :
            epk = tuple (self._raw_epk_iter (epk))
        else :
            epk = tuple (self._role_to_cooked_iter (epk))
        etype = self._etype
        errors  = []
        r_query = self.ems.r_query
        for r, pk in zip (etype.Roles, epk) :
            if r.max_links >= 0 :
                links = r_query (r.assoc, {r.name : pk}, strict = True)
                nol   = links.count ()
                if nol >= r.max_links :
                    errors.append \
                        (MOM.Error.Multiplicity (etype, r, pk, epk, * links))
        if errors :
            exc = errors [0] if len (errors) == 1 else \
                MOM.Error.Multiplicity_Errors (_T (etype.ui_name), errors)
            raise exc
    # end def _checked_roles

    def _cooked_role (self, r, v) :
        result = v
        if v is not None and not isinstance (result, MOM.Entity) :
            if not isinstance (v, (dict, tuple, list, int)) :
                if not (v.startswith ("(") and v.endswith (")")) :
                    v = (v, )
            result = r.from_string (v)
        return result
    # end def _cooked_role

    def _raw_epk_iter (self, epk) :
        for (pka, v) in zip (self._etype.primary, epk) :
            try :
                if getattr (pka, "role_type", None) :
                    ### Allow role attributes to be passed as objects even if
                    ### `raw` is specified
                    v = self._cooked_role (pka, v)
                elif v is not None :
                    v = pka.from_string   (v)
            except MOM.Error.No_Such_Entity :
                v = None
            yield v
    # end def _raw_epk_iter

    def _role_to_cooked_iter (self, epk, auto_create = False) :
        for (r, (pka, v)) in paired \
                (self._etype.Roles, zip (self._etype.primary, epk)) :
            if r is not None :
                ### Allow role attributes to be passed as raw values even if
                ### `raw` is not specified
                try :
                    v = self._cooked_role (r, v)
                except MOM.Error.No_Such_Entity :
                    if auto_create :
                        scope = self.home_scope
                        et    = scope [r.role_type.type_name]
                        if et.is_partial and et.default_child :
                            et = et.default_child
                        v = et (* v, implicit = True, raw = True)
                    else :
                        v = None
            elif v is not None :
                try :
                    v = pka.cooked (v)
                except MOM.Error.No_Such_Entity :
                    v = None
            yield v
    # end def _role_to_cooked_iter

    _cooked_epk_iter = _role_to_cooked_iter

# end class Link

class Link1 (Link) :
    """Scope-specific manager for essential unary link-types."""

# end class Link1

class Link2 (Link) :
    """Scope-specific manager for essential binary link-types."""

    ### XXX dfc_synthesizer

# end class Link2

class Link3 (Link) :
    """Scope-specific manager for essential ternary link-types."""

# end class Link3

__doc__ = """
`MOM.E_Type_Manager` provides classes implementing scope-specific managers
for essential object and link types.

For each essential object and link type, a scope provides a
`E_Type_Manager` that is accessible under the `type_name` of the essential
type in question.

For instance, the `E_Type_Manager` for an essential
object type `BMT.Mouse` of a scope `s` can be accessed as::

  s.BMT.Mouse

and provides methods to create and query instances of `BMT.Mouse`. A new
mouse named `mickey` is created by::

  s.BMT.Mouse ("mickey")

The transitive extension of mice, i.e., the extension of `BMT.Mouse` and
all classes derived from it, is computed by the query::

  s.BMT.Mouse.query ()


"""

if __name__ != "__main__" :
    MOM._Export_Module ()
### __END__ MOM.E_Type_Manager
