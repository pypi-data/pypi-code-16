# -*- coding: utf-8 -*-
# Copyright (C) 2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.OMP.PAP.E164.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    GTW.OMP.PAP.E164._Country__33
#
# Purpose
#    Provide phone number mapping for France
#
# Revision Dates
#    27-Jul-2015 (CT) Creation
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _GTW                         import GTW
from   _TFL                         import TFL

from   _TFL.defaultdict             import defaultdict

import _GTW._OMP._PAP._E164.Country

class Country_33 (GTW.OMP.PAP.E164.Country_M) :
    """Provide phone number mapping for France."""

    generated_from     = \
        "https://en.wikipedia.org/wiki/Telephone_numbers_in_France"
    generation_date    = "2015-07-27 10:05"

    formatted_sn       = GTW.OMP.PAP.E164.Country_M.formatted_sn_4x2

    ndc_info_map       = \
        { "1" : "Île-de-France"
        , "2" : "Northwest France"
        , "3" : "Northeast France"
        , "4" : "Southeast France"
        , "5" : "Southwest France"
        , "6" : "Mobile phone services"
        , "7" : "Mobile phone services"
        , "8" : "Freephone (numéro vert) and shared-cost services."
        , "9" : "Non-geographic number (used by VoIP services)"
        }

    ndc_max_length     = 1

    ndc_types_normal   = {"geographic", "mobile", "voip"}

    ndc_usage_map      = \
        { "1" : "geographic"
        , "2" : "geographic"
        , "3" : "geographic"
        , "4" : "geographic"
        , "5" : "geographic"
        , "6" : "mobile"
        , "7" : "mobile"
        , "8" : "service"
        , "9" : "voip"
        }

    sn_max_length_map  = defaultdict (lambda : 8)
    sn_mix_length_map  = defaultdict (lambda : 8)

Country = Country_33 # end class

### __END__ GTW.OMP.PAP.E164._Country__33
