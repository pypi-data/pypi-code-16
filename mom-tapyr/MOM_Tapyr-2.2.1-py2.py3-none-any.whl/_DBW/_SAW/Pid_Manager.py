# -*- coding: utf-8 -*-
# Copyright (C) 2013 Mag. Christian Tanzer All rights reserved
# Glasauergasse 32, A--1130 Wien, Austria. tanzer@swing.co.at
# #*** <License> ************************************************************#
# This module is part of the package MOM.DBW.SAW.
# 
# This module is licensed under the terms of the BSD 3-Clause License
# <http://www.c-tanzer.at/license/bsd_3c.html>.
# #*** </License> ***********************************************************#
#
#++
# Name
#    MOM.DBW.SAW.Pid_Manager
#
# Purpose
#    SAW specific manager for permanent ids
#
# Revision Dates
#    19-Jun-2013 (CT) Creation
#     4-Jul-2013 (CT) Change `query` to use `session.pid_query`
#    16-Jul-2013 (CT) Change to use the right `SAW.Sequence`
#    18-Jul-2013 (CT) Fix various bugs
#    31-Jul-2013 (CT) Use `scalar`, not `fetchone`, to extract `tn_col`
#    31-Jul-2013 (CT) Use `session.con_man_seq`
#    ««revision-date»»···
#--

from   __future__     import division, print_function
from   __future__     import absolute_import, unicode_literals

from   _MOM           import MOM
from   _TFL           import TFL
from   _TFL.pyk       import pyk

from   _MOM._DBW._SAW import SA

import _MOM._DBW
import _MOM._DBW.Pid_Manager

import _TFL.Context
import _TFL._Meta.Object
import _TFL._Meta.Property

class Pid_Manager (MOM.DBW.Pid_Manager) :

    def __init__ (self, ems, db_url) :
        self.__super.__init__ (ems, db_url)
        self.dbs        = ems.DBW.DBS_map [db_url.scheme]
        self.ETW = ETW  = ems.scope.app_type._SAW ["MOM.Id_Entity"]
        self.sequence   = ETW.sequence
        self.pid_col    = ETW.spk_col
        self.tn_col     = ETW.type_name_col
    # end def __init__

    @property
    def connection (self) :
        return self.session.con_man_seq.connection
    # end def connection

    @property
    def max_pid (self) :
        return self.sequence.max_value
    # end def max_pid

    @property
    def session (self) :
        return self.ems.session
    # end def session

    def commit (self) :
        self.sequence.commit (self.session)
    # end def commit

    def close (self) :
        self.rollback ()
    # end def close

    def new (self, entity, commit = True) :
        pid = self.sequence.next_value (self.ems.session, commit = commit)
        if entity :
            entity.pid = pid
        return pid
    # end def new

    def query (self, pid) :
        return self.session.pid_query (pid)
    # end def query

    def reserve (self, entity, pid, commit = True) :
        self.sequence.reserve (self.ems.session, pid, commit = commit)
        if entity :
            type_name  = entity.type_name
            entity.pid = pid
            db_tn      = self.type_name (pid)
            if db_tn and db_tn != type_name :
                raise ValueError \
                    ( "Try to reserve pid %d with changed type_name %s != %s"
                    % (pid, db_tn, type_name)
                    )
        return pid
    # end def reserve

    def retire (self, entity) :
        pass ### XXX
    # end def retire

    def rollback (self) :
        self.sequence.rollback (self.session)
    # end def rollback

    def type_name (self, pid) :
        pid_col = self.pid_col
        result  = self.connection.execute \
            (SA.sql.select ([self.tn_col]).where (pid_col == pid)).scalar ()
        ### close transaction that was implicitly started by `execute`
        self.commit ()
        if result is None :
            raise LookupError ("No object with pid `%d` found" % (pid, ))
        return result
    # end def type_name

    def __iter__ (self) :
        pid_col = self.pid_col
        tn_col  = self.tn_col
        sar     = self.connection.execute \
            (SA.sql.select ([pid_col, tn_col]).order_by (pid_col.asc ()))
        for row in sar :
            tn = row [type_name]
            if tn :
                yield row [pid_col], tn
        sar.close ()
    # end def __iter__

# end class Pid_Manager

if __name__ != "__main__" :
    MOM.DBW.SAW._Export ("*")
### __END__ MOM.DBW.SAW.Pid_Manager
