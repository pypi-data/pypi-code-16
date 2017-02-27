# -*- coding: utf-8 -*-
# Copyright (C) 2011-2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package MOM.Attr.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    MOM.Attr.Querier
#
# Purpose
#    Model queries for MOM attributes
#
# Revision Dates
#     4-Dec-2011 (CT) Creation (factored from MOM.Attr.Filter)
#     4-Dec-2011 (CT) Change signature of `_Filter_.__init__` to `(querier)`
#     4-Dec-2011 (CT) Add `_full_name`
#     4-Dec-2011 (CT) Add `choices` to `_as_template_elem_inv`
#     7-Dec-2011 (CT) Add `E_Type`
#    12-Dec-2011 (CT) Add `Class`, remove `deep`
#    13-Dec-2011 (CT) Add `Atoms`, `Unwrapped`, and `Unwrapped_Atoms`
#    13-Dec-2011 (CT) Add `QC` and `QR`
#    16-Dec-2011 (CT) Add `IN`
#    20-Dec-2011 (CT) Use `.sig_attr` instead of home-grown code
#    20-Dec-2011 (CT) Factor `_Container_`, derive `E_Type` from it
#    20-Dec-2011 (CT) Add `Children_Transitive`, `E_Type.As_Json`
#    22-Dec-2011 (CT) s/Children/Attrs/
#    22-Dec-2011 (CT) Add `_attr_selector` to `_Type_` and use it in
#                     `_Container_._attrs`
#    22-Dec-2011 (CT) Add `E_Type.Select`
#     5-Oct-2012 (CT) Guard `_Container_._attrs` against missing `E_Type`
#    10-Oct-2012 (CT) Change `_Type_._cooker` to apply `from_string` to strings
#     7-Mar-2013 (CT) Add `_string_q_name`, `_string_attr_name`,`_string_cooker`
#     7-Mar-2013 (CT) Redefine `Raw.Table` to include `EQS` and `NES`
#    19-Mar-2013 (CT) Refactor `Attrs_Transitive` (and `_attrs_transitive`)
#    19-Mar-2013 (CT) Add argument `seen_etypes` to `_attrs_transitive` to
#                     break E_Type cycles
#    19-Mar-2013 (CT) Protect `As_Json_Cargo`, `As_Template_Elem` against cycles
#    19-Mar-2013 (CT) Protect `Atoms`, `Unwrapped_Atoms`
#    19-Mar-2013 (CT) Pass a copy of `seen_etypes` to recursive calls
#                     (otherwise, a sibling can mask a E_Type)
#    20-Mar-2013 (CT) Add and use `_recursion_limit = 2` to limit E_Type cycles
#    20-Mar-2013 (CT) Add `E_Type.As_Template_Elem`
#    21-Mar-2013 (CT) Factor `_do_recurse`
#                     * consider `has_identity` and `polymorphic_epk`
#    21-Mar-2013 (CT) Check `_do_recurse` once for `self` in `_as_json_cargo`,
#                     `_as_template_elem`; not for each element of `.Attrs`
#    21-Mar-2013 (CT) Redefine `Id_Entity._as_json_cargo_inv`
#                     * add `children_np`
#    22-Mar-2013 (CT) Add `default_child` to `Id_Entity._as_json_cargo_inv`,
#                     factor `E_Types_CNP`, add `E_Types_AQ`
#    22-Mar-2013 (CT) Move `_polymorphic` check out of `_do_recurse`
#    28-Mar-2013 (CT) Redefine `Id_Entity._as_json_cargo`, `._as_template_elem`
#                     to include `._as_...` for each of the `children_np`
#    28-Mar-2013 (CT) Redefine `_Id_Entity_NP_._as_json_cargo_inv`, and
#                     `._as_json_cargo`
#     2-Apr-2013 (CT) Redefine `Id_Entity._as_template_elem_inv` to add
#                     `type_name`
#     3-Apr-2013 (CT) Add `ui_type_name` to `Id_Entity._as_template_elem`
#    11-Apr-2013 (CT) Redefine `_Id_Entity_NP_._ui_name_T` to add `[type_name]`
#    11-Apr-2013 (CT) Include `children_np` in `Sig_Map`
#    18-Apr-2013 (CT) Change `E_Types_CNP` to use
#                     `selectable_e_types_unique_epk`, not `children_np`
#     3-Jun-2013 (CT) Get attribute descriptors from `E_Type.attributes`
#     5-Jun-2013 (CT) Use `Selector.ui_attr`, not `.all`
#     2-Mar-2014 (CT) Factor `_attr_selector`, add `_attr_selector_default`
#     2-Mar-2014 (CT) Add `Rev_Ref`
#     2-Mar-2014 (CT) Add `_nesting_level` and compare to `hidden_nested`
#     7-Mar-2014 (CT) Sort `Attrs` by `ui_rank`
#     6-May-2014 (CT) Add `Show_in_UI_Selector`
#    23-Jan-2015 (CT) Add `_ui_name_short_T`
#    13-Apr-2015 (CT) Use `TFL.json_dump.default`
#     6-May-2015 (CT) Use `TFL.json_dump.to_string`
#    28-Apr-2016 (CT) Remove `glob`, `locl` from `from_string`, `_from_string`
#     4-May-2016 (CT) Add and use `seen_refuse_e_types`
#     4-May-2016 (CT) Change `_polymorphic` to check `selectable_e_types`
#     4-May-2016 (CT) Change `E_Types_AQ` to use `derived_attr`
#                     and pass `_attr_selector` to `_Id_Entity_NP_`
#    11-May-2016 (CT) Factor `_getattr_transitive`, support `type_restriction`
#                     + Add `pattern_fragment` and `regexp`
#    12-May-2016 (CT) Redefine `_Id_Entity_NP_._full_name`, `._id`, `._q_name`
#                     + Append `[type_name]`
#    18-May-2016 (CT) Add `_id_sep`, `_op_sep`, `_ui_sep` to `_Base_`
#    19-May-2016 (CT) Use `E_Type.ui_name_T`, not `_T (E_Type.ui_name)`
#    20-May-2016 (CT) Use `E_Type.type_name`, not `E_Type`, to index
#                     `seen_etypes` (Python-3 compatibility)
#    20-May-2016 (CT) Pass `outer` to `_Id_Entity_NP_`
#                     + Fix `_attr_selector` in `_Id_Entity_NP_.__init__`
#                       (don't want `outer._attr_selector` there!)
#    24-May-2016 (CT) Change `Id_Entity.__getitem__` to return `self`
#                     `if self.E_Type.type_name == key`; raise `KeyError`
#    30-May-2016 (CT) Add `E_Type._polymorphic`
#    31-May-2016 (CT) Define `Select` for `_Type_`, `_Id_Entity_NP_`
#     1-Jun-2016 (CT) Change `_getattr_transitive` to allow empty `head`
#     1-Jun-2016 (CT) Add `E_Type.__getitem__` to allow access to `children_np`
#     6-Jun-2016 (CT) Change `_attr_selector.setter` to allow `.mandatory`
#     6-Jun-2016 (CT) Add `__` guard to `__getattr__`
#    10-Jun-2016 (CT) Add `E_Type.QC`, `.QR`
#     6-Jul-2016 (CT) Add `Range`
#    19-Jul-2016 (CT) Add `_Structured_`, factor `_Co_Mixin_`
#    19-Jul-2016 (CT) Add `Time`; derive `Date` from `_Structured_`
#     7-Oct-2016 (CT) Add `Time.Table` with `Filter.Time_*`  entries
#     7-Oct-2016 (CT) Change `_Structured_._atoms` to look at `E_Type.edit_attr`
#    ««revision-date»»···
#--

