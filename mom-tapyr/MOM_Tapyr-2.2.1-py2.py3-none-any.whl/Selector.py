# -*- coding: utf-8 -*-
# Copyright (C) 2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package MOM.
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this module. If not, see <http://www.gnu.org/licenses/>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    MOM.Selector
#
# Purpose
#    Model entity selector
#
# Revision Dates
#    29-May-2016 (CT) Creation...
#     8-Jun-2016 (CT) ...Finish creation
#    14-Jun-2016 (CT) Use `.sig`, not `.primary`, as `Attr_Selector`
#    14-Jun-2016 (CT) Change `Entity_PS.elements` to iterate over `aq.Atoms`
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _MOM                     import MOM
from   _TFL                     import TFL

from   _MOM._Attr               import Querier
import _MOM._Meta.M_Entity

import _TFL._Meta.Object
import _TFL._Meta.Property
import _TFL.Decorator
import _TFL.Undef

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL.Decorator           import getattr_safe
from   _TFL.I18N                import _, _T, _Tn
from   _TFL.predicate           import first, uniq
from   _TFL.pyk                 import pyk
from   _TFL.Regexp              import Multi_Regexp, Regexp, re

import logging

### `MOM.Attr.Selector.sig` works right for both Id_Entity and Composite
Attr_Selector = MOM.Attr.Selector.sig

Classes       = []

def _selector_type (AQ) :
    E_Type = AQ.E_Type
    if AQ._polymorphic :
        result = Entity_P
    elif E_Type.polymorphic_epks :
        result = Entity_PS
    else :
        result = Entity_N
    return result
# end def _selector_type

def _lp_ES (f = None, name = "ES") :
    if f is None :
        return lambda f : _lp_ES (f, name)
    else :
        return TFL.Meta.Lazy_Property_NI (name, f, f.__doc__)
# end def _lp_ES

@TFL.Add_To_Class ("ES", Querier.Id_Entity, Querier.E_Type, decorator = _lp_ES)
def _entity_selector_AQ_ (AQ) :
    """Entity selector for `AQ.E_Type`"""
    T = _selector_type (AQ)
    if AQ._attr_selector is not Attr_Selector :
        AQ = AQ.Select (Attr_Selector)
    return T (AQ)
# end def _entity_selector_AQ_

@TFL.Add_To_Class ("ESW", Querier.Id_Entity, decorator = _lp_ES (name = "ESW"))
def _entity_selector_AQW_ (AQW) :
    """Entity selector for `AQW._attr.E_Type`"""
    AQ     = AQW._attr.E_Type.AQ
    result = AQ.ES
    return result.__class__ (AQ, AQW = AQW) if AQ._polymorphic else result
# end def _entity_selector_AQW_

@TFL.Add_To_Class ("ES", MOM.Meta.M_E_Type_Id, decorator = _lp_ES)
def _entity_selector_ET_ (E_Type) :
    """Entity selector for `E_Type`"""
    return E_Type.AQ.ES
# end def _entity_selector_ET_

class _Base_ (TFL.Meta.Object) :
    """Base class for selector classes and Instance."""

    def level_elements (self, level = 0) :
        yield level, self
        level += 1
        for e in self.elements :
            for l, i in e.level_elements (level) :
                yield l, i
    # end def level_elements

    def recursive_repr (self, level = 0) :
        return "\n".join \
            (  "%s%r" % ("  " * l, e)
            for l, e in self.level_elements (level)
            )
    # end def recursive_repr

    @Once_Property
    def _repr_type (self) :
        return self.E_Type.type_name
    # end def _repr_type

    def __repr__ (self) :
        return "<Selector.%s for %s>" % \
            (self.__class__.__name__, self._repr_tail)
    # end def __repr__

# end class _Base_

class _M_Selector_Base_ (TFL.Meta.Object.__class__) :
    """Meta class for atom and entity selector classes."""

    macro_name = None

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        if not name.startswith ("_") :
            cls.macro_name = "do_%s" % name.lower ()
            Classes.append (cls)
    # end def __init__

    def __call__ (cls, * args, ** kw) :
        result = cls.__m_super.__call__ (* args, ** kw)
        k      = result.AQ._q_name
        if k :
            result.root._element_map [k] = result
        return result
    # end def __call__

# end class _M_Selector_Base_

class _Selector_Base_ (TFL.Meta.BaM (_Base_, metaclass = _M_Selector_Base_)) :
    """Base class for atom and entity selectors."""

    id               = TFL.Meta.Alias_Property ("name")
    r_name           = TFL.Meta.Alias_Property ("name")

    @Once_Property
    def attr (self) :
        return self.AQ._attr
    # end def attr

    @Once_Property
    def Class (self) :
        return self.AQ.Class
    # end def Class

    @Once_Property
    def name (self) :
        return self.root.elem_prefix + (self.AQ._q_name or "")
    # end def name

    @property ### depends on currently selected language (I18N/L10N)
    def ui_name (self) :
        return self.AQ._ui_name_T
    # end def ui_name

    def instance (self, completer, ** kw) :
        return Instance (completer, self, ** kw)
    # end def instance

