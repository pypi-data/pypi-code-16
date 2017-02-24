# -*- coding: utf-8 -*-
# Copyright (C) 2015 Mag. Christian Tanzer All rights reserved
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
#    GTW.RST.TOP.Sitemap
#
# Purpose
#    Page providing a map of all non-hidden and authorized pages in tree-of-pages
#
# Revision Dates
#    22-Apr-2015 (CT) Creation
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

import _GTW._RST.Resource
import _GTW._RST._TOP.Page

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL.Decorator           import getattr_safe

_Ancestor = GTW.RST.TOP.Page

class Sitemap (_Ancestor) :
    """Page providing a sitemap of all non-hidden, authorized pages."""

    document_class     = "sitemap"
    page_template_name = "html/sitemap.jnj"
    pid                = "Sitemap"
    skip_etag          = True

    class Sitemap_GET (_Ancestor.GET) :

        _real_name      = "GET"
        _renderers      = _Ancestor.GET._renderers + \
            (GTW.RST.Mime_Type.TXT, )

        def _response_body (self, resource, request, response) :
            if response.renderer and response.renderer.name == "TXT" :
                returner = self._response_body_txt
            else :
                returner = self.__super._response_body
            return returner (resource, request, response)
        # end def _response_body

        def _response_body_txt (self, resource, request, response) :
            site   = request.host_url.rstrip ("/")
            result = "\n".join \
                (   "".join ((site, r.permalink))
                for r in resource.all_resources ()
                )
            return result
        # end def _response_body_txt

    GET = Sitemap_GET # end class

    def __init__ (self, ** kw) :
        kw.setdefault ("name",        "sitemap")
        kw.setdefault ("short_title", "Sitemap")
        self.__super.__init__ (** kw)
    # end def __init__

    def all_resources (self, resource = None) :
        for r in self.resources (resource) :
            yield r
            if r.own_links :
                for s in self.all_resources (r) :
                    yield s
    # end def all_resources

    def resources (self, resource = None, user = None) :
        if resource is None :
            resource = self.top
        if user is None :
            user = getattr (self.top, "user", None)
        for r in resource.own_links :
            if self.show_resource_p (r, user) :
                yield r
    # end def resources

    def show_resource_p (self, resource, user = None) :
        top = self.top
        if resource.hidden or resource.implicit :
            return False
        permissive = getattr (top, "permissive", False)
        return permissive or top.allow (resource, user)
    # end def show_resource_p

# end class Sitemap

if __name__ != "__main__" :
    GTW.RST.TOP._Export ("*")
### __END__ GTW.RST.TOP.Sitemap
