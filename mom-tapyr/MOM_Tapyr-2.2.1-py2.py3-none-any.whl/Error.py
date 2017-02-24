# -*- coding: utf-8 -*-
# Copyright (C) 2008-2016 Mag. Christian Tanzer. All rights reserved
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
#    MOM.Error
#
# Purpose
#    Provide exception classes for MOM
#
# Revision Dates
#    18-Sep-2009 (CT) Creation (factored from TOM.Error)
#    12-Oct-2009 (CT) `Invalid_Primary_Key` added
#    21-Oct-2009 (CT) Creation continued
#    24-Nov-2009 (CT) `No_Such_Object` added
#    24-Nov-2009 (CT) `Error.__str__` changed
#    26-Nov-2009 (CT) Use `except ... as ...` (3-compatibility)
#     3-Dec-2009 (CT) Optional argument `exc` added to `Invalid_Attribute`
#    15-Jan-2010 (MG) `Attribute_Syntax_Error.__unicode__` added
#    12-Feb-2010 (CT) `Invariant_Error._attribute_values` changed to use `%r`
#                     instead of `%s` for val
#    12-Feb-2010 (CT) `Invariant_Errors.__init__` redefined to sort `errors`
#    11-Mar-2010 (CT) `Mandatory_Missing` added
#    16-Jun-2010 (CT) `__str__` changed to `.encode` result of `__unicode__`
#    17-Jun-2010 (CT) Use `TFL.I18N.encode_o` instead of home-grown code
#    22-Jun-2010 (CT) `is_mandatory` added
#    30-Jun-2010 (CT) `Readonly_DB` added
#     8-Feb-2011 (CT) s/Required/Necessary/, s/Mandatory/Required/
#    22-Mar-2011 (MG) `Commit_Conflict` added
#     8-Nov-2011 (CT) Add `Required_Empty` and `any_required_empty`
#    30-Jan-2012 (CT) Change `Name_Clash` to show `.type_name`
#    12-Apr-2012 (CT) Change `Required_Missing` to use `I18N`,
#                     make it compatible to `Invariant_Error`
#    15-Apr-2012 (CT) Complete overhaul: cleanup, renamings, reparentings, I18N
#    16-Apr-2012 (CT) Continue complete overhaul: __super, refactoring, cleanup
#    17-Apr-2012 (CT) Add `as_json_cargo`, factor `Invariant.bindings`, cleanup
#    19-Apr-2012 (CT) Generalize `_formatted_bindings` for use in
#                     `Required_Missing.description`
#    19-Apr-2012 (CT) Use translated `.ui_name` instead of `.type_name`
#    19-Apr-2012 (CT) Change `_formatted_bindings` to remove @*$&@*% `u` prefix
#    20-Apr-2012 (CT) Add `_Invariant_.all_bindings`, put them into
#                     `as_json_cargo` as `bindings`
#    20-Apr-2012 (CT) Factor `Invariants._sort_key` and robustify
#    20-Apr-2012 (CT) Improve output of `Required_Missing`
#    20-Apr-2012 (CT) Add `Required_Missing.missing_t`
#    23-Apr-2012 (CT) Add `Ambiguous_Epk`
#    27-Apr-2012 (CT) Add `ui_display` to json cargo of `extra_links`
#    27-Apr-2012 (CT) Change `_Invariant_.bindings` to apply `unicode` to values
#    27-Apr-2012 (CT) Add and use `Invariants._flattened`
#    30-Apr-2012 (CT) Add `Duplicate_Link.__init__`
#    11-May-2012 (CT) Add message to `assert` in `Ambiguous_Epk.__init__`
#    11-May-2012 (CT) Change `Attribute_Syntax` to use
#                     `self.attribute.name`, not `self.attribute`, for json
#     1-Aug-2012 (CT) Add `Destroyed_Entity`
#     8-Aug-2012 (CT) Derive base class from `StandardError`, not `Exception`
#                     (too many exception clauses still use `StandardError`)
#    10-Aug-2012 (MG) Use `getattr` too access pid `Invariant.__init__`
#    12-Aug-2012 (CT) Add `Not_Unique`
#    10-Sep-2012 (CT) Fix name error in `Not_Unique`
#    11-Sep-2012 (CT) Derive `Not_Unique` from `_Invariant_`
#    12-Dec-2012 (CT) Change `Attribute.bindings` to format `value`
#    29-Jan-2013 (CT) Improve text of `Name_Clash`
#    30-Jan-2013 (CT) Fix `Not_Unique`, remove `Duplicate_Link`
#    26-Feb-2013 (CT) Improve text of `Multiplicity`
#    26-Feb-2013 (CT) Improve text of `Not_Unique`
#     1-Mar-2013 (CT) Use `_real_name` for `Error`
#    18-Apr-2013 (CT) Change `Link_Error` to `Wrong_Type`
#    25-Apr-2013 (CT) Add `Permission`
#     6-May-2013 (CT) Change `Error.as_unicode` to use `__doc__`, unless `.args`
#    11-Jun-2013 (CT) Add guard to `Attribute.bindings`
#    21-Aug-2013 (CT) Guard `is_required` in `Attribute_Syntax.__init__`
#    14-Jan-2014 (CT) Robustify `Attribute.__init__` and `.bindings`
#    17-Feb-2014 (CT) Improve `No_Such_Directory`, `No_Such_File`
#     1-May-2014 (CT) Use `pyk.encoded`, not `str`
#    30-Jun-2014 (CT) Fix `embed` (replace attribute keys in `val_disp`)
#    30-Jun-2014 (CT) Set `Required_Missing.attributes` to `missing`,
#                     not `needed`; set `Required_Missing.val_disp` to `kw`
#     2-Jul-2014 (CT) Improve `Attribute_Syntax`
#     3-Jul-2014 (CT) Redefine `Required_Empty.head`
#     1-Sep-2014 (CT) Fix translatability of `Permission.as_unicode`
#     9-Oct-2014 (CT) Use `portable_repr`
#    10-Oct-2014 (CT) Use `pyk.reprify`, not `pyk.encoded`
#    15-Oct-2014 (CT) Add `db_meta_data` to `Incompatible_DB_Version`
#     2-Apr-2015 (CT) Fix various encoding and L10N issues
#                     * Change `__repr__` to use `reprify (text_type (self))`
#                     * Override `__repr__` for `_Invariant_`, `Invariants`
#                     * Use `decoded`, not `text_type`,  in `str_arg`
#                     * Use `decoded`, not `reprify`, in `bindings`,
#                     * Use `decoded` in  `__init__` methods
#                     * Don't include `inv` in `args` of `Invariant`
#                     * Add `_T` for `description`, `explanation`
#    13-Apr-2015 (CT) Add `json_encode_exception`, `json_encode_error`
#    21-Jun-2016 (CT) Fix typos in `Quant._violator_values`
#    22-Jun-2016 (CT) Fix `bvar` handling in `Quant._violator_values`
#                     + Allow nested names in `bvar`, e.g.,
#                       `((a1, b1), (a2, b2))`
#    22-Jun-2016 (CT) Use `TFL.ui_display`, not `portable_repr`, for
#                     `Quant._violator_values`
#    18-Jul-2016 (CT) Add exception handler to `Invariants.embed`
#    10-Aug-2016 (CT) Add `Not_Exclude`
#    ««revision-date»»···
#--

