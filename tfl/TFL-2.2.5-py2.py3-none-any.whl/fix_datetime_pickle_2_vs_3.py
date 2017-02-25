# -*- coding: utf-8 -*-
# Copyright (C) 2015 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package TFL.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    TFL.fix_datetime_pickle_2_vs_3
#
# Purpose
#    Fix compatibility of datetime pickles created by Python-2
#
# Revision Dates
#    13-Oct-2015 (CT) Creation
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

"""
Provide a workaround for http://bugs.python.org/issue22005: datetime
pickles created by Python 2 cannot be unpickled by Python 3 (up to and
including Python 3.5).

This module uses `copyreg` (`copy_reg` in Python 2) to register
backward- and forward-compatible pickle/unpickle functions for
datetime.date, datetime.datetime, and datetime.time instances.
"""
from   _TFL                   import TFL
from   _TFL.pyk               import pyk

import datetime
import sys

def unpickle_date (pv) :
    return datetime.date (pyk.encoded (pv, "latin1"))
# end def unpickle_date

def unpickle_datetime (pv) :
    return datetime.datetime (pyk.encoded (pv, "latin1"))
# end def unpickle_datetime

def unpickle_time (pv) :
    return datetime.time (pyk.encoded (pv, "latin1"))
# end def unpickle_time

if sys.version_info < (3,) :
    ### register pickle functions only for Python 2
    ### Python 3 pickles are backward compatible
    def pickle_date (dti) :
        pv = dti.__reduce__ () [1] [0]
        return (unpickle_date, (pyk.decoded (pv, "latin1"), ))
    # end def pickle_date

    def pickle_datetime (dti) :
        pv = dti.__reduce__ () [1] [0]
        return (unpickle_datetime, (pyk.decoded (pv, "latin1"), ))
    # end def pickle_datetime

    def pickle_time (dti) :
        pv = dti.__reduce__ () [1] [0]
        return (unpickle_time, (pyk.decoded (pv, "latin1"), ))
    # end def pickle_time

    pyk.copyreg.pickle (datetime.date,     pickle_date,     unpickle_date)
    pyk.copyreg.pickle (datetime.datetime, pickle_datetime, unpickle_datetime)
    pyk.copyreg.pickle (datetime.time,     pickle_time,     unpickle_time)

if __name__ != "__main__" :
    TFL._Export_Module ()
### __END__ TFL.fix_datetime_pickle_2_vs_3
