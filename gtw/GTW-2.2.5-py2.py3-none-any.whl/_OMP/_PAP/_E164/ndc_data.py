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
#    GTW.OMP.PAP.E164.ndc_data
#
# Purpose
#    Provide data about national destination code (ndc) and subscriber numer
#    (sn) for countries with a simple national number plan
#
# Revision Dates
#    24-Jul-2015 (CT) Creation
#    ««revision-date»»···
#--

from   __future__               import division, print_function
from   __future__               import absolute_import, unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

from   _TFL.Regexp              import \
    (Regexp, Multi_Regexp, Re_Replacer, Multi_Re_Replacer, re)

import _GTW._OMP._PAP._E164

### https://en.wikipedia.org/wiki/Telephone_numbers_in_Poland
_poland_geo_ndc = "".join \
    ( ( "(?:"
      , "|".join
           ( ( "1[2-8]"
             , "2[2-59]"
             , "3[2-4]"
             , "4[1-468]"
             , "5[245689]"
             , "6[123578]"
             , "7[14-7]"
             , "8[1-79]"
             , "9[145]"
             )
           )
      , ")"
      )
    )
_poland_mobile_ndc = "".join \
    ( ( "(?:"
      , "|".join
           ( ( "5[0137]"
             , "6[069]"
             , "7[2389]"
             , "88"
             )
           )
      , ")"
      )
    )
_poland_ndc= "".join \
    ( ( "(?:"
      , "|".join ((_poland_geo_ndc, _poland_mobile_ndc))
      , ")"
      )
    )

### https://en.wikipedia.org/wiki/Local_conventions_for_writing_telephone_numbers
### Map of regular expressions for matching phone numbers,
### indexed by country code
ndc_sn_matcher_map = \
    {    "1" : ### North America (US, CA, ...)
               ### https://en.wikipedia.org/wiki/Local_conventions_for_writing_telephone_numbers#United_States.2C_Canada.2C_and_other_NANP_countries
               ### https://en.wikipedia.org/wiki/North_American_Numbering_Plan
        Multi_Regexp
          ( Regexp
              ( r"\(" + r"(?P<ndc>[0-9]{3})" + r"\) ?"
                r"(?P<sn>[0-9]{3}[- .]?[0-9]{4})?"
              )
          , Regexp
              ( r"(?P<ndc>[0-9]{3})[- .]"
                r"(?P<sn>[0-9]{3}[- .]?[0-9]{4})?"
              )
          )
    , "351" : ### Portugal
              ### https://en.wikipedia.org/wiki/Local_conventions_for_writing_telephone_numbers#Portugal
        Multi_Regexp
          ( Regexp
              ( r"(?P<ndc>2[12]|9[1236])[- ]?"
                r"(?P<sn>\d{2}[- ]?\d{2}[- ]?\d{3})?"
              )
          , Regexp
              ( r"(?P<ndc>256|309)[- ]?"
                r"(?P<sn>\d{3}[- ]?\d{3})?"
              )
          )
    ,  "36" : ### Hungary
              ### https://en.wikipedia.org/wiki/Telephone_numbers_in_Hungary
        Regexp
          ( r"(?P<ndc>1|[2-9][0-9]) ?"
            r"(?P<sn>[0-9]{3}[- ]?[0-9]{3,4})?"
          )
    ,  "47" : ### Norway
              ### https://en.wikipedia.org/wiki/Telephone_numbers_in_Norway
        Multi_Regexp
          ( Regexp
              ( r"(?P<ndc>[49]\d{2}|59\d)[- ]?"
                r"(?P<sn>\d{2}[- ]?\d{3})?"
              )
          , Regexp
              ( r"(?P<ndc>58\d)[- ]?"
                r"(?P<sn>\d{3}[- ]?\d{3}[- ]?\d{3})?"
              )
          , Regexp
              ( r"(?P<ndc>3[23578])[- ]?"
                r"(?P<sn>\d{2}[- ]?\d{2}[- ]?\d{2})?"
              )
          , Regexp
              ( r"(?P<ndc>[2567])"
                r"(?P<sn>\d[- ]?\d{2}[- ]?\d{2}[- ]?\d{2})?"
              )
          )
    ,  "48" : ### Poland
              ### https://en.wikipedia.org/wiki/Telephone_numbers_in_Poland
        Multi_Regexp
          ( Regexp
              ( r"(?P<ndc>" + _poland_ndc + ")[- ]?"
                r"(?P<sn>\d{3}[- ]?\d{2}[- ]?\d{2})?"
              )
          , Regexp
              ( r"(?P<ndc>" + _poland_mobile_ndc + ")?"
                r"(?P<sn>\d[- ]?\d{3}[- ]?\d{3})?"
              )
          , Regexp
              ( r"\(" + r"(?P<ndc>" + _poland_ndc + ")" + r"\) ?"
                r"(?P<sn>\d{3}[- ]?\d{2}[- ]?\d{2})?"
              )
          )
    }

### https://en.wikipedia.org/wiki/Local_conventions_for_writing_telephone_numbers
### maximum length of ndc+sn, indexed by country code
ndc_sn_max_length = \
    {   "1" : 10
    ,  "31" :  9
    ,  "32" :  9
    ,  "33" :  9
    , "351" :  9
    ,  "34" :  9
    , "386" :  8
    ,  "41" :  9
    ,  "43" : 13
    ,  "44" : 10
    ,  "45" :  8
    ,  "47" :  8
    ,  "48" :  9
    ,  "49" : 11
    }

### https://en.wikipedia.org/wiki/Local_conventions_for_writing_telephone_numbers
### minimum length of ndc+sn, indexed by country code
ndc_sn_min_length = \
    {   "1" : 10
    ,  "31" :  9
    ,  "32" :  8
    ,  "33" :  9
    , "351" :  9
    ,  "34" :  9
    , "386" :  8
    ,  "41" :  9
    ,  "43" :  8
    ,  "44" :  9
    ,  "45" :  8
    ,  "47" :  8
    ,  "48" :  9
    ,  "49" :  5
    }

if __name__ != "__main__" :
    GTW.OMP.PAP.E164._Export ("*")
### __END__ GTW.OMP.PAP.E164.ndc_data
