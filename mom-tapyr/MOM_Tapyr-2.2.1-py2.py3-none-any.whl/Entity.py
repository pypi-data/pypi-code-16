# -*- coding: utf-8 -*-
# Copyright (C) 1999-2016 Mag. Christian Tanzer. All rights reserved
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
#    MOM.Entity
#
# Purpose
#    Root class for object- and link-types of MOM meta object model
#
# Revision Dates
#    17-Sep-2009 (CT) Creation (factored from `TOM.Entity`)
#    23-Sep-2009 (CT) Journal-related methods removed
#     1-Oct-2009 (CT) `Entity_Essentials` removed
#     7-Oct-2009 (CT) `filters` removed
#     8-Oct-2009 (CT) `An_Entity` and `Id_Entity` factored from `Entity`
#     9-Oct-2009 (CT) Cooked instead of raw values assigned to
#                     attribute `default`s
#    12-Oct-2009 (CT) `Entity.__init__` changed to set attributes from `kw`
#    12-Oct-2009 (CT) `Id_Entity._init_epk` added and used
#    13-Oct-2009 (CT) `Id_Entity`: redefined `set` and `set_raw`
#    13-Oct-2009 (CT) `Id_Entity`: added `_extract_primary*`,
#                     `_rename`, and `_reset_epk`
#    13-Oct-2009 (CT) `__init__` and `__new__` refactored
#    15-Oct-2009 (CT) `is_relevant` and `relevant_root` added
#    20-Oct-2009 (CT) Moved call of `init_epk` from `__new__` to `__init__`
#    20-Oct-2009 (CT) `epk_as_dict` added
#    21-Oct-2009 (CT) `is_locked` changed to use `.default` if called
#                     as class method
#    21-Oct-2009 (CT) `Class_Uses_Default_Mixin` removed
#    21-Oct-2009 (CT) `_finish__init__` factored
#    21-Oct-2009 (CT) Predicate `primary_key_defined` removed
#    25-Oct-2009 (MG) `__getattr__` Use %s instead of %r to avoid recursive
#                     calls of `__getattr__`
#     4-Nov-2009 (CT) `refuse_links` changed from dict to set
#    23-Nov-2009 (CT) `epk_as_code` added and used in `_repr` and `__str__`
#    25-Nov-2009 (CT) `set` and `set_raw` of `Id_Entity` corrected
#    25-Nov-2009 (CT) `as_code`, `attr_as_code` and `errors` added
#    26-Nov-2009 (CT) `_extract_primary` changed to allow `role_name`, too
#    26-Nov-2009 (CT) `set` and `set_raw` of `Id_Entity` changed to include
#                     `len (pkas_ckd)` in `result`
#    26-Nov-2009 (CT) Use `except ... as ...` (3-compatibility)
#    26-Nov-2009 (CT) s/_finish__init__/_main__init__/
#    27-Nov-2009 (CT) `update_dependency_names` removed
#    28-Nov-2009 (CT) `is_partial = True` added to all classes
#     3-Dec-2009 (CT) `set_raw` changed to use `on_error`
#     3-Dec-2009 (CT) `on_error` changed to use `scope._attr_errors` and print
#                     warning
#     3-Dec-2009 (CT) `sorted_by` changed to be `Alias_Property` for
#                     `sorted_by_epk`
#    14-Dec-2009 (CT) `user_attr_iter` factored
#    14-Dec-2009 (CT) `copy` changed to handle `scope`
#    14-Dec-2009 (CT) `Id_Entity._main__init__` changed to not call `scope.add`
#    15-Dec-2009 (MG) `_reset_epk`: guard added to make sure `epk` is only
#                     deleted if it is present in the instance dict
#    16-Dec-2009 (CT) `_reset_epk` un-DRY-ed
#    16-Dec-2009 (CT) `_set_ckd` and `_set_raw` factored and used
#    16-Dec-2009 (CT) `copy` rewritten to use `nested_change_recorder`
#    17-Dec-2009 (CT) `_record_context` factored from `set` and `set_raw` and
#                     guard for `electric` added
#    17-Dec-2009 (CT) `epk_raw` added
#    17-Dec-2009 (CT) `changes` and `async_changes` added
#    17-Dec-2009 (CT) `user_diff` and `user_equal` added
#    18-Dec-2009 (CT) Initialization of `dependencies` moved to
#                     `_init_meta_attrs`
#    21-Dec-2009 (CT) `as_pickle_cargo` and `from_pickle_cargo` added
#    21-Dec-2009 (CT) Signature of `_finish__init__` changed to `(self)`
#    30-Dec-2009 (CT) s/Package_NS/PNS/
#    20-Jan-2010 (CT) `ETM` and `lid` added to `Id_Entity`
#    21-Jan-2010 (CT) `copy` changed to only copy attributes `to_save`
#    21-Jan-2010 (CT) `epkified` added, `epkified_ckd` and `epkified_raw` used
#     2-Feb-2010 (CT) Support for `updates_pending` of attributes added
#     4-Feb-2010 (CT) `An_Entity.as_string` added
#     4-Feb-2010 (CT) Optional argument `kind` added to `is_correct`
#     4-Feb-2010 (CT) `An_Entity.copy` added and `._init_attributes` redefined
#     5-Feb-2010 (CT) Change management for `set` and `set_raw` moved from
#                     `Id_Entity` to `Entity`
#     5-Feb-2010 (CT) Exception handler added `epkified` to improve error
#                     message
#     8-Feb-2010 (CT) `An_Entity.__init__` added to disable `* args`
#     8-Feb-2010 (CT) `snapshot` and `has_changed` removed
#     9-Feb-2010 (CT) `epk_hash` added
#     9-Feb-2010 (CT) `An_Entity.set` and `.set_raw` redefined
#    10-Feb-2010 (CT) `FO` and `ui_display` added
#    12-Feb-2010 (CT) `FO` turned into a Auto_Cached attribute
#    13-Feb-2010 (MG) `_record_iter` changed to allow recognition of specific
#                     role names (e.g.: rodent, trap, person, ...)
#    16-Feb-2010 (MG) `copy` fixed (use the correct etypes from the passed
#                     scope argument)
#    16-Feb-2010 (CT) `copy` changed to use `scope.entity_type` instead of
#                     home-grown code
#    19-Feb-2010 (MG) `Entity.__repr__` changed
#    22-Feb-2010 (CT) `cooked_attrs` added
#    25-Feb-2010 (CT) `mandatory_defined` added
#    25-Feb-2010 (CT) `Id_Entity._main__init__` changed to pass both `epk` and
#                     `kw` in a single call to `setter`
#     1-Mar-2010 (CT) `set_pickle_cargo` factored from `from_pickle_cargo`
#     1-Mar-2010 (CT) `_record_iter_attrs` replaced by `recordable_attrs`
#    11-Mar-2010 (CT) `mandatory_defined` removed (was a Bad Idea (tm))
#    11-Mar-2010 (CT) `_kw_check_mandatory` added
#    11-Mar-2010 (CT) `raw_attr_dict` factored
#    11-Mar-2010 (CT) `An_Entity.set` and `.set_raw` changed to handle changes
#                     of primary composite attributes properly (rename!)
#    15-Mar-2010 (CT) Exception handler added to `epk_as_code`
#    22-Mar-2010 (CT) `last_changed` added
#     8-Apr-2010 (CT) `last_changed.computed` guarded against `first` returning
#                     `None`
#    26-Apr-2010 (CT) Guard against `raw` added to `Entity.set` and
#                     `Entity.set_raw`
#     3-May-2010 (CT) `epk` and `epk_raw` changed to append `type_name`
#    12-May-2010 (CT) `lid` removed
#    17-May-2010 (CT) `copy` changed to not handle other `scope` instances
#    19-May-2010 (CT) `user_diff` and `user_equal` rewritten to compare
#                     `as_pickle_cargo` (otherwise, attributes pointing to
#                     other entities make trouble)
#    27-May-2010 (CT) `cooked_attrs` changed to `from_string` instead `cooked`
#    27-May-2010 (CT) `on_error` added to `cooked_attrs`
#    17-Jun-2010 (CT) Use `TFL.I18N.encode_o` instead of home-grown code
#    17-Jun-2010 (CT) `__unicode__` introduced
#    18-Jun-2010 (CT) s/""/u""/
#    22-Jun-2010 (CT) `_kw_check_mandatory` changed to set
#                     `_pred_man.missing_mandatory`
#    22-Jun-2010 (CT) `_main__init__` changed to raise `mandatory_errors`, if
#                     any (otherwise, `on_error` can lead to object creation
#                     with missing `epk`)
#    24-Jun-2010 (CT) `relevant_root = None` moved from `Id_Entity` to `Entity`
#    29-Jun-2010 (CT) s/from_pickle_cargo/from_attr_pickle_cargo/
#                     s/as_pickle_cargo/as_attr_pickle_cargo/
#    29-Jun-2010 (CT) New `as_pickle_cargo` added
#    30-Jun-2010 (CT) Reference to `home_scope._locked` removed
#     1-Jul-2010 (CT) `Id_Entity.as_pickle_cargo` changed to put `pid` last
#    11-Aug-2010 (CT) `last_cid` added
#    11-Aug-2010 (CT) Optional argument `ignore` added to `user_diff`
#    18-Aug-2010 (CT) `owner_attr` added to `An_Entity`
#    19-Aug-2010 (CT) `An_Entity.__nonzero__` added
#    19-Aug-2010 (CT) `Id_Entity.ui_display_format` changed to use
#                     `has_substance` to check attributes
#     3-Sep-2010 (CT) `epk_hash` removed
#     8-Sep-2010 (CT) `record_attr_change` implemented
#    13-Sep-2010 (CT) `_FO_.__getattr__` changed to return `FO` of `Entity`
#                     instances
#    14-Sep-2010 (CT) `unicode_literals` added
#    28-Sep-2010 (CT) `epk_raw` changed to use `get_raw_epk` instead of
#                     `get_raw`
#    14-Oct-2010 (CT) `init_finished` added
#    14-Oct-2010 (CT) `Init_Only_Mixin` added to `electric`
#    22-Dec-2010 (CT) `is_relevant` moved from `Id_Entity` to `Entity`
#     8-Feb-2011 (CT) s/Required/Necessary/, s/Mandatory/Required/
#    27-May-2011 (CT) Guard for unchanged `epk` added to `_set_raw`
#     9-Sep-2011 (CT) `Id_Entity.__eq__` (& `__hash__`) redefined to cheaply
#                     support queries against integers (interpreted as `pid`)
#    15-Nov-2011 (CT) Add defaults for `polymorphic_epk` and `polymorphic_epks`
#    20-Dec-2011 (CT) Remove `sorted` from `attr_as_code`
#    19-Jan-2012 (CT) Add `_init_pending`, make `_home_scope` optional
#    19-Jan-2012 (CT) Call `_finish__init__` only if `_home_scope`
#    24-Jan-2012 (CT) Remove `generate_doc`, `auto_display`, and `save_to_db`
#    24-Jan-2012 (CT) Add `show_in_ui`
#    31-Jan-2012 (CT) Change defaults for `polymorphic_epk` & `polymorphic_epks`
#                     from `None` to `False`
#    29-Mar-2012 (CT) Factor `all_links` up from `MOM.Object`
#    11-Apr-2012 (CT) Delay call of `_finish__init__` (called by `Scope.add`)
#    11-Apr-2012 (CT) Change `__eq__` (and `__hash__`) to use `pid` (and `guid`)
#    12-Apr-2012 (CT) Raise `Required_Missing`, not `TypeError`, in `epkified`
#    12-Apr-2012 (CT) Adapt `_kw_check_required` to change of `Required_Missing`
#    15-Apr-2012 (CT) Adapted to changes of `MOM.Error`
#    16-Apr-2012 (CT) Factor `FO.__call__`, add optional argument `value`
#    16-Apr-2012 (CT) Change `epkified` to `raise TypeError` if `not missing`
#    19-Apr-2012 (CT) Use translated `.ui_name` instead of `.type_name` for
#                     exceptions
#    20-Apr-2012 (CT) Change `Id_Entity._main__init__` to wrap
#                     `MOM.Error.Required_Missing` in `MOM.Error.Invariants`
#                     after checking predicates
#    20-Apr-2012 (CT) Factor `_kw_raw_check_predicates`
#    20-Apr-2012 (CT) Change `_set_ckd` and `_set_raw` to not set attributes in
#                     case of predicate errors
#    20-Apr-2012 (CT) Change `errors` to return `iter (self._pred_man)` instead
#                     of home-grown code (that lacked `missing_required`)
#    22-Apr-2012 (CT) Rename argument `kind` of `is_correct` and
#                     `_kw_check_required` to `_kind` to avoid possible name
#                     clash with an attribute with name `kind`
#     6-Jun-2012 (CT) Add `tn_pid`
#     6-Jun-2012 (CT) Set `_A_Id_Entity_.P_Type = Id_Entity`
#    13-Jun-2012 (CT) Add `reload_from_pickle_cargo`
#    18-Jun-2012 (CT) Add `_Id_Entity_Reload_Mixin_`
#     4-Jul-2012 (CT) `Id_Entity.__eq__` (& `__hash__`) redefined to cheaply
#                     support queries against strings (interpreted as `pid`)
#    30-Jul-2012 (CT) Change `_Id_Entity_Reload_Mixin_` to delegate `__repr__`
#     1-Aug-2012 (CT) Change `destroy_dependency` to consider
#                     `attr.is_required` and `attr.is_primary`, record changes
#     1-Aug-2012 (CT) Add `_Id_Entity_Destroyed_Mixin_`
#     3-Aug-2012 (CT) Add `all_referrers`, rewrite `all_links` to use it
#     4-Aug-2012 (CT) Add `Id_Entity.restore`
#     5-Aug-2012 (CT) Add `epk_raw_pid`
#     5-Aug-2012 (MG) Change `set` to use `get_raw_pid`
#     5-Aug-2012 (CT) Change `_record_iter_raw` to include `raw_pid`
#     7-Aug-2012 (CT) Use `Add_To_Class` instead of home-grown code
#     8-Aug-2012 (CT) Use `logging` instead of `print`
#     9-Sep-2012 (CT) Add `creation_date`
#    10-Sep-2012 (CT) Fix `creation_date.computed`
#    12-Sep-2012 (CT) Call `record_change` unconditionally
#    24-Sep-2012 (CT) Don't wrap `Error.Attribute_Value`
#    27-Sep-2012 (CT) Remove `rank` (never used in MOM)
#    12-Oct-2012 (CT) Use `signified` in `An_Entity._main__init__` to (allow
#                     `* args`), remove `.__init__` (which disallowed `* args`)
#    12-Oct-2012 (CT) Call `An_Entity.attr_as_code`, not `_formatted_user_attr`,
#                     in `An_Entity._repr` and `.__unicode__`
#    16-Oct-2012 (CT) Factor `attr_tuple_to_save` from `An_Entity.attr_as_code`
#     6-Dec-2012 (CT) Factor `creation` and `last_change`,
#                     add `created_by` and `last_changed_by`
#    10-Dec-2012 (CT) Add support for nested attributes to `FO`
#    11-Dec-2012 (CT) Move `_Class_Kind` from `Entity` to `M_Entity`
#    11-Jan-2013 (CT) Check `primary_ais` in `_main__init__`
#    16-Jan-2013 (CT) Use `.E_Type.primary_ais`, not `.primary_ais`
#    29-Jan-2013 (CT) Add `uniqueness_dbw` and `uniqueness_ems`
#    30-Jan-2013 (CT) Add access to `last_cid` and `restore` to
#                     `_Id_Entity_Destroyed_Mixin_`
#    30-Jan-2013 (CT) Add access to `last_cid` to `_Id_Entity_Destroyed_Mixin_`
#    22-Feb-2013 (CT)  Use `TFL.Undef ()` not `object ()`
#    26-Feb-2013 (CT) Add attribute `ui_repr`
#     5-Mar-2013 (CT) Remove `Attr.Init_Only_Mixin` from `electric`
#    21-Mar-2013 (CT) Add `has_identity`
#    27-Mar-2013 (CT) Add `TFL.Q_Result._Attr_` to `Id_Entity.__eq__`;
#                     add `Id_Entity.__ne__`
#    26-Apr-2013 (CT) Remove support for `primary_ais`
#    30-Apr-2013 (CT) Add `add_error`
#    10-May-2013 (CT) Add `show_in_ui_T`
#    26-May-2013 (CT) Add `Id_Entity.as_migration`
#     3-Jun-2013 (CT) Add `attr_prop`, get attribute descriptors from
#                     `.attributes`, not from `__class__`
#     4-Jun-2013 (CT) Simplify `is_locked`
#     4-Jun-2013 (CT) Exclude attribute `type_name` from `as_migration`
#     4-Jun-2013 (CT) Add attribute `type_name`
#     4-Jun-2013 (CT) Add attribute `pid`
#     5-Jun-2013 (CT) Set `x_locked.q_able` to `False`
#     6-Jun-2013 (CT) Add `destroy_dependency` to
#                     `_Id_Entity_Destroyed_Mixin_.__getattr__`
#    12-Jul-2013 (CT) Add `MD_Entity._Attributes.kind`
#    12-Jul-2013 (CT) Add `Id_Entity.creation_q`
#    17-Jul-2013 (CT) Add `MD_Entity._main__init__`, `._repr`
#    17-Jul-2013 (CT) Add `MD_Change._Attributes.scm_change.Pickler`,
#                     remove `MD_Change._Attributes.pickle`
#    17-Jul-2013 (CT) Change `async_changes` to use `scope.query_changes`
#    18-Jul-2013 (CT) Add `An_Entity.attr_tuple`
#    22-Jul-2013 (CT) Add `_Sync_Change_` to, remove `Just_Once_Mixin` from,
#                     `MD_Change._Attributes._Derived_Attr_`
#    24-Jul-2013 (CT) Add `c_time` and `c_user` to `MD_Change`
#     1-Aug-2013 (CT) Add `spk_attr_name` and `spk`
#     9-Aug-2013 (CT) Set `_A_Id_Entity_.P_Type_S` to `Id_Entity`
#    21-Aug-2013 (CT) Convert `creation` and `last_change` to Query,
#                     remove `creation_q`, factor _A_Change_
#    22-Aug-2013 (CT) Remove `tn_pid`
#    25-Aug-2013 (CT) Change `as_attr_pickle_cargo` to use `a.save_to_db`, not
#                     `a.to_save (self)`
#    18-Sep-2013 (CT) Change `_extract_primary_ckd` to call `pka.cooked (w)`
#    18-Sep-2013 (CT) Add change-guard for `new_epk` to `_set_ckd`, `_set_raw`
#     4-Oct-2013 (CT) Remove guard for `pid` from `attr_prop`
#     9-Oct-2013 (CT) Fix `created_by.computed`
#    16-Jan-2014 (CT) Factor class/instance property `ui_name_T`
#     1-Mar-2014 (CT) Change `ui_repr.computed` to use `sig_attr`, not `epk_raw`
#     1-Mar-2014 (CT) Factor `ui_display_format` to `Entity`
#     1-Mar-2014 (CT) Add `MD_Entity.has_identity`, `._sig_attr_names`
#     1-Mar-2014 (CT) Redefine `MD_Change.ui_display_format`
#     2-Mar-2014 (CT) Set `MD_Change.user.only_e_types`
#     2-Mar-2014 (CT) Add `hidden_nested` to various attributes
#     3-Mar-2014 (CT) Factor `FO_nested`
#     1-May-2014 (CT) Change `_kw_raw_check_predicates` to catch  `Invariants`
#                     * up to now, Error.Invariants of nested composites were
#                       silently ignored, doh!
#     2-Jul-2014 (CT) Change `_kw_raw_check_predicates` to wrap errors in
#                     `MOM.Error.Invariants`
#    30-Aug-2014 (CT) Correct `_kw_check_required` to refuse value `None` for
#                     required attributes
#    25-Sep-2014 (CT) Rename `signified` to `args_as_kw`; add `epk_as_kw`
#    25-Sep-2014 (CT) Add and use `_kw_polished`
#    25-Sep-2014 (CT) Factor `_kw_undeprecated`, `_set_ckd_inner`,
#                     `_set_raw_inner`
#    26-Sep-2014 (CT) Change `_kw_polished`, `_kw_undeprecated` to `classmethod`
#     9-Oct-2014 (CT) Use `portable_repr`
#    26-Jan-2015 (CT) Use `M_Auto_Update_Combined`, not `M_Auto_Combine`,
#                     as metaclass
#    13-Apr-2015 (CT) Add `_json_encode`, `__json_encode_FO_`
#    23-Apr-2015 (CT) Add `Id_Entity.use_indices` with: `last_cid`
#    23-Apr-2015 (CT) Add `MD_Change.use_indices` with: `parent_cid`, `pid`,
#                     and `(type_name, cid)`
#    27-Apr-2015 (CT) Use `use_index`, not `use_indices`, where possible
#    15-Jun-2015 (CT) Change `_kw_raw_check_predicates` to add `None` to `ckd_kw`
#    30-Jul-2015 (CT) Add argument `essence`, `picky` to `polisher`
#    30-Jul-2015 (CT) Change `_kw_polished` to handle polisher errors
#     3-Aug-2015 (CT) Use `_init_raw_default`, not literal `False`
#    10-Aug-2015 (CT) Add documentation for introspective attribute properties
#    12-Aug-2015 (CT) Remove obsolete `compute_defaults_internal`
#    12-Aug-2015 (CT) Add method docstrings; split up module docstring
#    15-Aug-2015 (CT) Set `type_name.max_length` to 0
#    16-Aug-2015 (CT) Add `auto_derived_p`, `auto_derived_root`
#     8-Oct-2015 (CT) Change `__getattr__` to *not* handle `__XXX__`
#    16-Dec-2015 (CT) Add `UI_Spec`
#    18-Dec-2015 (CT) Change `_main__init__` to not pass `on_error` to
#                     `epk_as_kw`
#     5-Feb-2016 (CT) Add `polish_empty`
#     5-May-2016 (CT) Add support for predicates of kind `object_init`
#     6-May-2016 (CT) Add computed attribute `playback_p`
#    22-Jun-2016 (CT) Add staticmethod `_ui_display`
#     6-Jul-2016 (CT) Call `attr.set_cooked`, not `attr._set_cooked`
#    22-Jul-2016 (CT) Move `has_identity` from `An_Entity` to `Entity`
#    19-Oct-2016 (CT) Change `attr_prop` to handle dotted names
#                     + I.e., access to nested attribute properties of
#                       composite/structured attributes
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division
from   __future__  import print_function, unicode_literals

