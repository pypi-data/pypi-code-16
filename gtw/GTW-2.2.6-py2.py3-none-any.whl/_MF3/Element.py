# -*- coding: utf-8 -*-
# Copyright (C) 2014-2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.MF3.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.MF3.Element
#
# Purpose
#    Model elements of MOM Forms
#
# Revision Dates
#    24-Apr-2014 (CT) Creation
#     2-May-2014 (CT) Remove `changeable`;
#                     replaced by `attr.kind.change_forbidden`
#     2-May-2014 (CT) Use `readonly`, not `prefilled`, in
#                     `Field_Entity.__call__`
#     2-May-2014 (CT) Honor `skip` in `elements_transitive`,
#                     `field_elements`, `template_elements`
#     3-May-2014 (CT) Change `_Field_.required` to honor `parent.required`
#     7-May-2014 (CT) Add `MAT.A_Int.mf3_input_widget`
#     7-May-2014 (CT) Add and use `GTW.MF3.Completer`
#     8-May-2014 (CT) Factor `_new_element`, `_Auto_Element`
#     8-May-2014 (CT) Add `attr_map`, `__getitem__` to `_Field_Composite_Mixin_`
#     8-May-2014 (CT) Add `completer_elems`
#     9-May-2014 (CT) Factor `check_sigs`
#    16-May-2014 (CT) Redefine `Field_Entity.collapsed`
#     4-Jun-2014 (CT) Split `id` into `bare_id` and `index`
#     4-Jun-2014 (CT) Add and use `_pop_to_self_`
#     7-Jun-2014 (CT) Add `Field_Rev_Ref`
#     8-Jun-2014 (CT) Add `Entity_Rev_Ref`
#    11-Jun-2014 (CT) Factor `_Field_Base_`
#    11-Jun-2014 (CT) Fix `id` and `__getitem__` for `Entity_Rev_Ref`,
#                     `Field_Rev_Ref`
#    14-Jun-2014 (CT) Add `Field_Rev_Ref.add`
#    14-Jun-2014 (CT) Add support for `Entity_Rev_Ref` to `_Entity_.__getitem__`
#    16-Jun-2014 (CT) Factor `_Field_Entity_Mixin_`
#    17-Jun-2014 (CT) Add `populate_new`, `reset_once_properties`
#    17-Jun-2014 (CT) Add `.index` to `sig`
#    18-Jun-2014 (CT) Factor `_Entity_Mixin_.as_json_cargo`,
#                     `.checkers_as_json_cargo`, `.completers_as_json_cargo`,
#                     `.entity_elements`, `.sigs_as_json_cargo`,
#                     and `.submitted_value`
#    18-Jun-2014 (CT) Redefine `Entity_Rev_Ref.ui_display`
#    18-Jun-2014 (CT) Redefine `Field_Ref_Hidden.__call__` and
#                     `.submitted_value`
#    19-Jun-2014 (CT) Factor `cooked` and `init` to `_Field_Entity_Mixin_`
#    19-Jun-2014 (CT) Add `action_buttons`, `Entity_Rev_Ref.edit`
#    27-Jun-2014 (CT) Add `po_index`
#    30-Jun-2014 (CT) Change `Field.__call__` to skip empty, unchanged values
#    30-Jun-2014 (CT) Use `GTW..MF3.Error.List`
#     1-Jul-2014 (CT) Add `_Entity_.label`
#     2-Jul-2014 (CT) Sort `submission_errors` by `po_index`
#     3-Jul-2014 (CT) Factor and redefine `_required_missing_error`
#     3-Jul-2014 (CT) Swap arguments of `_update_element_map`,
#                     redefine `Entity_Rev_Ref._update_element_map`
#     3-Jul-2014 (CT) Change `_Entity_Mixin_.__call__` to consider `required`
#     8-Jul-2014 (CT) DRY `_Entity_.__getitem__`
#    21-Aug-2014 (CT) Set `mf3_template_module` for `A_Time_Interval`  to
#                     `mf3_h_cols`, too
#    21-Aug-2014 (CT) Allow unknown names in `include_rev_refs`
#    27-Aug-2014 (CT) Change `Field_Entity._new_element` to only
#                     set `kw ["skip"]` if `not self.allow_new`
#    27-Aug-2014 (CT) Add `Field_Entity.default_essence`
#    27-Aug-2014 (CT) Use `input_widget`, not `mf3_input_widget`, for MOM.Attr
#    27-Aug-2014 (CT) Add `_Field_Base_.inner_required`
#    29-Aug-2014 (CT) Add `max_rev_ref`, `min_rev_ref` to `Field_Rev_Ref`
#    29-Aug-2014 (CT) Redefine `Entity_Rev_Ref._create_instance` to avoid
#                     some errors due to empty rev-ref sub-form
#                     (does not help against nested empty `Field_Entity`s)
#    30-Aug-2014 (CT) Redefine `_Field_Entity_Mixin_._required_missing_error`
#                     to ignore errors resulting from optional Entity or Rev_Ref
#                     attributes that aren't filled in at all
#     2-Sep-2014 (CT) Add `set_request_defaults`
#     2-Sep-2014 (CT) Fix `change_forbidden` call in `_Field_Base_.readonly`
#     3-Sep-2014 (CT) Add attribute `restrict_completion`
#    25-Sep-2014 (CT) Add `polisher`
#    12-Oct-2014 (CT) Use `TFL.Secure_Hash`
#    22-Jan-2015 (CT) Add `css_class` and `css_align` for `MAT`
#    26-Jan-2015 (CT) Derive `_M_Element_` from `M_Auto_Update_Combined`,
#                     not `M_Auto_Combine_Lists`
#     3-Apr-2015 (CT) Add `_Field_Entity_Mixin_.choices`
#     3-Apr-2015 (CT) Change `Field_Entity.__call__` to handle `pid == -1`
#    13-Apr-2015 (CT) Use `TFL.json_dump.default`
#    16-Apr-2015 (CT) Take default of `max_rev_ref` from `.attr`
#    29-Apr-2015 (CT) Add `record_commit_errors`
#     6-May-2015 (CT) Use `TFL.json_dump.to_string`
#    11-May-2015 (CT) Add `completer_choose_value_iter`
#    15-Jun-2015 (CT) Add all invariants in `_Entity_Mixin_._create_instance`
#                     * remove the guard `not exc.any_required_empty`
#    15-Aug-2015 (CT) Use `@eval_function_body` for scoped setup code
#    20-Dec-2015 (CT) Add properties `aside` and `aside_x` to `_Field_Base_`
#    20-Dec-2015 (CT) Add `syntax` to `_Field_Base_._attr_prop_map`
#    26-Apr-2016 (CT) Add `buddies` to `as_json_cargo`,
#                     factor `cargo_as_json_cargo`
#    22-May-2016 (CT) Add guard `self.required` to `_create_instance`
#    14-Jun-2016 (CT) Change `allow_new` to consider `E_Type.polymorphic_epk`
#    15-Jun-2016 (CT) Fix `ui_display`
#     8-Sep-2016 (CT) Add `Field_Structured`, factor `_Field_Composite_`
#    17-Oct-2016 (CT) Rename `Entity.__call__` to `submit`
#                     + rename `__call__` to `_submit` for:
#                       `_Entity_Mixin_`, `_Field_Composite_`, `Field`,
#                       `Field_Entity`, `Field_Ref_Hidden`, `Field_Rev_Ref`
#    17-Oct-2016 (CT) Factor `Submission`; remove `_submitted_value`...
#    18-Oct-2016 (CT) Add `ui_allow_change`
#                     + Redefine `Field_Entity._change_from_submission` to check
#    19-Oct-2016 (CT) Redefine `Field_Entity._submitted_value_iter`
#                     + Filter empty elements for creation of optional fields
#    ««revision-date»»···
#--

