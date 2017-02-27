# -*- coding: utf-8 -*-
# Copyright (C) 2014-2016 Mag. Christian Tanzer All rights reserved
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
#    MOM.Attr.Polisher
#
# Purpose
#    Polishers for MOM attributes
#
# Revision Dates
#    24-Sep-2014 (CT) Creation
#    26-Sep-2014 (CT) Add `guard`, `capitalize_if_not_mixed_case`,
#                     `capitalize_if_lower_case`
#    26-Feb-2015 (CT) Change `_polish` to `_polished`
#                     + return new dict instead of updating parameter
#    26-Feb-2015 (CT) Change `area_code_clean` to `area_code_split`;
#                     factor, add patterns to, and improve `_phone_multi_regexp`
#    15-Apr-2015 (CT) Add `compress_spaces` and capitalize+compress combos
#    29-Jul-2015 (CT) Adapt to name change of PAP.Phone attributes
#    30-Jul-2015 (CT) Add arguments `essence`, `picky` to
#                     `_Polisher_.__call__`, `._polished`
#    31-Jul-2015 (CT) Factor `_attr_value`
#     5-Feb-2016 (CT) Add `polish_empty`
#    26-Apr-2016 (CT) Add `pre_complete`
#    26-Apr-2016 (CT) Add `Instance`, `buddies`
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _MOM                  import MOM
from   _TFL                  import TFL

import _MOM._Attr

from   _TFL.predicate        import uniq
from   _TFL.pyk              import pyk
from   _TFL.Regexp           import *

import _TFL._Meta.Object

class _Polisher_ (TFL.Meta.Object) :
    """Base class for Polishers"""

    buddies      = ()
    guard        = None
    polish_empty = False
    pre_complete = True

    def __init__ (self, ** kw) :
        for k, v in pyk.iteritems (kw) :
            ### use `setattr` to allow `property.__set__` to intervene
            setattr (self, k, v)
    # end def __init__

    def __call__ \
            ( self, attr, value_dict
            , essence = None
            , picky   = False
            , value   = None
            ) :
        """Polish value of `attr` in `value_dict`, if any, return polished `value_dict`."""
        result = dict (value_dict)
        name   = attr.name
        value  = self._attr_value (attr, name, value, value_dict, essence)
        if isinstance (value, pyk.string_types) :
            guard  = self.guard
            value  = value.strip ()
            if (   (self.polish_empty or value)
               and (guard is None     or guard (value))
               ) :
                polished = self._polished \
                    (attr, name, value, value_dict, essence, picky)
                result.update (polished)
        return result
    # end def __call__

    def Instance (self, attr) :
        return _Polisher_Instance_ (self, attr)
    # end def Instance

    def _attr_value (self, attr, name, value, value_dict, essence) :
        result = value
        if result is None :
            result = value_dict.get (name)
        return result
    # end def _attr_value

    def _polished (self, attr, name, value, value_dict, essence, picky) :
        raise NotImplementedError \
            ( "%s needs to implement either __call__ or _polished"
            % (self.__class__, )
            )
    # end def _polished

# end class _Polisher_

class _Polisher_Instance_ (TFL.Meta.Object) :
    """Polisher instance for a specific instance of MOM.Attr.Kind."""

    def __init__ (self, polisher, attr) :
        self.attr      = attr
        self.name      = attr.name
        self.polisher  = polisher
    # end def __init__

    def __call__ (self, * args, ** kw) :
        return self.polisher (* args, ** kw)
    # end def __call__

    @TFL.Meta.Once_Property
    def names (self) :
        return tuple (uniq ((self.name, ) + self.polisher.buddies))
    # end def names

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        result = getattr (self.polisher, name)
        setattr (self, name, result)
        return result
    # end def __getattr__

# end class _Polisher_Instance_

