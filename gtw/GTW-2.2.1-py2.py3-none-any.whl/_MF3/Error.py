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
#    GTW.MF3.Error
#
# Purpose
#    Deal with errors during MF3 form submission
#
# Revision Dates
#    30-Jun-2014 (CT) Creation
#     1-Jul-2014 (CT) Continue creation
#     2-Jul-2014 (CT) Continue creation..
#    29-Aug-2014 (CT) Add `guard` for `e.attributes` to `finish`
#    30-Aug-2014 (CT) Use `b"..."` for `__repr__` formats
#    29-Apr-2015 (CT) Change `fields` to try canonical attribute name
#    29-Apr-2015 (CT) Change `_error_as_json_cargo` to use
#                     `MOM.Error.as_json_cargo`
#    29-Apr-2015 (CT) Add optional arguments `errors` to `List.__init__`
#    18-Dec-2015 (CT) Fix `__repr__` of `Wrapper` and `List` (3-compatibility)
#    18-Oct-2016 (CT) Add `__str__`
#    18-Oct-2016 (CT) Move `e.__keep` into `guard` for `e.attributes` (`finish`)
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _GTW                       import GTW
from   _MOM                       import MOM
from   _TFL                       import TFL

import _GTW._MF3

from   _MOM.import_MOM          import Q

import _MOM.Error

import _TFL._Meta.Once_Property
import _TFL._Meta.Property

from   _TFL._Meta.Single_Dispatch import Single_Dispatch, Single_Dispatch_Method
from   _TFL.defaultdict           import defaultdict_cb
from   _TFL.I18N                  import _, _T, _Tn
from   _TFL.predicate             import dusplit, uniq
from   _TFL.pyk                   import pyk
from   _TFL.Regexp                import Regexp, re

import _TFL._Meta.Object

from   itertools                import chain  as ichain
from   xml.sax.saxutils         import escape as html_escape

_max_rank        = 1 << 63
defaultdict_rank = defaultdict_cb.New \
    ( __name__        = "defaultdict_rank"
    , default_factory = lambda x = 0 : (_max_rank, _max_rank)
    )

MOM.Error.Error._mf3_json_attributes = \
    ( "description"
    , "explanation"
    , "head"
    , "is_required"
    , "missing_t"
    )

class _Attr_Name_Replacer_ (TFL.Meta.Object) :
    """Replace attribute names by html links to fields."""

    def __init__ (self, wrapper) :
        self.wrapper = wrapper
    # end def __init__

    def __call__ (self, text) :
        return self.pattern.sub (self._replace, text) \
            if self.field_map else text
    # end def __call__

    @TFL.Meta.Once_Property
    def field_map (self) :
        result = dict ((f.r_name, f) for f in self.wrapper.fields)
        result.update ((f.name,   f) for f in self.wrapper.fields)
        return result
    # end def field_map

    @TFL.Meta.Once_Property
    def pattern (self) :
        names = sorted \
            ( self.field_map
            , key = lambda x : (- len (x), x)
            )
        return Regexp \
            ( r"(?P<head>^|\W)"
              r"(?P<name>" + "|".join (re.escape (n) for n in names) + ")"
              r"(?P<tail>\W|$)"
            )
    # end def pattern

    def _replace (self, match) :
        result = match.group ("name")
        try :
            f  = self.field_map [result]
        except KeyError :
            pass
        else :
            head   = match.group ("head")
            tail   = match.group ("tail")
            result = """%s<a data-id="%s">%s</a>%s""" % \
                (head, f.id, html_escape (_T (f.label)), tail)
        return result
    # end def _replace

# end class _Attr_Name_Replacer_