from   __future__               import unicode_literals

from   _TFL                     import TFL
from   _MOM                     import MOM

import _CAL.ui_display

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL.Decorator           import getattr_safe
from   _TFL.I18N                import _, _T, _Tn
from   _TFL.predicate           import *
from   _TFL.portable_repr       import portable_repr
from   _TFL.pyk                 import pyk
from   _TFL.Record              import Record
from   _TFL.Regexp              import Regexp
from   _TFL.ui_display          import ui_display

import _TFL._Meta.Object
import _TFL.Caller
import _TFL.Accessor
import _TFL.I18N
import _TFL.json_dump
import _TFL.Record

import itertools

class Exception_Handled (BaseException) :
    """Raised after an exception was already handled to bail out from an
       arbitrary position in a call-tree. Should be ignored further up.
    """
# end class Exception_Handled

def as_json_cargo (* excs) :
    def _gen (excs) :
        for exc in excs :
            try :
                cargo = exc.as_json_cargo
            except AttributeError :
                cargo = dict \
                    ( description = pyk.text_type (exc)
                    , head        = exc.__class__.__name__
                    )
            if isinstance (cargo, (list, tuple)) :
                for c in cargo :
                    yield c
            else :
                yield cargo
    return list (_gen (excs))
# end def as_json_cargo

