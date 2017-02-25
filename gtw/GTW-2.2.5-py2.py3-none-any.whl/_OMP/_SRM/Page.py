# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package GTW.OMP.SRM.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.OMP.SRM.Page
#
# Purpose
#    Model a web page with information about a sailing regatta
#
# Revision Dates
#    20-Apr-2010 (CT) Creation
#    21-Apr-2010 (CT) Creation continued
#    22-Sep-2011 (CT) s/A_Entity/A_Id_Entity/
#    22-Sep-2011 (CT) s/Class/P_Type/ for _A_Id_Entity_ attributes
#    18-Nov-2011 (CT) Import `unicode_literals` from `__future__`
#    17-Apr-2013 (CT) Use `Computed_Set_Mixin`, not `Computed_Mixin`
#    ««revision-date»»···
#--

from   __future__            import unicode_literals

from   _GTW                     import GTW
from   _MOM.import_MOM          import *
from   _MOM._Attr.Date_Interval import *

import _GTW._OMP._SRM.Entity
import _GTW._OMP._SRM.Regatta_Event

import _GTW._OMP._SWP.import_SWP

from   _TFL.I18N                import _, _T, _Tn

_Ancestor_Essence = GTW.OMP.SWP.Page

class _SRM_Page_ (GTW.OMP.SRM.Object, _Ancestor_Essence) :
    """Web page with information about a sailing regatta."""

    _real_name = "Page"
    ui_name    = "Regatta_Page"

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        ### Primary attributes

        class event (A_Id_Entity) :
            """Regatta event to which this page belongs."""

            kind               = Attr.Primary
            P_Type             = GTW.OMP.SRM.Regatta_Event

        # end class event

        ### Non-primary attributes

        class desc (A_String) :
            """Description of the purpose of the page."""

            kind               = Attr.Optional
            Kind_Mixins        = (Attr.Computed_Set_Mixin, )
            max_length         = 30

            def computed (self, obj) :
                return obj.perma_name.rsplit (".", 1) [0].capitalize ()
            # end def computed

        # end class desc

        class short_title (A_String) :
            """Short title (used in navigation)."""

            kind               = Attr.Cached
            Kind_Mixins        = (Attr.Computed_Set_Mixin, )
            auto_up_depends    = ("desc", "event")

            def computed (self, obj) :
                return obj.desc
            # end def computed

        # end class short_title

        class title (A_String) :
            """Title of the web page"""

            kind               = Attr.Cached
            Kind_Mixins        = (Attr.Computed_Set_Mixin, )
            max_length         = 128
            auto_up_depends    = ("desc", "event")

            def computed (self, obj) :
                if obj.desc and obj.event :
                    return "%s %s" % (obj.desc, obj.event.title)
            # end def computed

        # end class title

        class year (A_Int) :
            """Year in which the regatta happens."""

            kind               = Attr.Cached
            Kind_Mixins        = (Attr.Computed_Set_Mixin, )
            auto_up_depends    = ("event", )

            def computed (self, obj) :
                if obj.event :
                    return obj.event.year
            # end def computed

        # end class year

    # end class _Attributes

Page = _SRM_Page_ # end class

if __name__ != "__main__" :
    GTW.OMP.SRM._Export ("*")
### __END__ GTW.OMP.SRM.Page