# end class _Selector_Base_

class _Entity_ (_Selector_Base_) :
    """Base class for entity selectors."""

    ES              = property (lambda s : s)
    E_Type          = TFL.Meta.Alias_Property ("AQ.E_Type")
    E_Type_NP       = TFL.Meta.Alias_Property ("root.E_Type")
    E_Type_Root     = TFL.Meta.Alias_Property ("root.E_Type")
    elem_prefix     = ""
    type_name       = TFL.Meta.Alias_Property ("AQ.E_Type.type_name")
    ui_name         = \
    ui_type_name    = TFL.Meta.Alias_Property ("AQ.E_Type.ui_name_T")

    def __init__ (self, AQ, root = None, AQW = None) :
        self.AQ   = AQ
        self.AQW  = AQW
        self.root = self if root is None else root
        if self.is_root :
            self._element_map = {}
    # end def __init__

    @Once_Property
    def atoms (self) :
        def _gen (self) :
            for e in self.elements :
                for a in e.atoms :
                    yield a
        return tuple (_gen (self))
    # end def atoms

    @Once_Property
    def is_root (self) :
        return self.root is self
    # end def is_root

    @Once_Property
    def _repr_tail (self) :
        return "%s for %s" % (self.AQ, self._repr_type)
    # end def _repr_tail

    def completer (self, scope, trigger, values) :
        return Completer (self, self, scope, trigger, values)
    # end def completer

    def Wrapped (self, root) :
        return self.__class__ (self.AQ, root)
    # end def Wrapped

    def __getitem__ (self, key) :
        root = self.root
        map  = root._element_map
        if not map :
            root.atoms ### materialize all elements
        try :
            return map [key]
        except KeyError :
            try :
                aq = getattr (root.AQ, key)
            except AttributeError :
                raise KeyError (key)
            else :
                ### try normalized key
                try :
                    return map [aq._q_name]
                except AttributeError :
                    raise KeyError (key)
    # end def __getitem__

    def __str__ (self) :
        return "<%s.ES>" % (self.E_Type.type_name, )
    # end def __str__

# end class _Entity_

class Atom (_Selector_Base_) :
    """Atomic element of an entity selector."""

    E_Type          = TFL.Meta.Alias_Property ("outer.E_Type")
    is_root         = False

    def __init__ (self, outer, AQ) :
        self.outer  = outer
        self.AQ     = AQ
        self.root   = outer.root
    # end def __init__

    @Once_Property
    def elements (self) :
        return ()
    # end def elements

    @Once_Property
    def atoms (self) :
        return (self, )
    # end def atoms

    @Once_Property
    def _repr_tail (self) :
        return self.AQ._q_name
    # end def _repr_tail

# end class Atom

class Entity_N (_Entity_) :
    """Entity selector for non-polymorphic E_Type."""

    @Once_Property
    def elements (self) :
        def _gen (self) :
            AQ  = self.AQ
            for aq in AQ.Atoms :
                yield Atom (self, aq)
        return tuple (_gen (self))
    # end def elements

# end class Entity_N

