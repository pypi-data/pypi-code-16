# -*- coding: utf-8 -*-
# Copyright (C) 2012 Mag. Christian Tanzer All rights reserved
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
#    GTW.RST.TOP.ReST
#
# Purpose
#    Model a static page based on literal text in ReST format
#
# Revision Dates
#     6-Dec-2012 (CT) Creation (based on GTW.NAV.ReST)
#    ««revision-date»»···
#--

from   __future__ import absolute_import, division, print_function, unicode_literals

from   _GTW                     import GTW
from   _ReST                    import ReST
from   _TFL                     import TFL

import _GTW._RST.Resource
import _GTW._RST._TOP.Page

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL.Decorator           import getattr_safe
from   _TFL.predicate           import split_hst

class Page_ReST (GTW.RST.TOP.Page) :
    """Model a static page based on literal text in ReST format."""

    def __init__ (self, ** kw) :
        self.__super.__init__ (** kw)
        self._contents_by_lang = {}
    # end def __init__

    @property
    @getattr_safe
    def contents (self) :
        lang   = split_hst (getattr (self, "language", "en"), "_") [0]
        result = self._contents_by_lang.get (lang)
        if result is None :
            src = self.src_contents
            if src is not None :
                result = self._contents_by_lang [lang] = ReST.to_html \
                    ( src
                    , encoding = self.encoding
                    , language = lang
                    )
        return result
    # end def contents

# end class Page_ReST

if __name__ != "__main__" :
    GTW.RST.TOP._Export ("*")
### __END__ GTW.RST.TOP.ReST
