# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package MOM.DBW.SAW.SQ.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    MOM.DBW.SAW.SQ.SA_Type
#
# Purpose
#    Encapsulate SQLalchemy types for SQLite
#
# Revision Dates
#    18-Jul-2013 (CT) Creation
#    16-Jun-2016 (CT) Add `Decimal` to store decimal values as scaled integers
#                     + By default, sqlite+pysqlite stores floats and gives a
#                       warning
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _MOM                  import MOM
from   _TFL                  import TFL
from   _TFL.pyk              import pyk

from   _MOM._DBW._SAW        import SA
import _MOM._DBW._SAW.SA_Type

import decimal

class _Decimal_ (SA.types.TypeDecorator) :
    """Augmented decimal type that stores values as scaled integers."""

    impl     = SA.types.BigInteger

    def __init__ (self, max_digits, decimal_places, * args, ** kw) :
        self._SAW_max_digits     = max_digits
        self._SAW_decimal_places = decimal_places
        self._SAW_scale          = int (10 ** decimal_places)
        self._SAW_C              = decimal.Context \
            ( prec     = decimal_places + max_digits
            , rounding = decimal.ROUND_HALF_UP
            )
        SA.types.TypeDecorator.__init__ (self, * args, ** kw)
    # end def __init__

    def process_bind_param   (self, value, dialect) :
        if value is not None :
            with decimal.localcontext (self._SAW_C) :
                result = int (value * self._SAW_scale)
        else :
            result = value
        return result
    # end def process_bind_param

    def process_result_value (self, value, dialect) :
        if isinstance (value, pyk.int_types) :
            result = decimal.Decimal (value, self._SAW_C) / self._SAW_scale
        else :
            result = value
        return result
    # end def process_result_value

# end class _Decimal_

class _SQ_SA_Type_ (MOM.DBW.SAW.SA_Type) :
    """Encapsulate SQLalchemy types for SQLite"""

    _real_name   = "SA_Type"

    Decimal      = _Decimal_

SA_Type = _SQ_SA_Type_ # end class

if __name__ != "__main__" :
    MOM.DBW.SAW.SQ._Export ("SA_Type")
### __END__ MOM.DBW.SAW.SQ.SA_Type
