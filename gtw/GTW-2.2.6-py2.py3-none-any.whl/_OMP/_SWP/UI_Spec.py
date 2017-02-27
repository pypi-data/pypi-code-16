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
#    GTW.OMP.SWP.UI_Spec
#
# Purpose
#    UI specification for E_Types defined by GTW.OMP.SWP
#
# Revision Dates
#    16-Feb-2010 (MG) Creation (based on GTW.OMP.PAP.Nav)
#    24-Feb-2010 (CT) Creation continued
#    11-Mar-2010 (MG) Special widget's used for event date/time
#    23-Mar-2010 (CT) `Gallery` and `Picture` added
#    30-Apr-2010 (MG) Adapted to new form's
#     2-May-2010 (MG) Simplified
#     6-May-2010 (MG) Switch to render mode rendering
#     7-Nov-2011 (CT) Remove boilerplate from `afs_spec` for Entity_Link `clips`
#    18-Nov-2011 (CT) Import `unicode_literals` from `__future__`
#    24-Jan-2012 (CT) Remove `Form_args`, `*_completer`,
#                     i.e., stuff related to non-AFS forms
#    28-Jan-2014 (CT) Add `Referral`
#    26-Aug-2014 (CT) Replace `GTW.AFS` specification by `MF3_Form_Spec`
#    27-Nov-2015 (CT) Add `Video`
#    16-Dec-2015 (CT) Change to `UI_Spec`
#   ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

import _GTW._OMP._SWP

import _TFL.Sorted_By

class UI_Spec (object) :
    """UI specification for E_Types defined by GTW.OMP.SWP."""

    Clip_X               = dict \
        ( list_display   =
            ( "ui_display", "short_title", "date", "created_by", "format"
            , "last_changed"
            )
        , sort_key       = TFL.Sorted_By ("-date.start", "-prio", "perma_name")
        )

    Gallery              = dict \
        ( sort_key       = TFL.Sorted_By ("-date.start", "perma_name")
        )

    Page                 = dict \
        ( list_display   =
            ( "ui_display", "short_title", "date", "created_by", "format"
            , "last_changed"
            )
        , sort_key       = TFL.Sorted_By ("-date.start", "-prio", "perma_name")
        , MF3_Attr_Spec        = dict
            ( { "events.recurrence"    : dict
                ( include_rev_refs     = ("rules", )
                )
              }
            , events           = dict
                ( include_rev_refs = ("recurrence", )
                )
            )
        , MF3_Form_Spec        = dict
            ( include_rev_refs = ("events", "clips")
            )
        )

    Picture              = dict \
        ( sort_key       = TFL.Sorted_By \
            ("-left.date.start", "left.perma_name", "number")
        )

    Referral             = dict \
        ( list_display   = \
            ("date", "parent_url", "perma_name", "short_title")
        , sort_key       = TFL.Sorted_By \
            ("-date.start", "parent_url", "perma_name")
        )

    Video                = dict \
        ( sort_key       = TFL.Sorted_By ("-date.start", "perma_name")
        )

# end class UI_Spec

if __name__ != "__main__" :
    GTW.OMP.SWP._Export ("UI_Spec")
### __END__ GTW.OMP.SWP.UI_Spec
