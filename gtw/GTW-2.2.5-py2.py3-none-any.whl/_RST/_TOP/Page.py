# -*- coding: utf-8 -*-
# Copyright (C) 2012-2017 Mag. Christian Tanzer All rights reserved
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
#    GTW.RST.TOP.Page
#
# Purpose
#    Model a leaf in tree of pages
#
# Revision Dates
#     5-Jul-2012 (CT) Creation (based on GTW.NAV.Base)
#    20-Jul-2012 (CT) Add `Alias`
#     6-Aug-2012 (MG) Add `Alias.is_current_page`
#     8-Aug-2012 (MG) Fix `Alias.is_current_page`
#    26-Sep-2012 (CT) Redefine `show_in_nav`
#     3-May-2013 (CT) Rename `login_required` to `auth_required`
#    24-Jan-2014 (CT) Add `_Mixin_` to bases of `Alias`
#    24-Jan-2014 (CT) Add `A_Link`
#    12-Mar-2014 (CT) Add `Alias.independent_permissions_p`
#     8-Oct-2015 (CT) Change `__getattr__` to *not* handle `__XXX__`
#    12-May-2016 (CT) Redefine `A_Link.as_static_page` to `pass`
#     8-Feb-2017 (CT) Make argument `nav_page` of `show_in_nav` optional
#    ««revision-date»»···
#--

from   __future__  import absolute_import, division, print_function, unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

import _GTW._RST.Resource
import _GTW._RST._TOP.Base

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL.Decorator           import getattr_safe

class TOP_Page (GTW.RST.TOP._Base_, GTW.RST.Leaf) :
    """Leaf of tree of pages."""

    _real_name                 = "Page"

    dir_template_name          = None

    def show_in_nav (self, nav_page = None) :
        return \
            (  self.__super.show_in_nav (nav_page)
            or (nav_page is not None and self.is_current_page (nav_page))
            )
    # end def show_in_nav

Page = TOP_Page # end class

class _Page_O_ (Page) :
    """Page relying on an object for some of its properties."""

    def __getattr__ (self, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        try :
            return self.__super.__getattr__ (name)
        except AttributeError :
            if name != "obj" :
                try :
                    obj = self.obj
                except Exception :
                    raise AttributeError (name)
                else :
                    return getattr (obj, name)
            raise
    # end def __getattr__

# end class _Page_O_

class Page_O (_Page_O_) :
    """Page relying on an object for some of its properties."""

    def __init__ (self, * args, ** kw) :
        self.ETM_name = kw.pop ("ETM")
        self.epk      = kw.pop ("epk")
        self.__super.__init__ (* args, ** kw)
    # end def __init__

    @property
    @getattr_safe
    def obj (self) :
        return self.top.scope [self.ETM_name].instance (* self.epk)
    # end def obj

# end class Page_O

class Page_P (_Page_O_) :
    """Page relying on an object stored by another page for some of its properties."""

    def __init__ (self, * args, ** kw) :
        self.base_href = kw.pop ("base_href")
        self.__super.__init__ (* args, ** kw)
    # end def __init__

    @property
    @getattr_safe
    def obj (self) :
        base_page = self.top.resource_from_href (self.base_href)
        if base_page is not None :
            return base_page.obj
    # end def obj

# end class Page_P

class TOP_Alias (GTW.RST.TOP._Mixin_, GTW.RST.Alias) :
    """Alias page delegating to a target page."""

    _real_name                 = "Alias"

    @Once_Property
    @getattr_safe
    def auth_required (self) :
        if self.independent_permissions_p :
            return self.__super.auth_required
        else :
            return (not self.target) or self.target.auth_required
    # end def auth_required

    def is_current_page (self, page) :
        if self.hidden :
            return self.target.is_current_page (page)
        else :
            return self.href_dynamic == page.href_dynamic
    # end def is_current_page

Alias = TOP_Alias # end class

class TOP_A_Link (GTW.RST.TOP._Mixin_, GTW.RST.A_Link) :
    """A link to another URL"""

    _real_name = "A_Link"

    def as_static_page (self) :
        """There is no static HTML page for this resource: it's just a link!"""
        pass
    # end def as_static_page

A_Link = TOP_A_Link # end class

if __name__ != "__main__" :
    GTW.RST.TOP._Export ("*")
### __END__ GTW.RST.TOP.Page