@pyk.adapt__str__
class _MOM_Error_ \
          ( TFL.Meta.BaM
              (Exception, metaclass = TFL.Meta.Object.__class__)
          ) :
    """Root class of MOM exceptions"""

    _real_name       = "Error"

    arg_sep          = ", "
    is_required      = False

    _json_attributes = \
        ( "as_text"
        , "is_required"
        )

    _json_map        = dict \
        ( as_text    = "description"
        )

    _rank_d          = 1
    _rank_s          = 1

    @Once_Property
    def as_json_cargo (self) :
        json_map = self._json_map
        result   = {}
        for k in self._json_attributes :
            v = getattr (self, k, None)
            if v :
                result [json_map.get (k, k)] = v
        return result
    # end def as_json_cargo

    @Once_Property
    def as_text (self) :
        result = self.arg_sep.join (self.str_arg (self.args))
        if not result :
            result = _T (self.__class__.__doc__)
        return result
    # end def as_text

    @Once_Property
    def encoded (self) :
        return pyk.encoded (self.as_text)
    # end def encoded

    @Once_Property
    def rank (self) :
        return (self._rank_s, self._rank_d)
    # end def rank

    def str_arg (self, args) :
        for a in args :
            try :
                s = pyk.decoded (a)
            except Exception as exc :
                s = "%s --> %s" % (portable_repr (a), exc)
            yield s
    # end def str_arg

    def __eq__ (self, other) :
        return self.encoded == pyk.encoded (other)
    # end def __eq__

    def __le__ (self, other) :
        return self.encoded <= pyk.encoded (other)
    # end def __le__

    def __lt__ (self, other) :
        return self.encoded < pyk.encoded (other)
    # end def __lt__

    def __hash__ (self) :
        return hash (self.encoded)
    # end def __hash__

    def __repr__ (self) :
        return pyk.reprify (pyk.text_type (self))
    # end def __repr__

    def __str__ (self) :
        return self.as_text
    # end def __str__

Error = _MOM_Error_ # end class

class _Invariant_ (Error) :

    attr_map_eo      = {} ### map embedded to original attribute names
    attr_map_oe      = {} ### map original to embedded attribute names
    attributes       = ()
    description      = ""
    description_plus = ""
    explanation      = ""
    extra_links      = ()
    indent           = " " * 4
    val_disp         = {}

    _json_attributes = \
        ( "all_bindings"
        , "attributes"
        , "description"
        , "explanation"
        , "head"
        , "is_required"
        )
    _json_map        = dict \
        ( all_bindings = "bindings"
        )

    def __init__ (self, obj, raw = False) :
        self.obj = obj
        self.raw = raw
    # end def __init__

    @Once_Property
    def all_bindings (self) :
        result = self.bindings
        result.extend \
            ((a, None) for a in self.attributes if a not in self.val_disp)
        return sorted (result)
    # end def all_bindings

    @Once_Property
    def as_json_cargo (self) :
        result = self.__super.as_json_cargo
        xtra   = sorted \
            ( (   (pid, d)
              for pid, d in
                    (   (getattr (x, "pid", None), x.ui_display)
                    for x in self.extra_links
                    )
              if  pid is not None
              )
            , key = TFL.Getter [1]
            )
        if xtra :
            result ["extra_links"] = xtra
        return result
    # end def as_json_cargo

    @Once_Property
    def bindings (self) :
        return sorted (pyk.iteritems (self.val_disp))
    # end def bindings

    @property
    def head (self) :
        return _T ("Invariant error")
    # end def head

    def assertion (self) :
        result = []
        for info in self.head, self.description, self.explanation :
            if info :
                result.append (pyk.decoded (info))
        return ("\n" + self.indent).join (result)
    # end def assertion

    def embed (self, obj, c_name, c_attr) :
        amap_eo = self.attr_map_eo
        if amap_eo is self.__class__.attr_map_eo :
            amap_eo = self.attr_map_eo = {}
            amap_oe = self.attr_map_oe = {}
        val_disp = self.val_disp
        self.val_disp = {}
        for a in self.attributes :
            k = ".".join ((c_name, a))
            amap_eo [k] = a
            amap_oe [a] = k
            if a in val_disp :
                self.val_disp [k] = val_disp [a]
        self.attributes = tuple (amap_oe [a] for a in self.attributes)
    # end def embed

    def _clean_this (self, s) :
        return s.replace ("this.", "").strip ()
    # end def _clean_this

    def _formatted_bindings (self, bindings = None) :
        if bindings is None :
            bindings = self.bindings
        for k, v in bindings :
            if isinstance (v, (list, tuple)) :
                v = ", ".join \
                    ("%s" % (portable_repr (pyk.decoded (x)), ) for x in v)
            elif v is None or v == "''":
                v = _T ("None")
            yield "%s = %s" % (k, v)
    # end def _formatted_bindings

    def __repr__ (self) :
        obj    = self.obj
        obj_p  = isinstance (obj, MOM.Entity)
        fmt    = "<%(name)s: %(obj)s, %(repr)s>" if obj_p \
            else "<%(name)s: (%(repr)s>"
        result = fmt % dict \
            ( name = _T (self.__class__.__name__)
            , obj  = obj.ui_repr if obj_p else ""
            , repr = pyk.decoded (self.__super.__repr__ ())
            )
        return pyk.reprify (result)
    # end def __repr__