from   __future__  import unicode_literals

from   _MOM                  import MOM
from   _TFL                  import TFL

from   _MOM._Attr            import Filter

import _TFL._Meta.Object

from   _TFL.Decorator        import getattr_safe
from   _TFL.I18N             import _, _T, _Tn
from   _TFL.defaultdict      import defaultdict_int as ETC
from   _TFL.predicate        import filtered_join, first, split_hst, uniq
from   _TFL.pyk              import pyk
from   _TFL.Regexp           import Regexp, re

import _TFL._Meta.Object
import _TFL._Meta.Once_Property
import _TFL.json_dump

id_sep = "__"
op_sep = "___"
ui_sep = "/"

class pattern_fragment :
    """Class is namespace for pattern fragments"""

    type_restriction = r"[A-Za-z0-9_.]+"

    name_1           = r"[a-zA-Z0-9]+ (?: _[a-zA-Z0-9]+)*"
    name_1_tr        = " ".join \
        ( ( name_1                               ### leading name
          ,   r"(?: "
          ,     r"\[", type_restriction, r"\]"   ### type_name
          ,     id_sep                           ### name separator
          ,     name_1                           ### trailing name
          ,   r")?"
          )
        )
    name             = " ".join \
        ( ( r"(?P<name>"
          ,   name_1_tr                          ### leading name
          ,   r"(?: "
          ,     id_sep                           ### name separator
          ,     name_1_tr                        ### trailing name
          ,   r")*"
          , r")"
          )
        )
    operation        = r"(?P<op> [A-Z]+)"

### end class pattern_fragment

class regexp :
    """Class is namespace for regular expression objects"""

    _pf              = pattern_fragment

    attr             = Regexp \
        ( "".join ((_pf.name, op_sep, _pf.operation, r"$"))
        , re.VERBOSE
        )

    attr_opt         = Regexp \
        ( "".join ((_pf.name, r"(?:", op_sep, _pf.operation, r")?", r"$"))
        , re.VERBOSE
        )

    id_seps          = Regexp \
        ( "".join
            ( ( "(?: \.|"
              ,   id_sep
              , r")"
              )
            )
        , re.VERBOSE
        )

    type_restriction = Regexp \
        ( "".join
            ( ( r"\["
              ,   r"""['"]?""" ### use of a group here would break `split`
              ,     r"(?P<type>"
              ,       _pf.type_restriction
              ,     r")"
              ,   r"""['"]?""" ### use of a backreference would break `split`
              , r"\]"
              , "(?: \.|"
              ,   id_sep
              , r")?" ### remove trailing separator, if any, from `split` result
              )
            )
        , re.VERBOSE
        )

### end class regexp