from   _MOM                  import MOM
from   _TFL                  import TFL

import _MOM._Attr.Kind
import _MOM._Attr.Manager
import _MOM._Attr.Spec
import _MOM._Attr.Type

import _MOM._Meta.M_Entity

import _MOM._Pred.Kind
import _MOM._Pred.Manager
import _MOM._Pred.Spec
import _MOM._Pred.Type

import _MOM._SCM.Change

from   _MOM._Attr.Type        import *
from   _MOM._Attr.Date_Time   import *
from   _MOM._Attr             import Attr
from   _MOM._Pred             import Pred

import _TFL._Meta.Once_Property
import _TFL.Decorator
import _TFL.defaultdict
import _TFL.Sorted_By
import _TFL.Undef

from   _TFL.I18N             import _, _T, _Tn
import _TFL.json_dump
from   _TFL.object_globals   import object_globals
from   _TFL.portable_repr    import portable_repr
from   _TFL.predicate        import paired
from   _TFL.pyk              import pyk

import itertools
import logging
import traceback

class Entity (TFL.Meta.BaM (TFL.Meta.Object, metaclass = MOM.Meta.M_Entity)) :
    """Internal root class for MOM entities with and without identity."""

    PNS                   = MOM

    auto_derived_p        = False ### Set by meta machinery
    auto_derived_root     = None  ### Set by meta machinery
    deprecated_attr_names = {}
    electric              = False
    has_identity          = False
    init_finished         = False
    is_partial            = True
    is_relevant           = False
    is_used               = True
    polymorphic_epk       = False ### Set by meta machinery
    polymorphic_epks      = False ### Set by meta machinery
    relevant_root         = None  ### Set by meta machinery
    show_in_ui            = True  ### Modified by meta machinery
    show_in_ui_T          = True  ### Default for descendent classes
    show_package_prefix   = False ### Include `PNS` in `ui_name` ???
    spk                   = None
    spk_attr_name         = None  ### Name of `surrogate primary key` attribute
    ui_display_sep        = ", "
    x_locked              = False

    _app_globals             = {}
    _attrs_to_update_combine = ("deprecated_attr_names", )
    _home_scope              = None
    _init_raw_default        = False
    _Reload_Mixin_           = None

    class _Attributes (MOM.Attr.Spec) :

        class FO (A_Blob) :
            """`FO.foo` gives the `ui_display` of attribute `foo`, if defined,
               or the raw value of `foo`, otherwise.
            """

            kind               = Attr.Auto_Cached

            def computed (self, obj) :
                return obj._FO_ (obj)
            # end def computed

        # end class FO

        class playback_p (A_Boolean) :

            kind               = Attr.Computed
            hidden             = True

            def computed (self, obj) :
                return obj.home_scope.playback_p
            # end def computed

        # end class playback_p

        class ui_display (A_String) :
            """Display in user interface"""

            kind               = Attr.Computed
            max_length         = 0

            def computed (self, obj) :
                return obj.ui_display_format % obj.FO
            # end def computed

        # end class ui_display

        class ui_repr (A_String) :
            """Repr for user interface"""

            kind               = Attr.Computed
            max_length         = 0

            def computed (self, obj) :
                return "%s %s" % \
                    ( obj.type_name
                    , portable_repr
                        (tuple (a.get_raw (self) for a in self.sig_attr))
                    )
            # end def computed

        # end class ui_repr

    # end class _Attributes

    class _Predicates (MOM.Pred.Spec) :
        pass
    # end class _Predicates

    @pyk.adapt__str__
    class _FO_ (TFL.Meta.Object) :
        """Formatter for attributes of object."""

        undefined = TFL.Undef ("value")

        def __init__ (self, obj) :
            self.__obj = obj
        # end def __init__

        def __call__ (self, name, value = undefined) :
            getter   = getattr (TFL.Getter, name)
            obj      = self.__obj
            try :
                names = name.split (".")
                attr  = obj.attributes [names [0]]
                obj, attr, value = attr.FO_nested (obj, names [1:], value)
            except (AttributeError, LookupError) :
                result = self._get_repr (name, getter)
            else :
                if isinstance (attr, MOM.Attr.Kind) :
                    if value is self.undefined :
                        value   = attr.get_value (obj)
                        get_raw = lambda : attr.get_raw  (obj)
                    else :
                        def get_raw () :
                            result = attr.attr.as_string (value)
                            if isinstance (value, pyk.string_types) :
                                result = portable_repr (result)
                            elif result == "" :
                                result = "None"
                            return result
                    if isinstance (value, Entity) :
                        return value.FO
                    else :
                        uid = getattr (value, "ui_display", None)
                        if uid :
                            result = uid
                        else :
                            result = get_raw ()
                else :
                    if value is self.undefined :
                        result = self._get_repr (name, getter)
                    else :
                        result = value
            return result
        # end def __call__

        def _get_repr (self, name, getter) :
            try :
                result = portable_repr (getter (self.__obj))
            except (AttributeError, LookupError) :
                if "." in name :
                    result = ""
                else :
                    raise
        # end def _get_repr

        def __getattr__ (self, name) :
            if name.startswith ("__") and name.endswith ("__") :
                ### Placate inspect.unwrap of Python 3.5,
                ### which accesses `__wrapped__` and eventually throws
                ### `ValueError`
                return getattr (self.__super, name)
            result = self (name)
            if "." not in name :
                setattr (self, name, result)
            return result
        # end def __getattr__

        def __getitem__ (self, key) :
            try :
                return self.__getattr__ (key)
            except AttributeError :
                raise KeyError (key)
        # end def __getitem__

        def __str__ (self) :
            return self.__obj.ui_display
        # end def __str__

    # end class _FO_

    @TFL.json_dump.default.add_type (_FO_)
    def __json_encode_FO_ (fo) :
        return pyk.text_type (fo)
    # end def __json_encode_FO_

    @property
    def home_scope (self) :
        return self._home_scope or MOM.Scope.active
    # end def home_scope

    @home_scope.setter
    def home_scope (self, value) :
        self._home_scope = value
    # end def home_scope

    @property
    def raw_attr_dict (self) :
        """Dictionary with raw attr values of :attr:`user_attr` that
           `has_substance`.
        """
        return dict \
            (  (a.name, a.get_raw (self))
            for a in self.user_attr if a.has_substance (self)
            )
    # end def raw_attr_dict

    @property
    def recordable_attrs (self) :
        return self.__class__.m_recordable_attrs
    # end def recordable_attrs

    @property
    def ui_display_format (self) :
        """Format used for :attr:`ui_display`."""
        return self.ui_display_sep.join \
            ( "%%(%s)s" % a.name for a in self.sig_attr
            if a.has_substance (self)
            )
    # end def ui_display_format

    @TFL.Meta.Class_Property
    @TFL.Meta.Class_and_Instance_Method
    def ui_name_T (soc) :
        """Localized `ui_name`."""
        ### Must not be a `Once_Property`, because `language` can change
        return _T (soc.ui_name)
    # end def ui_name_T

    def __new__ (cls, * args, ** kw) :
        if cls.is_partial :
            raise MOM.Error.Partial_Type (cls.ui_name_T)
        result = cls.__c_super.__new__ (cls)
        result._home_scope = kw.get ("scope")
        result._init_meta_attrs ()
        return result
    # end def __new__

    def __init__ (self, * args, ** kw) :
        self._init_attributes ()
        kw.pop                ("scope", None)
        self._main__init__    (* args, ** kw)
    # end def __init__

    @classmethod
    def from_attr_pickle_cargo (cls, scope, cargo) :
        """Create new entity in `scope` based on pickle `cargo`."""
        result = cls.__new__    (cls, scope = scope)
        result._init_attributes ()
        result.set_pickle_cargo (cargo)
        return result
    # end def from_attr_pickle_cargo

    ### provide read-only access to this class' __init__
    _MOM_Entity__init__ = property (lambda self, __init__ = __init__ : __init__)

    def after_init (self) :
        """Is called by the UI after an instance of the class was
           (successfully) created. `after_init` can create additional objects
           automatically to ease the life of the interactive user of the
           application.
        """
        pass
    # end def after_init

    def as_attr_pickle_cargo (self) :
        """Dictionary with pickle cargo of :attr:`attributes` that are
           `save_to_db`.
        """
        return dict \
            (   (a.name, a.get_pickle_cargo  (self))
            for a in pyk.itervalues (self.attributes) if a.save_to_db
            )
    # end def as_attr_pickle_cargo

    def as_code (self) :
        return "%s (%s)" % (self.type_name, self.attr_as_code ())
    # end def as_code

    def attr_as_code (self) :
        uai = self.user_attr_iter ()
        return ", ".join ("%s = %s" % (a.name, a.as_code (v)) for (a, v) in uai)
    # end def attr_as_code

    @classmethod
    def attr_prop (cls, name) :
        """Return the property of the attribute named `name`.
           Return None if there is no such attribute.
        """
        result = cls.attributes.get (name)
        if result is None :
            aq = getattr (cls.AQ, name, None)
            if aq is not None :
                result = aq._attr.kind
        return result
    # end def attr_prop

    def attr_value_maybe (self, name) :
        attr = self.attributes.get (name)
        if attr :
            return attr.get_value (self)
    # end def attr_value_maybe

    @TFL.Meta.Class_and_Instance_Method
    def cooked_attrs (soc, kw, on_error = None) :
        """Dictionary `kw` converted to cooked values."""
        attributes = soc.attributes
        result     = {}
        if on_error is None :
            on_error = soc._raise_attr_error
        for name, value in pyk.iteritems (kw) :
            attr = attributes.get (name)
            if attr :
                try :
                    try :
                        result [name] = attr.from_string (value)
                    except MOM.Error.Attribute_Value as exc :
                        raise
                    except (TypeError, ValueError) as exc :
                        raise MOM.Error.Attribute_Value \
                            (soc, name, value, attr.kind, exc)
                except Exception as exc :
                    on_error (exc)
        return result
    # end def cooked_attrs

    def globals (self) :
        return self.__class__._app_globals or object_globals (self)
    # end def globals

    def has_substance (self) :
        """TRUE if there is at least one attribute with a non-default value."""
        return any (a.has_substance (self) for a in self.user_attr)
    # end def has_substance

    def is_correct (self, attr_dict = {}, _kind = "object")  :
        """True if predicates of `_kind` are satisfied for `attr_dict`."""
        ews = self._pred_man.check_kind (_kind, self, attr_dict)
        return not ews
    # end def is_correct

    def raw_attr (self, name) :
        """Returns the raw value of attribute `name`, i.e., the value entered
           by the user into the object editor.
        """
        attr = self.attributes.get (name)
        if attr :
            return attr.get_raw (self) or u""
    # end def raw_attr

    def record_attr_change (self, kw) :
        if kw and self._home_scope :
            self.home_scope.record_change (self.SCM_Change_Attr, self, kw)
    # end def record_attr_change

    def reload_from_pickle_cargo (self, cargo) :
        self.init_finished  = False
        self._init_pending  = []
        self._init_attributes ()
        self.set_pickle_cargo (cargo)
        self._finish__init__  ()
    # end def reload_from_pickle_cargo

    def reset_syncable (self) :
        self._attr_man.reset_syncable ()
    # end def reset_syncable

    def set (self, _pred_kinds = None, on_error = None, ** kw) :
        """Set attributes  from cooked values specified in `kw`."""
        assert "raw" not in kw
        ukw = dict (self._kw_undeprecated (kw))
        return self._set_ckd_inner (_pred_kinds, on_error, ** kw)
    # end def set

    def set_attr_iter (self, attr_dict, on_error = None) :
        attr_get = self.E_Type.attr_prop
        if on_error is None :
            on_error = self._raise_attr_error
        for name, val in pyk.iteritems (attr_dict) :
            attr = attr_get (name)
            if attr is not None :
                if not attr.is_settable :
                    on_error \
                        (MOM.Error.Attribute_Set (self, name, val, attr.kind))
                else :
                    yield (name, val, attr)
            elif name != "raw" :
                on_error (MOM.Error.Attribute_Unknown (self, name, val))
    # end def set_attr_iter

    def set_pickle_cargo (self, cargo) :
        attr_get = self.attributes.get
        for k, v in pyk.iteritems (cargo) :
            attr = attr_get (k)
            ### XXX Add legacy lifting
            if attr :
                attr.set_pickle_cargo  (self, v)
    # end def set_pickle_cargo

    def set_raw (self, _pred_kinds = None, on_error = None, ** kw) :
        """Set attributes from raw values specified in `kw`."""
        assert "raw" not in kw
        ukw = dict (self._kw_undeprecated (kw))
        pkw = self._kw_polished (ukw, on_error)
        return self._set_raw_inner (_pred_kinds, on_error, ** pkw)
    # end def set_raw

    def sync_attributes (self) :
        """Synchronizes all user attributes with the values from
           _raw_attr and all sync-cached attributes.
        """
        self._attr_man.sync_attributes (self)
    # end def sync_attributes

    def user_attr_iter (self) :
        user_attr = self.user_attr
        return ((a, a.get_value (self)) for a in user_attr if a.to_save (self))
    # end def user_attr_iter

    def _finish__init__ (self) :
        """Redefine this to perform additional initialization."""
        assert not self.init_finished
        self.init_finished = True
        for ip in self._init_pending :
            ip ()
        try :
            del self._init_pending
        except AttributeError :
            pass
    # end def _finish__init__

    def _init_attributes (self) :
        self._attr_man.reset_attributes (self)
    # end def _init_attributes_

    def _init_meta_attrs (self) :
        self._init_pending = []
        self._attr_man     = MOM.Attr.Manager (self._Attributes)
        self._pred_man     = MOM.Pred.Manager (self._Predicates)
    # end def _init_meta_attrs

    def _kw_check_required (self, * args, ** kw) :
        needed  = tuple (m.name for m in self.required)
        missing = tuple (k for k in needed if kw.get (k) is None)
        if missing :
            on_error   = kw.pop ("on_error") or self._raise_attr_error
            all_needed = tuple (m.name for m in self.primary_required) + needed
            error = MOM.Error.Required_Missing \
                (self.__class__, all_needed, missing, args, kw)
            on_error (error)
            raise error
    # end def _kw_check_required

    def _kw_check_predicates (self, _kinds = None, on_error = None, ** kw) :
        result = True
        errors = []
        if _kinds is None :
            _kinds = ["object"]
        for _kind in _kinds :
            kr = self.is_correct (kw, _kind)
            if not kr :
                errors.extend (self._pred_man.errors [_kind])
                result = False
        if not result :
            if on_error is None :
                on_error = self._raise_attr_error
            on_error (MOM.Error.Invariants (errors))
        return result
    # end def _kw_check_predicates

    def _kw_raw_check_predicates (self, _kinds = None, on_error = None, ** kw) :
        Err    = MOM.Error
        ckd_kw = {}
        to_do  = []
        errors = []
        if on_error is None :
            on_error = self._raise_attr_error
        for name, val, attr in self.set_attr_iter (kw, on_error) :
            if val is not None :
                try :
                    ckd_kw [name] = ckd_val = attr.from_string (val, self)
                except (Err.Attribute_Value, Err.Attribute_Syntax) as exc :
                    errors.append (exc)
                    to_do.append  ((attr, u"", None))
                except Err.Invariants as exc :
                    exc.embed     (self, name, attr)
                    errors.append (exc)
                    to_do.append  ((attr, u"", None))
                except (TypeError, ValueError, Err.Error) as exc :
                    errors.append \
                        ( MOM.Error.Attribute_Value
                            (self, name, val, attr.kind, exc)
                        )
                    if __debug__ :
                        logging.exception  \
                            ( "\n    %s %s, attribute conversion error "
                              "%s: %s [%s]"
                            , self.type_name, self, name, val, type (val)
                            )
                    to_do.append ((attr, u"", None))
                except Exception as exc :
                    if __debug__ :
                        logging.exception \
                        ( "\n    %s %s, attribute conversion error %s: %s [%s]"
                        , self.type_name, self, name, val, type (val)
                        )
                else :
                    to_do.append ((attr, val, ckd_val))
            else :
                to_do.append ((attr, u"", None))
                ckd_kw [name] = None
        if errors :
            on_error (MOM.Error.Invariants (errors))
        result = self._kw_check_predicates \
            (_kinds = _kinds, on_error = on_error, ** ckd_kw)
        return result, to_do
    # end def _kw_raw_check_predicates

    @TFL.Meta.Class_and_Instance_Method
    def _kw_polished (soc, attr_dict, on_error = None) :
        Err    = MOM.Error
        errors = []
        result = attr_dict
        self   = soc if isinstance (soc, Entity) else None
        if on_error is None :
            on_error = soc._raise_attr_error
        for attr in soc.polish_attr :
            if attr.name in result or attr.polisher.polish_empty :
                val  = result.get (attr.name)
                try :
                    result = attr.polisher \
                        ( attr, result
                        , essence = self
                        , picky   = True
                        , value   = val
                        )
                except (Err.Attribute_Value, Err.Attribute_Syntax) as exc :
                    errors.append (exc)
                except Err.Invariants as exc :
                    if self is not None :
                        exc.embed (self, attr.name, attr)
                    errors.append (exc)
                except (TypeError, ValueError, Err.Error) as exc :
                    errors.append \
                        ( Err.Attribute_Value
                            (soc, attr.name, val, attr.kind, exc)
                        )
                except Exception as exc :
                    if __debug__ :
                        logging.exception \
                        ( "\n    %s %s, attribute polisher error %s: %s [%s]"
                        , soc.type_name, self, attr.name, val, type (val)
                        )
        if errors :
            on_error (MOM.Error.Invariants (errors))
        return result
    # end def _kw_polished

    @classmethod
    def _kw_undeprecated (cls, attr_dict) :
        for name, val in pyk.iteritems (attr_dict) :
            cnam = cls.deprecated_attr_names.get (name, name)
            yield cnam, val
    # end def _kw_undeprecated

    def _print_attr_err (self, exc) :
        if debug:
            logging.exception (repr (self))
        print (self, exc)
    # end def _print_attr_err

    @TFL.Meta.Class_and_Instance_Method
    def _raise_attr_error (soc, exc) :
        raise exc
    # end def _raise_attr_error

    @TFL.Contextmanager
    def _record_context (self, gen, Change) :
        if not self._home_scope :
            yield
        else :
            rvr = dict (gen)
            yield rvr
            if rvr :
                self.home_scope.record_change (Change, self, rvr)
    # end def _record_context

    def _record_iter (self, kw) :
        attributes = self.__class__.attributes
        recordable = self.recordable_attrs
        for name, value in pyk.iteritems (kw) :
            attr = attributes.get (name, None)
            if attr in recordable :
                yield attr, attr.name, value
    # end def _record_iter

    def _record_iter_raw (self, kw) :
        for a, name, value in self._record_iter (kw) :
            yield a, name, value, a.get_raw (self), a.get_raw_pid (self)
    # end def _record_iter_raw

    def _set_ckd (self, _pred_kinds = None, on_error = None, ** kw) :
        man = self._attr_man
        tc  = man.total_changes
        man.reset_pending ()
        if kw :
            is_correct = self._kw_check_predicates \
                (_kinds = _pred_kinds, on_error = on_error, ** kw)
            if is_correct :
                for name, val, attr in self.set_attr_iter (kw, on_error) :
                    attr.set_cooked (self, val)
        if man.updates_pending :
            try :
                man.do_updates_pending (self)
            except Exception :
                pass
        return man.total_changes - tc
    # end def _set_ckd

    def _set_ckd_inner (self, _pred_kinds = None, on_error = None, ** kw) :
        gen = \
            (   (name, attr.get_raw_pid (self))
            for attr, name, value in self._record_iter (kw)
            if  attr.get_value (self) != value
            )
        with self._record_context (gen, self.SCM_Change_Attr) :
            return self._set_ckd (_pred_kinds, on_error, ** kw)
    # end def _set_ckd_inner

    def _set_raw (self, _pred_kinds = None, on_error = None, ** kw) :
        man = self._attr_man
        tc  = man.total_changes
        if kw :
            is_correct, to_do = self._kw_raw_check_predicates \
                (_kinds = _pred_kinds, on_error = on_error, ** kw)
            man.reset_pending ()
            if is_correct :
                for attr, raw_val, val in to_do :
                    attr._set_raw (self, raw_val, val)
        if man.updates_pending :
            man.do_updates_pending (self)
        return man.total_changes - tc
    # end def _set_raw

    def _set_raw_inner (self, _pred_kinds = None, on_error = None, ** kw) :
        gen = \
            (   (name, raw_pid)
            for attr, name, value, raw, raw_pid in self._record_iter_raw (kw)
            if  raw != value
            )
        with self._record_context (gen, self.SCM_Change_Attr) :
            return self._set_raw (_pred_kinds, on_error, ** kw)
    # end def _set_raw_inner

    def _store_attr_error (self, exc) :
        logging.exception ("Setting attribute failed with exception")
        if self._home_scope :
            self.home_scope._attr_errors.append (exc)
    # end def _store_attr_error

    @staticmethod
    def _ui_display (o) :
        return o.ui_display
    # end def _ui_display

    def __getattr__ (self, name) :
        ### just to ease up-chaining in descendents
        raise AttributeError ("%r <%s>" % (name, self.type_name))
    # end def __getattr__

    def __ne__ (self, rhs) :
        return not (self == rhs)
    # end def __ne__

    def __repr__ (self) :
        try :
            return pyk.reprify (self._repr (self.type_name))
        except AttributeError :
            return "<%s Incomplete>" % (self.ui_name_T, )
    # end def __repr__