# end class _Invariant_

class Ambiguous_Epk (_Invariant_) :

    arg_sep        = ". "
    raw            = False

    def __init__ (self, e_type, epk, kw, count, * matches) :
        assert 1 < count <= len (matches), \
            "count = %s, matches = %s" % (count, matches)
        self.e_type     = e_type
        self.epk        = ui_display (epk)
        self.kw         = kw
        self.count      = count
        self.matches    = tuple (m.ui_display for m in matches)
        self.FO         = matches [0].FO
    # end def __init__

    @Once_Property
    def all_bindings (self) :
        result = self.bindings
        given  = dict (result)
        e_type = self.e_type
        result.extend \
            ( (a.name, None)
            for a in itertools.chain (e_type.primary, e_type.required)
            if  a.name not in given
            )
        return sorted (result)
    # end def all_bindings

    @Once_Property
    def args (self) :
        attrs = _T ("Attributes given: (%s)") % \
            ( ", ".join
                ( self._formatted_bindings
                    ((k, v) for k, v in self.bindings if v is not None)
                )
            )
        return (self.head, attrs, self.description)
    # end def args

    @Once_Property
    def bindings (self) :
        FO = self.FO
        return sorted \
            (   (k, (pyk.decoded (FO (k, v)) if v is not None else v))
            for (k, v) in itertools.chain
                ( (zip (self.e_type.epk_sig, self.epk))
                , pyk.iteritems (self.kw)
                )
            )
    # end def bindings

    @Once_Property
    def head (self) :
        return \
            ( _T
              ("The given attributes match %s entities instead of one or none")
            % (self.count, )
            )
    # end def head

    @Once_Property
    def description (self) :
        matches = self.matches
        more    = self.count - len (matches)
        result  = \
            ( _T ("Matching entities: %s%s")
            % ("; ".join (matches), " ..." if more else "")
            )
        return result
    # end def description

# end class Ambiguous_Epk

class Attribute (Error) :

    _json_attributes = \
        ( "as_text"
        , "attributes"
        , "bindings"
        , "is_required"
        )

    def __init__ (self, entity, name, val, kind = "unknown", exc = None) :
        if entity :
            msg = \
                ( _T ("Can't set %s attribute %s.%s to %s")
                % (_T (kind), entity.type_base_name, name, portable_repr (val))
                )
        else :
            msg = \
                ( _T ("Can't set %s attribute %s to %s")
                % (_T (kind), name, portable_repr (val))
                )
        if exc :
            msg = "%s.\n    %s" % (msg, exc)
        self.args       = (msg, )
        self.entity     = entity
        self.kind       = kind
        self.attribute  = name
        self.attributes = (name, )
        self.value      = val
    # end def __init__

    @Once_Property
    def bindings (self) :
        if self.entity :
            FO    = self.entity.FO
            name  = self.attribute
            try :
                fov   = FO (name, self.value)
            except Exception :
                value = pyk.decoded (self.value)
            else :
                value = pyk.decoded (fov)
            return ((name, value), )
    # end def bindings

    def correct (self) :
        pass
    # end def correct

# end class Attribute

class Attribute_Set (Attribute, AttributeError) :
    """Attribute can't be set."""

# end class Attribute_Set