class _Base_ (TFL.Meta.Object) :

    E_Types_CNP      = None
    _id_sep          = id_sep
    _nesting_level   = 0
    _op_sep          = op_sep
    _recursion_limit = 2
    _ui_sep          = ui_sep

    @property    ### depends on currently selected language (I18N/L10N)
    @getattr_safe###
    def As_Json_Cargo (self) :
        return self._as_json_cargo (ETC ())
    # end def As_Json_Cargo

    @property    ### depends on currently selected language (I18N/L10N)
    @getattr_safe###
    def As_Template_Elem (self) :
        return self._as_template_elem (ETC ())
    # end def As_Template_Elem

    @TFL.Meta.Once_Property
    @getattr_safe
    def Atoms (self) :
        return tuple (self._atoms (ETC ()))
    # end def Atoms

    @TFL.Meta.Once_Property
    @getattr_safe
    def Attrs_Transitive (self) :
        return tuple (self._attrs_transitive (ETC ()))
    # end def Attrs_Transitive

    @TFL.Meta.Once_Property
    @getattr_safe
    def Unwrapped_Atoms (self) :
        return tuple (self._unwrapped_atoms (ETC ()))
    # end def Unwrapped_Atoms

    @TFL.Meta.Once_Property
    @getattr_safe
    def _polymorphic (self) :
        ET     = self.E_Type
        cnp    = getattr (self._attr, "selectable_e_types", None)
        result = \
            (   ET is not None
            and ET.has_identity
            and ET.polymorphic_epk
            and cnp
            and not (len (cnp) == 1 and first (cnp) == ET.type_name)
                ### if there aren't any selectable_e_types except `ET`
                ### --> not polymorphic in the context of `self._attr`
            )
        return result
    # end def _polymorphic

    def _as_json_cargo (self, seen_etypes) :
        return dict (self._as_json_cargo_inv, ui_name = self._attr.ui_name_T)
    # end def _as_json_cargo

    def _as_template_elem (self, seen_etypes) :
        result = dict (self._as_template_elem_inv, ui_name = self._ui_name_T)
        return TFL.Record (** result)
    # end def _as_template_elem

    @property
    @getattr_safe
    def _attr_selector (self) :
        return getattr (self, "__attr_selector")
    # end def _attr_selector

    @_attr_selector.setter
    @getattr_safe
    def _attr_selector (self, value) :
        setattr (self, "__attr_selector", value or self._attr_selector_default)
    # end def _attr_selector

    def _sig_map_transitive (self, seen_etypes) :
        return {}
    # end def _sig_map_transitive

# end class _Base_

class _Container_ (_Base_) :

    @TFL.Meta.Once_Property
    @getattr_safe
    def Attrs (self) :
        return tuple \
            ( sorted
                ( (getattr (self, c.name) for c in self._attrs)
                , key = TFL.Getter._attr.kind.ui_rank
                )
            )
    # end def Attrs

    @TFL.Meta.Once_Property
    @getattr_safe
    def _attrs (self) :
        ET = self.E_Type
        if ET is not None :
            return self._attr_selector (self.E_Type)
        else :
            return ()
    # end def _attrs

    def _as_json_cargo (self, seen_etypes) :
        ET = self.E_Type
        seen_etypes [ET.type_name] += 1
        result = self.__super._as_json_cargo (seen_etypes)
        if self._do_recurse (self, self._recursion_limit, seen_etypes) :
            if not self._polymorphic :
                attrs = list \
                    (c._as_json_cargo (ETC (seen_etypes)) for c in self.Attrs)
                if attrs :
                    result ["attrs"] = attrs
        return result
    # end def _as_json_cargo

    def _as_template_elem (self, seen_etypes) :
        ET = self.E_Type
        seen_etypes [ET.type_name] += 1
        result = self.__super._as_template_elem (seen_etypes)
        if self._do_recurse (self, self._recursion_limit, seen_etypes) :
            if not self._polymorphic :
                attrs = list \
                    (   c._as_template_elem (ETC (seen_etypes))
                    for c in self.Attrs
                    )
                if attrs :
                    result ["attrs"] = attrs
        return result
    # end def _as_template_elem

    def _atoms (self, seen_etypes) :
        seen_etypes [self.E_Type.type_name] += 1
        rc = self._recursion_limit
        for c in self.Attrs :
            if self._do_recurse (c, rc, seen_etypes) and not c._polymorphic :
                for ct in c._atoms (ETC (seen_etypes)):
                    yield ct
    # end def _atoms

    def _attrs_transitive (self, seen_etypes) :
        seen_etypes [self.E_Type.type_name] += 1
        rc = self._recursion_limit
        for c in self.Attrs :
            if self._do_recurse (c, rc, seen_etypes) and not c._polymorphic :
                for ct in c._attrs_transitive (ETC (seen_etypes)):
                    yield ct
            else :
                yield c
    # end def _attrs_transitive

    def _do_recurse (self, c, rc, seen_etypes) :
        cet    = c.E_Type
        result = True
        if cet is not None :
            if cet.has_identity :
                result = seen_etypes [cet.type_name] <= rc
            seen_etypes [cet.type_name] += 1
        return result
    # end def _do_recurse

    def _getattr_transitive (self, name) :
        name, _, op = split_hst (name, op_sep)
        tr = regexp.type_restriction
        if tr.search (name) :
            head, typ, tail = tr.split (name, 1, 2)
            result = self._getattr_transitive_inner (head) if head else self
            try :
                result = result [typ]
            except LookupError :
                raise ValueError \
                    ( _T ("Unknown type %s for attribute %s.%s")
                    % (typ, self.E_Type.type_name, name)
                    )
            if tail :
                result = getattr (result, tail)
        else :
            result = self._getattr_transitive_inner (name)
        return result
    # end def _getattr_transitive

    def _getattr_transitive_inner (self, name) :
        E_Type = self.E_Type
        id_sep = regexp.id_seps
        if id_sep.search (name) :
            head, tail = id_sep.split (name, 1)
        else :
            head = name
            tail = None
        try :
            result = self.E_Type.attributes [head].AQ.Wrapped (self)
            setattr (self, head, result)
            if tail :
                result = getattr (Filter.Q, tail) (result)
        except LookupError :
            raise AttributeError \
                (_T ("Unknown attribute %s.%s") % (E_Type.type_name, name))
        return result
    # end def _getattr_transitive_inner

    def _sig_map_transitive (self, seen_etypes) :
        seen_etypes [self.E_Type.type_name] += 1
        result = self.__super._sig_map_transitive (seen_etypes)
        rc = self._recursion_limit
        for c in self.Attrs :
            if self._do_recurse (c, rc, seen_etypes) :
                result.update (c._sig_map_transitive (seen_etypes))
        return result
    # end def _sig_map_transitive

    def _unwrapped_atoms (self, seen_etypes) :
        seen_etypes [self.E_Type.type_name] += 1
        rc = self._recursion_limit
        for c in self.Attrs :
            if self._do_recurse (c, rc, seen_etypes) and not c._polymorphic :
                for ct in c.Unwrapped.Atoms :
                    yield ct
    # end def _unwrapped_atoms

