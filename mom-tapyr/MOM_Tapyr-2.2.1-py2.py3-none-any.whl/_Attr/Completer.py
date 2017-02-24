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
#    MOM.Attr.Completer
#
# Purpose
#    Model field and entity completers for MOM attributes
#
# Revision Dates
#     5-Jul-2011 (CT) Creation
#     6-Jul-2011 (CT) Creation continued
#    17-Jul-2011 (CT) Creation continued.. (major surgery)
#    22-Jul-2011 (CT) `__call__` changed to use `E_Type.ac_query_attrs`
#                     instead of `attr_completion`
#    22-Jul-2011 (CT) `all_names` added
#    27-Jul-2011 (CT) `entity_p` added
#    15-Sep-2011 (CT) `Completer.__init__` changed to save `spec`
#    20-Sep-2011 (CT) `all_names` and `dependents` removed
#    20-Sep-2011 (CT) `C_Completer` and `E_Completer` (plus their `_Spec`) added
#     7-Nov-2011 (CT) Change `Completer.__call__` to query results for
#                     `treshold == 0` without `fs`
#    13-Dec-2012 (CT) Add arguments `ETM_R`, `AQ` to `Completer.__call__`
#    25-Apr-2013 (CT) Add optional arg `xtra_filter` to `Completer.__call__`
#     7-May-2014 (CT) Add `** kw` to `copy`; use in `embedded`
#     8-May-2014 (CT) Add `_Nested_Completer_Spec_.default_selector`
#    30-Mar-2015 (CT) Allow `buddies` as single argument for `Completer_Spec`
#                     + add `treshold` to `_Nested_Completer_Spec_.__init__`
#                     + factor `default_selector` to `Completer_Spec`
#     9-Sep-2016 (CT) Add `S_Completer`.`S_Completer_Spec`
#    ««revision-date»»···
#--

from   __future__            import absolute_import, division
from   __future__            import print_function, unicode_literals

from   _MOM                  import MOM
from   _TFL                  import TFL

from   _TFL.predicate        import uniq
from   _TFL.pyk              import pyk

import _MOM._Attr.Selector

import _TFL._Meta.Object

class Completer (TFL.Meta.Object) :
    """Attribute completer instance for a specific E_Type."""

    buddies    = ()
    kind       = "Atom"
    embedded_p = False

    def __init__ (self, acs, attr, E_Type) :
        self.etn      = E_Type.type_name
        self.name     = name = attr.name
        self.spec     = acs
        self.treshold = acs.treshold
        if acs.buddies :
            self.buddies = acs.buddies (E_Type, name).names
        self.entity_p = set (self.names) == set (E_Type.epk_sig)
    # end def __init__

    def copy (self, ** kw) :
        cls    = self.__class__
        result = cls.__new__   (cls)
        result.__dict__.update (self.__dict__, ** kw)
        return result
    # end def copy

    def __call__ \
            ( self, scope, val_dict
            , ETM_R       = None
            , AQ          = None
            , xtra_filter = None
            ) :
        ETM = scope [self.etn]
        if ETM_R is None :
            ETM_R = ETM
        vd  = dict  ((k, v) for k, v in pyk.iteritems (val_dict) if v != "")
        fs  = tuple (ETM.ac_query_attrs (self.names, vd, AQ))
        if fs or self.treshold == 0 :
            q = ETM_R.query_s (* fs)
            if xtra_filter is not None :
                q = q.filter (xtra_filter)
            return q.distinct ()
        return TFL.Q_Result (())
    # end def __call__

    @property
    def as_json_cargo (self) :
        result = dict \
            ( entity_p = self.entity_p
            , names    = list (self.names)
            , treshold = self.treshold
            )
        if self.embedded_p :
            result ["embedded_p"] = True
        return result
    # end def as_json_cargo

    @TFL.Meta.Once_Property
    def names (self) :
        return tuple (uniq ((self.name, ) + self.buddies))
    # end def names

    def embedded (self, spec) :
        return self.copy (embedded_p = True, ** (spec or {}))
    # end def embedded

# end class Completer

class _Nested_Completer_ (Completer) :

    def __init__ (self, acs, attr, E_Type) :
        self.__super.__init__ (acs, attr, E_Type)
        self.nested_specs = acs.nested_specs
        self.nested = []
    # end def __init__

    def derived (self, nested) :
        if nested is not None :
            name   = nested.name
            result = nested.embedded (self.nested_specs.get (name, {}))
            self.nested.append (result)
            return result
    # end def derived

# end class _Nested_Completer_

class C_Completer (_Nested_Completer_) :
    """A_Composite completer instance for a specific E_Type."""

    kind       = "Composite"

# end class C_Completer

class E_Completer (_Nested_Completer_) :
    """A_Id_Entity completer instance for a specific E_Type."""

    kind       = "Id_Entity"

# end class E_Completer

class S_Completer (_Nested_Completer_) :
    """_A_Structured_ completer instance for a specific E_Type."""

    kind       = "Structured"

# end class S_Completer

class Completer_Spec (TFL.Meta.Object) :
    """Attribute completer specification for a MOM attribute."""

    buddies          = None
    default_selector = None
    treshold         = 1
    Type             = Completer

    def __init__ (self, treshold = None, buddies = None) :
        Selector = MOM.Attr.Selector._Selector_
        if isinstance (treshold, Selector) and buddies is None:
            treshold, buddies = None, treshold
        if treshold is not None :
            self.treshold = treshold
        if buddies is None :
            buddies = self.default_selector
        if buddies is not None :
            assert isinstance (buddies, Selector), \
                "Expected Attr.Selector for `buddies`, got `%s`" % (buddies, )
            self.buddies = buddies
    # end def __init__

    def __call__ (self, attr, E_Type) :
        return self.Type (self, attr, E_Type)
    # end def __call__

# end class Completer_Spec

class _Nested_Completer_Spec_ (Completer_Spec) :

    def __init__ (self, treshold = None, buddies = None, ** kw) :
        self.__super.__init__ (treshold = treshold, buddies = buddies)
        self.nested_specs = kw
    # end def __init__

# end class _Nested_Completer_Spec_

class C_Completer_Spec (_Nested_Completer_Spec_) :
    """Attribute completer specification for A_Composite."""

    Type             = C_Completer

# end class C_Completer_Spec

class E_Completer_Spec (_Nested_Completer_Spec_) :
    """Attribute completer specification for A_Id_Entity."""

    Type             = E_Completer
    default_selector = MOM.Attr.Selector.primary

# end class E_Completer_Spec

class S_Completer_Spec (_Nested_Completer_Spec_) :
    """Attribute completer specification for _A_Structured_."""

    Type             = S_Completer
    default_selector = MOM.Attr.Selector.editable

# end class S_Completer_Spec

if __name__ != "__main__" :
    MOM.Attr._Export ("*", "_Nested_Completer_")
### __END__ MOM.Attr.Completer
