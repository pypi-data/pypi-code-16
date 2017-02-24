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
#    MOM.Meta.M_Entity
#
# Purpose
#    Meta class for essential entity
#
# Revision Dates
#    23-Sep-2009 (CT) Creation started (factored from `MOM.Meta.M_Entity`)
#    22-Oct-2009 (CT) Creation finished
#    27-Oct-2009 (CT) s/Scope_Proxy/E_Type_Manager/
#    28-Oct-2009 (CT) I18N
#    18-Nov-2009 (CT) Major surgery (removed generic e-types [i.e., those for
#                     non-derived app_types])
#    19-Nov-2009 (CT) `M_E_Type.sort_key` added
#    19-Nov-2009 (CT) `app_type.DBW.etype_decorator` called
#    23-Nov-2009 (CT) `Manager` for `M_Id_Entity.M_E_Type` corrected
#    24-Nov-2009 (CT) `_m_auto__init__` changed to set `i_bases` of `__init__`
#    25-Nov-2009 (CT) `_m_setup_attributes` changed to use `P._attr_map`
#                     instead of `attr.invariant` (because `attr` can be shared
#                     between superclass and subclasses, but `P` isn't shared)
#    26-Nov-2009 (CT) `M_Id_Entity.__init__` added to disallow redefinition
#                     of `__init__`
#    26-Nov-2009 (CT) `_m_auto__init__` changed to chain up directly to
#                     `self._MOM_Entity__init__`
#    26-Nov-2009 (CT) `M_Entity`: `add_attribute` and `add_predicate` added
#    27-Nov-2009 (CT) `_m_setup_prop_names` factored and called from
#                     `m_setup_etypes`, too
#    27-Nov-2009 (CT) `M_E_Type_Id.sort_key` fixed by introducing `__sort_key`
#    28-Nov-2009 (CT) `_m_init_prop_specs` changed to assign `is_partial` to
#                     `False` unless it is contained in `dct`
#    30-Nov-2009 (CT) `_m_create_e_types` changed to call
#                     `app_type.DBW.update_etype` after all etypes were created
#     3-Dec-2009 (CT) `_m_setup_sorted_by` added and called
#    14-Dec-2009 (CT) `g_rank`, `i_rank`, and `m_sorted_by` added
#    16-Dec-2009 (MG) `_m_create_e_types` call `DBW.prepare` before the
#                     e-types will be created
#    22-Dec-2009 (CT) `_m_new_e_type_dict` changed to include `epk_sig`
#    30-Dec-2009 (CT) s/Package_NS/PNS/, `PNS_s` added
#     5-Jan-2010 (CT) Use `TFL._Meta.M_Auto_Combine` as base class
#    14-Jan-2010 (CT) `PNS_s` removed
#    21-Jan-2010 (CT) `M_Id_Entity` changed to auto-generate `epkified_ckd`
#                     and `epkified_raw` instead of `__init__`
#    27-Jan-2010 (MG) Add `app_type` parameter when calling `update_etype`
#     4-Feb-2010 (CT) `M_E_Type_An` added
#     7-Feb-2010 (MG) `M_E_Type_An.__call__` added to support creation of
#                     scopeless `An_Entity's`
#     9-Feb-2010 (CT) `M_E_Type_An._m_setup_attributes` redefined to set
#                     `hash_sig`
#    12-Feb-2010 (CT) `M_Entity._m_init_prop_specs` changed to create a new
#                     `ui_display` attribute for each class (with the proper
#                     `ui_name`)
#    18-Feb-2010 (CT) `M_E_Type_An._m_setup_sorted_by` redefined
#    25-Feb-2010 (CT) `M_E_Type._m_setup_attributes` changed to handle
#                     `check_always`
#     1-Mar-2010 (CT) `M_E_Type.m_recordable_attrs` added
#     1-Mar-2010 (CT) `M_E_Type_An._m_setup_attributes` changed to guard
#                     against `primary`
#     5-Mar-2010 (CT) `_m_setup_attributes` changed to set `.Class` of
#                     `_A_Object_` attributes to app_type specific e-type
#    11-Mar-2010 (CT) `M_Id_Entity` changed t use `epk_def_set_ckd` and
#                     `epk_def_set_raw`
#    11-Mar-2010 (CT) `check_always` removed (was a Bad Idea (tm))
#    12-Mar-2010 (CT) `link_map` moved in here (from `M_Object`)
#    24-Mar-2010 (CT) `_set_type_names` changed to take `ui_name` from
#                     `cls.__dict__` if there
#    27-Mar-2010 (MG) `polymorphic_epk` added
#     8-Apr-2010 (CT) `_m_create_e_types` to percolate `polymorphic_epk` up to
#                     base classes
#     9-Apr-2010 (CT) `M_Id_Entity._m_new_e_type_dict` changed to  filter
#                     attributes set to `None`
#    21-Apr-2010 (CT) `M_Id_Entity._m_new_e_type_dict` changed to use `_d_rank`
#     3-May-2010 (CT) `Type_Name_Type` added and used for `type_name`
#    22-Jun-2010 (CT) `_m_setup_attributes` changed to set `is_mandatory` and
#                     to put `a` instead of `a.attr` into `P._syntax_checks`
#    24-Jun-2010 (CT) `db_sig` added
#     5-Aug-2010 (CT) Property `M_E_Type.Class` added
#     9-Aug-2010 (CT) `M_E_Type_Id._m_setup_sorted_by` changed to handle
#                     `_A_Composite_` attributes properly
#     3-Sep-2010 (CT) `M_E_Type_An._m_setup_attributes` changed to set
#                     `cls.hash_sig` to `.user_attr` instead of `.required`
#     4-Sep-2010 (CT) `M_E_Type.__init__` changed to set `Class` and `C_Type`
#                     to `cls` (property `M_E_Type.Class` removed)
#    13-Oct-2010 (CT) `default_child` added
#    17-Nov-2010 (CT) `_m_setup_sorted_by` changed to honor `sort_rank`
#     8-Feb-2011 (CT) s/Mandatory/Required/
#    10-Feb-2011 (CT) `_nested_classes_to_combine` defined as class attribute
#    10-Feb-2011 (CT) `_m_combine_nested_class` factored to `TFL.Meta.M_Base`
#    24-Feb-2011 (CT) s/A_Object/A_Entity/
#    22-Sep-2011 (CT) s/A_Entity/A_Id_Entity/
#    22-Sep-2011 (CT) s/Class/P_Type/ for _A_Id_Entity_ attributes
#    22-Sep-2011 (CT) s/C_Type/P_Type/ for _A_Composite_ attributes
#     8-Nov-2011 (CT) Add `M_Entity.change_attribute_default`
#    15-Nov-2011 (CT) Add `polymorphic_epks` to `_m_create_e_types`
#    15-Nov-2011 (CT) s/sort_key/sort_key_pm/; s/__sort_key/sort_key/
#    15-Nov-2011 (CT) Remove `epk_sig` from `sort_key_pm`
#                     (`Sorted_by` does the right thing now)
#    15-Nov-2011 (CT) Change default for `sorted_by_epk` from `sort_key_pm`
#                     to `sort_key`
#    18-Nov-2011 (CT) Derive `Type_Name_Type` from `unicode`  instead of `str`
#    18-Nov-2011 (CT) Add `cls.AQ = MOM.Attr.Filter.E_Type (cls)`
#     4-Dec-2011 (CT) Replace `MOM.Attr.Filter` by `MOM.Attr.Querier`
#    20-Dec-2011 (CT) Add `sig_attr`
#    24-Jan-2012 (CT) Change `M_Entity._m_init_prop_specs` to set `show_in_ui`
#    24-Jan-2012 (CT) Change `M_E_Type_Id._m_setup_attributes` to use
#                     `show_in_ui` instead of `generate_doc`
#    31-Jan-2012 (CT) Propagate `polymorphic_epk` directly to
#                     `relevant_root`, let all children inherit that value
#    31-Jan-2012 (CT) Add `epk_sig_root` to `M_E_Type_Id._m_setup_children`
#    29-Mar-2012 (CT) Change `link_map` to exclude partial E_Types
#    14-May-2012 (CT) Remove `children_iter`, use `children.itervalues` instead
#     4-Jun-2012 (CT) Add guard for `et.epk_sig` to `_m_setup_sorted_by`
#     6-Jun-2012 (CT) Use `tn_pid`, not `sort_key`, as default sort-key
#    18-Jun-2012 (CT) Add `M_E_Type_Id_Reload`
#    26-Jun-2012 (CT) Use `app_type.PNS_Aliases_R` in `pns_qualified`
#    29-Jun-2012 (CT) Add `children_np`
#     1-Aug-2012 (CT) Add `M_E_Type_Id_Destroyed`
#     1-Aug-2012 (CT) Use `MOM._Id_Entity_Destroyed_Mixin_`
#     3-Aug-2012 (CT) Add `Ref_Opt_Map` and `Ref_Req_Map`, remove `link_map`
#     4-Aug-2012 (CT) Add `E_Type` to `M_E_Type` instances
#     7-Aug-2012 (CT) Add `parents`
#    11-Aug-2012 (CT) Add `Ref_Map` (union of `Ref_Opt_Map` and `Ref_Req_Map`)
#    11-Aug-2012 (CT) Fix `_calc_ref_map` (`k.type_name`, `if v`)
#    12-Aug-2012 (CT) Add `use_indices`
#     4-Sep-2012 (CT) Add `Roles` and `role_map` to
#                     `M_Id_Entity._m_new_e_type_dict`
#    12-Sep-2012 (CT) Move `children_np` and `_m_setup_children` from
#                     `M_E_Type` to `M_E_Mixin`
#    12-Sep-2012 (CT) Do `_m_setup_auto_props` before `_m_create_base_e_types`
#    12-Sep-2012 (CT) Add `_m_create_auto_children`
#    18-Sep-2012 (CT) Add `_m_fix_refuse_links`
#    20-Sep-2012 (CT) Factor `_m_setup_roles`
#    27-Sep-2012 (CT) Remove references to `Entity.rank`
#    11-Oct-2012 (CT) Use `sig_rank` instead of home-grown code
#    11-Oct-2012 (CT) Add `M_An_Entity._m_new_e_type_dict`, `._m_auto_signified`
#    12-Oct-2012 (CT) Add `raw` and use `undefined` in `_m_auto_signified`
#    11-Dec-2012 (CT) Add `M_E_Type.__instancecheck__`, `.__subclasscheck__`
#    14-Dec-2012 (CT) Set `.relevant_roots` to `{}` for relevant classes
#    17-Dec-2012 (CT) Add `ui_type_name` as alias for `ui_name`
#    31-Jan-2013 (MG) Add call to `DBW.finalize`
#    22-Feb-2013 (CT) Use `TFL.Undef ()` not `object ()`
#    27-Feb-2013 (CT) Add `sort_skip`
#    27-Feb-2013 (CT) Factor `_m_finish_init` from `M_E_Type.__init__`
#    27-Feb-2013 (CT) Call `_m_finish_init` and `e_deco` in separate passes
#                     over `app_type._T_Extension`
#    27-Feb-2013 (CT) Simplify signature of `_m_fix_doc`,
#                     `_m_setup_attributes`, and `_m_setup_ref_maps`
#     6-Mar-2013 (CT) Change semantics of `polymorphic_epk`
#                     add `polymorphic_relevant_epk` with previous semantics
#                     of `polymorphic_epk`
#     8-Mar-2013 (CT) Change `_m_create_e_types` to bubble up `polymorphic_epk`
#    11-Mar-2013 (CT) Use `MOM.Prop.Spec.fix_doc`, not home-grown code
#                     Call `_Predicates.fix_doc`, too
#    21-Mar-2013 (CT) Add `polymorphic_epk = False` to `M_An_Entity`
#    21-Mar-2013 (CT) Use `P_Type_S`, if defined, for `epk_sig_t`
#    22-Mar-2013 (CT) Fix `default_child` in `_m_create_e_types` (PNS_Aliases)
#    15-Apr-2013 (CT) Add `children_np_transitive`
#    16-Apr-2013 (CT) Add `_m_create_role_children` to `_m_setup_auto_props`
#    16-Apr-2013 (CT) Move `__instancecheck__`, `__subclasscheck__` to M_Entity
#    16-Apr-2013 (CT) Add to `refuse_e_types` in `_m_fix_refuse_links`
#    17-Apr-2013 (CT) Use `cls.is_locked` instead of home-grown code
#    17-Apr-2013 (CT) Move `_m_auto_epkified` from M_Id_Entity to M_E_Type_Id
#    18-Apr-2013 (CT) Factor `children_transitive`
#    10-May-2013 (CT) Use `cls.show_in_ui_T` as default for `.show_in_ui`
#    10-May-2013 (CT) Consider `children_np` for `show_in_ui` of `.is_partial`
#    10-May-2013 (CT) Fix `M_Entity.__subclasscheck__` for `Spec Essence`
#    11-May-2013 (CT) Factor `_m_create_rev_ref_attr`
#                     (from `M_Link._m_create_link_ref_attr` to `M_Id_Entity`)
#    11-May-2013 (CT) Redefine `M_Id_Entity._m_setup_roles` to call
#                     `_m_create_rev_ref_attr`
#    12-May-2013 (CT) Add `rev_type` to `_m_create_rev_ref_attr`
#    13-May-2013 (CT) Fix `.__subclasscheck__`, again
#    27-May-2013 (CT) Kludge around Python 2.6's broken type.__subclasscheck__
#     3-Jun-2013 (CT) Use `.attr_prop` to access attribute descriptors
#     3-Jun-2013 (CT) Pass `et_scope` to `fix_doc`
#     4-Jun-2013 (CT) Set `_type_name` to same value as `type_name`
#     7-Jun-2013 (CT) Add property `type_name` to `M_E_Type`, redefine
#                     `M_E_Type._m_finish_init` and `.__set_type_names` to
#                     temporarily remove that property
#     7-Jun-2013 (CT) Add properties `M_E_Type_Id.electric` and `.x_locked`,
#                     redefine `M_E_Type_Id._m_finish_init`  to
#                     temporarily remove these properties
#    12-Jun-2013 (CT) Add argument `app_type` to `_m_setup_prop_names`,
#                     `m_setup_names`
#    13-Jun-2013 (CT) Add `M_E_Mixin.PNS_Aliases`, `.PNS_Aliases_R`, and
#                     `m_add_PNS_Alias`
#    13-Jun-2013 (CT) Add `pns_name`, `pns_name_fq`, `pns_qualified_f`, and
#                     `type_name_fq`
#    13-Jun-2013 (CT) Add and use `M_Id_Entity._m_fix_type_set`
#    24-Jun-2013 (CT) Pass argument `app_type` to `DBW.prepare`
#     8-Jul-2013 (CT) Pass `app_type` to `DBW.finalize`
#     5-Aug-2013 (CT) Fix `polymorphic_epk` and `polymorphic_relevant_epk` in
#                     `M_Id_Entity._m_new_e_type_dict`
#    13-Aug-2013 (CT) Add `M_E_Type.ancestors`
#    21-Aug-2013 (CT) Add `M_E_Type_Md.relevant_roots`
#    22-Aug-2013 (CT) Replace `tn_pid` by `type_name, pid` as default sort-key
#    25-Aug-2013 (CT) Change `M_Entity.__init__` to set `E_Spec`
#     1-Mar-2014 (CT) Redefine `M_E_Type_MD._m_setup_attributes`
#     2-Mar-2014 (CT) Add `ref.only_e_types` to `M_Id_Entity._m_setup_roles`
#    10-Mar-2014 (CT) Set `i_rank`, `g_rank` as first thing in `__init__`
#     2-Apr-2014 (CT) Change `M_Id_Entity._m_setup_roles` to resolve
#                     attributes referring to the type itself
#    18-Jun-2014 (CT) Add `i_rank` to `db_sig`
#     7-Jul-2014 (CT) Fix `_m_fix_type_set`
#    11-Jul-2014 (CT) Add `is_partial`, `is_relevant` to `db_sig`
#     4-Sep-2014 (CT) Add `pka.E_Type.is_relevant` to `_m_setup_sorted_by`
#    25-Sep-2014 (CT) Rename `signified` to `args_as_kw`
#    25-Sep-2014 (CT) Move `_m_auto_args_as_kw` up to `M_E_Mixin`, remove `raw`
#    25-Sep-2014 (CT) Add `args_as_kw` to `M_E_Type_Id`
#    26-Sep-2014 (CT) Add `args_as_kw` for partial types with `epk_sig`, too
#    17-Oct-2014 (CT) Change `db_sig` to
#                     * return a dict, not a tuple
#                     * use a dict, not tuple, of attributes
#    26-Jan-2015 (CT) Use `M_Auto_Update_Combined`, not `M_Auto_Combine_Dict`,
#                     as metaclass
#     7-Apr-2015 (CT) Factor `_m_default_ui_name`
#                     + remove spurious redefinitions of `ui_display`
#    13-Apr-2015 (CT) Add `_json_encode` to `m_setup_etypes`
#     5-May-2015 (CT) Remove obsolete methods `_m_entity_type`, `_m_scope`
#    12-Aug-2015 (CT) Change `_m_init_prop_specs` to reset `__doc_*__`
#    15-Aug-2015 (CT) Improve readability of `M_E_Type._m_setup_attributes`
#    16-Aug-2015 (CT) Add missing import for `...M_Auto_Update_Combined`
#    16-Aug-2015 (CT) Change `_m_init_prop_specs` to reset `immaterial`
#    13-Nov-2015 (CT) Add `M_E_Type.__lt__` to allow sorting of E_Types
#    16-Dec-2015 (CT) Add `UI_Spec` to `_m_create_base_e_types`
#    24-Feb-2016 (CT) Change `_m_add_prop` to allow early calls
#     1-Jun-2016 (CT) Use `Once_Property_NI`, not `Once_Property`
#    22-Jun-2016 (CT) Add `ui_display.add_type` for `MOM.Entity.Essence`
#    22-Jun-2016 (CT) Add `MOM.Attr.Kind.is_void.add_type`
#                     for `MOM.An_Entity.Essence`
#    20-Oct-2016 (CT) Add `M_E_Type.iea_type_restrictions`
#                     and `M_E_Type.iea_type_restriction_map`
#    ««revision-date»»···
#--

