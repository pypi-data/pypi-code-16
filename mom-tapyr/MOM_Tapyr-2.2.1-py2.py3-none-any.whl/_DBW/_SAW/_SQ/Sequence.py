# -*- coding: utf-8 -*-
# Copyright (C) 2013 Mag. Christian Tanzer All rights reserved
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
#    MOM.DBW.SAW.SQ.Sequence
#
# Purpose
#    Emulate a database sequence for SQLite
#
# Revision Dates
#    24-Jun-2013 (CT) Creation
#    17-Jul-2013 (CT) Redefine `reserve`
#    31-Jul-2013 (CT) Redefine `_reserve`, not `reserve`
#    26-Aug-2013 (CT) Split into `Sequence`, `Sequence_PID`, `Sequence_X`
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _MOM       import MOM
from   _TFL       import TFL

from   _TFL.pyk   import pyk

import _MOM._DBW
import _MOM._DBW._SAW._SQ.DBS
import _MOM._DBW._SAW.Sequence

class _SQ_Sequence_ (MOM.DBW.SAW._Sequence_) :
    """Emulate a database sequence for SQLite"""

    _table_kw           = dict \
        ( sqlite_autoincrement = True
        )

    def _reserve (self, conn, value) :
        result = self.__super._reserve (conn, value)
        conn.execute \
            ( "UPDATE sqlite_sequence SET seq = %d "
                  "WHERE name == '%s' and seq < %d"
            % (value, self.table_name, value)
            )
        return result
    # end def reserve

# end class _SQ_Sequence_

class SQ_Sequence (_SQ_Sequence_, MOM.DBW.SAW.Sequence) :
    """Emulate a database sequence for SQLite without its own sequence table"""

    _real_name          = "Sequence"

Sequence = SQ_Sequence # end class

class SQ_Sequence_PID (_SQ_Sequence_, MOM.DBW.SAW.Sequence_PID) :
    """Emulate a database sequence for SQLite for `pid`"""

    _real_name          = "Sequence_PID"

Sequence_PID = SQ_Sequence_PID # end class

class SQ_Sequence_X (_SQ_Sequence_, MOM.DBW.SAW.Sequence_X) :
    """Emulate a database sequence for SQLite with its own sequence table"""

    _real_name          = "Sequence_X"

Sequence_X = SQ_Sequence_X # end class

if __name__ != "__main__" :
    MOM.DBW.SAW.SQ._Export ("*")
### __END__ MOM.DBW.SAW.SQ.Sequence
