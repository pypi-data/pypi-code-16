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
#    GTW.OMP.PAP.E164._Country__386
#
# Purpose
#    Provide phone number mapping for Slovenia
#
# Revision Dates
#    26-Jul-2015 (CT) Creation
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _GTW                         import GTW
from   _TFL                         import TFL

from   _TFL.defaultdict             import defaultdict

import _GTW._OMP._PAP._E164.Country

class Country__386 (GTW.OMP.PAP.E164.Country_M) :
    """Provide phone number mapping for Slovenia."""

    generated_from     = \
        "https://en.wikipedia.org/wiki/Telephone_numbers_in_Slovenia"
    generation_date    = "2015-07-26 15:10"

    ndc_info_map       = \
        {  "1" : "Ljubljana"
        ,  "2" : "Maribor, Murska Sobota, Ravne na Koroškem"
        ,  "3" : "Celje, Trbovlje"
        ,  "4" : "Kranj"
        ,  "5" : "Koper, Postojna, Nova Gorica"
        ,  "7" : "Novo Mesto, Krško"
        , "30" : "Si.mobil"
        , "31" : "Telekom Slovenije"
        , "40" : "Si.mobil"
        , "41" : "Telekom Slovenije"
        , "51" : "Telekom Slovenije"
        , "59" : "VoIP"
        , "64" : "T-2"
        , "68" : "Si.mobil"
        , "70" : "Tušmobil"
        , "71" : "Telekom Slovenije"
        , "81" : "VoIP"
        , "82" : "VoIP"
        , "83" : "VoIP"
        }

    ndc_max_length     = 2

    ndc_types_normal   = {"geographic", "mobile", "voip"}

    ndc_usage_map = \
        {  "1" : "geographic"
        ,  "2" : "geographic"
        ,  "3" : "geographic"
        ,  "4" : "geographic"
        ,  "5" : "geographic"
        ,  "7" : "geographic"
        , "30" : "mobile"
        , "31" : "mobile"
        , "40" : "mobile"
        , "41" : "mobile"
        , "51" : "mobile"
        , "59" : "voip"
        , "64" : "mobile"
        , "68" : "mobile"
        , "70" : "mobile"
        , "71" : "mobile"
        , "81" : "voip"
        , "82" : "voip"
        , "83" : "voip"
        }

    sn_max_length_map  = defaultdict \
        ( lambda : 6
        , {  "1" : 7
          ,  "2" : 7
          ,  "3" : 7
          ,  "4" : 7
          ,  "5" : 7
          ,  "7" : 7
          }
        )
    sn_min_length_map  = sn_max_length_map

Country = Country__386 # end class

### __END__ GTW.OMP.PAP.E164._Country__386