from   __future__               import division, print_function
from   __future__               import absolute_import, unicode_literals

from   _GTW                     import GTW
from   _MOM                     import MOM
from   _TFL                     import TFL

import _GTW._MF3.Completer
import _GTW._MF3.Error
import _GTW._MF3.Polisher
import _GTW._MF3.Submission

from   _MOM.import_MOM          import Q

import _MOM._Attr.Selector
import _MOM._Attr.Type

from   _TFL._Meta.M_Class       import BaM
from   _TFL.portable_repr       import portable_repr
from   _TFL.predicate           import filtered_join, rsplit_hst
from   _TFL.pyk                 import pyk
from   _TFL.Regexp              import Regexp, re

import _TFL._Meta.Object
from   _TFL.Decorator           import eval_function_body, getattr_safe
import _TFL._Meta.M_Auto_Combine_Lists
import _TFL._Meta.Once_Property
import _TFL._Meta.Property
import _TFL.json_dump
import _TFL.Undef

from   itertools                import chain as ichain

import json
import logging

MAT                                     = MOM.Attr

MAT.A_Attr_Type.input_widget            = "mf3_input, string"
MAT.A_Boolean.input_widget              = "mf3_input, boolean"
MAT.A_Confirmation.input_widget         = "mf3_input, boolean"
MAT.A_Date.input_widget                 = "mf3_input, date"
MAT.A_Date_Time.input_widget            = "mf3_input, datetime"
MAT.A_Email.input_widget                = "mf3_input, email"
MAT.A_Enum.input_widget                 = "mf3_input, named_object"
MAT.A_Int.input_widget                  = "mf3_input, integer"
MAT.A_Numeric_String.input_widget       = "mf3_input, number"
MAT.A_Text.input_widget                 = "mf3_input, text"
MAT.A_Url.input_widget                  = "mf3_input, url"
MAT._A_Id_Entity_.input_widget          = "mf3_input, id_entity"
MAT._A_Named_Object_.input_widget       = "mf3_input, named_object"
MAT._A_Named_Value_.input_widget        = "mf3_input, named_value"
MAT._A_Number_.input_widget             = "mf3_input, number"

MAT.A_Attr_Type.mf3_template_macro      = None
MAT.A_Confirmation.mf3_template_macro   = "Field__Confirmation"

MAT.A_Attr_Type.mf3_template_module     = None

MAT.Kind.css_class                      = ""
MAT.A_Attr_Type.css_class               = ""

MAT.A_Attr_Type.css_align               = ""
MAT._A_Number_.css_align                = "right"
MAT.A_Date.css_align                    = "right"
MAT.A_Numeric_String.css_align          = "right"
MAT.A_Time.css_align                    = "right"

@MOM._Add_Import_Callback ("_MOM._Attr.Date_Interval")
def _set_date_interval_templates (module) :
    MOM.Attr.A_Date_Interval.mf3_template_module = "mf3_h_cols"

@MOM._Add_Import_Callback ("_MOM._Attr.Time_Interval")
def _set_time_interval_templates (module) :
    MOM.Attr.A_Time_Interval.mf3_template_module = "mf3_h_cols"

@MOM._Add_Import_Callback ("_MOM._Attr.Range")
def _set_range_template (module) :
    MOM.Attr._A_Range_.mf3_template_module = "mf3_h_cols"

class Delay_Call (BaseException) :
    """Delay call until rev-ref is defined."""
# end class Delay_Call

class _M_Element_ (TFL.Meta.M_Auto_Update_Combined) :
    """Meta class for `_Element_`"""

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        ### get real name (necessary, if `_real_name` was used in class def)
        name = cls.__name__
        if not name.startswith ("_") :
            if "template_macro" not in dct :
                cls.template_macro = name
            root = cls.m_root
            if getattr (root, "_Element_Map_body", None) :
                root._update_element_map (cls)
    # end def __init__

    def __call__ (cls, * args, ** kw) :
        result = cls.__m_super.__call__ (* args, ** kw)
        Entity = result.Entity
        while Entity is not None :
            ### update all `_Element_Map`s up to `root`
            while getattr (Entity, "_Element_Map_body", None) is None :
                Entity = Entity.Parent_Entity
            Entity._update_element_map (result)
            Entity = Entity.Parent_Entity
        return result
    # end def __call__

    @property
    def elements (self) :
        return self._elements
    # end def elements

    @elements.setter
    def elements (self, value) :
        self._elements = value
    # end def elements

    @property
    def id (cls) :
        return cls.bare_id
    # end def id

    ### `m_root` cannot be a `Once_Property` because inheritance
    @property
    def m_root (cls) :
        parent = cls.parent
        return cls if parent is None else parent.m_root
    # end def m_root

    def __repr__ (cls) :
        if cls.bare_id :
            return "<class %s %s>" % (cls.__name__, cls.bare_id)
        return cls.__m_super.__repr__ ()
    # end def __repr__

# end class _M_Element_

class M_Entity (_M_Element_) :
    """Meta class for `_Entity_`."""

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        ### delay construction of `cls._Element_Map` until first call
        ### of `__getitem__`
        ### * `id` of elements is set later by `_add_auto_attributes`
        cls._Element_Map_body = None
    # end def __init__

    @property
    def _Element_Map (cls) :
        return cls.__Element_Map
    # end def _Element_Map

    @property
    def __Element_Map (cls) :
        result = cls._Element_Map_body
        if result is None :
            result = cls._Element_Map_body = {}
            for e in cls.elements_transitive () :
                if e is not cls :
                    cls._update_element_map (e)
        return result
    # end def _Element_Map

    def __getitem__ (cls, key) :
        try :
            return cls.__Element_Map [key]
        except KeyError :
            head, _, tail = rsplit_hst (key, Entity_Rev_Ref.id_sep)
            if head and tail :
                return cls [head] [tail]
            raise
    # end def __getitem__

# end class M_Entity

class M_Entity_Rev_Ref (M_Entity) :
    """Meta class for `Entity_Rev_Ref`"""

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        cls.input_widget = "mf3_input, id_entity"
    # end def __init__

# end class M_Entity_Rev_Ref

class M_Field (_M_Element_) :
    """Meta class for `Field`."""

# end class M_Field

class M_Field_Rev_Ref (M_Field) :
    """Meta class for `Field_Rev_Ref`."""

    def __getitem__ (cls, key) :
        if Entity_Rev_Ref.id_sep in key :
            try :
                return cls.m_root [key]
            except KeyError :
                pass
        return cls.proto [cls.id_sep.join ((cls.name, key))]
    # end def __getitem__

# end class M_Field_Rev_Ref

