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
#    MOM.Attr.Selector
#
# Purpose
#    Selector for a group of attributes of an essential Entity
#
# Revision Dates
#     5-Jul-2011 (CT) Creation
#     7-Sep-2011 (CT) `all` added
#     7-Sep-2011 (CT) `Primary_Followers` added
#                     (plus `anchor`, `_Primary_Followers_`)
#    20-Dec-2011 (CT) Add `sig`
#    22-Dec-2011 (CT) Add `query`, change `_Selector_.__call__` to allow
#                     composite/entity attributes for `E_Type`
#     4-Apr-2012 (CT) Use `TFL.Getter.is_required` instead of home-grown lambda
#     7-May-2012 (CT) Add `editable`
#     7-May-2012 (CT) Change `Pred`, `Not_Pred`, and `_Pred_Selection_` to
#                     take a selector, not `kind` as second argument
#    17-Dec-2012 (CT) Change `_Kind_Selection_.attrs` to honor `hidden` for
#                     kind `query`
#    16-May-2013 (CT) Add `A_Type` (plus `_A_Type_Selection_`)
#     3-Jun-2013 (CT) Get attribute descriptors from `E_Type.attributes`
#     5-Jun-2013 (CT) Add `q_able`, rename `all` to `ui_attr`, define
#                     `ui_attr` as synonym for `q_able`
#    10-Jul-2013 (CT) Define `ui_attr` as `Pred (Q.show_in_ui, q_able)`
#     2-Mar-2014 (CT) Add `ui_attr_transitive`
#    21-Aug-2014 (CT) Add `ignore_missing` to `Name` and `_Name_Selection_`
#     3-May-2016 (CT) Add `mandatory`
#    ««revision-date»»···
#--

from   __future__            import absolute_import, division
from   __future__            import print_function, unicode_literals

from   _MOM                  import MOM
from   _TFL                  import TFL

from   _TFL.predicate        import uniq
from   _TFL.pyk              import pyk

from   _MOM._Attr.Filter     import Q

import _TFL._Meta.Object
import _TFL._Meta.Once_Property
import _TFL.Accessor
import _TFL.Sorted_By

import itertools

class _Selection_ (TFL.Meta.Object) :
    """Base class for attribute selections."""

    def __init__ (self, E_Type, anchor) :
        self.E_Type = E_Type
        self.anchor = anchor
    # end def __init__

    @TFL.Meta.Once_Property
    def attr_set (self) :
        return set (self.attrs)
    # end def attr_set

    @TFL.Meta.Once_Property
    def names (self) :
        return tuple (a.name for a in self.attrs)
    # end def names

    def __contains__ (self, item) :
        return item in self.attr_set
    # end def __contains__

    def __iter__ (self) :
        return iter (self.attrs)
    # end def __iter__

# end class _Selection_

class _A_Type_Selection_ (_Selection_) :
    """Attribute selection for a specific type of attributes."""

    def __init__ (self, spec, E_Type, anchor = None) :
        self.__super.__init__ (E_Type, anchor)
        self.a_type = spec.a_type
    # end def __init__

    @TFL.Meta.Once_Property
    def attrs (self) :
        E_Type = self.E_Type
        a_type = self.a_type
        sk     = TFL.Sorted_By ("rank", "name")
        result = tuple \
            (  a for a in sorted (pyk.itervalues (E_Type.attributes), key = sk)
            if isinstance (a.attr, a_type)
            )
        return result
    # end def attrs

# end class _A_Type_Selection_

class _Combo_Selection_ (_Selection_) :
    """Attribute selection assembled from `include` and `exclude` selectors."""

    exclude = None

    def __init__ (self, spec, E_Type, anchor = None) :
        self.__super.__init__ (E_Type, anchor)
        self.include = spec.include (E_Type, anchor)
        if spec.exclude is not None :
            self.exclude = spec.exclude (E_Type, anchor)
    # end def __init__

    @TFL.Meta.Once_Property
    def attrs (self) :
        exclude = self.exclude
        result  = self.include.attrs
        if exclude is not None :
            result = (a for a in result if a not in exclude)
        return tuple (result)
    # end def attrs

# end class _Combo_Selection_

class _Kind_Selection_ (_Selection_) :
    """Attribute selection for a specific kind of attributes."""

    def __init__ (self, spec, E_Type, anchor = None) :
        self.__super.__init__ (E_Type, anchor)
        self.kind = spec.kind
    # end def __init__

    @TFL.Meta.Once_Property
    def attrs (self) :
        kind = self.kind
        result = tuple (getattr (self.E_Type, kind))
        if kind == "query" :
            result = tuple (a for a in result if not a.hidden)
        return result
    # end def attrs

# end class _Kind_Selection_

class _List_Selection_ (_Selection_) :
    """Attribute selection combined from a list of selectors."""

    def __init__ (self, spec, E_Type, anchor = None) :
        self.__super.__init__ (E_Type, anchor)
        self.sels = tuple (s (E_Type, anchor) for s in spec.sels)
    # end def __init__

    @TFL.Meta.Once_Property
    def attrs (self) :
        return tuple (uniq (itertools.chain (* (s.attrs for s in self.sels))))
    # end def attrs

# end class _List_Selection_

