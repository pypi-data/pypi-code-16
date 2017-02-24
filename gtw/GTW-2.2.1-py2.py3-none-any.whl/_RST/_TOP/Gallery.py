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
#    GTW.RST.TOP.Gallery
#
# Purpose
#    Page displaying a gallery of pictures
#
# Revision Dates
#    24-Nov-2015 (CT) Creation
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

import _GTW._RST.Resource
import _GTW._RST._TOP.Page
import _GTW._RST._TOP.Dir

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL.Decorator           import getattr_safe
from   _TFL.Filename            import *
from   _TFL.I18N                import _, _T, _Tn
from   _TFL.pyk                 import pyk
from   _TFL                     import sos

from   posixpath import join as pjoin

_Ancestor = GTW.RST.TOP.Page

class _Picture_ (_Ancestor) :

    implicit        = True
    _size           = None

    def __init__ (self, ** kw) :
        self.__super.__init__ (** kw)
        self.hidden = False
    # end def __init__

    @property
    def height (self) :
        size = self.size
        if size is not None :
            return size [1]
    # end def height

    @Once_Property
    @getattr_safe
    def short_title (self) :
        return "%s: %s %s/%s" % \
            ( self.parent.short_title
            , _T ("picture")
            , self.number
            , self.parent.count
            )
    # end def short_title

    @property
    def size (self) :
        if self._size is None :
            from PIL import Image
            img = Image.open (self.src)
            self._size = img.size
        return self._size
    # end def size

    @Once_Property
    @getattr_safe
    def title (self) :
        return "%s: %s %s/%s" % \
            ( self.parent.title
            , _T ("picture")
            , self.number
            , self.parent.count
            )
    # end def title

    @property
    def width (self) :
        size = self.size
        if size is not None :
            return size [0]
    # end def width

# end class _Picture_

class Photo (_Picture_) :
    """Model one page of a web site displaying a single photo of a gallery."""

    page_template_name = "photo"
    photo              = property (lambda s : s)
    thumb              = None

# end class Photo

class Thumbnail (_Picture_) :

    photo              = None
    thumb              = property (lambda s : s)

# end class Thumbnail

_Ancestor = GTW.RST.TOP._Base_

class _Gallery_ (_Ancestor) :

    dir_template_name   = "gallery"
    nav_off_canvas      = True
    page_template_name  = "photo"
    sort_key            = TFL.Sorted_By  ("number")
    static_page_suffix  = "/index.html"

    _greet_entry        = None

    @property
    @getattr_safe
    def entries_transitive (self) :
        for e in self.entries :
            yield e
    # end def entries_transitive

    @Once_Property
    @getattr_safe
    def max_height_photo (self) :
        if self.pictures :
            return max (p.photo.height for p in self.pictures)
        return 0
    # end def max_height_photo

    @Once_Property
    @getattr_safe
    def max_height_thumb (self) :
        if self.pictures :
            return max (p.thumb.height for p in self.pictures)
        return 0
    # end def max_height_thumb

    @Once_Property
    @getattr_safe
    def max_width_photo (self) :
        if self.pictures :
            return max (p.photo.width for p in self.pictures)
        return 0
    # end def max_width_photo

    @Once_Property
    @getattr_safe
    def max_width_thumb (self) :
        if self.pictures :
            return max (p.thumb.width for p in self.pictures)
        return 0
    # end def max_width_thumb

    @property
    @getattr_safe
    def pictures (self) :
        result = self.entries
        if result and not isinstance (result [-1], self.Entity):
            result = result [:-1]
        return result
    # end def pictures

    def is_current_dir (self, page) :
        return False
    # end def is_current_dir

    def is_current_page (self, page) :
        return \
            ( not self.hidden
            and   self.href_dynamic in
                      (page.href_dynamic, page.parent.href_dynamic)
            )
    # end def is_current_page

# end class _Gallery_

class Gallery (_Gallery_, GTW.RST.TOP.Dir_V) :
    """Page displaying a gallery of pictures."""

    Entity              = Photo

    def __init__ (self, pic_dir, ** kw) :
        base           = Filename (pic_dir).base
        name           = pjoin (base, u"")
        pic_dir_abs    = sos.path.abspath (pic_dir)
        self.im_dir    = pjoin (pic_dir_abs, "im")
        self.th_dir    = pjoin (pic_dir_abs, "th")
        self._entries  = []
        self.__super.__init__ (name = name, pic_dir = pic_dir, ** kw)
    # end def __init__

    @property
    def count (self) :
        return len (self.pictures)
    # end def count

    @property
    def entries (self) :
        if not self._entries :
            self._read_entries ()
        return self._entries
    # end def entries

    def _get_child (self, child, * grandchildren) :
        if not grandchildren :
            if child == "index.html" :
                return self
            for p in self.photos :
                if child == p.name :
                    return p
    # end def _get_child

    def _read_entries (self) :
        result = []
        images = sorted (sos.expanded_globs (pjoin (self.im_dir, "*.jpg")))
        i      = 0
        for im in images :
            name = Filename (im).base
            th   = pjoin (self.th_dir, "%s.jpg" % name)
            if sos.path.exists (th) :
                i += 1
                photo = Photo     \
                    ( name         = name
                    , number       = i
                    , parent       = self
                    , src          = im
                    )
                thumb = photo.thumb = Thumbnail \
                    ( name         = name
                    , number       = i
                    , parent       = self
                    , photo        = photo
                    , src          = th
                    )
                result.append (photo)
        self.add_entries (* result)
    # end def _read_entries

# end class Gallery

if __name__ != "__main__" :
    GTW.RST.TOP._Export ("*", "_Gallery_")
### __END__ GTW.RST.TOP.Gallery