# end class _Container_

class _M_Type_ (TFL.Meta.Object.__class__) :
    """Meta class for Type classes."""

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        cls.Op_Map  = dict  (cls.Table, ** cls._Table)
        cls.Op_Keys = tuple (sorted (cls.Table))
        if cls.Op_Keys and cls.Op_Keys not in cls.Signatures :
            cls.Signatures [cls.Op_Keys] = len (cls.Signatures)
    # end def __init__

    def __str__ (cls) :
        return "<Attr.Type.Querier %s %s>" % (cls.__name__, cls.Op_Keys)
    # end def __str__

# end class _M_Type_

class _Type_ (TFL.Meta.BaM (_Base_, metaclass = _M_Type_)) :
    """Base class for Type classes.

       A Type class provides all filters for a set of Attr.Type classes.
    """

    Base_Op_Table = Filter._Filter_.Base_Op_Table

    Class         = None
    Signatures    = {}

    ### `Table` maps the filter operations that can sensibly be selected in a UI
    Table   = dict \
        ( EQ                 = Filter.Equal
        , GE                 = Filter.Greater_Equal
        , GT                 = Filter.Greater_Than
        , IN                 = Filter.In
        , LE                 = Filter.Less_Equal
        , LT                 = Filter.Less_Than
        , NE                 = Filter.Not_Equal
        )
    ### `_Table` maps additonal filter operations that don't make sense in a UI
    _Table  = dict \
        ( AC                 = Filter.Auto_Complete
        )

    def __init__ (self, attr, outer = None, _attr_selector = None) :
        self._attr          = attr
        self._outer         = outer
        self._nesting_level = (outer._nesting_level + 1) if outer else 0
        self._attr_selector = (outer and outer._attr_selector) \
            if _attr_selector is None else _attr_selector
    # end def __init__

    def Select (self, _attr_selector) :
        return self.__class__ (self._attr, self._outer, _attr_selector)
    # end def Select

    def Wrapped (self, outer) :
        assert not self._outer
        return self.__class__ (self._attr, outer)
    # end def Wrapped

    @TFL.Meta.Once_Property
    @getattr_safe
    def Attrs (self) :
        return ()
    # end def Attrs

    @TFL.Meta.Once_Property
    @getattr_safe
    def E_Type (self) :
        return self._attr.E_Type
    # end def E_Type

    @TFL.Meta.Once_Property
    @getattr_safe
    def QC (self, ) :
        return getattr (Filter.Q, self._q_name)
    # end def QC

    @TFL.Meta.Once_Property
    @getattr_safe
    def QR (self, ) :
        return getattr (Filter.Q, self._q_name_raw)
    # end def QR

    @TFL.Meta.Once_Property
    @getattr_safe
    def Show_in_UI_Selector (self) :
        outer  = self._outer
        result = self._attr.show_in_ui_selector
        if outer is not None :
            result = result and outer.Show_in_UI_Selector
        return result
    # end def Show_in_UI_Selector

    @TFL.Meta.Once_Property
    @getattr_safe
    def Sig_Key (self) :
        if self.Op_Keys :
            return self.Signatures [self.Op_Keys]
    # end def Sig_Key

    @TFL.Meta.Once_Property
    @getattr_safe
    def Unwrapped (self) :
        result = self
        if self._outer :
            result = self.__class__ (self._attr)
        return result
    # end def Unwrapped

    @TFL.Meta.Once_Property
    @getattr_safe
    def _as_json_cargo_inv (self) :
        attr     = self._attr
        Class    = self.Class
        Sig_Key  = self.Sig_Key
        result   = dict (name = attr.name)
        if Class :
            result ["Class"]    = Class
        if Sig_Key is not None :
            result ["sig_key"]  = Sig_Key
        return result
    # end def _as_json_cargo_inv

    @TFL.Meta.Once_Property
    @getattr_safe
    def _as_template_elem_inv (self) :
        attr     = self._attr
        result   = dict \
            ( self._as_json_cargo_inv
            , attr        = attr
            , id          = self._id
            , full_name   = self._full_name
            )
        if attr.Choices :
            result ["choices"] = attr.Choices
        return result
    # end def _as_template_elem_inv

    @TFL.Meta.Once_Property
    @getattr_safe
    def _attr_name (self) :
        return self._attr.name
    # end def _attr_name

    @property
    @getattr_safe
    def _attr_selector (self) :
        return getattr (self, "__attr_selector")
    # end def _attr_selector

    @_attr_selector.setter
    @getattr_safe
    def _attr_selector (self, value) :
        default = self._attr_selector_default
        if value is None :
            value = default
        elif not (  value is MOM.Attr.Selector.editable
                 or value is MOM.Attr.Selector.mandatory
                 or value is MOM.Attr.Selector.ui_attr
                 or value is MOM.Attr.Selector.ui_attr_transitive
                 or isinstance (value, MOM.Attr.Selector.Kind)
                 ) :
            value = default
        setattr (self, "__attr_selector", value)
    # end def _attr_selector

    @property
    @getattr_safe
    def _attr_selector_default (self) :
        return MOM.Attr.Selector.sig
    # end def _attr_selector

    @TFL.Meta.Once_Property
    @getattr_safe
    def _full_name (self) :
        outer = self._outer
        return filtered_join (".", (outer and outer._q_name, self._attr.name))
    # end def _full_name

    @TFL.Meta.Once_Property
    @getattr_safe
    def _id (self) :
        outer = self._outer
        return filtered_join (id_sep, (outer and outer._id, self._attr.name))
    # end def _id

    @TFL.Meta.Once_Property
    @getattr_safe
    def _q_name (self) :
        outer = self._outer
        return filtered_join (".", (outer and outer._q_name, self._attr_name))
    # end def _q_name

    @TFL.Meta.Once_Property
    @getattr_safe
    def _q_name_raw (self) :
        outer = self._outer
        return filtered_join \
            (".", (outer and outer._q_name, self._attr.raw_name))
    # end def _q_name_raw

    @property    ### depends on currently selected language (I18N/L10N)
    @getattr_safe###
    def _ui_name_T (self) :
        outer = self._outer
        return filtered_join \
            (ui_sep, (outer and outer._ui_name_T, self._attr.ui_name_T))
    # end def _ui_name_T

    @property    ### depends on currently selected language (I18N/L10N)
    @getattr_safe###
    def _ui_name_short_T (self) :
        outer = self._outer
        return filtered_join \
            ( ui_sep
            , (outer and outer._ui_name_short_T, self._attr.ui_name_short_T)
            )
    # end def _ui_name_short_T

    def _atoms (self, seen_etypes) :
        yield self
    # end def _atoms

    def _attrs_transitive (self, seen_etypes) :
        yield self
    # end def _attrs_transitive

    def _cooker (self, value) :
        attr = self._attr
        if isinstance (value, pyk.string_types) :
            return attr.from_string (value)
        else :
            return attr.cooked (value)
    # end def _cooker

    def _sig_map_transitive (self, seen_etypes) :
        result  = self.__super._sig_map_transitive (seen_etypes)
        op_keys = self.Op_Keys
        if op_keys :
            result [self.Signatures [op_keys]] = op_keys
        return result
    # end def _sig_map_transitive

    def _unwrapped_atoms (self, seen_etypes) :
        yield self.Unwrapped
    # end def _unwrapped_atoms

    def __getattr__ (self, name) :
        try :
            result_type = self.Op_Map [name]
        except KeyError :
            raise AttributeError (name)
        else :
            result = result_type (self)
            setattr (self, name, result)
            return result
    # end def __getattr__

    def __repr__ (self) :
        return str (self)
    # end def __repr__

    def __str__ (self) :
        return "<%s.AQ [Attr.Type.Querier %s]>" % \
            (self._q_name, self.__class__.__name__)
    # end def __str__

