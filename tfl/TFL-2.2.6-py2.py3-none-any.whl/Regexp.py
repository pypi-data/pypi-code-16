# -*- coding: utf-8 -*-
# Copyright (C) 2000-2016 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    TFL.Regexp
#
# Purpose
#    Class wrapper around re.RegexObject and re.MatchObject
#
# Revision Dates
#     9-Sep-2000 (CT) Creation
#    13-Oct-2000 (CT) `quote' argument added to `Regexp.__init__'
#    17-Oct-2000 (CT) Pass `sys.maxint' instead of `None' for `endpos'
#    15-Jan-2001 (CT) `__getattr__' tries `group', too
#    16-Jan-2001 (CT) `if self.last_match' guard added to `__getattr__'
#    22-Jan-2001 (CT) `Regexp.__init__' accepts re.RegexObject, too
#    26-Jan-2001 (CT) Adapt to python 2.0
#                     (`sre' doesn't export RegexObject, anymore)
#     4-Apr-2001 (CT) `_re_RegexObject' renamed to `re_RegexObject'
#    17-Apr-2001 (CT) `__getattr__' tries `last_match' first, then `_pattern'
#                     (in Python 2.0, `_pattern' suddenly has an attribute
#                     `groups')
#     9-Dec-2001 (CT) `search_all` added
#    12-Dec-2001 (CT) `search_all` protected against zero-width matches
#    15-Dec-2002 (CT) `split` and `split_n` added
#     4-Dec-2003 (CT) `search_iter` factored from `search_all`
#     2-Nov-2004 (CT) `Multi_Regexp` added
#    26-Jan-2006 (CT) `max_index` factored
#     7-Jun-2006 (CT) `Re_Replacer` added
#    14-Jun-2006 (CT) `Multi_Re_Replacer` added
#    23-Dec-2007 (CT) `Dict_Replacer` added
#    31-Dec-2010 (CT) `Multi_Regexp.search_all` and `.search_iter` added
#    25-Mar-2013 (CT) Add `Copy`, `__nonzero__`, doctest to `Regexp`
#    27-Mar-2013 (CT) Add `Multi_Re_Replacer.add`
#    24-Sep-2014 (CT) Factor `Multi_Regexp.add`
#    13-Oct-2014 (CT) Add `Multi_Regexp.sub` and `.subn`
#     8-Oct-2015 (CT) Change `__getattr__` to *not* handle `__XXX__`
#    16-Oct-2015 (CT) Add `__future__` imports
#    10-Feb-2016 (CT) Add `__head` and `__tail` args to `Dict_Replacer`
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _TFL           import TFL
from   _TFL.pyk       import pyk

import _TFL._Meta.Object
import _TFL.Environment
import re

if hasattr (re, "RegexObject") :
    re_RegexObject = re.RegexObject
else :
    ### `sre` returns a type
    re_RegexObject = type (re.compile (""))