# end class Entity

@pyk.adapt__bool__
@pyk.adapt__str__
class An_Entity (TFL.Meta.BaM (Entity, metaclass = MOM.Meta.M_An_Entity)) :
    """Root class for anonymous entities without identity."""

    is_partial            = True
    is_primary            = False
    owner                 = None
    attr_name             = None

    @property
    def hash_key (self) :
        """Hash key: tuple of hash values for attributes in :attr:`hash_sig`.
        """
        return tuple (a.get_hash (self) for a in self.hash_sig)
    # end def hash_key

    @property
    def SCM_Change_Attr (self) :
        return MOM.SCM.Change.Attr_Composite
    # end def SCM_Change_Attr

    def as_pickle_cargo (self) :
        """Pickle cargo of `self`."""
        return (str (self.type_name), self.as_attr_pickle_cargo ())
    # end def as_pickle_cargo

    def as_string (self) :
        """Serialization of `self` as string"""
        return tuple (sorted (pyk.iteritems (self.raw_attr_dict)))
    # end def as_string

    def attr_as_code (self) :
        attrs  = self.attr_tuple_to_save ()
        values = tuple (a.as_code (a.get_value (self)) for a in attrs)
        if len (values) == 1 :
            ### trailing comma for single element tuple
            values += ("", )
        result = ", ".join ("%s" % (v, ) for v in values)
        return result
    # end def attr_as_code

    def attr_tuple_to_save (self) :
        """Tuple of attributes in :attr:`user_attr` that need saving."""
        result  = self.user_attr
        save_p  = tuple (a.to_save (self) for a in result) [::-1]
        to_drop = tuple (itertools.takewhile ((lambda x : not x), save_p))
        if to_drop :
            ### drop trailing attributes that don't need to be saved
            result = result [: -len (to_drop)]
        return result
    # end def attr_tuple_to_save

    def attr_tuple (self) :
        """Tuple of of cooked values of attributes in :attr:`user_attr`"""
        return tuple (a.get_value (self) for a in self.user_attr)
    # end def attr_tuple

    def copy (self, ** kw) :
        scope  = kw.pop  ("scope", self.home_scope)
        etype  = scope.entity_type (self.type_name)
        result = etype             (scope = scope, ** kw)
        raw_kw = dict \
            (  (a.name, a.get_raw (self))
            for a in self.user_attr if a.name not in kw
            )
        if raw_kw :
            result.set_raw (** raw_kw)
        return result
    # end def copy

    @classmethod
    def example_attrs (cls, full = False) :
        attrs = cls.user_attr if full else cls.required
        return dict ((a.name, a.example) for a in attrs)
    # end def example_attrs

    @property
    def owner_attr (self) :
        """Return the attribute (kind property) of the `owner` object that
           holds `self`.
        """
        if self.owner and self.attr_name :
            return self.owner.attr_prop (self.attr_name)
    # end def owner_attr

    def _init_attributes (self) :
        self.owner = None
        self.__super._init_attributes ()
    # end def _init_attributes_

    @staticmethod
    def _json_encode (o) :
        return pyk.text_type (o)
    # end def _json_encode

    def _main__init__ (self, * args, ** kw) :
        raw = bool (kw.pop ("raw", self._init_raw_default))
        akw = self.args_as_kw   (* args, ** kw)
        ukw = dict (self._kw_undeprecated (akw))
        skw = self._kw_polished (ukw) if raw else ukw
        self._kw_check_required (* args, ** skw)
        if skw :
            setter = self._set_raw if raw else self._set_ckd
            setter (_pred_kinds = ("object_init", "object"), ** skw)
    # end def _main__init__

    def _repr (self, type_name) :
        return u"%s (%s)" % (type_name, self.attr_as_code ().rstrip (", "))
    # end def _repr

    def _set_ckd_inner (self, _pred_kinds = None, on_error = None, ** kw) :
        owner_attr = self.owner_attr
        if owner_attr is None or self.electric or not owner_attr.record_changes :
            return self._set_ckd (_pred_kinds, on_error, ** kw)
        elif owner_attr and owner_attr.is_primary :
            ### Change in primary attribute might be a `rename`
            return self.owner.set (** {self.attr_name : self.copy (** kw)})
        else :
            return self.__super._set_ckd_inner (_pred_kinds, on_error, ** kw)
    # end def _set_ckd_inner

    def _set_raw_inner (self, _pred_kinds = None, on_error = None, ** kw) :
        owner_attr = self.owner_attr
        if owner_attr is None or self.electric or not owner_attr.record_changes :
            return self._set_raw (_pred_kinds, on_error, ** kw)
        elif owner_attr and owner_attr.is_primary :
            ### Change in primary attribute might be a `rename`
            return self.owner.set \
                (** {self.attr_name : self.copy (raw = True, ** kw)})
        else :
            return self.__super._set_raw_inner (on_error, ** kw)
    # end def _set_raw_inner

    def __eq__ (self, rhs) :
        rhs = getattr (rhs, "hash_key", rhs)
        return self.hash_key == rhs
    # end def __eq__

    def __hash__ (self) :
        return hash (self.hash_key)
    # end def __hash__

    def __bool__ (self) :
        return self.has_substance ()
    # end def __bool__

    def __str__ (self) :
        return "(%s)" % (self.attr_as_code ())
    # end def __str__