class _Base_ (TFL.Meta.Object) :
    """Base class of element classes."""

    action_buttons      = ()
    bare_id             = None
    completer           = None
    id_sep              = "."
    index_sep           = "/"
    name                = None
    parent              = None
    pid_sep             = "@"
    polisher            = None
    q_name              = None
    restrict_completion = False
    skip                = False
    submission          = None
    template_module     = "mf3"
    ui_allow_change     = True
    ui_allow_move       = False
    ui_display          = ""
    undef               = TFL.Undef ("value")

    _attrs_uniq_to_update_combine = \
        ("_element_ids", "_reset_properties", "_pop_to_self", "_pop_to_self_")
    _commit_errors      = ()
    _conflicts          = 0
    _elements           = ()
    _element_ids        = ("id", )
    _index              = None
    _pop_to_self        = ("parent", "template_macro", "template_module")
    _pop_to_self_       = ("index", )
    _po_index           = None
    _required           = False
    _reset_properties   = ("template_elements", "po_index")
    _submission_errors  = ()
    _ui_rank            = (0, )

    def __init__ (self, ** kw) :
        pass
    # end def __init__

    @TFL.Meta.Once_Property
    def commit_errors (self) :
        return list \
            ( ichain
                ( self._commit_errors
                , * (e.commit_errors for e in self.elements)
                )
            )
    # end def commit_errors

    @TFL.Meta.Once_Property
    def conflicts (self) :
        return sum ((e.conflicts for e in self.elements), self._conflicts)
    # end def conflicts

    @TFL.Meta.Property
    def elements (self) :
        return self._elements
    # end def elements

    @elements.setter
    def elements (self, value) :
        self._elements = value
    # end def elements

    @TFL.Meta.Once_Property
    def errors (self) :
        return self.submission_errors + self.commit_errors
    # end def errors

    @TFL.Meta.Once_Property
    def fq_id (self) :
        return filtered_join ("", [self.bare_id, self.index])
    # end def fq_id

    @TFL.Meta.Property
    def id (self) :
        return self.fq_id
    # end def id

    @TFL.Meta.Once_Property
    def index (self) :
        return filtered_join \
            ("", [self.parent and self.parent.index, self._index])
    # end def index

    @TFL.Meta.Once_Property
    def Parent_Entity (self) :
        if self.parent :
            return self.parent.Entity
    # end def Parent_Entity

    @property
    def po_index (self) :
        """Pre-order index of `self` in element hierarchy"""
        root = self.root
        if root._po_index is None :
            root._setup_po_index ()
        return self._po_index
    # end def po_index

    @po_index.deleter
    def po_index (self) :
        self._po_index = None
    # end def po_index

    @TFL.Meta.Once_Property
    def root (self) :
        parent = self.parent
        return self if parent is None else parent.root
    # end def root

    @TFL.Meta.Once_Property
    def submission_errors (self) :
        return sorted \
            ( ichain
                ( self._submission_errors
                , * (e.submission_errors for e in self.elements)
                )
            , key = Q.po_index
            )
    # end def submission_errors

    @property
    def submitted_value (self) :
        submission = self.submission
        return submission.value if submission is not None else self.undef
    # end def submitted_value

    @TFL.Meta.Once_Property
    def template_elements (self) :
        return sorted \
            ((e for e in self.elements if not e.skip), key = Q.ui_rank)
    # end def template_elements

    @property
    def ui_rank (self) :
        return self._ui_rank
    # end def ui_rank

    @ui_rank.setter
    def ui_rank (self, value) :
        self._ui_rank = value
    # end def ui_rank

    @TFL.Meta.Class_and_Instance_Method
    def elements_transitive (soc) :
        if not soc.skip :
            yield soc
            for e in soc.elements :
                for et in e.elements_transitive () :
                    yield et
    # end def elements_transitive

    def reset_once_properties (self) :
        for k in self._reset_properties :
            try :
                delattr (self, k)
            except AttributeError :
                pass
    # end def reset_once_properties

    def reset_once_properties_p (self) :
        p = self
        while p is not None :
            p.reset_once_properties ()
            p = p.parent
    # end def reset_once_properties

    def submitted_value_transitive (self) :
        return dict (self._submitted_value_iter ())
    # end def submitted_value_transitive

    @classmethod
    def template_module_iter (cls) :
        for e in cls.elements_transitive () :
            tm = e.template_module
            if tm :
                yield tm
    # end def template_module_iter

    def _mapped_id (self, map, sig) :
        try :
            result = map [sig]
        except KeyError :
            result = map [sig] = len (map) + 1
        return result
    # end def _mapped_id

    def _my_cargo (self, cargo) :
        return cargo ["field_values"].get (self.id, {})
    # end def _my_cargo

    def _my_submission (self, scope, cargo, submission = None, ** kw) :
        if submission is None :
            submission = self.Submission (self, scope, cargo, ** kw)
        self.submission = submission
        return submission
    # end def _my_submission

    def _setup_po_index (self) :
        for i, e in enumerate (self.root.elements_transitive ()) :
            e._po_index = i
    # end def _setup_po_index

    def _submitted_value_iter (self) :
        undef = self.undef
        for e in self.elements :
            v = e.submitted_value
            if v is not undef :
                yield e.name, v
    # end def _submitted_value_iter

    @TFL.Meta.Class_and_Instance_Method
    def _update_element_map (soc, elem) :
        if soc is not elem :
            Map = soc._Element_Map
            for k in elem._element_ids :
                key = getattr (elem, k, None)
                if key and not key in Map :
                    Map [key] = elem
    # end def _update_element_map

    _update_element_map_base = _update_element_map

    def __iter__ (self) :
        for e in self.elements :
            if not e.skip :
                yield e
    # end def __iter__

    def __repr__ (self) :
        return "<%s %s>" % (self.__class__.__name__, self.id)
    # end def __repr__

# end class _Base_

class _Element_ (BaM (_Base_, metaclass = _M_Element_)) :
    """Base class for MF3 element classes."""

    id_essence          = TFL.Meta.Alias_Property ("essence")

    _reset_properties   = ("field_elements", )

    def __init__ (self, essence = None, ** kw) :
        self.__super.__init__ (essence = essence, ** kw)
        self.pop_to_self      (kw, * self._pop_to_self)
        self.pop_to_self      (kw, * self._pop_to_self_, prefix = "_")
        elements      = self.__class__.elements
        self.essence  = essence
        self.elements = list (self._new_element (e, ** kw) for e in elements)
    # end def __init__

    @TFL.Meta.Once_Property
    def field_elements (self) :
        def _gen (self) :
            for e in self.elements :
                if isinstance (e, _Field_Composite_) and not e.skip :
                    for f in e.field_elements :
                        yield f
                elif isinstance (e, _Field_) :
                    yield e
        return tuple (e for e in _gen (self) if not e.skip)
    # end def field_elements

    def completer_choose_value_iter (self, value, seen) :
        """Generate `id, value` pair for `self` if not in `seen`"""
        id = self.id
        if id not in seen :
            seen.add (id)
            yield self.id, value
    # end def completer_choose_value_iter

    @classmethod
    def _add_auto_attributes (cls, E_Type, ** kw) :
        kw.pop ("parent", None)
        cls.elements = tuple \
            (   cls._Auto_Element (ak, E_Type, ** kw)
            for ak in cls._auto_attributes (E_Type)
            )
    # end def _add_auto_attributes

    @classmethod
    def _auto_attributes (cls, E_Type) :
        return cls.attr_selector (E_Type)
    # end def _auto_attributes

    @classmethod
    def _Auto_Element (cls, ak, E_Type, ** kw) :
        return ak.MF3_Element.Auto (ak, E_Type, parent = cls, ** kw)
    # end def _Auto_Element

    def _new_element (self, e, ** kw) :
        return e (self.essence, parent = self, ** kw)
    # end def _new_element

    @TFL.Meta.Class_and_Instance_Method
    def _new_id (soc, essence) :
        parent = soc.parent
        return parent.id_sep.join ((parent.bare_id, soc._own_id (essence)))
    # end def _new_id

# end class _Element_

