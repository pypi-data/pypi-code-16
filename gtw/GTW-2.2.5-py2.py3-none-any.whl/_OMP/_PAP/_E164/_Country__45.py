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
#    GTW.OMP.PAP.E164._Country__45
#
# Purpose
#    Provide phone number mapping for Denmark
#
# Revision Dates
#     3-Aug-2015 (CT) Creation
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _GTW                         import GTW
from   _TFL                         import TFL

from   _TFL.defaultdict             import defaultdict
from   _TFL.Regexp                  import Regexp

import _GTW._OMP._PAP._E164.Country

class Country__45 (GTW.OMP.PAP.E164.Country_R) :
    """Provide phone number mapping for Denmark."""

    ###  3-Aug-2015 11:46 XXX This mapping is not really correct
    ### It should be generated from::
    ###     https://en.wikipedia.org/wiki/Telephone_numbers_in_Denmark
    ### Unfortunately, that page is ambiguous

    generated_from     = \
        "https://en.wikipedia.org/wiki/Local_conventions_for_writing_telephone_numbers#Denmark"
    generation_date    = "2015-08-03 10:30"

    formatted_sn       = GTW.OMP.PAP.E164.Country_M.formatted_sn_4x2

    ndc_max_length     = 0
    ndc_min_length     = 0
    ndc_sn_min_length  = 8
    ndc_sn_max_length  = 8

    regexp             = Regexp \
        ( r"(?P<sn>"
            r"(?:\d{2}[- ]\d{2}[- ]\d{2}[- ]\d{2}"
              r"|\d{4}[- ]\d{4}"
              r"|\d{2}[- ]\d{3}[- ]\d{3}"
              r"|\d{8}"
            r")"
          r")"
        )

Country = Country__45 # end class

### __END__ GTW.OMP.PAP.E164._Country__45
