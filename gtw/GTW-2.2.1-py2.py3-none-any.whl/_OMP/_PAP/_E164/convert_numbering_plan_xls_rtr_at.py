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
#    GTW.OMP.PAP.E164.convert_numbering_plan_xls_rtr_at
#
# Purpose
#    Convert the spreadsheet supplied by rtr.at for the Austrian Numbering Plan
#
# Revision Dates
#    23-Jul-2015 (CT) Creation
#    ««revision-date»»···
#--

from   __future__          import division, print_function
from   __future__          import absolute_import, unicode_literals

from   _TFL                import TFL
from   _TFL                import sos
from   _TFL.defaultdict    import defaultdict
from   _TFL.formatted_repr import formatted_repr
from   _TFL.portable_repr  import portable_repr
from   _TFL.predicate      import identity
from   _TFL.pyk            import pyk
from   _TFL.Regexp         import Regexp, Re_Replacer, Multi_Re_Replacer, re

import _TFL.CAO
import _TFL._Meta.Object

import datetime
import xlrd

### 23-Jul-2015 10:43
### https://www.rtr.at/de/tk/E129/2312_Austrian_Numbering_Plan_2011-03-30.xls

_module_format = r"""
# -*- coding: utf-8 -*-
# Copyright (C) %(year)s Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package GTW.OMP.PAP.E164.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
# *** This file was generated automatically by
# ***     %(generated_by)s
# *** DO NOT edit it manually !
#

from   __future__               import unicode_literals

from   _GTW                     import GTW
from   _TFL                     import TFL

from   _TFL.defaultdict         import defaultdict

import _GTW._OMP._PAP._E164.Country

class Country__43 (GTW.OMP.PAP.E164.Country_M) :

    generated_from     = %(generated_from)s
    generation_date    = %(generation_date)s

    ndc_info_map       = \
        %(ndc_info_map)s

    ndc_types_normal   = %(ndc_types_normal)s

    ndc_usage_map      = \
        %(ndc_usage_map)s

    sn_max_length_map  = defaultdict \
        ( lambda : %(max_len_default)s
        , %(sn_max_length_map)s
        )

    sn_min_length_map  = defaultdict \
        ( lambda : %(min_len_default)s
        , %(sn_min_length_map)s
        )

Country = Country__43 # end class

### __END__ GTW.OMP.PAP.E164._Country__43
"""

def _decoded (x) :
    return pyk.decoded (x, "utf-8", "iso-8859-1")
# end def _decoded

def _str_int (x) :
    return pyk.text_type (int (x))
# end def _str_int


@pyk.adapt__str__
class NDC (TFL.Meta.Object) :

    ### Want three integer columns, two string columns
    _converters   = (_str_int, int, int, _decoded, _decoded)

    ### DRY info
    _info_cleaner = Re_Replacer ("^Area code for ", "")
    _info_map     = \
        {  "650" : "Mobile (Telering)"
        ,  "660" : "Mobile (Hutchison 3G/3)"
        ,  "664" : "Mobile (A1)"
        ,  "676" : "Mobile (T-Mobile Austria)"
        ,  "677" : "Mobile (HoT)"
        ,  "680" : "Mobile (BoB)"
        ,  "681" : "Mobile (yesss!)"
        ,  "688" : "Mobile (Previously Tele2)"
        ,  "699" : "Mobile (Previously Orange, yesss!)"
        }

    ### rtr.at specifies 67, 68, 69 as NDCs but these are not complete — the
    ### actual NDCs look like 676, 688, or 699
    _ndc_add_digit    = Regexp ("^6[789]$")

    ### Shorten usage to one word
    _usage_map    = \
        { "local network code" : "geographic"
        , "mobile services"    : "mobile"
        , "service number"     : "service"
        , "routing number"     : "routing"
        }

    def __init__ (self, ndc, max_len, min_len, usage, info) :
        self.ndc      = ndc
        self.max_len  = max_len
        self.min_len  = min_len
        self.usage    = usage
        self.info     = info
    # end def __init__

    @classmethod
    def from_xls_row (cls, row) :
        try :
            ndc, max_len, min_len, usage, info = tuple \
                (c (x.value) for c, x in zip (cls._converters, row))
        except Exception :
            pass
        else :
            if cls._ndc_add_digit.match (ndc) :
                for i in range (10) :
                    ndc_x = ndc + str (i)
                    yield cls._from_row (ndc_x, max_len, min_len, usage, info)
            else :
              yield cls._from_row (ndc, max_len, min_len, usage, info)
    # end def from_xls_row

    @classmethod
    def _from_row (cls, ndc, max_len, min_len, usage, info) :
        ndc_len  = len (ndc)
        usage    = cls._usage_map.get (usage, usage)
        info     = cls._info_cleaner  (cls._info_map.get (ndc, info))
        if not info :
            info = usage.capitalize ()
        return cls (ndc, max_len - ndc_len, min_len - ndc_len, usage, info)
    # end def _from_row

    def __repr__ (self) :
        return "%s (%s, %s)" % (self, self.min_len, self.max_len)
    # end def __repr__

    def __str__ (self) :
        return "%s [%s]" % (self.ndc, self.info)
    # end def __str__