from   __future__  import print_function

from   _MOM import MOM
from   _TFL import TFL

import _TFL._Meta.M_Auto_Combine
import _TFL._Meta.M_Auto_Update_Combined
import _TFL._Meta.Once_Property
import _TFL._Meta.Property
import _TFL.Caller
import _TFL.Decorator
import _TFL.Sorted_By
import _TFL.ui_display
import _TFL.Undef

from   _TFL.I18N             import _, _T, _Tn
from   _TFL.object_globals   import class_globals
from   _TFL.Q_Exp            import Q
from   _TFL.predicate        import any_true, first
from   _TFL.pyk              import pyk

import _MOM._Meta
import _MOM.Scope
import _MOM.E_Type_Manager

import sys

class Type_Name_Type (pyk.text_type) :
    """Type used for `type_name`."""

    def __repr__ (self) :
        result = super (Type_Name_Type, self).__repr__ ()
        if result.startswith (("u'", 'u"')) :
            result = result [1:]
        return result
    # end def __repr__

# end class Type_Name_Type

class M_E_Mixin \
        ( TFL.Meta.M_Auto_Update_Combined
        , TFL.Meta.M_Auto_Combine_Nested_Classes
        ) :
    """Meta mixin for M_Entity and M_E_Type."""

    _Class_Kind      = "Bare Essence"

    _S_Extension     = []   ### List of E_Spec
    _BET_map         = {}   ### Dict of bare essential types (type_name -> BET)
    _PNS_Aliases     = {}
    _PNS_Aliases_R   = None

    _args_as_kw_sep  = "\n    "
    _args_as_kw_body = """%(body)s"""
    _args_as_kw_tail = """return kw\n"""

    _type_names      = set ()

    args_as_kw       = None

    m_sorted_by      = TFL.Sorted_By ("i_rank")

    M_Root           = None
    Type_Name_Type   = Type_Name_Type

    ### `ui_type_name` can be used in docstrings of attribute types, where
    ### `ui_name` would refer to the attribute's ui-name, not the E_Type's
    ui_type_name     = TFL.Meta.Alias_Property ("ui_name")

    @property
    def PNS_Aliases (cls) :
        return M_E_Mixin._PNS_Aliases
    # end def PNS_Aliases

    @PNS_Aliases.setter
    def PNS_Aliases (cls, value) :
        M_E_Mixin._PNS_Aliases   = value
        M_E_Mixin._PNS_Aliases_R = None
    # end def PNS_Aliases

    @property
    def PNS_Aliases_R (cls) :
        result = M_E_Mixin._PNS_Aliases_R
        if result is None :
            result = M_E_Mixin._PNS_Aliases_R = dict \
                (  (v._Package_Namespace__qname, k)
                for k, v in pyk.iteritems (M_E_Mixin._PNS_Aliases)
                )
        return result
    # end def PNS_Aliases_R

    @property
    def pns_name (cls) :
        result = getattr (cls, "pns_alias", None)
        if result is None :
            PNS = getattr (cls, "PNS", None)
            if PNS :
                result = PNS._Package_Namespace__qname
        if result in cls.PNS_Aliases_R :
            result = cls.PNS_Aliases_R [result]
        return result
    # end def pns_name

    @property
    def pns_name_fq (cls) :
        PNS = getattr (cls, "PNS", None)
        if PNS :
            return PNS._Package_Namespace__qname
    # end def pns_name_fq

    def __init__ (cls, name, bases, dct) :
        cls._children_np            = None
        cls._children_np_transitive = None
        cls._children_transitive    = None
        cls.__m_super.__init__      (name, bases, dct)
        cls._m_init_name_attributes ()
        cls._m_setup_children       (bases, dct)
    # end def __init__

    def __call__ (cls, * args, ** kw) :
        raise TypeError \
            ( _T ("Can't instantiate %s %r, use <scope>.%s %r instead")
            % (cls.type_name, args, cls.type_name, args)
            )
    # end def __call__

    @property
    def children_np (cls) :
        """Closest non-partial descendents of `cls`."""
        result = cls._children_np
        if result is None :
            def _gen (cls) :
                for k, c in pyk.iteritems (cls.children) :
                    if c.is_partial :
                        for knp, cnp in pyk.iteritems (c.children_np) :
                            yield knp, cnp
                    else :
                        yield k, c
            result = cls._children_np = dict (_gen (cls))
        return result
    # end def children_np

    @property
    def children_np_transitive (cls) :
        """All non-partial descendents of `cls`, including `cls`."""
        result = cls._children_np_transitive
        if result is None :
            result = cls._children_np_transitive = dict \
                (  (tn, c) for tn, c in pyk.iteritems (cls.children_transitive)
                if not c.is_partial
                )
        return result
    # end def children_np_transitive

    @property
    def children_transitive (cls) :
        """All descendents of `cls`, including `cls`."""
        result = cls._children_transitive
        if result is None :
            def _gen (cls) :
                def _gen_children (cls) :
                    yield cls
                    for c in pyk.itervalues (cls.children) :
                        for x in _gen_children (c) :
                            yield x
                for c in _gen_children (cls) :
                    yield c.type_name, c
            result = cls._children_transitive = dict (_gen (cls))
        return result
    # end def children_transitive

    @property
    def default_child (cls) :
        if cls.is_partial :
            return cls._default_child
    # end def default_child

    @default_child.setter
    def default_child (cls, child) :
        if not cls.is_partial :
            raise TypeError \
                ( "Cannot set default_child of non-partial class %s to %s"
                % (cls, child)
                )
        elif cls._default_child is not None :
            raise TypeError \
                ( "Cannot change default_child of class %s from %s to %s"
                % (cls, cls._default_child, child)
                )
        else :
            if isinstance (child, M_E_Mixin) :
                child = child.type_name
            cls._default_child = child
    # end def default_child

    def m_add_PNS_Alias (cls, alias, PNS) :
        M_E_Mixin._PNS_Aliases [alias] = PNS
        M_E_Mixin._PNS_Aliases_R       = None
    # end def m_add_PNS_Alias

    def m_setup_etypes (cls, app_type) :
        """Setup EMS- and DBW -specific essential types for all classes in
           `cls._S_Extension`.
        """
        assert not app_type.etypes
        if not cls._BET_map :
            cls.m_init_etypes ()
            ### Call `_m_setup_prop_names` again to make sure automatically
            ### created properties are included in subclasses, too
            for s in cls._S_Extension :
                s._m_setup_prop_names (app_type)
            for s in cls._S_Extension [:1] :
                TFL.ui_display.add_type (s.Essence, func = s._ui_display)
            for s in cls._S_Extension [1:2] :
                MOM.Attr.Kind.is_void.add_type \
                    (s.Essence, func = MOM.Attr.Kind._is_void_an_entity)
            for s in cls._S_Extension [1:3] :
                TFL.json_dump.default.add_type \
                    (s.Essence, func = s._json_encode)
        cls._m_create_e_types (app_type, cls._S_Extension)
        for t in reversed (app_type._T_Extension) :
            t._m_setup_relevant_roots ()
    # end def m_setup_etypes

    def pns_qualified_f (cls, name) :
        """Returns the `name` qualified with `cls.pns_name_fq`."""
        pn = cls.pns_name_fq
        if pn :
            result = ".".join ((pn, name))
        else :
            result = name
        return pyk.text_type (result)
    # end def pns_qualified_f

    def pns_qualified (cls, name) :
        """Returns the `name` qualified with `cls.pns_name`."""
        pn = cls.pns_name
        if pn :
            result = ".".join ((pn, name))
        else :
            result = name
        return pyk.text_type (result)
    # end def pns_qualified

    def set_default_child (cls, child) :
        cls.default_child = child
        return child
    # end def set_default_child

    def set_ui_name (cls, base_name) :
        """Sets `ui_name` of `cls`"""
        if getattr (cls, "_ui_name_xp", False) :
            ui_name = cls.ui_name
        else :
            ui_name = cls._m_default_ui_name (base_name)
        if not cls.show_package_prefix :
            cls.ui_name = pyk.text_type      (ui_name)
        else :
            cls.ui_name = cls.pns_qualified  (ui_name)
    # end def set_ui_name

    def _m_auto_args_as_kw (cls, sig, attrs) :
        def _gen_args (attrs, dict) :
            fmt = """("%s", %s)"""
            for a in attrs :
                yield fmt % (a.name, a.name)
        args    = ", ".join ("%s = undefined" % a for a in sig)
        form    = cls._args_as_kw_sep.join \
            ((cls._args_as_kw_head, cls._args_as_kw_body, cls._args_as_kw_tail))
        undefined = TFL.Undef ("argument")
        globals = dict (class_globals (cls), undefined = undefined)
        scope   = dict ()
        code    = form % dict \
            ( args   = args
            , body   =
                ( "%s ((k, v) for k, v in [%s] if v is not undefined)"
                % (cls._args_as_kw_dict, ", ".join (_gen_args (attrs, dict)))
                )
            )
        exec (code, globals, scope)
        result             = scope ["args_as_kw"]
        result.sig         = sig
        result.args        = args
        result.source_code = code
        return classmethod (result)
    # end def _m_auto_args_as_kw

    def _m_init_name_attributes (cls) :
        cls._set_type_names (cls.__name__)
    # end def _m_init_name_attributes

    def _m_create_e_types (cls, app_type, SX) :
        etypes   = app_type.etypes
        e_deco   = app_type.DBW.etype_decorator
        e_update = app_type.DBW.update_etype
        app_type.DBW.prepare (app_type)
        for s in SX :
            app_type.add_type (s._m_new_e_type (app_type, etypes))
        for t in reversed (app_type._T_Extension) :
            ### let `polymorphic_epk`, `polymorphic_relevant_epk` bubble up
            ###     `_m_new_e_type_dict` only sets `polymorphic_epk` of
            ###     immediate parent, but grandparents and higher ups also
            ###     need it set
            if t.polymorphic_epk and getattr (t, "epk_bases", ()) :
                for b in t.epk_bases :
                    b.polymorphic_epk = True
                    if b.relevant_root :
                        b.polymorphic_relevant_epk = True
        for t in app_type._T_Extension :
            ### set up attributes and predicates only after all
            ### etypes are registered in app_type
            t._m_finish_init ()
        for t in app_type._T_Extension :
            t.polymorphic_epks = t.polymorphic_epk or any \
                (   (  pka.P_Type.polymorphic_epks
                    or pka.P_Type.polymorphic_epk
                    or not pka.P_Type.relevant_root
                    )
                for pka in t.primary
                if  isinstance (pka.attr, MOM.Attr._A_Id_Entity_) and pka.P_Type
                )
            t._m_fix_refuse_links (app_type)
            t._m_setup_sorted_by  ()
            td = e_deco (t)
            assert td is t
            if t.default_child :
                ### make sure `default_child` is right regarding
                ### `app_type.PNS_Aliases`
                dc = app_type.entity_type (t.default_child)
                t._default_child = dc.type_name if dc else None
        for t in app_type._T_Extension :
            ### `DBW.update_etype` can use features like `children` or
            ### `Ref_Req_Map` that are only available after *all* etypes have
            ### already been created
            e_update (t, app_type)
        ### give the DBW a final chance to make some adjustments after all
        ### etypes have been updated
        app_type.DBW.finalize (app_type)
    # end def _m_create_e_types

    def _m_default_ui_name (cls, base_name) :
        return base_name
    # end def _m_default_ui_name

    def _m_new_e_type (cls, app_type, etypes) :
        M_E_Type = cls.M_E_Type
        bases    = cls._m_new_e_type_bases (app_type, etypes)
        dct      = cls._m_new_e_type_dict  (app_type, etypes, bases)
        name     = dct.pop                 ("__name__")
        result   = M_E_Type                (name, bases, dct)
        return result
    # end def _m_new_e_type

    def _m_new_e_type_bases (cls, app_type, etypes) :
        return tuple (cls._m_new_e_type_bases_iter (app_type, etypes))
    # end def _m_new_e_type_bases

    def _m_new_e_type_bases_iter (cls, app_type, etypes) :
        yield cls.Essence
        for b in cls.__bases__ :
            tn = getattr (b, "type_name", None)
            if tn in etypes :
                b = etypes [tn]
            if b is not cls.Essence :
                yield b
    # end def _m_new_e_type_bases_iter

    def _m_new_e_type_dict (cls, app_type, etypes, bases, ** kw) :
        if "epk_sig" not in kw :
            kw ["epk_sig"] = kw ["epk_sig_t"] = ()
        return dict  \
            ( cls.__dict__
            , app_type      = app_type
            , children      = {}
            , parents       = []
            , use_indices   = set (cls.use_indices)
            , M_E_Type      = cls.M_E_Type
            , __metaclass__ = None ### avoid `Metatype conflict among bases`
            , __name__      = cls.__dict__ ["__real_name"] ### M_Autorename
            , _real_name    = str (cls.type_base_name)     ### M_Autorename
            , _children_np            = None
            , _children_np_transitive = None
            , _children_transitive    = None
            , _dyn_doc                = cls._dyn_doc
            , ** kw
            )
    # end def _m_new_e_type_dict

    def _m_setup_children (cls, bases, dct) :
        M_Root = cls.M_Root
        if M_Root is not None :
            cls.children = {}
            cls.parents  = parents = []
            for b in bases :
                if isinstance (b, M_Root) :
                    b.children [cls.type_name] = cls
                    parents.append (b)
    # end def _m_setup_children

    def _m_setup_prop_names (cls, app_type = None) :
        for P in cls._Attributes, cls._Predicates :
            P.m_setup_names (cls, app_type)
    # end def _m_setup_prop_names

    def _set_type_names (cls, base_name) :
        TNT = cls.Type_Name_Type
        tn  = TNT (cls.pns_qualified (base_name))
        cls.type_base_name = TNT (base_name)
        cls.type_name      = cls._type_name = tn
        cls.type_name_fq   = TNT (cls.pns_qualified_f (base_name))
        cls.set_ui_name      (base_name)
        cls._type_names.add  (tn)
    # end def _set_type_names

    def __repr__ (cls) :
        app_type = getattr (cls, "app_type", None)
        if app_type :
            kind = app_type.name
        else :
            kind = getattr (cls, "_Class_Kind", "unknown")
        return "<class %r [%s]>" % (str (cls.type_name), kind)
    # end def __repr__

