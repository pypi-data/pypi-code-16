# -*- coding: utf-8 -*-
# Copyright (C) 2013 Mag. Christian Tanzer All rights reserved
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
#    MOM.DBW.SAW.PG.Sequence
#
# Purpose
#    Wrap a PostgreSQL sequence
#
# Revision Dates
#    24-Jun-2013 (CT) Creation
#    26-Jul-2013 (CT) Redefine `_reserve`, not `reserve`
#    28-Jul-2013 (CT) Quote `seq_name` in `SELECT setval`; fix typo
#    26-Aug-2013 (CT) Split into `Sequence`, `Sequence_PID`, `Sequence_X`
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _MOM       import MOM
from   _TFL       import TFL

from   _TFL.pyk   import pyk

import _MOM._DBW
import _MOM._DBW._SAW._PG.DBS
import _MOM._DBW._SAW.Sequence

class _PG_Sequence_ (MOM.DBW.SAW._Sequence_S_) :
    """Wrap a PostgreSQL sequence"""

    def _reserve (self, conn, value) :
        result = self.__super._reserve (conn, value)
        stmt   = "SELECT setval('%s', %d)" % (self.seq_name, value)
        conn.execute (stmt)
        return result
    # end def _reserve

# end class _PG_Sequence_

class PG_Sequence (_PG_Sequence_, MOM.DBW.SAW.Sequence) :
    """Wrap a PostgreSQL sequence without its own sequence table"""

    _real_name          = "Sequence"

Sequence = PG_Sequence # end class

class PG_Sequence_PID (_PG_Sequence_, MOM.DBW.SAW.Sequence_PID) :
    """Wrap a PostgreSQL sequence for `pid`"""

    _real_name          = "Sequence_PID"

Sequence_PID = PG_Sequence_PID # end class

class PG_Sequence_X (_PG_Sequence_, MOM.DBW.SAW.Sequence_X) :
    """Wrap a PostgreSQL sequence with its own sequence table"""

    _real_name          = "Sequence_X"

Sequence_X = PG_Sequence_X # end class

if __name__ != "__main__" :
    MOM.DBW.SAW.PG._Export ("*")
### __END__ MOM.DBW.SAW.PG.Sequence
