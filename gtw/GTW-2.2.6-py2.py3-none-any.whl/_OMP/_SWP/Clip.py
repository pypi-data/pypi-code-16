# -*- coding: utf-8 -*-
# Copyright (C) 2010-2013 Mag. Christian Tanzer All rights reserved
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
#    GTW.OMP.SWP.Clip
#
# Purpose
#    Model a news clip
#
# Revision Dates
#     9-Apr-2010 (CT) Creation
#    12-Apr-2010 (CT) Creation continued
#    22-Sep-2011 (CT) s/C_Type/P_Type/ for _A_Composite_ attributes
#    18-Nov-2011 (CT) Import `unicode_literals` from `__future__`
#    15-May-2013 (CT) Replace `auto_cache` by `rev_ref_attr_name`
#    25-Jul-2013 (CT) Add import of `SWP.Object_PN`
#    30-Oct-2013 (CT) Fix `Clip_O.left` to set `link_ref_attr_name`, not
#                     `rev_ref_attr_name`
#    ««revision-date»»···
#--

from   __future__            import unicode_literals

from   _GTW                     import GTW
from   _MOM.import_MOM          import *
from   _MOM._Attr.Date_Interval import *

import _GTW._OMP._SWP.Object_PN
import _GTW._OMP._SWP.Page
from   _GTW._OMP._SWP.Format    import A_Format

from   _TFL.I18N                import _, _T, _Tn

_Ancestor_Essence = GTW.OMP.SWP.Link1

class Clip_O (_Ancestor_Essence) :
    """News clip for a object."""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        ### Primary attributes

        class left (_Ancestor.left) :
            """Object the news clip refers to"""

            role_type          = GTW.OMP.SWP.Object_PN
            role_name          = "object"
            link_ref_attr_name = "clip"

        # end class left

        class date_x (A_Date_Interval) :
            """Publication (`start`) and expiration date (`finish`).
               Unspecified values will be taken from the web page the clip
               belongs to.
            """

            kind               = Attr.Primary_Optional
            ui_name            = "date"

        # end class date_x

        ### Non-primary attributes

        class abstract (A_Text) :
            """Text for news clip in markup specified by `format`."""

            kind               = Attr.Required

        # end class abstract

        class contents (A_Text) :
            """Contents of web page in html format"""

            kind               = Attr.Internal
            auto_up_depends    = ("abstract", )

            def computed (self, obj) :
                if obj.left :
                    return obj.left.format.convert (obj.abstract)
            # end def computed

        # end class contents

        class date (A_Date_Interval) :

            kind               = Attr.Internal
            auto_up_depends    = ("date_x", "left")

            def computed (self, obj) :
                result = obj.date_x
                if result is not None and obj.left :
                    if not (result.start and result.finish) :
                        result = self.P_Type \
                            ( start  = result.start  or obj.left.date.start
                            , finish = result.finish or obj.left.date.finish
                            )
                return result
            # end def computed

        # end class date

        class prio (A_Int) :
            """Higher prio sorts before lower prio."""

            kind               = Attr.Optional
            Kind_Mixins        = (Attr.Sticky_Mixin, )
            default            = 0

        # end class prio

    # end class _Attributes

# end class Clip_O

_Ancestor_Essence = GTW.OMP.SWP.Page

class Clip_X (_Ancestor_Essence) :
    """News clip for the front page of a website referring to an external web
       page.
    """

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        head_line = None

        class link_to (A_Url) :
            """Url of external web page providing information about this clip"""

            kind               = Attr.Optional

        # end class link_to

        short_title = None

        class text (_Ancestor.text) :
            """Text for news clip in markup specified by `format`."""

        # end class text

        class title (_Ancestor.title) :
            """Title of news clip."""

        # end class title

    # end class _Attributes

# end class Clip_X

if __name__ != "__main__" :
    GTW.OMP.SWP._Export ("*")
### __END__ GTW.OMP.SWP.Clip