# end class M_E_Mixin

class M_Entity (M_E_Mixin) :
    """Meta class for essential entity of MOM meta object model.


       `MOM.Meta.M_Entity` provides the meta machinery for defining the
       characteristics of essential object and link types of the MOM meta object
       model. It is the common base class for
       :class:`MOM.Meta.M_Object<_MOM._Meta.M_Object.M_Object>` and
       :class:`MOM.Meta.M_Link<_MOM._Meta.M_Link.M_Link>`.

       .. attribute:: PNS_Aliases

         Specifies an optional mapping of package namespace aliases to
         the canonical package namespace name. This allows the decoupling
         of the concrete package structure from the abstract view of the
         object model.

         For instance::

             MOM.Entity.PNS_Aliases = dict \\
                 ( PAP             = GTW.OMP.PAP
                 , SRM             = GTW.OMP.SRM
                 , SWP             = GTW.OMP.SWP
                 )

       XXX
    """

    _Class_Kind                = "Spec Essence"

    _dyn_doc                   = None
    _nested_classes_to_combine = ("_Attributes", "_Predicates")

    def __new__ (mcls, name, bases, dct) :
        dct ["_default_child"] = dct.pop ("default_child", None)
        dct ["use_indices"]    = dct.pop ("use_indices",   None) or []
        dct ["_ui_name_xp"]    = bool    (dct.get ("ui_name"))
        doc = dct.get ("__doc__")
        if doc and "%(" in doc :
            dct ["_dyn_doc"] = doc
        result = mcls.__mc_super.__new__ (mcls, name, bases, dct)
        return result
    # end def __new__

    def __init__ (cls, name, bases, dict) :
        cls.E_Spec = cls
        cls.i_rank = len (cls._S_Extension) - 1
        cls.g_rank = 1 + max \
            ([getattr (b, "g_rank", -1) for b in bases] + [-1])
        cls.__m_super.__init__  (name, bases, dict)
        cls._m_init_prop_specs  (name, bases, dict)
        cls._S_Extension.append (cls)
    # end def __init__

    def add_attribute (cls, attr, verbose = True, override = False) :
        """Add `attr` to `cls`"""
        cls._m_add_prop (attr, cls._Attributes, verbose, override)
    # end def add_attribute

    def add_predicate (cls, pred, verbose = True, override = False) :
        """Add `pred` to `cls`"""
        cls._m_add_prop (pred, cls._Predicates, verbose, override)
    # end def add_predicate

    def change_attribute_default \
            (cls, name, raw_default = None, default = None) :
        """Change (raw or cooked) default of attribute with `name`."""
        attr = getattr (cls._Attributes, name)
        if raw_default is not None :
            assert default is None, \
                ( "Can't specify both raw default and %s "
                  "and cooked default %s for %s"
                % (raw_default, default, attr)
                )
            attr.raw_default = raw_default
        else :
            attr.default     = default
            attr.raw_default = attr.as_string (default)
    # end def change_attribute_default

    def m_init_etypes (cls) :
        """Initialize bare essential types for all classes in `cls._S_Extension`."""
        if not cls._BET_map :
            SX = cls._S_Extension
            cls._m_setup_auto_props     (SX)
            cls._m_create_base_e_types  (SX)
    # end def m_setup_etypes

    def _m_add_prop (cls, prop, _Properties, verbose, override = False) :
        name = prop.__name__
        prop_names = getattr (_Properties, "_names", None)
        if prop_names is None :
            ### `_Properties._names` isn't set up yet
            ### --> just add `prop` to `_Properties`
            if (not override) and name in _Properties.__dict__ :
                if __debug__ :
                    if verbose :
                        p = gettatr (_Properties, name)
                        print \
                            ( "Property %s.%s already defined as %s [%s]"
                            % ( cls.type_name, name
                              , getattr (p,    "kind")
                              , getattr (prop, "kind")
                              )
                            )
            else :
                setattr (_Properties, name, prop)
        elif (not override) and name in prop_names :
            if __debug__ :
                if verbose :
                    p = _Properties._names.get (name)
                    print \
                        ( "Property %s.%s already defined as %s [%s]"
                        % ( cls.type_name, name
                          , getattr (p,    "kind")
                          , getattr (prop, "kind")
                          )
                        )
        else :
            _Properties._m_add_prop (cls, name, prop)
    # end def _m_add_prop

    def _m_create_auto_children (cls) :
        pass
    # end def _m_create_auto_children

    def _m_create_base_e_types (cls, SX) :
        BX = cls._BET_map
        for s in SX :
            tbn = s.type_base_name
            bet = M_E_Mixin \
                ( "_BET_%s_" % str (s.type_base_name)
                , tuple (getattr (b, "__BET", b) for b in s.__bases__)
                , dict
                    ( app_type            = None
                    , E_Spec              = s
                    , is_partial          = s.is_partial
                    , PNS                 = s.PNS
                    , show_package_prefix = s.show_package_prefix
                    , UI_Spec             = TFL.Meta.Alias_Property
                        ("E_Spec.UI_Spec")
                    , _real_name          = str (tbn)
                    , __module__          = s.__module__
                    )
                )
            bet.Essence = s.Essence = BX [s.type_name] = bet
            setattr   (bet,                        "__BET", bet)
            setattr   (s,                          "__BET", bet)
            setattr   (s.PNS,                      tbn,     bet)
            setattr   (sys.modules [s.__module__], tbn,     bet)
    # end def _m_create_base_e_types

    def _m_init_prop_specs (cls, name, bases, dct) :
        if "is_partial" not in dct :
            setattr (cls, "is_partial", False)
        if "show_in_ui" not in dct :
            setattr (cls, "show_in_ui", cls.show_in_ui_T)
        for d in ( "__doc_attr_head__", "__doc_attr_tail__"
                 , "__doc_pred_head__", "__doc_pred_tail__"
                 , "immaterial"
                 ) :
            if d not in dct :
                setattr (cls, d, None)
        for psn in cls._nested_classes_to_combine :
            cls._m_combine_nested_class (psn, bases, dct)
    # end def _m_init_prop_specs

    def _m_setup_auto_props (cls, SX) :
        for c in SX :
            c._m_setup_etype_auto_props ()
        for c in SX [::-1] :
            if getattr (c, "_role_children_to_add", None) :
                c._m_create_role_children ()
        for c in SX [::-1] :
            c._m_create_auto_children ()
    # end def _m_setup_auto_props

    def _m_setup_etype_auto_props (cls) :
        cls._m_setup_prop_names ()
        cls._m_setup_roles      ()
    # end def _m_setup_etype_auto_props

    def _m_setup_roles (cls) :
        cls.Roles         = ()
        cls.Partial_Roles = ()
    # end def _m_setup_roles

    def __instancecheck__ (cls, instance) :
        return isinstance (instance, cls.Essence)
    # end def __instancecheck__

    def __subclasscheck__ (cls, subclass) :
        Essence_c  = getattr (cls,      "Essence", cls)
        Essence_s  = getattr (subclass, "Essence", subclass)
        try :
            _super = Essence_c.__m_super
        except AttributeError :
            try :
                return type.__subclasscheck__ (Essence_c, Essence_s)
            except TypeError :
                ### Python 2.6's __subclasscheck__ is broken beyond belief
                if cls is Essence_c :
                    return super (M_Entity, cls).__subclasscheck__ (Essence_s)
                else :
                    return issubclass (Essence_s, Essence_c)
        else :
            return _super.__subclasscheck__ (Essence_s)
    # end def __subclasscheck__