@pyk.adapt__str__
class Wrapper (TFL.Meta.Object) :
    """Wrapper around a MOM.Error instance for a specific MF3 entity element."""

    index = -1

    def __init__ (self, entity, error) :
        self.entity = entity
        self.error  = error
    # end def __init__

    @TFL.Meta.Once_Property
    def as_json_cargo (self) :
        result = dict \
            ( self._error_as_json_cargo (self.error)
            , entity = self.entity.id
            , fields =
                [dict (fid = f.id, label = _T (f.label)) for f in self.fields]
            , id     = self.id
            )
        return result
    # end def as_json_cargo

    @TFL.Meta.Once_Property
    def attr_name_replacer (self) :
        return _Attr_Name_Replacer_ (self)
    # end def attr_name_replacer

    @TFL.Meta.Once_Property
    def fields (self) :
        def _gen (entity, error) :
            for a in error.attributes :
                try :
                    f = entity [a]
                except KeyError :
                    ### try to use canonical attribute name, if any
                    try :
                        aq = getattr (self.entity.AQ, a, None)
                        f  = entity  [aq._q_name]
                    except (KeyError, AttributeError) :
                        f  = None
                if f is not None :
                    yield f
        return sorted (_gen (self.entity, self.error), key = Q.po_index)
    # end def fields

    @TFL.Meta.Once_Property
    def id (self) :
        return "%s;ERR-%d" % (self.entity.id, self.index)
    # end def id

    @TFL.Meta.Once_Property
    def po_index (self) :
        fields = self.fields
        return fields [0].po_index if fields else -1
    # end def po_index

    @Single_Dispatch_Method
    def _error_as_json_cargo (self, error) :
        return MOM.Error.as_json_cargo (error)
    # end def _error_as_json_cargo

    @_error_as_json_cargo.add_type (MOM.Error.Error)
    def _error_as_json_cargo__Error (self, error) :
        std_cargo = error.as_json_cargo
        result    = {}
        anr       = self.attr_name_replacer
        for k in error._mf3_json_attributes :
            v = std_cargo.get (k)
            if v is not None :
                if isinstance (v, pyk.string_types) :
                    v = anr (html_escape (v))
                result [k] = v
        return result
    # end def _error_as_json_cargo__Error

    @_error_as_json_cargo.add_type (MOM.Error._Invariant_)
    def _error_as_json_cargo__Invariant (self, error) :
        result     = self._error_as_json_cargo__Error (error)
        attributes = error.attributes
        bindings   = result.get ("bindings")
        if bindings :
            ### don't include bindings of `attributes`
            result ["bindings"] = dict \
                (  (k, v)
                for k, v in pyk.iteritems (bindings)
                if  k not in attributes
                )
        return result
    # end def _error_as_json_cargo__Invariant

    @_error_as_json_cargo.add_type (MOM.Error.Required_Missing)
    def _error_as_json_cargo__Required_Missing (self, error) :
        result  = self._error_as_json_cargo__Error (error)
        missing = self.attr_name_replacer (", ".join (error.missing))
        n       = len (error.missing)
        result.update \
            ( head =
                _Tn ( "%s needs the attribute: %s"
                    , "%s needs the attributes: %s"
                    , n
                    )
                % (_T (self.entity.label), missing)
            , description =
                _Tn ( "Please enter a value for the missing attribute"
                    , "Please enter values for the missing attributes"
                    , n
                    )
            )
        result.pop ("explanation", None)
        return result
    # end def _error_as_json_cargo__Required_Missing

    def __repr__ (self) :
        result = "%s;ERR-%d: %s" % (self.entity, self.index, self.error)
        return pyk.reprify (result)
    # end def __repr__

    def __str__ (self) :
        return "%s: %s" % (self.entity, self.error)
    # end def __str__

# end class Wrapper

@pyk.adapt__bool__
@pyk.adapt__str__
class List (TFL.Meta.Object) :
    """Manage a list of errors for a specific MF3 entity element."""

    def __init__ (self, entity, errors = None) :
        self.entity          = entity
        self._raw_errors     = [] if errors is None else list (errors)
        self._wrapped_errors = None
    # end def __init__

    @property
    def wrapped_errors (self) :
        if self._wrapped_errors is None :
            self.finish ()
        return self._wrapped_errors
    # end def wrapped_errors

    def append (self, error) :
        try :
            errors = error.errors
        except AttributeError :
            self._raw_errors.append (error)
        else :
            self._raw_errors.extend (errors)
        self._wrapped_errors = None
    # end def append

    def finish (self) :
        if self._wrapped_errors is None :
            ### keep only those error instances that are lowest-rank for
            ### each and every of their `attributes`
            raw_errors = self._raw_errors
            arm = defaultdict_rank ()
            for e in raw_errors :
                try :
                    attrs = e.attributes
                except AttributeError :
                    pass
                else :
                    for a in attrs :
                        arm [a] = min (e.rank, arm [a])
                    e.__keep = all ((arm [a] == e.rank) for a in attrs)
            errors = dusplit (raw_errors, Q.__keep) [-1]
            ### wrap the filtered error instances
            entity = self.entity
            wrapped_errors = self._wrapped_errors = sorted \
                ( (Wrapper (entity, error) for error in uniq (errors))
                , key = Q.po_index
                )
            for i, w in enumerate (wrapped_errors) :
                w.index = i
    # end def finish

    def __bool__ (self) :
        return len (self) > 0
    # end def __bool__

    def __enter__ (self) :
        return self
    # end def __enter__

    def __exit__ (self, exc_type, exc_val, exc_tb) :
        self.finish ()
    # end def __exit__

    def __iter__ (self) :
        return iter (self.wrapped_errors)
    # end def __iter__

    def __len__ (self) :
        return len (self._wrapped_errors or self._raw_errors)
    # end def __len__

    def __repr__ (self) :
        return pyk.reprify (str (self))
    # end def __repr__

    def __str__ (self) :
        return "%s: %d errors" % (self.entity, len (self))
    # end def __str__

# end class List

if __name__ != "__main__" :
    GTW.MF3._Export_Module ()
### __END__ GTW.MF3.Error