class _Entity_Mixin_ (_Base_) :
    """Mixin for Entity elements"""

    attr_selector       = MOM.Attr.Selector.List \
        (MOM.Attr.Selector.primary, MOM.Attr.Selector.required)
    include_rev_refs    = ()
    render_groups       = ()
    Submission          = GTW.MF3.Submission.Entity_Mixin
    _pop_to_self        = \
        ( "attr_selector"
        , "include_rev_refs"
        , "render_groups"
        , "restrict_completion"
        )
    _reset_properties   = ("sig", )

    def __init__ (self, essence = None, ** kw) :
        self.buddies_map = {}
        self.__super.__init__ (essence, ** kw)
    # end def __init__

    @TFL.Meta.Once_Property
    def as_json_cargo (self) :
        result     = dict \
            ( buddies      = self.buddies_as_json_cargo
            , cargo        = self.cargo_as_json_cargo
            , checkers     = self.checkers_as_json_cargo
            , completers   = self.completers_as_json_cargo
            )
        return result
    # end def as_json_cargo

    @TFL.Meta.Once_Property
    def buddies_as_json_cargo (self) :
        ### prime `.buddies_map` by touching all completers and polishers
        def _gen () :
            for e in self.elements_transitive () :
                if e.polisher :
                    yield e.polisher.id
        _ = self.completers_as_json_cargo
        _ = tuple (_gen ())
        return dict \
            (  (id, list (fields))
            for fields, id in pyk.iteritems (self.buddies_map)
            )
    # end def checkers_as_json_cargo

    @TFL.Meta.Once_Property
    def cargo_as_json_cargo (self) :
        def _gen (self, elems) :
            for e in elems :
                for k, v in e.fields_as_json_cargo () :
                    yield k, v
        return dict \
            ( field_values  = dict (_gen (self, self.entity_elements))
            , sigs          = self.sigs_as_json_cargo
            )
    # end def cargo_as_json_cargo

    @TFL.Meta.Once_Property
    def checkers_as_json_cargo (self) :
        return {} ### XXX
    # end def checkers_as_json_cargo

    @TFL.Meta.Once_Property
    def completers_as_json_cargo (self) :
        return dict \
            (  (e.completer.id, e.completer.as_json_cargo)
            for e in self.elements_transitive () if e.completer
            )
    # end def completers_as_json_cargo

    @TFL.Meta.Once_Property
    def entity_elements (self) :
        def _gen (self) :
            for e in self.elements_transitive () :
                if isinstance (e, _Entity_Mixin_) and e.field_elements :
                    yield e
        return tuple (_gen (self))
    # end def entity_elements

    @TFL.Meta.Once_Property
    def sig (self) :
        return tuple (f.sig for f in self.field_elements)
    # end def sig

    @TFL.Meta.Once_Property
    def sigs_as_json_cargo (self) :
        sig_hash = self.root.sig_hash
        return dict ((e.id, sig_hash (e.sig)) for e in self.entity_elements)
    # end def sigs_as_json_cargo

    @property
    def submitted_value (self) :
        return self.submitted_value_transitive ()
    # end def submitted_value

    def completer_choose_value_iter (self, value, seen) :
        """Generate `id, value` pairs for all nested elements and `self`."""
        if value is not None :
            AQ = self.E_Type.AQ
            for e in self.elements :
                q  = getattr (AQ, e.name).QR
                ev = q (value)
                for i, v in e.completer_choose_value_iter (ev, seen) :
                    yield i, v
        for i, v in self.__super.completer_choose_value_iter (value, seen) :
            yield i, v
    # end def completer_choose_value_iter

    def fields_as_json_cargo (self) :
        return ((f.id, f.field_as_json_cargo) for f in self.field_elements)
    # end def fields_as_json_cargo

    @classmethod
    def _auto_attributes (cls, E_Type) :
        result = cls.__c_super._auto_attributes (E_Type)
        if cls.include_rev_refs :
            irrs   = MOM.Attr.Selector.Name \
                (* cls.include_rev_refs, ignore_missing = True) (E_Type)
            result = tuple (ichain (result, irrs))
        return result
    # end def _auto_attributes

    def _change_from_submission (self, scope, svs) :
        if svs :
            on_error = self._submission_errors.append
            try :
                self.submission.essence.set_raw (on_error = on_error, ** svs)
            except MOM.Error.Error as exc :
                on_error (exc)
            except Exception as exc :
                logging.exception \
                    ( "Exception from `set_raw` for %r with %s"
                    % (self.essence, sorted (pyk.iteritems (svs)))
                    )
                on_error (exc)
    # end def _change_from_submission

    def _create_from_submission (self, scope, svs) :
        ETM = scope [self.E_Type.type_name]
        return self._create_instance (ETM, svs)
    # end def _create_from_submission

    def _create_instance (self, ETM, svs) :
        error    = None
        on_error = self._submission_errors.append
        result   = self.undef
        try :
            try :
                rqas      = ETM.raw_query_attrs (svs, svs)
                matches   = ETM.query (* rqas)
            except Exception as exc :
                count     = 0
            else :
                count     = matches.count ()
            if not count :
                result    = ETM (on_error = on_error, raw = True, ** svs)
            else :
                error     = None
                try :
                    epks  = ETM.E_Type.epkified (** svs)
                except MOM.Error.Required_Missing as exc :
                    error = self._required_missing_error (exc, svs)
                except Exception :
                    pass
                if error is None and self.required :
                    if count == 1 :
                        result = matches.one ()
                    else :
                        error = MOM.Error.Ambiguous_Epk \
                            ( ETM.E_Type, (), svs, count
                            , * matches.limit (3).all ()
                            )
                if error is not None and error is not self.undef :
                    on_error (error)
        except MOM.Error.Invariants as exc :
            on_error (exc)
        else :
            self.submission.value = result
            if result is not self.undef :
                self.essence = result
            return result
    # end def _create_instance

    def _required_missing_error (self, exc, svs) :
        return exc
    # end def _required_missing_error

    def _submit (self, scope, cargo, submission = None) :
        errors     = self._submission_errors = GTW.MF3.Error.List (self)
        submission = self._my_submission \
            (scope, cargo, submission, essence = self.essence)
        with errors :
            r_errs  = 0
            handler = \
                ( self._create_from_submission if submission.essence is None
                    else self._change_from_submission
                )
            try :
                to_do = []
                for e in self.elements :
                    try :
                        e._submit (scope, cargo)
                    except Delay_Call :
                        to_do.append (e)
                    else :
                        if e.attr.kind.is_required :
                            r_errs += len (e.submission_errors)
                svs = self.submitted_value or {}
                if (svs or self.required) and not (self.conflicts or r_errs) :
                    ### `self.required` --> trigger create checks
                    handler (scope, svs)
                for e in to_do :
                    try :
                        e._submit (scope, cargo)
                    except Delay_Call :
                        ### Errors in form submission can result in missing
                        ### `e.parent.essence` here which raises `Delay_Call`
                        pass
            except MOM.Error.Error as exc :
                if not errors :
                    errors.append (exc)
    # end def _submit

    def __iter__ (self) :
        result = self.render_groups or self.elements
        return iter (result)
    # end def __iter__

# end class _Entity_Mixin_

