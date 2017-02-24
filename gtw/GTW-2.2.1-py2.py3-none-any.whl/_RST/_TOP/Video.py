# -*- coding: utf-8 -*-
# Copyright (C) 2015-2016 Mag. Christian Tanzer All rights reserved
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
#    GTW.RST.TOP.Video
#
# Purpose
#    Page displaying a video
#
# Revision Dates
#    27-Nov-2015 (CT) Creation
#    11-Oct-2016 (CT) Change `GTW.HTML` to `TFL.HTML`
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

import _GTW._RST._TOP.Page
import _TFL.HTML

from   _TFL._Meta.Once_Property import Once_Property
from   _TFL.Decorator           import getattr_safe
from   _TFL.I18N                import _, _T, _Tn
from   _TFL.pyk                 import pyk

_Ancestor = GTW.RST.TOP._Base_

class _Video_ (_Ancestor) :

    page_template_name = "video"

    @Once_Property
    @getattr_safe
    def contents (self) :
        return self.render_video (** self._render_kw ())
    # end def contents

    @Once_Property
    @getattr_safe
    def render_video (self) :
        name   = "%s_video" % (self.video_server, )
        result = getattr (TFL.HTML, name)
        return result
    # end def render_video

    def _render_kw (self, ** kw) :
        return dict \
            ( dict
                ( css_class    = "centered"
                , desc         = getattr (self, "desc", None) or self.title
                , height       = self.height
                , video_id     = self.video_id
                , width        = self.width
                )
            , ** kw
            )
    # end def _render_kw

# end class _Video_

_Ancestor = GTW.RST.TOP.Page

class Video (_Video_, _Ancestor) :
    """Page displaying a video"""

    video_server = "youtube"
    height       = 360
    width        = 640

    def __init__ (self, video_id, ** kw) :
        self.__super.__init__ (video_id = video_id, ** kw)
    # end def __init__

# end class Video

if __name__ != "__main__" :
    GTW.RST.TOP._Export ("*", "_Video_")
### __END__ GTW.RST.TOP.Video