# end class M_Entity

M_Entity.M_Root = M_Entity

class M_An_Entity (M_Entity) :
    """Meta class for MOM.An_Entity"""

    _args_as_kw_dict = "kw = dict"
    _args_as_kw_head = """def args_as_kw (cls, %(args)s) :"""

    def _m_new_e_type_dict (cls, app_type, etypes, bases, ** kw) :
        user_attrs = sorted \
            ( (  a for a in pyk.itervalues (cls._Attributes._names)
              if a is not None and not a.kind.electric
              )
            , key  = TFL.Getter.sig_rank
            )
        usr_sig    = tuple (a.name for a in user_attrs)
        r_kw       = dict \
            ( polymorphic_epk = False
            , args_as_kw      = None
            , usr_sig         = usr_sig
            )
        if usr_sig and not cls.is_partial :
            r_kw ["args_as_kw"] = cls._m_auto_args_as_kw (usr_sig, user_attrs)
        result     = cls.__m_super._m_new_e_type_dict \
            (app_type, etypes, bases, ** r_kw)
        return result
    # end def _m_new_e_type_dict

# end class M_An_Entity

class M_Id_Entity (M_Entity) :
    """Meta class for MOM.Id_Entity"""

    def __init__ (cls, name, bases, dct) :
        assert "__init__" not in dct, \
          "%s: please redefine `_finish__init__`, not __init__" % cls
        cls.__m_super.__init__  (name, bases, dct)
    # end def __init__

    def _m_create_rev_ref_attr \
            (cls, Attr_Type, rev_name, ref, ref_type, rev_type, ** kw) :
        if rev_name in ref_type._Attributes._names :
            r        = getattr (ref_type._Attributes, rev_name)
            own      = rev_name in ref_type._Attributes._own_names
            r_is_ref = issubclass (r, MOM.Attr._A_Rev_Ref_)
            if (  (not r_is_ref)
               or (own and not issubclass (cls, r.Ref_Type))
               ) :
                expl = ""
                if r_is_ref :
                    expl = "for %s.%s " % (r.Ref_Type.type_name, r.ref_name)
                raise TypeError \
                    ( "Name conflict between %s attribute '%s' %s"
                      "and automagic reverse reference for %s.%s"
                    % ( ref_type.type_name, r.name, expl
                      , cls.type_name, ref.name
                      )
                    )
            if own :
                return r
        akw = dict \
            ( P_Type       = rev_type
            , Ref_Type     = cls
            , ref_name     = ref.name
            , __module__   = ref_type.__module__
            , ** kw
            )
        if "description" not in akw :
            akw ["description"] = \
                (_T ( "Set of `%s` instances referring to this entity "
                      "by attribute %s"
                    ) % (_T (cls.ui_name), ref.name)
                )
        result = type (Attr_Type) (rev_name, (Attr_Type, ), akw)
        ref_type.add_attribute (result, override = True)
        return result
    # end def _m_create_rev_ref_attr

    def _m_fix_type_set (cls, type_set) :
        PNS_Aliases_R = cls.PNS_Aliases_R
        for r in tuple (type_set) :
            pn, tn = r.rsplit (".", 1)
            if pn in PNS_Aliases_R :
                type_set.update (".".join ((PNS_Aliases_R [pn], tn)))
    # end def _m_fix_type_set

    def _m_new_e_type_dict (cls, app_type, etypes, bases, ** kw) :
        def _typ (a) :
            return getattr (a, "P_Type_S", a.P_Type)
        pkas = sorted \
            ( (  a for a in pyk.itervalues (cls._Attributes._names)
              if a is not None and a.kind.is_primary
              )
            , key = TFL.Getter.sig_rank
            )
        epk_bases   = tuple \
            (b for b in bases if getattr (b, "epk_sig", None) is not None)
        epk_sig     = tuple (a.name             for a in pkas)
        epk_sig_t   = tuple ((a.name, _typ (a)) for a in pkas)
        is_relevant = cls.is_relevant or (not cls.is_partial)
        pr_epk      = False
        for eb in epk_bases :
            if eb.epk_sig_t != epk_sig_t :
                if eb.is_relevant and eb.epk_sig_t :
                    if epk_sig_t :
                        eb.polymorphic_epk = pr_epk = True
                        eb.polymorphic_relevant_epk = eb.is_relevant
                else :
                    eb.polymorphic_epk = True
        r_kw   = dict \
            ( epk_bases                = epk_bases
            , epk_sig                  = epk_sig
            , epk_sig_t                = epk_sig_t
            , is_relevant              = is_relevant
            , polymorphic_epk          = False
            , polymorphic_relevant_epk = pr_epk and is_relevant
            , Roles                    = ()
            , role_map                 = {}
            , _all_ref_map             = None
            , _all_ref_opt_map         = None
            , _all_ref_req_map         = None
            , _own_ref_opt_map         = TFL.defaultdict (set)
            , _own_ref_req_map         = TFL.defaultdict (set)
            , ** kw
            )
        result = cls.__m_super._m_new_e_type_dict \
            (app_type, etypes, bases, ** r_kw)
        return result
    # end def _m_new_e_type_dict

    def _m_setup_roles (cls) :
        cls._m_fix_type_set (cls.refuse_links)
        cls.__m_super._m_setup_roles ()
        def _gen_refs (cls) :
            for a in list (pyk.itervalues (cls._Attributes._names)) :
                if a is not None and issubclass (a, MOM.Attr.A_Id_Entity) :
                    yield a
        for ref in _gen_refs (cls) :
            for ts in (ref.allow_e_types, ref.only_e_types, ref.refuse_e_types):
                cls._m_fix_type_set (ts)
            rev_name = ref.rev_ref_attr_name
            if rev_name :
                r_type = ref.E_Type
                if r_type :
                    if r_type == cls.type_name :
                        r_type = cls
                    if not isinstance (r_type, pyk.string_types) :
                        cls._m_create_rev_ref_attr \
                            (MOM.Attr.A_Rev_Ref_Set, rev_name, ref, r_type, cls)
    # end def _m_setup_roles