class Attribute_Syntax (_Invariant_, ValueError) :
    """Raised for syntax errors in attributes of MOM objects/links."""

    _rank_s        = -10

    _json_attributes = ("description", ) + tuple \
        (a for a in _Invariant_._json_attributes if a != "as_text")

    class inv :
        name       = "syntax_valid"

    def __init__ (self, obj, attr, val, exc_str = "") :
        self.__super.__init__ (obj)
        self.args         = (obj, attr, val, exc_str)
        self.obj          = obj
        self.attribute    = attr
        self.attributes   = (attr.name, )
        try :
            self.is_required  = attr.is_required
        except AttributeError :
            self.is_required  = getattr (attr.kind, "is_required", False)
        self.value        = val
        self.exc_str      = pyk.decoded (exc_str)
    # end def __init__

    @Once_Property
    def as_text (self) :
        attr   = self.attribute
        result = \
            ( _T ( "`%s` for : `%s`"
                   "\n     expected type  : %s"
                   "\n     got      value : %s"
                 )
            % ( self.exc_str or _T ("Syntax error")
              , portable_repr (attr)
              , portable_repr (attr.typ)
              , portable_repr (self.value)
              )
            )
        if attr.syntax :
            result = "\n".join ((result, _T (attr.syntax)))
        return result
    # end def as_text

    @Once_Property
    def bindings (self) :
        return ((self.attributes [0], self.value), )
    # end def bindings

    @Once_Property
    @getattr_safe
    def description (self) :
        if self.attribute.syntax :
            return "%s: %s" % (_T ("Syntax"), _T (self.attribute.syntax))
        elif self.attribute.example :
            return "%s: %s" % (_T ("Example"), _T (self.attribute.example))
    # end def description

    @Once_Property
    def explanation (self) :
        if self.exc_str :
            return "%s: %s" % (_T ("Exception"), self.exc_str)
    # end def explanation

    @Once_Property
    def head (self) :
        return \
            ( _T( "Syntax error for %s: "
                  "\n  expected type `%s`\n  got value `%s`"
                )
            % (self.attributes [0], _T (self.attribute.typ), self.value)
            )
    # end def head

# end class Attribute_Syntax

class Attribute_Unknown (Attribute, AttributeError) :
    """An unknown name was used to set an attribute."""

    def correct (self) :
        """Try to correct this error."""
        self.entity.correct_unknown_attr (self)
    # end def correct

# end class Attribute_Unknown

class Attribute_Value (Attribute, ValueError) :
    """Invalid value for attribute."""

# end class Attribute_Value

class Circular_Link (Error) :
    """Raised when a link is added to an association which results directly or indirectly in a circular link."""
# end class Circular_Link

class DB (Error) :
    pass
# end class DB

class Commit_Conflict (DB) :
    """Conflict during commit of database."""
# end class Commit_Conflict

class Destroyed_Entity (Error) :
    """The entity was already destroyed and cannot be used anymore."""
# end class Destroyed_Entity

class Empty_DB (DB) :
    """Database is empty."""
# end class Empty_DB

class Incompatible_DB_Version (DB) :
    """Database version is not compatible to software version."""

    def __init__ (self, db_meta_data, * args, ** kw) :
        self.db_meta_data = db_meta_data
        self.__super.__init__ (* args, ** kw)
    # end def __init__

# end class Incompatible_DB_Version

class Inconsistent_Attribute (Error) :
    pass
# end class Inconsistent_Attribute

class Inconsistent_Predicate (Error) :
    pass
# end class Inconsistent_Predicate

class Invariant (_Invariant_) :

    def __init__ (self, obj, inv) :
        self.__super.__init__ (obj)
        pid               = getattr (obj, "pid", None)
        self.args         = (obj, ) if pid else (_T (obj.ui_name), )
        self.inv          = inv
        self.is_required  = inv.is_required
        self.attributes   = sorted (inv.attributes + inv.attr_none)
        self.extra_links  = list   (inv.extra_links)
        self.val_disp     = dict   (inv.val_disp)
        description       = _T     (inv.description)
        try :
            self.inv_desc = description % TFL.Caller.Object_Scope (obj)
        except TypeError :
            self.inv_desc = description
    # end def __init__

    @Once_Property
    def as_text (self) :
        return self._as_string \
            (head = "%s `%s` : " % (_T ("Condition"), _T (self.inv.name)))
    # end def as_text

    @Once_Property
    def description (self) :
        inv    = self.inv
        more   = inv.error_info
        result = []
        if inv.description and inv.assertion :
            result.append ("(%s)" % (inv.assertion, ))
        if more :
            result.extend (more)
        return "\n".join (result)
    # end def description

    @Once_Property
    def description_plus (self) :
        description = self.description
        result      = self._tail ("")
        if description :
            result = "\n".join ((description, "", result))
        return self._clean_this (result)
    # end def description_plus

    @Once_Property
    def explanation (self) :
        return _T (self.inv.explanation)
    # end def explanation

    @Once_Property
    def head (self) :
        return self.inv_desc or self.inv.assertion
    # end def head

    @Once_Property
    def _rank_d (self) :
        return self.inv.rank
    # end def _rank_d

    def assertion (self) :
        indent = self.indent
        return self._as_string (sep = "\n" + indent, indent = indent)
    # end def assertion

    def _as_string (self, sep = " ", head = "", indent = None) :
        desc   = self.description
        result = [head]
        if self.head :
            result.extend ((self.head, sep))
        if desc :
            result.append (desc)
        result.append (self._tail (indent))
        return self._clean_this ("".join (result))
    # end def _as_string

    def _tail (self, indent = None) :
        if indent is None :
            indent = self.indent
        result = []
        sep    = "\n" + indent
        if self.bindings :
            result = itertools.chain ([""], self._formatted_bindings ())
        return sep.join (result)
    # end def _tail