class _Entity_ (BaM (_Entity_Mixin_, _Element_, metaclass = M_Entity)) :

    attr_selector       = MOM.Attr.Selector.editable

    def __init__ (self, essence = None, ** kw) :
        self._Element_Map_body = {}
        self.__super.__init__ (essence, ** kw)
    # end def __init__

    @classmethod
    def Auto (cls, E_Type, ** kw) :
        E_Type = E_Type.E_Type ### necessary if E_Type_Manager is passed in
        result = cls.New \
            ( E_Type.type_name.replace (".", "__")
            , E_Type        = E_Type
            , attr_selector = kw.pop ("attr_selector", cls.attr_selector)
            , ** kw
            )
        kw.pop ("include_rev_refs", None)
        result._add_auto_attributes (E_Type, ** kw)
        return result
    # end def Auto

    @TFL.Meta.Once_Property
    def Entity (self) :
        return self
    # end def Entity

    @property
    def label (self) :
        return self.E_Type.ui_name_T
    # end def label

    @property
    @getattr_safe (default = "")
    def ui_display (self) :
        return self.essence.ui_display if self.essence else ""
    # end def ui_display

    @TFL.Meta.Property
    def _Element_Map (self) :
        return self._Element_Map_body
    # end def _Element_Map

    def get (self, key, default = None) :
        return self._Element_Map.get (key, default)
    # end def get

    def __getitem__ (self, key) :
        try :
            return self._Element_Map [key]
        except KeyError :
            ### only new rev-ref elements, i.e., those with `index_sep` in
            ### key, might not in `_Element_Map`
            head, _, index = rsplit_hst (key, self.index_sep)
            if head and index :
                id_sep     = Entity_Rev_Ref.id_sep
                if id_sep in head :
                    head, _, tail  = rsplit_hst (head, id_sep)
                else :
                    tail   = None
                head_elem  = self [head]
                key        = tail if tail else int (index)
                result     = head_elem [key]
                return result
            raise
    # end def __getitem__

# end class _Entity_

class _Field_Base_ (BaM (_Element_, metaclass = M_Field)) :

    collapsed               = False
    default                 = _Base_.undef
    prefilled               = False
    syntax                  = None
    template_module         = None

    _attr_prop_map          = dict \
        ( ( (k, k) for k in
            ( "css_align",   "css_class"
            , "description", "explanation", "syntax"
            , "ui_allow_change", "ui_allow_move", "ui_allow_new"
            , "ui_description", "ui_name"
            )
          )
        , choices           = "Choices"
        , label             = "ui_name"
        , input_widget      = "input_widget"
        , _required         = "is_required"
        , settable          = "is_settable"
        , template_macro    = "mf3_template_macro"
        , template_module   = "mf3_template_module"
        , _ui_rank          = "ui_rank"
        )

    _edit                   = _Base_.undef
    _element_ids            = ("q_name", )
    _init                   = _Base_.undef
    _pop_to_self            = \
        ( "allow_new"
        , "css_align",           "css_class"
        , "default",             "description"
        , "edit",                "explanation"
        , "init",                "input_widget"
        , "label",               "prefilled"
        , "restrict_completion"
        , "skip"
        , "template_module",     "template_macro"
        )
    _pop_to_self_           = ("collapsed", "required")
    _q_name                 = None
    _restrict_completion    = _Base_.undef

    def __init__ (self, essence = None, ** kw) :
        q_name      = self.q_name
        attr_spec   = kw.get  ("attr_spec", {}).get (q_name, {})
        akw         = dict    (attr_spec, ** kw)
        self.__super.__init__ (essence,   ** akw)
    # end def __init__

    @classmethod
    def Auto (cls, ak, E_Type, ** kw) :
        name   = q_name = ak.name
        parent = kw.get ("parent")
        if cls.attr_selector is not None :
            E_Type = E_Type.attr_prop (name).E_Type
        def _gen_attr (cls, ak) :
            for k, n in cls._attr_prop_map.items () :
                v = getattr (ak, n, None)
                if not (v is None and getattr (cls, k, None)) :
                    yield k, v
        akw    = dict  (_gen_attr (cls, ak), ** kw)
        if parent :
            q_name = ".".join ((parent.q_name, name)) if parent.q_name else name
            attr_spec = akw.get ("attr_spec", {}).get (q_name, {})
            akw.update (attr_spec)
        akw.setdefault ("attr_selector", cls.attr_selector)
        result = cls.New \
            ( name
            , E_Type        = E_Type
            , attr          = ak.attr
            , name          = name
            , _q_name       = q_name
            , ** akw
            )
        if parent :
            result.bare_id = result._new_id (E_Type)
        if cls.attr_selector is not None :
            result._add_auto_attributes (E_Type, ** kw)
        return result
    # end def Auto

    @TFL.Meta.Once_Property
    def aside (self) :
        desc   = self.ui_description or self.description
        expl   = self.explanation
        labl   = self.label
        result = ""
        if desc :
            result = desc if desc != labl else expl
        elif expl != labl :
            result = expl
        return result
    # end def aside

    @TFL.Meta.Once_Property
    def aside_x (self) :
        result = []
        expl   = self.explanation
        if expl and expl != self.aside :
            result.append (expl)
        if self.syntax :
            result.append (self.syntax)
        return result
    # end def aside_x

    @TFL.Meta.Once_Property
    def completer (self) :
        a_completer = self.attr.completer
        if a_completer is not None and not (self.readonly or self.skip) :
            return a_completer.MF3 (self)
    # end def completer

    @TFL.Meta.Once_Property
    def Entity (self) :
        result = self.parent
        while isinstance (result, _Field_Composite_) :
            result = result.parent
        return result
    # end def Entity

    @property
    def edit (self) :
        result = self._edit
        if result is self.undef :
            result = self._edit = self.init
        return result
    # end def edit

    @edit.setter
    def edit (self, value) :
        self._edit = value
    # end def edit

    @property
    def init (self) :
        if self.id_essence is None and self.default is not self.undef :
            result = self.default
        else :
            result = self._init
            if result is self.undef :
                result = self._init = self.attr.kind.get_raw (self.essence)
            else :
                ### XXX TBD: what to do about cooked values here ???
                pass
        return result
    # end def init

    @init.setter
    def init (self, value) :
        self._init = value
    # end def init

    @property
    def inner_required (self) :
        return self._required and not self.parent.required
    # end def inner_required

    @TFL.Meta.Class_Property
    @TFL.Meta.Class_and_Instance_Method
    def q_name (soc) :
        result = soc._q_name
        if result is None :
            parent = soc.parent
            result = soc.name
            if parent.q_name :
                result = soc._q_name = ".".join ((parent.q_name, result))
        return result
    # end def q_name

    @TFL.Meta.Once_Property
    def r_name (self) :
        """Name relative to `self.Entity`"""
        e_q_name = self.Entity.q_name
        result   = self.q_name
        if e_q_name :
            result = result [len (e_q_name) + 1:]
        return result
    # end def r_name

    @property
    def readonly (self) :
        p_essence = self.parent.id_essence
        return any \
            ( ( not self.settable
              , self.prefilled
              , p_essence is not None
                and self.attr.kind.change_forbidden (p_essence)
              )
            )
    # end def readonly

    @property
    def required (self) :
        return self.parent.required and self._required
    # end def required

    @property
    def restrict_completion (self) :
        result = self._restrict_completion
        if result is self.undef :
            result = self.parent.restrict_completion
        return result
    # end def restrict_completion

    @restrict_completion.setter
    def restrict_completion (self, value) :
        self._restrict_completion = value
    # end def restrict_completion

    @property
    def sig (self) :
        return (self.name, self.index, self.readonly)
    # end def sig

    @TFL.Meta.Class_and_Instance_Method
    def _own_id (soc, essence) :
        return soc.name
    # end def _own_id

    def _set_request_default (self, v, scope) :
        self.default = v
    # end def _set_request_default

# end class _Field_Base_

