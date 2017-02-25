# -*- coding: utf-8 -*-
# Copyright (C) 2012-2016 Mag. Christian Tanzer All rights reserved
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
#    GTW.RST.TOP.Robot_Excluder
#
# Purpose
#    Page providing a /robots.txt file
#
# Revision Dates
#    24-Jul-2012 (CT) Creation
#    19-Feb-2014 (CT) Add `extra_excludes`
#    22-Apr-2015 (CT) Change `extra_excludes` to "/media/pdf" (was "/media")
#    22-Apr-2015 (CT) Factor `.Literal.TXT`; add `skip_etag`
#    22-Apr-2015 (CT) Add `Sitemap` to `contents`
#    26-Nov-2015 (CT) Factor `_excluded_urls`; consider `dynamic_p`, `static_p`
#     2-Dec-2015 (CT) Fix directories and sitemap of static pages
#    11-Jan-2016 (CT) Add missing `/` to `Sitemap` url
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

import _GTW._RST.Mime_Type
import _GTW._RST._TOP.Literal

from   _TFL._Meta.Once_Property import Once_Property

from   itertools                import chain as iter_chain

_Ancestor = GTW.RST.TOP.Literal.TXT

class Robot_Excluder (_Ancestor) :
    """Page providing a /robots.txt file."""

    exclude_robots             = False
    extra_excludes             = ["/media/pdf"]
    hidden                     = True
    ignore_picky_accept        = True
    implicit                   = False
    skip_etag                  = True
    static_page_suffix         = ".txt"

    def __init__ (self, ** kw) :
        self.__super.__init__ (name = "robots", ** kw)
    # end def __init__

    @Once_Property
    def contents (self) :
        top     = self.top
        dis_fmt = "Disallow: %s"
        exclude = list (dis_fmt % x for x in self._excluded_urls (top))
        extra   = list (dis_fmt % x for x in self.extra_excludes)
        result  = ""
        if exclude or extra :
            result = "\n".join \
                (iter_chain (["User-agent: *"], exclude, extra))
        sitemap = getattr (top.SC, "Sitemap", None)
        if sitemap is not None :
            request = getattr (top, "request", None)
            if request is not None :
                site   = request.host_url.rstrip ("/")
                if not site.endswith ("//localhost") :
                    result = "\n".join \
                        ( ( result
                          , "".join
                              (("Sitemap: ", site, "/", sitemap.name, ".txt"))
                          )
                        )
        return result
    # end def contents

    def _excluded_urls (self, top) :
        for r in top.own_links :
            if r.exclude_robots and (top.dynamic_p or r.static_p) :
                if r.static_page_suffix == "/index.html" :
                    yield r.abs_href_dynamic
                else :
                    yield r.abs_href_static
    # end def _excluded_urls

# end class Robot_Excluder

if __name__ != "__main__" :
    GTW.RST.TOP._Export ("*")
### __END__ GTW.RST.TOP.Robot_Excluder
