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
#    MOM.DBW.SAW.SQ.Session
#
# Purpose
#    SAW session handling for SQLite
#
# Revision Dates
#     1-Aug-2013 (CT) Creation
#     5-Aug-2013 (CT) Redefine `rollback_pending_change`, `save_point`
#    ««revision-date»»···
#--

from   __future__ import division, print_function
from   __future__ import absolute_import, unicode_literals

from   _MOM       import MOM
from   _TFL       import TFL

from   _TFL.pyk   import pyk

from   _MOM._DBW._SAW        import SAW

import _MOM._DBW
import _MOM._DBW._SAW.Session

class SQ_Session_S (SAW.Session_S) :
    """Scope-bound session handling for SAW using SQLite"""

    _real_name = "Session_S"

    def rollback (self, * args, ** kw) :
        restore_seqs = self.con_man.transaction and not self.in_rollback
        self.__super.rollback (* args, ** kw)
        if restore_seqs :
            con_man = self.con_man
            for seq, v in pyk.iteritems (self.seq_high) :
                try :
                    seq.reserve (self, v, commit = False)
                except Exception :
                    con_man.rollback ()
                else :
                    con_man.needs_commit = True
                    con_man.commit ()
    # end def rollback

    def rollback_pending_change (self) :
        ### unfortunately, sqlalchemy 0.8.2 doesn't use SQLite save_points
        self.scope.rollback_pending_change ()
    # end def rollback_pending_change

    @TFL.Contextmanager
    def save_point (self) :
        ### unfortunately, sqlalchemy 0.8.2 doesn't use SQLite save_points
        yield
    # end def save_point

Session_S = SQ_Session_S # end class

if __name__ != "__main__" :
    MOM.DBW.SAW.SQ._Export ("*")
### __END__ MOM.DBW.SAW.SQ.Session