class _Name_Selection_ (_Selection_) :
    """Attribute selection specifed by a list of names."""

    def __init__ (self, spec, E_Type, anchor = None) :
        self.__super.__init__ (E_Type, anchor)
        self._names          = tuple (spec.names)
        self._ignore_missing = spec._ignore_missing
    # end def __init__

    @TFL.Meta.Once_Property
    def attrs (self) :
        def _gen (self) :
            attributes = self.E_Type.attributes
            ignore     = self._ignore_missing
            for n in self._names :
                try :
                    yield attributes [n]
                except KeyError :
                    if not ignore :
                        raise
        return tuple (_gen (self))
    # end def attrs

    @TFL.Meta.Once_Property
    def names (self) :
        return tuple (a.name for a in self.attrs)
    # end def names

# end class _Name_Selection_

class _Pred_Selection_ (_Selection_) :
    """Attribute selection specifed by a predicate."""

    def __init__ (self, spec, E_Type, anchor = None) :
        self.__super.__init__ (E_Type, anchor)
        self.sel  = spec.sel (E_Type, anchor)
        self.pred = spec.pred
    # end def __init__

    @TFL.Meta.Once_Property
    def attrs (self) :
        pred = self.pred
        return tuple (a for a in self.sel if pred (a))
    # end def attrs

    def __contains__ (self, item) :
        return bool (self.pred (item))
    # end def __contains__

# end class _Pred_Selection_

class _Primary_Followers_ (_Selection_) :
    """Selection of primary attributes following a specific attribute."""

    def __init__ (self, spec, E_Type, anchor = None) :
        self.__super.__init__ (E_Type, anchor)
        self.anchor = spec.anchor or anchor
    # end def __init__

    @TFL.Meta.Once_Property
    def attrs (self) :
        anchor = self.E_Type.attributes [self.anchor]
        return tuple \
            (  a for a in getattr (self.E_Type, "primary")
            if a.rank > anchor.rank
            )
    # end def attrs

# end class _Primary_Followers_

class _Selector_ (TFL.Meta.Object) :
    """Base class for attributes selectors."""

    def __call__ (self, E_Type, anchor = None) :
        if isinstance (E_Type, MOM.Attr.Kind) :
            E_Type = E_Type.E_Type
        return self.Type (self, E_Type, anchor)
    # end def __call__

# end class _Selector_

class A_Type (_Selector_) :
    """Selector for a specific type of attributes."""

    Type = _A_Type_Selection_

    def __init__ (self, a_type) :
        self.a_type = a_type
    # end def __init__

    def __repr__ (self) :
        return "<MOM.Attr.Selector.Type %s>" % (self.a_type, )
    # end def __repr__

# end class A_Type

class Combo (_Selector_) :
    """Selector for a set of attributes assembled from `include` and
       `exclude` selectors.
    """

    Type = _Combo_Selection_

    def __init__ (self, include, exclude = None) :
        self.include = include
        self.exclude = exclude
    # end def __init__

# end class Combo

class Kind (_Selector_) :
    """Selector for a specific kind of attributes."""

    Type = _Kind_Selection_

    def __init__ (self, kind) :
        self.kind = kind
    # end def __init__

    def __repr__ (self) :
        return "<MOM.Attr.Selector.Kind %s>" % (self.kind, )
    # end def __repr__

# end class Kind

class List (_Selector_) :
    """Selector combined from a list of selectors."""

    Type = _List_Selection_

    def __init__ (self, * sels) :
        assert sels
        self.sels = sels
    # end def __init__

    def __repr__ (self) :
        return "<MOM.Attr.Selector.List %s>" % \
            ([repr (s) for s in self.sels], )
    # end def __repr__

# end class List

class Name (_Selector_) :
    """Selector for a group of attributes specifed by a list of names."""

    Type = _Name_Selection_

    def __init__ (self, * names, ** kw) :
        assert names
        self.names           = names
        self._ignore_missing = kw.pop ("ignore_missing", False)
        assert not kw
    # end def __init__

    def __repr__ (self) :
        return "<MOM.Attr.Selector.Name %s>" % (self.names, )
    # end def __repr__

# end class Name

class Pred (_Selector_) :
    """Selector for attributes satisfying a predicate."""

    Type = _Pred_Selection_

    def __init__ (self, pred, sel = None) :
        self.pred = pred
        self.sel  = sel if sel is not None else user
    # end def __init__

    def __repr__ (self) :
        return "<MOM.Attr.Selector.Pred %s if %s>" % (self.sel, self.pred)
    # end def __repr__

# end class Pred

class Not_Pred (Pred) :
    """Selector for attributes not satisfying a predicate."""

    def __init__ (self, pred, sel = None) :
        self.__super.__init__ ((lambda x : not pred (x)), sel)
    # end def __init__

    def __repr__ (self) :
        return "<MOM.Attr.Selector.Not_Pred %s if not %s>" % \
            (self.sel, self.pred)
    # end def __repr__

# end class Not_Pred

class Primary_Followers (_Selector_) :
    """Selector for primary attributes following a specific attribute."""

    Type = _Primary_Followers_

    def __init__ (self, anchor = None) :
        self.anchor = anchor
    # end def __init__

# end class Primary_Followers

necessary          = Kind     ("necessary")
optional           = Kind     ("optional")
primary            = Kind     ("primary")
query              = Kind     ("query")
q_able             = Kind     ("q_able")
required           = Kind     ("required")
sig                = Kind     ("sig_attr")
user               = Kind     ("user_attr")

ui_attr            = Pred     (Q.show_in_ui,        q_able)
ui_attr_transitive = Pred     (Q.q_able_transitive, ui_attr)
editable           = List     (primary,             user)
mandatory          = List     (primary,             required)

P_optional         = Not_Pred (Q.is_required,       user)
P_required         = Pred     (Q.is_required,       user)

if __name__ != "__main__" :
    MOM.Attr._Export_Module ()
### __END__ MOM.Attr.Selector
