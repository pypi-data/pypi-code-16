# -*- coding: utf-8 -*-
# Copyright (C) 2016 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package MOM.DBW.SAW.PG.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    MOM.DBW.SAW.PG.Attr
#
# Purpose
#    PostgreSQL specific attribute handling for SAW
#
# Revision Dates
#    14-Sep-2016 (CT) Creation
#    ««revision-date»»···
#--

from   __future__  import absolute_import
from   __future__  import division
from   __future__  import print_function
from   __future__  import unicode_literals

from   _MOM                import MOM
from   _TFL                import TFL
from   _TFL.pyk            import pyk

from   _MOM._DBW._SAW      import SAW, SA

import _MOM._DBW._SAW.Attr
import _MOM._DBW._SAW._PG

if __name__ != "__main__" :
    MOM.DBW.SAW.PG._Export_Module ()
### __END__ MOM.DBW.SAW.PG.Attr
