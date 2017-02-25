# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.RST.TOP.MOM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.RST.TOP.MOM.Gallery
#
# Purpose
#    Page displaying a gallery of pictures
#
# Revision Dates
#    18-Jul-2012 (CT) Creation
#    26-Jul-2012 (CT) Remove `_admin` from `pictures`
#     6-Aug-2012 (MG) Consider `hidden`in  `is_current_page`
#    10-Aug-2012 (CT) Fix `_admin` removal in `pictures` (use `isinstance`)
#     7-Dec-2012 (CT) Rename `query_filters` to `query_filters_d`
#    17-Nov-2015 (CT) Add `Gallery.entries_transitive`
#    17-Nov-2015 (CT) Set `Picture.hidden` to `False`
#    17-Nov-2015 (CT) Add `.html` if `not self.top.dynamic_p` to `permalink`
#    24-Nov-2015 (CT) Factor `GTW.RST.TOP._Gallery_`
#    ««revision-date»»···
#--

from   __future__ import absolute_import, division, print_function, unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

import _GTW._RST._TOP._MOM.Mixin
import _GTW._RST._TOP.Dir
import _GTW._RST._TOP.Gallery
import _GTW._RST._TOP.Page

from   _MOM.import_MOM          import MOM, Q

from   _TFL._Meta.Property      import Alias_Property
from   _TFL._Meta.Once_Property import Once_Property
from   _TFL.Decorator           import getattr_safe
from   _TFL.I18N                import _, _T, _Tn
from   _TFL.predicate           import first

from   posixpath                import join as pp_join

_Ancestor = GTW.RST.TOP.Page

class Picture (_Ancestor) :

    implicit = True

    def __init__ (self, ** kw) :
        obj = kw ["obj"]
        if "name" not in kw :
            kw ["name"] = obj.name
        self.__super.__init__ (** kw)
        self.hidden = False
    # end def __init__

    @property
    @getattr_safe
    def permalink (self) :
        result = self.parent.href_display (self.obj)
        if not self.top.dynamic_p :
            result = "".join ((result, self.static_page_suffix))
        return result
    # end def permalink

    @Once_Property
    @getattr_safe
    def photo (self) :
        return self.obj.photo
    # end def photo

    @Once_Property
    @getattr_safe
    def short_title (self) :
        return "%s: %s %s/%s" % \
            ( self.parent.obj.short_title
            , _T ("picture")
            , self.obj.name
            , self.parent.count
            )
    # end def short_title

    @Once_Property
    @getattr_safe
    def thumb (self) :
        return self.obj.thumb
    # end def thumb

# end class Picture

class Gallery \
          ( GTW.RST.TOP._Gallery_
          , GTW.RST.TOP.MOM.Entity_Mixin_Base
          , GTW.RST.TOP.MOM.E_Type_Mixin
          , GTW.RST.TOP.Dir_V
          ) :
    """Page displaying a gallery of pictures."""

    Entity              = Picture
    sort_key            = TFL.Sorted_By  ("number")

    def __init__ (self, ** kw) :
        kw ["ETM"] = "SWP.Picture"
        self.__super.__init__ (** kw)
    # end def __init__

    @Once_Property
    @getattr_safe
    def change_query_filters (self) :
        pid    = self.obj.pid
        rq     = self.ETM.query (Q.left == pid).attr ("pid")
        result = (Q.OR (Q.pid.IN (rq), Q.pid == pid), )
        return result
    # end def change_query_filters

    @property
    @getattr_safe
    def query_filters_d (self) :
        return self.__super.query_filters_d + (Q.left == self.obj.pid, )
    # end def query_filters_d

    def href_display (self, obj) :
        return pp_join (self.abs_href_dynamic, obj.name)
    # end def href_display

    def _get_child (self, child, * grandchildren) :
        result = self.__super._get_child (child, * grandchildren)
        if result and result.name in self._entry_map and not grandchildren :
            ### make sure to use result from `_entry_map`
            ### that allows `1`, `01`, `001`, `0001`, ...
            result = self._entry_map [result.name]
        return result
    # end def _get_child

    def _get_child_query (self, child) :
        try :
            number = int (child.split (".") [0])
        except (TypeError, ValueError) :
            result = None
        else :
            n, result = self.ETM.query_1 (number = number, * self.query_filters)
        if result is None :
            result = self.__super._get_child_query (child)
        return result
    # end def _get_child_query

# end class Gallery

_Ancestor = GTW.RST.TOP.MOM.Display.E_Type_Archive_DSY

class Archive (_Ancestor) :
    """Archive of galleries organized by year."""

    class _Gallery_Year_ (_Ancestor.Year) :

        _real_name = "Year"

        Entity     = Gallery

    Year = _Gallery_Year_ # end class

# end class Archive

if __name__ != "__main__" :
    GTW.RST.TOP.MOM._Export_Module ()
### __END__ GTW.RST.TOP.MOM.Gallery
