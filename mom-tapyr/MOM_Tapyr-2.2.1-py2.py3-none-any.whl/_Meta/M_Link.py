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
#    MOM.Meta.M_Link
#
# Purpose
#    Meta class of link-types of MOM meta object model
#
# Revision Dates
#    23-Sep-2009 (CT) Creation (factored from `TOM.Meta.M_Link`)
#    27-Oct-2009 (CT) s/Scope_Proxy/E_Type_Manager/
#     4-Nov-2009 (CT) s/E_Type_Manager_L/E_Type_Manager.Link/
#     4-Nov-2009 (CT) `M_Link2` and `M_E_Type_Link2` added
#    18-Nov-2009 (CT) Major surgery (removed generic e-types [i.e., those for
#                     non-derived app_types])
#    19-Nov-2009 (CT) `cls.sorted_by` fixed for default case (3-compatibility)
#    19-Nov-2009 (CT) `_m_setup_roles` changed to set `role.attr.Class` to
#                     `role_type` (needed by MOM.Attr._A_Object_._to_cooked)
#    20-Nov-2009 (CT) `M_Link3`, `M_Link2_Ordered`, `M_E_Type_Link3`, and
#                     `M_E_Type_Link2_Ordered` added
#    24-Nov-2009 (CT) `_m_setup_roles` changed to add to `rt._own_link_map`
#    26-Nov-2009 (CT) `_m_setup_etype_auto_props` changed to handle
#                     `auto_cache`
#    26-Nov-2009 (CT) `other_role_name` added
#    27-Nov-2009 (CT) `_m_setup_etype_auto_props` adapted to change of
#                     `Role_Cacher`
#    27-Nov-2009 (CT) `destroy_dependency` added
#     3-Dec-2009 (CT) `sorted_by` hack removed from `_m_setup_roles`
#     3-Dec-2009 (CT) `M_Link3` and `M_Link2_Ordered` derived from `M_Link`
#                     instead of from `M_Link2`
#    22-Dec-2009 (CT) `M_Link2_Ordered` and `Sequence_Number` removed
#    18-Jan-2010 (CT) `M_Link2._m_setup_etype_auto_props` changed to handle
#                     `auto_cache` for `max_links != 1`, too
#    18-Feb-2010 (CT) `M_Link1` and `M_E_Type_Link1` added (`M_Link_n` factored)
#    19-Feb-2010 (CT) `M_Link_n._m_setup_auto_cache_role` changed to not
#                     create `A_Cached_Role` (done by `Role_Cacher`, now)
#     4-Mar-2010 (CT) `_m_setup_roles` changed to fix the `Class` of
#                     cached-role attributes
#    23-Mar-2010 (CT) `_m_setup_etype_auto_props` changed to set
#                     `role_type.is_relevant` only for non-partial link-types
#    11-May-2010 (CT) `_m_setup_etype_auto_props` changed to set
#                     `auto_cache_roles` depending on `_names`, not
#                     `_own_names` (otherwise, role cachers for inherited
#                     roles get lost)
#    22-Sep-2011 (CT) s/Class/P_Type/ for _A_Id_Entity_ attributes
#     7-Nov-2011 (CT) Redefine `_m_new_e_type_dict` to add `other_role_name`
#    19-Jan-2012 (CT) Remove `raise MOM.Error.No_Scope` from `M_E_Type.__call__`
#    23-Mar-2012 (CT) Change `_m_setup_etype_auto_props` to setup `auto_cache`
#                     properly even if `cls.type_name != rc.link_type_name`
#                     (i.e., for descendent classes)
#    24-Mar-2012 (CT) Change `_m_setup_etype_auto_props` to not overwrite
#                     `auto_cache` (don't rewrite ancestor's `auto_cache`)
#    18-Jun-2012 (CT) Add `M_E_Type_Link[123]_Reload`
#    23-Jul-2012 (CT) Change `M_Link._m_setup_etype_auto_props` to consider
#                     `a.Cacher_Type`
#     1-Aug-2012 (CT) Add `M_E_Type_Link[123]_Destroyed`
#    31-Aug-2012 (CT) Restrict `_m_setup_roles` to roles in `_own_names`
#    12-Sep-2012 (CT) Add `Partial_Roles`, `_m_create_auto_children`
#    13-Sep-2012 (CT) Factor `m_create_role_child`, add `m_create_role_children`
#    13-Sep-2012 (CT) Call `_m_setup_roles` before `_m_setup_ref_maps`
#    14-Sep-2012 (CT) Add `fix_doc` for `auto_cache_roles` to `_m_setup_roles`
#    18-Sep-2012 (CT) Change `m_create_role_child` to obey `refuse_links`
#    19-Sep-2012 (CT) Add guard against role_name clashes to `_m_setup_roles`
#    20-Sep-2012 (CT) Change `m_create_role_child` to set `is_partial`
#    20-Sep-2012 (CT) Redefine `_m_init_prop_specs` to set `Role_Attrs`
#    20-Sep-2012 (CT) Rename `M_Link._m_setup_etype_auto_props` to
#                     `_m_setup_roles`, use `Role_Attrs` instead of
#                     home-grown code
#    21-Sep-2012 (CT) Add `child_np`, `child_np_map`
#    27-Feb-2013 (CT) Simplify signature of `_m_setup_ref_maps` and
#                     `_m_setup_roles`
#    16-Apr-2013 (CT) Add and use `auto_derive_np_kw`
#    16-Apr-2013 (CT) Make `m_create_role_children` lazy
#    16-Apr-2013 (CT) Rename `m_create_role_child` to `_m_create_role_child`
#     8-May-2013 (CT) Add `_m_create_link_ref_attr`, call from `_m_setup_roles`
#    10-May-2013 (CT) Factor `plural_of`
#    10-May-2013 (CT) Add `link_ref_singular`
#    11-May-2013 (CT) Factor `_m_create_rev_ref_attr` to `M_Id_Entity`
#    12-May-2013 (CT) Add `_m_create_role_ref_attr`, call from `_m_setup_roles`
#    12-May-2013 (CT) Remove setup of `auto_cache_roles` from `_m_setup_roles`
#    12-May-2013 (CT) Add `rev_type` to calls of `_m_create_rev_ref_attr`
#    15-May-2013 (CT) Rename `auto_cache` to `auto_rev_ref`
#     3-Jun-2013 (CT) Add `role_name` to aliases of `attributes` dictionary
#    12-Jun-2013 (CT) Add `None` guard to `_m_init_prop_specs`
#    12-Jun-2013 (CT) Add argument `app_type` to `m_setup_names`
#     1-Mar-2014 (CT) Change `_m_create_link_ref_attr` to set `hidden`
#     2-Mar-2014 (CT) Change `_m_create_link_ref_attr` to set `hidden_nested`
#    16-Apr-2014 (CT) Add role-specific `auto_derive_np_kw` and support for
#                     `_update_auto_kw` to `_m_create_role_child`
#    11-Jul-2014 (CT) Change `child_np` to use `.E_Type`, not `.__class__` to
#                     determine the `etypes` of `roles`
#     7-Apr-2015 (CT) Redefine `_m_default_ui_name` to improve auto-`ui_name`
#    16-Aug-2015 (CT) Add `auto_derived_p`, `auto_derived_root`
#    25-Feb-2016 (CT) Change `_m_setup_roles` to always set `number_of_roles`
#     1-Jun-2016 (CT) Change `_m_create_auto_children` to honor `refuse_e_types`
#                     and `refuse_links`
#    20-Oct-2016 (CT) Change `_m_create_role_child` to set `E_Type_Parent`
#    ««revision-date»»···
#--