# end class An_Entity

_Ancestor_Essence = Entity

@TFL.Add_To_Class ("P_Type",   _A_Id_Entity_)
@TFL.Add_To_Class ("P_Type_S", _A_Id_Entity_)
@pyk.adapt__str__
class Id_Entity \
          (TFL.Meta.BaM (_Ancestor_Essence, metaclass = MOM.Meta.M_Id_Entity)) :
    """Root class for MOM entities with identity, i.e.,
       objects and links.
    """

    has_identity          = True
    is_partial            = True
    max_count             = 0
    record_changes        = True
    refuse_links          = set ()
    sorted_by             = TFL.Meta.Alias_Property ("sorted_by_epk")
    spk                   = TFL.Meta.Alias_Property ("pid")
    spk_attr_name         = "pid" ### Name of `surrogate primary key` attribute
    tutorial              = None

    ### Thanks to `Alias_Property`, `uniqueness_dbw` and `uniqueness_ems` are
    ### accessible for both  the instances and the class
    uniqueness_dbw        = TFL.Meta.Alias_Property \
        ("_Predicates.uniqueness_dbw")
    uniqueness_ems        = TFL.Meta.Alias_Property \
        ("_Predicates.uniqueness_ems")

    _attrs_to_update_combine = ("refuse_links", "_UI_Spec_Defaults")

    _UI_Spec_Defaults     = dict \
        ( show_in_admin   = False
        )

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class _A_Change_ (A_Rev_Ref) :
            """Creation change of the object"""

            P_Type             = "MOM.MD_Change"
            Ref_Type           = P_Type
            ref_name           = "pid"
            hidden             = False
            hidden_nested      = 1
            q_able             = True

        # end class _A_Change_

        class created_by (A_Id_Entity) :
            """User that created the entity"""

            kind               = Attr.Computed
            P_Type             = "MOM.Id_Entity"

            def computed (self, obj) :
                cc = obj.creation
                if cc is not None :
                    result = cc.c_user
                    if isinstance (result, pyk.int_types) :
                        try :
                            result = obj.home_scope.pid_query (result)
                        except Exception :
                            return
                    return result
            # end def computed

        # end class created_by

        class creation (_A_Change_) :
            """Creation change of the object"""

            sqx_filter         = (Q.kind == "Create")

        # end class creation

        class creation_date (A_Date_Time) :
            """Date/time of creation."""

            kind               = Attr.Computed

            def computed (self, obj) :
                cc = obj.creation
                if cc is not None :
                    return cc.c_time
            # end def computed

        # end class creation_date

        class electric (A_Boolean) :
            """Indicates if object/link was created automatically or not."""

            kind               = Attr.Internal
            default            = False
            hidden             = True

        # end class electric

        class is_used (A_Int) :
            """Specifies whether entity is used by another entity."""

            kind               = Attr.Cached
            default            = 1

        # end class is_used

        class last_change (_A_Change_) :
            """Last change of the object"""

            finished_query     = A_Rev_Ref.finished_query_first
            sort_key           = TFL.Sorted_By ("-cid")

        # end class last_change

        class last_changed (A_Date_Time) :
            """Date/time of last change."""

            kind               = Attr.Computed

            def computed (self, obj) :
                lc = obj.last_change
                if lc is not None :
                    return lc.time
            # end def computed

        # end class last_changed

        class last_changed_by (A_Id_Entity) :
            """User that applied the last change."""

            kind               = Attr.Computed
            P_Type             = "MOM.Id_Entity"

            def computed (self, obj) :
                lc = obj.last_change
                if lc is not None :
                    result = lc.user
                    if isinstance (result, pyk.int_types) :
                        try :
                            result = obj.home_scope.pid_query (result)
                        except Exception :
                            return
                    return result
            # end def computed

        # end class last_changed_by

        class last_cid (A_Int) :
            """Change id of last change for this entity."""

            kind               = Attr.Internal
            default            = 0
            hidden_nested      = 1
            record_changes     = False
            use_index          = True

        # end class last_cid

        class pid (A_Surrogate) :
            """Permanent id of the instance."""

            explanation        = """
                The `pid` is unique over all entities in a given scope. Once
                created, the `pid` of an instance never changes and is not ever
                reused for a different instance.

                The `pid` remains unchanged during database migrations.
            """

            hidden_nested      = 1

        # end class pid

        class type_name (A_String) :
            """Name of type of this entity."""

            kind               = Attr.Internal
            Kind_Mixins        = (Attr._Type_Name_Mixin_, )
            hidden_nested      = 1
            max_length         = 0

        # end class type_name

        class ui_repr (_Ancestor.ui_repr) :

            def computed (self, obj) :
                return "%s %s" % \
                    (obj.type_name, portable_repr (obj.epk_raw [:-1]))
            # end def computed

        # end class ui_repr

        class x_locked (A_Boolean) :
            """Specifies if object can be changed by user"""

            kind               = Attr.Internal
            default            = False
            hidden             = True
            q_able             = False

        # end class x_locked

    # end class _Attributes

    class _Predicates (_Ancestor_Essence._Predicates) :

        class completely_defined (Pred.Condition) :
            """All necessary attributes must be defined."""

            kind          = Pred.System
            guard         = "is_used"
            guard_attr    = ("is_used", )

            def eval_condition (self, obj, glob_dict, val_dict) :
                result = []
                add    = result.append
                for a in obj.necessary :
                    if not a.has_substance (obj) :
                        m = _T ("Necessary attribute %s is not defined") % (a, )
                        add (m)
                self._error_info.extend (result)
                return not result
            # end def eval_condition

        # end class completely_defined

        class object_correct (Pred.Condition) :
            """All object invariants must be satisfied."""

            kind          = Pred.System

            def eval_condition (self, obj, glob_dict, val_dict) :
                result = []
                add    = result.append
                for p in obj._pred_man.errors ["object"] :
                    add (str (p))
                self._error_info.extend (result)
                return not result
            # end def eval_condition

        # end class object_correct

    # end class _Predicates

    @TFL.Meta.Once_Property
    def ETM (self) :
        """E_Type_Manager managing `self`."""
        return self.home_scope [self.type_name]
    # end def ETM

    @TFL.Meta.Once_Property
    def epk (self) :
        """Essential primary key as tuple of cooked values."""
        return tuple \
            (a.get_value (self) for a in self.primary) + (self.type_name,)
    # end def epk

    @property
    def epk_as_code (self) :
        def _conv (tup) :
            if len (tup) == 1 :
                tup += ("", )
            for t in tup :
                if isinstance (t, tuple) :
                    if len (t) == 1 :
                        t += ("", )
                    t = "(%s)" % (", ".join (_conv (t)))
                yield t
        def _gen () :
            for a in self.primary :
                r = a.as_code (a.get_value (self))
                if isinstance (r, tuple) :
                    r = "(%s)" % (", ".join (_conv (r)))
                yield r
        try :
            result = tuple (_gen ())
        except Exception :
            result = ("...", )
        return result
    # end def epk_as_code

    @TFL.Meta.Once_Property
    def epk_as_dict (self) :
        """Dictionary of values in :attr:`epk`."""
        return dict (zip (self.epk_sig, self.epk))
    # end def epk_as_dict

    @property
    def epk_raw (self) :
        """Essential primary key as tuple of raw values."""
        return \
            ( tuple (a.get_raw_epk (self) for a in self.primary)
            + (self.type_name, )
            )
    # end def epk_raw

    @property
    def epk_raw_pid (self) :
        """Essential primary key as tuple of raw values
           but pids for Id_Entity attributes.
        """
        return \
            ( tuple (a.get_raw_pid (self) for a in self.primary)
            + (self.type_name, )
            )
    # end def epk_raw

    @property
    def errors (self) :
        return iter (self._pred_man)
    # end def errors

    @property
    def has_errors (self) :
        return self._pred_man.has_errors
    # end def has_errors

    @property
    def has_warnings (self) :
        return self._pred_man.has_warnings
    # end def has_warnings

    @property
    def SCM_Change_Attr (self) :
        return MOM.SCM.Change.Attr
    # end def SCM_Change_Attr

    @property
    def ui_display_format (self) :
        """Format used for :attr:`ui_display`."""
        return self.ui_display_sep.join \
            ( "%%(%s)s" % a.name for (a, v) in zip (self.primary, self.epk)
              if a.has_substance (self)
            )
    # end def ui_display_format

    @TFL.Meta.Class_and_Instance_Once_Property
    def UI_Spec (soc) :
        try :
            UI_Spec_module = soc.PNS._Import_Module ("UI_Spec")
        except ImportError :
            pass
        else :
            try :
                UI_Spec    = UI_Spec_module.UI_Spec
            except AttributeError :
                pass
            else :
                defaults   = soc._UI_Spec_Defaults
                try :
                    result = getattr (UI_Spec, soc.type_base_name)
                except AttributeError :
                    result = dict (defaults)
                    setattr (UI_Spec, soc.type_base_name, result)
                else :
                    show_in_admin = result.get ("show_in_admin", True)
                    for k in defaults :
                        if k not in result :
                            result [k] = defaults [k]
                    result ["show_in_admin"] = show_in_admin
                return result
    # end def UI_Spec

    def add_error (self, err, kind = "object") :
        """Add `err` to error-list of predicate manager"""
        self._pred_man.errors [kind].append (err)
    # end def add_error

    def all_links (self) :
        return sorted \
            ( self.all_referrers ()
            , key = self.home_scope.MOM.Id_Entity.sort_key_pm ()
            )
    # end def all_links

    def all_referrers (self) :
        """Return query set of all entities that refer to `self`."""
        scope = self.home_scope
        def _gen (self, ref_map, scope) :
            pid = self.pid
            for ET, attrs in pyk.iteritems (ref_map) :
                qfs = tuple ((getattr (Q, a) == pid) for a in attrs)
                ETM = scope [ET.type_name]
                yield ETM.query (Q.OR (* qfs)).distinct ()
        return scope.ems.Q_Result_Composite \
            ( tuple (_gen (self, self.__class__.Ref_Req_Map, scope))
            + tuple (_gen (self, self.__class__.Ref_Opt_Map, scope))
            )
    # end def all_referrers

    def async_changes (self, * filter, ** kw) :
        """Changes that happened asynchronously since `self` was last read from
           database.
        """
        result = self.home_scope.query_changes \
            (Q.cid > self.last_cid, Q.pid == self.pid)
        if filters or kw :
            result = result.filter (* filters, ** kw)
        return result
    # end def async_changes

    def as_migration (self) :
        """Migration of `self`."""
        def _gen (self) :
            skip = set (("last_cid", "pid", "type_name"))
            for ak in self.db_attr :
                if not (ak.is_primary or ak.name in skip) :
                    yield ak.name, ak.get_raw_epk (self)
        return (self.epk_raw, dict (_gen (self)))
    # end def as_migration

    def as_pickle_cargo (self) :
        """Pickle cargo of `self`."""
        return (str (self.type_name), self.as_attr_pickle_cargo (), self.pid)
    # end def as_pickle_cargo

    def attr_as_code (self) :
        eas    = self.epk_as_code
        aas    = (self.__super.attr_as_code (), )
        result = ", ".join (eas + aas)
        if "," not in result :
            result += ","
        return result
    # end def attr_as_code

    def changes (self, * filters, ** kw) :
        """Return change objects for `self` that match `filters` and `kw`."""
        result = self.home_scope.query_changes (Q.pid == self.pid)
        if filters or kw :
            result = result.filter (* filters, ** kw)
        return result
    # end def changes

    def check_all (self) :
        """True if all predicates are satisfied."""
        return self._pred_man.check_all (self)
    # end def check_all

    def copy (self, * new_epk, ** kw) :
        """Make copy with primary key `new_epk`."""
        scope  = self.home_scope
        etype  = self.__class__
        result = etype (* new_epk, scope = scope, ** kw)
        with scope.nested_change_recorder \
                 (MOM.SCM.Change.Copy, result) as change :
            scope.add (result)
            change.pid = result.pid
            raw_kw     = dict \
                (  (a.name, a.get_raw (self))
                for a in self.user_attr if a.name not in kw and a.to_save (self)
                )
            if raw_kw :
                result.set_raw (** raw_kw)
        return result
    # end def copy

    def correct_unknown_attr (self, error) :
        """Try to correct an unknown attribute error."""
        pass
    # end def correct_unknown_attr

    def destroy (self) :
        """Remove entity from `home_scope`."""
        if self._home_scope :
            if self is self.home_scope.root :
                self.home_scope.destroy ()
            else :
                self.home_scope.remove (self)
    # end def destroy

    def destroy_dependency (self, other) :
        for attr in self.object_referring_attributes.pop (other, ()) :
            if attr.is_required :
                self.destroy ()
            elif attr.is_primary :
                ### resetting a primary attribute means a rename operation
                self.set (** {attr.name : None})
            else :
                old = attr.get_value   (self)
                raw = attr.get_raw_pid (self)
                attr.reset (self)
                if old != attr.get_value (self) :
                    self.record_attr_change ({attr.name : raw})
        if self and other in self.dependencies :
            del self.dependencies [other]
    # end def destroy_dependency

    @classmethod
    def example_attrs (cls, full = False) :
        attrs = itertools.chain \
            (cls.primary, cls.user_attr if full else cls.required)
        return dict ((a.name, a.example) for a in attrs)
    # end def example_attrs

    @classmethod
    def epk_as_kw (cls, * epk, ** kw) :
        """Dictionary with values of `epk` and values of `kw`"""
        on_error = kw.pop ("on_error", None)
        if epk and isinstance (epk [-1], cls.Type_Name_Type) :
            epk  = epk [:-1]
        return dict (cls.args_as_kw (* epk, ** kw), on_error = on_error)
    # end def epk_as_kw

    @classmethod
    def epkified (cls, * epk, ** kw) :
        """Return `epk` tuple and `kw` dictionary, no matter if `epk` values
           were passed as positional or named arguments.
        """
        if epk and isinstance (epk [-1], cls.Type_Name_Type) :
            epk  = epk [:-1]
        raw      = bool (kw.get ("raw", False))
        epkifier = (cls.epkified_ckd, cls.epkified_raw) [raw]
            ### `epkified_ckd` and `epkified_raw` are created by meta machinery
        try :
            return epkifier (* epk, ** kw)
        except TypeError as exc :
            on_error = kw.pop ("on_error", None) or cls._raise_attr_error
            needed   = tuple (m.name for m in cls.primary_required)
            missing  = tuple (p for p in needed [len (epk):] if p not in kw)
            if missing :
                error = MOM.Error.Required_Missing \
                    (cls, needed, missing, epk, kw, "primary")
                on_error (error)
                raise error
            else :
                raise TypeError \
                    ( _T ("%s needs the arguments %s, got %s instead")
                    % (cls.ui_name_T, needed, portable_repr (epk))
                    )
    # end def epkified

    def is_defined (self)  :
        """True if all necessary attributes have substance."""
        return \
            (  (not self.is_used)
            or all (a.has_substance (self) for a in self.necessary)
            )
    # end def is_defined

    def is_g_correct (self)  :
        """True if all system predicates are satisfied."""
        ews = self._pred_man.check_kind ("system", self)
        return not ews
    # end def is_g_correct

    @TFL.Meta.Class_and_Instance_Method
    def is_locked (soc) :
        return soc.x_locked or soc.electric
    # end def is_locked

    def notify_dependencies_destroy (self) :
        """Notify all entities registered in `self.dependencies` and
           `self.object_referring_attributes` about the destruction of `self`.
        """
        ### Use `list` because dictionaries are changed inside loop
        for d in list (self.dependencies) :
            d.destroy_dependency (self)
        for o in list (self.object_referring_attributes) :
            o.destroy_dependency (self)
    # end def notify_dependencies_destroy

    def register_dependency (self, other) :
        """Register that `other` depends on `self`"""
        self.dependencies [other] += 1
    # end def register_dependency

    def restore (self, * epk, ** kw) :
        """Restore an object that was destroyed before but not committed."""
        if not (self.pid and self.home_scope) :
            raise TypeError \
                ("%r: pid %r, scope %r" % (self, self.pid, self.home_scope))
        self.init_finished  = False
        self._init_pending  = []
        self.__init__         (* epk, ** kw)
        self.home_scope.add   (self, pid = self.pid)
        return self
    # end def restore

    def unregister_dependency (self, other) :
        """Unregister dependency of `other` on `self`"""
        deps = self.dependencies
        deps [other] -= 1
        if deps [other] <= 0 :
            del deps [other]
    # end def unregister_dependency

    def user_diff (self, other, ignore = ()) :
        """Return differences in user attributes between `self` and `other`."""
        result = {}
        undef  = TFL.Undef ()
        if ignore :
            ignore = set (ignore)
        if self.type_name != other.type_name :
            result ["type_name"] = (self.type_name, other.type_name)
        pc_s = self.as_attr_pickle_cargo  ()
        pc_o = other.as_attr_pickle_cargo ()
        for k in set (pc_s).union (pc_o) :
            if k in ignore :
                continue
            p = pc_s.get (k, undef)
            q = pc_o.get (k, undef)
            if p != q :
                result [k] = \
                    ( p if p is not undef else "<Missing>"
                    , q if q is not undef else "<Missing>"
                    )
        return result
    # end def user_diff

    def user_equal (self, other) :
        """Compare `self` and `other` concerning user attributes."""
        return \
            (   self.type_name               == other.type_name
            and self.as_attr_pickle_cargo () == other.as_attr_pickle_cargo ()
            )
    # end def user_equal

    def _destroy (self) :
        self.notify_dependencies_destroy ()
    # end def _destroy

    def _extract_primary (self, kw) :
        result = {}
        for pka in self.primary :
            name      = pka.name
            role_name = getattr (pka, "role_name", None)
            if name in kw :
                result [name] = kw.pop (name)
            elif role_name and role_name in kw :
                result [name] = kw.pop (role_name)
        return result
    # end def _extract_primary

    def _extract_primary_ckd (self, kw) :
        new_epk  = []
        pkas_ckd = self._extract_primary (kw)
        pkas_raw = {}
        for pka in self.primary :
            name = pka.name
            if name in pkas_ckd :
                w               = pkas_ckd      [name]
                v               = pka.cooked    (w)
                pkas_raw [name] = pka.as_string (w)
            else :
                v = getattr (self, name)
            new_epk.append (v)
        return new_epk, pkas_raw, pkas_ckd
    # end def _extract_primary_ckd

    def _extract_primary_raw (self, kw) :
        new_epk  = []
        pkas_ckd = {}
        pkas_raw = self._extract_primary (kw)
        for pka in self.primary :
            name = pka.name
            if name in pkas_raw :
                pkas_ckd [name] = v = pka.from_string (pkas_raw [name], self)
            else :
                v = getattr (self, name)
            new_epk.append (v)
        return new_epk, pkas_raw, pkas_ckd
    # end def _extract_primary_raw

    def _init_epk (self, epk) :
        return ((a.name, pka) for a, pka in zip (self.primary, epk))
    # end def _init_epk

    def _init_meta_attrs (self) :
        self.__super._init_meta_attrs ()
        self.dependencies                = TFL.defaultdict (int)
        self.object_referring_attributes = TFL.defaultdict (list)
    # end def _init_meta_attrs

    @staticmethod
    def _json_encode (o) :
        return dict (display = o.FO, pid = o.pid)
    # end def _json_encode

    def _main__init__ (self, * epk, ** kw) :
        ### `epk_as_kw` needs to raise errors to avoid follow-up errors
        ### --> override `on_error` in `kw` when calling `epk_as_kw`
        self.implicit = kw.pop ("implicit", False)
        raw           = bool (kw.pop ("raw", self._init_raw_default))
        akw           = self.epk_as_kw (* epk, ** dict (kw, on_error = None))
        ukw           = dict (self._kw_undeprecated (akw))
        pkw           = self._kw_polished (ukw) if raw else ukw
        checker       = \
            (  self._kw_raw_check_predicates
            if raw else self._kw_check_predicates
            )
        setter        = self.__super._set_raw if raw else self.__super._set_ckd
            ### Need to use `__super.` methods here because it's not a `rename`
        try :
            epk, pkw = self.epkified (raw = raw, ** pkw)
            self._kw_check_required (* epk, ** pkw)
        except MOM.Error.Required_Missing as exc :
            self._pred_man.missing_required = exc
            pkw.update (self._init_epk (epk))
            checker (** pkw)
            raise MOM.Error.Invariants (self._pred_man)
        pkw.update (self._init_epk (epk))
        setter (_pred_kinds = ("object_init", "object"), ** pkw)
        required_errors = self._pred_man.required_errors
        if required_errors :
            raise MOM.Error.Invariants (self._pred_man)
    # end def _main__init__

    def _rename (self, new_epk, pkas_raw, pkas_ckd) :
        diffs = sum ((n != o) for n, o in paired (new_epk, self.epk [:-1]))
        if diffs :
            def _renamer () :
                attributes = self.attributes
                for k, v in pyk.iteritems (pkas_ckd) :
                    attr = attributes [k]
                    attr._set_cooked_inner (self, v)
                    attr._set_raw_inner    (self, pkas_raw [k], v)
                self._reset_epk ()
            self._kw_check_predicates (on_error = None, ** pkas_ckd)
            self.home_scope.rename    (self, tuple (new_epk), _renamer)
        return diffs
    # end def _rename

    def _repr (self, type_name) :
        return "%s (%s)" % (type_name, ", ".join (self.epk_as_code))
    # end def _repr

    def _reset_epk (self) :
        sd = self.__dict__
        for a in ("epk", "epk_as_dict") :
            if a in sd :
                delattr (self, a)
    # end def _reset_epk

    def _set_ckd (self, _pred_kinds = None, on_error = None, ** kw) :
        result = 0
        if kw :
            new_epk, pkas_raw, pkas_ckd = self._extract_primary_ckd (kw)
            if pkas_ckd and tuple (new_epk) != self.epk [:-1] :
                result += self._rename (new_epk, pkas_raw, pkas_ckd)
            result += self.__super._set_ckd (_pred_kinds, on_error, ** kw)
        return result
    # end def _set_ckd

    def _set_raw (self, _pred_kinds = None, on_error = None, ** kw) :
        result = 0
        if kw :
            new_epk, pkas_raw, pkas_ckd = self._extract_primary_raw (kw)
            if pkas_ckd and tuple (new_epk) != self.epk [:-1] :
                result += self._rename (new_epk, pkas_raw, pkas_ckd)
            result += self.__super._set_raw (_pred_kinds, on_error, ** kw)
        return result
    # end def _set_raw

    def __eq__ (self, rhs) :
        if isinstance (rhs, pyk.int_types) or \
           (   isinstance (rhs, TFL.Q_Result._Attr_)
           and isinstance (rhs._VALUE, pyk.int_types)
           ) :
            return self.pid == rhs
        elif isinstance (rhs, pyk.string_types) :
            try :
                pid = int (rhs)
            except (ValueError, TypeError) :
                return False
            else :
                return self.pid == pid
        else :
            try :
                rhs = (rhs.pid, rhs.home_scope.guid)
            except AttributeError :
                pass
            return (self.pid, self.home_scope.guid) == rhs
    # end def __eq__

    def __ne__ (self, rhs) :
        return not (self == rhs)
    # end def __ne__

    def __hash__ (self) :
        return hash ((self.pid, self.home_scope.guid))
    # end def __hash__

    def __setattr__ (self, name, value) :
        ### If an attribute descriptor's `__get__` does not return `self`
        ### when accessed via the class it's `__set__` won't be used by Python
        ### --> call it manually here, instead
        try :
            attr = self.attributes [name]
        except KeyError :
            return self.__super.__setattr__ (name, value)
        else :
            attr.__set__ (self, value)
    # end def __setattr__

    def __str__ (self) :
        epk = self.epk
        if len (epk) == 1 :
            format = "%s"
        else :
            format = "(%s)"
        return format % (", ".join (self.epk_as_code))
    # end def __str__

