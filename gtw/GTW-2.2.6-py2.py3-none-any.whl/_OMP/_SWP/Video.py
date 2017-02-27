# -*- coding: utf-8 -*-
# Copyright (C) 2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.OMP.SWP.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.OMP.SWP.Video
#
# Purpose
#    Model a video served by youtube or vimeo
#
# Revision Dates
#    27-Nov-2015 (CT) Creation
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _MOM.import_MOM          import *
from   _GTW                     import GTW

import _GTW._OMP._SWP.Entity

from   _TFL.I18N                import _, _T, _Tn

_Ancestor_Essence = GTW.OMP.SWP.Object_PN

class Video (_Ancestor_Essence) :
    """Video served by youtube or vimeo."""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class video_id (A_String) :
            """Id of video as served by `video_server`."""

            kind               = Attr.Required

        # end class video_id

        class video_server (A_Enum) :
            """Service providing the video."""

            kind               = Attr.Optional
            typ                = "Video-Server"
            default            = "youtube"
            C_Type             = A_String
            Table              = dict \
                ( vimeo        = "vimeo.com"
                , youtube      = "youtube.com"
                )

        # end class video_server

        class desc (A_Text) :
            """Description of video."""

            kind               = Attr.Optional
            ui_name            = _ ("Description")

        # end class desc

        class height (A_Int) :
            """Height of video in pixels."""

            kind               = Attr.Optional
            default            = 360
            max_value          = 2160
            min_value          = 240

        # end class height

        class width (A_Int) :
            """Width of video in pixels."""

            kind               = Attr.Optional
            default            = 640
            max_value          = 4096
            min_value          = 240

        # end class width

    # end class _Attributes

# end class Video

if __name__ != "__main__" :
    GTW.OMP.SWP._Export ("*")
### __END__ GTW.OMP.SWP.Video