# end class M_Id_Entity

class M_MD_Entity (M_Entity) :
    """Meta class for MOM.MD_Entity"""

    def _m_new_e_type_dict (cls, app_type, etypes, bases, ** kw) :
        result = cls.__m_super._m_new_e_type_dict \
            ( app_type, etypes, bases
            , polymorphic_epk          = False
            , polymorphic_epks         = False
            , polymorphic_relevant_epk = False
            , ** kw
            )
        return result
    # end def _m_new_e_type_dict

# end class M_MD_Entity

@TFL.Add_To_Class ("M_E_Type", M_Entity)
class M_E_Type (M_E_Mixin) :
    """Meta class for for essence of MOM.Entity.

       `MOM.Meta.M_E_Type` provides the meta machinery for defining app-type
       specific essential object and link types (aka, e_types).

       Each instance of `M_E_Type` is a class that is defined using information
       of an essential class, i.e., a descendent of :class:`~_MOM.Entity.Entity`.

       For each instance of `M_E_Type`, it:

       * Setups the attributes and predicates by instantiating
         `Essence._Attributes` and `Essence._Predicates` (and assigning it to
         class variables `_Attributes` and `_Predicates`, respectively, of the
         `etype`).

       * Assigns the class variables `is_editable` and `show_in_ui` according
         the settings of essential and app-type specific settings.

       * Checks that object predicates don't depend on electric attributes.

       * Adds all object predicates to the `invariant` lists of the attributes
         the predicates depend on.

       * Adds `_syntax_checks` entries to `_Predicates` for all non-electric
         attributes with a callable `check_syntax`.

       * Adds the `etype` to the `children` dictionary of all its base classes.

       `M_E_Type` provides the attributes:

       .. attribute:: db_sig

         `db_sig` defines the database signature of the `etype`. The `db_sig`
         comprises the `type_name` and the :attr:`db_sig<MOM.Attr.Type.db_sig>`
         of a attributes stored in the database.

       .. attribute:: default_child

         For partial classes, `default_child` can be set to refer to the
         non-partial descendent class that should be used by default (for
         instance, to create a new object in an object editor).

       `M_E_Type` provides the methods:

       .. method:: add_attribute

         Add an essential attribute  to the etype.

       .. method:: add_predicate

         Add an essential predicate to the etype.

       .. method:: add_to_app_type(app_type)

         Adds the newly created `etype` to the `app_type`.

       .. method:: after_creation(instance)

         Called after the creation of `instance`. Descendent meta classes
         can override `after_creation` to modify certain instances
         automatically when they are created.

    """

    app_type    = None

    _Class_Kind = "Essence"

    @TFL.Meta.Once_Property_NI
    def ancestors (cls) :
        M_Root = cls.M_Root
        return tuple (b for b in cls.__mro__ if isinstance (b, M_Root))
    # end def ancestors

    @TFL.Meta.Once_Property_NI
    def db_sig (cls) :
        return dict \
            ( i_rank        = cls.i_rank
            , is_partial    = cls.is_partial
            , is_relevant   = cls.is_relevant
            , db_attributes = dict ((a.name, a.db_sig) for a in cls.db_attr)
            )
    # end def db_sig

    @TFL.Meta.Once_Property_NI
    def iea_type_restriction_map (cls) :
        """Type-restrictions for attributes referring to `Id_Entity` instances.
        """
        result = {}
        for ak in cls.id_entity_attr :
            at = ak.attr
            if at.E_Type_Parent is not None :
                result [at.name] = at.E_Type.type_name
        return result
    # end def iea_type_restriction_map

    @TFL.Meta.Once_Property_NI
    def iea_type_restrictions (cls) :
        """Type-restrictions for attributes referring to `Id_Entity` instances.
        """
        from _MOM._Attr.Filter import Q
        return tuple \
            (   getattr (Q, k) [v]
            for k, v in sorted (pyk.iteritems (cls.iea_type_restriction_map))
            )
    # end def iea_type_restrictions

    @TFL.Meta.Once_Property_NI
    def m_recordable_attrs (cls) :
        """Set of attributes that need recording by change management and DBW"""
        return set \
            (a for a in pyk.itervalues (cls.attributes) if a.record_changes)
    # end def m_recordable_attrs

    @property
    def type_name (cls) :
        """Qualified name of essential class."""
        ### Define `type_name` as property to make changes of the class
        ### attribute impossible
        return cls._type_name
    # end def type_name

    def __init__ (cls, name, bases, dct) :
        if issubclass (cls, MOM._Id_Entity_Destroyed_Mixin_) :
            type.__init__ (cls, name, bases, dct)
        else :
            cls.E_Type = cls.P_Type = cls
            cls.__m_super.__init__  (name, bases, dct)
    # end def __init__

    def __call__ (cls, * args, ** kw) :
        return cls._m_call (* args, ** kw)
    # end def __call__

    def add_attribute (cls, attr, verbose = True, parent = None, transitive = True, override = False) :
        """Add `attr` to `cls`"""
        result = cls._m_add_prop \
            (attr, cls._Attributes, verbose, parent, override)
        if result is not None :
            if result.check :
                cls._Predicates._setup_attr_checker (cls, result)
            if transitive :
                for c in pyk.itervalues (cls.children) :
                    c.add_attribute \
                        ( attr
                        , verbose   = False
                        , parent    = parent or cls
                        , override = override
                        )
        return result
    # end def add_attribute

    def add_predicate (cls, pred, verbose = True, parent = None, transitive = True, override = False) :
        """Add `pred` to `cls`"""
        result = cls._m_add_prop \
            (pred, cls._Predicates, verbose, parent, override)
        if transitive and result is not None :
            for c in pyk.itervalues (cls.children) :
                c.add_predicate \
                    ( pred
                    , verbose   = False
                    , parent    = parent or cls
                    , override = override
                    )
        return result
    # end def add_predicate

    def after_creation (cls, instance) :
        """Called after the creation of `instance`. Descendent meta classes
           can override `after_creation` to modify certain instances
           automatically when they are created.
        """
        pass
    # end def after_creation

    def _m_add_prop (cls, prop, _Properties, verbose, parent = None, override = False) :
        name = prop.__name__
        if (not override) and name in _Properties._prop_dict :
            if __debug__ :
                if verbose :
                    p = _Properties._prop_dict.get (name)
                    print \
                        ( "Property %s.%s already defined for %s as %s [%s]"
                        % ( cls.type_name, name, cls.app_type.name
                          , getattr (p,    "kind")
                          , getattr (prop, "kind")
                          )
                        )
        else :
            result = _Properties._add_prop (cls, name, prop)
            if result is not None and name not in _Properties._names :
                ### needed for descendents of `cls.Essence` yet to be imported
                _Properties._names [name] = prop
            return result
    # end def _m_add_prop

    def _m_call (cls, * args, ** kw) :
        result = cls.__new__ (cls, * args, ** kw)
        result.__init__      (* args, ** kw)
        cls.after_creation   (result)
        return result
    # end def _m_call

    def _m_finish_init (cls) :
        with TFL.Context.attr_let (M_E_Type, type_name = cls._type_name) :
            ### temporarily disable metaclass property `type_name` to allow
            ### assignment of attribute descriptor to `cls`
            cls._m_setup_attributes ()
        cls._m_fix_doc          ()
    # end def _m_finish_init

    def _m_fix_doc (cls) :
        doc      = cls._dyn_doc
        et_scope = TFL.Caller.Object_Scope (cls, locls = cls.attributes)
        if doc :
            cls.__doc__ = doc % et_scope
        for S in (cls._Attributes, cls._Predicates) :
            S.fix_doc (et_scope)
    # end def _m_fix_doc

    def _m_fix_refuse_links (cls, app_type) :
        pass
    # end def _m_fix_refuse_links

    def _m_setup_attributes (cls) :
        cls.AQ          = MOM.Attr.Querier.E_Type (cls)
        cls._Attributes = A = cls._Attributes (cls)
        cls._Predicates = P = cls._Predicates (cls)
        attr_dict       = A._attr_dict
        app_type        = cls.app_type
        for pk in sorted (P._pred_kind.get ("object", []), key = Q.rank) :
            pn = pk.name
            n_attrs = len (pk.attrs)
            for an in pk.attrs :
                if an in attr_dict :
                    ak = attr_dict [an]
                    if ak :
                        at = ak.attr
                        if ak.electric :
                            if not isinstance (ak, MOM.Attr.Once_Cached) :
                                print \
                                    ( "%s: %s attribute `%s` of `%s` cannot "
                                      "be referred to by object "
                                      "invariant `%s`"
                                    % (cls, ak.kind, an, cls.type_name, pn)
                                    )
                        else :
                            P._attr_map [at].append (pn)
                            if ak.is_required :
                                pk.pred.is_required = True
        P._syntax_checks = \
            [  a for a in pyk.itervalues (attr_dict)
            if (not a.electric) and TFL.callable (a.attr.check_syntax)
            ]
    # end def _m_setup_attributes

    def _m_setup_relevant_roots (cls) :
        pass
    # end def _m_setup_relevant_roots

    def _m_setup_sorted_by (cls) :
        pass
    # end def _m_setup_sorted_by

    def _set_type_names (cls, base_name) :
        with TFL.Context.attr_let (M_E_Type, type_name = None) :
            ### temporarily disable metaclass property `type_name` to allow
            ### change
            cls.__m_super._set_type_names (base_name)
    # end def _set_type_names

    def __lt__ (cls, rhs) :
        return cls.__name__ < getattr (rhs, "__name__", rhs)
    # end def __lt__

    def __getattr__ (cls, name) :
        ### just to ease up-chaining in descendents
        head = repr (cls) if name == "_type_name" else cls.type_name
        raise AttributeError ("%s.%s" % (head, name))
    # end def __getattr__