# end class Id_Entity

class _Id_Entity_Mixin_ (object) :

    def __setattr__ (self, name, value) :
        ### Avoid `Id_Entity.__setattr__` triggering infinite recursion
        object.__setattr__ (self, name, value)
    # end def __setattr__

# end class _Id_Entity_Mixin_

class _Id_Entity_Reload_Mixin_ (_Id_Entity_Mixin_) :
    """Mixin triggering a reload from the database on any attribute access."""

    def __getattribute__ (self, name) :
        if name in ("__class__", ) :
            return object.__getattribute__ (self, name)
        else :
            cls    = object.__getattribute__ (self, "__class__")
            reload = cls._RELOAD_INSTANCE
            e_type = cls._RESTORE_CLASS (self)
            reload (self, e_type)
            return getattr (self, name)
    # end def __getattribute__

    @classmethod
    def _RELOAD_INSTANCE (cls, self, e_type) :
        raise TypeError \
            ( "%s needs to implement _RELOAD_INSTANCE"
            % self.__class__.__bases__ [0]
            )
    # end def _RELOAD_INSTANCE

    @classmethod
    def _RESTORE_CLASS (cls, self) :
        result = self.__class__ = cls.__bases__ [2]
        return result
    # end def _RESTORE_CLASS

    @classmethod
    def define_e_type (cls, e_type, mixin) :
        e_type._RELOAD_E_TYPE = e_type.New \
            ( "_Reload"
            , head_mixins = (mixin, cls)
            )
    # end def define_e_type