# end class _Type_

class _Co_Mixin_ (_Container_, _Type_) :

    def _attrs_transitive (self, seen_etypes) :
        yield self
        for c in self.__super._attrs_transitive (seen_etypes) :
            yield c
    # end def _attrs_transitive

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        try :
            result = self.__super.__getattr__ (name)
        except AttributeError :
            result = self._getattr_transitive (name)
        return result
    # end def __getattr__

# end class _Co_Mixin_

class _Composite_ (_Co_Mixin_) :

    pass

# end class _Composite_

class _Structured_ (_Co_Mixin_) :

    def _atoms (self, seen_etypes) :
        if self.E_Type.edit_attr :
            for x in self.__super._atoms (seen_etypes) :
                yield x
        else :
            yield self
    # end def _atoms

# end class _Structured_

class Boolean (_Type_) :

    Table  = dict \
        ( EQ                 = Filter.Equal
        )

# end class Boolean

class Ckd (_Type_) :

    pass

# end class Ckd

class Composite (_Composite_) :

    Table  = dict ()
    _Table = dict \
        ( AC                 = Filter.Composite_Auto_Complete
        , EQ                 = Filter.Composite_Equal
        , GE                 = Filter.Composite_Greater_Equal
        , GT                 = Filter.Composite_Greater_Than
        , IN                 = Filter.Composite_In
        , LE                 = Filter.Composite_Less_Equal
        , LT                 = Filter.Composite_Less_Than
        , NE                 = Filter.Composite_Not_Equal
        )

