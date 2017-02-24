# -*- coding: utf-8 -*-
# Copyright (C) 2015 Mag. Christian Tanzer All rights reserved
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
#    GTW.RST.TOP.MOM.Video
#
# Purpose
#    Page displaying a video
#
# Revision Dates
#    27-Nov-2015 (CT) Creation
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

import _GTW._RST._TOP._MOM.Display
import _GTW._RST._TOP.Video

from   _MOM.import_MOM          import MOM, Q

from   _TFL._Meta.Property      import Alias_Property
from   _TFL._Meta.Once_Property import Once_Property
from   _TFL.Decorator           import getattr_safe
from   _TFL.I18N                import _, _T, _Tn

class Video (GTW.RST.TOP._Video_, GTW.RST.TOP.MOM.Display.Entity) :
    """Page displaying a video"""

    @property
    @getattr_safe
    def desc (self) :
        return self.obj.desc
    # end def desc

    @property
    @getattr_safe
    def height (self) :
        return self.obj.height
    # end def height

    @property
    @getattr_safe
    def video_id (self) :
        return self.obj.video_id
    # end def video_id

    @property
    @getattr_safe
    def width (self) :
        return self.obj.width
    # end def width

# end class Video

_Ancestor = GTW.RST.TOP.MOM.Display.E_Type_Archive_DSY

class Archive (_Ancestor) :
    """Archive of videos organized by year."""

    class _Video_Year_ (_Ancestor.Year) :

        _real_name = "Year"

        Entity     = Video

    Year = _Video_Year_ # end class

# end class Archive

if __name__ != "__main__" :
    GTW.RST.TOP.MOM._Export_Module ()
### __END__ GTW.RST.TOP.MOM.Video