class Match_Split (_Polisher_) :
    """Polisher splitting a value into several attribute values."""

    def __init__ (self, matcher, ** kw) :
        if isinstance (matcher, (Regexp, ) + pyk.string_types) :
            matcher = Multi_Regexp (matcher)
        self.__super.__init__ (matcher = matcher, ** kw)
    # end def __init__

    def add (self, * matchers, ** kw) :
        self.matcher.add (* matchers, ** kw)
    # end def add

    def _polished (self, attr, name, value, value_dict, essence, picky) :
        result = {}
        match  = self.matcher.search (value)
        if match is not None :
            dct = match.groupdict ()
            for k, v in pyk.iteritems (dct) :
                if v is not None :
                    result [k] = v
        return result
    # end def _polished

# end class Match_Split

class Replace (_Polisher_) :
    """Polisher replacing matches of regular expressions."""

    def __init__ (self, replacer, ** kw) :
        self.__super.__init__ (replacer = replacer, ** kw)
    # end def __init__

    def _polished (self, attr, name, value, value_dict, essence, picky) :
        result = { name : self.replacer (value) }
        return result
    # end def _polished

# end class Replace

def _capitalize_words (match) :
    words  = match.group (0).split ("-")
    result = "-".join (w.capitalize () for w in words)
    return result
# end def _capitalize_words

### `_uni_case_word` should use `[:lower:]` and `[:upper:]` but
### unfortunately Python regular expressions don't support these
_uni_case_word_pat = \
    ( r"("
      r"[a-zäüöß0-9][-a-zäüöß0-9]*"
      r"|"
      r"[A-ZÄÜÖ0-9][-A-ZÄÜÖ0-9]*"
      r")"
    )

capitalize = Replace \
    ( Re_Replacer
        ( r"\b"
        + _uni_case_word_pat
        + r"\b"
        , _capitalize_words
        , re.UNICODE
        )
    )

capitalize_if_lower_case = Replace \
    ( Re_Replacer (r"\w+", _capitalize_words, re.UNICODE)
    , guard = lambda s : s.islower ()
    )

capitalize_if_not_mixed_case = Replace \
    ( Re_Replacer (r"\w+", _capitalize_words, re.UNICODE)
    , guard = TFL.is_not_mixed_case
    )

capitalize_last_word = Replace \
    ( Re_Replacer
        ( r"\b"
        + _uni_case_word_pat
        + r"$"
        , _capitalize_words
        , re.UNICODE
        )
    )

compress_spaces = Replace (Re_Replacer (r"[ \t]+", " ", re.UNICODE))

capitalize_compress_spaces = Replace \
    ( Multi_Re_Replacer
        ( capitalize.replacer
        , compress_spaces.replacer
        )
    , guard = capitalize.guard
    )

capitalize_if_lower_case_compress_spaces = Replace \
    ( Multi_Re_Replacer
        ( capitalize_if_lower_case.replacer
        , compress_spaces.replacer
        )
    , guard = capitalize_if_lower_case.guard
    )

capitalize_if_not_mixed_case_compress_spaces = Replace \
    ( Multi_Re_Replacer
        ( capitalize_if_not_mixed_case.replacer
        , compress_spaces.replacer
        )
    , guard = capitalize_if_not_mixed_case.guard
    )

capitalize_last_word_compress_spaces = Replace \
    ( Multi_Re_Replacer
        ( capitalize_last_word.replacer
        , compress_spaces.replacer
        )
    , guard = capitalize_last_word.guard
    )

_phone_cc_pat  = r"(?:(?:\+ *|00)(?P<cc>\d+))"
_phone_ndc_pat = r"(?P<ndc>\d+)"
_phone_sn_pat  = r"(?P<sn>\d+)\s*"

