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
#    GTW.OMP.SRM.Regatta_Event
#
# Purpose
#    Model a sailing regatta event for one or more classes/handicaps
#
# Revision Dates
#    15-Apr-2010 (CT) Creation
#     5-May-2010 (CT) `perma_name` changed from `Cache` to `Internal` to
#                     allow use in queries
#    11-May-2010 (CT) `club` added
#    23-Nov-2010 (CT) `ui_date` changed to avoid display of `start == finish`
#    14-Dec-2010 (CT) `year` changed from `Internal` to `Cached`
#     8-Sep-2011 (CT) `completer` added to `name`, `club` and `desc`
#    23-Sep-2011 (CT) `club` changed from `A_String` to `A_Id_Entity`
#     9-Nov-2011 (CT) Change `computed` methods to use `FO`
#    18-Nov-2011 (CT) Import `unicode_literals` from `__future__`
#    24-Jan-2012 (CT) Correct `club.description`
#    30-May-2012 (CT) Add attribute `is_cancelled`
#     9-Jan-2014 (CT) Use `–`, not `--`
#    17-Jan-2014 (CT) Change attribute `year` to `Attr.Query`
#    10-Feb-2015 (CT) Add `ui_date_short` (`ui_date` without `year`)
#    ««revision-date»»···
#--

from   __future__            import unicode_literals

from   _GTW                     import GTW
from   _MOM.import_MOM          import *
from   _MOM._Attr.Date_Interval import *

import _GTW._OMP._SRM.Club
import _GTW._OMP._SRM.Entity

from   _TFL.I18N                import _, _T, _Tn
from   _TFL.pyk                   import pyk

import _TFL.Ascii

_Ancestor_Essence = GTW.OMP.SRM.Object

class Regatta_Event (_Ancestor_Essence) :
    """Sailing regatta event for one or more classes/handicaps."""

    ui_display_sep        = " "

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        ### Primary attributes

        class name (A_String) :
            """Name of the regatta event."""

            kind               = Attr.Primary
            ignore_case        = True
            example            = "Fastnet Race"
            max_length         = 64
            completer          = Attr.Completer_Spec  (1, Attr.Selector.primary)

        # end class name

        class date (A_Date_Interval_C) :
            """`start` and `finish` date of regatta"""

            kind               = Attr.Primary

            completer          = Attr.C_Completer_Spec (Attr.Selector.primary)

        # end class date

        ### Non-primary attributes

        class club (A_Id_Entity) :
            """Club that organizes the regatta."""

            P_Type             = GTW.OMP.SRM.Club
            kind               = Attr.Optional

        # end class club

        class desc (A_String) :
            """Short description of the regatta."""

            kind               = Attr.Optional
            example            = "The famous classic"
            max_length         = 160
            completer          = Attr.Completer_Spec  (1)

        # end class desc

        class is_cancelled (A_Boolean) :
            """Indicates that the regatta is cancelled"""

            kind               = Attr.Optional
            default            = False

        # end class is_cancelled

        class perma_name (A_String) :
            """Name used for perma-link."""

            kind               = Attr.Internal
            Kind_Mixins        = (Attr.Computed_Set_Mixin, )
            auto_up_depends    = ("name", )

            def computed (self, obj) :
                return pyk.decoded \
                    (TFL.Ascii.sanitized_filename (obj.name.lower ()))
            # end def computed

        # end class perma_name

        class short_title (A_String) :

            kind               = Attr.Cached
            Kind_Mixins        = (Attr.Computed_Set_Mixin, )
            auto_up_depends    = ("name", )

            def computed (self, obj) :
                return obj.FO.name
            # end def computed

        # end class title

        class title (A_String) :

            kind               = Attr.Cached
            Kind_Mixins        = (Attr.Computed_Set_Mixin, )
            max_length         = 128
            auto_up_depends    = ("date", "name", "desc")

            def computed (self, obj) :
                return " ".join ((obj.FO.desc or obj.FO.name, obj.ui_date))
            # end def computed

        # end class title

        class _ui_date_ (A_String) :

            kind               = Attr.Cached
            Kind_Mixins        = (Attr.Computed_Set_Mixin, )
            auto_up_depends    = ("date", )
            ui_name            = _ ("Date")

            def computed (self, obj) :
                date_format   = self.date_format
                start, finish = obj.date.start, obj.date.finish
                result        = []
                if finish is not None and finish.month == start.month :
                    if finish != start :
                        result.append (start.strftime  ("%d."))
                else :
                    result.append (start.strftime  (date_format))
                if finish is not None :
                    result.append (finish.strftime (date_format))
                return "–".join (result)
            # end def computed

        # end class _ui_date_

        class ui_date (_ui_date_) :

            date_format        = "%d.%m.%Y"

        # end class ui_date

        class ui_date_short (_ui_date_) :

            date_format        = "%d.%m."

        # end class ui_date_short

        class year (A_Int) :
            """Year in which the regatta happens."""

            kind               = Attr.Query
            query              = Q.date.start.year

        # end class year

    # end class _Attributes

# end class Regatta_Event

if __name__ != "__main__" :
    GTW.OMP.SRM._Export ("*")
### __END__ GTW.OMP.SRM.Regatta_Event