# end class Composite

class Date (_Structured_) :

    Table  = dict \
        ( EQ                 = Filter.Date_Equal
        , GE                 = Filter.Date_Greater_Equal
        , GT                 = Filter.Date_Greater_Than
        , IN                 = Filter.Date_In
        , LE                 = Filter.Date_Less_Equal
        , LT                 = Filter.Date_Less_Than
        , NE                 = Filter.Date_Not_Equal
        )
    _Table = dict \
        ( AC                 = Filter.Date_Auto_Complete
        )

# end class Date

class Id_Entity (_Composite_) :

    Class  = "Entity"
    Table  = dict \
        ( EQ                 = Filter.Id_Entity_Equal
        , IN                 = Filter.Id_Entity_In
        , NE                 = Filter.Id_Entity_Not_Equal
        )
    _Table = dict \
        ( AC                 = Filter.Id_Entity_Auto_Complete
        , GE                 = Filter.Id_Entity_Greater_Equal
        , GT                 = Filter.Id_Entity_Greater_Than
        , LE                 = Filter.Id_Entity_Less_Equal
        , LT                 = Filter.Id_Entity_Less_Than
        )

    _ref_name = None

    @TFL.Meta.Once_Property
    @getattr_safe
    def E_Types_AQ (self) :
        result      = {}
        E_Types_CNP = self.E_Types_CNP
        if E_Types_CNP :
            def _gen (self, E_Types_CNP) :
                E_Type       = self.E_Type
                derived_attr = self._attr.derived_for_e_type
                outer        = self._outer
                for (k, ET) in pyk.iteritems (E_Types_CNP) :
                    ### if `E_Type` is in `E_Types_CNP`, it is non-partial
                    ### --> include all editable attributes
                    ats = MOM.Attr.Selector.editable if ET == E_Type else None
                    T   = _Id_Entity_NP_ (ET, derived_attr (ET), outer, ats)
                    yield k, T
            result = dict (_gen (self, E_Types_CNP))
        return result
    # end def E_Types_AQ

    @TFL.Meta.Once_Property
    @getattr_safe
    def E_Types_CNP (self) :
        result  = {}
        if self._polymorphic :
            ET     = self.E_Type
            apt    = ET.app_type
            cnp    = self._attr.selectable_e_types
            result = dict ((str (c), apt.entity_type (c)) for c in cnp)
        return result
    # end def E_Types_CNP

    @TFL.Meta.Once_Property
    @getattr_safe
    def refuse_e_types (self) :
        ET = self.E_Type
        if ET :
            apt   = ET.app_type
            a_ret = getattr (self._attr, "refuse_e_types_transitive", ())
            return set (apt.etypes.get (ret) for ret in a_ret)
        return set ()
    # end def refuse_e_types

    @TFL.Meta.Once_Property
    @getattr_safe
    def seen_refuse_e_types (self) :
        rc = 1 << 31
        return dict ((ret.type_name, rc) for ret in self.refuse_e_types)
    # end def seen_refuse_e_types

    @TFL.Meta.Once_Property
    @getattr_safe
    def _as_json_cargo_inv (self) :
        result = self.__super._as_json_cargo_inv
        if self.E_Types_CNP :
            dc = self.E_Type.default_child
            if dc :
                result ["default_child"] = dc
        return result
    # end def _as_json_cargo_inv

    @TFL.Meta.Once_Property
    @getattr_safe
    def _as_template_elem_inv (self) :
        result = self.__super._as_template_elem_inv
        result ["type_name"] = self.E_Type.type_name
        return result
    # end def _as_template_elem_inv

    def _as_json_cargo (self, seen_etypes) :
        seen_etypes = ETC (dict (seen_etypes, ** self.seen_refuse_e_types))
        result      = {}
        E_Types_CNP = self.E_Types_CNP
        if E_Types_CNP :
            ### Process `E_Types_CNP` first to allow inclusion of own `E_Type`
            ### in `children_np` before `__super` increments `seen_etypes`
            result ["children_np"] = list  \
                (   self [etn]._as_json_cargo (seen_etypes)
                for etn in sorted (E_Types_CNP)
                )
        result.update (self.__super._as_json_cargo (seen_etypes))
        return result
    # end def _as_json_cargo

    def _as_template_elem (self, seen_etypes) :
        seen_etypes = ETC (dict (seen_etypes, ** self.seen_refuse_e_types))
        E_Types_CNP = self.E_Types_CNP
        if E_Types_CNP :
            ### Process `E_Types_CNP` first to allow inclusion of own `E_Type`
            ### in `children_np` before `__super` increments `seen_etypes`
            children_np = list \
                (   self [etn]._as_template_elem (seen_etypes)
                for etn in sorted (E_Types_CNP)
                )
        result = self.__super._as_template_elem (seen_etypes)
        result ["ui_type_name"]    = self.E_Type.ui_name_T
        if E_Types_CNP :
            result ["children_np"] = children_np
        return result
    # end def _as_template_elem

    @TFL.Meta.Once_Property
    @getattr_safe
    def _attrs (self) :
        for a in self.__super._attrs :
            if (   self._nesting_level < a.hidden_nested
               and a.name != self._ref_name
               ) :
                yield a
    # end def _attrs

    def _sig_map_transitive (self, seen_etypes) :
        seen_etypes = ETC (dict (seen_etypes, ** self.seen_refuse_e_types))
        result      = self.__super._sig_map_transitive (seen_etypes)
        E_Types_AQ  = self.E_Types_AQ
        if E_Types_AQ :
            for aq in pyk.itervalues (E_Types_AQ) :
                result.update (aq._sig_map_transitive (seen_etypes))
        return result
    # end def _sig_map_transitive

    def __getitem__ (self, key) :
        E_Types_AQ = self.E_Types_AQ
        if E_Types_AQ :
            try :
                return E_Types_AQ [key]
            except KeyError :
                pass
        if key == self.E_Type.type_name :
            return self
        raise KeyError (key)
    # end def __getitem__