def _phone_multi_regexp (tail = "") :
    return Multi_Regexp \
        ( Regexp
            ( r"^"
            + r"(?:" + _phone_cc_pat + " +|0 *)?"
            + _phone_ndc_pat
            + ((r" " + tail) if tail else "")
            + r"$"
            , re.UNICODE
            )
        , Regexp
            ( r"^"
            + r"(?:" + _phone_cc_pat + "|0)? *"
            + r"\("
            + _phone_ndc_pat
            + r"\) *"
            + tail
            + r"$"
            , re.UNICODE
            )
        , Regexp
            ( r"^"
            + r"(?:" + _phone_cc_pat + "|0)? *"
            + r"/"
            + _phone_ndc_pat
            + r"/"
            + ("" if tail else "?")
            + " *"
            + tail
            + r"$"
            , re.UNICODE
            )
        , Regexp
            ( r"^"
            + r"(?:" + _phone_cc_pat + "|0)? *"
            + r"-"
            + _phone_ndc_pat
            + r"-"
            + ("" if tail else "?")
            + " *"
            + tail
            + r"$"
            , re.UNICODE
            )
        , Regexp
            ( r"^"
            + r"(?:" + _phone_cc_pat + "|0)? *"
            + ((r" +" + tail) if tail else "")
            + r"$"
            , re.UNICODE
            )
        )
# end def _phone_multi_regexp

phone_cc_clean  = Match_Split (r"^" + _phone_cc_pat + r"$")
phone_ndc_split = Match_Split (_phone_multi_regexp ())
phone_sn_split  = Match_Split (_phone_multi_regexp (_phone_sn_pat))

_test_capitalize = """
    >>> from _TFL.Record import Record
    >>> attr = Record (name = "test")
    >>> def test (polisher, value) :
    ...     rd = polisher (attr, dict (test = value))
    ...     print (rd ["test"])

    >>> l = "fröhlich-tanzer"
    >>> m = "Fröhlich-Tanzer"
    >>> u = "FRÖHLICH-TANZER"

    >>> test (capitalize, l)
    Fröhlich-Tanzer
    >>> test (capitalize, m)
    Fröhlich-Tanzer
    >>> test (capitalize, u)
    Fröhlich-Tanzer

    >>> test (capitalize_last_word, l)
    Fröhlich-Tanzer
    >>> test (capitalize_last_word, m)
    Fröhlich-Tanzer
    >>> test (capitalize_last_word, u)
    Fröhlich-Tanzer

    >>> l = "christian fröhlich-tanzer"
    >>> m = "Christian Fröhlich-Tanzer"
    >>> u = "CHRISTIAN FRÖHLICH-TANZER"

    >>> test (capitalize, l)
    Christian Fröhlich-Tanzer
    >>> test (capitalize, m)
    Christian Fröhlich-Tanzer
    >>> test (capitalize, u)
    Christian Fröhlich-Tanzer

    >>> test (capitalize_last_word, l)
    christian Fröhlich-Tanzer
    >>> test (capitalize_last_word, m)
    Christian Fröhlich-Tanzer
    >>> test (capitalize_last_word, u)
    CHRISTIAN Fröhlich-Tanzer

    >>> l = "van der fröhlich-tanzer"
    >>> m = "van der Fröhlich-Tanzer"
    >>> u = "van der FRÖHLICH-TANZER"
    >>> v = "VAN DER FRÖHLICH-TANZER"

    >>> test (capitalize, l)
    Van Der Fröhlich-Tanzer
    >>> test (capitalize, m)
    Van Der Fröhlich-Tanzer
    >>> test (capitalize, u)
    Van Der Fröhlich-Tanzer

    >>> test (capitalize_if_not_mixed_case, l)
    Van Der Fröhlich-Tanzer
    >>> test (capitalize_if_not_mixed_case, m)
    van der Fröhlich-Tanzer
    >>> test (capitalize_if_not_mixed_case, u)
    van der FRÖHLICH-TANZER
    >>> test (capitalize_if_not_mixed_case, v)
    Van Der Fröhlich-Tanzer

    >>> test (capitalize_last_word, l)
    van der Fröhlich-Tanzer
    >>> test (capitalize_last_word, m)
    van der Fröhlich-Tanzer
    >>> test (capitalize_last_word, u)
    van der Fröhlich-Tanzer

    >>> l = "mctanzer"
    >>> m = "McTanzer"
    >>> u = "MCTANZER"

    >>> test (capitalize, l)
    Mctanzer
    >>> test (capitalize, m)
    McTanzer
    >>> test (capitalize, u)
    Mctanzer

    >>> test (capitalize_last_word, l)
    Mctanzer
    >>> test (capitalize_last_word, m)
    McTanzer
    >>> test (capitalize_last_word, u)
    Mctanzer

    >>> l = "mag."
    >>> m = "Mag."
    >>> u = "MAG."

    >>> test (capitalize, l)
    Mag.
    >>> test (capitalize, m)
    Mag.
    >>> test (capitalize, u)
    Mag.

    >>> l = "dipl.ing."
    >>> m = "Dipl.Ing."
    >>> u = "DIPL.ING."

    >>> test (capitalize, l)
    Dipl.Ing.
    >>> test (capitalize, m)
    Dipl.Ing.
    >>> test (capitalize, u)
    Dipl.Ing.

"""