# end class Invariant

class Invariants (Error) :

    arg_sep = "\n  "

    def __init__ (self, errors) :
        errors = self.errors = sorted \
            (self._flattened (errors), key = self._sort_key)
        self.__super.__init__ (* errors)
    # end def __init__

    @Once_Property
    def as_json_cargo (self) :
        return list (e.as_json_cargo for e in self.errors)
    # end def as_json_cargo

    @property
    def any_required_empty (self) :
        return any (isinstance (e, Required_Empty) for e in self.errors)
    # end def any_required_empty

    def embed (self, obj, c_name, c_attr) :
        for e in self.errors :
            try :
                embed = e.embed
            except AttributeError :
                logging.warning \
                    ( "Error class %s doesn't define `embed`\n    %s"
                    % (e.__class__, e)
                    )
            else :
                embed (obj, c_name, c_attr)
    # end def embed

    def _flattened (self, errors) :
        for e in errors :
            ee = getattr (e, "errors", None)
            if ee is not None :
                e = tuple (ee)
            if isinstance (e, (list, tuple)) :
                for x in self._flattened (e) :
                    yield x
            else :
                yield e
    # end def _flattened

    def _sort_key (self, err) :
        try :
            return err.inv.name
        except AttributeError :
            return pyk.text_type (err)
    # end def _sort_key

    def __repr__ (self) :
        result = "<%s: %s>" % \
            ( _T (self.__class__.__name__)
            , "; ".join (pyk.decoded (repr (e)) for e in self.errors)
            )
        return pyk.reprify (result)
    # end def __repr__

# end class Invariants

class Link_Scope_Mix (Error) :
    """Raised when objects with different home scopes are put into a link."""
# end class Link_Scope_Mix

class Multiplicity (Error) :
    """Raised when the maximum multiplicity for an association is violated."""

    def __init__ (self, e_type, role, r_obj, epk, * links) :
        self.e_type       = e_type
        self.role         = role
        self.type_name    = e_type.ui_name
        self.l_ui_display = pyk.decoded (pyk.reprify (epk))
        self.r_ui_display = r_obj.ui_repr
        self.extra_links  = tuple \
            ( TFL.Record
                ( pid        = getattr (x, "pid", None)
                , ui_display = pyk.decoded (x.ui_repr)
                , type_name  = _T (x.ui_name)
                )
            for x in links
            )
    # end def __init__

    @Once_Property
    def as_text (self) :
        return self.description
    # end def as_text

    @Once_Property
    def head (self) :
        fmt = _T \
            ( "The new definition of %s %s would exceed the maximum "
              "number [%s] of links allowed for %s."
            )
        return \
            ( fmt
            % ( self.type_name, self.l_ui_display
              , self.role.max_links, self.r_ui_display
              )
            )
    # end def head

    @Once_Property
    def description (self) :
        result = [self.head]
        extras = tuple (x.ui_display for x in self.extra_links)
        result.append \
            ( _T ("Already existing:\n    %s") % ("\n    ".join (extras), ))
        return "\n  ".join (result)
    # end def description

# end class Multiplicity

class Multiplicity_Errors (Error) :

    arg_sep = "\n  "

    @Once_Property
    def as_json_cargo (self) :
        return list (a.as_json_cargo for a in self.args)
    # end def as_json_cargo

# end class Multiplicity_Errors

class Name_Clash (Error) :
    """Raised when one name is used for more than one object."""

    arg_sep = " "

    def __init__ (self, new, old) :
        otn = _T (old.ui_name) if old else ""
        otd = ("`%s`" % (old.ui_display, )) if old else _T ("object")
        self.__super.__init__ \
            ( _T ("new definition of %s `%s` clashes with existing %s %s")
            % (_T (new.ui_name), new.ui_display, otn, otd)
            )
    # end def __init__

