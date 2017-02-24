# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package GTW.OMP.EVT.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.OMP.EVT.UI_Spec
#
# Purpose
#    UI specification for E_Types defined by GTW.OMP.EVT
#
# Revision Dates
#    15-Mar-2010 (CT) Creation
#    30-Apr-2010 (MG) Adapted to new form's
#     2-May-2010 (MG) Simplified
#     8-Nov-2011 (CT) `Calendar` added
#    18-Nov-2011 (CT) Import `unicode_literals` from `__future__`
#    24-Jan-2012 (CT) Remove `Form_args`,
#                     i.e., stuff related to non-AFS forms
#    24-Feb-2012 (CT) Remove `Event_occurs` (too electric by far)
#    24-Feb-2014 (CT) Change `Event.list_display` (add `short_title`; order)
#    26-Aug-2014 (CT) Replace `GTW.AFS` specification by `MF3_Form_Spec`
#    16-Dec-2015 (CT) Change to `UI_Spec`
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

import _GTW._OMP._EVT

import _TFL.Sorted_By

class UI_Spec (object) :
    """UI specification for E_Types defined by GTW.OMP.EVT."""

    Calendar            = dict \
        (
        )

    Event               = dict \
        ( list_display  = ("date", "time", "short_title", "left", "calendar")
        , sort_key      = TFL.Sorted_By
            ("-date.start", "-time.start", "short_title", "left")
        , MF3_Attr_Spec        = dict
            ( recurrence       = dict
                ( include_rev_refs = ("rules", )
                )
            )
        , MF3_Form_Spec        = dict
            ( include_rev_refs = ("recurrence", )
            )
        )

    Recurrence_Spec     = dict \
        ( MF3_Form_Spec        = dict
            ( include_rev_refs = ("rules", )
            )
        )

# end class UI_Spec

if __name__ != "__main__" :
    GTW.OMP.EVT._Export ("UI_Spec")
### __END__ GTW.OMP.EVT.UI_Spec
