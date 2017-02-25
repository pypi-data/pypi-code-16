# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Mag. Christian Tanzer All rights reserved
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
#    GTW.OMP.SWP.Picture
#
# Purpose
#    Model a picture that can be displayed on a web page
#
# Revision Dates
#    22-Mar-2010 (CT) Creation
#    13-Oct-2010 (CT) `example` added
#     5-Sep-2011 (CT) `width.max_value` increased from 1000 to 1200
#    22-Sep-2011 (CT) s/C_Type/P_Type/ for _A_Composite_ attributes
#    18-Nov-2011 (CT) Import `unicode_literals` from `__future__`
#    30-Jan-2013 (MG) Make `extension` changeable, change min values for
#                     width and height
#    31-Jan-2013 (MG) change kind of `extension` to `Optional`
#    15-May-2013 (CT) Replace `auto_cache` by `rev_ref_attr_name`
#    22-May-2013 (CT) Change `max_value` of `height` and `width` to 1280
#    30-Oct-2013 (CT) Remove unnecessary `Picture.left.rev_ref_attr_name`
#    25-Nov-2015 (CT) Change `_Pic_.path` from `A_String` to `A_Text`
#                     * don't want a restrictive `max_length`
#    ««revision-date»»···
#--

from   __future__            import unicode_literals

from   _MOM.import_MOM          import *
from   _GTW                     import GTW

import _GTW._OMP._SWP.Gallery

from   _MOM._Attr.A_2D          import A_2D_Int, D2_Value_Int

from   _TFL                     import sos
from   _TFL.I18N                import _, _T, _Tn

_Ancestor_Essence = D2_Value_Int

class _Pic_ (_Ancestor_Essence) :
    """Model a picture"""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class dir (A_String) :
            """Directory in gallery holding pictures."""

            kind               = Attr.Const
            default            = "im"

        # end class dir

        class extension (A_String) :
            """Extension of file holding picture."""

            kind               = Attr.Optional
            Kind_Mixins        = (Attr.Init_Only_Mixin, )
            max_length         = 10
            default            = ".jpg"

        # end class extension

        class height (_Ancestor.y) :
            """Height of picture."""

            max_value          = 1280
            min_value          = 200

        # end class height

        class path (A_Text) :
            """Path of file holding picture."""

            kind               = Attr.Computed

            def computed (self, obj) :
                owner = obj.owner
                if owner :
                    p = sos.path.join \
                        (owner.gallery.directory, obj.dir, owner.name)
                    return p + obj.extension
            # end def computed

        # end class path

        class width (_Ancestor.x) :
            """Width of picture."""

            max_value          = 1280
            min_value          = 200

        # end class width

    # end class _Attributes

# end class _Pic_

_Ancestor_Essence = _Pic_

class _Thumb_ (_Ancestor_Essence) :
    """Model a thumbnail of a picture."""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class dir (_Ancestor.dir) :
            """Directory in gallery holding thumbnails."""

            default            = "th"
            example            = "th"

        # end class dir

        class height (_Ancestor.height) :

            max_value          = 200
            min_value          = 50

        # end class height

        class width (_Ancestor.width) :

            max_value          = 200
            min_value          = 50

        # end class width

    # end class _Attributes

# end class _Thumb_

_Ancestor_Essence = GTW.OMP.SWP.Link1

class Picture (_Ancestor_Essence) :
    """Model a picture that can be displayed on a web page."""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        ### Primary attributes

        class left (_Ancestor.left) :
            """Gallery to which this picture belongs."""

            role_type          = GTW.OMP.SWP.Gallery

        # end class left

        class number (A_Int) :
            """Number of picture in gallery."""

            kind               = Attr.Primary
            check              = ("value >= 0", )

        # end class number

        ### Non-primary attributes

        class name (A_String) :

            kind               = Attr.Optional
            Kind_Mixins        = (Attr.Computed_Set_Mixin, )
            max_length         = 100

            def computed (self, obj) :
                if obj.number is not None :
                    return "%4.4d" % obj.number
            # end def computed

        # end class name

        class photo (A_2D_Int) :
            """Picture."""

            kind               = Attr.Necessary
            P_Type             = _Pic_
            typ                = "Picture"

        # end class photo

        class thumb (A_2D_Int) :
            """Thumbnail"""

            kind               = Attr.Necessary
            P_Type             = _Thumb_
            typ                = "Thumbnail"

        # end class thumb

    # end class _Attributes

# end class Picture

if __name__ != "__main__" :
    GTW.OMP.SWP._Export ("*")
### __END__ GTW.OMP.SWP.Picture
