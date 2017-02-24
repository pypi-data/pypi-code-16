# -*- coding: utf-8 -*-
# Copyright (C) 2010-2014 Mag. Christian Tanzer All rights reserved
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
#    GTW.OMP.SWP.Page
#
# Purpose
#    Model a static web page
#
# Revision Dates
#    31-Jan-2010 (CT) Creation
#     2-Feb-2010 (CT) Creation continued
#     9-Feb-2010 (CT) Creation continued..
#    24-Feb-2010 (CT) s/Lifetime/Date_Interval/
#    24-Feb-2010 (CT) `head_line` added
#     5-Mar-2010 (CT) `author.Class` set to class `GTW.OMP.PAP.Person`
#     5-Mar-2010 (CT) `Page.rank` defined, attribute `prio` added
#     7-Mar-2010 (CT) s/title/short_title/; s/description/title/
#    17-Mar-2010 (CT) `email_obfuscator` removed
#    22-Mar-2010 (CT) `Object_PN` factored
#    24-Mar-2010 (CT) `Page_Y` added
#     8-Apr-2010 (CT) `year_max` removed from `Page_Y` (was a bad idea (TM))
#    10-May-2011 (CT) `hidden` added
#    14-Jul-2011 (CT) `head_line.max_length` increased to 256 (from 120)
#    18-Nov-2011 (CT) Import `unicode_literals` from `__future__`
#    11-Aug-2012 (CT) Set `Page` as `Object_PN.default_child`
#    28-Jan-2014 (CT) Factor `hidden`, `prio` to `Object_PN`
#    ««revision-date»»···
#--

from   __future__            import unicode_literals

from   _MOM.import_MOM          import *

from   _GTW                     import GTW

from   _GTW._OMP._SWP.Format    import A_Format
import _GTW._OMP._SWP.Object_PN

from   _TFL.I18N                import _, _T, _Tn

import _TFL.Decorator

_Ancestor_Essence = GTW.OMP.SWP.Entity

class Page_Mixin (_Ancestor_Essence) :
    """Mixin with the attributes of `Page`."""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        ### Non-primary attributes

        class contents (A_Text) :
            """Contents of web page in html format"""

            kind               = Attr.Internal
            auto_up_depends    = ("format", "text")

            def computed (self, obj) :
                return obj.format.convert (obj.text)
            # end def computed

        # end class contents

        class format (A_Format) :
            """Markup format used for `text`"""

            kind               = Attr.Optional
            Kind_Mixins        = (Attr.Sticky_Mixin, )
            default            = GTW.OMP.SWP.Format.ReST

        # end class format

        class head_line (A_String) :
            """Head line of the web page"""

            kind               = Attr.Optional
            max_length         = 256

        # end class head_line

        class text (A_Text) :
            """Text for web page in markup specified by `format`."""

            kind               = Attr.Required

        # end class text

    # end class _Attributes

# end class Page_Mixin

_Ancestor_Essence = GTW.OMP.SWP.Object_PN

@TFL.Add_To_Class ("default_child", _Ancestor_Essence)
class Page (_Ancestor_Essence, Page_Mixin) :
    """Model a static web page."""

# end class Page

_Ancestor_Essence = Page

class Page_Y (_Ancestor_Essence) :
    """Model a year-specific static web page."""

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        class year (A_Int) :
            """Year to which the web page applies."""

            kind               = Attr.Primary_Optional
            min_value          = 1986

        # end class year

    # end class _Attributes

# end class Page_Y

if __name__ != "__main__" :
    GTW.OMP.SWP._Export ("*")
### __END__ GTW.OMP.SWP.Page
