# -*- coding: utf-8 -*-
# Copyright (C) 2010-2013 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package ReST.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    ReST.Roles
#
# Purpose
#    Define some interpreted text roles for reStructuredText
#
# Revision Dates
#    15-Feb-2010 (CT) Creation
#    15-Jan-2011 (CT) `deleted` role added
#    28-Feb-2012 (CT) Add `_quoted_role`
#     7-Mar-2013 (CT) Add `_added_role`
#     8-Mar-2013 (CT) Use `...-inline` for short text `added` or `deleted`
#    20-Aug-2013 (CT) Add `_char_entity`
#    20-Aug-2013 (CT) Change `_uri_role` to replace space by thin no-break space
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division
from   __future__  import print_function, unicode_literals

from   _ReST                      import ReST
from   _TFL.I18N                  import _, _T
from   _TFL.Regexp                import *

from   docutils                   import nodes, utils
from   docutils.parsers.rst.roles import CustomRole, register_local_role

_uri_pat = Regexp \
    ( r"(?P<text> .*)<(?P<uri> [^>]+)>$"
    , re.VERBOSE | re.DOTALL
    )

def _uri_role (role, rawtext, text, lineno, inliner, options={}, content=[]) :
    if _uri_pat.match (text) :
        text = _uri_pat.text.strip ()
        uri  = _uri_pat.uri.strip  ()
    else :
        text = uri = text.strip ()
    scheme   = options.pop ("uri_scheme", None)
    if scheme :
        ref  = "%s:%s" % (scheme, uri)
    else :
        ref  = uri
    text = text.replace    (" ", "\u202F") ### narrow non breaking space
    node = nodes.reference (rawtext, text, refuri = ref, ** options)
    return [node], []
# end def _uri_role

_email_role = CustomRole ("email", _uri_role, dict (uri_scheme = "mailto"))
_tel_role   = CustomRole ("tel",   _uri_role, dict (uri_scheme = "tel"))

register_local_role (_email_role.name, _email_role)
register_local_role ("tel",            _tel_role)

def _added_role (role, rawtext, text, lineno, inliner, options={}, content=[]) :
    cssc = "added" if len (rawtext) > 60 else "added-inline"
    node = nodes.inline (rawtext, text, classes = [cssc], ** options)
    return [node], []
# end def _added_role

register_local_role ("added", _added_role)

def _deleted_role (role, rawtext, text, lineno, inliner, options={}, content=[]) :
    cssc = "deleted" if len (rawtext) > 60 else "deleted-inline"
    node = nodes.inline (rawtext, text, classes = [cssc], ** options)
    return [node], []
# end def _deleted_role

register_local_role ("deleted", _deleted_role)

### http://de.wikipedia.org/wiki/Anf%C3%BChrungszeichen#Kodierung
_quot_map = dict \
    ( qd  = (_("\u201C"), _("\u201D")) # ("&ldquo;",  "&rdquo;")
    , qf  = (_("\u2039"), _("\u203A")) # ("&lsaquo;", "&rsaquo;")
    , qg  = (_("«"),      _("»"))      # ("&laquo;",  "&raquo;")
    , qs  = (_("\u2018"), _("\u2019")) # ("&lsquo;",  "&rsquo;")
    )

def _quoted_role \
        (role, rawtext, text, lineno, inliner, options={}, content=[]) :
    ql, qr = _quot_map.get (role) or _quot_map ["qd"]
    text   = "%s%s%s" % (_T (ql), text, _T (qr))
    node   = nodes.inline (rawtext, text, ** options)
    return [node], []
# end def _quoted_role

register_local_role ("q",  _quoted_role)
register_local_role ("qd", _quoted_role)
register_local_role ("qf", _quoted_role)
register_local_role ("qg", _quoted_role)
register_local_role ("qs", _quoted_role)

_char_entity_map = \
    { "~"        : "\u00A0" ### non breaking space
    , ","        : "\u202F" ### narrow non breaking space
    , "."        : "\u00B7" ### middle dot
    , "0"        : "\u2007" ### figure space
    , "deg"      : "\u00B0" ### degree symbol
    , "mu"       : "\u00B5" ### micro sign
    , "ne"       : "\u2260" ### not equal sign
    , "x"        : "\u00D7" ### multiplication sign
    , "/"        : "\u00F7" ### division sign
    , "$"        : "€"
    }

def _char_entity \
        (role, rawtext, text, lineno, inliner, options={}, content=[]) :
    char   = _char_entity_map.get (text, text)
    node   = nodes.inline (rawtext, char, ** options)
    return [node], []
# end def _char_entity

register_local_role ("x", _char_entity)

### __END__ ReST.Roles
