# -*- coding: utf-8 -*-
# Copyright (C) 2010-2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package GTW.OMP.PAP.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.OMP.PAP.UI_Spec
#
# Purpose
#    UI specification for E_Types defined by GTW.OMP.PAP
#
# Revision Dates
#    29-Jan-2010 (CT) Creation
#     2-Feb-2010 (MG) `legend` and `title` added
#     3-Feb-2010 (MG) Completer added
#     3-Feb-2010 (MG) Use new `Role_Description`
#     5-Feb-2010 (MG) Adapted to new form handling
#     5-Feb-2010 (MG) First completer added
#     8-Feb-2010 (MG) Fixed `Person` form spec: `position` now is a
#                     composite attribute
#    27-Feb-2010 (MG) Additional completers added
#    30-Apr-2010 (MG) Adapted to new form's
#     2-May-2010 (MG) Simplified
#     6-May-2010 (MG) Switch to render mode rendering
#    13-Oct-2010 (CT) `Entity_created_by_Person` added
#    15-Mar-2011 (CT) Definitions for `GTW.AFS` added
#    19-May-2011 (CT) More definitions for `GTW.AFS` added
#    18-Nov-2011 (CT) Import `unicode_literals` from `__future__`
#    24-Jan-2012 (CT) Remove `Form_args`, `*_completer`,
#                     i.e., stuff related to non-AFS forms
#    22-Mar-2012 (CT) Add `Company` and its links
#    11-Oct-2012 (CT) Add `Address_Position`, `Url`
#     6-Dec-2012 (CT) Remove `Entity_created_by_Person`
#    12-Dec-2012 (CT) Add `Person_has_Account`
#    12-Dec-2012 (CT) Add `accounts` to `include_links` of `Person`
#     7-May-2013 (CT) Add `IM_Handle`, `Nickname`
#     7-May-2013 (CT) Add `Association`, `_import_association_cb`
#     7-May-2013 (CT) Add `urls` to `include_links` of `Person`
#    15-May-2013 (CT) Use `*_links` for `include_links`
#    21-Aug-2014 (CT) Replace `GTW.AFS` specification by `MF3_Form_Spec`
#     4-Sep-2014 (CT) Add `Adhoc_Group`, `Id_Entity_permits_Group`,
#                     `Person_in_Group`
#    16-Dec-2015 (CT) Change to `UI_Spec`
#     9-Feb-2016 (CT) Add `Company_1P`
#    24-Feb-2016 (CT) Add `Company_has_VAT_IDN`, `Person_has_VAT_IDN`
#     3-May-2016 (CT) Add `Subject_has_Property`
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

import _GTW._OMP._PAP

import _TFL.Sorted_By

class UI_Spec (object) :
    """UI specification for E_Types defined by GTW.OMP.PAP"""

    property_include_rev_refs = \
        ("persons", "companies", "associations")

    subject_include_rev_refs  = \
        ("addresses", "emails", "phones")

    Address              = dict \
        ( list_display   = ("zip", "city", "street", "desc")
        , MF3_Form_Spec  = dict
            ( include_rev_refs = ("gps", ) + property_include_rev_refs
            )
        , sort_key       = TFL.Sorted_By ( "zip", "street")
        )

    Adhoc_Group          = dict \
        (
        )

    Association          = dict \
        ( list_display   = ("name", "short_name", "lifetime")
        , MF3_Form_Spec  = dict
            ( include_rev_refs = subject_include_rev_refs
            )
        )

    Company              = dict \
        ( list_display   = ("name", "short_name", "lifetime")
        , MF3_Form_Spec  = dict
            ( include_rev_refs = subject_include_rev_refs
            )
        )

    Company_1P           = dict \
        ( list_display   =
            ( "ui_display", "short_name", "lifetime")
        , MF3_Form_Spec  = dict
            ( include_rev_refs = subject_include_rev_refs
            )
        )

    Email                = dict \
        ( list_display   = ("ui_display", "desc")
        , MF3_Form_Spec  = dict
            ( include_rev_refs = property_include_rev_refs
            )
        )

    IM_Handle            = dict \
        ( list_display   = ("ui_display", "desc")
        , MF3_Form_Spec  = dict
            ( include_rev_refs = property_include_rev_refs
            )
        )

    Nickname             = dict \
        ( list_display   = ("ui_display", "desc")
        , MF3_Form_Spec  = dict
            ( include_rev_refs = property_include_rev_refs
            )
        )

    Person               = dict \
        ( list_display   =
            ( "last_name", "first_name", "middle_name", "title"
            , "lifetime", "sex"
            )
        , MF3_Form_Spec  = dict
            ( include_rev_refs =
                (subject_include_rev_refs + ("im_handles", "accounts"))
            )
        )

    Phone                = dict \
        ( list_display   = ("ui_display", "desc")
        , MF3_Form_Spec  = dict
            ( include_rev_refs = property_include_rev_refs
            )
        )

    Url                  = dict \
        ( list_display   = ("ui_display", "desc")
        , MF3_Form_Spec  = dict
            ( include_rev_refs = property_include_rev_refs
            )
        )

    Address_Position     = dict \
        (
        )

    Company_has_Address  = dict \
        (
        )

    Company_has_Email    = dict \
        (
        )

    Company_has_Phone    = dict \
        (
        )

    Company_has_Url      = dict \
        (
        )

    Company_has_VAT_IDN  = dict \
        ( list_display   = ("left.ui_display", "vin")
        )

    Id_Entity_permits_Group = dict \
        (
        )

    Person_has_Account   = dict \
        (
        )

    Person_has_Address   = dict \
        (
        )

    Person_has_Email     = dict \
        (
        )

    Person_has_IM_Handle = dict \
        (
        )

    Person_has_Nickname  = dict \
        (
        )

    Person_has_Phone     = dict \
        (
        )

    Person_has_Url       = dict \
        (
        )

    Person_has_VAT_IDN   = dict \
        ( list_display   = ("left.ui_display", "vin")
        )

    Person_in_Group      = dict \
        ( sort_key       = TFL.Sorted_By ("pid") ### XXX remove this
        )

    Subject_has_Property = dict \
        (
        )

# end class UI_Spec

if __name__ != "__main__" :
    GTW.OMP.PAP._Export ("UI_Spec")
### __END__ GTW.OMP.PAP.UI_Spec