class _Field_Entity_Mixin_ (_Entity_Mixin_) :

    action_buttons      = ("close", "clear", "reset")
    _reset_properties   = ("field_as_json_cargo", )

    @TFL.Meta.Once_Property
    def allow_new (self) :
        return self.ui_allow_new and not self.E_Type.polymorphic_epk
    # end def allow_new

    @TFL.Meta.Once_Property
    def choices (self) :
        ETM = self.root.scope [self.E_Type]
        q   = ETM.query (sort_key = ETM.sorted_by_epk)
        if q.count () < 100 :
            return [(o.pid, o.ui_display) for o in q]
    # end def choices

    @property
    def cooked (self) :
        return self.essence
    # end def cooked

    @TFL.Meta.Once_Property
    def field_as_json_cargo (self) :
        essence = self.essence
        if essence is None :
            value  = {}
        else :
            value  = dict \
                ( cid     = essence.last_cid
                , display = essence.ui_display
                , pid     = essence.pid
                )
        result = dict (init = value)
        return result
    # end def field_as_json_cargo

    @property
    def init (self) :
        essence = self.essence
        result  = "" if essence is None else essence.pid
        return result
    # end def init

    @init.setter
    def init (self, value) :
        self.essence = value
    # end def init

    def fields_as_json_cargo (self) :
        result = self.__super.fields_as_json_cargo () if self.allow_new else ()
        if self.essence is not None :
            result = ichain (((self.id, self.field_as_json_cargo), ), result)
        return result
    # end def fields_as_json_cargo

    def _required_missing_error (self, exc, svs) :
        result     = self.undef
        filled_in  = list \
            (  f.name for f in self.elements
            if f.submitted_value and f.submitted_value != f.init
            )
        if filled_in or self.required :
            result = self.__super._required_missing_error (exc, svs)
        return result
    # end def _required_missing_error

    def _set_request_default (self, v, scope) :
        ETM = scope [self.E_Type]
        try :
            self.essence = ETM.pid_query (v)
        except Exception as exc :
            logging.error \
                ("Invalid request parameter for %s: %s\n    %s", self, v, exc)
    # end def _set_request_default

# end class _Field_Entity_Mixin_

class _Field_ (_Field_Base_) :
    """Base class for MF3 field classes."""

    Submission          = GTW.MF3.Submission.Field

    @property
    def FO (self) :
        if self.id_essence :
            return self.essence.FO
    # end def FO

# end class _Field_

class _Field_Composite_Mixin_ (_Element_) :
    """Mixin for Field_Composite and Field_Entity"""

    def __init__ (self, essence = None, ** kw) :
        ref = getattr (essence, self.name) if essence is not None else None
        self.__super.__init__ (ref, ** kw)
    # end def __init__

    @TFL.Meta.Once_Property
    def attr_map (self) :
        result = {}
        for e in self.elements :
            result [e.attr.name] = e
        return result
    # end def attr_map

    @property
    def submitted_value (self) :
        return self.submitted_value_transitive () or self.undef
    # end def submitted_value

    @property
    @getattr_safe (default = "")
    def ui_display (self) :
        result = self.essence.ui_display if self.id_essence else ""
        return result
    # end def ui_display

    def get (self, key, default = None) :
        return self.attr_map.get (key, default)
    # end def get

    def __getitem__ (self, key) :
        return self.attr_map [key]
    # end def __getitem__

# end class _Field_Composite_Mixin_

class _Field_Composite_ (_Field_Composite_Mixin_, _Field_) :
    """Base class for fields comprising a composite or structured attribute."""

    attr_selector       = MOM.Attr.Selector.editable

    @TFL.Meta.Once_Property
    def completer_elems (self) :
        return self.elements
    # end def completer_elems

    @property
    def cooked (self) :
        return self.essence if self.id_essence is not None else ()
    # end def edit

    @property
    def edit (self) :
        return ""
    # end def edit

    @property
    def id_essence (self) :
        """Return essence of parent/ancestor element that is an Id_Entity."""
        return self.Entity.essence
    # end def id_essence

    @property
    def init (self) :
        return ""
    # end def init

    def _submit (self, scope, cargo, submission = None) :
        for e in self.elements :
            e._submit (scope, cargo)
    # end def _submit

# end class _Field_Composite_

class Entity (_Entity_) :
    """Form comprising a single essential entity."""

    id_sep              = ":"
    required            = True
    sid                 = 0
    session_secret      = "some-secret"

    _hash_fct           = None
    _pop_to_self        = ("_hash_fct", "sid", "session_secret")
    _reset_properties   = ("as_json", "as_json_cargo", "entity_elements", )

    def __init__ (self, scope, essence = None, ** kw) :
        self.completer_map = {}
        self.scope         = scope
        self.__super.__init__ (essence, ** kw)
    # end def __init__

    @classmethod
    def Auto (cls, E_Type, ** kw) :
        cls._set_id (E_Type, kw)
        result = cls.__c_super.Auto (E_Type, ** kw)
        parent = kw.get ("parent")
        if parent is None and "template_macro" not in kw :
            result.template_macro = "Entity_Form"
        return result
    # end def Auto

    @TFL.Meta.Once_Property
    def as_json (self) :
        cargo = self.as_json_cargo
        return TFL.json_dump.to_string (cargo)
    # end def as_json

    @TFL.Meta.Once_Property
    def as_json_cargo (self) :
        result = dict (self.__super.as_json_cargo)
        result ["cargo"] ["sid"] = self.sid
        essence = self.essence
        if essence is not None :
            result ["cargo"] ["pid"] = essence.pid
        errors = self.errors
        if errors :
            result ["errors"] = MOM.Error.as_json_cargo (* errors)
        return result
    # end def as_json_cargo

    @property
    def hash_fct (self) :
        result = self._hash_fct
        if result is None :
            result = self._hash_fct = TFL.user_config.sha
        return result
    # end def hash_fct

    def check_sigs (self, cargo) :
        cargo_sigs = cargo.get ("sigs", {})
        for e in self.entity_elements :
            sh = self.sig_hash (e.sig)
            ch = cargo_sigs.get (e.id)
            if sh != ch :
                ### XXX TBD ???
                print \
                    ( "Sig mismatch for %s:\n    expected %s,\n    got %s"
                    % (e, sh, ch)
                    )
    # end def check_sigs

    def populate_new (self, cargo) :
        for e in self.elements_transitive () :
            if e is not self :
                try :
                    pn = e.populate_new
                except AttributeError :
                    pass
                else :
                    pn (cargo)
            e.reset_once_properties ()
    # end def populate_new

    def record_commit_errors (self, scope, exc) :
        for e in self.entity_elements :
            errors = e.essence and e.essence.errors
            if errors :
                e._commit_errors = GTW.MF3.Error.List (e, errors)
    # end def record_commit_errors

    def set_request_defaults (self, req_data, scope) :
        AQ = self.E_Type.AQ
        for k, v in sorted (pyk.iteritems (req_data)) :
            try :
                ### Use `AQ` and `aq._q_name` to allow specific role-names, etc.
                aq   = getattr (AQ, k)
                elem = self [aq._q_name]
            except Exception :
                ### not an attribute default, obviously
                pass
            else :
                if elem.id_essence is None and not elem.readonly :
                    elem._set_request_default (v, scope)
    # end def set_request_defaults

    def sig_hash (self, sig) :
        dbid   = self.scope.db_meta_data.dbid
        salt   = self.session_secret
        result = self.hash_fct.hmac (salt)
        for s in (self.id, sig, self.E_Type.db_sig, dbid) :
            result.update (s)
        return portable_repr (result.b64digest (strip = True)).strip (""""'""")
    # end def sig_hash

    def submit (self, scope, cargo) :
        self.populate_new (cargo)
        self.check_sigs   (cargo)
        self._submit      (scope, cargo)
        return self
    # end def submit

    @TFL.Meta.Class_and_Instance_Method
    def _own_id (soc, E_Type) :
        return str (E_Type.i_rank)
    # end def _own_id

    @TFL.Meta.Class_and_Instance_Method
    def _set_id (soc, E_Type, kw) :
        parent     = kw.get ("parent")
        postfix    = kw.pop ("id_postfix", None) or soc._own_id (E_Type)
        if parent is None :
            prefix = kw.pop ("id_prefix", "MF")
            id     = "%s-%s" % (prefix, postfix)
        else :
            id     = parent.id_sep.join ((parent.bare_id, postfix))
        kw ["bare_id"] = id
    # end def _new_id