class Entity_P (_Entity_) :
    """Entity selector for polymorphic E_Type."""

    E_Type_NP_field_name = "E_Type_NP"

    def __init__ (self, AQ, root = None, AQW = None) :
        self.__super.__init__ (AQ, root = root, AQW = AQW)
        self._child_map = map = {}
        if not self.is_root :
            self.E_Type_NP_field_name = "%s/%s" % \
                (self.name, self.E_Type_NP_field_name)
        if AQW is None :
            E_Types_AQ = getattr (AQ, "E_Types_AQ", None)
        else :
            E_Types_AQ = getattr (AQW, "E_Types_AQ", None)
            if E_Types_AQ :
                E_Types_AQ = dict \
                    ((k, v.E_Type.AQ) for k, v in pyk.iteritems (E_Types_AQ))
        if E_Types_AQ is None :
            def _gen (AQ) :
                ET = AQ.E_Type
                for k, v in pyk.iteritems (ET.children_np_transitive) :
                    yield k, v.ES
            E_Types_AQ = dict (_gen (AQ))
        for k, v in pyk.iteritems (E_Types_AQ) :
            map [k] = Entity_P_CNP (AQ, self, v)
    # end def __init__

    @property ### depends on currently selected language (I18N/L10N)
    def choices (self) :
        return list \
            (  (v.E_Type_NP.type_name, v.E_Type_NP.ui_name_T)
            for v in self.elements
            )
    # end def choices

    @Once_Property
    def elements (self) :
        children_np = sorted (pyk.iteritems (self._child_map))
        return tuple (v for k, v in children_np)
    # end def elements

    @Once_Property
    def selected_type (self) :
        return self.E_Type.default_child
    # end def selected_type

    def completer (self, scope, trigger, values) :
        this = self._get_child_np (values)
        if values and this is not None :
            return Completer (self, this, scope, trigger, values)
        else :
            return self.__super.choices  (scope, trigger, values)
    # end def completer

    def instance (self, completer, ** kw) :
        value = completer.obj if self.is_root else self.AQ.QC (completer.obj)
        ikw   = dict (kw, selected_type = value.type_name)
        return self.__super.instance (completer, ** ikw)
    # end def instance

    def _get_child_np (self, values) :
        rtn = values.get (self.E_Type_NP_field_name)
        if not rtn :
            return None
        try :
            return self._child_map [rtn]
        except KeyError :
            raise ValueError ("Unknown E_Type %s" % rtn)
    # end def _get_child_np

    def __getitem__ (self, key) :
        tr = MOM.Attr.Querier.regexp.type_restriction
        if self.is_root :
            map = self._child_map
            if key in map :
                return map [key]
            elif tr.match (key) :
                _, typ, tail = tr.split (key, 1, 2)
                result = map [typ]
                if tail :
                    result = result [tail]
                return result
        return self.__super.__getitem__ (key)
    # end def __getitem__

# end class Entity_P

class Entity_P_CNP (_Entity_) :
    """Entity selector for non-polymorphic child of polymorphic E_Type."""

    atoms           = TFL.Meta.Alias_Property ("selector_np.atoms")
    elements        = TFL.Meta.Alias_Property ("selector_np.elements")
    E_Type_NP       = TFL.Meta.Alias_Property ("selector_np.E_Type")
    type_name       = TFL.Meta.Alias_Property ("E_Type_NP.type_name")
    ui_type_name    = TFL.Meta.Alias_Property ("ui_name")

    def __init__ (self, AQ, selector_p, E_Type_NP) :
        root = self if selector_p.is_root else selector_p.root
        self.__super.__init__ (AQ, root)
        self.selector_p  = selector_p
        self.selector_np = E_Type_NP.ES.Wrapped (root)
    # end def __init__

    @Once_Property
    def elem_prefix (self) :
        """For top-level, `elem_prefix` is needed for disambiguation.

           Otherwise, fields for two different E_Type_NPs end up
           with the same id/name if the have attributes with identical names.
        """
        return "[%s]" % self.type_name if self.is_root else ""
    # end def elem_prefix

    @property ### depends on currently selected language (I18N/L10N)
    def ui_name (self) :
        return "%s[%s]" % (self.AQ.E_Type.ui_name_T, self.E_Type_NP.ui_name_T)
    # end def ui_name

    @Once_Property
    def _repr_type (self) :
        return self.E_Type_NP.type_name
    # end def _repr_type

    def instance (self, completer, _outer, ** kw) :
        ikw = dict \
            ( kw
            , selected_p = _outer.selected_type == self._repr_type
            , selector_p = _outer
            , _outer     = _outer
            )
        return self.__super.instance (completer, ** ikw)
    # end def instance

# end class Entity_P_CNP

class Entity_PS (_Entity_) :
    """Entity selector for non-polymorphic E_Type with polymorphic attributes."""

    @Once_Property
    def elements (self) :
        def _gen (self) :
            root = self.root
            for aq in self.AQ.Attrs :
                if isinstance (aq, Querier.Id_Entity) :
                    yield aq.ES.Wrapped (root)
                else :
                    ### `aq` might be composite --> use `aq.Atoms`
                    for aq_atom in aq.Atoms :
                        yield Atom (self, aq_atom)
        return tuple (_gen (self))
    # end def elements

# end class Entity_PS

