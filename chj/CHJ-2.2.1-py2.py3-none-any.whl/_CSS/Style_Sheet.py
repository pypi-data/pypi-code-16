# -*- coding: utf-8 -*-
# Copyright (C) 2010-2017 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package CHJ.CSS.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    CHJ.CSS.Style_Sheet
#
# Purpose
#    Model a CSS style sheet
#
# Revision Dates
#    29-Dec-2010 (CT) Creation
#     1-Jan-2011 (CT) `Eval` added
#     2-Jan-2011 (CT) `_Eval` factored
#     3-Jan-2011 (CT) `rank` added
#    14-Jan-2011 (CT) `Parameter_Scope` changed to `import_CSS.__dict__` as
#                     object
#    14-Jan-2011 (CT) `Parameter_Scope` moved to `GTW.Parameters.Scope`
#    14-Jan-2011 (CT) `Eval` and `Read` removed (done by JNJ.Templateer now)
#    13-Sep-2011 (CT) `Style_File` added
#     9-Apr-2014 (CT) Add `static_handler` to `Style_File`
#    10-Oct-2014 (CT) Use `@pyk.adapt__str__` abnd `pyk.decoded`
#    22-Jan-2016 (CT) Use `pyk.text_type`, not `str`, in `__str__`
#    11-Oct-2016 (CT) Move from `GTW` to `CHJ`
#     5-Jan-2017 (CT) Remove alias `S`
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division
from   __future__  import print_function, unicode_literals

from   _CHJ                       import CHJ
from   _TFL                       import TFL

import _CHJ._CSS.Media

from   _TFL                       import sos
from   _TFL.pyk                   import pyk

import _TFL._Meta.Object
import _TFL.Caller
import _TFL._Meta.Once_Property
import _TFL.Filename

class M_Style_Sheet (TFL.Meta.Object.__class__) :
    """Meta class for `Style_Sheet`"""

# end class M_Style_Sheet

class _Style_Sheet_ \
        (TFL.Meta.BaM (TFL.Meta.Object, metaclass = M_Style_Sheet)) :

    name          = None
    rank          = 0

    def __init__ (self, media = None, ** kw) :
        self.media = media or CHJ.CSS.Media.Type ("all")
        self.__dict__.update (kw)
    # end def __init__

# end class _Style_Sheet_

@pyk.adapt__str__
class Style_Sheet (_Style_Sheet_) :
    """Model a CSS style sheet"""

    _CSS_globs    = {}

    def __init__ (self, * rules, ** attrs) :
        self.__super.__init__ \
            ( attrs   = attrs
            , imports = list (attrs.pop ("imports", []))
            , media   = attrs.pop ("media", None)
            , name    = attrs.pop ("name",  None)
            , rank    = attrs.pop ("rank",  0)
            , rules   = list (rules)
            )
    # end def __init__

    def add_import (self, * imports) :
        self.imports.extend (imports)
    # end def add_import

    def add_rule (self, * rules) :
        self.rules.extend (rules)
    # end def add_rule

    def __iter__ (self) :
        for i in self.imports :
            for r in i :
                yield r
        for r in self.rules :
            for x in r :
                yield x
    # end def __iter__

    def __str__ (self) :
        return "\n\n".join (pyk.text_type (r) for r in self)
    # end def __str__

# end class Style_Sheet

@pyk.adapt__str__
class Style_File (_Style_Sheet_) :
    """Model a style file containing plain old CSS."""

    static_handler = None

    def __init__ (self, file_name, ** kw) :
        self.__super.__init__ \
            ( file_name = file_name
            , name      = kw.pop ("name", None) or TFL.Filename (file_name).base
            , ** kw
            )
    # end def __init__

    @TFL.Meta.Once_Property
    def body (self) :
        fn = self.file_name
        if self.static_handler and not sos.path.isfile (fn) :
            fn = self.static_handler.get_path (fn)
        with open (fn, "rb") as f :
            return pyk.decoded (f.read ().strip ())
    # end def body

    def __str__ (self) :
        return self.body
    # end def __str__

# end class Style_File

__all__ = tuple \
    ( k for (k, v) in pyk.iteritems (globals ())
        if  isinstance (v, M_Style_Sheet)
    )

if __name__ != "__main__" :
    CHJ.CSS._Export (* __all__)
### __END__ CHJ.CSS.Style_Sheet
