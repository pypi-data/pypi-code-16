# -*- coding: utf-8 -*-
# Copyright (C) 2013 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package MOM.DBW.SAW.MY.
# 
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    MOM.DBW.SAW.MY.Manager
#
# Purpose
#    Database wrapper for mySQL accessed by sqlalchemy wrapped by SAW
#
# Revision Dates
#    28-Jun-2013 (CT) Creation
#    ««revision-date»»···
#--

from   __future__                 import division, print_function
from   __future__                 import absolute_import, unicode_literals

from   _MOM                       import MOM
from   _TFL                       import TFL
from   _TFL.pyk                   import pyk

from   _MOM._DBW._SAW             import SA

import _MOM._DBW._SAW.Manager
import _MOM._DBW._SAW._MY.DBS
import _MOM._DBW._SAW._MY.Pid_Manager

class _M_SAW_MY_Manager_ (MOM.DBW.SAW.Manager.__class__) :
    """Meta class of MOM.DBW.SAW.MY.Manager"""

# end class _M_SAW_MY_Manager_

class _SAW_MY_Manager_ \
          (TFL.Meta.BaM (MOM.DBW.SAW.Manager, metaclass = _M_SAW_MY_Manager_)) :
    """Database wrapper for SAW-wrapped sqlalchemy-mySQL"""

    _real_name    = "Manager"

    PNS           = MOM.DBW.SAW.MY

Manager = _SAW_MY_Manager_ # end class

if "Filesystem names" == "case insensitive" >= " you might need this" :
    @MOM.Meta.M_E_Type._saw_table_name.add_type (T = Manager.__class__)
    def _saw_table_name (cls, DBW) :
        return cls.type_name.lower ()
    # end def _saw_table_name

if __name__ != "__main__" :
    MOM.DBW.SAW.MY._Export ("*")

    ### The following modules dispatch on `Manager.__class__` and therefore
    ### needs to import `Manager`. Due to the cycle we need to import them
    ### after defining and exporting `Manager`
    import _MOM._DBW._SAW._MY.Attr
    import _MOM._DBW._SAW._MY.E_Type_Wrapper
### __END__ MOM.DBW.SAW.MY.Manager
