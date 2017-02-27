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
#    MOM.DBW.SAW.SQ.DBS
#
# Purpose
#    Encapsulate SQLite-specific functionality for SAW
#
# Revision Dates
#    24-Jun-2013 (CT) Creation
#    17-Jul-2013 (CT) Remove dependency on `MOM.DBW.SAS`
#    31-Jul-2013 (CT) Add `Con_Man_Seq`; remove `commit_pid`,
#                     `connection_pid`, `rollback_pid`
#    23-Aug-2013 (CT) Remove SAS-compatibility kludge `sa_scheme`
#    25-Aug-2013 (CT) Move "PRAGMA foreign_keys=ON" into `create_engine`
#    ««revision-date»»···
#--

from   __future__          import division, print_function
from   __future__          import absolute_import, unicode_literals

from   _MOM                import MOM
from   _TFL                import TFL
from   _TFL.pyk            import pyk

from   _MOM._DBW._SAW      import SA

import _MOM._DBW._SAW.DBS

class Con_Man_Seq (TFL.Meta.Object) :
    """Manage a sqlalchemy connection and a related transaction for sequences.

       Reuses the normal `con_man` instances due to SQLite constraints.
    """

    def __init__ (self, engine) :
        self.con_man = engine.con_man
    # end def __init__

    @property
    def connection (self) :
        return self.con_man.connection
    # end def connection

    @property
    def needs_commit (self) :
        return self.con_man.needs_commit
    # end def needs_commit

    @property
    def transaction (self) :
        return self.con_man.transaction
    # end def transaction

    def close (self) :
        pass
    # end def close

    def commit (self) :
        pass
    # end def commit

    def rollback (self) :
        self.con_man.rollback ()
    # end def rollback

# end class Con_Man_Seq

class SQ_DBS (MOM.DBW.SAW.DBS) :
    """Encapsulate SQLite-specific functionality for SAW"""

    _real_name          = "DBS"

    Con_Man_Seq         = Con_Man_Seq

    default_url         = "sqlite:///:memory:"
    scheme              = "sqlite"

    @classmethod
    def create_engine (cls, db_url, isolation_level = None) :
        engine = super (SQ_DBS, cls).create_engine (db_url)
        engine.execute ("PRAGMA case_sensitive_like = true;")
        ### http://sqlalchemy.readthedocs.org/en/rel_0_8/dialects/sqlite.html#foreign-key-support
        engine.execute ("PRAGMA foreign_keys=ON")
        return engine
    # end def create_engine

DBS = SQ_DBS # end class

if __name__ != "__main__" :
    MOM.DBW.SAW.SQ._Export ("*")
### __END__ MOM.DBW.SAW.SQ.DBS