# end class Entity

class Entity_Rev_Ref (BaM (_Field_Entity_Mixin_, _Entity_, metaclass = M_Entity_Rev_Ref)) :
    """Subform comprising an entity with a reverse reference to the enclosing
       entity.
    """

    action_buttons          = ("close", "clear", "reset", "remove")
    allow_new               = True
    id_sep                  = "::"
    required                = True
    _pop_to_self            = ("allow_new", )

    @property
    def collapsed (self) :
        return self.essence is not None
    # end def collapsed

    @property
    def edit (self) :
        return self.init
    # end def edit

    @property
    @getattr_safe (default = "")
    def ui_display (self) :
        return filtered_join \
            (", ", (e.ui_display for e in self.template_elements))
    # end def ui_display

    @classmethod
    def Auto (cls, E_Type, ** kw) :
        parent = kw.get ("parent")
        kw.update (bare_id = parent.bare_id)
        result = cls.__c_super.Auto (E_Type, ** kw)
        cls.name = cls.q_name = parent.q_name
        return result
    # end def Auto

    @classmethod
    def _add_auto_attributes (cls, E_Type, ** kw) :
        parent   = cls.parent
        cls.q_name = parent.q_name
        ref_attr = parent.attr.ref_attr
        ref_ak   = parent.attr.Ref_Type.attributes [ref_attr.name]
        cls.__c_super._add_auto_attributes (E_Type, ** kw)
        kw.pop ("parent", None)
        cls.elements += \
            ( Field_Ref_Hidden.Auto (ref_ak, E_Type, parent = cls, ** kw)
            ,
            )
    # end def _add_auto_attributes

    @classmethod
    def _auto_attributes (cls, E_Type) :
        ref_attr = cls.parent.attr.ref_attr
        return tuple \
            ( a for a in cls.__c_super._auto_attributes (E_Type)
                if  a is not ref_attr
            )
    # end def _auto_attributes

    def _create_instance (self, ETM, svs) :
        def filled_p (self, svs) :
            for k in svs :
                e = self [k]
                if not e.readonly :
                    return True
            return False
        if filled_p (self, svs) :
            return self.__super._create_instance (ETM, svs)
    # end def _create_instance

    def _required_missing_error (self, exc, svs) :
        req_fields = list (e for e in self.elements if e._required)
        missing    = list \
            (f.name for f in req_fields if not f.submitted_value)
        needed     = list (f.name for f in req_fields)
        result     = MOM.Error.Required_Missing \
            (self.E_Type, needed, missing, [], {})
        return self.__super._required_missing_error (result, svs)
    # end def _required_missing_error

    @TFL.Meta.Class_and_Instance_Method
    def _update_element_map (soc, elem) :
        if soc is not elem :
            soc._update_element_map_base (elem)
            Map = soc._Element_Map
            l   = len (soc.parent.q_name)
            key = elem.q_name [l+1:]
            if key and not key in Map :
                Map [key] = elem
    # end def _update_element_map

# end class Entity_Rev_Ref

@TFL.Add_To_Class ("MF3_Element", MAT.A_Attr_Type)
class Field (_Field_) :
    """Field comprising a single atomic attribute."""

    asyn                = _Base_.undef
    attr_selector       = None
    _reset_properties   = ("field_as_json_cargo", )

    @TFL.Meta.Once_Property
    def completer_elems (self) :
        return (self, )
    # end def completer_elems

    @property
    def cooked (self) :
        attr = self.attr
        kind = attr.kind
        if self.id_essence :
            return kind.get_value   (self.essence)
        else :
            return attr.from_string (self.edit)
    # end def edit

    @TFL.Meta.Once_Property
    def field_as_json_cargo (self) :
        init   = self.init
        edit   = self.edit
        asyn   = self.asyn
        asyn_p = asyn is not self.undef
        if self.id_essence is None and not asyn_p :
            init = None
        result = {}
        if asyn_p or init :
            result ["init"] = init
        if asyn_p or (edit and init != edit) :
            result ["edit"] = edit
        if asyn_p :
            result ["conflict"] = asyn
        return result
    # end def field_as_json_cargo

    @TFL.Meta.Once_Property
    def polisher (self) :
        a_polisher = self.attr.polisher
        if a_polisher is not None and not (self.readonly or self.skip) :
            return GTW.MF3.Polisher (self)
    # end def polisher

    @property
    @getattr_safe (default = "")
    def ui_display (self) :
        FO = self.FO
        return getattr (FO, self.name) if FO is not None else ""
    # end def ui_display

    def _submit (self, scope, cargo, submission = None) :
        my_cargo   = self._my_cargo (cargo)
        submission = self._my_submission (scope, my_cargo, submission)
        if my_cargo :
            if submission.value is not self.undef :
                id_essence = self.id_essence
                if id_essence is not None :
                    asyn = self.attr.kind.get_raw (id_essence)
                    if submission.init != asyn :
                        self.conflicts += 1
                        self.asyn       = asyn
                        ### XXX add MOM.Error.?Async_Conflict?...
                        ###     to self.Entity._submission_errors
    # end def _submit

# end class Field

@TFL.Add_To_Class ("MF3_Element", MAT._A_Composite_)
class Field_Composite (_Field_Composite_) :
    """Field comprising a composite attribute."""

# end class Field_Composite

@TFL.Add_To_Class ("MF3_Element", MAT._A_Id_Entity_)
class Field_Entity (_Field_Composite_Mixin_, _Field_Entity_Mixin_, _Field_) :
    """Field comprising an attribute referring to another essential Entity."""

    Submission          = GTW.MF3.Submission.Field_Entity
    _collapsed          = _Base_.undef
    _essence            = None

    @property
    def collapsed (self) :
        result = self._collapsed
        if result is self.undef :
            result = self.essence is not None
        return result
    # end def collapsed

    @TFL.Meta.Once_Property
    def completer_elems (self) :
        if self.allow_new and self.attr.completer and not self.readonly :
            def _gen (self) :
                attr_map = self.attr_map
                for a in self.E_Type.primary :
                    e = attr_map.get (a.name)
                    if e is not None and not e.skip :
                        yield e
            return tuple (_gen (self))
        else :
            return (self, )
    # end def completer_elems

    @TFL.Meta.Once_Property
    def default_essence (self) :
        result = self.default
        if result is self.undef :
            result = self.attr.kind.get_value (None)
        else :
            ### XXX TBD: what to do about raw values here ???
            pass
        return result
    # end def default_essence

    @property
    def essence (self) :
        result = self._essence
        if result is None :
            result = self.default_essence
        return result
    # end def essence

    @essence.setter
    def essence (self, value) :
        old = self._essence
        if not (old is None or old is self.default_essence) :
            raise TypeError \
                ( "%s already has value %s; cannot change to %"
                % ( self
                  , getattr (old,   "ui_display", value)
                  , getattr (value, "ui_display", value)
                  )
                )
        self._essence = value
    # end def essence

    @property
    def submitted_value (self) :
        submission = self.submission
        result     = submission.value
        if submission.elem_p :
            result = self.submitted_value_transitive ()
            if not result :
                result = self.undef
        return result
    # end def submitted_value

    def _change_from_submission (self, scope, svs) :
        submission = self.submission
        if  (   submission.elem_p
            and submission.value is not None
            and not self.ui_allow_change
            ) :
            if any (e.submission.changed for e in self.elements) :
                attr = self.attr
                self._submission_errors.append \
                    ( MOM.Error.Attribute_Set
                        (submission.value, attr.name, svs, attr.kind)
                    )
                return ### error     --> nothing more to do here
            else :
                return ### no change --> nothing to do
        return self.__super._change_from_submission (scope, svs)
    # end def _change_from_submission

    def _new_element (self, e, ** kw) :
        if not self.allow_new :
            kw ["skip"] = True
        return self.__super._new_element (e, ** kw)
    # end def _new_element

    def _submit (self, scope, cargo, submission = None) :
        my_cargo   = self._my_cargo (cargo)
        submission = self._my_submission \
            (scope, my_cargo, submission, essence = self._essence)
        if submission.elem_p :
            self._essence = None
            self.__super._submit (scope, cargo, submission)
            submission.elem_p = False
    # end def _submit

    def _submitted_value_iter (self) :
        submission  = self.submission
        create_p    = submission.essence is None
        yield_empty = not create_p or self.required
        for k, v in self.__super._submitted_value_iter () :
            ### For creation of optional fields, filter empty fields
            if yield_empty or v != "" :
                yield k, v
    # end def _submitted_value_iter