# end class _Id_Entity_Reload_Mixin_

@pyk.adapt__bool__
class _Id_Entity_Destroyed_Mixin_ (_Id_Entity_Mixin_) :
    """Mixin indicating an entity that was already destroyed."""

    def __getattribute__ (self, name) :
        if name in ("E_Type", "__bool__", "__class__", "__nonzero__", "__repr__") :
            return object.__getattribute__ (self, name)
        elif name in ("last_cid", "pid", "type_name") :
            try :
                ### Need to reset `self.__class__` temporarily to allow
                ### properties to run
                cls            = self.__class__
                self.__class__ = cls.__bases__ [1]
                result         = getattr (self, name)
            finally :
                self.__class__ = cls
            return result
        elif name == "restore" :
            cls = self.__class__
            self.__class__ = cls.__bases__ [1]
            return getattr (self, name)
        elif name == "destroy_dependency" :
            return lambda s : True
        else :
            raise MOM.Error.Destroyed_Entity \
                ( "%r: access to attribute %r not allowed"
                % (self, name)
                )
    # end def __getattribute__

    @classmethod
    def define_e_type (cls, e_type) :
        e_type._DESTROYED_E_TYPE = type (cls) \
            (str (e_type.type_base_name + "_Destroyed"), (cls, e_type), {})
    # end def define_e_type

    def __bool__ (self) :
        return False
    # end def __bool__

    def __repr__ (self) :
        ### Need to reset `self.__class__` temporarily to get proper `__repr__`
        try :
            cls            = self.__class__
            self.__class__ = cls.__bases__ [1]
            result = "<Destroyed entity %s>" % (self.__repr__ (), )
        finally :
            self.__class__ = cls
        return result
    # end def __repr__