# end class M_E_Type

M_E_Type.M_Root = M_E_Type

@TFL.Add_To_Class ("M_E_Type", M_An_Entity)
class M_E_Type_An (M_E_Type) :
    """Meta class for essence of MOM.An_Entity."""

    Manager     = MOM.E_Type_Manager.An_Entity

    def __call__ (cls, * args, ** kw) :
        if "scope" not in kw :
            kw ["scope"] = MOM.Scope.active
        return cls._m_call (* args, ** kw)
    # end def __call__

    def _m_setup_attributes (cls) :
        cls.__m_super._m_setup_attributes ()
        cls.hash_sig = cls.sig_attr = cls.user_attr
        assert not cls.primary, \
            "An_Entity `%s` cannot have primary attributes" % (cls.type_name, )
    # end def _m_setup_attributes

    def _m_setup_sorted_by (cls) :
        cls.sorted_by = TFL.Sorted_By (* tuple (a.name for a in cls.hash_sig))
    # end def _m_setup_sorted_by

# end class M_E_Type_An

@TFL.Add_To_Class ("M_E_Type", M_Id_Entity)
class M_E_Type_Id (M_E_Type) :
    """Meta class for essence of MOM.Id_Entity."""

    Manager          = MOM.E_Type_Manager.Id_Entity

    _args_as_kw_dict = "kw = dict (kw)\n    kw.update"
    _args_as_kw_head = """def args_as_kw (cls, %(args)s, ** kw) :"""

    _epkified_sep    = "\n    "
    _epkified_head   = """def epkified_%(suffix)s (cls, %(args)s) :"""
    _epkified_tail   = """return (%(epk)s), kw\n"""

    @property
    def electric (cls) :
        ### Define `electric` as property to make changes of the class
        ### attribute impossible
        return cls.attr_prop ("electric").default
    # end def electric

    @property
    def Ref_Map (cls) :
        result = cls._all_ref_map
        if result is None :
            result = cls._all_ref_map = {}
            result.update (cls.Ref_Opt_Map)
            result.update (cls.Ref_Req_Map)
        return result
    # end def Ref_Map

    @property
    def Ref_Opt_Map (cls) :
        result = cls._all_ref_opt_map
        if result is None :
            result = cls._all_ref_opt_map = cls._calc_ref_map \
                ("Ref_Opt_Map", "_own_ref_opt_map")
        return result
    # end def Ref_Opt_Map

    @property
    def Ref_Req_Map (cls) :
        result = cls._all_ref_req_map
        if result is None :
            result = cls._all_ref_req_map = cls._calc_ref_map \
                ("Ref_Req_Map", "_own_ref_req_map", cls.refuse_links)
        return result
    # end def Ref_Req_Map

    @property
    def x_locked (cls) :
        ### Define `x_locked` as property to make changes of the class
        ### attribute impossible
        return cls.attr_prop ("x_locked").default
    # end def x_locked

    def sort_key_pm (cls, sort_key = None) :
        return TFL.Sorted_By \
            ("relevant_root.type_name", sort_key or cls.sort_key)
    # end def sort_key_pm

    def sort_key (cls, entity) :
        ###
        ### Using `cls.sorted_by` here fails in Python 3.x for sorting
        ### lists with different link types
        ###
        ###     Because each link type redefines `sorted_by` differently,
        ###     `cls.sorted_by` of their common ancestor doesn't do
        ###     the right thing (TM)
        ###
        ### `sort_key` re-evaluates `sorted_by` for each `entity` to be
        ### sorted and thus avoids this problem
        ###
        return entity.sorted_by (entity)
    # end def sort_key

    def _calc_ref_map (cls, name, _name, refuse = None) :
        result = TFL.defaultdict (set)
        for b in cls.__bases__ :
            for k, v in pyk.iteritems (getattr (b, name, {})) :
                if refuse and k.type_name in refuse :
                    def _filter (k, v):
                        for n in v :
                            a = k.attr_prop (n)
                            if not isinstance (a, MOM.Attr.Link_Role) :
                                yield a
                    v = tuple (_filter (k, v))
                if v :
                    result [k].update (v)
        own_map = getattr (cls, _name)
        for k, v in pyk.iteritems (own_map) :
            if not k.is_partial :
                result [k].update (v)
        return result
    # end def _calc_ref_map

    def _m_auto_epkified (cls, epk_sig, args, code, suffix) :
        form    = cls._epkified_sep.join \
            (x for x in (cls._epkified_head, code, cls._epkified_tail) if x)
        globals = class_globals (cls)
        scope   = dict          ()
        code    = form % dict \
            ( epk    = ", ".join (epk_sig) + ("," if len (epk_sig) == 1 else "")
            , args   = ", ".join (x for x in (args, "** kw") if x)
            , suffix = suffix
            )
        exec (code, globals, scope)
        result             = scope ["epkified_%s" % suffix]
        result.epk_sig     = epk_sig
        result.args        = args
        result.source_code = code
        return classmethod (result)
    # end def _m_auto_epkified

    def _m_finish_init (cls) :
        with TFL.Context.attr_let \
                 (cls.__class__, electric = None, x_locked = None) :
            ### temporarily disable metaclass properties to allow
            ### assignment of attribute descriptors to `cls`
            cls.__m_super._m_finish_init ()
    # end def _m_finish_init

    def _m_fix_refuse_links (cls, app_type) :
        for tn in cls.refuse_links :
            ET = app_type.etypes.get (tn)
            if ET is not None :
                rs = (r for r in ET.Role_Attrs if issubclass (cls, r.E_Type))
                for r in rs :
                    a = ET.attr_prop (r.name)
                    a.refuse_e_types.update ((cls.type_name, cls.type_name_fq))
    # end def _m_fix_refuse_links

    def _m_setup_attributes (cls) :
        cls.__m_super._m_setup_attributes ()
        cls.is_editable  = cls.user_attr and not cls.is_locked ()
        cls.show_in_ui   = \
            (   cls.record_changes and cls.show_in_ui
            and bool (cls.children_np or not cls.is_partial)
            )
        cls.sig_attr     = cls.primary
        MOM._Id_Entity_Destroyed_Mixin_.define_e_type (cls)
        cls._m_setup_ref_maps   ()
        ### setup `epkified_ckd` and `epkified_raw`
        pkas             = tuple (a.attr for a in cls.primary)
        a_ckd            = ", ".join (a.as_arg_ckd () for a in pkas)
        a_raw            = ", ".join (a.as_arg_raw () for a in pkas)
        d_ckd            = cls._epkified_sep.join \
            (x for x in (a.epk_def_set_ckd () for a in pkas) if x)
        d_raw            = cls._epkified_sep.join \
            (x for x in (a.epk_def_set_raw () for a in pkas) if x)
        epk_sig          = cls.epk_sig
        cls.epkified_ckd = cls._m_auto_epkified (epk_sig, a_ckd, d_ckd, "ckd")
        cls.epkified_raw = cls._m_auto_epkified (epk_sig, a_raw, d_raw, "raw")
        if epk_sig :
            cls.args_as_kw = cls._m_auto_args_as_kw (epk_sig, pkas)
    # end def _m_setup_attributes

    def _m_setup_children (cls, bases, dct) :
        cls.__m_super._m_setup_children (bases, dct)
        cls.relevant_roots = {}
        if cls.is_relevant :
            rel_bases = tuple \
                (b for b in bases if getattr (b, "is_relevant", False))
            if not rel_bases :
                cls.relevant_root = cls
            epk_sig  = cls.epk_sig
            es_roots = tuple (rb for rb in rel_bases if rb.epk_sig == epk_sig)
            if not es_roots :
                cls.epk_sig_root = cls
    # end def _m_setup_children

    def _m_setup_sorted_by (cls) :
        sbs        = []
        sb_default = ["type_name", "pid"]
        if cls.epk_sig :
            def _pka_sorted_by (name, et) :
                return tuple ("%s.%s" % (name, s) for s in et.sorted_by)
            for pka in sorted (cls.primary, key = TFL.Getter.sort_rank) :
                if not pka.sort_skip :
                    if pka.E_Type and pka.E_Type.sorted_by is not None :
                        pka_sb = _pka_sorted_by (pka.name, pka.E_Type)
                        if isinstance (pka.attr, MOM.Attr._A_Id_Entity_) :
                            if pka_sb and pka.E_Type.is_relevant :
                                sbs.extend (pka_sb)
                            else :
                                ### Class is too abstract:
                                ### need to use `type_name, pid`
                                sbs.extend \
                                    (   "%s.%s" % (pka.name, k)
                                    for k in ["type_name", "pid"]
                                    )
                        elif isinstance (pka.attr, MOM.Attr._A_Composite_) :
                            sbs.extend (pka_sb)
                    else :
                        sbs.append (pka.name)
        sb = TFL.Sorted_By (* (sbs or sb_default))
        cls.sorted_by_epk = sb
    # end def _m_setup_sorted_by

    def _m_setup_ref_maps (cls) :
        for eia in cls.id_entity_attr :
            ET = eia.E_Type
            if ET :
                req = eia.is_required
                map = ET._own_ref_req_map if req else ET._own_ref_opt_map
                map [cls].add (eia.name)
    # end def _m_setup_ref_maps

    def _m_setup_relevant_roots (cls) :
        if not cls.relevant_root :
            rr = cls.relevant_roots
            for c in pyk.itervalues (cls.children) :
                if c.relevant_root is c :
                    rr [c.type_name] = c
                else :
                    rr.update (c.relevant_roots)
    # end def _m_setup_relevant_roots