from   _MOM                  import MOM
from   _TFL                  import TFL

import _MOM._Meta.M_Entity
import _MOM.E_Type_Manager

from   _TFL.I18N             import _, _T, _Tn
from   _TFL.predicate        import cartesian, filtered_join, paired, plural_of, uniq
from   _TFL.pyk              import pyk
from   _TFL.Regexp           import Regexp, re

import _TFL.multimap
import _TFL.Undef

import itertools

class M_Link (MOM.Meta.M_Id_Entity) :
    """Meta class of link-types of MOM meta object model.

       `MOM.Meta.M_Link` provides the meta machinery for defining
       essential association types and link instances. It is based on
       :class:`~_MOM._Meta.M_Entity.M_Entity`.

       `M_Link` is the common base class for the arity-specific subclasses.

       `M_Link` provides the attribute:

       .. attribute:: Roles

         The tuple of role objects (contains as many role objects as the arity
         of the association specifies).

    """

    auto_derive_np_kw = TFL.mm_dict_mm_dict ()
    _orn              = {}

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        if "_role_children_to_add" not in dct :
            cls._role_children_to_add = []
    # end def __init__

    def m_create_role_children (cls, role) :
        if not isinstance (role, pyk.string_types) :
           role = role.name
        cls._role_children_to_add.append (role)
    # end def m_create_role_children

    def other_role_name (cls, role_name) :
        raise TypeError \
            ( "%s.%s.other_role_name needs to be explicitly defined"
            % (cls.type_name, role_name)
            )
    # end def other_role_name

    def _m_create_auto_children (cls) :
        adrs = tuple \
            ( tuple
                ( (r.name, c)
                for c in sorted
                    ( pyk.itervalues (r.E_Type.children_np)
                    , key = TFL.Getter.i_rank
                    )
                if not
                    (  cls.type_name in c.refuse_links
                    or c.type_name   in r.refuse_e_types
                    )
                )
            for r in cls.Roles
            if  r.auto_derive_np and r.E_Type.children_np
            )
        if adrs :
            for adr in cartesian (* adrs) :
                cls._m_create_role_child (* adr)
    # end def _m_create_auto_children

    def _m_create_link_ref_attr (cls, role, role_type, plural) :
        name      = cls._m_link_ref_attr_name (role, plural)
        Attr_Type = MOM.Attr.A_Link_Ref_List if plural else MOM.Attr.A_Link_Ref
        return cls._m_create_rev_ref_attr \
            ( Attr_Type, name, role, role_type, cls
            , assoc         = cls ### XXX remove after auto_cache_roles are removed
            , description   =
                ( _Tn ( "`%s` link", "`%s` links", 7 if plural else 1)
                % (_T (cls.ui_name), )
                )
            , hidden        =
                cls.rev_ref_attr_hidden or (plural and role.max_links == 1)
            , hidden_nested = 1
            )
    # end def _m_create_link_ref_attr

    def _m_create_role_child (cls, * role_etype_s) :
        """Create derived link classes for the (role, e_type) combinations
           specified.
        """
        rkw     = {}
        rets    = []
        tn      = cls.type_name
        tbn     = cls.type_base_name
        for role_name, etype in role_etype_s :
            role  = getattr (cls._Attributes, role_name)
            rET   = role.E_Type
            tbn   = tbn.replace (rET.type_base_name, etype.type_base_name)
            tn    = tn.replace  (rET.type_base_name, etype.type_base_name)
            if tn == cls.type_name :
                raise NameError \
                    ( "Cannot auto-derive from %s for role `%s` from %s to %s"
                    % ( cls.type_name, role_name
                      , rET.type_base_name, etype.type_base_name
                      )
                    )
            if cls.type_name in etype.refuse_links :
                return
            rets.append ((role, etype))
        if any ((cls.type_name in etype.refuse_links) for role, etype in rets):
            return
        elif tn not in cls._type_names :
            if tn in cls.auto_derive_np_kw :
                auto_kw = cls.auto_derive_np_kw [tn]
            else :
                auto_kw = cls.auto_derive_np_kw [tbn]
            auto_kw = auto_kw.__class__ (auto_kw)
            for role, etype in rets :
                for rtn in (etype.type_name, etype.type_base_name) :
                    ra_kw = cls.auto_derive_np_kw [rtn, role.name]
                    auto_kw.update (ra_kw)
            for auto_kw_updater in pyk.itervalues (auto_kw ["_update_auto_kw"]):
                auto_kw_updater (auto_kw)
            for role, etype in rets :
                r_rkw = dict \
                    ( auto_kw [role.name]
                    , auto_rev_ref   = role.auto_rev_ref_np
                    , auto_derive_np = role.auto_derive_npt
                    , E_Type_Parent  = role.E_Type
                    , role_type      = etype
                    , __module__     = cls.__module__
                    )
                rkw [role.name] = role.__class__ (role.name, (role, ), r_rkw)
                ### reset cache
                role._children_np = role._children_np_transitive = None
            is_partial = \
                (  any (r.role_type.is_partial for r in pyk.itervalues (rkw))
                or any
                    (   (not r.role_type) or r.role_type.is_partial
                    for r in cls.Role_Attrs if r.name not in rkw
                    )
                )
            result = cls.__class__ \
                ( tbn
                , (cls, )
                , dict
                    ( auto_kw ["properties"]
                    , _Attributes        = cls._Attributes.__class__
                        ( "_Attributes"
                        , (cls._Attributes, )
                        , dict
                            ( auto_kw ["extra_attributes"]
                            , __module__ = cls.__module__
                            , ** rkw
                            )
                        )
                    , auto_derived_p     = True
                    , auto_derived_root  = cls.auto_derived_root or cls
                    , is_partial         = is_partial
                    , PNS                = cls.PNS
                    , __module__         = cls.__module__
                    )
                )
            ### reset cache
            cls._children_np = cls._children_np_transitive = None
            result._m_setup_etype_auto_props ()
            return result
    # end def _m_create_role_child

    def _m_create_role_children (cls) :
        for role in uniq (cls._role_children_to_add) :
            role = getattr (cls._Attributes, role)
            children = sorted \
                ( pyk.itervalues (role.E_Type.children_np)
                , key = TFL.Getter.i_rank
                )
            for c in children :
                cls._m_create_role_child ((role.name, c))
    # end def _m_create_role_children

    def _m_create_role_ref_attr (cls, name, role, role_type) :
        orn        = cls.other_role_name (role.name)
        other_role = getattr (cls._Attributes, orn)
        plural     = other_role.max_links != 1
        Attr_Type  = MOM.Attr.A_Role_Ref
        if plural :
            if not role.rev_ref_singular :
                name   = plural_of (name)
            Attr_Type  = MOM.Attr.A_Role_Ref_Set
        if other_role.role_type :
            result = cls._m_create_rev_ref_attr \
                ( Attr_Type, name, other_role, other_role.role_type, role_type
                , description     = _T ("`%s` linked to `%s`") %
                    (_T (role_type.ui_name), _T (other_role.role_type.ui_name))
                , other_role_name = role.name
                )
            return result
    # end def _m_create_role_ref_attr

    def _m_init_prop_specs (cls, name, bases, dct) :
        result = cls.__m_super._m_init_prop_specs (name, bases, dct)
        cls._Attributes.m_setup_names (cls)
        def _gen_roles (cls) :
            for a in sorted \
                    ( pyk.itervalues (cls._Attributes._names)
                    , key = TFL.Sorted_By ("rank", "name")
                    ) :
                if a is not None and issubclass (a, MOM.Attr.A_Link_Role) :
                    yield a
        cls.Role_Attrs = tuple (_gen_roles (cls))
        return result
    # end def _m_init_prop_specs

    def _m_link_ref_attr_name (cls, role, plural = True) :
        result = role.link_ref_attr_name or cls.link_ref_attr_name_p (role)
        suffix = role.link_ref_suffix
        if isinstance (suffix, TFL.Undef) :
            suffix = cls.link_ref_attr_name_s
        if suffix is not None :
            result += suffix
            if plural :
                result = plural_of (result)
        elif not plural :
            result += "_1"
        return result
    # end def _m_link_ref_attr_name

    def _m_new_e_type_dict (cls, app_type, etypes, bases, ** kw) :
        result = cls.__m_super._m_new_e_type_dict \
            ( app_type, etypes, bases
            , child_np_map    = {}
            , other_role_name = cls._orn
            , ** kw
            )
        return result
    # end def _m_new_e_type_dict

    def _m_setup_roles (cls) :
        cls.__m_super._m_setup_roles ()
        cls.Partial_Roles = PRs = []
        cls.Roles         = Rs  = []
        cls.acr_map = acr_map = dict (getattr (cls, "acr_map", {}))
        for a in cls.Role_Attrs :
            Rs.append (a)
            if a.role_type :
                if a.role_type.is_partial :
                    PRs.append (a)
            else :
                cls.is_partial = True
        for role in Rs :
            r_type = role.role_type
            if r_type and not isinstance (role.link_ref_attr_name, TFL.Undef) :
                if role.link_ref_singular :
                    if role.max_links != 1 :
                        raise TypeError \
                            ( "%s.%s: inconsistent `max_links` %s "
                              "for link_ref_singular"
                            % (cls, role.name, role.max_links)
                            )
                else :
                    cls._m_create_link_ref_attr (role, r_type, plural = True)
                if role.max_links == 1 :
                    cls._m_create_link_ref_attr (role, r_type, plural = False)
                rran = role.rev_ref_attr_name or role.auto_rev_ref
                if rran and len (cls.Role_Attrs) == 2 :
                    if rran == True :
                        rran = role.role_name
                    cls._m_create_role_ref_attr (rran, role, r_type)
        cls.auto_cache_roles = ()
    # end def _m_setup_roles