# end class _Id_Entity_Destroyed_Mixin_

class MD_Entity (TFL.Meta.BaM (Entity, metaclass = MOM.Meta.M_MD_Entity)) :
    """Root class for meta-data entities, e.g., entities recording changes to
       the object model.
    """

    has_identity          = True
    is_locked             = True
    is_partial            = True
    record_changes        = False
    sorted_by             = TFL.Sorted_By ()
    x_locked              = True
    _sig_attr_names       = ()

    def _main__init__ (self, * args, ** kw) :
        pass
    # end def _main__init__

    def _repr (self, type_name) :
        return u"%s" % (type_name, )
    # end def _repr

# end class MD_Entity

_Ancestor_Essence = MD_Entity

class MD_Change (_Ancestor_Essence) :
    """Meta-data about changes of the object model."""

    record_changes        = False
    sorted_by             = TFL.Sorted_By ("-cid")
    spk                   = TFL.Meta.Alias_Property ("cid")
    spk_attr_name         = "cid" ### Name of `surrogate primary key` attribute
    use_indices           = [("type_name", "-cid")]
    _sig_attr_names       = ("kind", "time", "user")

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class _Derived_Attr_ (A_Attr_Type) :

            class _Sync_Change_ (Attr.Kind) :

                def _set_cooked_value_inner \
                        (self, obj, value, old_value = None) :
                    setattr (obj.scm_change, self.scm_name, value)
                # end def _set_cooked_value_inner

                def reset (self, obj) :
                    pass
                # end def reset

            # end class _Sync_Change_

            kind               = Attr.Internal
            Kind_Mixins        = (_Sync_Change_, Attr._Computed_Mixin_)
            hidden_nested      = 2
            record_changes     = False

            def computed (self, obj) :
                return getattr (obj.scm_change, self.scm_name, None)
            # end def computed

            @property
            def scm_name (self) :
                return self.name
            # end def scm_name

        # end class _Derived_Attr_

        class cid (_Derived_Attr_, A_Surrogate) :
            """Change id."""

            hidden_nested      = 1

        # end class cid

        class c_time (_Derived_Attr_, A_Date_Time) :
            """Creation date and time (only for creation changes)."""

        # end class c_time

        class c_user (_Derived_Attr_, A_Id_Entity) :
            """User that triggered the creation change, if known."""

            P_Type             = "MOM.Id_Entity"
            only_e_types       = ("Auth.Account", "PAP.Person")

        # end class c_user

        class parent (A_Int) :

            kind               = Attr.Query
            hidden_nested      = 1
            query              = Q.parent_cid

        # end class parent

        class parent_cid (_Derived_Attr_, A_Int) :
            """Cid of parent change, if any."""

            hidden_nested      = 1
            use_index          = True

            def computed (self, obj) :
                parent = obj.scm_change.parent
                if parent is not None :
                    return parent.cid
            # end def computed

        # end class parent_cid

        class kind (_Derived_Attr_, A_String) :
            """Kind of change"""

            max_length         = 10

        # end class kind

        class pid (_Derived_Attr_, A_Int) :
            """Permanent id of the entity that was changed, if any."""

            hidden_nested      = 1
            use_index          = True

        # end class pid

        class scm_change (A_Blob) :
            """SCM.Change instance describing the change."""

            kind               = Attr.Internal
            record_changes     = False

            class Pickler (TFL.Meta.Object) :

                Type = _A_Binary_String_

                @classmethod
                def as_cargo (cls, attr_kind, attr_type, value) :
                    if value is not None :
                        return value.as_pickle ()
                # end def as_cargo

                @classmethod
                def from_cargo (cls, scope, attr_kind, attr_type, cargo) :
                    if cargo is not None :
                        return MOM.SCM.Change._Change_.from_pickle (cargo)
                # end def from_cargo

            # end class Pickler

        # end class scm_change

        class time (_Derived_Attr_, A_Date_Time) :
            """Date and time of the change."""

        # end class time

        class type_name (_Derived_Attr_, A_String) :
            """Name of type of the entity that was changed, if any."""

            hidden_nested      = 1

        # end class type_name

        class user (_Derived_Attr_, A_Id_Entity) :
            """User that triggered the change, if known."""

            P_Type             = "MOM.Id_Entity"
            only_e_types       = ("Auth.Account", "PAP.Person")

        # end class user

    # end class _Attributes

    def __init__ (self, scm_change) :
        self.__super.__init__ ()
        self.scm_change = scm_change
    # end def __init__

    @property
    def ui_display_format (self) :
        return self.ui_display_sep.join \
            ( "%%(%s)s" % a.name for a in self.sig_attr
            if a.get_value (self) not in (None, "")
            )
    # end def ui_display_format

    def _repr (self, type_name) :
        return u"%s [%s]: %s, %s, %s" % \
            (type_name, self.kind, self.cid, self.time, self.pid)
    # end def _repr

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        return getattr (self.scm_change, name)
    # end def __getattr__