# end class Name_Clash

class No_Such_Directory (Error) :
    """Raised for a file specification containing a non-existent directory."""

    def __init__ (self, d) :
        self.__super.__init__ (_T ("Directory `%s` not found") % (d, ))
    # end def __init__

# end class No_Such_Directory

class No_Such_Entity (Error) :
    """Raised if an unknown epk is passed for an object or link-role."""
# end class No_Such_Entity

class No_Such_File (Error) :
    """Raised for a file specification of a non-existing file."""

    def __init__ (self, d) :
        self.__super.__init__ (_T ("File `%s` not found") % (d, ))
    # end def __init__

# end class No_Such_File

class Not_Unique (_Invariant_) :
    """Set of attributes is not unique for each entity."""

    def __init__ (self, obj, inv) :
        self.__super.__init__ (obj)
        self.attributes   = sorted (inv.attributes + inv.attr_none)
        self.count        = len (inv.clashes)
        self.extra_links  = tuple \
            ( TFL.Record
                ( pid        = getattr (x, "pid", None)
                , ui_display = pyk.decoded (x.ui_repr)
                , type_name  = _T (x.ui_name)
                )
            for x in inv.extra_links
            )
        self.inv          = inv
        self.type_name    = _T (obj.ui_name)
        self.ui_display   = pyk.decoded (obj.ui_repr)
        self.args         = (self.type_name, self.ui_display)
        description       = _T (inv.description)
        try :
            self.inv_desc = description % TFL.Caller.Object_Scope (obj)
        except TypeError :
            self.inv_desc = description
    # end def __init__

    @Once_Property
    def as_text (self) :
        return self.description
    # end def as_text

    @Once_Property
    def head (self) :
        return \
            ( _T
                ( "The new definition of %s %s would clash with %s "
                  "existing entities"
                )
            % (self.type_name, self.ui_display, self.count)
            )
    # end def head

    @Once_Property
    def description (self) :
        result = [self.inv_desc] if self.inv_desc else []
        result.append  (self.head)
        extras = tuple (x.ui_display for x in self.extra_links)
        result.append \
            ( _T ("Already existing:\n    %s") % ("\n    ".join (extras), ))
        return "\n  ".join (result)
    # end def description

# end class Not_Unique

class Not_Exclude (Not_Unique) :
    """Set of attributes is not exclusive for each entity."""
# end class Not_Exclude

class Partial_Type (Error) :
    """Raised when creation of an object of a partial type is tried."""

    attributes       = ()

# end class Partial_Type

class Permission (_Invariant_, ValueError) :
    """You are not allowed to use that object in this context"""

    class inv :
        name       = "Permission_Error"

    def __init__ (self, obj, attr, val, allowed) :
        self.__super.__init__ (obj)
        self.args         = (obj, attr, val.ui_display)
        self.obj          = obj
        self.attribute    = attr
        self.attributes   = (attr.name, )
        self.is_required  = attr.is_required
        self.value        = val.ui_display
        self.allowed      = tuple (x.ui_display for x in allowed)
    # end def __init__

    @Once_Property
    def as_text (self) :
        attr   = self.attribute
        result = \
            ( _T( "Permission error for : `%s`;"
                  "\n     allowed  values : (%s),"
                  "\n     got      value  : `%s`"
                )
            % (attr.ui_name_T, ", ".join (self.allowed), self.value)
            )
        return result
    # end def as_text

    @Once_Property
    def bindings (self) :
        return ((self.attribute.name, self.value), )
    # end def bindings

    @Once_Property
    def head (self) :
        return pyk.text_type (self)
    # end def head

# end class Permission

