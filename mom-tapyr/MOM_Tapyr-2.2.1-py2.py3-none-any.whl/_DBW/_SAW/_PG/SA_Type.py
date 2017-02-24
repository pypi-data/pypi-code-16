# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Mag. Christian Tanzer All rights reserved
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
#    MOM.DBW.SAW.PG.SA_Type
#
# Purpose
#    Encapsulate SQLalchemy types for PostgreSQL
#
# Revision Dates
#     2-Aug-2013 (CT) Creation
#     8-Oct-2015 (CT) Change `__getattr__` to *not* handle `__XXX__`
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _MOM                  import MOM
from   _TFL                  import TFL
from   _TFL.pyk              import pyk

from   _MOM._DBW._SAW        import SA
import _MOM._DBW._SAW.SA_Type

import sqlalchemy.dialects.postgresql

class M_SA_Type_PG (MOM.DBW.SAW.SA_Type.__class__) :

    _real_name = "M_SA_Type"

    def __getattr__ (cls, name) :
        if name.startswith ("__") and name.endswith ("__") :
            ### Placate inspect.unwrap of Python 3.5,
            ### which accesses `__wrapped__` and eventually throws `ValueError`
            return getattr (self.__super, name)
        try :
            return cls.__m_super.__getattr__ (name)
        except AttributeError :
            result = getattr (sqlalchemy.dialects.postgresql, name.upper ())
            setattr (cls, name, result)
            return result
    # end def __getattr__

M_SA_Type = M_SA_Type_PG # end class

class _PG_SA_Type_ \
        (TFL.Meta.BaM (MOM.DBW.SAW.SA_Type, metaclass = M_SA_Type_PG)) :
    """Encapsulate SQLalchemy types for PostgreSQL"""

    _real_name   = "SA_Type"

SA_Type = _PG_SA_Type_ # end class

if __name__ != "__main__" :
    MOM.DBW.SAW.PG._Export ("SA_Type")
### __END__ MOM.DBW.SAW.PG.SA_Type