# end class Field_Entity

class Field_Ref_Hidden (Field_Entity) :
    """Hidden field for entity ref"""

    _attr_prop_map          = dict \
        (  (k, v)
        for k, v in pyk.iteritems (Field_Entity._attr_prop_map)
        if  k not in ("input_widget", "_required")
        )
    _required           = False
    Submission          = GTW.MF3.Submission.Field_Ref_Hidden

    @property
    def input_widget (self) :
        return "mf3_input, hidden"
    # end def input_widget

    @property
    def prefilled (self) :
        return True
    # end def prefilled

    @property
    def ref (self) :
        return self.Parent_Entity.Parent_Entity
    # end def ref

    @property
    def submitted_value (self) :
        ref = self.ref
        return ref.essence or ref.submitted_value
    # end def submitted_value

    @property
    def ui_display (self) :
        return ""
    # end def ui_display

    def _submit (self, scope, cargo, submission = None) :
        self._my_submission (scope, cargo, submission)
    # end def _submit

# end class Field_Ref_Hidden

@TFL.Add_To_Class ("MF3_Element", MAT._A_Rev_Ref_)
class Field_Rev_Ref (BaM (_Field_Base_, metaclass = M_Field_Rev_Ref)) :
    """Rev_Ref field: encapsulates any number of Entity_Rev_Ref referring to
       `parent.essence`.
    """

    attr_selector         = None
    max_index             = 0
    ui_rank               = (1 << 31, )

    _max_rev_ref          = None
    _min_rev_ref          = None
    _pop_to_self_         = ("max_rev_ref", "min_rev_ref")

    def __init__ (self, essence = None, ** kw) :
        self.__super.__init__ (essence, ** kw)
        kw.pop ("parent", None)
        q_name        = self.q_name
        attr_spec     = kw.get ("attr_spec", {}).get (q_name, {})
        self.akw      = akw = dict (attr_spec, parent = self, ** kw)
        self.elements = []
        self._new_rrs = {}
        if essence is None :
            n = self.min_rev_ref
            if n > 0 :
                self.add (n, ** akw)
        else :
            proto     = self.proto
            scope     = essence.home_scope
            ETM       = scope [self.attr.Ref_Type.type_name]
            rrs       = ETM.query (self.attr.ref_filter == essence.pid)
            self.elements.extend \
                ( proto
                    ( rr
                    , index   = "%s%s" % (self.pid_sep, rr.pid)
                    , ** akw
                    )
                for rr in rrs
                )
    # end def __init__

    @classmethod
    def Auto (cls, ak, E_Type, ** kw) :
        result       = cls.__c_super.Auto (ak, E_Type, ** kw)
        q_name       = result.q_name
        attr_spec    = kw.get ("attr_spec", {}).get (q_name, {})
        akw          = dict (attr_spec, ** kw)
        akw.pop ("parent", None)
        akw.pop ("_q_name", None)
        result.proto = proto = Entity_Rev_Ref.Auto \
            (ak.Ref_Type, parent = result, ** akw)
        return result
    # end def Auto

    @classmethod
    def template_module_iter (cls) :
        for tm in cls.__c_super.template_module_iter () :
            yield tm
        for tm in cls.proto.template_module_iter () :
            yield tm
    # end def template_module_iter

    @TFL.Meta.Once_Property
    def max_rev_ref (self) :
        result = self._max_rev_ref
        if result is None :
            result = self.attr.max_rev_ref
        if result < 0 :
            result = 1 << 31
        return result
    # end def max_rev_ref

    @TFL.Meta.Once_Property
    def min_rev_ref (self) :
        result = self._min_rev_ref
        if result is None :
            result = self.attr.min_rev_ref
        if result < 0 :
            result = 0
        return result
    # end def min_rev_ref

    @property
    @getattr_safe (default = "")
    def ui_display (self) :
        return filtered_join \
            (", ", (e.ui_display for e in self.template_elements))
    # end def ui_display

    def add (self, how_many = 1, ** kw) :
        """Add `how_many` new `Entity_Rev_Ref` instances to `self.elements`"""
        assert how_many > 0
        akw       = dict (self.akw, ** kw)
        max_index = self.max_index
        for i in range (how_many) :
            max_index += 1
            result = self._new (akw, max_index)
        self.max_index = max_index
        self.reset_once_properties_p ()
        return result
    # end def add

    def populate_new (self, cargo) :
        akw  = self.akw
        maxi = self.max_index
        sigs = cargo.get ("sigs", {})
        pat  = Regexp \
            ( r"^%s%s(?P<ix>\d+)$"
            % (re.escape (self.id), re.escape (self.index_sep))
            )
        for k in sorted (sigs) :
            if pat.match (k) :
                i    = int (pat.ix)
                maxi = max (maxi, i)
                self._new (akw, i)
        self.max_index = maxi
    # end def populate_new

    def _new (self, akw, i) :
        map = self._new_rrs
        if i not in map :
            index  = "%s%s" % (self.index_sep, i)
            result = map [i] = self.proto (index = index, ** akw)
            self.elements.append (result)
            return result
        else :
            return map [i]
    # end def _new

    def _submit (self, scope, cargo, submission = None) :
        self.populate_new (cargo)
        if self.parent.essence :
            for e in self.elements :
                e._submit (scope, cargo)
        else :
            raise Delay_Call
    # end def _submit

    def __getitem__ (self, key) :
        return self._new_rrs [key]
    # end def __getitem__

# end class Field_Rev_Ref

class Field_Structured (_Field_Composite_) :
    """Field comprising an attribute with internal structure."""

    attr_selector       = MOM.Attr.Selector.editable

    @property
    def FO (self) :
        if self.id_essence :
            return self.parent.essence.FO
    # end def FO

    @property
    @getattr_safe (default = "")
    def ui_display (self) :
        FO = self.FO
        return getattr (FO, self.name) if FO is not None else ""
    # end def ui_display

# end class Field_Structured

@TFL.Add_To_Class ("MF3_Element", MAT._A_Structured_, decorator = property)
def _field_structured_element_class (self) :
    return Field_Structured if self.E_Type.edit_attr else Field
# end def _field_structured_element_class

if __name__ != "__main__" :
    GTW.MF3._Export_Module ()
### __END__ GTW.MF3.Element
