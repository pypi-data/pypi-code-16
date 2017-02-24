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
#    GTW.OMP.PAP.E164._Country__41
#
# Purpose
#    Provide phone number mapping for Switzerland
#
# Revision Dates
#    27-Jul-2015 (CT) Creation
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _GTW                         import GTW
from   _TFL                         import TFL

from   _TFL.defaultdict             import defaultdict

import _GTW._OMP._PAP._E164.Country

class Country_41 (GTW.OMP.PAP.E164.Country_M) :
    """Provide phone number mapping for Switzerland, """

    generated_from     = \
        "https://en.wikipedia.org/wiki/Telephone_numbers_in_Switzerland"
    generation_date    = '2015-07-27 10:35'

    ndc_info_map       = \
        {  "21" : "Lausanne"
        ,  "22" : "Geneva"
        ,  "24" : "Yverdon, Aigle"
        ,  "26" : "Fribourg"
        ,  "27" : "Valais/Wallis"
        ,  "31" : "Bern and surrounding areas."
        ,  "32" : "Biel/Bienne, Neuchâtel, Solothurn, Jura"
        ,  "33" : "Berner Oberland"
        ,  "34" : "Region Bern-Emme"
        ,  "41" : "Central Switzerland (Luzern, Zug etc.)"
        ,  "43" : "Zurich"
        ,  "44" : "Zurich"
        ,  "51" : "business telecommunication networks (SBB, CFF, FFS)"
        ,  "52" : "Winterthur"
        ,  "55" : "Rapperswil"
        ,  "56" : "Baden"
        ,  "58" : "business telecommunication networks"
        ,  "61" : "Region Basel"
        ,  "62" : "Region Olten-Langenthal(Oberaargau)-Aargau-West"
        ,  "71" : "Region Eastern Switzerland (St. Gallen etc.)"
        ,  "74" : "mobile services: paging services"
        ,  "75" : "mobile services: GSM / UMTS - Swisscom"
        ,  "76" : "mobile services: GSM / UMTS - Sunrise (with Yallo, talktalk, Lebara, MTV Mobile)"
        ,  "77" : "mobile services: GSM / UMTS - various (M-Budget, Tele2)"
        ,  "78" : "mobile services: GSM / UMTS - Salt/Orange (with CoopMobile, cablecom)"
        ,  "79" : "mobile services: GSM / UMTS - Swisscom"
        , "800" : "freephone numbers"
        ,  "81" : "Chur"
        , "840" : "shared-cost numbers"
        , "842" : "shared-cost numbers"
        , "844" : "shared-cost numbers"
        , "848" : "shared-cost numbers"
        , "860" : "voice mail access (+ 9 digits phone without the initial 0, i.e. +41 860 66 555 44 33 is the voice mail of +41 66 555 44 33)"
        , "868" : "test numbers - Not accessible from abroad"
        , "869" : "VPN access code ( + 3 - 10 digits)"
        , "878" : "personal numbers (UPT)"
        , "900" : "Premium rate service for business, marketing"
        , "901" : "Premium rate service for entertainment,"
        , "906" : "Premium rate service for adult entertainment"
        ,  "91" : "Ticino"
        ,  "98" : "Inter-network routing numbers - Not accessible from abroad - Non diallable"
        ,  "99" : "Internal network numbers - Not accessible from abroad - Non diallable"
        }

    ndc_min_length     = 2

    ndc_types_normal   = {"geographic", "mobile"}

    ndc_usage_map = \
        {  "21" : "geographic"
        ,  "22" : "geographic"
        ,  "24" : "geographic"
        ,  "26" : "geographic"
        ,  "27" : "geographic"
        ,  "31" : "geographic"
        ,  "32" : "geographic"
        ,  "33" : "geographic"
        ,  "34" : "geographic"
        ,  "41" : "geographic"
        ,  "43" : "geographic"
        ,  "44" : "geographic"
        ,  "51" : "service"
        ,  "52" : "geographic"
        ,  "55" : "geographic"
        ,  "56" : "geographic"
        ,  "58" : "service"
        ,  "61" : "geographic"
        ,  "62" : "geographic"
        ,  "71" : "geographic"
        ,  "74" : "service"
        ,  "75" : "mobile"
        ,  "76" : "mobile"
        ,  "77" : "mobile"
        ,  "78" : "mobile"
        ,  "79" : "mobile"
        , "800" : "service"
        ,  "81" : "geographic"
        , "840" : "service"
        , "842" : "service"
        , "844" : "service"
        , "848" : "service"
        , "860" : "service"
        , "868" : "test"
        , "869" : "service"
        , "878" : "service"
        , "900" : "service"
        , "901" : "service"
        , "906" : "service"
        ,  "91" : "geographic"
        ,  "98" : "routing"
        ,  "99" : "internal"
        }

    sn_max_length_map  = sn_min_length_map = defaultdict \
        ( lambda : 7
        , { "800" : 6
          , "840" : 6
          , "842" : 6
          , "844" : 6
          , "848" : 6
          , "860" : 6
          , "868" : 6
          , "869" : 6
          , "878" : 6
          , "900" : 6
          , "901" : 6
          , "906" : 6
          }
        )

Country = Country_41 # end class

### __END__ GTW.OMP.PAP.E164._Country__41