# end class MD_Change

### «text» ### start of documentation

Id_Entity.__doc_attr_head__ = """
    `MOM.Id_Entity` provides the framework for defining essential classes and
    associations. Each essential class or association is characterized by

    - `essential attributes`_

    - `essential predicates`_

    - `class attributes`_

    - `methods`_

    Each instance of `Id_Entity` has a attribute :attr:`home_scope` that
    refers to the :class:`~_MOM.Scope.Scope` in which the instance lives.

    `Id_Entity` is normally not directly used as a base class. Instead,
    `Id_Entity`'s subclasses :class:`~_MOM.Object.Object` and
    :class:`~_MOM.Link.Link` serve as root classes for the hierarchies
    of essential classes and associations, respectively.

    .. _`essential attributes`:

    **Essential Attributes**

    Essential attributes are defined inside the class `_Attributes`
    that is nested in `Id_Entity` (or one of its derived classes).

    Any essential class derived (directly or indirectly) from `Id_Entity`
    needs to define a `_Attributes` class that's derived from its
    ancestors `_Attributes`. The top-most `_Attributes` class is
    derived from :class:`MOM.Attr.Spec<_MOM._Attr.Spec.Spec>`.

    Each essential attribute is defined by a class derived from one of
    the attribute types in :mod:`MOM.Attr.Type<_MOM._Attr.Type>`.
"""

Id_Entity.__doc_attr_tail__ = """
    Each essential type provides introspective properties specifying the
    various categories of essential attributes defined for the type:

    .. attribute:: db_attr

      All attributes stored in the database

    .. attribute:: edit_attr

      All editable attributes

    .. attribute:: id_entity_attr

      All attributes referring to instances of :class:`Id_Entity`

    .. attribute:: link_ref_attr

      All query attributes containing links to the essential type

    .. attribute:: primary

      All attributes that are part of the essential primary key

    .. attribute:: primary_optional

      All optional attributes that are part of the essential primary key

    .. attribute:: primary_required

      All required attributes that are part of the essential primary key

    .. attribute:: q_able

      All attributes that can be used in query expressions

    .. attribute:: rev_ref_attr

      All query attributes containing reverse references to the essential type

    .. attribute:: surrogate_attr

      All attributes containing surrogate keys

    .. attribute:: ui_attr

     All attributes accessible in a user interface (not all of these are
     editable)

    .. attribute:: user_attr

      All editable attributes except for the ones listed by :attr:`primary`

"""

Id_Entity.__doc_pred_head__ = """
    .. _`essential predicates`:

    **Essential Predicates**

    Essential predicates are defined inside the class `_Predicates` that
    is nested in `Id_Entity` (or one of its derived classes).

    Any essential class derived (directly or indirectly) from `Id_Entity`
    needs to define a `_Predicates` class that's derived from its
    ancestors `_Predicates`. The top-most `_Predicates` class is
    derived from :class:`MOM.Pred.Spec<_MOM._Pred.Spec.Spec>`.

    Each essential predicate is defined by a class derived from one of
    the predicate types in :mod:`MOM.Pred.Type<_MOM._Pred.Type>`.

    `MOM.Id_Entity` defines two predicates that should not be overriden by
    descendant classes:

    - completely_defined

    - object_correct

    Please note that these two predicates are *not* to be used as examples
    of how predicates should be defined. Normally, predicates define
    `assertion`, not `eval_condition`! This is explained in more detail in
    :mod:`MOM.Pred.Type<_MOM._Pred.Type>`.

"""

Id_Entity.__doc_pred_tail__ = """

    .. _`class attributes`:

    **Class Attributes**

    `MOM.Id_Entity` provides a number of class attributes that control various
    aspects of the use of an essential class by the framework.

    .. attribute:: default_child

      Specifies which child of a partial class should be used by the UI by
      default. The value of this attribute is set for the partial class by
      one specific derived class.

    .. attribute:: deprecated_attr_names

      This is a dictionary that maps deprecated names
      of attributes to the currently preferred names (this is used to
      allow the reading of older databases without loss of information).

    .. attribute:: home_scope

      The scope to which the entity belongs.

    .. attribute:: is_partial

      Specifies if objects/links can be created for the essential
      class in question.

      `is_partial` must be explicitly set to `True` for each essential
      class that doesn't allow the creation of objects or links. If
      `is_partial` isn't defined for a class, `False` is assumed.

    .. attribute:: max_count

      Restricts the number of instances that can be created.

    .. attribute:: PNS

      The package namespace in which this class is defined.

      Ideally, each package namespace defining essential classes defines a
      common root for these, e.g., `SPN.Entity`, that defines
      `PNS`, e.g., ::

          class _SPN_Entity_ (MOM.Id_Entity) :

              _real_name = "Entity"

              PNS = SPN
              ...

    .. attribute:: recordable_attrs

      Set of attributes stored in the database for the entity.

    .. attribute:: record_changes

      Changes of the entity will only be recorded if `record_changes` is True.

    .. attribute:: refuse_links

      This is a set of (names of) classes that must not be linked
      to instances of the essential class in question. This can be used if
      objects of a derived class should not participate in associations of
      a base class.

    .. attribute:: show_in_ui

      Class is shown in the UI only if `show_in_ui` is True.

      `show_in_ui` is not inherited --- it must be set to `False` for every
      single class that shouldn't be shown in the UI. Alternatively, a class
      can set `show_in_ui_T` to False to force its descendents `show_in_ui` to
      `False`.

      The meta machinery modifies `show_in_ui` by combining it with
      `record_changes`.

    .. attribute:: show_package_prefix

      Specifies whether the class name should be prefixed by the name of
      the package namespace in the UI.

    .. attribute:: tutorial

      Describes why and how to define instances of the essential class and
      is used in step-by-step tutorials.

    .. _`methods`:

    **Methods and Properties**

"""

__doc__  = """

"""

if __name__ != "__main__" :
    MOM._Export ("*", "_Id_Entity_Reload_Mixin_", "_Id_Entity_Destroyed_Mixin_")
### __END__ MOM.Entity