# end class Id_Entity

class _Id_Entity_NP_ (Id_Entity) :

    _polymorphic = False

    def __init__ (self, ET, attr, outer = None, _attr_selector = None) :
        self._E_Type = ET
        self.__super.__init__ \
            ( attr
            , outer          = outer
            , _attr_selector = self._attr_selector_default
                if _attr_selector is None else _attr_selector
                ### Use `_attr_selector_default`, not `outer._attr_selector`,
                ### as default `_attr_selector` for `_Id_Entity_NP_`
            )
    # end def __init__

    def Select (self, _attr_selector) :
        return self.__class__ \
            (self._E_Type, self._attr, self._outer, _attr_selector)
    # end def Select

    def Wrapped (self, outer) :
        assert not self._outer
        return self.__class__ (self._E_Type, self._attr, outer)
    # end def Wrapped

    @property
    def E_Type (self) :
        return self._E_Type
    # end def E_Type

    @TFL.Meta.Once_Property
    @getattr_safe
    def E_Types_CNP (self) :
        pass
    # end def E_Types_CNP

    @TFL.Meta.Once_Property
    @getattr_safe
    def Unwrapped (self) :
        result = self
        if self._outer :
            result = self.__class__ (self._E_Type, self._attr)
        return result
    # end def Unwrapped

    @TFL.Meta.Once_Property
    @getattr_safe
    def _as_json_cargo_inv (self) :
        result = self.__super._as_json_cargo_inv
        result ["type_name"] = self.E_Type.type_name
        return result
    # end def _as_json_cargo_inv

    @TFL.Meta.Once_Property
    @getattr_safe
    def _full_name (self) :
        return "%s[%s]" % (self.__super._full_name, self.E_Type.type_name)
    # end def _full_name

    @TFL.Meta.Once_Property
    @getattr_safe
    def _id (self) :
        return "%s[%s]" % (self.__super._id, self.E_Type.type_name)
    # end def _id

    @TFL.Meta.Once_Property
    @getattr_safe
    def _q_name (self) :
        return "%s[%s]" % (self.__super._q_name, self.E_Type.type_name)
    # end def _q_name

    @property    ### depends on currently selected language (I18N/L10N)
    @getattr_safe###
    def _ui_name_T (self) :
        return "%s[%s]" % (self.__super._ui_name_T, self.E_Type.ui_name_T)
    # end def _ui_name_T

    @property    ### depends on currently selected language (I18N/L10N)
    @getattr_safe###
    def _ui_name_short_T (self) :
        return "%s[%s]" % \
            (self.__super._ui_name_short_T, self.E_Type.ui_name_T)
    # end def _ui_name_short_T

    def _as_json_cargo (self, seen_etypes) :
        result = self.__super._as_json_cargo (seen_etypes)
        result ["ui_type_name"] = self.E_Type.ui_name_T
        return result
    # end def _as_json_cargo

# end class _Id_Entity_NP_

class Rev_Ref (Id_Entity) :

    def __init__ (self, attr, outer = None, _attr_selector = None) :
        self.__super.__init__ \
            ( attr
            , outer          = outer
            , _attr_selector = self._attr_selector_default
                if _attr_selector is None else _attr_selector
            )
        self._ref_name      = attr.ref_name
    # end def __init__

    @TFL.Meta.Once_Property
    @getattr_safe
    def E_Types_CNP (self) :
        pass
    # end def E_Types_CNP

    @property
    @getattr_safe
    def _attr_selector_default (self) :
        return MOM.Attr.Selector.ui_attr_transitive
    # end def _attr_selector

# end class Rev_Ref

class String (_Type_) :

    Table  = dict \
        ( _Type_.Table
        , CONTAINS           = Filter.Contains
        , ENDSWITH           = Filter.Ends_With
        , STARTSWITH         = Filter.Starts_With
        )
    _Table = dict \
        ( AC                 = Filter.Auto_Complete_S
        )

    @TFL.Meta.Once_Property
    @getattr_safe
    def _string_attr_name (self) :
        return self._attr_name
    # end def _string_attr_name

    @TFL.Meta.Once_Property
    @getattr_safe
    def _string_cooker (self) :
        return self._cooker
    # end def _string_cooker

    @TFL.Meta.Once_Property
    @getattr_safe
    def _string_q_name (self) :
        return self._q_name
    # end def _string_cooker

