# -*- coding: utf-8 -*-
# Copyright (C) 2004-2015 Mag. Christian Tanzer. All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    Ascii
#
# Purpose
#    Functions for unicode/ASCII handling
#
# Revision Dates
#     6-Sep-2004 (CT) Creation
#    13-May-2005 (CT) Call to `strip` added to `sanitized_filename`
#     9-Aug-2006 (CT) Use `unicodedata.normalize` (and simplify `_diacrit_map`)
#     9-Mar-2007 (CT) `_diacrit_map` corrected (`Oe` and `Ue` instead `O`/`U`)
#     9-Mar-2007 (CT) Optional `translate_table` added to `sanitized_unicode`
#                     and `sanitized_filename`
#    23-Dec-2007 (CT) Use `Re_Replacer` and `Dict_Replacer` instead of
#                     home-grown code
#    18-Oct-2010 (CT) `_quote_map` added and used
#    12-Oct-2015 (CT) Apply `pyk.decoded` to `result` of `_encoded`
#    ««revision-date»»···
#--

from   __future__  import print_function, unicode_literals

from   _TFL        import TFL
from   _TFL.pyk    import pyk
from   _TFL.Regexp import Regexp, Re_Replacer, Dict_Replacer, re

import _TFL.CAO

from   itertools   import chain as ichain
import unicodedata

_diacrit_map    = \
    { "Ä"      : "Ae"
    , "Ö"      : "Oe"
    , "Ü"      : "Ue"
    , "ß"      : "ss"
    , "ä"      : "ae"
    , "ö"      : "oe"
    , "ü"      : "ue"
    }

_diacrit_rep    = Dict_Replacer (_diacrit_map)

_graph_rep      = Re_Replacer \
    ( "(%s)+"
    % "|".join   (re.escape (c) for c in ("^!$%&([{}]) ?`'*+#:;<>|" '"'))
    , "_"
    )

_non_print_rep  = Re_Replacer \
    ( "|".join (re.escape (chr (i)) for i in ichain (range (0, 32), [127]))
    , ""
    )

_quote_map      = \
    { "«"      : "<<"
    , "»"      : ">>"
    , "\u2018" : "'"
    , "\u2019" : "'"
    , "\u201A" : "'"
    , "\u201B" : "'"
    , "\u201C" : '"'
    , "\u201D" : '"'
    , "\u201E" : '"'
    , "\u201F" : '"'
    , "\u2039" : "'"
    , "\u203A" : "'"
    }

_quote_rep      = Dict_Replacer (_quote_map)

def _encoded (s) :
    return pyk.decoded \
        (unicodedata.normalize ("NFKD", s).encode ("ascii", "ignore"))
# end def _encoded

def _sanitized_unicode (s, translate_table = None) :
    if translate_table :
        s = s.translate (translate_table)
    s = _quote_rep (_diacrit_rep (s))
    return s
# end def _sanitized_unicode

def _show (s) :
    from _TFL.portable_repr import portable_repr
    result = portable_repr (s)
    pyk.fprint (result)
# end def _show

def sanitized_unicode (s, translate_table = None) :
    """Return sanitized version of unicode string `s` reduced to
       pure ASCII 8-bit string. Caveat: passing in an 8-bit string with
       diacriticals doesn't work.

       >>> _show (sanitized_unicode ("üxäyözßuÜXÄYÖZbc¡ha!"))
       'uexaeyoezssuUeXAeYOeZbcha!'
       >>> _show (sanitized_unicode ("«ÄÖÜ»"))
       '<<AeOeUe>>'
       >>> _show \\
       ... (sanitized_unicode ("«ÄÖÜ»", {ord ("«") : "<", ord ("»") : ">"}))
       '<AeOeUe>'
    """
    return _encoded (_sanitized_unicode (s, translate_table))
# end def sanitized_unicode

def sanitized_filename (s, translate_table = None) :
   """Return `sanitized_unicode (s)` with all non-printable and some graphic
      characters removed so that the result is usable as a filename.

       >>> _show (sanitized_filename \\
       ...    ("überflüßig komplexer'; und $gefährlicher*' Filename"))
       'ueberfluessig_komplexer_und_gefaehrlicher_Filename'
       >>> _show (sanitized_filename ("«ÄÖÜß»"))
       '_AeOeUess_'
   """
   s = _sanitized_unicode (s.strip (), translate_table)
   s = _non_print_rep     (s)
   s = _graph_rep         (s)
   return _encoded        (s)
# end def sanitized_filename

__doc__ = """
.. moduleauthor:: Christian Tanzer <tanzer@swing.co.at>

"""

def _main (cmd) :
    """For each argument, write sanitized_filename to stdout. If `-rename` is
       specified, the files are renamed to the sanitized_filenames instead.
    """
    from _TFL     import sos
    from _TFL.pyk import pyk
    for f in cmd.argv :
        sf = sanitized_filename (pyk.decoded (f))
        if cmd.rename :
            sos.rename (f, sf)
            if cmd.verbose :
                pyk.fprint ("Renamed", f, "to", sf)
        else :
            pyk.fprint (sf, end = " ")
# end def _main

_Command = TFL.CAO.Cmd \
    ( handler       = _main
    , args          =
        ( "file:P?File(s) to rename"
        ,
        )
    , opts          =
        ( TFL.CAO.Opt.Input_Encoding
            ( description   = "Input encoding"
            , default       = "utf-8"
            )
        , "-rename:B?Rename the files to names by `sanitized_filename`"
        , "-verbose:B"
        )
    , min_args      = 1
    )

if __name__ == "__main__" :
    _Command ()
else :
    TFL._Export_Module ()
### __END__ Ascii
