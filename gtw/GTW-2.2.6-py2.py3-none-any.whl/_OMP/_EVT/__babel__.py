# -*- coding: utf-8 -*-
# Copyright (C) 2010 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package GTW.OMP.EVT.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    GTW.OMP.EVT.__babel__
#
# Purpose
#    This file is the entry point for the Babel translation extraction
#    process.
#
# Revision Dates
#    16-Mar-2010 (CT) Creation
#    ««revision-date»»···
#--

from   _MOM.import_MOM import *
import _MOM.Babel
import _GTW._OMP._EVT.import_EVT

def main (encoding, config, method) :
    from   _MOM._EMS.Hash         import Manager as EMS
    from   _MOM._DBW._HPS.Manager import Manager as DBW
    from   _GTW                   import GTW

    return MOM.Babel.Add_Translations \
        ( encoding, config, method
        , MOM.App_Type ("EVT", GTW).Derived (EMS, DBW)
        )
# end def main

### __END__ GTW.OMP.EVT.__babel__