# end class String

class Raw (String) :

    Table  = dict \
        ( String.Table
        , EQS                = Filter.Equal_S
        , NES                = Filter.Not_Equal_S
        )

    @TFL.Meta.Once_Property
    @getattr_safe
    def _string_attr_name (self) :
        return self._attr.raw_name
    # end def _string_attr_name

    @TFL.Meta.Once_Property
    @getattr_safe
    def _string_cooker (self) :
        return pyk.text_type
    # end def _string_cooker

    @TFL.Meta.Once_Property
    @getattr_safe
    def _string_q_name (self) :
        return self._q_name_raw
    # end def _string_cooker

# end class Raw

### Define this after the other classes above to not change `Signatures`

class Range (_Structured_) :
    ### XXX Access to `lower`, `upper` or `start`, `finish`

    Table  = dict \
        ( _Type_.Table
        , CONTAINS           = Filter.Range_Contains
        , IN                 = Filter.Range_In
        , IS_ADJACENT        = Filter.Range_Is_Adjacent
        , OVERLAPS           = Filter.Range_Overlaps
        )

# end class Range

class Time (_Structured_) :

    Table  = dict \
        ( EQ                 = Filter.Time_Equal
        , GE                 = Filter.Time_Greater_Equal
        , GT                 = Filter.Time_Greater_Than
        , IN                 = Filter.Time_In
        , LE                 = Filter.Time_Less_Equal
        , LT                 = Filter.Time_Less_Than
        , NE                 = Filter.Time_Not_Equal
        )
    _Table = dict \
        ( AC                 = Filter.Time_Auto_Complete
        )

# end class Time

class E_Type (_Container_) :
    """Query object for `E_Type` returning an essential attribute's `AQ`"""

    _id = _q_name = _ui_name_T = _ui_name_short_T = None

    Show_in_UI_Selector = property (lambda s : True)

    def __init__ (self, E_Type, _attr_selector = None) :
        self.E_Type = E_Type
        self._attr_selector = _attr_selector
    # end def __init__

    def Select (self, _attr_selector) :
        return self.__class__ (self.E_Type, _attr_selector)
    # end def Select

    @property
    def As_Json (self) :
        return TFL.json_dump.to_string (self.As_Json_Cargo)
    # end def as_json

    @property    ### depends on currently selected language (I18N/L10N)
    @getattr_safe###
    def As_Json_Cargo (self) :
        filters = [f.As_Json_Cargo for f in self.Attrs]
        return dict \
            ( filters   = filters
            , name_sep  = id_sep
            , op_map    = self.Op_Map
            , op_sep    = op_sep
            , sig_map   = self.Sig_Map
            , ui_sep    = ui_sep
            )
    # end def As_Json_Cargo

    @property    ### depends on currently selected language (I18N/L10N)
    @getattr_safe###
    def As_Template_Elem (self) :
        return [f.As_Template_Elem for f in self.Attrs]
    # end def As_Template_Elem

    @property
    def Op_Map (self) :
        result = {}
        for k, v in pyk.iteritems (_Type_.Base_Op_Table) :
            sym = _T (v.op_sym)
            result [k] = dict \
                ( desc  = _T (v.desc)
                , sym   = sym
                )
        return result
    # end def Op_Map

    @TFL.Meta.Once_Property
    @getattr_safe
    def QC (self, ) :
        return Filter.Q.SELF
    # end def QC

    @TFL.Meta.Once_Property
    @getattr_safe
    def QR (self, ) :
        return Filter.Q.ui_display
    # end def QR

    @TFL.Meta.Once_Property
    @getattr_safe
    def _polymorphic (self) :
        ET     = self.E_Type
        cnp    = ET.children_np
        result = \
            (   ET is not None
            and ET.has_identity
            and ET.polymorphic_epk
            and ET.is_partial
            )
        return result
    # end def _polymorphic

    @TFL.Meta.Once_Property
    def Sig_Map (self) :
        result      = {}
        seen_etypes = ETC ()
        for c in self.Attrs :
            result.update (c._sig_map_transitive (seen_etypes))
        return result
    # end def Sig_Map

    @property
    @getattr_safe
    def _attr_selector_default (self) :
        return MOM.Attr.Selector.ui_attr
    # end def _attr_selector_default

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        return self._getattr_transitive (name)
    # end def __getattr__

    def __getitem__ (self, key) :
        E_Type = self.E_Type
        if key == self.E_Type.type_name :
            return self
        elif E_Type.children_np :
            return E_Type.children_np [key].AQ
        raise KeyError (key)
    # end def __getitem__

    def __repr__ (self) :
        return "<Attr.Type.Querier.%s for %s>" % \
            (self.__class__.__name__, self.E_Type.type_name)
    # end def __repr__

    def __str__ (self) :
        return "<%s.AQ>" % (self.E_Type.type_name, )
    # end def __str__

# end class E_Type

if __name__ != "__main__" :
    MOM.Attr._Export_Module ()
### __END__ MOM.Attr.Querier
