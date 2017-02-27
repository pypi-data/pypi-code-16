# -*- coding: utf-8 -*-
# Copyright (C) 2010-2013 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# ****************************************************************************
# This module is part of the package MOM.DBW.HPS.
#
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# ****************************************************************************
#
#++
# Name
#    MOM.DBW.HPS.DBS
#
# Purpose
#    Encapsulate db-specific functionality for HPS
#
# Revision Dates
#    23-Jun-2010 (CT) Creation
#    ««revision-date»»···
#--

from   _MOM                      import MOM
from   _TFL                      import TFL
from   _TFL                      import sos

import _MOM._DBW._DBS_
import _TFL.Filename

class HPS (MOM.DBW._DBS_) :
    """DB-specific functionality for HPS"""

    scheme = "hps"

    @classmethod
    def Url (cls, value, ANS, default_path = None) :
        result = super (HPS, cls).Url (value, ANS, default_path)
        if result.authority :
            raise ValueError \
                ( "HPS url cannot specify authority `%s`: %s"
                % (result.authority, value)
                )
        if result.path :
            result._parsed.path = TFL.Filename \
                ( result.path
                , ANS.Version.db_version.db_extension
                , absolute = True
                ).name
        result.create = not sos.path.exists (result.path)
        return result
    # end def Url

# end class HPS

if __name__ != "__main__" :
    MOM.DBW.HPS._Export ("*")
### __END__ MOM.DBW.HPS.DBS