# end class M_Link

class M_Link1 (M_Link) :
    """Meta class of unary link-types of MOM meta object model.

       `MOM.Meta.M_Link1` provides the meta machinery for
       :class:`unary links<_MOM.Link.Link1>`.
    """

    link_ref_attr_name_s = ""
    rev_ref_attr_hidden  = False

    def link_ref_attr_name_p (cls, role) :
        return cls.type_base_name.lower ()
    # end def link_ref_attr_name_p

    def other_role_name (cls, role_name) :
        raise TypeError \
            ( "%s: There is no other role than %s"
            % (cls.type_name, role_name)
            )
    # end def other_role_name

# end class M_Link1

class M_Link_n (M_Link) :
    """Meta class of link-types with more than 1 role."""

    link_ref_attr_name_s = "_link"
    rev_ref_attr_hidden  = True

    def link_ref_attr_name_p (cls, role) :
        return "__".join \
            (r.role_name for r in cls.Roles if r.name != role.name)
    # end def link_ref_attr_name_p

# end class M_Link_n

class M_Link2 (M_Link_n) :
    """Meta class of binary entity-based link-types of MOM meta object model.

       `MOM.Meta.M_Link2` provides the meta machinery for
       :class:`binary links<_MOM.Link.Link2>`.
    """

    _orn = dict (left = "right", right = "left")

    def other_role_name (cls, role_name) :
        return cls._orn [role_name]
    # end def other_role_name