# end class M_E_Type_Id

class _M_E_Type_Id_RC_ (M_E_Mixin) :
    """Meta class for destroyed classes."""

    def __init__ (cls, name, bases, dct) :
        type.__init__ (cls, name, bases, dct)
    # end def __init__

    def __call__ (cls, * args, ** kw) :
        raise TypeError ("%s cannot be instantiated." % (cls, ))
    # end def __call__

    def __repr__ (cls) :
        return type.__repr__ (cls)
    # end def __repr__

# end class _M_E_Type_Id_RC_

class M_E_Type_Id_Destroyed (_M_E_Type_Id_RC_) :
    """Meta class for destroyed classes."""

# end class M_E_Type_Id_Destroyed

class M_E_Type_Id_Reload (_M_E_Type_Id_RC_) :
    """Meta class for reload classes."""

# end class M_E_Type_Id_Reload

@TFL.Add_To_Class ("M_E_Type", M_MD_Entity)
class M_E_Type_MD (M_E_Type) :
    """Meta class for essence of MOM.MD_Entity."""

    Manager        = MOM.E_Type_Manager.MD_Entity

    relevant_roots = {}

    def _m_setup_attributes (cls) :
        cls.__m_super._m_setup_attributes ()
        cls.sig_attr = tuple \
            (cls._Attributes._attr_dict [k] for k in cls._sig_attr_names)
    # end def _m_setup_attributes

# end class M_E_Type_MD

### «text» ### start of documentation
__doc__ = """


"""

if __name__ != "__main__" :
    MOM.Meta._Export ("*", "_M_E_Type_Id_RC_")
### __END__ MOM.Meta.M_Entity
