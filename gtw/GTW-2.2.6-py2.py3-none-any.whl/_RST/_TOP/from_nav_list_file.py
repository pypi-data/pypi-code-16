# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.RST.TOP.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.RST.TOP.from_nav_list_file
#
# Purpose
#    Read tree-of-pages from navigation.list+referred-to-files
#
# Revision Dates
#    23-Nov-2015 (CT) Creation (based on GTW.NAV methods)
#     1-Dec-2015 (CT) Change `_entries` to use `parent.Page`, if any,
#                     as default `Type`
#     1-Dec-2015 (CT) Improve `_fix_dict` (no `desc` nor `short_title`)
#     2-Dec-2015 (CT) Add `logging.exception` to `from_nav_list_file`
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _GTW                     import GTW
from   _ReST                    import ReST
from   _TFL                     import TFL

from   _CAL.Date_Time           import Date_Time as DT

import _GTW._RST.Resource
import _GTW._RST._TOP.Gallery
import _GTW._RST._TOP.Page
import _GTW._RST._TOP.ReST
import _GTW._RST._TOP.Video

import _ReST.To_Html
import _GTW._RST._TOP.import_TOP

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL.formatted_repr      import formatted_repr
from   _TFL.Decorator           import getattr_safe
from   _TFL.Filename            import Filename
from   _TFL.predicate           import split_hst
from   _TFL.pyk                 import pyk
from   _TFL.Record              import Record
from   _TFL.Regexp              import Regexp, re
from   _TFL                     import sos

import _TFL.Sorted_By

from   posixpath import join as pjoin

import textwrap

_code_header = """\
from __future__  import unicode_literals
"""

_globs = None

_nav_info_pat  = Regexp \
    ( r"^\.\. *$"
      "\n"
      r" +<(?P<expired>!?)Nav-Info> *$"
      "\n"
        r"(?P<code>"
          r"(?:^ +(?:\w+ *=|[][(),]).*$" "\n" r")+"
        r")"
      r" +<!?/Nav-Info> *$"
    , re.MULTILINE
    )

def _entries (parent, src_dir, list_of_dicts) :
    for d in list_of_dicts :
        _fix_dict    (d)
        sd   = d.pop ("sub_dir", None)
        Type = d.pop ("Type",    None) or \
            (    getattr (parent, "Page", GTW.RST.TOP.Page)
            if   sd is None
            else GTW.RST.TOP.Dir
            )
        if sd is None :
            entry        = Type  (parent = parent, src_dir = src_dir, ** d)
        else :
            entry        = Type  (name = sd, parent = parent, ** d)
            sub_dir_path = pjoin (src_dir, sd)
            from_nav_list_file   (entry, sub_dir_path)
        if entry is not None :
            yield entry
# end def _entries

def _exec (text) :
    code   = "\n".join (( _code_header, text))
    result = dict (__builtins__ = {})
    exec (code, _globs, result)
    result.pop ("__builtins__")
    return result
# end def _exec

def _file_contents (name, encoding = "utf-8") :
    if sos.path.exists (name) :
        with open (name, "rb") as f :
             result = pyk.decoded (f.read ().strip (), encoding)
        return result
    else :
        print ("*** *** *** File doesn't exist:", name, "*** *** ***")
# end def _file_contents

def _fix_dict (dct) :
    if "title" in dct and "short_title" not in dct :
        if "desc" in dct :
            dct ["short_title"] = dct.pop ("title")
            dct ["title"]       = dct.pop ("desc")
        else :
            dct ["short_title"] = dct.get ("title")
    for k, v in list (pyk.iteritems (dct)) :
        if isinstance (v, pyk.byte_types) :
            dct [k] = pyk.decoded (v, "utf-8", "latin-1")
    return dct
# end def _fix_dict

def _page_info (f) :
    src = _file_contents (f)
    pat = _nav_info_pat
    if pat.search (src) :
        result = _fix_dict (_exec (textwrap.dedent (pat.code)))
        if pat.expired :
            date     = result.get ("date")
            exp_date = "20091231"
            if date :
                try :
                    exp_date = \
                        (DT.from_string (date) + DT.Delta (30)).formatted ()
                except Exception :
                    pass
            result ["exp_date"] = exp_date
        result ["src_contents"] = pat.sub ("", src).strip ()
        return result
# end def _page_info

A_Link  = GTW.RST.TOP.A_Link
Alias   = GTW.RST.TOP.Alias

def Dyn_Slice_ReST_Dir (parent, src_dir) :
    def _gen (parent, src_dir) :
        for f in sos.expanded_globs (pjoin (src_dir, "*.txt")) :
            info = _page_info (f)
            if info :
                n = info.get ("name", f)
                info ["perma_name"] = base = Filename (n).base
                info ["name"]       = name = "%s.html" % (base, )
                yield GTW.RST.TOP.Page_ReST \
                    (parent = parent, src_dir = src_dir, ** info)
    sort_key = TFL.Sorted_By ("rank", "-date", "name")
    entries  = sorted (_gen (parent, src_dir), key = sort_key)
    parent.add_entries (* entries)
# end def Dyn_Slice_ReST_Dir

Gallery = GTW.RST.TOP.Gallery

def Page_ReST_F (parent, src_dir, name, ** kw) :
    src_path     = pjoin          (src_dir, Filename (".txt", name).name)
    src_contents = _file_contents (src_path)
    return GTW.RST.TOP.Page_ReST \
        ( parent       = parent
        , src_dir      = src_dir
        , name         = name
        , src_contents = src_contents
        , ** kw
        )
# end def Page_ReST_F

Video   = GTW.RST.TOP.Video

def from_nav_list_file (parent, src_dir, nav_context = {}) :
    global _globs
    if _globs is None :
        _globs = dict  (globals (), ** nav_context)
    parent.src_dir = src_dir
    fn = pjoin (src_dir, "navigation.list")
    fc = _file_contents (fn)
    if fc is not None :
        try :
            dct = _exec (fc)
        except Exception as exc :
            import logging
            logging.exception ("Error in %s" % (fn, ))
        else :
            parent.add_entries \
                (* _entries (parent, src_dir, dct ["own_links"]))
    else :
        print ("*** navigation.list not found in directory", src_dir, "***")
# end def from_nav_list_file

if __name__ != "__main__" :
    GTW.RST.TOP._Export ("from_nav_list_file")
### __END__ GTW.RST.TOP.from_nav_list_file
