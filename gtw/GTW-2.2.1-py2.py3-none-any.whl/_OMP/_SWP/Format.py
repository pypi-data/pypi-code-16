# -*- coding: utf-8 -*-
# Copyright (C) 2010-2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package GTW.OMP.SWP.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.OMP.SWP.Format
#
# Purpose
#    Provide formatter objects for different markup types
#
# Revision Dates
#    31-Jan-2010 (CT) Creation
#     2-Feb-2010 (CT) Creation continued
#    17-Mar-2010 (CT) Use `ReST.to_html` instead of `GTW.ReST.to_html`
#    17-Mar-2010 (CT) `Cleaner` added to `HTML`
#    22-Mar-2011 (CT) `M_Format.__str__` added
#    18-Nov-2011 (CT) Import `unicode_literals` from `__future__`
#    12-Oct-2014 (CT) Adapt `HTML` to `GTW.HTML.Cleaner` using BeautifulSoup4
#    13-Nov-2015 (CT) Adapt to changes in `markdown.Markdown` signature
#    11-Oct-2016 (CT) Change `GTW.HTML` to `TFL.HTML`
#    ««revision-date»»···
#--

from   __future__            import unicode_literals

from   _GTW                   import GTW
from   _ReST                  import ReST as RST
from   _TFL                   import TFL

from   _MOM.import_MOM        import *

import _GTW._OMP._SWP
import _TFL.HTML
import _ReST.To_Html

from   _TFL.I18N              import _, _T, _Tn
from   _TFL.pyk               import pyk

import _TFL._Meta.Object

class M_Format (TFL.Meta.Object.__class__) :
    """Meta class for formatter classes"""

    Table = {}

    def __init__ (cls, name, bases, dct) :
        cls.__m_super.__init__ (name, bases, dct)
        if name != "_Format_" :
            cls._m_add (name, cls.Table)
    # end def __init__

    def __str__ (cls) :
        return cls.__name__
    # end def __str__

    def _m_add (cls, name, Table) :
        name = pyk.text_type (name)
        assert name not in Table, "Name clash: `%s` <-> `%s`" % \
            (name, Table [name].__class__)
        Table [name] = cls
    # end def _m_add

# end class M_Format

class _Format_ (TFL.Meta.BaM (TFL.Meta.Object, metaclass = M_Format)) :

    pass

# end class _Format_

class HTML (_Format_) :
    """Formatter for text in HTML markup"""

    forbidden = \
        ( "applet body frame frameset head html iframe input object script"
            .split (" ")
        )

    @classmethod
    def convert (cls, text) :
        cleaner  = TFL.HTML.Cleaner (text, "html.parser")
        comments = cleaner.remove_comments ()
        if comments :
            raise ValueError \
                ( _T ("HTML must not contain comments:\n%s")
                % ("\n    ".join (comments), )
                )
        forbidden = cleaner.remove_tags (* cls.forbidden)
        if forbidden :
            raise ValueError \
                ( _T ("HTML must not contain any of the tags:\n%s")
                % ("    ".join (forbidden), )
                )
        return pyk.text_type (cleaner)
    # end def convert

# end class HTML

class ReST (_Format_) :
    """Formatter for re-structured text"""

    @classmethod
    def convert (cls, text) :
        return RST.to_html (text, encoding = "utf8")
    # end def convert

# end class ReST

class Markdown (_Format_) :
    """Formatter for text in `Markdown` markup"""

    MD         = None
    extensions = \
        ["markdown.extensions.headerid", "markdown.extensions.tables"]

    @classmethod
    def convert (cls, text) :
        if cls.MD is None :
            import markdown
            cls.MD = markdown.Markdown (extensions = cls.extensions)
        return HTML.convert (cls.MD.convert (text))
    # end def convert

# end class Markdown

class A_Format (MOM.Attr._A_Named_Object_) :
    """Format to use for text of a page"""

    example     = u"ReST"
    typ         = "Format"
    Table       = M_Format.Table

# end class A_Format

if __name__ != "__main__" :
    GTW.OMP.SWP._Export_Module ()
### __END__ GTW.OMP.SWP.Format