@pyk.adapt__bool__
class Regexp (TFL.Meta.Object) :
    """Wrap a regular expression pattern and the last match, if any.

       The last result of match/search is available in the instance attribute
       `last_match`. `match` and `search` return the result of the match
       *and* store it into `last_match`.

       This allows constructions like::

           if pat.match (some_string) :
               (g1, g2, g3) = pat.groups ()

       `Regexp` instances support access to named match groups via attribute
       syntax::

           if pat.match (some_string) :
              g1 = pat.group_1


    >>> pat = Regexp (r"(?P<nm> [a-zA-Z0-9]+ (?: _{1,2}[a-zA-Z0-9]+)*)___(?P<op> [A-Z]+)$", re.VERBOSE)
    >>> _   = pat.match ("last_name___EQ")
    >>> bool (pat)
    True
    >>> print (", ".join (pat.groups ()))
    last_name, EQ

    >>> sav = pat.Copy()
    >>> _   = pat.match ("owner__last_name___STARTSWITH")
    >>> print (", ".join (pat.groups ()))
    owner__last_name, STARTSWITH
    >>> print (", ".join (sav.groups ()))
    last_name, EQ

    """

    default_flags = 0

    max_index     = TFL.Environment.practically_infinite

    def __init__ (self, pattern, flags = 0, quote = 0) :
        if isinstance (pattern, Regexp) :
            pattern = pattern._pattern
        elif not isinstance (pattern, re_RegexObject) :
            if quote :
                pattern  = re.escape  (pattern)
            pattern      = re.compile (pattern, flags or self.default_flags)
        self._pattern    = pattern
        self.last_match  = None
    # end def __init__

    def Copy (self) :
        """Return a copy with `last_match` saved for later use."""
        result            = self.__class__.__new__ (self.__class__)
        result._pattern   = self._pattern
        result.last_match = self.last_match
        return result
    # end def Copy

    def match (self, string, pos = 0, endpos = None) :
        """Try to match `self._pattern` at the beginning of `string`.

           The result is returned and stored in `self.last_match`.

           `pos` and `endpos` determine the region of the string included in
           the search (see documentation of re.match for more documentation).
        """
        endpos = endpos or self.max_index
        result = self.last_match = self._pattern.match (string, pos, endpos)
        return result
    # end def match

    def search (self, string, pos = 0, endpos = None) :
        """Scan through `string` looking for a location where `self._pattern`
           produces a match.

           The result is returned and stored in `self.last_match`.

           `pos` and `endpos` determine the region of the string included in
           the search (see documentation of re.match for more documentation).
        """
        if not isinstance (string, pyk.string_types) :
            string = string.decode ("latin-1")
        endpos = endpos or self.max_index
        result = self.last_match = self._pattern.search (string, pos, endpos)
        return result
    # end def search

    def search_all (self, string, pos = 0, endpos = None) :
        """Returns a list of all non-overlapping match-objects of
           `self._pattern` in `string` (this is similar to `findall` but
           returns the match-objects instead of strings).
        """
        return list (self.search_iter (string, pos, endpos))
    # end def search_all

    def search_iter (self, string, pos = 0, endpos = None) :
        """Iterator returning all non-overlapping match-objects of
           `self._pattern` in `string`.
        """
        endpos  = endpos or self.max_index
        lastpos = len (string)
        while pos < lastpos :
            match = self._pattern.search (string, pos, endpos)
            if match :
                yield match
                pos = match.end (0)
                if match.start (0) == match.end (0) :
                    ### protect against zero-width matches
                    pos += 1
            else :
                pos = lastpos
    # end def search_iter

    def split (self, string, maxsplit = 0, minsplit = 0) :
        """Split `string` by `self._pattern`"""
        result = self._pattern.split (string, maxsplit)
        l      = len (result)
        if minsplit and l <= minsplit :
            result += [""] * (minsplit + 1 - l)
        return result
    # end def split

    def split_n (self, string, n) :
        """Split `string` by `self._pattern` into `n` parts"""
        return self.split (string, n+1, n+1)
    # end def split_n

    def __getattr__ (self, name) :
        if name [:2] != "__" :
            try :
                try :
                    return getattr (self.last_match, name)
                except AttributeError :
                    try :
                        return self.last_match.group (name)
                    except IndexError :
                        raise AttributeError (name)
            except AttributeError :
                return getattr (self._pattern, name)
        raise AttributeError (name)
    # end def __getattr__

    def __bool__ (self) :
        return bool (self.last_match)
    # end def __bool__

# end class Regexp