class Quant (Invariant) :
    """Raised when a quantifier invariant of a MOM object/link is violated."""

    def __init__ (self, obj, inv, violators, violators_attr) :
        self.violators      = violators
        self.violators_attr = violators_attr
        self.__super.__init__ (obj, inv)
    # end def __init__

    @Once_Property
    def bindings (self) :
        result = list \
            (itertools.chain (self.__super.bindings, self._violator_values ()))
        return result
    # end def bindings

    def _violator_values (self) :
        inv   = self.inv
        bvars = list \
            (   x.strip ()
            for x in inv.bvar.replace ("(", "").replace (")", "").split (",")
            )
        for v, d in paired (self.violators, self.violators_attr) :
            if len (bvars) > 1 and isinstance (v, (list, tuple)) :
                for k, w in paired (flattened (bvars), flattened (v)) :
                    yield (pyk.decoded (k.strip (), "utf-8"), ui_display (w))
            elif isinstance (v, (list, tuple)) :
                yield \
                    ( pyk.decoded (inv.bvar, "utf-8")
                    , "[%s]" % (", ".join (map (pyk.text_type, v)), )
                    )
            else :
                yield (pyk.decoded (inv.bvar, "utf-8"), ui_display (v))
            if d :
                try :
                    items = pyk.iteritems (d)
                except AttributeError :
                    val = ui_display (d)
                else :
                    val = sorted \
                        (   (pyk.decoded (a, "utf-8"), ui_display (x))
                        for (a, x) in items
                        )
                yield ui_display (v), val
    # end def _violator_values

# end class Quant

class Readonly_DB (DB) :
    """Database is set to readonly."""
# end class Readonly_DB

class Required_Empty (Invariant) :
    """Primary attribute must not be empty."""

    is_required    = True
    _rank_s        = -5

    @Once_Property
    def head (self) :
        return  \
            (  _T ("The attribute %s needs a non-empty value")
            % (self.attributes [0], )
            )
    # end def head

# end class Required_Empty

class Required_Missing (_Invariant_) :
    """Raised when required attributes are missing."""

    arg_sep        = "; "
    is_required    = True

    _rank_s        = -5

    class inv :
        name       = "required_not_missing"

    def __init__ \
            (self, e_type, needed, missing, epk, kw, kind = _("required")) :
        kw  = dict   (kw)
        raw = kw.pop ("raw", False)
        self.__super.__init__ (e_type, raw)
        self.attributes = missing
        self.epk        = epk
        self.e_type     = e_type
        self.kind       = kind
        self.kw         = kw
        self.missing    = missing
        self.needed     = needed
        self.val_disp   = kw
        self.args       = (self.head, self.description)
    # end def __init__

    @Once_Property
    def as_json_cargo (self) :
        result = self.__super.as_json_cargo
        missing_t = self.missing_t
        if missing_t :
            result ["missing_t"] = missing_t
        return result
    # end def as_json_cargo

    @Once_Property
    def description (self) :
        epk_values   = zip \
            (self.e_type.epk_sig, (portable_repr (x) for x in self.epk))
        epk_bindings = self._formatted_bindings (epk_values)
        kw_bindings  = self._formatted_bindings (pyk.iteritems (self.kw))
        return \
            ( _T ("Instead it got: (%s)")
            % ", ".join (itertools.chain (epk_bindings, kw_bindings))
            )
    # end def description

    @Once_Property
    def explanation (self) :
        return _T ("All required attributes must be supplied")
    # end def explanation

    @Once_Property
    def head (self) :
        n = len (self.needed)
        return  \
            (  _Tn ( "%s needs the attribute: %s"
                   , "%s needs the attributes: %s"
                   , n
                   )
            % (_T (self.e_type.ui_name), self.needed)
            )
    # end def head

    @Once_Property
    def missing_t (self) :
        AQ = self.e_type.AQ
        def _gen (AQ, missing) :
            for m in missing :
                aq = getattr (AQ, m)
                t  = list \
                    ( a._attr.name
                    for a in aq.Attrs
                    if  a._attr.is_required
                    )
                if t :
                    yield m, t
        return dict (_gen (self.e_type.AQ, self.missing))
    # end def missing_t

# end class Required_Missing

class Too_Many_Objects (Error) :
    """Raised when too many objects are created."""

    def __init__ (self, obj, max_count) :
        self.__super.__init__ \
            ( _T ("Cannot create more than %d objects of %s")
            % (max_count, _T (obj.ui_name))
            )
    # end def __init__

# end class Too_Many_Objects

class Wrong_Type (Error) :
    """Raised when an instance of inccorect type is passed to an attribute."""
# end class Wrong_Type

@TFL.json_dump.default.add_type (Exception)
def json_encode_exception (exc) :
    return dict \
        ( description = pyk.text_type (exc)
        , head        = exc.__class__.__name__
        )
# end def json_encode_exception

@TFL.json_dump.default.add_type (Error)
def json_encode_error (err) :
    return err.as_json_cargo
# end def json_encode_error

if __name__ != "__main__" :
    MOM._Export_Module ()
### __END__ MOM.Error