_test_phone_ndc_split = r"""
    >>> from _TFL.Record import Record

    >>> attr = Record (name = "ndc")

    >>> def show_split (v) :
    ...     r  = phone_ndc_split (attr, dict (ndc = v))
    ...     vs = ("%s = %s" % (k, v) for k, v in sorted (r.items ()))
    ...     print (", ".join (vs))

    >>> show_split ("664")
    ndc = 664

    >>> show_split ("0664")
    ndc = 664

    >>> show_split ("0 664")
    ndc = 664

"""

_test_phone_cc_clean = r"""
    >>> from _TFL.Record import Record

    >>> attr = Record (name = "cc")

    >>> def show_split (v) :
    ...     r  = phone_cc_clean (attr, dict (cc = v))
    ...     vs = ("%s = %s" % (k, v) for k, v in sorted (r.items ()))
    ...     print (", ".join (vs))

    >>> show_split ("43")
    cc = 43

    >>> show_split ("+43")
    cc = 43

    >>> show_split ("+ 43")
    cc = 43

    >>> show_split ("0043")
    cc = 43

"""

_test_phone_sn_split = r"""
    >>> from _TFL.Record import Record

    >>> attr = Record (name = "sn")

    >>> def show_split (sn) :
    ...     r  = phone_sn_split (attr, dict (sn = sn))
    ...     vs = ("%s = %s" % (k, v) for k, v in sorted (r.items ()))
    ...     print (", ".join (vs))

    >>> show_split ("12345678")
    sn = 12345678

    >>> show_split ("0043 664 12345678")
    cc = 43, ndc = 664, sn = 12345678

    >>> show_split ("+43 664 12345678")
    cc = 43, ndc = 664, sn = 12345678

    >>> show_split ("0043 664 12345678")
    cc = 43, ndc = 664, sn = 12345678

    >>> show_split ("664 12345678")
    ndc = 664, sn = 12345678

    >>> show_split ("0664 12345678")
    ndc = 664, sn = 12345678

    >>> show_split ("+43(664)12345678")
    cc = 43, ndc = 664, sn = 12345678

    >>> show_split ("+43 (664) 12345678")
    cc = 43, ndc = 664, sn = 12345678

    >>> show_split ("0(664)12345678")
    ndc = 664, sn = 12345678

    >>> show_split ("0 (664) 12345678")
    ndc = 664, sn = 12345678

    >>> show_split ("43 66412345678")
    ndc = 43, sn = 66412345678

    >>> show_split ("+43 66412345678")
    cc = 43, sn = 66412345678

"""

__test__ = dict \
    ( test_phone_ndc_split    = _test_phone_ndc_split
    , test_phone_cc_clean     = _test_phone_cc_clean
    , test_capitalize         = _test_capitalize
    , test_phone_sn_split     = _test_phone_sn_split
    )

if __name__ != "__main__" :
    MOM.Attr._Export_Module ()
### __END__ MOM.Attr.Polisher