# end class M_Link2

class M_Link3 (M_Link_n) :
    """Meta class of ternary link-types of MOM meta object model.

       `MOM.Meta.M_Link3` provides the meta machinery for
       :class:`ternary links<_MOM.Link.Link3>`.
    """

# end class M_Link3

@TFL.Add_To_Class ("M_E_Type", M_Link)
class M_E_Type_Link (MOM.Meta.M_E_Type_Id) :
    """Meta class for essence of MOM.Link."""

    Manager = MOM.E_Type_Manager.Link

    ### `Alias_Property` makes `destroy_dependency` usable as class and as
    ### instance method
    ### - called as class method it refers to `destroy_links`
    ### - called as instance method it refers to `destroy_dependency` defined
    ###   in `Link` (or one of its ancestors)
    destroy_dependency = TFL.Meta.Alias_Property ("destroy_links")

    def child_np (cls, roles) :
        """Return non-partial descendent for e-types of `roles`, if any."""
        ### `roles` can contain `_Reload` instances --> need to use
        ### `.E_Type`, because `.__class__` would be wrong
        etypes = tuple (r.E_Type     for r  in roles)
        etns   = tuple (et.type_name for et in etypes)
        try :
            result = cls.child_np_map [etns]
        except KeyError :
            for cnp in pyk.itervalues (cls.children_np) :
                if etypes == tuple (r.role_type for r in cnp.Roles) :
                    result = cls.child_np_map [etns] = cnp
                    break
            else :
                ### cache non-existence, too
                result = cls.child_np_map [etns] = None
        return result
    # end def child_np

    def destroy_links (cls, obj) :
        """Destroy all links where `obj` participates."""
        scope = obj.home_scope
        etm   = getattr (scope, cls.type_name)
        for l in etm.links_of (obj) :
            scope.remove (l)
    # end def destroy_links

    def _m_default_ui_name (cls, base_name) :
        result = base_name
        Roles  = getattr (cls, "Roles", [])
        if Roles and all (R.E_Type for R in Roles) :
            rn_pat = Regexp \
                ( "^"
                + "_(.+)_".join (R.E_Type.type_base_name for R in Roles)
                + "$"
                )
            if rn_pat.match (base_name) :
                cs     = rn_pat.groups ()
                ns     = tuple (R.E_Type.ui_name for R in Roles)
                result = filtered_join \
                    (" ", itertools.chain (* paired (ns, cs)))
        return result
    # end def _m_default_ui_name

    def _m_fix_doc (cls) :
        cls.set_ui_name          (cls.__name__)
        cls.__m_super._m_fix_doc ()
    # end def _m_fix_doc

    def _m_setup_ref_maps (cls) :
        cls._m_setup_roles              ()
        cls.__m_super._m_setup_ref_maps ()
    # end def _m_setup_ref_maps

    def _m_setup_roles (cls) :
        cls.Roles  = Roles  = tuple \
            (p for p in cls.primary if isinstance (p, MOM.Attr.Link_Role))
        role_types = tuple \
            (r.role_type for r in Roles if r.role_type is not None)
        rns = set ()
        cls.number_of_roles = len (Roles)
        if len (role_types) == len (Roles) :
            type_base_names = [rt.type_base_name for rt in role_types]
            cls.role_map    = role_map = {}
            for i, r in enumerate (Roles) :
                if r.role_name in rns :
                    crs = tuple (s for s in Roles if s.role_name == r.role_name)
                    raise TypeError \
                        ( "%s: role name `%s` cannot be used for %s roles %s"
                        % ( cls.type_name, r.role_name, len (crs)
                          , ", ".join
                              ("`%s`" % r.generic_role_name for r in crs)
                          )
                        )
                rns.add (r.role_name)
                if r.attr.name in cls._Attributes._own_names :
                    ### Replace by app-type specific e-type
                    r.attr.assoc     = r.assoc       = cls
                    r.attr.role_type = r.attr.P_Type = rt = \
                        cls.app_type.entity_type (r.role_type)
                    r.attr.typ       = rt.type_base_name
                    ac      = cls.acr_map.get (r.attr.name)
                    cr_attr = ac and ac.cr_attr
                    if cr_attr and cr_attr.P_Type :
                        cr_attr.P_Type = cls.app_type.entity_type \
                            (cr_attr.P_Type)
                if r.role_name != r.generic_role_name :
                    setattr \
                        ( cls, r.role_name
                        , TFL.Meta.Alias_Property (r.generic_role_name)
                        )
                    cls.attributes.add_alias (r.role_name, r.generic_role_name)
                r.role_index = i
                for key in set \
                        (( r.default_role_name, r.generic_role_name
                         , r.role_name, r.role_type.type_name
                         , r.role_type.type_base_name
                        )) :
                    role_map [key] = r.role_index
    # end def _m_setup_roles