class Completer (TFL.Meta.Object) :
    """Completer for an entity selector for a specific set of `values`."""

    obj                   = None
    _attr_selectors       = None
    _e_type_selectors     = None
    _filters_q_map        = None

    def __init__ (self, selector, selector_np, scope, trigger, values) :
        self.selector     = selector
        self.selector_np  = selector_np
        self.scope        = scope
        self.trigger      = trigger
        self.values       = values
        self.E_Type       = selector_np.E_Type
        self.E_Type_NP    = selector_np.E_Type_NP
    # end def __init__

    @Once_Property
    def ETM (self) :
        return self.scope [self.E_Type_NP.type_name]
    # end def ETM

    @Once_Property
    def attr_selectors (self) :
        if self._attr_selectors is None :
            self._split_values ()
        return self._attr_selectors
    # end def attr_selectors

    @Once_Property
    def e_type_selectors (self) :
        if self._e_type_selectors is None :
            self._split_values ()
        return self._e_type_selectors
    # end def e_type_selectors

    @Once_Property
    def filters_q (self) :
        if self._filters_q_map is None :
            self._split_values ()
        return sorted \
            (pyk.itervalues (self._filters_q_map), key = pyk.text_type)
    # end def filters_q

    @Once_Property
    def names (self) :
        def _gen (self) :
            selector = self.selector
            skip_pat = self.name_skip_pat
            trigger  = self.trigger
            try :
                f = selector [trigger]
            except KeyError :
                logging.warning \
                    ( "Unknown trigger attribute %s for %r"
                    % (trigger, selector)
                    )
            else :
                yield f.name
            for f in selector.atoms :
                n = f.name
                if not skip_pat.match (n) :
                    yield n
        return tuple (uniq (_gen (self)))
    # end def names

    @Once_Property
    def name_skip_pat (self) :
        """Multi/Regexp matching all attribute names that are **not** selected.

           Use negative lookahead assertions to skip all names belonging to
           E_Types not in the set of `e_type_selectors` selected by the client.
        """
        ets = self.e_type_selectors
        def _gen (self, ets) :
            def _sk (x) :
                k, _ = x
                return - len (k), k ### longest first, deterministic
            for k, v in sorted (pyk.iteritems (ets), key = _sk) :
                head = k.split ("/") [0] if "/" in k else ""
                yield Regexp \
                    ("%s\[(?!%s\])" % (re.escape (head), re.escape (v)))
        pats   = _gen (self, ets)
        result = first (pats) if len (ets) == 1 else Multi_Regexp (* pats)
        return result
    # end def name_skip_pat

    def instance (self, obj) :
        self.obj = obj
        return self.selector.instance (self)
    # end def instance

    def query (self, * args, ** kw) :
        result = self.ETM.query (* args, ** kw)
        fqs    = self.filters_q
        if fqs :
            result = result.filter (* fqs)
        return result
    # end def query

    def _split_values (self) :
        ats      = self._attr_selectors   = {}
        ets      = self._e_type_selectors = {}
        fqs      = self._filters_q_map    = {}
        selector = self.selector
        tn       = Entity_P.E_Type_NP_field_name
        for k, v in pyk.iteritems (self.values) :
            if v :
                if k.endswith (tn) :
                    ets [k] = v
                else :
                    try :
                        f = selector [k]
                    except (LookupError, ValueError) :
                        logging.warning \
                            ( "Unknown attribute %s = '%s' for %r"
                            % (k, v, selector)
                            )
                    else :
                        key       = f.name
                        fqs [key] = f.AQ.AC (v)
                        ats [key] = v
    # end def _split_values

# end class Completer

class Instance (_Base_) :
    """Instance of selector for a choosen E_Type instance."""

    edit            = TFL.Meta.Alias_Property ("value")
    selected_p      = True
    _outer          = None
    _selected_type  = TFL.Undef ("selected_type")
    _undef          = TFL.Undef ("value")

    def __init__ (self, completer, selector, ** kw) :
        self._completer = completer
        self._selector  = selector
        for k, v in pyk.iteritems (kw) :
            setattr (self, k, v)
    # end def __init__

    @Once_Property
    def elements (self) :
        if self.selected_p :
            c = self._completer
            s = self._selector
            return tuple (e.instance (c, _outer = self) for e in s.elements)
        else :
            return ()
    # end def elements

    @property
    def selected_type (self) :
        result = self._selected_type
        if TFL.is_undefined (result) :
            outer = self._outer
            if outer is not None :
                result = self._selected_type = outer.selected_type
        return result
    # end def selected_type

    @selected_type.setter
    def selected_type (self, value) :
        self._selected_type = value
    # end def selected_type

    @Once_Property
    @getattr_safe
    def value (self) :
        obj = self._completer.obj
        if self._outer is None :
            return obj
        elif self.selected_p :
            return self._selector.AQ.QR (obj)
        else :
            return self._undef
    # end def value

    @Once_Property
    @getattr_safe
    def values (self) :
        result = {}
        for _, e in self.level_elements () :
            v = e.value
            if v and e.id :
                result [e.id] = v
        return result
    # end def values

    @Once_Property
    def _repr_tail (self) :
        return "%s = %s" % (self._selector._repr_tail, self.value)
    # end def _repr_tail

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        result = getattr (self._selector, name)
        setattr (self, name, result)
        return result
    # end def __getattr__

# end class Instance

if __name__ != "__main__" :
    MOM._Export_Module ()
### __END__ MOM.Selector