class Multi_Regexp (TFL.Meta.Object) :
    """Wrap multiple regexpes (returns the first match, if any)."""

    def __init__ (self, * patterns, ** kw) :
        self.patterns   = []
        self.last_match = None
        self.add (* patterns, ** kw)
    # end def __init__

    def add (self, * patterns, ** kw) :
        add = self.patterns.append
        for p in patterns :
            if isinstance (p, pyk.string_types) :
                p = Regexp (p, ** kw)
            add (p)
    # end def add

    def match (self, * args, ** kw) :
        return self._delegate ("match", * args, ** kw)
    # end def match

    def search (self, * args, ** kw) :
        return self._delegate ("search", * args, ** kw)
    # end def search

    def search_all (self, string, pos = 0, endpos = None) :
        return list (self.search_iter (string, pos, endpos))
    # end def search_all

    def search_iter (self, string, pos = 0, endpos = None) :
        for p in self.patterns :
            for m in p.search_iter (string, pos, endpos) :
                yield m
    # end def search_iter

    def sub (self, * args, ** kw) :
        return self._delegate ("sub", * args, ** kw)
    # end def sub

    def subn (self, * args, ** kw) :
        return self._delegate ("subn", * args, ** kw)
    # end def subn

    def _delegate (self, meth, * args, ** kw) :
        for p in self.patterns :
            result = self.last_match = getattr (p, meth) (* args, ** kw)
            if result :
                return result
    # end def _delegate

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        try :
            return getattr (self.last_match, name)
        except AttributeError :
            try :
                return self.last_match.group (name)
            except IndexError :
                raise AttributeError (name)
    # end def __getattr__

# end class Multi_Regexp

class Re_Replacer (TFL.Meta.Object) :
    """Wrap a regular expression and a replacement (text or function).

       >>> rep = Re_Replacer (
       ...     "[abc]", lambda m : str ("abc".index (m.group (0))))
       >>> print (rep ("abc"))
       012
       >>> print (rep ("abc", count = 1))
       0bc
    """

    default_flags = 0

    def __init__ (self, pattern, replacement, flags = 0) :
        self.regexp      = Regexp (pattern, flags or self.default_flags)
        self.replacement = replacement
    # end def __init__

    def __call__ (self, text, count = 0) :
        try :
            return self.regexp.sub (self.replacement, text, count)
        except TypeError :
            print (self.regexp.pattern, self.replacement)
            raise
    # end def __call__

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        return getattr (self.regexp, name)
    # end def __getattr__

# end class Re_Replacer

class Dict_Replacer (Re_Replacer) :
    """Replace all keys (which are assumed to be plain strings, not regexpes)
       of a dictionary with the corresponding values.

       >>> dr = Dict_Replacer ({"--" : "\\endash", "---" : "\\emdash"})
       >>> print (dr ("TeX interprets `--` as an en-dash and `---` as an em-dash"))
       TeX interprets `\\endash` as an en-dash and `\\emdash` as an em-dash
    """

    _group = 0

    def __init__ \
            (self, __dict = {}, __flags = 0, __head = "", __tail = "", ** kw) :
        self._map = map = dict (__dict, ** kw)
        pattern   = "|".join \
            ( re.escape (k) for k in sorted
                (pyk.iterkeys (map), key = lambda k : (-len (k), k))
            )
        if __head or __tail :
            pattern     = "".join ((__head, "(", pattern, ")", __tail))
            self._group = 1
        regexp = Regexp (pattern, __flags)
        self.__super.__init__ (regexp, self._replacer, __flags)
    # end def __init__

    def _replacer (self, match) :
        return self._map [match.group (self._group)]
    # end def _replacer

# end class Dict_Replacer

class Multi_Re_Replacer (TFL.Meta.Object) :
    """Wrap multiple `Re_Replacer` instances and apply them in sequence"""

    def __init__ (self, * rerep) :
        self.rereps = list (rerep)
    # end def __init__

    def __call__ (self, text, count = 0) :
        result = text
        for rerep in self.rereps :
            result = rerep (result, count)
        return result
    # end def __call__

    def add (self, * rereps) :
        self.rereps.extend (rereps)
    # end def add

# end class Multi_Re_Replacer

__doc__ = """

.. moduleauthor:: Christian Tanzer <tanzer@swing.co.at>

"""

if __name__ != "__main__" :
    TFL._Export ("*", "re")
### __END__ TFL.Regexp