# end class M_E_Type_Link

@TFL.Add_To_Class ("M_E_Type", M_Link1)
class M_E_Type_Link1 (M_E_Type_Link) :
    """Meta class for essence of MOM.Link1."""

    Manager = MOM.E_Type_Manager.Link1

# end class M_E_Type_Link1

@TFL.Add_To_Class ("M_E_Type", M_Link2)
class M_E_Type_Link2 (M_E_Type_Link) :
    """Meta class for essence of MOM.Link2."""

    Manager = MOM.E_Type_Manager.Link2

# end class M_E_Type_Link2

@TFL.Add_To_Class ("M_E_Type", M_Link3)
class M_E_Type_Link3 (M_E_Type_Link2) :
    """Meta class for essence of MOM.Link2."""

    Manager = MOM.E_Type_Manager.Link3

# end class M_E_Type_Link3

class M_E_Type_Link1_Destroyed (MOM.Meta.M_E_Type_Id_Destroyed, M_E_Type_Link1) :
    """Meta class for `_Destroyed` classes of descendents of MOM.Link1."""

# end class M_E_Type_Link1_Destroyed

class M_E_Type_Link2_Destroyed (MOM.Meta.M_E_Type_Id_Destroyed, M_E_Type_Link2) :
    """Meta class for `_Destroyed` classes of descendents of MOM.Link2."""

# end class M_E_Type_Link2_Destroyed

class M_E_Type_Link3_Destroyed (MOM.Meta.M_E_Type_Id_Destroyed, M_E_Type_Link3) :
    """Meta class for `_Destroyed` classes of descendents of MOM.Link3."""

# end class M_E_Type_Link3_Destroyed

class M_E_Type_Link1_Reload (MOM.Meta.M_E_Type_Id_Reload, M_E_Type_Link1) :
    """Meta class for `_Reload` classes of descendents of MOM.Link1."""

# end class M_E_Type_Link1_Reload

class M_E_Type_Link2_Reload (MOM.Meta.M_E_Type_Id_Reload, M_E_Type_Link2) :
    """Meta class for `_Reload` classes of descendents of MOM.Link2."""

# end class M_E_Type_Link2_Reload

class M_E_Type_Link3_Reload (MOM.Meta.M_E_Type_Id_Reload, M_E_Type_Link3) :
    """Meta class for `_Reload` classes of descendents of MOM.Link3."""

# end class M_E_Type_Link3_Reload

### «text» ### start of documentation
__doc__ = """


"""

if __name__ != "__main__" :
    MOM.Meta._Export ("*")
### __END__ MOM.Meta.M_Link