# end class NDC

def _convert_row (row) :
    if len (row) == 5 :
        for ndc in NDC.from_xls_row (row) :
            yield ndc
# end def _convert_row

def gen_records (xls_name) :
    book    = xlrd.open_workbook  (xls_name, encoding_override = "iso-8859-1")
    sheet   = book.sheet_by_index (0)
    for i in pyk.xrange (0, sheet.nrows) :
        for ndc in _convert_row (sheet.row (i)) :
            yield ndc
# end def gen_records

def _main (cmd) :
    """Convert the rtr.at spreadsheet for the Austrian Numbering Plan"""
    ndcs       = list (gen_records (cmd.xls_name))
    info_map   = {}
    max_counts = defaultdict (int)
    min_counts = defaultdict (int)
    type_map   = defaultdict (set)
    usage_map  = {}
    for ndc in ndcs :
        max_counts [ndc.max_len] +=1
        min_counts [ndc.min_len] +=1
        info_map   [ndc.ndc]      = ndc.info
        usage_map  [ndc.ndc]      = ndc.usage
        type_map   [ndc.usage].add (ndc.ndc)
    max_len_default = sorted \
        ((v, k) for k, v in pyk.iteritems (max_counts)) [-1] [1]
    min_len_default = sorted \
        ((v, k) for k, v in pyk.iteritems (min_counts)) [-1] [1]
    max_len = dict \
        ((r.ndc, r.max_len) for r in ndcs if r.max_len != max_len_default)
    min_len = dict \
        ((r.ndc, r.min_len) for r in ndcs if r.min_len != min_len_default)
    now     = datetime.datetime.now ()
    f_repr  = formatted_repr
    p_repr  = portable_repr
    pyk.fprint \
        ( ( _module_format
          % dict
              ( generated_by      = sos.path.basename (__file__)
              , generated_from    = p_repr (sos.path.basename (cmd.xls_name))
              , generation_date   = p_repr (str (now) [:16])
              , max_len_default   = max_len_default
              , min_len_default   = min_len_default
              , ndc_types_normal  = p_repr (set (("geographic", "mobile")))
              , ndc_info_map      = f_repr (info_map,  level = 4).strip ()
              , ndc_type_map      = f_repr (type_map,  level = 4).strip ()
              , ndc_usage_map     = f_repr (usage_map, level = 4).strip ()
              , sn_max_length_map = f_repr (max_len,   level = 5).strip ()
              , sn_min_length_map = f_repr (min_len,   level = 5).strip ()
              , year              = now.year
              )
          ).strip ()
        )
# end def _main

_Command = TFL.CAO.Cmd \
    ( handler       = _main
    , args          =
        ( "xls_name:P"
          "?Name of spreadsheet containing the Austrian Numbering Plan"
        ,
        )
    , opts          =
        ()
    , min_args      = 1
    , max_args      = 1
    )

r"""
Example usage:

    python convert_numbering_plan_xls_rtr_at.py \
        /tmp/2312_Austrian_Numbering_Plan_2011-03-30.xls > _Country__43.py

"""

if __name__ == "__main__" :
    _Command ()
### __END__ GTW.OMP.PAP.E164.convert_numbering_plan_xls_rtr_at
