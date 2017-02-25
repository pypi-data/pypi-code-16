# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Mag. Christian Tanzer All rights reserved
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
#    GTW.OMP.SWP.Object_PN
#
# Purpose
#    Model an object with a perma_name.
#
# Revision Dates
#    17-Jun-2013 (CT) Creation (recovered from late `_SWP.Entity` module)
#    28-Jan-2014 (CT) Add `hidden` and `prio` (move from `SWP.Page_Mixin`)
#    13-Mar-2015 (CT) Add `check` against `/` to `perma_name`
#    27-Feb-2015 (CT) Add `not_in_past` to `date.start`  and `.finish`
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _MOM.import_MOM          import *
from   _MOM._Attr.Date_Interval import *

from   _GTW                     import GTW

import _GTW._OMP._SWP

_Ancestor_Essence = GTW.OMP.SWP.Object

class Object_PN (_Ancestor_Essence) :
    """Object with a perma_name."""

    is_partial  = True

    class _Attributes (_Ancestor_Essence._Attributes) :

        _Ancestor = _Ancestor_Essence._Attributes

        ### Primary attributes

        class perma_name (A_Date_Slug) :
            """Name used for perma-link."""

            kind               = Attr.Primary
            max_length         = 80
            ui_name            = "Name"

            check              = \
                ( """' ' not in value"""
                , """'/' not in value"""
                )

        # end class perma_name

        ### Non-primary attributes

        class date (A_Date_Interval_N) :
            """Publication (`start`) and expiration date (`finish`)"""

            class _Attributes :
                _Overrides     = dict \
                    ( finish   = dict (not_in_past = True)
                    , start    = dict (not_in_past = True)
                    )
            # end class _Attributes

            kind               = Attr.Optional

            explanation        = """
              The page won't be visible before the start date.

              After the finish date, the page won't be displayed (except
              possibly in an archive).
              """

        # end class date

        class hidden (A_Boolean) :
            """Don't show page in navigation."""

            kind               = Attr.Optional
            default            = False
            rank               = 1

        # end class hidden

        class prio (A_Int) :
            """Higher prio sorts before lower prio."""

            kind               = Attr.Optional
            Kind_Mixins        = (Attr.Sticky_Mixin, )
            default            = 0
            rank               = 1

        # end class prio

        class short_title (A_String) :
            """Short title (used in navigation)."""

            kind               = Attr.Necessary
            max_length         = 30

        # end class title

        class title (A_String) :
            """Title of the web page"""

            kind               = Attr.Necessary
            max_length         = 120

        # end class title

    # end class _Attributes

# end class Object_PN

if __name__ != "__main__" :
    GTW.OMP.SWP._Export ("*")
### __END__ GTW.OMP.SWP.Object_PN
